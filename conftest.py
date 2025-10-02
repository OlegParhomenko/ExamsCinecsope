import pytest
import requests
import os
import random
from dotenv import load_dotenv
from faker import Faker
from constans import BASE_URL
from utils.data_generator import DataGenerator
from clients.api_manager import ApiManager
from resources.user_creds import SuperAdminCreds
from entities.user import User
from constans import Roles

faker = Faker()
load_dotenv()


@pytest.fixture(scope="function")
def test_user():
    """
    Генерация случайного пользователя для тестов.
    """
    random_email = DataGenerator.generate_random_email()
    random_name = DataGenerator.generate_random_name()
    random_password = DataGenerator.generate_random_password()

    return {
        "email": random_email,
        "fullName": random_name,
        "password": random_password,
        "passwordRepeat": random_password,
        "roles": [Roles.USER.value],
    }

@pytest.fixture(scope="session")
def admin_creds():
    username = os.getenv("ADMIN_USERNAME")
    password = os.getenv("ADMIN_PASSWORD")
    return username, password


@pytest.fixture(scope="session")
def session():
    s = requests.Session()
    yield s
    s.close()


@pytest.fixture(scope="session")
def api_manager(session, admin_creds):
    from clients.api_manager import ApiManager
    manager = ApiManager(session)
    manager.auth_api.authenticate(admin_creds)
    return manager


@pytest.fixture(scope="function")
def new_movie():
    return {
        "name": f"{DataGenerator.generate_movie_title()}_{random.randint(1000, 9999)}",
        "imageUrl": DataGenerator.generate_random_url(),
        "price": DataGenerator.generate_random_price(),
        "description": DataGenerator.generate_random_description(),
        "location": DataGenerator.generate_random_location(),
        "published": DataGenerator.generate_published(),
        "genreId": DataGenerator.generate_genre_id()
    }


@pytest.fixture(scope="function")
def create_movie_fixture(api_manager, new_movie):
    response = api_manager.movies_api.create_movie(new_movie, expected_status=201)
    response_data = response.json()
    movie_id = response_data["id"]

    yield {"id": movie_id, "response": response_data, "name": response_data["name"]}


@pytest.fixture(scope="session")
def new_params():
    return {
        "pageSize": DataGenerator.generate_pages_size(),
        "page": random.randint(1, 5),
        "minPrice": 1,
        "maxPrice": random.randint(2, 1000),
        "locations": DataGenerator.generate_random_location(),
        "published": DataGenerator.generate_published(),
        "genreId": DataGenerator.generate_genre_id(),
        "createdAt": DataGenerator.generate_created_at()
    }


@pytest.fixture(scope="session")
def login_user(api_manager, admin_creds):
    response_data = api_manager.auth_api.authenticate(admin_creds)

    assert "accessToken" in response_data, 'Токен доступа отсутствует'
    assert response_data["user"]["email"] == admin_creds[0]

    return response_data

@pytest.fixture
def user_session():
    user_pool = []

    def _create_user_session():
        session = requests.Session()
        user_session = ApiManager(session)
        user_pool.append(user_session)
        return user_session

    yield _create_user_session

    for user in user_pool:
        user.close_session()

@pytest.fixture(scope="function")
def creation_user_data(test_user):
    update_data = test_user.copy()

    update_data.update({
        "verified": True,
        "banned": False
    })

    return update_data


@pytest.fixture
def super_admin(user_session):
    new_session = user_session()

    super_admin = User(
        SuperAdminCreds.USERNAME,
        SuperAdminCreds.PASSWORD,
        [Roles.SUPER_ADMIN.value],
        new_session)

    super_admin.api.auth_api.authenticate(super_admin.creds)
    return super_admin

@pytest.fixture
def admin_user(user_session, super_admin, creation_user_data):
    new_session = user_session()

    admin = User(
        creation_user_data["email"],
        creation_user_data["password"],
        [Roles.ADMIN.value],
        new_session
    )

    super_admin.api.user_api.create_user(creation_user_data)
    admin.api.auth_api.authenticate(admin.creds)

    return admin

@pytest.fixture
def common_user(user_session, super_admin, creation_user_data):
    new_session = user_session()

    common_user = User(
        creation_user_data["email"],
        creation_user_data["password"],
        [Roles.USER.value],
        new_session
    )

    super_admin.api.user_api.create_user(creation_user_data)
    common_user.api.auth_api.authenticate(common_user.creds)
    return common_user
