import random
import string

import allure
import pytest

from api_tests.test_api.base import ApiBase

EXISTING_USERNAME = object()
EXISTING_PASSWORD = object()
EXISTING_EMAIL = object()


class TestAuth(ApiBase):
    authorize = False

    @pytest.mark.API('API')
    @allure.title('Успешная авторизация')
    def test_api_successful_login(self):
        res = self.api_client.post_login(self.base_user.username, self.base_user.password)
        assert res.request.url == 'http://127.0.0.1:8095/welcome/'
        assert res.status_code == 200
        assert 'Logged as' in res.text

    @pytest.mark.parametrize(
        'login, password, expected_result',
        [
            ('', '', (200, 'Welcome to the TEST SERVER')),
            (EXISTING_USERNAME, '', (200, 'Welcome to the TEST SERVER')),
            ('', EXISTING_PASSWORD, (200, 'Welcome to the TEST SERVER')),
            ('wrong_login', 'wrong_password', (401, 'Invalid username or password')),
            (''.join(random.choice(string.ascii_letters) for i in range(2)), 'qazswxde', (401, 'Incorrect username length')),
            (''.join(random.choice(string.ascii_letters) for i in range(19)), 'qazswxde', (401, 'Incorrect username length')),
            (EXISTING_USERNAME, 'incorrect_pass', (401, 'Invalid username or password')),
            ('incorrect_name', EXISTING_PASSWORD, (401, 'Invalid username or password')),
        ]
    )
    @pytest.mark.API
    @allure.title('Неуспешная авторизация')
    @allure.description('Негативный тест на авторизацию')
    def test_api_unsuccessful_login(self, login, password, expected_result):
        if login == EXISTING_USERNAME:
            login = self.base_user.username
        if password == EXISTING_PASSWORD:
            password = self.base_user.password
        res = self.api_client.post_login(login, password)
        assert res.status_code == expected_result[0]
        assert expected_result[1] in res.text
        assert 'Test Server | Welcome!' not in res.text

    @pytest.mark.API
    @allure.title('Тест на логаут')
    @allure.description('Тест на выход из сессии пользователя')
    def test_api_logout(self):
        self.api_client.post_login(self.base_user.username, self.base_user.password)
        res = self.api_client.get_logout()
        assert res.status_code == 200
        assert 'Welcome to the TEST SERVER' in res.text


