from core import VkApi
import config
from commands.speak import cmd as speak
import logger

bot = VkApi(config.CLIENT_ID, config.EMAIL, config.PASSWORD, config.SCOPE)

logger.log("Подключение команд")

commands = [speak]  #Тут указать команды

list_commands = []

for cmd in commands:
    list_commands.append(str(cmd['name']))

logger.log("Были подключены следующий команды: " + str(",".join(list_commands)))

logger.log("Запуск обработки сообщений")

while True:
    last_message = bot.get_last_messages(10)
    bot.listen(last_message, commands)
