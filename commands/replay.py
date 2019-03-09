import random


class Replay:
    """
    Команда #менялюбит
    Тестовая команда, которая случайно выбирает из беседы участника
    и отправляет запись о том, что этот участник вас любит
    """
    def __init__(self):
        self.name = 'менялюбит'
        self.event = "message_new"

    def filter(self, object_, symbol_command, symbol_answer):
        """
        Проверка на соответствие команды
        :param object_:
        :param symbol_command:
        :param symbol_answer:
        :return Boolean:
        """
        if 'text' in object_:
            text_msg = str(object_['text']).lower()
            text_cmd = symbol_command + self.name

            return text_cmd == text_msg

    @staticmethod
    def result(api, item):
        """
        Если надо что-то ответить, то выполняется этот метод
        :param api:
        :param item:
        :return:
        """
        list_profiles = api.query('messages.getConversationMembers',
                                  {'peer_id': item['object']['peer_id']})['profiles']

        profiles = []
        for profile in list_profiles:
            profiles.append(profile['first_name'] + ' ' + profile['last_name'])

        random_user = profiles[random.randint(0, len(profiles) - 1)]
        return random_user + ' - любит тебя, но это не точно!'
