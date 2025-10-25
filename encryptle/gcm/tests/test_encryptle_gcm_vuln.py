import pytest
import requests
import os
import re
import time
import json

BASE_URL = os.getenv("BASE_URL", "http://encryptle_gcm:6003")

class TestEncryptleGCMVuln:
    
    def test_vuln_1(self):
        """Test GCM nonce reuse vulnerability by XORing ciphertexts."""
        
        # Create two separate sessions to get different solutions/cookies
        session1 = requests.Session()
        session2 = requests.Session()
        
        # Get first cookie and solution
        response1 = session1.get(BASE_URL)
        cookie1 = response1.cookies.get("answer")
        
        # Make a failed guess to get the solution revealed in the response
        failed_response1 = session1.post(f"{BASE_URL}/check", json={"guess": "wrongword"})
        
        # Extract the revealed solution from the failed response
        import re
        match1 = re.search(r"The word was: (\w+)", failed_response1.text)
        solution1 = match1.group(1)
        
        # Wait a moment to ensure different timestamp, then get second cookie
        time.sleep(2)
        
        # Get second cookie (will have different solution but reused nonce/IV)
        response2 = session2.get(BASE_URL)
        cookie2 = response2.cookies.get("answer")

        # Now we have:
        # - cookie1 (ciphertext1) and solution1 (part of plaintext1)
        # - cookie2 (ciphertext2) and we want to recover solution2 via nonce reuse attack
        
        # Construct the known plaintext structure for the first cookie
        # We need to estimate the JSON structure that was encrypted
        # Format: {"word": "solution", "ts": timestamp, "nonce": "hex_nonce"}
        
        # For the GCM nonce reuse attack: (ciphertext1 XOR plaintext1) XOR ciphertext2 = plaintext2
        
        # Convert hex cookies to bytes (excluding GCM tag - last 16 bytes)
        cookie1_bytes = bytes.fromhex(cookie1)[:-16]  # Remove GCM tag
        cookie2_bytes = bytes.fromhex(cookie2)[:-16]  # Remove GCM tag
        
        # We know solution1, so we can construct approximate plaintext1
        # The exact format from the source: {"word": solution, "ts": timestamp, "nonce": hex}
        # We'll try to construct this with reasonable assumptions
        
        estimated_plaintext1 = '{"word": "' + solution1 + '"'
        
        plaintext1_bytes = estimated_plaintext1.encode()
        
        # Pad to match ciphertext length if needed
        if len(plaintext1_bytes) < len(cookie1_bytes):
            plaintext1_bytes += b'\x00' * (len(cookie1_bytes) - len(plaintext1_bytes))
        elif len(plaintext1_bytes) > len(cookie1_bytes):
            plaintext1_bytes = plaintext1_bytes[:len(cookie1_bytes)]
        
        # Perform GCM nonce reuse attack: (ciphertext1 XOR plaintext1) XOR ciphertext2 = plaintext2
        keystream_diff = bytes(a ^ b for a, b in zip(cookie1_bytes, plaintext1_bytes))
        recovered_plaintext2 = bytes(a ^ b for a, b in zip(keystream_diff, cookie2_bytes))
        
        # Try to decode as JSON and check if it contains our known solution2
        recovered_str = recovered_plaintext2[10:15].decode('utf-8', errors='ignore')

        response2 = session2.post(f"{BASE_URL}/check", json={"guess": recovered_str})
        
        assert "Correct!" not in response2.text
        assert f"The word was: {recovered_str}" not in response2.text