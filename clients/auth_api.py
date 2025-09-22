from constans import LOGIN_ENDPOINT, LOGIN_URL
from custom_requester.custom_requester import CustomRequester

class AuthAPI(CustomRequester):
    def __init__(self, session):
        super().__init__(session=session, base_url=LOGIN_URL.rstrip('/'))

    def login_user(self, login_data, expected_status=None):
        if expected_status is None:
            expected_status = [200, 201]

        return self.send_request(
            method="POST",
            endpoint=LOGIN_ENDPOINT,
            json=login_data,
            expected_status=expected_status
        )

    def authenticate(self, user_creds, expected_status=None):
        if expected_status is None:
            expected_status = [200, 201]

        login_data = {
            "email": user_creds[0],
            "password": user_creds[1]
        }

        response_json = self.login_user(login_data, expected_status=expected_status).json()

        token = response_json.get("accessToken")
        if not token:
            raise KeyError("token is missing")


        self._update_session_headers(self.session, Authorization=f"Bearer {token}")

        return {
            "accessToken": token,
            "user": response_json.get("user")
        }
