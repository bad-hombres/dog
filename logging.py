 # -*- coding: utf8 -*
import datetime
import sys

class Logger:
    def __init__(self, publisher):
        self.publisher = publisher

    def __log__(self, symbol, level, message):
        d = datetime.datetime.now()
        line = u"timestamp=%s~type=logs~level=%s~message=%s\n" % (d, level, message.replace("=", u"%3d").replace("~", "%7e"))
        sys.stdout.write(line)
        sys.stdout.flush()

    def error(self, message):
        self.__log__("*", "ERROR", message)

    def info(self, message):
        self.__log__("+", "INFO", message)

    def warn(self, message):
        self.__log__("!", "WARN", message)
