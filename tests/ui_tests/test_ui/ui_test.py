import allure
import pytest

from ui_tests.test_ui.base import BaseCase
from ui_tests.ui.locators.pages_locators import MainPageLocators

main_page_locators = MainPageLocators()


EXISTING_USERNAME = object()
EXISTING_PASSWORD = object()
EXISTING_EMAIL = object()


class TestLogin(BaseCase):
    authorize = False

    @pytest.mark.UI
    @allure.title('Успешная авторизация')
    @allure.description('Тест успешной авторизации')
    def test_ui_successful_login(self):
        self.login_page.successful_login(self.base_user.username, self.base_user.password)

    @pytest.mark.parametrize(
        'login, password, expected_result',
        [
            ('', '', 'Welcome to the TEST SERVER'),
            ('', 'qazswxde', 'Welcome to the TEST SERVER'),
            ('Marrisa', '', 'Welcome to the TEST SERVER'),
            ('wrong_login', 'wrong_password', 'Invalid username or password'),
            ('Stepy', 'qazswxde', 'Incorrect username length'),
            ('Sqazwsxedcrfvtgby', 'qazswxde', 'Incorrect username length'),
            (EXISTING_USERNAME, 'incorrect_pass', 'Invalid username or password'),
            ('incorrect_name', EXISTING_PASSWORD, 'Invalid username or password'),
        ]
    )
    @pytest.mark.UI
    @allure.title('Неуспешная авторизация')
    @allure.description('Негативный тест на авторизацию')
    def test_ui_unsuccessful_login(self, login, password, expected_result):
        if login == EXISTING_USERNAME:
            login = self.base_user.username
        if password == EXISTING_PASSWORD:
            password = self.base_user.password
        self.login_page.unsuccessful_login(login, password, expected_result)

    @pytest.mark.UI
    @allure.title('Тест на логаут')
    @allure.description('Тест на выход из сессии пользователя')
    def test_ui_logout(self):
        self.login_page.open_registration_page()
        self.registration_page.register_user()
        self.main_page.logout()
        assert 'Welcome to the TEST SERVER' in self.driver.page_source


class TestRegistration(BaseCase):
    authorize = False

    @pytest.mark.UI
    @allure.title('Успешная регистрация пользователя')
    @allure.description('Тест успешной регистрации пользователя')
    def test_ui_successful_registration(self):
        self.login_page.open_registration_page()
        user = self.registration_page.register_user()
        assert 'Logged as ' + user.username in self.driver.page_source

    @pytest.mark.parametrize(
        'login, email, password, confirm_pass, expected_result',
        [
            ('TooLooongUsername', None, 'qwerty', 'qwerty', 'Incorrect username length'),
            ('S', None, 'qazswxde', 'qazswxde', 'Incorrect username length'),
            (None, '', 'qazswxde', 'qazswxde', 'Incorrect email length'),
            (None, 'tqwertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiopest@email.com', 'qazswxde', 'qazswxde',
             'Incorrect email length'),
            (None, 'a@b.c', 'qazswxde', 'qazswxde', 'Incorrect email length'),
            (None, 'test.ru', 'qazswxde', 'qazswxde', 'Invalid email address'),
            (None, 'test@ru', 'qazswxde', 'qazswxde', 'Invalid email address'),
            (None, 'testwertyuiru', 'qazswxde', 'qazswxde', 'Invalid email address'),
            (None, None, 'qazswxde', '', 'Passwords must match'),
            (None, None, 'qazswxde', 'qazswxd', 'Passwords must match'),
            (None, None, '', 'qazswxde', 'Registration'),
            ('', None, 'qazswxde', 'qazswxde', 'Registration'),
            (None, None, 'qwertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiopqwe'
                         'rtyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiopqw'
                         'ertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiopqwerty',
             None, 'Incorrect password length')
        ]
    )
    @pytest.mark.UI
    @allure.title('Регистрация пользователя с невалидными данными')
    @allure.description('Тест регистрации пользователя с невалидными данными')
    def test_ui_registration_invalid_data(self, login, email, password, confirm_pass, expected_result):
        self.login_page.open_registration_page()
        self.registration_page.register_user(login, email, password, confirm_pass)
        assert 'Logged as ' + self.base_user.username not in self.driver.page_source
        assert expected_result in self.driver.page_source

    @pytest.mark.UI
    @allure.title('Регистрация пользователя без принятия согласия')
    @allure.description('Тест регистрации пользователя без принятия согласия')
    def test_ui_registration_without_acceptance(self):
        self.login_page.open_registration_page()
        self.registration_page.register_user_no_accept()
        assert 'Registration' in self.driver.page_source

    @pytest.mark.parametrize(
        'login, email, password, expected_result',
        [
            (None, EXISTING_EMAIL, 'qazswxde', 'User already exists'),
            (EXISTING_USERNAME, 'normal@email.com', 'qazswxde', 'User already exists'),
            (None, None, EXISTING_PASSWORD, 'Logged as'),
        ]
    )
    @pytest.mark.UI
    @allure.title('Регистрация существующего пользователя')
    @allure.description('Тест на попытку зарегистрировать пользователя с данными уже существующего пользователя')
    def test_ui_register_existing_user(self, login, email, password, expected_result):
        if login == EXISTING_USERNAME:
            login = self.base_user.username
        if email == EXISTING_EMAIL:
            email = self.base_user.email
        if password == EXISTING_PASSWORD:
            password = self.base_user.password
        self.login_page.open_registration_page()
        self.registration_page.register_user(login, email, password)
        assert expected_result in self.driver.page_source


