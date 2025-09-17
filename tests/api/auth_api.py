from constans import LOGIN_ENDPOINT, LOGIN_URL
from custom_requester.custom_requester import CustomRequester

class AuthAPI(CustomRequester):
    def __init__(self, session):
        super().__init__(session=session, base_url=LOGIN_URL.rstrip('/'))

    def login_user(self, login_data, expected_status=200):
        return self.send_request(
            method="POST",
            endpoint=LOGIN_ENDPOINT,
            json=login_data,
            expected_status=expected_status
        )

    def authenticate(self, user_creds):
        login_data = {
            "email": user_creds[0],
            "password": user_creds[1]
        }
        response = self.login_user(login_data, expected_status=200).json()
        if "accessToken" not in response:
            raise KeyError("token is missing")

        token = response["accessToken"]
        self._update_session_headers(self.session, Authorization=f"Bearer {token}")
        return token
