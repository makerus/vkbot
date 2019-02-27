import config

from vk_api.api import VkApi
import vk_api.logger as logger

log = logger.Logger('main')

bot = VkApi({
    'client_id': config.CLIENT_ID,
    "scope": config.SCOPE,
    "api_v": config.VERSION_API,
    "login": config.LOGIN,
    "password": config.PASSWORD
})

bot.login()
