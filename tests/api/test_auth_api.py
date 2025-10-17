from clients.api_manager import ApiManager
from utils.user_with_pydantic import TestUser, RegisterUserResponse
import allure
import datetime
from utils.user_with_pydantic import Roles
import pytest_check as check


class TestAuthAPI:
    def test_register_user(self, api_manager: ApiManager, creation_user_data):

        user_data = TestUser(**creation_user_data)

        # user_data['roles'] = [role.value for role in user_data["roles"]]
        # print(user_data)
        response = api_manager.auth_api.register_user(user_data)
        register_user_response = RegisterUserResponse(**response.json())

        assert register_user_response.email == creation_user_data['email'], "Email не совпадает"

    def test_register_and_login_user(self, api_manager: ApiManager, creation_user_data):

        user_data = TestUser(**creation_user_data)

        register_response = api_manager.auth_api.register_user(user_data)
        RegisterUserResponse(**register_response.json())
        assert register_response.status_code in [200, 201]

        login_data = {
            "email": user_data.email,
            "password": user_data.password,
        }
        login_response = api_manager.auth_api.login_user(login_data)
        login_response_data = login_response.json()

        assert "accessToken" in login_response_data
        assert login_response_data["user"]["email"] == user_data.email

    @allure.title("Тест регистрации пользователя с помощью Mock")
    @allure.severity(allure.severity_level.MINOR)
    @allure.label("qa_name", "Ivan Petrovich")
    def test_register_user_mock(self, api_manager: ApiManager, test_user: TestUser, mocker):
            with allure.step(" Мокаем метод register_user в auth_api"):
                mock_response = RegisterUserResponse(  # Фиктивный ответ
                    id="id",
                    email="email@email.com",
                    fullName="fullName",
                    verified=True,
                    banned=False,
                    roles=[Roles.SUPER_ADMIN],
                    createdAt=str(datetime.datetime.now())
                )

                mocker.patch.object(
                    api_manager.auth_api,  # Объект, который нужно замокать
                    'register_user',  # Метод, который нужно замокать
                    return_value=mock_response  # Фиктивный ответ
                )

            with allure.step("Вызываем метод, который должен быть замокан"):
                register_user_response = api_manager.auth_api.register_user(test_user)

            with allure.step("Проверяем, что ответ соответствует ожидаемому"):
                with allure.step("Проверка поля персональных данных"):  # обратите внимание на вложенность allure.step
                    # Строка ниже выдаст исключение и, но выполнение теста продолжится
                    check.equal(register_user_response.fullName, "fullName", "НЕСОВПАДЕНИЕ fullName")
                    check.equal(register_user_response.email, mock_response.email)

                with allure.step("Проверка поля banned"):
                # можно использовать вместо allure.step
                    check.equal(register_user_response.banned, mock_response.banned)
