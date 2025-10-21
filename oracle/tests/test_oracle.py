import requests
import os
import time
import base64
import json

BASE_URL = os.getenv("BASE_URL", "http://diceroller:6004")

def extract_session_id(session_cookie_value):
    """Extract session ID from Play Framework session cookie (JWT format)."""
    try:
        parts = session_cookie_value.split('.')
        if len(parts) != 3:
            print("Cookie is not in JWT format")
            return None
            
        payload = parts[1]
        
        padding = len(payload) % 4
        if padding:
            payload += '=' * (4 - padding)
            
        decoded_bytes = base64.urlsafe_b64decode(payload)
        decoded_str = decoded_bytes.decode('utf-8')
        
        session_data = json.loads(decoded_str)
        
        if 'data' in session_data and 'sessionId' in session_data['data']:
            return session_data['data']['sessionId']
            
    except Exception as e:
        print(f"Error extracting session ID: {e}")
        
    return None

class TestBasicFunctionality:

    def test_index_endpoint_accessible(self):
        """Test that the main page loads."""
        session = requests.Session()
        response = session.get(BASE_URL)
        assert response.status_code == 200
        assert "PLAY_SESSION" in response.cookies

    def test_guess_endpoint_requires_session(self):
        """Test that guess endpoint redirects without session."""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/guess",
                                     data={'guess': '1000'},
                                     allow_redirects=False)
        assert response.status_code == 303

    def test_make_valid_guess(self):
        """Test making a valid guess with session."""
        session = requests.Session()
        session.get(BASE_URL)

        response = session.post(f"{BASE_URL}/guess", data={'guess': '1000000'})
        assert response.status_code == 200

    def test_successful_guess_with_shared_file(self):
        """Test successful guess by reading target number from shared file."""
        session = requests.Session()
        response = session.get(BASE_URL)
        assert response.status_code == 200
        assert "PLAY_SESSION" in response.cookies

        session_cookie = response.cookies.get("PLAY_SESSION")
        session_id = extract_session_id(session_cookie)
        assert session_id is not None, "Could not extract session ID from cookie"

        time.sleep(1)

        results_dir = "/shared"

        target_file = os.path.join(results_dir, f"target_{session_id}.txt")
        assert os.path.exists(target_file), f"Target file {target_file} not found"

        with open(target_file, 'r') as f:
            target_number = int(f.read().strip())

        response = session.post(f"{BASE_URL}/guess", data={'guess': str(target_number)})
        assert response.status_code == 200
        assert "Congratulations! You guessed correctly!" in response.text

    def test_wrong_guess_reveals_answer(self):
        """Test that making a wrong guess reveals the correct answer in the response."""
        session = requests.Session()
        session.get(BASE_URL)

        response = session.post(f"{BASE_URL}/guess", data={'guess': '123456789'})
        assert response.status_code == 200

        import re
        match = re.search(r"The number was ([-]?\d+)", response.text)
        assert match is not None, "Response should reveal the correct answer with 'The number was X'"
        revealed_number = int(match.group(1))

        assert revealed_number != 123456789, "Should reveal actual target, not our guess"
        assert "Congratulations! You guessed correctly!" not in response.text
