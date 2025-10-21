import requests
import os

BASE_URL = os.getenv("BASE_URL", "http://sp1nwh33l:6007")

class TestSp1nwh33l:

    def test_spin_wheel_and_get_points(self):
        """Test basic functionality: spin wheel and get points."""
        session = requests.Session()

        # Get initial state
        response = session.get(f"{BASE_URL}/api/state")
        assert response.status_code == 200
        initial_state = response.json()
        assert "points" in initial_state
        assert "spins_used" in initial_state
        assert "spins_left" in initial_state

        spin_data = {"Angle": 1}
        response = session.post(f"{BASE_URL}/api/spin", json=spin_data)
        assert response.status_code == 200

        spin_result = response.json()
        assert "prize" in spin_result
        assert "points" in spin_result
        assert "spins_left" in spin_result
        assert "angle" in spin_result

        # Verify we got points
        assert spin_result["prize"] > 0
        assert spin_result["points"] > initial_state["points"]
        assert spin_result["spins_left"] == initial_state["spins_left"] - 1

        # Verify state is updated
        response = session.get(f"{BASE_URL}/api/state")
        assert response.status_code == 200
        new_state = response.json()
        assert new_state["points"] == spin_result["points"]
        assert new_state["spins_used"] == initial_state["spins_used"] + 1
        assert new_state["spins_left"] == initial_state["spins_left"] - 1

    def test_state_endpoint(self):
        """Test the state endpoint returns correct format."""
        session = requests.Session()

        response = session.get(f"{BASE_URL}/api/state")
        assert response.status_code == 200

        state = response.json()
        assert "points" in state
        assert "spins_used" in state
        assert "spins_left" in state
        assert isinstance(state["points"], (int, float))
        assert isinstance(state["spins_used"], int)
        assert isinstance(state["spins_left"], int)
        assert state["spins_used"] + state["spins_left"] <= 3

    def test_homepage_loads(self):
        """Test that the homepage loads successfully."""
        session = requests.Session()

        response = session.get(BASE_URL)
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")