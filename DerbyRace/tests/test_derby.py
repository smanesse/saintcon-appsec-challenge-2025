import requests
import os
import io
import json
import time

BASE_URL = os.getenv("BASE_URL", "http://derby-race:6009")

class TestDerbyRace:

    def test_full_race(self):
        """Test that I can complete a full race"""
        setup_data = {
            "horseName": "TestHorse",
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
        assert player_horse["name"] == "TestHorse"
        assert player_horse["position"] == 0

        max_dashes = 100
        race_complete = False

        for dash_count in range(max_dashes):
            time.sleep(1.1)  # Wait slightly more than 1 second between dashes
            dash_response = requests.post(f"{BASE_URL}/api/derby/dash",
                                        headers={"Content-Type": "application/json"})

            assert dash_response.status_code == 200
            dash_json = dash_response.json()
            assert dash_json["success"] == True

            if dash_json["race_over"]:
                race_complete = True
                break

            assert "horses" in dash_json
            assert "last_roll" in dash_json

            player_horse = None
            for horse in dash_json["horses"]:
                if horse["is_player"]:
                    player_horse = horse
                    break

            assert player_horse is not None
            assert player_horse["position"] >= 0

        assert race_complete, f"Race did not complete after {max_dashes} dashes"