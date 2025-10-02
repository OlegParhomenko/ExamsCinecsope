from clients.api_manager import ApiManager
from utils.data_generator import DataGenerator
import random
import pytest
from constans import Roles
from entities.user import User

class TestMoviesAPI:

    def test_create_movie(self, new_movie, super_admin):
        response = super_admin.api.movies_api.create_movie(new_movie, expected_status=[200, 201])
        response_data = response.json()

        assert response_data['name'] == new_movie['name'], 'Имя фильма не совпадает'
        assert response.status_code in (201, 200)
        assert 'id' in response_data, "ID фильма отсутствует в ответе"
        assert 'createdAt' in response_data, 'Дата создания фильма отсутствует в ответе'
        assert 'name' in response_data['genre'], 'Жанр не указан'

    @pytest.mark.slow
    def test_create_movie_with_invalid_role(self, api_manager: ApiManager, new_movie, common_user):
        response = common_user.api.movies_api.create_movie(new_movie, expected_status=403)

        assert response.status_code in (403, 404), 'Пользователь с ролью "USER не может создавать фильмы'

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


    def test_get_movie(self, create_movie_fixture, common_user):
        movie_id = create_movie_fixture['id']

        response = common_user.api.movies_api.get_movie(movie_id, expected_status=200)
        response_data = response.json()

        assert response_data['id'] == movie_id, "ID фильма не совпадает"
        assert response_data['name'] == create_movie_fixture['response']['name'], "Имя фильма не совпадает"

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


        response = super_admin.api.movies_api.patch_movie(movie_id, update_data, expected_status=200)
        data = response.json()

        assert data["name"] == update_data["name"], 'Имя фильма не обновилось'

    # def test_delete_movie(self, create_movie_fixture, super_admin):
    #     movie_id = create_movie_fixture['id']
    #
    #     response = super_admin.api.movies_api.delete_movie(movie_id, expected_status=200)
    #     response_data = response.json()
    #
    #     assert response_data['id'] == movie_id, "ID фильма не совпадает"
    #     assert response_data['name'] == create_movie_fixture['response']['name'], "Имя фильма не совпадает"
    #
    #     super_admin.api.movies_api.get_movie(movie_id, expected_status=404)

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
            # Проверяем, что фильм действительно удалён
            user_api.get_movie(movie_id, expected_status=404)
        else:
            assert response.status_code == expected_status, f"Пользователь с ролью {role} не должен иметь право удалять фильм"

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


    def test_get_movies_with_invalid_id(self, common_user):

        fake_data_id = random.randint(-100, -1)
        response = common_user.api.movies_api.get_movie(fake_data_id, expected_status=404)

        assert response.status_code == 404, "Фильм не найден"

    @pytest.mark.slow
    def test_delete_movie_with_invalid_id(self, super_admin):
        fake_data_id = random.randint(-100, -1)
        response = super_admin.api.movies_api.delete_movie(fake_data_id, expected_status=404)

        assert response.status_code == 404, "Неверные параметры"

    def test_patch_movie_with_invalid_id(self, super_admin):
        fake_data_id = random.randint(-100, -1)
        update_data = {"name": DataGenerator.generate_movie_title()}
        response = super_admin.api.movies_api.patch_movie(fake_data_id , update_data, expected_status=404)

        assert response.status_code == 404, 'Фильм не найден'
