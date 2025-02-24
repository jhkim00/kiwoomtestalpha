import sys
import logging
import time
from collections import OrderedDict, deque

from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, QThread, QMutex, QMutexLocker, QWaitCondition

logger = logging.getLogger()


class QueueWorker(QThread):
    def __init__(self, queue):
        super().__init__()
        logger.debug("")
        self.queue = queue
        self.callbackMap = {}

    def run(self):
        while True:
            # logger.debug(f".")
            request, result = self.queue.get()
            # logger.debug(f"request: {request}")
            # logger.debug(f"typeof result: {type(result)}")
            # logger.debug(f"result: {result}")
            if request == "finish":
                logger.debug(f"finish received")
                break
            if request in self.callbackMap:
                callbacks = self.callbackMap[request]
                if callbacks and len(callbacks) > 0:
                    for cb in callbacks:
                        cb(result)

class RequestQueueProxy(QThread):
    def __init__(self, queue):
        super().__init__()
        logger.debug("")
        self.queue = queue
        self.buffer = deque()
        self.mutex = QMutex()
        self.condition = QWaitCondition()

    def insert(self, data):
        with QMutexLocker(self.mutex):
            self.buffer.append(data)
            self.condition.wakeOne()

    def run(self):
        while True:
            with QMutexLocker(self.mutex):
                if not self.buffer:
                    self.condition.wait(self.mutex)

                filtered_dict = OrderedDict(self.buffer)
                self.buffer = deque(filtered_dict.items())
                data = self.buffer.popleft()

            self.queue.put(data)
            if data == 'finish':
                logger.debug(f"finish received")
                return
            time.sleep(0.01)

class Client(QObject):
    instance = None

    def __init__(self):
        super().__init__()
        logger.debug("")

        self.requestQueue = None
        self.responseQueue = None
        self.eventQueue = None
        self.realDataQueue = None

        self.eventQueueWorker = None
        self.realDataQueueWorker = None
        self.requestQueueProxy = None

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
             eventQueue, realDataQueue):
        self.requestQueue = requestQueue
        self.responseQueue = responseQueue
        self.eventQueue = eventQueue
        self.realDataQueue = realDataQueue

        self.eventQueueWorker = QueueWorker(self.eventQueue)
        self.eventQueueWorker.start()
        self.realDataQueueWorker = QueueWorker(self.realDataQueue)
        self.realDataQueueWorker.start()
        self.requestQueueProxy = RequestQueueProxy(self.requestQueue)
        self.requestQueueProxy.start()

    def login(self):
        logging.debug("")
        self.requestQueueProxy.insert(("login", None))

    def login_info(self):
        logging.debug("")
        self.requestQueueProxy.insert(("login_info", None))
        request, result = self.responseQueue.get()
        logger.debug(f"request: {request}, result:{result}")

        return result

    def account_info(self, account_no, screen_no):
        logging.debug("")
        self.requestQueueProxy.insert(("account_info", {"account_no": account_no, "screen_no": screen_no}))

    def stock_name_by_code(self, stock_no):
        logging.debug("")
        self.requestQueueProxy.insert(("stock_name_by_code", {"stock_no": stock_no}))
        request, result = self.responseQueue.get()

        return result

    def stock_list(self):
        logging.debug("")
        self.requestQueueProxy.insert(("stock_list", None))
        request, result = self.responseQueue.get()
        # logger.debug(f"request: {request}, result:{result}")

        return result

    def stock_basic_info(self, stock_no, screen_no):
        logging.debug("")
        self.requestQueueProxy.insert(("stock_basic_info", {"stock_no": stock_no, "screen_no": screen_no}))

    def stock_price_real(self, code_list, screen_no, discard_old_stocks: bool):
        logging.debug("")
        opt_type = "1" if discard_old_stocks else "0"

        self.requestQueueProxy.insert(
            ("stock_price_real",
             {"screen_no": screen_no,
              "code_list": code_list,
              "opt_type": opt_type})
        )

    def stop_stock_price_real(self, code, screen_no):
        logging.debug("")
        self.requestQueueProxy.insert(("stop_stock_price_real", {"screen_no": screen_no, "code": code}))

    def condition_load(self):
        logging.debug("")
        self.requestQueueProxy.insert(("condition_load", None))

    def stocks_info(self, code_list, screen_no):
        logging.debug(f"code_list:{code_list}")
        self.requestQueueProxy.insert(("stocks_info", {"code_list": code_list, "screen_no": screen_no}))
        request, result = self.responseQueue.get()

        return result

    def condition_info(self, name, code: int, screen_no):
        logging.debug("")
        self.requestQueueProxy.insert(("condition_info", {"name": name, "code": code, "screen_no": screen_no}))
        request, result = self.responseQueue.get()

        return result

    def stop_condition_info(self, name, code: int, screen_no):
        logging.debug("")
        self.requestQueueProxy.insert(("stop_condition_info", {"name": name, "code": code, "screen_no": screen_no}))

    def daily_chart(self, code, screen_no):
        logging.debug("")
        self.requestQueueProxy.insert(("daily_chart", {"stock_no": code, "screen_no": screen_no}))

    def minute_chart(self, code, tick_range, screen_no):
        logging.debug("")
        self.requestQueueProxy.insert(("minute_chart", {"stock_no": code, "tick_range": tick_range, "screen_no": screen_no}))

    def send_order(self, account_no, order_type, stock_no, quantity, price, hoga, order_no, screen_no):
        logging.debug("")
        self.requestQueueProxy.insert(
            ("send_order",
             {"account_no": account_no,
              "order_type": order_type,
              "stock_no": stock_no,
              "quantity": quantity,
              "price": price,
              "hoga": hoga,
              "order_no": order_no,
              "screen_no": screen_no}
             )
        )

    def get_hoga(self, stock_no, screen_no):
        logging.debug("")
        self.requestQueueProxy.insert(("hoga", {"stock_no": stock_no, "screen_no": screen_no}))

    def registerEventCallback(self, event: str, callback):
        self.registerCallback(self.eventQueueWorker, event, callback)

    def registerRealDataCallback(self, realType: str, callback):
        self.registerCallback(self.realDataQueueWorker, realType, callback)

    @classmethod
    def registerCallback(cls, que, type_: str, callback):
        if que:
            if type_ in que.callbackMap:
                callbacks = que.callbackMap[type_]
                if callback not in callbacks:
                    callbacks.append(callback)
            else:
                que.callbackMap[type_] = [callback]