class TestRegistration(ApiBase):
    authorize = False

    @pytest.mark.API
    @allure.title('Успешная регистрация пользователя')
    @allure.description('Тест успешной регистрации пользователя')
    def test_api_successful_registration(self):
        user, res = self.api_client.post_register()
        assert res.request.url == 'http://127.0.0.1:8095/welcome/'
        assert res.status_code == 200
        assert 'Logged as' in res.text

    @pytest.mark.parametrize(
        'login, email, password, confirm_pass, expected_result',
        [
            ('TooLooongUsername', None, 'qwerty', 'qwerty', 'Incorrect username length'),
            ('S', None, 'qazswxde', 'qazswxde', 'Incorrect username length'),
            (None, '', 'qazswxde', 'qazswxde', 'Incorrect email length'),  # TODO should it say to fill in email field?
            (None, 'tqwertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiopest@email.com', 'qazswxde', 'qazswxde',
             'Incorrect email length'),
            (None, 'a@b.c', 'qazswxde', 'qazswxde', 'Incorrect email length'),
            (None, 'test.ru', 'qazswxde', 'qazswxde', 'Invalid email address'),
            (None, 'test@ru', 'qazswxde', 'qazswxde', 'Invalid email address'),
            (None, 'testwertyuiru', 'qazswxde', 'qazswxde', 'Invalid email address'),
            (None, None, 'qazswxde', '', 'Passwords must match'),
            (None, None, 'qazswxde', 'qazswxd', 'Passwords must match'),
            (None, None, 'qwertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiopqwe'
                         'rtyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiopqw'
                         'ertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiopqwerty',
             None, 'Incorrect password length'),
            (None, None, '', 'qazswxde', 'Registration'),
            ('', None, 'qazswxde', 'qazswxde', 'Registration')
        ]
    )
    @pytest.mark.API
    @allure.title('Регистрация пользователя с невалидными данными')
    @allure.description('Тест регистрации пользователя с невалидными данными')
    def test_api_registration_invalid_data(self, login, email, password, confirm_pass, expected_result):
        self.user, res = self.api_client.post_register(login, email, password, confirm_pass)
        assert res.status_code == 400
        assert expected_result in res.text
        assert 'Test Server | Welcome!' not in res.text

    @pytest.mark.parametrize(
        'term',
        ['', 'n', 123]
    )
    @pytest.mark.API
    @allure.title('Регистрация пользователя без принятия согласия')
    @allure.description('Тест регистрации пользователя невалидное значение принятия согласия')
    def test_api_registration_without_acceptance(self, term):
        self.user, res = self.api_client.post_register(term=term)
        assert 'Registration' in res.text
        assert 'Test Server | Welcome!' not in res.text
        assert res.status_code == 400

    @pytest.mark.parametrize(
        'login, email, password, expected_result',
        [
            (None, EXISTING_EMAIL, None, (409, 'User already exists')),
            (EXISTING_USERNAME, None, None, (409, 'User already exists')),
            (None, None, EXISTING_PASSWORD, (200, 'Logged as')),
        ]
    )
    @pytest.mark.API
    @allure.title('Регистрация существующего пользователя')
    @allure.description('Тест на попытку зарегистрировать пользователя с данными уже существующего пользователя')
    def test_api_create_existing_user(self, login, email, password, expected_result):
        if login == EXISTING_USERNAME:
            login = self.base_user.username
        if password == EXISTING_PASSWORD:
            password = self.base_user.password
        if email == EXISTING_EMAIL:
            email = self.base_user.email
        self.user, res = self.api_client.post_register(login, email, password)
        assert res.status_code == expected_result[0]
        assert expected_result[1] in res.text