class TestMainPage(BaseCase):
    authorize = True

    @pytest.mark.UI
    @allure.title('Проверка имени пользователя')
    @allure.description('Проверка отображения имени авторизованного пользователя')
    def test_ui_logged_user_text(self):
        assert 'Logged as ' + self.base_user.username in self.driver.page_source

    @pytest.mark.UI
    @allure.title('Проверка VK ID пользователя')
    @allure.description('Проверка отображения VK ID авторизованного пользователя')
    def test_ui_vk_id(self):
        assert 'VK ID: id' + self.base_user.username in self.driver.page_source

    @pytest.mark.parametrize(
        'locators, expected_result',
        [
            ((main_page_locators.PYTHON_DROPDOWN_LOCATOR, main_page_locators.PYTHON_HISTORY_BUTTON_LOCATOR),
             'History of Python'),
            ((main_page_locators.PYTHON_DROPDOWN_LOCATOR, main_page_locators.ABOUT_FLASK_BUTTON_LOCATOR), 'Flask'),
            ((main_page_locators.LINUX_DROPDOWN_LOCATOR, main_page_locators.DOWNLOAD_CENTOS_BUTTON_LOCATOR), 'Download Centos7'),
            ((main_page_locators.NETWORK_DROPDOWN_LOCATOR, main_page_locators.WIRESHARK_NEWS_BUTTON_LOCATOR),
             'Wireshark'),
            ((main_page_locators.NETWORK_DROPDOWN_LOCATOR, main_page_locators.DOWNLOAD_WIRESHARK_BUTTON_LOCATOR),
             'Download Wireshark'),
            ((main_page_locators.NETWORK_DROPDOWN_LOCATOR, main_page_locators.TCPDUMP_EXAMPLES_BUTTON_LOCATOR),
            'Tcpdump Examples'),
            ([main_page_locators.API_BUTTON_LOCATOR], 'API'),
            ([main_page_locators.FUTURE_OF_INTERNET_BUTTON_LOCATOR], 'What Will the Internet Be'),
            ([main_page_locators.SMTP_BUTTON_LOCATOR], 'SMTP'),
        ]
    )
    @pytest.mark.UI
    @allure.title('Проверка открытия всех ссылок')
    @allure.description('Проверка открытия всех ссылок в новых вкладок')
    def test_ui_open_links(self, locators, expected_result):
        self.main_page.open_redirect_page(locators, expected_result)

    @pytest.mark.parametrize(
        'locator, expected_results',
        [
            (main_page_locators.PYTHON_DROPDOWN_LOCATOR, ('Python history', 'About Flask')),
            (main_page_locators.LINUX_DROPDOWN_LOCATOR, ('Download Centos7')),
            (main_page_locators.NETWORK_DROPDOWN_LOCATOR, ('Wireshark', 'News', 'Download', 'Tcpdump', 'Examples'))
        ]
    )
    @pytest.mark.UI
    @allure.title('Нажать на все кнопки панели навигации')
    @allure.description('Проверка открытия всех выпадающих списков на панели навигации')
    def test_ui_check_dropdown(self, locator, expected_results):
        self.main_page.open_dropdow_menu(locator)
        for result in expected_results:
            assert result in self.driver.page_source

    @pytest.mark.UI
    @allure.title('Проверка дзена питона')
    @allure.description('Проверка отображения дзена питона')
    def test_ui_zen_of_python(self):
        assert self.main_page.check_zen_of_python_text()

    # Test press Home
