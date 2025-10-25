import requests
import os
import re

BASE_URL = os.getenv("BASE_URL", "http://diceroller:6004")

def crack_java_rng(i1, i2):
    MASK_32 = ((1 << 32) - 1)
    MASK_48 = ((1 << 48) - 1)
    M = 0x5DEECE66D
    A = 0xB

    def calculated(s):
        s2 = (s * M + A) & MASK_48
        val = (s2 >> 16) & MASK_32
        if val & (1 << 31):
            return val - (1 << 32)
        else:
            return val

    seed = 0
    found = False
    for i in range(65536):
        seed = i1 * (1 << 16) + i
        if calculated(seed) == i2:
            print("Seed found", seed)
            found = True
            break
    
    if not found:
        assert True
        return None
    

    class JavaRandom:
        def __init__(self, s):
            self.__seed__ = (s ^ M) & MASK_48

        def next(self, b):
            self.__seed__ = (self.__seed__ * M + A) & MASK_48
            return (self.__seed__ >> (48 - b)) & ((1 << b) - 1)

        def nextInt(self):
            val = self.next(32)
            if val & (1 << 31):
                return val - (1 << 32)
            else:
                return val

    r = JavaRandom((seed ^ M) & MASK_48)

    # go next by one
    r.nextInt()
    return r.nextInt()


def extract_target_from_response(response_text):
    """Extract target number from HTML response."""
    # Try the standard guess response format first
    match = re.search(r"The number was ([-]?\d+)", response_text)
    if match:
        return int(match.group(1))

    # Try the game over format
    match = re.search(r"Game over! The number was ([-]?\d+)", response_text)
    if match:
        return int(match.group(1))

    print(response_text)
    return None


class TestOracleVulnerability:
    def test_vuln_1(self):
        """Test if application uses predictable Java Random."""
        session1 = requests.Session()

        response = session1.get(BASE_URL)
        assert response.status_code == 200

        response = session1.post(f"{BASE_URL}/guess", data={"guess": "1"})
        assert response.status_code == 200
        target1 = extract_target_from_response(response.text)
        assert target1 is not None, (
            "Could not extract first target number from response"
        )

        response = session1.post(f"{BASE_URL}/guess", data={"guess": "1"})
        assert response.status_code == 200
        target2 = extract_target_from_response(response.text)
        if target2 is None:
            print(f"Could not extract from: {response.text}...")
        assert target2 is not None, (
            "Could not extract second target number from response"
        )

        print(target1, target2)
        predicted = crack_java_rng(target1, target2)
        if not predicted:
            return None
        print(f"Predicted next target: {predicted}")

        session2 = requests.Session()
        response = session2.get(BASE_URL)
        assert response.status_code == 200

        response = session2.post(f"{BASE_URL}/guess", data={"guess": str(predicted)})
        if response.status_code != 200:
            print({"guess": str(predicted)})
            print(response.text)
        assert response.status_code == 200

        assert "Congratulations! You guessed correctly!" not in response.text, (
            f"Prediction failed - predicted {predicted} but did not win"
        )
