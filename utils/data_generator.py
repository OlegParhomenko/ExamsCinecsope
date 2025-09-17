import random
import string

import pytest
from faker import Faker
faker = Faker()


class DataGenerator:
    @staticmethod
    def generate_movie_title():
        horror_movies = [
            "Звонок",
            "Кошмар на улице Вязов",
            "Пила",
            "Сияние",
            "Заклятие",
            "Хэллоуин"
        ]

        words = [
            'Смешнявка',
            "Котик",
            "Сковородка",
            "Пельмень",
            "НЛО",
            "Утюг",
            'Скуфа'
        ]

        horror_part = random.choice(horror_movies)
        words_part = random.choice(words)
        movie_title = f'{horror_part} {words_part}'
        return movie_title

    @staticmethod
    def generate_random_url():
        domain = faker.url()
        return f'{domain}.domain'

    @staticmethod
    def generate_random_price():
        price = random.randint(1,100)
        return price

    @staticmethod
    def generate_random_description():
        genres = ["ужас", "комедия", "приключение", "фэнтези", "драма"]
        heroes = ["герой", "отважная девушка", "группа друзей", "одинокий путешественник"]
        locations = ["в тёмном замке", "в космосе", "в маленьком городе", "в параллельном мире"]
        events = ["спасает мир", "находит тайну", "борется с монстрами", "попадает в ловушку времени"]
        result = f'Фильм в {random.choice(genres)} где {random.choice(heroes)} {random.choice(locations)} {random.choice(events)}'
        return result

    @staticmethod
    def generate_random_location():
        base_location = ['SPB', 'MSK']
        return random.choice(base_location)

    @staticmethod
    def generate_published():
        published = [True, False]
        return random.choice(published)

    @staticmethod
    def generate_genre_id():
        genre_id = random.randint(1,10)
        return genre_id


    @staticmethod
    def generate_pages_size():
        pages_size = random.randint(1,20)
        return pages_size

    @staticmethod
    def generate_created_at():
        created_at = ['asc', 'desc']
        return random.choice(created_at)
