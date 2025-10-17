import pytest
import requests
import os
import random
from dotenv import load_dotenv
from faker import Faker
from utils.data_generator import DataGenerator
from clients.api_manager import ApiManager
from resources.user_creds import SuperAdminCreds
from entities.user import User
from utils.user_with_pydantic import Roles, TestUser
from sqlalchemy.orm import Session
from db_requester.db_client import get_db_session
from db_requester.db_helpers import DBHelper
from utils.movies_with_pydantic import TestMovies
from enum import Enum
from Tools import Tools

faker = Faker()
load_dotenv()

DEFAULT_TIMEOUT = 30000

@pytest.fixture(scope="session")
def browser(playwright):
    browser = playwright.chromium.launch(headless=False, slow_mo=50)
    yield browser
    browser.close()


@pytest.fixture(scope="function")
def context(browser):
    context = browser.new_context()
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    context.set_default_timeout(DEFAULT_TIMEOUT)
    yield context
    log_name = f"trace_{Tools.get_timestamp()}.zip"
    trace_path = Tools.files_dir('playwright_trace', log_name)
    context.tracing.stop(path=trace_path)
    context.close()


@pytest.fixture(scope="function")
def page(context):
    page = context.new_page()
    yield page
    page.wait_for_timeout(DEFAULT_TIMEOUT)
    page.close()


@pytest.fixture(scope="function")
def db_helper(db_session) -> DBHelper:
    """
    Фикстура для экземпляра хелпера
    """
    db_helper = DBHelper(db_session)
    return db_helper


@pytest.fixture(scope="module")
def db_session() -> Session:
    """
    Фикстура, которая создает и возвращает сессию для работы с базой данных
    После завершения теста сессия автоматически закрывается
    """
    db_session = get_db_session()
    yield db_session
    db_session.close()

    
@pytest.fixture(scope="function")
# в примере это registration_user_data
def test_user() -> TestUser:
    """
    Генерация случайного пользователя для тестов.
    """
    random_email = DataGenerator.generate_random_email()
    random_name = DataGenerator.generate_random_name()
    random_password = DataGenerator.generate_random_password()

    return TestUser(
        email=random_email,
        fullName=random_name,
        password=random_password,
        passwordRepeat=random_password,
        roles=[Roles.USER]
    )
    # return user.model_dump(exclude_unset=True)


@pytest.fixture(scope="function")
def created_test_user_db(db_helper):
    """
    Фикстура, которая создает тестового пользователя в БД
    и удаляет его после завершения теста
    """

    user_data = DataGenerator.generate_user_data()
    user_data["verified"] = True
    user_data["banned"] = False
    user = db_helper.create_test_user(user_data)
    yield user
    # Cleanup после теста
    if db_helper.get_user_by_id(user.id):
        db_helper.delete_user(user)


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
def new_movie() -> TestMovies:
    name = f"{DataGenerator.generate_movie_title()}_{random.randint(1000, 9999)}"
    image_url = DataGenerator.generate_random_url()
    price = DataGenerator.generate_random_price()
    description = DataGenerator.generate_random_description()
    location = DataGenerator.generate_random_location()
    published = DataGenerator.generate_published()
    genre_id = DataGenerator.generate_genre_id()


    return TestMovies(
        name=name,
        imageUrl=image_url,
        price=price,
        description=description,
        location=location,
        published=published,
        genreId=genre_id,
    )

@pytest.fixture(scope="function")
def create_movie_fixture(api_manager, new_movie):
    new_movie_data = new_movie.model_dump()

    if isinstance(new_movie_data.get("location"), Enum):
        new_movie_data["location"] = new_movie_data["location"].value

    response = api_manager.movies_api.create_movie(new_movie_data, expected_status=201)
    response_data = response.json()
    movie_id = response_data["id"]

    yield {"id": movie_id, "response": response_data, "name": response_data["name"]}


@pytest.fixture(scope="function")
def create_movie_fixture_db(db_helper, new_movie):
    import datetime

    movie_data = {
        "name": new_movie.get("name"),
        "price": new_movie.get("price"),
        "description": new_movie.get("description"),
        "image_url": new_movie.get("imageUrl"),
        "location": new_movie.get("location"),
        "published": new_movie.get("published"),
        "rating": new_movie.get("rating", 0.0),
        "genre_id": new_movie.get("genreId"),
        "created_at": new_movie.get("created_at") or datetime.datetime.now()
    }

    movie_obj = db_helper.create_test_movie(movie_data)

    yield movie_obj

    movie_from_db = db_helper.get_movie_by_id(movie_obj.id)
    if movie_from_db:
        db_helper.delete_movie(movie_from_db)


# @pytest.fixture(scope="function")
# def create_movie_fixture_db(db_helper, new_movie):
#     movie = db_helper.create_test_movie(new_movie)
#     yield movie
#     # Cleanup после теста
#     if db_helper.get_movie_by_id(movie["id"]):
#         db_helper.delete_movie(movie["id"])



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
def creation_user_data(test_user: TestUser):
    user = test_user.model_copy(update={
        "verified": True,
        "banned": False
    })
    # return json.loads(user.model_dump_json())  # словарь с roles как строками
    return user.model_dump(mode="json") # возвращает словарь с enum преобразованным в строку


@pytest.fixture
def super_admin(user_session):
    new_session = user_session()

    super_admin = User(
        SuperAdminCreds.USERNAME,
        SuperAdminCreds.PASSWORD,
        [Roles.SUPER_ADMIN],
        new_session)

    super_admin.api.auth_api.authenticate(super_admin.creds)
    return super_admin


@pytest.fixture
def admin_user(user_session, super_admin, creation_user_data):
    new_session = user_session()

    admin = User(
        creation_user_data["email"],
        creation_user_data["password"],
        [Roles.ADMIN],
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
        [Roles.USER],
        new_session
    )

    super_admin.api.user_api.create_user(creation_user_data)
    common_user.api.auth_api.authenticate(common_user.creds)
    return common_user
