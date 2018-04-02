from datetime import datetime


def log(text):
    output = "["+str(datetime.strftime(datetime.now(), "%x %H:%M"))+"]LOG: " + str(text) + "..."
    log_info = open("info.log", 'a', encoding="utf-8")
    log_info.write(output+'\n')
    log_info.close()
    print(output)


def error(text):
    output = "["+str(datetime.strftime(datetime.now(), "%x %H:%M"))+"]ERROR: " + str(text) + "..."
    log_error = open("error.log", 'a', encoding="utf-8")
    log_error.write(output+'\n')
    log_error.close()
    print(output)


def debug(text):
    output = "[" + str(datetime.strftime(datetime.now(), "%x %H:%M")) + "]DEBUG: " + str(repr(text)) + "..."
    log_debug = open("debug.log", 'a', encoding="utf-8")
    log_debug.write(output + '\n')
    log_debug.close()
    print(repr(output))
