from pages.register_page import RegisterPage
from utils.data_generator import DataGenerator
import allure

@allure.epic("UI Тесты")
@allure.feature("Регистрация пользователя")
class TestRegisterUI:

    @allure.story("Успешная регистрация")
    @allure.title("Проверка успешной регистрации")
    def test_register(self, page):
        fullname = DataGenerator.generate_random_name()
        email = DataGenerator.generate_random_email()
        password = DataGenerator.generate_random_password()
        repeat_password = password

        register_page = RegisterPage(page)
        with allure.step("Открываем страницу логина"):
            register_page.open()
        with allure.step("Заполняем поля для регистрации"):
            register_page.register(fullname, email, password, repeat_password)
        with allure.step('Проверяем отсутствие ошибки после регистрации'):
            register_page.assert_register_error()





