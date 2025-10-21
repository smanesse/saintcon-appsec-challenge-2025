import requests
import os
import json

BASE_URL = os.getenv("BASE_URL", "http://localhost:6006")

class TestiTrivia:

    def test_can_get_new_token(self):
        """Test that we can get a new user token."""
        response = requests.get(f"{BASE_URL}/new")
        assert response.status_code == 200
        token = response.text.strip()
        assert len(token) > 15  # Based on database constraint

    def test_can_submit_guess_and_get_status(self):
        """Test that we can submit a guess and get status back."""
        session = requests.Session()

        # Get a new token
        response = session.get(f"{BASE_URL}/new")
        assert response.status_code == 200
        token = response.text.strip()

        # Get a question
        response = session.get(f"{BASE_URL}/next", headers={"User": token})
        assert response.status_code == 200
        question = response.text.strip()
        assert len(question) > 0
        assert "how many" in question.lower()

        # Submit an answer (doesn't matter if correct)
        response = session.post(f"{BASE_URL}/answer", data="42", headers={"User": token})
        assert response.status_code == 200
        result = response.text.strip()
        assert result.startswith("TRUE") or result.startswith("FALSE")

        # Get status
        response = session.get(f"{BASE_URL}/status", headers={"User": token})
        assert response.status_code == 200
        status = json.loads(response.text)
        assert "game_over" in status
        assert "answers_given" in status
        assert "allowed_questions" in status
        assert "trivia_results" in status
        assert status["answers_given"] == 1
        assert status["allowed_questions"] == 3