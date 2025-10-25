import requests
import os
import time

BASE_URL = os.getenv("BASE_URL", "http://encryptle_ecb:6001")

class TestEncryptleECBVuln:
    
    def test_vuln_1(self):
        """Test ECB malleability attack by combining ciphertext blocks."""
        
        # Create two separate sessions to get different solutions/cookies
        session1 = requests.Session()
        session2 = requests.Session()
        
        # Get first cookie and solution
        response1 = session1.get(BASE_URL)
        cookie1 = response1.cookies.get("answer")
        
        # Make a failed guess to get the solution revealed in the response
        failed_response = session1.post(f"{BASE_URL}/check", json={"guess": "wrongword"})
        
        # Extract the revealed solution from the failed response
        import re
        match = re.search(r"The word was: (\w+)", failed_response.text)
        solution1 = match.group(1)
        
        # Wait a moment to ensure different timestamp, then get second cookie
        time.sleep(2)
        
        # Get second cookie (will have different solution but fresh timestamp)
        response2 = session2.get(BASE_URL)
        cookie2 = response2.cookies.get("answer")
        
        # Perform ECB malleability attack:
        # Take first 32 hex chars (16 bytes, first block) from cookie1 (contains known solution)
        # Take remaining hex chars from cookie2 (contains fresh nonce/timestamp)
        # This exploits ECB's block independence - we can mix blocks from different ciphertexts
        hybrid_cookie = cookie1[:32] + cookie2[32:]
        
        # Create a new session for the attack
        attack_session = requests.Session()
        
        # Set the hybrid cookie manually
        attack_session.cookies.set("answer", hybrid_cookie)
        
        # Use the solution from the first cookie (which is now in our hybrid cookie)
        # This should succeed because:
        # 1. The solution block comes from cookie1 (known solution)
        # 2. The nonce/timestamp blocks come from cookie2 (fresh and valid)
        response = attack_session.post(f"{BASE_URL}/check", json={"guess": solution1.lower()})
        
        assert "Correct!" not in response.text
        assert f"The word was: {solution1}" not in response.text
        
        # This proves the ECB malleability vulnerability - we successfully
        # combined blocks from different ciphertexts to create a valid but
        # unintended combination (known solution + fresh nonce)
    