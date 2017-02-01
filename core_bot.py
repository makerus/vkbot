import random, time, logger, vk

class Bot:

    #Конфигурация бота
    title_dialog = "" #Заголовок беседы
    author = "makerus"
    date_create = "2016 год"
    app_id = 'app_id' #ваш id приложения
    user_login = '' #ваш логин от аккаунта вконтакте
    user_password = '' #ваш пароль от аккаунта вконтакте
    scope = 'offline, messages, wall, friends, photos, status'

    log = logger.Log()

    def __init__(self):
        # Авторизация и запуск сессии в ВК
        self.log.info("Авторизация в ВК")
        session = vk.AuthSession(app_id=self.app_id, user_login=self.user_login,
                                 user_password=self.user_password, scope=self.scope)
        # Выбор версии ВК API
        api_version = "5.60"
        api = vk.API(session, v=api_version)

        self.log.info("Версия API: " + api_version)
        self.log.info("Авторизация завершена!")

        self.messages = api.messages
        self.users = api.users
        self.wall = api.wall
        self.photos = api.photos
        self.friends = api.friends
        self.news = api.news
        self.likes = api.likes
        self.status = api.status

    #Отправка статуса "печатает сообщение"
    def typing(self,inbox):
        messages = self.messages
        if (self.check_chat(inbox)):
            messages.setActivity(type='typing', chat_id=inbox['chat_id'])
        else:
            messages.setActivity(type='typing', user_id=inbox['user_id'])

    #Отправка сообщения
    def sendMessage(self, inbox, message):
        messages = self.messages
        self.typing(inbox)
        time.sleep(4)
        if (self.check_chat(inbox)):
            messages.send(random_id=random.randint(1, 999999),
                                    chat_id=inbox['chat_id'],
                                    message=message)
        else:
            messages.send(random_id=random.randint(1, 999999),
                                    user_id=inbox['user_id'],
                                    message=message)

    #Установка статуса-времени
    def setTimeStatus(self):
        status = self.status
        now = time.strftime("%H:%M")
        date = time.strftime("%d:%m:%Y")
        ej_time = self.convertToNumberEmoji(now)
        ej_date = self.convertToNumberEmoji(date)
        status.set(text="&#8986; " + ej_time + " &#128467; " + ej_date)

    #Перевод простого числа в Эмоджи - число
    def convertToNumberEmoji(self, value):
        value = str(value)
        list_numbers_emoji = ["0&#8419;", "1&#8419;", "2&#8419;", "3&#8419;", "4&#8419;", "5&#8419;", "6&#8419;",
                              "7&#8419;", "8&#8419;", "9&#8419;"]
        list_numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        list_out = []
        string_out = ""
        for list_numbers in value:
            if(str(list_numbers).isdigit()):
                list_out.append(list_numbers_emoji[int(list_numbers)])
            else:
                list_out.append(list_numbers)
        for datetime in list_out:
            string_out = string_out + datetime
        return string_out

    #Проверка типа исходящего сообщения (true - групповая беседа, false - пользователь)
    def check_chat(self, messages):
        if 'chat_id' in messages:
            return True
        else:
            return False

    #Проверка на наличие новых друзей и отписок
    def check_friends(self):

        friends = self.friends

        #отписываемся от удавлиших бота товарищей
        unFriends = friends.getRequests(out=1)
        for user_id in unFriends['items']:
            friends.delete(user_id=user_id)

        #добавляем новых друзей
        toFriends = friends.getRequests(out=0)
        for user_id in toFriends['items']:
            friends.add(user_id=user_id)

    def get_photo_id(self, user_info):
        if 'photo_id' in user_info[0]:
            photo_meta = user_info[0]['photo_id'].split('_')
            photo_id = photo_meta[1]
            return photo_id

    def get_like(self, inbox, user_info):
        photo_id = self.get_photo_id(user_info)
        if(self.isLike(user_info)):
            self.likes.add(type='photo', owner_id=user_info[0]['id'], item_id=photo_id)
            self.sendMessage(inbox, user_info[0]['first_name'] + ", держи &#9829; симпотяжка!")
        else:
            self.sendMessage(inbox, user_info[0]['first_name'] + ", ты уже получил свой лайк! &#9996;")


    def isLike(self, user_info):
        photo_id = self.get_photo_id(user_info)
        user_info = user_info[0]
        isLike = self.likes.isLiked(type="photo", owner_id=user_info['id'], item_id=photo_id)
        if(isLike['liked'] == 1):
            return False
        else:
            return True
