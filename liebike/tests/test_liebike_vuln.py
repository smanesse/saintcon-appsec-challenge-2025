import requests
import time
import os

BASE_URL = os.getenv("BASE_URL", "http://lightcycle:6008")

class TestLightCycleVuln:

    def test_vuln_1(self):
        """Test that arbitrary scores can be submitted (the vulnerability)."""
        # Start a game
        start_response = requests.post(f"{BASE_URL}/api/start_game")
        session_id = start_response.json()["session_id"]

        # Submit minimum required moves with proper timing
        for i in range(5):
            move_data = {
                "session_id": session_id,
                "position": {"x": 20 + i, "y": 20}
            }
            requests.post(f"{BASE_URL}/api/move", json=move_data)
            time.sleep(0.1)

        # Submit with an arbitrarily high score (vulnerability!)
        # The trail is validated but the score is NOT
        score_data = {
            "session_id": session_id,
            "final_position": {"x": -1, "y": 20},  # Valid wall crash
            "score": 99999  # Arbitrary high score that doesn't match trail length
        }
        response = requests.post(f"{BASE_URL}/api/submit_score", json=score_data)

        # The vulnerability: server accepts the arbitrary score
        assert response.status_code == 200
        data = response.json()
        assert data["high_score"] != 99999
