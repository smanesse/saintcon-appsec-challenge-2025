import requests
import os
import io
from PIL import Image

BASE_URL = os.getenv("BASE_URL", "http://fortune_teller:6010")

class TestFortuneTeller:
    
    def test_vuln_1(self):
        
        config_response = requests.get(f"{BASE_URL}/admin/config", 
                                      params={'GOLDEN_TICKET_RARITY': '100000000', 'MAX_ATTEMPTS': 10})
        assert config_response.status_code == 200

        
        
        response = requests.post(f"{BASE_URL}/api/fortune", 
                                json={'image_url': 'http://localhost:6010/admin/config?GOLDEN_TICKET_RARITY=1'},
                                headers={'Content-Type': 'application/json'})

        # Create a test image
        img = Image.new('RGB', (100, 100), color=(0, 255, 0))
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        # Upload the image - should get golden ticket
        files = {'photo': ('test_image.png', img_bytes, 'image/png')}
        response = requests.post(f"{BASE_URL}/api/fortune", files=files)
        data = response.json()
        assert "The stars align perfectly for you" not in data['fortune']