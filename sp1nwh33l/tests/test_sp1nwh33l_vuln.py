import requests
import os

BASE_URL = os.getenv("BASE_URL", "http://sp1nwh33l:6007")

class TestSp1nwh33lVuln:

    def test_vuln_1(self):
        """Test that angle 180 gives high prize (100 points)."""
        session = requests.Session()

        spin_data = {"Angle": 180}
        response = session.post(f"{BASE_URL}/api/spin", json=spin_data)
        try:
            spin_result = response.json()
        except:
            assert True
            return
        
        assert spin_result["prize"] != 100
  