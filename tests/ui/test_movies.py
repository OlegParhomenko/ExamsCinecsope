from pages.movies_page import MoviesPage
import allure

@allure.epic("UI Tests")
@allure.feature("Фильтрация фильмов")
class TestMoviesUI:

    @allure.story("Проверка работы фильтров и открытия фильма")
    @allure.title("Проверка фильтров по жанру, времени, локации и открытие фильма")
    def test_filters(self, page):
        movies_page = MoviesPage(page)

        with allure.step("Открываем страницу фильмов"):
            movies_page.open()

        with allure.step("Применяем фильтр по жанру"):
            movies_page.filter_by_genre()

        with allure.step("Применяем фильтр по времени"):
            movies_page.filter_by_time()

        with allure.step("Применяем фильтр по локации"):
            movies_page.filter_by_location()

        with allure.step("Проверяем, что фильмы найдены"):
            movies_page.assert_movies_found()

        with allure.step("Открываем страницу подробностей первого фильма"):
            movies_page.open_about_movie()

