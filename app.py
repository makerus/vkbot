import config

from vk_api.api import VkApi
from vk_api.logger import Logger

from commands.replay import Replay

log = Logger('main')

bot = VkApi({
    'client_id': config.CLIENT_ID,
    'scope': config.SCOPE_GROUP,
    'api_v': config.VERSION_API,
    'token': config.TOKEN_GROUP,
    'max_timeout': config.MAX_TIMEOUT,
    'group_id': config.GROUP_ID
})

bot.get_token(bot)
bot.long_poll()

# Инициализация команд
bot.register_commands(Replay)
# Регистрация символа команды
bot.register_symbol_command('#')
# Регистрация символа ответа
bot.register_symbol_answer('!')