class TestUsers(ApiBase):
    authorize = True

    @pytest.mark.API
    @allure.title('запросы неавторизованным пользователем')
    @allure.description('Тест на попытку выполнить API запросы неавторизованным пользователем')
    def test_api_requests_unauthorized(self):
        self.api_client.get_logout()
        user, res = self.api_client.post_add_user()
        assert res.status_code == 401
        res_del = self.api_client.get_delete(self.base_user.username)
        assert res_del.status_code == 401
        res_block = self.api_client.get_block_user(self.base_user.username)
        assert res_block.status_code == 401
        res_unblock = self.api_client.get_block_user(self.base_user.username)
        assert res_unblock.status_code == 401

    @pytest.mark.API
    @allure.title('Добавление пользователя')
    @allure.description('Тест на добавление пользователя')
    def test_api_add_user(self):
        self.api_client.post_add_user()

    @pytest.mark.parametrize(
        'login, email, password',
        [
            (''.join(random.choice(string.ascii_letters) for i in range(3)), None, 'qazswxde'), # get 210 - and user created
            ('TooLooongUsername', None, 'qazswxde'), # get 210 - and user not created
            (None, '', None), # creates user without email
            ('', '', ''), # returns 210 - doesnt create user
            (None, 'tqwertyuiopqwertyuiopqwertyuiopqweetftuuhojikrxycfugyhtyuiopqwertyuiopest@emafhil.com', None), # returns 210 - doesnt create user
            (None, ''.join(random.choice(string.ascii_letters) for i in range(3)), None), # get 210 - and user created
            (None, ''.join(random.choice(string.ascii_letters) for i in range(10)), None), # get 210 - and user created
            (None, None, ''),
            ('', None, None),
            (None, None, 'qwertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiopqwe'
                         'rtyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiopqw'
                         'ertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiopqwerty'),
        ]
    )
    @pytest.mark.API
    @allure.title('Негативный тест на добавление пользователя')
    @allure.description('Негативный тест на добавление пользователя')
    def test_api_negative_add_user(self, login, email, password):
        user, res = self.api_client.post_add_user(login, email, password)
        assert res.status_code == 400

    @pytest.mark.API
    @pytest.mark.parametrize(
        'login, email, password, expected_result',
        [
            (None, EXISTING_EMAIL, None, 304),
            (EXISTING_USERNAME, None, None, 304),
            (None, None, EXISTING_PASSWORD, 201),
        ]
    )
    @pytest.mark.API
    @allure.title('Попытка добавления существующего пользователя')
    @allure.description('Тест на повторное добавление существующего пользователя')
    def test_api_add_existing_user(self, login, email, password, expected_result):
        if login == EXISTING_USERNAME:
            login = self.base_user.username
        if password == EXISTING_PASSWORD:
            password = self.base_user.password
        if email == EXISTING_EMAIL:
            email = self.base_user.email
        user, res = self.api_client.post_add_user(login, email, password)
        assert res.status_code == expected_result
        # assert user.username in db or user.password

    @pytest.mark.parametrize(
        'login, expected_result',
        [
            (EXISTING_USERNAME, (204, '')),
            ('Not_existing', (404, 'User does not exist!')),
        ]
    )
    @pytest.mark.API
    @allure.title('Удаление пользователя')
    @allure.description('Тест на удаление пользователя')
    def test_api_delete_user(self, login, expected_result):
        user, res = self.api_client.post_add_user()
        if login == EXISTING_USERNAME:
            login = user.username
        res_del = self.api_client.get_delete(login)
        assert res_del.status_code == expected_result[0]
        assert res_del.text == expected_result[1]
        # assert user.username not in db

    @pytest.mark.parametrize(
        'login, expected_result',
        [
            (EXISTING_USERNAME, (200, 'User was blocked!')),
            ('', (404, 'User does not exist!')), # непонятное отображение ошибки
            ('Not_existing', (404, 'User does not exist!')),
        ]
    )
    @pytest.mark.API
    @allure.title('Блокировка пользователя')
    @allure.description('Тест блокировки пользователя')
    def test_api_block_user(self, login, expected_result):
        user, res = self.api_client.post_add_user()
        if login == EXISTING_USERNAME:
            login = user.username
        res = self.api_client.get_block_user(login)
        assert res.status_code == expected_result[0]
        assert res.text == expected_result[1]
        #  access = 0 в БД

    @pytest.mark.API
    @allure.title('Блокировка заблокированного пользователя')
    @allure.description('Тест блокировки уже заблокированного пользователя')
    def test_api_block_blocked_user(self):
        user, res = self.api_client.post_add_user()
        self.api_client.get_block_user(user.username)
        res = self.api_client.get_block_user(user.username)
        assert res.status_code == 304

    @pytest.mark.parametrize(
        'login, expected_result',
        [
            (EXISTING_USERNAME, (200, 'User access granted!')),
            ('', (404, 'User does not exist!')),
            ('Not_existing', (404, 'User does not exist!')),
        ]
    )
    @pytest.mark.API
    @allure.title('Разблокировка пользователя')
    @allure.description('Тест на разблокировку пользователя')
    def test_api_unblock_user(self, login, expected_result):
        user, res = self.api_client.post_add_user()
        if login == EXISTING_USERNAME:
            login = user.username
            self.api_client.get_block_user(login)
        res = self.api_client.get_unblock_user(login)
        assert res.status_code == expected_result[0]
        assert res.text == expected_result[1]
        #  access = 0 в БД

    @pytest.mark.API
    @allure.title('Разблокировка незаблокированного пользователя')
    @allure.description('Тест на разблокировку пользователя, который не заблокирован')
    def test_api_unblock_not_blocked_user(self):
        user, res = self.api_client.post_add_user()
        res = self.api_client.get_unblock_user(user.username)
        assert res.status_code == 304


