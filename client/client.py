import sys
import logging

from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, QThread

logger = logging.getLogger()

class Client(QObject):
    instance = None

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

    def __init__(self):
        super().__init__()
        logger.debug("")

        self.requestQueue = None
        self.responseQueue = None
        self.eventQueue = None
        self.realDataQueue = None

        self.eventQueueWorker = None
        self.realDataQueueWorker = None

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

        self.eventQueueWorker = Client.QueueWorker(self.eventQueue)
        self.eventQueueWorker.start()
        self.realDataQueueWorker = Client.QueueWorker(self.realDataQueue)
        self.realDataQueueWorker.start()

    def login(self):
        logging.debug("")
        self.requestQueue.put(("login",))

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
        # logger.debug(f"request: {request}, result:{result}")

        return result

    def stock_basic_info(self, stock_no, screen_no):
        logging.debug("")
        self.requestQueue.put(("stock_basic_info", {"stock_no": stock_no, "screen_no": screen_no}))
        request, result = self.responseQueue.get()
        logger.debug(f"request: {request}, result:{result}")

        return result

    def stock_price_real(self, code_list, screen_no, discard_old_stocks: bool):
        logging.debug("")
        opt_type = "1"
        if discard_old_stocks:
            opt_type = "0"
        self.requestQueue.put(
            ("stock_price_real",
             {"screen_no": screen_no,
              "code_list": code_list,
              "opt_type": opt_type})
        )

    def condition_load(self):
        logging.debug("")
        self.requestQueue.put(("condition_load",))

    def stocks_info(self, code_list, screen_no):
        logging.debug(f"code_list:{code_list}")
        self.requestQueue.put(("stocks_info", {"code_list": code_list, "screen_no": screen_no}))
        request, result = self.responseQueue.get()

        return result

    def condition_info(self, name, code: int, screen_no):
        logging.debug("")
        self.requestQueue.put(("condition_info", {"name": name, "code": code, "screen_no": screen_no}))
        request, result = self.responseQueue.get()

        return result

    def stop_condition_info(self, name, code: int, screen_no):
        logging.debug("")
        self.requestQueue.put(("stop_condition_info", {"name": name, "code": code, "screen_no": screen_no}))

    def daily_chart(self, code, screen_no):
        logging.debug("")
        self.requestQueue.put(("daily_chart", {"stock_no": code, "screen_no": screen_no}))
        request, result = self.responseQueue.get()

        return result

    def minute_chart(self, code, tick_range, screen_no):
        logging.debug("")
        self.requestQueue.put(("minute_chart", {"stock_no": code, "tick_range": tick_range, "screen_no": screen_no}))
        request, result = self.responseQueue.get()

        return result

    def send_order(self, account_no, order_type, stock_no, quantity, price, hoga, order_no, screen_no):
        logging.debug("")
        self.requestQueue.put(
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
