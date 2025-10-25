import requests
import os

BASE_URL = os.getenv("BASE_URL", "http://encryptle_cbc:6002")
BLOCK_SIZE = 16

class TestEncryptleCBCVuln:
    
    def test_vuln_1(self):
        """Test CBC padding oracle attack by exploiting response length differences."""
        
        # Create session to get a cookie with ciphertext to attack
        session = requests.Session()
        
        # Get first cookie 
        response = session.get(BASE_URL)
        CIPHER = response.cookies.get("answer")

        def make_request(cookie):
            response = requests.post(BASE_URL + "/check", cookies={"answer":cookie})
            return len(response.text)

        def single_block_attack(block):
            """Returns the decryption of the given ciphertext block"""

            # zeroing_iv starts out nulled. each iteration of the main loop will add
            # one byte to it, working from right to left, until it is fully populated,
            # at which point it contains the result of DEC(ct_block)
            zeroing_iv = bytearray.fromhex(CIPHER[0:32])

            for pad_val in range(1, BLOCK_SIZE+1):
                padding_iv = [pad_val ^ b for b in zeroing_iv]

                for candidate in range(256):
                    padding_iv[-pad_val] = candidate
                    iv = bytes(padding_iv)
                    result = make_request(iv.hex() + block.hex())
                    if result < 200:
                        if pad_val == 1:
                            # make sure the padding really is of length 1 by changing
                            # the penultimate block and querying the oracle again
                            padding_iv[-2] ^= 1
                            iv = bytes(padding_iv)
                            if not make_request(iv.hex() + block.hex()):
                                continue  # false positive; keep searching
                        break
                else:
                    # unsuccessful attack
                    return None

                zeroing_iv[-pad_val] = candidate ^ pad_val

            return zeroing_iv

        block = bytes.fromhex(CIPHER[32:64])
        zeroiv = single_block_attack(block)
        if not zeroiv:
            assert True
            return
        recovered_plaintext = bytes(iv_byte ^ dec_byte for iv_byte, dec_byte in zip(zeroiv, bytearray.fromhex(CIPHER[0:32])))
        recovered_str = recovered_plaintext[10:14].decode('utf-8', errors='ignore')

        response = session.post(f"{BASE_URL}/check", json={"guess": recovered_str})
    
        assert "Correct!" not in response.text
        assert f"The word was: {recovered_str}" not in response.text