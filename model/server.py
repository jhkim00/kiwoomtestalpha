import sys
import logging
import asyncio
import multiprocessing
from multiprocessing import Process, Queue
import pythoncom
from PyQt5.QtWidgets import QApplication
from model.manager import Manager

logger = logging.getLogger()

class Server(Process):
    app = QApplication(sys.argv)
    funcIndex = 0
    futureIndex = 1

    def __init__(self,
                 requestQueue, responseQueue,
                 eventQueue, realDataQueue):
        super().__init__()
        logger.debug("")

        self.requestQueue = requestQueue
        self.responseQueue = responseQueue
        self.eventQueue = eventQueue
        self.realDataQueue = realDataQueue

        self.requestHandlerMap = None
        self.eventList = None
        self.manager = None
        self.finish = False

    def run(self):
        logger.setLevel(logging.DEBUG)
        logger.propagate = 0
        formatter = logging.Formatter('[%(asctime)s][%(levelname)s][%(thread)d][%(filename)s:%(funcName)s:%(lineno)d]'
                                      ' %(message)s')
        streamHandler = logging.StreamHandler()
        streamHandler.setFormatter(formatter)
        logger.addHandler(streamHandler)

        logger.debug("")

        asyncio.run(self.mainEventLoop())

    async def mainEventLoop(self):
        self.requestHandlerMap = {
            "login": [self.handle_login, asyncio.Future()],
            "login_info": [self.handle_login_info, asyncio.Future()],
            "account_info": [self.handle_account_info, asyncio.Future()],
            "stock_list": [self.handle_stock_list, asyncio.Future()],
            "stock_basic_info": [self.handle_stock_basic_info, asyncio.Future()],
            "stock_price_real": [self.handle_stock_price_real, None],
        }
        self.eventList = ["login"]
        logger.debug("")
        self.manager = Manager()
        self.manager.notifyLoginCompleted = self.notifyLoginCompleted
        self.manager.notifyLoginInfo = self.notifyLoginInfo
        self.manager.notifyAccountInfo = self.notifyAccountInfo
        self.manager.notifyStockList = self.notifyStockList
        self.manager.notifyStockBasicInfo = self.notifyStockBasicInfo
        self.manager.notifyStockPriceReal = self.notifyStockPriceReal

        """COM 메시지 루프와 요청 처리를 하나의 이벤트 루프에서 실행"""
        # `asyncio.create_task()`를 사용하여 두 개의 태스크를 동시에 실행
        task1 = asyncio.create_task(self.comEventLoop())  # COM 메시지 처리
        task2 = asyncio.create_task(self.processRequests())  # 요청 처리

        await asyncio.gather(task1, task2)  # 두 개의 작업을 동시에 실행

    async def comEventLoop(self):
        """COM 메시지 루프 (무한 루프)"""
        while not self.finish:
            pythoncom.PumpWaitingMessages()  # COM 이벤트 처리
            await asyncio.sleep(0.01)  # CPU 점유율 최소화

    async def processRequests(self):
        """요청을 블로킹 대기 후 처리 (multiprocessing.Queue 사용)"""
        while True:
            try:
                logger.debug("")
                loop = asyncio.get_running_loop()
                request, *params = await loop.run_in_executor(None, self.requestQueue.get)
                logger.debug(f"request:{request}")
                if request == "finish":
                    self.finish = True
                    break
                self.requestHandlerMap[request][self.funcIndex](*params)
                future = self.requestHandlerMap[request][self.futureIndex]
                # 실시간 요청은 요청에 대한 future가 없는 구조
                if not future:
                    continue
                result = await future

                # regenerate future
                self.requestHandlerMap[request][self.futureIndex] = asyncio.Future()

                logger.debug(f"result:{result}")
                if request in self.eventList:
                    self.eventQueue.put((request, result))
                else:
                    self.responseQueue.put((request, result))
            except Exception:
                pass  # 타임아웃 발생 시 무시하고 다시 대기

    def notifyLoginCompleted(self, result: bool):
        logger.debug("")
        self.requestHandlerMap["login"][self.futureIndex].set_result(result)

    def notifyLoginInfo(self, info):
        logger.debug("")
        self.requestHandlerMap["login_info"][self.futureIndex].set_result(info)

    def notifyAccountInfo(self, info):
        logger.debug("")
        self.requestHandlerMap["account_info"][self.futureIndex].set_result(info)

    def notifyStockList(self, stockList):
        logger.debug("")
        self.requestHandlerMap["stock_list"][self.futureIndex].set_result(stockList)

    def notifyStockBasicInfo(self, info):
        logger.debug("")
        self.requestHandlerMap["stock_basic_info"][self.futureIndex].set_result(info)

    def notifyStockPriceReal(self, data):
        logger.debug("")
        self.realDataQueue.put(("stock_price_real", data))

    """
    request handler
    """
    def handle_login(self):
        logger.debug("")
        self.manager.commConnect()

    def handle_login_info(self):
        logger.debug("")
        self.manager.getLoginInfo()

    def handle_account_info(self, data):
        logger.debug(data)
        self.manager.getAccountInfo(data)

    def handle_stock_list(self):
        logger.debug("")
        self.manager.getStockList()

    def handle_stock_basic_info(self, data):
        logger.debug(data)
        self.manager.getStockBasicInfo(data)

    def handle_stock_price_real(self, data):
        logger.debug(data)
        self.manager.getStockPriceRealData(data)
