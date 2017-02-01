#Инициализация ВК API
import vk
import logger
import time
import core_bot

log = logger.Log()
bot = core_bot.Bot()

#Работа со временем
save_time = ""  # переменная для проверки времени
uptime_start = time.time() #время запуска бота
#Работа с сообщениями
msg_ids = "" #id непрочитанных сообщений
log.info("Чтение сообщений...")

while True:
    #Проверка, не изменилось ли время
    if(save_time == "" or save_time != time.strftime("%H:%M")):
        bot.setTimeStatus()
        save_time = time.strftime("%H:%M")

    # Поиск диалогов с непрочитанными сообщениями
    dialogs = bot.messages.getDialogs(unread=1)
    #Разбор непрочитанного диалога!
    if dialogs['count'] >= 1:
        for items in dialogs['items']:
            dialog_msg = items['message'] #Объект с сообщением из диалога
            #Если нас не кикнули из группы
            if('action' not in dialog_msg or dialog_msg['action'] != 'chat_kick_user'):
                msg_id = dialog_msg['id']  # id непрочитанного сообщения
                if('users_count' in dialog_msg):
                    users_count = dialog_msg['users_count']  # Кол-во людей в диалоге
                if('chat_id' in dialog_msg):
                    chat_id = dialog_msg['chat_id']  # ID Диалога у бота
                dialog_title = dialog_msg['title']  # Заголовок диалога
                text_msg = dialog_msg['body'].lower()  # Текст диалога
                last_user = dialog_msg['user_id']  # ID последнего, написавшего в диалог
                # Поиск информации о последнем написавшем
                last_user_info = bot.users.get(user_ids=last_user, fields='photo_id')
                user = last_user_info[0]
                msg_ids = str(msg_id) + ','

                if(text_msg == "!оботе"):
                    uptime_end = time.time() - uptime_start
                    uptime_text = bot.convertToNumberEmoji(round(uptime_end))
                    send_text = "&#9995; Привет, я бот &#127974;! \n" \
                                + "&#128170; Мой автор: " + bot.author \
                                + "\n &#128467; Год создания: " + bot.date_create \
                                + "\n &#8986; Время работы: " + uptime_text + " секунд."
                    bot.sendMessage(dialog_msg,send_text)

                if(text_msg == "!статы"):
                    friends_list = bot.friends.get()
                    messages_list = bot.messages.get(out=1)
                    messages_list_in = bot.messages.get(out=0)
                    dialogs_list = bot.messages.getDialogs()
                    send_text = "Статистика: \n"\
                                + "&#128051; Кол-во друзей: " + str(friends_list['count']) + "\n" \
                                + "&#9993; Отправлено сообщений: " + str(messages_list['count']) + "\n" \
                                + "&#128233; Получено сообщений: " + str(messages_list_in['count']) + "\n" \
                                + "&#128227; Количество диалогов: " + str(dialogs_list['count']) + '\n'
                    bot.sendMessage(dialog_msg, send_text)

                if(text_msg == "!лайк"):
                    bot.get_like(dialog_msg, last_user_info)

                if(text_msg == "!аптайм"):
                    uptime_end = time.time() - uptime_start
                    uptime_text = bot.convertToNumberEmoji(round(uptime_end))
                    send_text =  "&#8986; Время работы: " + uptime_text + " секунд."
                    bot.sendMessage(dialog_msg, send_text)

                if(text_msg == "!время"):
                    now = time.strftime("%H:%M")
                    now_time = bot.convertToNumberEmoji(now)
                    send_text = "&#8986; Сейчас время: "+now_time
                    bot.sendMessage(dialog_msg, send_text)

                if(text_msg == "!обомне"):
                    adv_info = bot.users.get(user_ids=last_user, fields='counters')
                    adv_name = adv_info[0]
                    adv_info = adv_info[0]['counters']
                    send_text = "&#9999; Информация о: " + adv_name['first_name'] + " " + adv_name['last_name'] + "&#9999; \n" \
                                + "Заметок: "+str(adv_info['notes']) + '\n' \
                                + "Фотографий: "+str(adv_info['photos']) + '\n' \
                                + "Альбомов: "+str(adv_info['albums']) + '\n' \
                                + "Аудиозаписей (если открыто): "+str(adv_info['audios']) + '\n' \
                                + "Подписчиков: "+str(adv_info['followers']) + '\n' \
                                + "Групп: "+str(adv_info['pages']) + '\n' \
                                + "Друзей онлайн: "+str(adv_info['online_friends']) + '\n' \
                                + "Видеозаписей: "+str(adv_info['videos']) + '\n' \
                                + "Подписок: "+str(adv_info['subscriptions']) + '\n' \
                                + "Друзей: "+str(adv_info['friends']) + '\n'
                    bot.sendMessage(dialog_msg, send_text)


    #Когда проработали все сообщения, помечаем их, как прочитанные
    if(msg_ids != ""):
        bot.messages.markAsRead(message_ids=msg_ids)
        msg_ids = ""
    #проверка друзей
    bot.check_friends()

    #Ждать 5 секунд
    time.sleep(5)
