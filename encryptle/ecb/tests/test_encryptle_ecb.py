import requests
import os
import re
import time

BASE_URL = os.getenv("BASE_URL", "http://encryptle_ecb:6001")

class TestEncryptleECB:
    
    def test_cookie_set_on_homepage(self):
        """Test that answer cookie is set on homepage."""
        client_session = requests.Session()
        response = client_session.get(BASE_URL)
        assert response.status_code == 200
        answer_cookie = response.cookies.get("answer")
        assert answer_cookie is not None
        # Cookie should be hex-encoded ciphertext
        assert re.match(r'^[0-9a-fA-F]+$', answer_cookie)
    
    def test_incorrect_guess_behavior(self):
        client_session = requests.Session()
        """Test response for incorrect guess."""
        # Get homepage to create new solution and cookie
        response = client_session.get(BASE_URL)
        assert response.status_code == 200
        
        # Test incorrect guess
        response = client_session.post(f"{BASE_URL}/check", json={"guess": "wrongword"})
        assert response.status_code == 200
        assert "Score:" in response.text
        assert "Try again!" in response.text
        assert "Correct!" not in response.text
    
    def test_correct_guess_with_solution_file(self):
        """Test response for correct guess using solution file."""
        import requests
        session = requests.Session()
        
        # Get homepage to create new solution and cookie
        response = session.get(BASE_URL)
        assert response.status_code == 200
        
        # Wait for solution file to be written
        time.sleep(2)
        
        # Read the solution from shared directory
        results_dir = "/shared"
        solution_file = os.path.join(results_dir, "solution.txt")
        
        assert os.path.exists(solution_file), f"Solution file {solution_file} not found. Make sure TEST_MODE environment variable is set."
        
        with open(solution_file, 'r') as f:
            solution = f.read().strip()
        
        assert solution, "Solution file exists but is empty"
        
        # Test correct guess
        response = session.post(f"{BASE_URL}/check", json={"guess": solution.lower()})
        assert response.status_code == 200
        assert "Correct!" in response.text
        assert f"The word was: {solution}" in response.text
    
    def test_solution_revealed_on_failed_guess(self):
        client_session = requests.Session()
        """Test that solution is revealed when guess is incorrect."""
        # Get homepage to create new solution and cookie
        response = client_session.get(BASE_URL)
        assert response.status_code == 200
        
        # Make an incorrect guess 
        response = client_session.post(f"{BASE_URL}/check", json={"guess": "wrongword"})
        assert response.status_code == 200
        assert "Score:" in response.text
        assert "The word was:" in response.text
        assert "Try again!" in response.text
        
        # Extract the revealed solution from the response
        import re
        match = re.search(r"The word was: (\w+)", response.text)
        assert match is not None, "Solution should be revealed in failed guess response"
        revealed_solution = match.group(1)
        assert len(revealed_solution) > 0, "Revealed solution should not be empty"