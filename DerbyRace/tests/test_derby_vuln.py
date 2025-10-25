import requests
import os
import io
import json

BASE_URL = os.getenv("BASE_URL", "http://derby-race:6009")

class TestFortuneTeller:
    
    def test_vuln_1(self):
        """Buffer overflow"""
        setup_data = {
            "horseName": "AAAAAAAAAAAAAAAAx\xFF",
            "emblemId": 1
        }

        setup_response = requests.post(f"{BASE_URL}/api/derby/setup",
                                     json=setup_data,
                                     headers={"Content-Type": "application/json"})

        assert setup_response.status_code == 200
        setup_json = setup_response.json()
        assert setup_json["success"] is True
        assert "player_index" in setup_json
        assert "horses" in setup_json
        assert len(setup_json["horses"]) == 7  # 6 NPCs + 1 player

        player_horse = None
        for horse in setup_json["horses"]:
            if horse["is_player"]:
                player_horse = horse
                break

        assert player_horse is not None
        assert player_horse["position"] == 0