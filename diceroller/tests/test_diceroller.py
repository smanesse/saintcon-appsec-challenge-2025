import requests
import time
import os

BASE_URL = os.getenv("BASE_URL", "http://diceroller:6005")

class TestDiceroller:
    
    def test_homepage_accessible(self):
        """Test that the main page loads."""
        response = requests.get(BASE_URL)
        assert response.status_code == 200
        assert "Carnival d20 Roller" in response.text
        assert "Roll the Dice!" in response.text
    
    def test_dice_roll_with_timestamp(self):
        """Test making a dice roll with timestamp input."""
        timestamp = str(int(time.time()))
        data = {"input_string": timestamp}
        
        response = requests.post(BASE_URL, data=data)
        assert response.status_code == 200
        assert "Rolling..." in response.text
        assert "dice-container" in response.text
    
    def test_dice_twenty_count(self):
        """Test that dice count for 20s is reported correctly for a known input."""
        data = {"input_string": "test123"}
        
        response = requests.post(BASE_URL, data=data)
        assert response.status_code == 200
        assert "Rolling..." in response.text
        
        assert '3 20 rolls!' in response.text
