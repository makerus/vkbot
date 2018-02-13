import requests
from bs4 import BeautifulSoup
import re
import random
import time
import logger


class VkApi:
    """
    :param client_id: ID приложения в VK
    :param email: Номер телефона / Почта от профиля бота в VK
    :param password: Пароль от профиля бота в VK
    :param scope: права доступа для бота в VK
    :param version_vk: ПО УМОЛЧАНИЮ = 5.69, Версия api VK
    :param timeout: Максимальное время ответа в секундах, по умолчанию - 8 секунд.
    """
    def __init__(self, client_id, email, password, scope, timeout=8, version_vk="5.69"):

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

        self.api()

    """
    Метод для получаения токена и установки прав для профиля бота в вк
    """
    def api(self):

        logger.log("Получение токена")

        #Получаем страничку для авторизации и получения прав
        req_authorize_vk = self.req_session.get(
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

        #Разбираем страничку
        get_form_vk = BeautifulSoup(req_authorize_vk.text, "html.parser")
        #Формируем данные для отправки
        post_data = {}
        #Получаем все имена полей из формы, а так же их значения
        for el in get_form_vk.form.find_all('input'):
            if "name" in el.attrs and el['name'] != "email" and el['name'] != "pass":
                post_data.update({el['name']:el['value']})

        #Обновляем данные для отправки
        post_data.update({"email": self.email, "pass": self.password})
        #Отправляем подготовленные данные
        response = self.req_session.post(self.action, data=post_data)

        #Получаем вопрос на разрешения доступа к нужным нам правам
        get_page_privileges = BeautifulSoup(response.text, "html.parser")
        #Подтверждаем разрешение доступа к нужным нам правам
        get_privileges = self.req_session.post(get_page_privileges.form['action'])

        #Проверяем на наличие ошибок в ответе, поиском по URL
        #Если ошибка найдена то
        if get_privileges.url.find("error") >= 0:
            #Выводим ошибку
            logger.error("Ошибка авторизации")
            #Заходим на профиль в вк, на главную страницу
            m_vk = self.req_session.get("https://m.vk.com")
            #Ищем кнопку выйти
            m_vk_page = BeautifulSoup(m_vk.text, "html.parser")
            m_vk_links = m_vk_page.find_all('a')
            for link in m_vk_links:
                if str(link).find("https://login.vk.com") >= 0:
                    #Выходим из профиля
                    self.req_session.get(link['href'])

            #Чистим куки
            self.req_session.cookies.clear_expired_cookies()
            #Завершаем работу
            exit()

        #Если ошибок нет, то разбираем ответный URL
        re_url = re.compile("=[a-z0-9]+[^&]", re.UNICODE)
        #Находим в нем токен, для доступа к api
        get_token = re_url.search(get_privileges.url)
        #Возвращаем токен
        self.token = get_token.group()[1:]

    """
    :param method_name: Наименование метода api VK
    :param params: Параметры метода api VK
    """
    def method(self, method_name, params):
        #Подготавливаем наш URL для запроса к API VK
        url_action = []
        #Формируем из параметров GET запрос k(ключ)=v(значение)
        for k, v in params.items():
            url_action.append(str(k)+"="+str(v))

        #Добавляем к запросу наш токен
        url_action.append('access_token='+self.token)
        #Добавляем к запросу версию VK API
        url_action.append('v='+self.version_vk)

        #Формируем корректный URL из данных, что сформировали выше
        query = "&".join(url_action)
        url_command_api = self.method_action + method_name + "?"

        #Отправляем наш GET запрос
        response = self.req_session.get(url_command_api, params=query)

        #Проверяем какое количество элементов пришло в ответе
        #Если вернулось число, то возвращаем его
        if isinstance(response.json()['response'], int):
            return response.json()['response']
        #Если 1 элемент, то возвращаем первый элемент
        elif type(response.json()) != 'int' and len(response.json()['response']) == 1:
            return response.json()['response'][0]
        #Если несколько элементов, то возвращаем их в формате JSON
        elif 'response' not in response.json():
            return response.json()
        #Если вернулось, что-то другое (число), возвращаем ответ
        else:
            return response.json()['response']

    """
    :param params: Параметры для метода Messages.send в API VK
    :param chat_id: ID беседы, указывается если ответить нужно в беседу
    :param user_id: ID пользователя, указывается если нужно отправить ответ пользователю
    :param optional: Словарь { 'key' : 'value' } с дополнительными параметрами из api vk
    :param timeout_activity: Время показа статуса "печатает"
    """
    def send(self, message, chat_id=0, user_id=0, optional='', timeout_activity=3):

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

        #Формируем сообщение
        if chat_id > 0:
            params.update({'chat_id': chat_id})

        if user_id > 0:
            params.update({'user_id': user_id})

        if optional != '':
            params.update(optional)

        params.update({'message': message})

        #Генерируем случайный ID для сообщения
        params.update({'random_id': random.randrange(1111111, 9999999, 1)})
        #Отправляем сообщение
        self.method('messages.send', params)

    """
    :param method_name: Метод получает <count>(число) последних сообщений в беседе
    :param count: Количество сообщений
    """
    def get_last_messages(self, count):
        return self.method("messages.get", {'count': count})

    """
    :param method_name: Метод получает информацию о пользователе в VK
    :param fields: Поля которые необходимо получить
    :param user_ids: Идентификаторы пользователей через ","
    """
    def get_user(self, user_ids, fields=""):
        if len(fields) > 0:
            return self.method("users.get", {'user_ids': user_ids, fields: fields})
        else:
            return self.method("users.get", {'user_ids': user_ids})

    """
    :param method_name: Метод для пометки сообщений, как прочитанные
    :param msg: Список полученных сообщений
    """
    def reading_messages(self, msg):
        self.method("messages.markAsRead", {
            'peer_id': 2000000000 + int(msg['chat_id']),
            'start_message_id': int(msg['id'])
        })

    """
    :param method_name: Метод для обработки сообщений
    :param messages: Список полученных сообщений
    :param list_commands: Список команд
    """
    def listen(self, messages, list_commands):
        try:
            for msg in messages['items']:
                #Если сообщение не прочитано
                if int(msg['read_state']) == 0:
                    #Проходимся по списку команд
                    for cmd in list_commands:
                        #Если в сообщении есть команда
                        if str(msg).find(cmd['name']) > 0:
                            #Разбиваем команду по пробелам
                            params = str(msg['body']).split(' ')
                            if len(params) > 1:

                                #Формируем параметры
                                params.remove(cmd['name'])

                                # Выполняем команду с дополнительными параметрами
                                # Params - массив [arg1, arg2, arg3]
                                msg_out = cmd['run'](msg, self, params)
                            else:
                                #Выполняем команду без параметров
                                msg_out = cmd['run'](msg, self)

                            #Отправляем ответ в беседу
                            self.send(str(msg_out), msg['chat_id'])
                            #Помечаем сообщение как прочитанное
                            self.reading_messages(msg)
            # Ждем таймаут
            time.sleep(self.timeout)
        except KeyboardInterrupt:
            logger.log("Завершение работы")
            exit()
