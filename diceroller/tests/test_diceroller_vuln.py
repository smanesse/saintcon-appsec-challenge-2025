import requests
import os

BASE_URL = os.getenv("BASE_URL", "http://diceroller:6005")

class TestDiceroller:
    
    def test_vuln_1(self):
        """Test making a dice roll with timestamp input."""
        timestamp = str(49006445304)
        data = {"input_string": timestamp}
        
        response = requests.post(BASE_URL, data=data)
        assert response.status_code == 200
        assert "You win!!!" not in response.text
        assert "30 20 rolls!" not in response.text