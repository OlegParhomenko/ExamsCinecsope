from utils.user_with_pydantic import TestUser, RegisterUserResponse


class TestUserAPI:

    def test_create_user(self, super_admin, creation_user_data):

        user_data = TestUser(**creation_user_data)
        response = super_admin.api.user_api.create_user(user_data).json()

        RegisterUserResponse(**response)


    def test_get_user_by_locator(self, super_admin, creation_user_data):
        user_to_create  = TestUser(**creation_user_data)
        created_user_response = super_admin.api.user_api.create_user(user_to_create ).json()

        RegisterUserResponse(**created_user_response)

        response_by_id = RegisterUserResponse(**super_admin.api.user_api.get_user(created_user_response['id']).json())
        response_by_email = RegisterUserResponse(**super_admin.api.user_api.get_user(creation_user_data['email']).json())

        assert response_by_id == response_by_email, "Содержание ответов должно быть идентичным"
        assert response_by_id.id and response_by_id.id != '', "ID должен быть не пустым"
        assert response_by_id.email == user_to_create.email
        assert response_by_id.fullName == user_to_create.fullName
        assert response_by_id.roles == user_to_create.roles
        assert response_by_id.verified is True

    def test_db_requests(self, super_admin, db_helper, created_test_user_db):
        assert created_test_user_db == db_helper.get_user_by_id(created_test_user_db.id)
        assert db_helper.user_exists_by_email("api1@gmail.com")
