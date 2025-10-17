from pages.login_page import LoginPage
import allure


@allure.epic("UI Тесты")
@allure.feature("Логин в систему")
class TestLoginTestUI:

    @allure.story("Успешный логин")
    @allure.title("Проверка успешного логина и перезагрузки страницы")
    def test_login(self, page, super_admin):
        login_email = super_admin.email
        login_password = super_admin.password

        login_page = LoginPage(page)
        with allure.step("Открываем страницу логина"):
            login_page.open()

        with allure.step("Выполняем логин"):
            login_page.login(login_email, login_password)

        with allure.step("Проверяем отсутствие ошибки после логина"):
            login_page.assert_not_login_error()

        with allure.step("Перезагружаем страницу и проверяем видимость кнопки 'Профиль'"):
            login_page.reload()
            login_page.after_reload_check()






