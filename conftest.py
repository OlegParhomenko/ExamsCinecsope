import pytest
import requests
import os
import random
from dotenv import load_dotenv
from faker import Faker
from constans import MOVIES_ENDPOINT, BASE_URL
from custom_requester.custom_requester import CustomRequester
from tests.api.auth_api import AuthAPI
from tests.api.api_manager import ApiManager
from utils.data_generator import DataGenerator

faker = Faker()
load_dotenv()

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
def requester(api_manager):
    from custom_requester.custom_requester import CustomRequester
    return CustomRequester(session=api_manager.session, base_url=BASE_URL)

@pytest.fixture(scope="session")
def api_manager(session, admin_creds):
    from tests.api.api_manager import ApiManager
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
