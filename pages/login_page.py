from playwright.sync_api import Page, expect
import allure

class LoginPage:
    def __init__(self, page: Page):

        self.page = page
        self.email_input = page.locator('input[type="email"]')
        self.password_input = page.locator('input[type="password"]')
        self.login_button = page.locator('button[type="submit"]')
        self.error_message = page.locator('div.go3958317564')

    @allure.step("Открываем страницу логина")
    def open(self):
        self.page.goto('https://dev-cinescope.coconutqa.ru/login')

    @allure.step("Перезагружаем страницу")
    def reload(self):
        self.page.reload()

    @allure.step("Вводим логин (email) и пароль")
    def login(self, email: str, password: str):
        self.email_input.fill(email)
        self.password_input.fill(password)
        self.login_button.click()

    @allure.step("Проверяем отсутствие ошибки логина")
    def assert_not_login_error(self):
        expect(self.error_message).not_to_contain_text('Что-то пошло не так')
        # expect(self.error_message).not_to_contain_text('Неверная почта или пароль')

    @allure.step("Проверяем после перезагрузки, что кнопка 'Профиль' видна")
    def after_reload_check(self):
        self.page.reload()
        self.page.get_by_role('button', name='Профиль')
        expect(self.page.get_by_role('button', name='Профиль')).to_be_visible()

