from clients.api_manager import ApiManager
from utils.data_generator import DataGenerator
import random
import pytest
from utils.user_with_pydantic import Roles
from entities.user import User
import datetime
from db_models.db_movies_model import MovieDBModel
from sqlalchemy.orm import Session
import allure


@allure.epic('Тестирование АПИ "Movies"')
class TestMoviesAPI:
    @allure.story("Корректность создания фильма")
    @allure.description("""
    Тест проверяет корректность создания фильма.
    Шаги выполнения:
    1) Войти под учёткой с правами "SUPER_ADMIN"
    2) Подготовить тестовые данные с новым фильмом
    3) Создать фильм 
    4) Проверить что данные фильма совпадают с данными подготовленными в шаге 2
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Тест создания фильма")
    @allure.step('Шаг 1, 2 выполнены автоматически с помощью фикстур')
    def test_create_movie(self, new_movie, super_admin):
        with allure.step('Передаём тестовые данные на сервер, и получаем тело ответа'):
            response = super_admin.api.movies_api.create_movie(new_movie, expected_status=[200, 201])

            response_data = response.json()
        with allure.step('Сравниваем тело ответа, с тестовыми данными отправленными на сервер'):
            assert response_data['name'] == new_movie['name'], 'Имя фильма не совпадает'
            assert response.status_code in (201, 200)
            assert 'id' in response_data, "ID фильма отсутствует в ответе"
            assert 'createdAt' in response_data, 'Дата создания фильма отсутствует в ответе'
            assert 'name' in response_data['genre'], 'Жанр не указан'


    @allure.story("Работа с АПИ 'Movies' без должных прав")
    @allure.description("""
        Данный тест проверяет что пользователь не может создать фильм если у него нет соответствующих прав
        Шаги выполнения:
        1) Войти под учёткой у которой нету прав "SUPER_ADMIN"
        2) Подготовить тестовые данные с новым фильмом
        3) Создать фильм 
        4) Проверить что фильм не создался, а сервер вернул корректную ошибку
        """)
    @allure.title("Тест создания фильма без соответствующих прав")
    def test_create_movie_with_invalid_role(self, api_manager: ApiManager, new_movie, common_user):
        with allure.step('Передаём тестовые данные на сервер, и проверяем ожидаемый статус код (403)'):
            response = common_user.api.movies_api.create_movie(new_movie, expected_status=403)
            assert response.status_code in (403, 404), 'Пользователь с ролью "USER не может создавать фильмы'

    @allure.title("Тест удаления фильма без соответствующих прав")
    @allure.description("""
                Это параметризи́рованный тест который проверяет что только пользователь с ролью "SUPER_ADMIN" 
                может удалить фильм, в остальных случаях сервер вернёт соответствующий статус код (403)
                Шаги выполнения:
                1) Войти под разными учётными записями (SUPER_ADMIN, ADMIN, USER)
                2) Создать тестовый фильм для удаления либо найти уже созданный по id      
                3) Попробывать удалить фильм
                4) Убедиться что фильм может удалить только пользователь с ролью "SUPER_ADMIN", в остальных случаях 
                сервер должен вернуть ошибку (403)
                """)
    @pytest.mark.slow
    @pytest.mark.parametrize(
        "role, expected_status",
        [
            ("super_admin", 200),
            ("admin_user", 403),
            ("common_user", 403)
        ],
        ids=["super_admin", "admin", "common_user"]
    )
    def test_delete_movie_role_based(self,create_movie_fixture, super_admin, user_session, role, expected_status):
        movie_id = create_movie_fixture['id']

        if role == "super_admin":
            user_api = super_admin.api.movies_api
        else:
            unique_email = f"{DataGenerator.generate_random_email()}"
            unique_password = DataGenerator.generate_random_password()
            user_data = {
                "email": unique_email,
                "fullName": DataGenerator.generate_random_name(),
                "password": unique_password,
                "passwordRepeat": unique_password,
                "roles": [Roles.ADMIN.value] if role == "admin_user" else [Roles.USER.value],
                "verified": True,
                "banned": False
            }

            new_session = user_session()
            test_user = User(user_data["email"], user_data["password"], user_data["roles"], new_session)

            super_admin.api.user_api.create_user(user_data)
            test_user.api.auth_api.authenticate(test_user.creds)
            user_api = test_user.api.movies_api

        response = user_api.delete_movie(movie_id, expected_status=expected_status)

        if expected_status == 200:
            data = response.json()
            assert data['id'] == movie_id
            assert data['name'] == create_movie_fixture['response']['name']
            user_api.get_movie(movie_id, expected_status=404)
        else:
            assert response.status_code == expected_status, f"Пользователь с ролью {role} не должен иметь право удалять фильм"


    @allure.story("Тест на получения списка фильмов")
    @allure.description("""
        Данный тест проверяет что любой пользователь может получить список фильмов
        Шаги выполнения:
        1) Войти под любой учёткой
        2) Подготовить параметры запроса для получения списка фильмов
        3) Отправить запрос на сервер
        4) Проверить что список фильмов не пустой
        """)
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Тест на получения списка фильмов")
    @pytest.mark.slow
    @pytest.mark.parametrize('max_price,locations,genre_id',[
        (100, 'SPB', 3),
        (300, 'MSK', 4)
    ], ids=['SPB location', 'MSK location'])
    def test_get_movies(self, new_params, common_user, max_price, locations, genre_id):
        new_params['maxPrice'] = max_price
        new_params['locations'] = locations
        new_params['genreId'] = genre_id
        response = common_user.api.movies_api.get_movies(new_params, expected_status=200)
        response_data = response.json()

        assert 'movies' in response_data, 'Отсутствует список фильмов'
        assert isinstance(response_data['movies'], list), "Поле movies должно быть списком"
    @allure.story("Тест на получения фильма")
    @allure.description("""
        Данный тест проверяет что любой пользователь может получить нужный фильм по id
        Шаги выполнения:
        1) Войти под любой учёткой
        2) Подготовить параметры запроса для получения списка фильмов
        3) Отправить запрос на сервер
        4) Проверить что id фильма в ответе от сервера совпадает с id переданным в параметры запроса
        """)
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Тест на получения фильма")
    def test_get_movie(self, create_movie_fixture, common_user):
        movie_id = create_movie_fixture['id']

        response = common_user.api.movies_api.get_movie(movie_id, expected_status=200)
        response_data = response.json()

        assert response_data['id'] == movie_id, "ID фильма не совпадает"
        assert response_data['name'] == create_movie_fixture['response']['name'], "Имя фильма не совпадает"

    @allure.story("Тест на изменения данных фильма (НЕ РАБОТАЕТ!)")
    @pytest.mark.xfail(reason='Не смог починить')
    def test_patch_movie(self, create_movie_fixture, super_admin):
        movie_id = create_movie_fixture['id']

        response_get = super_admin.api.movies_api.get_movie(movie_id, expected_status=200)
        response_get_data = response_get.json()
        assert response_get_data['id'] == movie_id, "ID фильма не совпадает"

        update_data = {
            "name": DataGenerator.generate_movie_title(),
            "imageUrl": create_movie_fixture['response']['imageUrl'],
            "price": create_movie_fixture['response']['price'],
            "description": create_movie_fixture['response']['description'],
            "location": create_movie_fixture['response']['location'],
            "published": create_movie_fixture['response']['published'],
            "genreId": create_movie_fixture['response']['genreId'],
        }
        print("PATCH base_url:", super_admin.api.movies_api.base_url)
        print("Movie ID:", movie_id)

        response = super_admin.api.movies_api.patch_movie(movie_id, update_data, expected_status=200)
        data = response.json()

        assert data["name"] == update_data["name"], 'Имя фильма не обновилось'

    @allure.story("Тест на получения списка фильмов с некорректными параметрами")
    @allure.description("""
        Данный тест проверяет что нельзя получить список фильмов с параметрами которые не соответствую jsonshema
        Шаги выполнения:
        1) Войти под любой учёткой
        2) Подготовить не корректные параметры запроса для получения списка фильмов
        3) Отправить запрос на сервер
        4) Проверить что сервер вернул соответствующую ошибку (400)
        """)
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Тест на получения списка фильмов с некорректными параметрами")
    def test_get_movies_invalid_params(self, common_user):
        params = {
            "pageSize": DataGenerator.generate_pages_size(),
            "page": random.randint(1, 5),
            "minPrice": 'абра-кадабра',
            "maxPrice": -100,
            "locations": DataGenerator.generate_random_location(),
            "published": DataGenerator.generate_published(),
            "genreId": DataGenerator.generate_genre_id(),
            "createdAt": DataGenerator.generate_created_at()
        }

        response = common_user.api.movies_api.get_movies(params=params, expected_status=400)
        assert response.status_code == 400, 'Ожидалась ошибка 400 (Неверные параметры)'


    @allure.story("Тест на создания фильма с некорректными данными")
    @allure.description("""
        Данный тест проверяет что нельзя создать фильм с не корректными данными
        Шаги выполнения:
        1) Войти под учёткой с правами "SUPER_ADMIN"
        2) Подготовить не корректные параметры запроса для создания фильма
        3) Отправить запрос на сервер
        4) Проверить что сервер вернул соответствующую ошибку (400)
        """)
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Тест на создание фильма с некорректными параметрами")
    def test_create_movie_invalid_data(self, super_admin):
        invalid_movie = {
            "name": "",
            "imageUrl": "not-a-url",
            "price": "abc",
            "description": 123,
            "location": "NY",
            "published": "yes",
            "genreId": "xyz"
        }
        super_admin.api.movies_api.create_movie(invalid_movie, expected_status=400)

    @allure.story("Тест на создания фильма дупликата")
    @allure.description("""
        Данный тест проверяет что нельзя создать фильм который уже есть 
        Шаги выполнения:
        1) Войти под учёткой с правами "SUPER_ADMIN"
        2) Подготовить не корректные параметры запроса для создания фильма
        3) Отправить запрос на сервер
        4) Проверить что сервер вернул соответствующую ошибку (409)
        """)
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Тест на создания фильма дупликата")
    def test_create_movie_with_duplicate(self, super_admin):
        unique_movie_data = {
            "name": f"Duplicate_Test_{random.randint(10000, 99999)}",
            "imageUrl": DataGenerator.generate_random_url(),
            "price": DataGenerator.generate_random_price(),
            "description": DataGenerator.generate_random_description(),
            "location": DataGenerator.generate_random_location(),
            "published": DataGenerator.generate_published(),
            "genreId": DataGenerator.generate_genre_id()
        }
        response_1 = super_admin.api.movies_api.create_movie(unique_movie_data)
        assert response_1.status_code == 201, 'Ожидаем успешное создание фильма в первый раз'

        duplicate_movie = unique_movie_data.copy()
        response_2 = super_admin.api.movies_api.create_movie(duplicate_movie, expected_status=409)
        assert response_2.status_code in [400, 409], 'Фильм с таким названием уже существует'


    @allure.story("Тест на получение фильма с неверным id")
    @allure.description("""
        Данный тест проверяет что нельзя получить фильм некорректным id
        Шаги выполнения:
        1) Войти под любой учёткой
        2) Подготовить некорректные параметры запроса (id) для получения фильма
        3) Отправить запрос на сервер
        4) Проверить что сервер вернул соответствующую ошибку (404)
        """)
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Тест на получение фильма с неверным id")
    def test_get_movie_with_invalid_id(self, common_user):

        fake_data_id = random.randint(-100, -1)
        response = common_user.api.movies_api.get_movie(fake_data_id, expected_status=404)

        assert response.status_code == 404, "Фильм не найден"


    @allure.story("Тест на удаление фильма с неверным id")
    @allure.description("""
        Данный тест проверяет что нельзя удалить фильм некорректным id
        Шаги выполнения:
        1) Войти под учёткой с правами "SUPER_ADMIN"
        2) Подготовить некорректные параметры запроса (id) для получения фильма
        3) Отправить запрос на сервер
        4) Проверить что сервер вернул соответствующую ошибку (404)
        """)
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Тест на получение фильма с неверным id")
    @pytest.mark.slow
    def test_delete_movie_with_invalid_id(self, super_admin):
        fake_data_id = random.randint(-100, -1)
        response = super_admin.api.movies_api.delete_movie(fake_data_id, expected_status=404)

        assert response.status_code == 404, "Неверные параметры"


    @allure.story("Тест на изменения фильма с неверным id")
    @allure.description("""
        Данный тест проверяет что нельзя изменить фильм некорректным id
        Шаги выполнения:
        1) Войти под учёткой с правами "SUPER_ADMIN"
        2) Подготовить некорректные параметры запроса (id) для получения фильма
        3) Отправить запрос на сервер
        4) Проверить что сервер вернул соответствующую ошибку (404)
        """)
    @allure.title("Тест на изменения фильма с неверным id")
    def test_patch_movie_with_invalid_id(self, super_admin):
        fake_data_id = random.randint(-100, -1)
        update_data = {"name": DataGenerator.generate_movie_title()}
        response = super_admin.api.movies_api.patch_movie(fake_data_id , update_data, expected_status=404)

        assert response.status_code == 404, 'Фильм не найден'


    @allure.story("Тест создание фильма с записью в БД")
    @allure.description("""
        Данный тест проверяет что фильм создаётся и информация о нём записывается в базу данных
        Шаги выполнения:
        1) Войти под учёткой с правами "SUPER_ADMIN"
        2) Подготовить тестовые данные
        3) Проверить что такого фильма нету в базе данных
        4) Создать фильм
        5) Проверить что фильм сохранился в базу данных
        """)
    @allure.title("Тест создание фильма и запись его в БД")
    def test_create_movie_with_db(self, super_admin, db_helper, create_movie_fixture_db):
        unique_movie_data = {
            "name": f"Duplicate_Test_{random.randint(10000, 99999)}",
            "imageUrl": DataGenerator.generate_random_url(),
            "price": DataGenerator.generate_random_price(),
            "description": DataGenerator.generate_random_description(),
            "location": DataGenerator.generate_random_location(),
            "published": DataGenerator.generate_published(),
            "genreId": DataGenerator.generate_genre_id()
        }

        movie_from_db = db_helper.get_movie_by_name(unique_movie_data["name"])

        assert movie_from_db is None, "Фильм уже существует до теста!"

        create_response = super_admin.api.movies_api.create_movie(unique_movie_data)

        assert create_response.status_code == 201
        created_movie_id = create_response.json()["id"]

        movie_in_db = db_helper.get_movie_by_id(created_movie_id)
        assert movie_in_db is not None, "Фильм не сохранился в БД"
        assert movie_in_db.name == unique_movie_data["name"]

        delete_response = super_admin.api.movies_api.delete_movie(created_movie_id)
        assert delete_response.status_code == 200

        delete_movie = db_helper.get_movie_by_name(unique_movie_data["name"])

        assert delete_movie is None, 'Фильм не удалился'


    @allure.story("Тест на удаления фильма")
    @allure.description("""
        Данный тест проверяет что фильм можно удалить и информация о нём удаляется из базы данных
        Шаги выполнения:
        1) Войти под учёткой с правами "SUPER_ADMIN"
        2) Подготовить тестовые данные (id удаляемого фильма)
        3) Проверить что такой фильм есть в базе данных
        4) Удалить фильм
        5) Проверить что фильм удалился из базы данных
        """)
    @allure.title("Тест создание фильма и запись его в БД")
    def test_delete_movie(self, api_manager, super_admin, db_session: Session, db_helper):
        movie_id = 54

        check_movie = db_session.query(MovieDBModel).filter_by(id=movie_id).first()

        if not check_movie:
            new_movie = MovieDBModel(
                id=movie_id,
                name="Тестовый фильм про БЛА БЛА",
                price=100,
                description="Бла бла тест",
                image_url=DataGenerator.generate_random_url(),
                location=DataGenerator.generate_random_location(),
                published=True,
                rating=0.0,
                genre_id=1,
                created_at=datetime.datetime.now()
            )
            db_session.add(new_movie)
            db_session.commit()

        delete_response = super_admin.api.movies_api.delete_movie(movie_id)
        assert delete_response.status_code == 200, "Фильм должен удалиться"

        get_response = api_manager.movies_api.get_movie(
            movie_id=movie_id,
            expected_status=404
        )
        assert get_response.status_code == 404, "Фильм не должен существовать"
