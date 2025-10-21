import requests
import time
import os

BASE_URL = os.getenv("BASE_URL", "http://lightcycle:6008")

class TestLightCycle:

    def test_homepage_accessible(self):
        """Test that the main page loads."""
        response = requests.get(BASE_URL)
        assert response.status_code == 200
        assert "Light Cycle Racer" in response.text
        assert "gameCanvas" in response.text

    def test_leaderboard_endpoint(self):
        """Test that the leaderboard endpoint works."""
        response = requests.get(f"{BASE_URL}/api/leaderboard")
        assert response.status_code == 200
        data = response.json()
        assert "high_score" in data
        assert "top_player" in data

    def test_start_game_session(self):
        """Test starting a new game session."""
        response = requests.post(f"{BASE_URL}/api/start_game")
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert data["status"] == "started"
        assert len(data["session_id"]) > 0

    def test_move_with_valid_session(self):
        """Test submitting a move with a valid session."""
        # Start a game
        start_response = requests.post(f"{BASE_URL}/api/start_game")
        session_id = start_response.json()["session_id"]

        # Submit first move
        move_data = {
            "session_id": session_id,
            "position": {"x": 20, "y": 20}
        }
        response = requests.post(f"{BASE_URL}/api/move", json=move_data)
        assert response.status_code == 200
        assert response.json()["status"] == "recorded"

    def test_move_timing_validation(self):
        """Test that moves submitted too fast are rejected."""
        # Start a game
        start_response = requests.post(f"{BASE_URL}/api/start_game")
        session_id = start_response.json()["session_id"]

        # Submit first move
        move_data = {
            "session_id": session_id,
            "position": {"x": 20, "y": 20}
        }
        requests.post(f"{BASE_URL}/api/move", json=move_data)

        # Try to submit second move immediately (too fast)
        move_data["position"] = {"x": 21, "y": 20}
        response = requests.post(f"{BASE_URL}/api/move", json=move_data)
        assert response.status_code == 400
        assert "too fast" in response.text.lower()

    def test_valid_wall_crash(self):
        """Test that a valid wall crash is accepted."""
        # Start a game
        start_response = requests.post(f"{BASE_URL}/api/start_game")
        session_id = start_response.json()["session_id"]

        # Submit some moves with proper timing
        for i in range(5):
            move_data = {
                "session_id": session_id,
                "position": {"x": 20 + i, "y": 20}
            }
            requests.post(f"{BASE_URL}/api/move", json=move_data)
            time.sleep(0.05)  # Game loop timing

        # Submit score with wall crash (out of bounds)
        score_data = {
            "session_id": session_id,
            "final_position": {"x": -1, "y": 20},
            "score": 50
        }
        response = requests.post(f"{BASE_URL}/api/submit_score", json=score_data)
        assert response.status_code == 200
        assert response.json()["status"] == "accepted"

    def test_valid_trail_crash(self):
        """Test that a valid trail collision is accepted."""
        # Start a game
        start_response = requests.post(f"{BASE_URL}/api/start_game")
        session_id = start_response.json()["session_id"]

        # Submit moves creating a trail
        positions = [
            {"x": 20, "y": 20},
            {"x": 21, "y": 20},
            {"x": 22, "y": 20},
            {"x": 23, "y": 20},
        ]

        for pos in positions:
            move_data = {
                "session_id": session_id,
                "position": pos
            }
            requests.post(f"{BASE_URL}/api/move", json=move_data)
            time.sleep(0.1)

        # Crash into own trail (position that exists in trail)
        score_data = {
            "session_id": session_id,
            "final_position": {"x": 21, "y": 20},  # Exists in trail
            "score": 40
        }
        response = requests.post(f"{BASE_URL}/api/submit_score", json=score_data)
        assert response.status_code == 200
        assert response.json()["status"] == "accepted"

    def test_invalid_crash_location(self):
        """Test that an invalid crash location is rejected."""
        # Start a game
        start_response = requests.post(f"{BASE_URL}/api/start_game")
        session_id = start_response.json()["session_id"]

        # Submit some moves
        for i in range(5):
            move_data = {
                "session_id": session_id,
                "position": {"x": 20 + i, "y": 20}
            }
            requests.post(f"{BASE_URL}/api/move", json=move_data)
            time.sleep(0.1)

        # Try to submit with invalid crash (in bounds, not in trail)
        score_data = {
            "session_id": session_id,
            "final_position": {"x": 10, "y": 10},  # Not in trail, in bounds
            "score": 50
        }
        response = requests.post(f"{BASE_URL}/api/submit_score", json=score_data)
        assert response.status_code == 400
        assert "not valid" in response.text.lower()

    def test_trail_too_short(self):
        """Test that submissions with trails that are too short are rejected."""
        # Start a game
        start_response = requests.post(f"{BASE_URL}/api/start_game")
        session_id = start_response.json()["session_id"]

        # Submit only one move (trail too short)
        move_data = {
            "session_id": session_id,
            "position": {"x": 20, "y": 20}
        }
        requests.post(f"{BASE_URL}/api/move", json=move_data)
        time.sleep(0.1)

        # Try to submit score
        score_data = {
            "session_id": session_id,
            "final_position": {"x": -1, "y": 20},
            "score": 10
        }
        response = requests.post(f"{BASE_URL}/api/submit_score", json=score_data)
        assert response.status_code == 400
        assert "too short" in response.text.lower()

    def test_invalid_session_id(self):
        """Test that invalid session IDs are rejected."""
        score_data = {
            "session_id": "invalid-session-id",
            "final_position": {"x": -1, "y": 20},
            "score": 50
        }
        response = requests.post(f"{BASE_URL}/api/submit_score", json=score_data)
        assert response.status_code == 400
        assert "invalid session" in response.text.lower()
