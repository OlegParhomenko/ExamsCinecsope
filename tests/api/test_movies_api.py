from .api_manager import ApiManager
from utils.data_generator import DataGenerator
import random
import pytest


class TestMoviesAPI:

    def test_login_user(self, api_manager: ApiManager, admin_creds):
        login_data = {
            "email": admin_creds[0],
            "password": admin_creds[1]
        }
        response = api_manager.auth_api.login_user(login_data)
        response_data = response.json()
        assert "accessToken" in response_data, 'Токен доступа отсутствует'
        assert response_data["user"]["email"] == admin_creds[0]


    def test_create_movie(self, api_manager: ApiManager, new_movie):
        response = api_manager.movies_api.create_movie(new_movie, expected_status=201)
        response_data = response.json()

        assert response_data['name'] == new_movie['name'], 'Имя фильма не совпадает'
        assert 'id' in response_data, "ID фильма отсутствует в ответе"
        assert 'createdAt' in response_data, 'Дата создания фильма отсутствует в ответе'
        assert 'name' in response_data['genre'], 'Жанр не указан'


    def test_get_movie(self, api_manager: ApiManager, create_movie_fixture):
        movie_id = create_movie_fixture['id']

        response = api_manager.movies_api.get_movie(movie_id, expected_status=200)
        response_data = response.json()

        assert response_data['id'] == movie_id, "ID фильма не совпадает"
        assert response_data['name'] == create_movie_fixture['response']['name'], "Имя фильма не совпадает"


    def test_get_movies(self, api_manager: ApiManager, new_params):
        response = api_manager.movies_api.get_movies(new_params, expected_status=200)
        response_data = response.json()

        assert 'movies' in response_data, 'Отсутствует список фильмов'
        assert isinstance(response_data['movies'], list), "Поле movies должно быть списком"


    def test_patch_movie(self, api_manager: ApiManager, create_movie_fixture):
        movie_id = create_movie_fixture['id']

        update_data = {"name": DataGenerator.generate_movie_title()}
        response = api_manager.movies_api.patch_movie(movie_id, update_data, expected_status=200)
        data = response.json()

        assert data["name"] == update_data["name"], 'Имя фильма не обновилось'



    def test_delete_movie(self, api_manager: ApiManager, create_movie_fixture):
        movie_id = create_movie_fixture['id']

        response = api_manager.movies_api.delete_movie(movie_id, expected_status=200)
        response_data = response.json()

        assert response_data['id'] == movie_id, "ID фильма не совпадает"
        assert response_data['name'] == create_movie_fixture['response']['name'], "Имя фильма не совпадает"



    def test_get_movies_invalid_params(self, api_manager: ApiManager):
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

        response = api_manager.movies_api.get_movies(params=params, expected_status=400)
        assert response.status_code == 400, 'Ожидалась ошибка 400 (Неверные параметры)'


    def test_create_movie_invalid_data(self, api_manager: ApiManager):
        invalid_movie = {
            "name": "",
            "imageUrl": "not-a-url",
            "price": "abc",
            "description": 123,
            "location": "NY",
            "published": "yes",
            "genreId": "xyz"
        }
        response = api_manager.movies_api.create_movie(invalid_movie, expected_status=400)
        assert response.status_code == 400


    def test_create_movie_with_duplicate(self, api_manager: ApiManager):
        unique_movie_data = {
            "name": f"Duplicate_Test_{random.randint(10000, 99999)}",
            "imageUrl": DataGenerator.generate_random_url(),
            "price": DataGenerator.generate_random_price(),
            "description": DataGenerator.generate_random_description(),
            "location": DataGenerator.generate_random_location(),
            "published": DataGenerator.generate_published(),
            "genreId": DataGenerator.generate_genre_id()
        }
        response_1 = api_manager.movies_api.create_movie(unique_movie_data)
        assert response_1.status_code == 201, 'Ожидаем успешное создание фильма в первый раз'

        duplicate_movie = unique_movie_data.copy()
        response_2 = api_manager.movies_api.create_movie(duplicate_movie, expected_status=409)
        assert response_2.status_code in [400, 409], 'Фильм с таким названием уже существует'


    def test_get_movies_with_invalid_id(self, api_manager: ApiManager):

        fake_data_id = random.randint(-100, -1)

        response = api_manager.movies_api.get_movie(fake_data_id, expected_status=404)

        assert response.status_code == 404, "Фильм не найден"

    def test_delete_movie_with_invalid_id(self, api_manager: ApiManager):
        fake_data_id = random.randint(-100, -1)
        response = api_manager.movies_api.delete_movie(fake_data_id, expected_status=404)

        assert response.status_code == 404, "Неверные параметры"

    def test_patch_movie_with_invalid_id(self, api_manager: ApiManager):
        fake_data_id = random.randint(-100, -1)
        update_data = {"name": DataGenerator.generate_movie_title()}
        response = api_manager.movies_api.patch_movie(fake_data_id , update_data, expected_status=404)

        assert response.status_code == 404, 'Фильм не найден'
