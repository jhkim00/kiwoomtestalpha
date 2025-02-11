import sys
import logging

from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, QThread

logger = logging.getLogger()

class Client(QObject):
    """
    signals for event callback
    """
    login_result = pyqtSignal()
    # login_info_result = pyqtSignal(list)
    # account_info_result = pyqtSignal(tuple)
    # stock_list_result = pyqtSignal(list)
    # stock_basic_info_result = pyqtSignal(tuple)

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
                else:
                    logger.debug("??????????????????????")

    def __init__(self,
                 requestQueue, responseQueue,
                 eventQueue):
        super().__init__()
        logger.debug("")

        self.requestQueue = requestQueue
        self.responseQueue = responseQueue
        self.eventQueue = eventQueue

        """
        slots for callback
        """
        self._login_result_slot = None

        self.eventQueueWorker = Client.EventQueueWorker(self.eventQueue)
        self.eventQueueWorker.start()

    """
    public method
    """
    def login(self, callback):
        logging.debug("")
        self.requestQueue.put(("login",))
        self.eventQueueWorker.eventMap["login"] = callback

    def login_info(self):
        logging.debug("")
        self.requestQueue.put(("login_info",))
        request, result = self.responseQueue.get()
        logger.debug(f"request: {request}, result:{result}")
        logger.debug(f"typeof result: {type(result)}")

        return result

    def account_info(self, account_no, screen_no):
        logging.debug("")
        self.requestQueue.put(("account_info", {"account_no": account_no, "screen_no": screen_no}))
        request, result = self.responseQueue.get()
        logger.debug(f"request: {request}, result:{result}")
        logger.debug(f"typeof result: {type(result)}")

        return result

    def stock_list(self):
        logging.debug("")
        self.requestQueue.put(("stock_list",))
        request, result = self.responseQueue.get()
        logger.debug(f"request: {request}, result:{result}")
        logger.debug(f"typeof result: {type(result)}")

        return result

    def stock_basic_info(self, stock_no, screen_no):
        logging.debug("")
        self.requestQueue.put(("stock_basic_info", {"stock_no": stock_no, "screen_no": screen_no}))
        request, result = self.responseQueue.get()
        logger.debug(f"request: {request}, result:{result}")
        logger.debug(f"typeof result: {type(result)}")

        return result
