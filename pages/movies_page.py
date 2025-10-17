from playwright.sync_api import Page, expect
import re
import allure
class MoviesPage:

    def __init__(self, page: Page):

        self.page = page
        self.profile_button = page.get_by_role('button', name='Профиль')
        self.about_button = page.locator(
            '.text-md', has_text='Убийца 2'
        ).get_by_role('button', name='Подробнее')
        self.location_filter = page.locator('button[role="combobox"] span', has_text="Место")
        self.genre_filter = page.locator('button[role="combobox"] span', has_text="Жанр")
        self.time_filter = page.locator("button[role='combobox'] span", has_text='Создано')
        self.not_found_text = page.locator('text=Ничего не найдено')

    @allure.step("Открываем страницу фильмов")
    def open(self):
        self.page.goto('https://dev-cinescope.coconutqa.ru/movies')

    @allure.step("Фильтруем по локации")
    def filter_by_location(self):
        expect(self.location_filter).to_be_visible(timeout=10000)
        self.location_filter.click()

        dropdown = self.page.locator('[role="listbox"][data-state="open"]')
        expect(dropdown).to_be_visible(timeout=10000)

        option = dropdown.locator('span', has_text=re.compile('msk', re.IGNORECASE))
        expect(option).to_be_visible()
        option.click()

    @allure.step("Фильтруем по жанру")
    def filter_by_genre(self):

        self.page.wait_for_load_state("networkidle")

        expect(self.genre_filter).to_be_visible(timeout=10000)
        self.genre_filter.click()

        dropdown = self.page.locator('[role="listbox"][data-state="open"]')
        expect(dropdown).to_be_visible(timeout=10000)

        options = dropdown.locator('span', has_text=re.compile("комедия", re.IGNORECASE))

        expect(options.first).to_be_visible(timeout=5000)
        options.first.click()

    @allure.step("Фильтруем по дате создания")
    def filter_by_time(self):
        expect(self.time_filter).to_be_visible(timeout=10000)
        self.time_filter.click()

        dropdown = self.page.locator('[role="listbox"][data-state="open"]')
        expect(dropdown).to_be_visible(timeout=10000)

        option = dropdown.locator('span', has_text=re.compile('новые', re.IGNORECASE))
        expect(option).to_be_visible()
        option.click()

    @allure.step("Проверяем, что фильмы найдены")
    def assert_movies_found(self):
        expect(self.not_found_text).not_to_be_visible()

    @allure.step("Открываем страницу подробностей первого фильма")
    def open_about_movie(self):
        first_movie = self.page.locator('.rounded-xl.border.bg-card.text-card-foreground.shadow').first

        about_movie = first_movie.get_by_role("button", name="Подробнее")
        about_movie.click()
        rating = self.page.get_by_text('Рейтинг')
        expect(rating).to_be_visible()


