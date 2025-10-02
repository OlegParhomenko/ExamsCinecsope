from custom_requester.custom_requester import CustomRequester


class UserApi(CustomRequester):
    USER_BASE_URL = "https://auth.dev-cinescope.coconutqa.ru/"

    def __init__(self, session):
        self.session = session
        super().__init__(session, self.USER_BASE_URL)

    def get_user(self, user_locator):
        return self.send_request("GET", f"user/{user_locator}")

    def create_user(self, user_data, expected_status=201):
        return self.send_request(
            method="POST",
            endpoint="user",
            json=user_data,
            expected_status=expected_status
        )
