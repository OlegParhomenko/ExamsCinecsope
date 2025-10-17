from playwright.sync_api import Page, expect
import allure

class RegisterPage:
    def __init__(self, page: Page):

        self.page = page
        self.fullname_input = page.locator('input[name="fullName"]')
        self.email_input = page.locator('input[name="email"]')
        self.password_input = page.locator('input[name="password"]')
        self.repeat_password_input = page.locator('input[name="passwordRepeat"]')
        self.register_button = page.locator('button[type="submit"]')
        self.error_message = page.locator('div.go3958317564')

    @allure.step("Открываем страницу регистрации")
    def open(self):
        self.page.goto('https://dev-cinescope.coconutqa.ru/register')

    @allure.step("Вводим ФИО, email, пароль и повторяем пароль")
    def register(self, fullname, email, password, repeat_password):
        self.fullname_input.fill(fullname)
        self.email_input.fill(email)
        self.email_input.fill(email)
        self.password_input.fill(password)
        self.repeat_password_input.fill(repeat_password)
        self.register_button.click()

    @allure.step("Проверяем отсутствие ошибки регистрации")
    def assert_register_error(self):
        expect(self.error_message).not_to_contain_text('Что-то пошло не так')

