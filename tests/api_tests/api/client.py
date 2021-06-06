import logging
import json
from urllib.parse import urljoin

import allure
import requests

from builder import Builder

logger = logging.getLogger('test')
builder = Builder()

MAX_RESPONSE_LENGTH = 500


class ResponseStatusCodeException(Exception):
    pass


class ApiClient:

    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()

        self.csrf_token = None
        self.sessionid_gtp = None

    @staticmethod
    def log_pre(method, url, headers, data, params, expected_status):
        logger.info(f'Performing {method} request:\n'
                    f'URL: {url}\n'
                    f'HEADERS: {headers}\n'
                    f'DATA: {data}\n\n'
                    f'PARAMS: {params}\n\n'
                    f'expected status: {expected_status}\n\n')

    @staticmethod
    def log_post(response):
        log_str = 'Got response:\n' \
                  f'RESPONSE STATUS: {response.status_code}'

        if len(response.text) > MAX_RESPONSE_LENGTH:
            if logger.level == logging.INFO:
                logger.info(f'{log_str}\n'
                            f'RESPONSE CONTENT: COLLAPSED due to response size > {MAX_RESPONSE_LENGTH}. '
                            f'Use DEBUG logging.\n\n')
            elif logger.level == logging.DEBUG:
                logger.debug(f'{log_str}\n'
                             f'RESPONSE CONTENT: {response.text}\n\n')
        else:
            logger.info(f'{log_str}\n'
                        f'RESPONSE CONTENT: {response.text}\n\n')

    def _request(self, method, url, headers=None, data=None, params=None, expected_status=200, jsonify=True):
        self.log_pre(method, url, headers, data, params, expected_status)
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
            }
        response = self.session.request(method, url, headers=headers, data=data, params=params)
        self.log_post(response)

        if response.status_code != expected_status:
            raise ResponseStatusCodeException(f'Got {response.status_code} {response.reason} for URL "{url}"!\n'
                                              f'Expected status_code: {expected_status}.')
        if jsonify:
            binary_content = response.content
            parsed_response = json.loads(binary_content.decode())
            return parsed_response
        return response

    # @allure.step('Получение csrf-токена')
    # def get_token(self):
    #     location = urljoin(self.base_url, '/csrf/')
    #
    #     res = self._request('GET', location, jsonify=False)
    #
    #     headers = res.headers['set-cookie'].split(';')
    #
    #     token_header = [h for h in headers if 'csrftoken' in h]
    #     if not token_header:
    #         raise Exception('CSRF token not found in main page headers')
    #
    #     token_header = token_header[0]
    #     token = token_header.split('=')[-1]
    #
    #     return token

    @allure.step('Авторизация')
    def post_login(self, username, password, expected_status=200):
        location = urljoin(self.base_url, '/login')

        headers = {
            'Referer': location,
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept-Encoding': 'gzip, deflate, br',
        }

        data = {'username': username,
                'password': password,
                'submit': 'Login'}

        result = self._request('POST', location, headers=headers, data=data, jsonify=False, expected_status=expected_status)

        return result

    @allure.step('Регистрация')
    def post_register(self, username=None, email=None, password=None, confirm_password=None, expected_status=200, term='y'):
        user = builder.create_user(username, email, password)

        location = urljoin(self.base_url, '/reg')

        headers = {
            'Referer': location,
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept-Encoding': 'gzip, deflate, br',
        }

        if confirm_password is None:
            confirm_password = user.password

        data = {
            'username': user.username,
            'email': user.email,
            'password': user.password,
            'confirm': confirm_password,
            'term': term,
            'submit': 'Register'
        }

        result = self._request('POST', location, headers=headers, data=data, jsonify=False, expected_status=expected_status)

        return user, result

    def get_logout(self):
        location = urljoin(self.base_url, '/logout')

        headers = {
            'Referer': self.base_url + '/welcome/',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept-Encoding': 'gzip, deflate, br',
        }

        result = self._request('GET', location, headers=headers, jsonify=False)

        return result

