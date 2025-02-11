import sys
import logging

from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, QThread

logger = logging.getLogger()

class Client(QObject):
    instance = None

    class EventQueueWorker(QThread):
        def __init__(self, eventQueue):
            super().__init__()
            logger.debug("")
            self.eventQueue = eventQueue
            self.eventMap = {}

        def run(self):
            while True:
                request, result = self.eventQueue.get()
                logger.debug(f"request: {request}")
                logger.debug(f"typeof result: {type(result)}")
                logger.debug(f"result: {result}")
                if self.eventMap[request]:
                    logger.debug(f"self.eventMap[{request}]: {self.eventMap[request]}")
                    self.eventMap[request](result)

    def __init__(self):
        super().__init__()
        logger.debug("")

        self.requestQueue = None
        self.responseQueue = None
        self.eventQueue = None

        self.eventQueueWorker = None

    @classmethod
    def getInstance(cls):
        if cls.instance is None:
            cls.instance = Client()
        return cls.instance

    """
    public method
    """
    def init(self,
             requestQueue, responseQueue,
             eventQueue):
        self.requestQueue = requestQueue
        self.responseQueue = responseQueue
        self.eventQueue = eventQueue
        self.eventQueueWorker = Client.EventQueueWorker(self.eventQueue)
        self.eventQueueWorker.start()

    def login(self, callback):
        logging.debug("")
        self.requestQueue.put(("login",))
        self.eventQueueWorker.eventMap["login"] = callback

    def login_info(self):
        logging.debug("")
        self.requestQueue.put(("login_info",))
        request, result = self.responseQueue.get()
        logger.debug(f"request: {request}, result:{result}")

        return result

    def account_info(self, account_no, screen_no):
        logging.debug("")
        self.requestQueue.put(("account_info", {"account_no": account_no, "screen_no": screen_no}))
        request, result = self.responseQueue.get()
        logger.debug(f"request: {request}, result:{result}")

        return result

    def stock_list(self):
        logging.debug("")
        self.requestQueue.put(("stock_list",))
        request, result = self.responseQueue.get()
        logger.debug(f"request: {request}, result:{result}")

        return result

    def stock_basic_info(self, stock_no, screen_no):
        logging.debug("")
        self.requestQueue.put(("stock_basic_info", {"stock_no": stock_no, "screen_no": screen_no}))
        request, result = self.responseQueue.get()
        logger.debug(f"request: {request}, result:{result}")

        return result
