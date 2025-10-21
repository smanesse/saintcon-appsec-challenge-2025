import requests
import os
import io
from PIL import Image

BASE_URL = os.getenv("BASE_URL", "http://fortune_teller:6010")

class TestFortuneTeller:
    
    def test_image_upload_fortune(self):
        """Test that image upload returns a fortune."""
        # Create a simple test image
        img = Image.new('RGB', (100, 100), color=(255, 0, 0))
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        # Upload the image
        files = {'photo': ('test_image.png', img_bytes, 'image/png')}
        response = requests.post(f"{BASE_URL}/api/fortune", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data['fortune']) > 0
    
    def test_url_input_fortune(self):
        """Test that URL input returns a fortune."""
        # Use a valid https image URL
        payload = {
            "image_url": "https://httpbin.org/image/png"
        }
        
        response = requests.post(f"{BASE_URL}/api/fortune", 
                                json=payload,
                                headers={'Content-Type': 'application/json'})
        
        assert response.status_code == 200
        data = response.json()
        assert 'fortune' in data
        assert 'category' in data
        assert 'special' in data
        assert len(data['fortune']) > 0
        assert len(data['category']) > 0
    
    def test_golden_ticket_rarity(self):
        """Test that setting golden ticket rarity of 1 from localhost results in golden ticket."""
        # First, set the golden ticket rarity to 1 (guaranteed golden ticket)
        config_response = requests.get(f"{BASE_URL}/admin/config", 
                                      params={'GOLDEN_TICKET_RARITY': '1', 'MAX_ATTEMPTS': 10})
        assert config_response.status_code == 200
        assert "'MAX_ATTEMPTS': '10'" in config_response.text
        
        # Create a test image
        img = Image.new('RGB', (100, 100), color=(0, 255, 0))
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        # Upload the image - should get golden ticket
        files = {'photo': ('test_image.png', img_bytes, 'image/png')}
        response = requests.post(f"{BASE_URL}/api/fortune", files=files)
        data = response.json()
        assert "The stars align perfectly for you" in data['fortune']

        config_response = requests.get(f"{BASE_URL}/admin/config", 
                                      params={'GOLDEN_TICKET_RARITY': '100000000'})
        assert config_response.status_code == 200
        
        # Upload the image - should not get golden ticket
        img_bytes.seek(0)
        files = {'photo': ('test_image.png', img_bytes, 'image/png')}
        response = requests.post(f"{BASE_URL}/api/fortune", files=files)
        data = response.json()
        assert "The stars align perfectly for you" not in data['fortune']