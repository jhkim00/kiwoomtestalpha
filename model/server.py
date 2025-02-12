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
            "condition_load": [self.handle_condition_load, asyncio.Future()],
        }
        self.eventList = ["login", "condition_load"]
        logger.debug("")
        self.manager = Manager()
        self.manager.notifyLoginCompleted = self.notifyLoginCompleted
        self.manager.notifyLoginInfo = self.notifyLoginInfo
        self.manager.notifyAccountInfo = self.notifyAccountInfo
        self.manager.notifyStockList = self.notifyStockList
        self.manager.notifyStockBasicInfo = self.notifyStockBasicInfo
        self.manager.notifyStockPriceReal = self.notifyStockPriceReal
        self.manager.notifyConditionList = self.notifyConditionList

        """ `asyncio.create_task()`를 사용하여 여러 개의 태스크를 동시에 실행"""
        task1 = asyncio.create_task(self.comEventLoop())  # COM 메시지 처리
        task2 = asyncio.create_task(self.processRequests())  # 요청 처리
        task3 = asyncio.create_task(self.processEvents())  # 이벤트 처리

        await asyncio.gather(task1, task2, task3)  # 여러 개의 작업을 동시에 실행

    async def comEventLoop(self):
        """COM 메시지 루프 (무한 루프)"""
        while not self.finish:
            pythoncom.PumpWaitingMessages()  # COM 이벤트 처리
            await asyncio.sleep(0.01)  # CPU 점유율 최소화

    async def processRequests(self):
        while True:
            logger.debug("")
            loop = asyncio.get_running_loop()
            request, *params = await loop.run_in_executor(None, self.requestQueue.get)
            logger.debug(f"request:{request}")
            if request == "finish":
                self.finish = True
                break
            await self.requestHandlerMap[request][self.funcIndex](*params)

    async def processEvents(self):
        while True:
            logger.debug("")
            futures = [x[self.futureIndex] for x in self.requestHandlerMap.values() if x[self.futureIndex] is not None]
            done, pending = await asyncio.wait(futures, return_when=asyncio.FIRST_COMPLETED)
            for fut in done:
                for key in self.requestHandlerMap:
                    if fut == self.requestHandlerMap[key][self.futureIndex]:
                        if key in self.eventList:
                            self.eventQueue.put((key, fut.result()))
                        else:
                            self.responseQueue.put((key, fut.result()))

                        # regenerate future
                        self.requestHandlerMap[key][self.futureIndex] = asyncio.Future()
                        break

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

    def notifyConditionList(self, conditionList):
        logger.debug("")
        self.requestHandlerMap["condition_load"][self.futureIndex].set_result(conditionList)

    """
    request handler
    """
    async def handle_login(self):
        logger.debug("")
        await self.manager.commConnect()

    async def handle_login_info(self):
        logger.debug("")
        await self.manager.getLoginInfo()

    async def handle_account_info(self, data):
        logger.debug(data)
        await self.manager.getAccountInfo(data)

    async def handle_stock_list(self):
        logger.debug("")
        await self.manager.getStockList()

    async def handle_stock_basic_info(self, data):
        logger.debug(data)
        await self.manager.getStockBasicInfo(data)

    async def handle_stock_price_real(self, data):
        logger.debug(data)
        await self.manager.getStockPriceRealData(data)

    async def handle_condition_load(self):
        logger.debug("")
        await self.manager.getConditionLoad()
