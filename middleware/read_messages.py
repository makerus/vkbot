import logger


def read_messages(messages, api):
    """
    Подсчет непрочитанных сообщений, которые нужно прочитать
    :param messages: Сообщение с командой
    :param api: Ссылка на объект бота и на его методы
    """
    if 'count' not in api.data:
        api.data.update({"count": 0})
        count = api.data['count']
    else:
        count = api.data['count']

    api.data['count'] += 1
    logger.log("Количество непрочитанных сообщений: " + str(api.data['count']))
