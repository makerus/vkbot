import time
#Логгер для бота
class Log:

    def getDateTime(self):
        now = time.strftime("%H:%M")
        date = time.strftime("%d:%m:%Y")
        return "[" + date + "][" + now + "]"

    def info(self, value):
        date_now = self.getDateTime()
        print(date_now+"[ИНФО]: "+value)

    def error(self, value):
        date_now = self.getDateTime()
        print(date_now+"[ОШИБКА]: "+value)

    def action(self, value):
        date_now = self.getDateTime()
        print(date_now+"[ДЕЙСТВИЕ]: "+value)
