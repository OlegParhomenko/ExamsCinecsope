from clients.api_manager import ApiManager
from utils.user_with_pydantic import TestUser, RegisterUserResponse

class TestAuthAPI:
    def test_register_user(self, api_manager: ApiManager, test_user):

        user_data = test_user.model_dump()

        user_data['roles'] = [role.value for role in user_data["roles"]]

        response = api_manager.auth_api.register_user(user_data)
        register_user_response = RegisterUserResponse(**response.json())

        assert register_user_response.email == test_user.email, "Email не совпадает"

    def test_register_and_login_user(self, api_manager: ApiManager, test_user: TestUser):

        user_data = test_user.model_dump(mode="json")

        register_response = api_manager.auth_api.register_user(user_data)
        assert register_response.status_code in [200, 201]

        login_data = {
            "email": user_data["email"],
            "password": user_data["password"]
        }
        login_response = api_manager.auth_api.login_user(login_data)
        login_response_data = login_response.json()

        assert "accessToken" in login_response_data
        assert login_response_data["user"]["email"] == user_data["email"]
