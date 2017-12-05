import datetime

class Logger:
    def __init__(self, publisher):
        self.publisher = publisher

    def __log__(self, symbol, level, message):
        d = datetime.datetime.now()
        line = "[%s] %s - %s: %s" % (symbol, d, level, message)
        print line
        self.publisher.send_multipart([b"LOG", line.encode('ascii')])

    def error(self, message):
        self.__log__("*", "ERROR", message)

    def info(self, message):
        self.__log__("+", "INFO", message)

    def warn(self, message):
        self.__log__("!", "WARN", message)
