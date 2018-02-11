"""
:param messages: Сообщение с командой
:param api: Ссылка на объект бота и на его методы
:params params: Дополнительные данные
"""


def speak(messages, api, params):
    user_id = messages['user_id']
    user = api.get_user(user_id)

    phrase = str(" ".join(params))

    message_out = str(user['first_name']) + ", " + phrase
    return message_out


#Объект команды
cmd = {}

#Возращаем сформированную команду
cmd.update({'name': "/скажи", 'run': speak})