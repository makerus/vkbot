import re
import random
import time
import json

import requests
from bs4 import BeautifulSoup

import logger


class VkApi:
    def __init__(self, client_id, email, password, scope, timeout=8, version_vk="5.73"):
        """
            :param client_id: ID приложения в VK
            :param email: Номер телефона / Почта от профиля бота в VK
            :param password: Пароль от профиля бота в VK
            :param scope: права доступа для бота в VK
            :param version_vk: ПО УМОЛЧАНИЮ = 5.73, Версия api VK
            :param timeout: Максимальное время ответа в секундах, по умолчанию - 8 секунд.
        """

        logger.log("Инициализация бота")

        self.authorize_url = "https://oauth.vk.com/authorize"
        self.redirect_uri = "http://oauth.vk.com/blank.html"
        self.action = "https://login.vk.com/?act=login&soft=1&utf8=1"
        self.method_action = "https://api.vk.com/method/"
        self.client_id = client_id
        self.email = email
        self.password = password
        self.scope = scope
        self.version_vk = version_vk
        self.req_session = requests.Session()
        self.token = ""
        self.timeout = timeout
        self.list_messages = json.load(open('messages.json', encoding='utf-8'))
        self.data = {}  # Внутренний массив данных

        if not self.client_id or not self.email or not self.password:
            logger.error(self.list_messages['no_input'])
            exit()

        self.api()

    def api(self):
        """
            Метод для получаения токена и установки прав для профиля бота в вк
        """
        logger.log("Получение токена")
        req_authorize_vk = self.req_session.get(  # Получаем страничку для авторизации и получения прав
            self.authorize_url, params={
                "client_id": self.client_id,
                "redirect_uri": self.redirect_uri,
                "display": "mobile",
                "response_type": "token",
                "scope": self.scope,
                "v": self.version_vk,
                "revoke": 1
            }
        )

        get_form_vk = BeautifulSoup(req_authorize_vk.text, "html.parser")  # Разбираем страничку
        post_data = {}  # Формируем данные для отправки
        for el in get_form_vk.form.find_all('input'):  # Получаем все имена полей из формы, а так же их значения
            if "name" in el.attrs and el['name'] != "email" and el['name'] != "pass":
                post_data.update({el['name']: el['value']})

        post_data.update({"email": self.email, "pass": self.password})  # Обновляем данные для отправки
        response = self.req_session.post(self.action, data=post_data)  # Отправляем подготовленные данные

        # Получаем вопрос на разрешения доступа к нужным нам правам
        get_page_privileges = BeautifulSoup(response.text, "html.parser")
        # Подтверждаем разрешение доступа к нужным нам правам
        get_privileges = self.req_session.post(get_page_privileges.form['action'])

        if get_privileges.url.find("error") >= 0:  # Проверяем на наличие ошибок
            logger.error(self.list_messages['error_auth'])
            m_vk = self.req_session.get("https://m.vk.com")  # Заходим на главную страницу ВК
            m_vk_page = BeautifulSoup(m_vk.text, "html.parser")
            m_vk_links = m_vk_page.find_all('a')
            for link in m_vk_links:
                if str(link).find("https://login.vk.com") >= 0:  # Получаем ссылку на кнопку выхода
                    self.req_session.get(link['href'])  # Переходим по ссылке кнопки выхода

            self.req_session.cookies.clear_expired_cookies()  # Очищаем куки
            exit()

        re_url = re.compile("=[a-z0-9]+[^&]", re.UNICODE)  # Если ошибок нет, то разбираем ответный URL
        get_token = re_url.search(get_privileges.url)  # Находим в нем токен, для доступа к api
        if get_token is None:
            logger.error(self.list_messages['invalid_input'])
            exit()
        self.token = get_token.group()[1:]  # Возвращаем токен

    def method(self, method_name, params):
        """
            :param method_name: Наименование метода api VK
            :param params: Параметры метода api VK
        """

        url_action = []
        for k, v in params.items():  # Формируем из параметров GET запрос k(ключ)=v(значение)
            url_action.append(str(k) + "=" + str(v))

        url_action.append('access_token=' + self.token)  # Добавляем к запросу наш токен
        url_action.append('v=' + self.version_vk)  # Добавляем к запросу версию VK API
        query = "&".join(url_action)  # Формируем корректный URL из данных, что сформировали выше
        url_command_api = self.method_action + method_name + "?"
        response = self.req_session.get(url_command_api, params=query)  # Отправляем наш GET запрос

        # 2 Ответа: response, error
        if 'response' in response.json():
            if len(response.json()) > 1:
                return response.json()['response'][0]
            else:
                return response.json()['response']
        elif 'error' in response.json():
            return response.json()
        else:
            logger.error(self.list_messages['error_response'])
            logger.log(response.json())

    def send(self, message, chat_id=0, user_id=0, optional=None, timeout_activity=3):
        """
            :param message: Текст сообщения
            :param chat_id: ID беседы, указывается если ответить нужно в беседу
            :param user_id: ID пользователя, указывается если нужно отправить ответ пользователю
            :param optional: Словарь { 'key' : 'value' } с дополнительными параметрами из api vk
            :param timeout_activity: Время показа статуса "печатает"
        """

        params = {}
        if chat_id > 0:
            self.method("messages.setActivity", {
                'user_id': 1,
                'type': 'typing',
                'peer_id': 2000000000 + int(chat_id)
            })
            time.sleep(timeout_activity)
        else:
            self.method("messages.setActivity", {
                'user_id': 1,
                'type': 'typing',
                'peer_id': int(user_id)
            })
            time.sleep(timeout_activity)

        # Формируем сообщение
        if chat_id > 0:
            params.update({'chat_id': chat_id})

        if user_id > 0:
            params.update({'user_id': user_id})

        if optional is not None:
            params.update(optional)

        params.update({'message': message})
        params.update({'random_id': random.randrange(1111111, 9999999, 1)})  # Генерируем случайный ID для сообщения
        self.method('messages.send', params)  # Отправляем сообщение

    def get_last_messages(self, count):
        """
            Метод получает <count>(число) последних сообщений в беседе
            :param count: Количество сообщений
        """
        return self.method("messages.get", {'count': count})

    def get_user(self, user_ids, fields=None):
        """
            Метод получает информацию о пользователе в VK
            :param fields: Поля которые необходимо получить
            :param user_ids: Идентификаторы пользователей через ","
        """
        if fields is not None:
            response = self.method("users.get", {'user_ids': user_ids, 'fields': fields})
            return response[0]
        else:
            response = self.method("users.get", {'user_ids': user_ids})
            return response[0]

    def reading_messages(self, msg):
        """
            Метод для пометки сообщений, как прочитанные
            :param msg: Список полученных сообщений
        """
        self.method("messages.markAsRead", {
            'peer_id': 2000000000 + int(msg['chat_id']),
            'start_message_id': int(msg['id'])
        })

    def check_read_message(self, msg):
        """
        Проверка статуса сообщения (прочитано / не прочитано)
        :param msg: Сообщение
        :return: Boolean (True/False) True - прочитано, False - не прочитано
        """

        if int(msg['read_state']) == 1:
            return True
        else:
            return False

    def check_command_message(self, msg, list_commands):
        """
        Проверка наличия команды в сообщении
        :param msg: Сообщение
        :param list_commands: Список команд
        :return: String - результат выполнения команды, Boolean(False) - не найдена команда
        """

        for cmd in list_commands:  # Проходимся по списку команд
            if str(msg).find(cmd['name']) > 0:  # Если в сообщении есть команда
                params = str(msg['body']).split(' ')  # Разбиваем команду по пробелам
                if len(params) > 1:
                    params.remove(cmd['name'])  # Формируем параметры
                    msg_out = cmd['run'](msg, self, params)  # Выполняем команду с параметрами
                else:
                    msg_out = cmd['run'](msg, self)  # Выполняем команду без параметров

                return msg_out
        return False

    def start_middleware(self, message, list_middleware):
        """
        Поочередный запуск обработчиков
        :param message: Сообщение
        :param list_middleware: Список обработчиков
        """

        for middleware in list_middleware:
            middleware(messages=message, api=self)

    def listen(self, messages, list_commands, list_middlewares=None):
        """
            Метод для обработки сообщений
            :param messages: Список полученных сообщений
            :param list_commands: Список команд
            :param list_middlewares: Список обработчиков
        """
        try:
            for msg in messages['items']:
                if not self.check_read_message(msg):  # Не прочитано ли сообщение?
                    msg_out = self.check_command_message(msg, list_commands)  # Проверяем наличие команды
                    if msg_out:
                        self.send(str(msg_out), msg['chat_id'])  # Отправляем ответ в беседу
                    if list_middlewares:  # Если есть обработчики
                        self.start_middleware(msg, list_middlewares)  # Запускаем обработчик
                    self.reading_messages(msg)  # Помечаем сообщение как прочитанное
            time.sleep(self.timeout)  # Ждем таймаут
        except KeyboardInterrupt:
            logger.log(self.list_messages['exit'])
            exit()
