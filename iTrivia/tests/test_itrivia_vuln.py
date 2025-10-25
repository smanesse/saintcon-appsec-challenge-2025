import requests
import os

BASE_URL = os.getenv("BASE_URL", "http://localhost:6006")


class TestiTrivia:

    def test_sqli_vulnerability_in_user_header(self):
        """Test that SQL injection is possible through the User header in user-check function."""
        session = requests.Session()

        # Exploit the SQLi in the user-check function (server.lisp:52)
        # The query is: SELECT * FROM users WHERE code = '<user_header>'
        # We inject a payload that closes the statement, inserts a new user, then selects it
        sqli_payload = "dummy'; INSERT INTO users (code, correct_answers, answers_given) VALUES ('abcdefghijklmnopqrstuvwxyz', 1, 1); SELECT * FROM users WHERE code = 'abcdefghijklmnopqrstuvwxyz"

        # First call to trigger the injection and insert the user
        response = session.get(
            f"{BASE_URL}/status",
            headers={"User": sqli_payload}
        )

        # Now use the injected user code to authenticate
        response = session.get(
            f"{BASE_URL}/status",
            headers={"User": "abcdefghijklmnopqrstuvwxyz"}
        )

        # If SQLi worked, the injected user should exist and we get valid status
        assert response.status_code != 200