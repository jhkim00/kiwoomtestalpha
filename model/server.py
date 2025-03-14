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
                 eventQueue, realDataQueue, chejanDataQueue):
        super().__init__()
        logger.debug("")

        self.requestQueue = requestQueue
        self.responseQueue = responseQueue
        self.eventQueue = eventQueue
        self.realDataQueue = realDataQueue
        self.chejanDataQueue = chejanDataQueue

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
            "stock_name_by_code": [self.handle_stock_name_by_code, asyncio.Future()],
            "stock_list": [self.handle_stock_list, asyncio.Future()],
            "stock_basic_info": [self.handle_stock_basic_info, asyncio.Future()],
            "stock_price_real": [self.handle_stock_price_real, None],
            "stop_stock_price_real": [self.handle_stop_stock_price_real, None],
            "condition_load": [self.handle_condition_load, asyncio.Future()],
            "stocks_info": [self.handle_stocks_info, asyncio.Future()],
            "condition_info": [self.handle_condition_info, asyncio.Future()],
            "stop_condition_info": [self.handle_stop_condition_info, None],
            "weekly_chart": [self.handle_weekly_chart, asyncio.Future()],
            "daily_chart": [self.handle_daily_chart, asyncio.Future()],
            "minute_chart": [self.handle_minute_chart, asyncio.Future()],
            "send_order": [self.handle_send_order, asyncio.Future()],
            "hoga": [self.handle_hoga, asyncio.Future()],
            "michegyeol_info": [self.handle_michegyeol_info, asyncio.Future()],
        }
        self.eventList = ["login", "account_info", "stock_basic_info", "condition_load", "weekly_chart", "daily_chart",
                          "minute_chart", "hoga", "michegyeol_info"]
        logger.debug("")
        self.manager = Manager()
        self.manager.notifyLoginResult = self.notifyLoginResult
        self.manager.notifyLoginInfo = self.notifyLoginInfo
        self.manager.notifyAccountInfo = self.notifyAccountInfo
        self.manager.notifyStockNameByCode = self.notifyStockNameByCode
        self.manager.notifyStockList = self.notifyStockList
        self.manager.notifyStockBasicInfo = self.notifyStockBasicInfo
        self.manager.notifyStockPriceReal = self.notifyStockPriceReal
        self.manager.notifyConditionList = self.notifyConditionList
        self.manager.notifyStocksInfo = self.notifyStocksInfo
        self.manager.notifyConditionInfo = self.notifyConditionInfo
        self.manager.notifyWeeklyChart = self.notifyWeeklyChart
        self.manager.notifyDailyChart = self.notifyDailyChart
        self.manager.notifyConditionInfoReal = self.notifyConditionInfoReal
        self.manager.notifyMinuteChart = self.notifyMinuteChart
        self.manager.notifyHogaRemainsReal = self.notifyHogaRemainsReal
        self.manager.notifyHoga = self.notifyHoga
        self.manager.notifySendOrderResult = self.notifySendOrderResult
        self.manager.notifyOrderChegyeolData = self.notifyOrderChegyeolData
        self.manager.notifyChejanData = self.notifyChejanData
        self.manager.notifyMichegyeolInfo = self.notifyMichegyeolInfo

        """ `asyncio.create_task()`를 사용하여 여러 개의 태스크를 동시에 실행"""
        tasks = [
            asyncio.create_task(self.comEventLoop()),       # COM 메시지 처리
            asyncio.create_task(self.processRequests()),    # 요청 처리
            asyncio.create_task(self.processEvents())       # 이벤트 처리
        ]

        """ 하나의 태스크가 종료되면 나머지 태스크들도 종료되도록 하여 프로세스가 종료되도록 함 """
        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        for task in pending:
            task.cancel()

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

    def notifyLoginResult(self, result: int):
        logger.debug("")
        self.requestHandlerMap["login"][self.futureIndex].set_result(result)

    def notifyLoginInfo(self, info):
        logger.debug("")
        self.requestHandlerMap["login_info"][self.futureIndex].set_result(info)

    def notifyAccountInfo(self, info):
        logger.debug("")
        self.requestHandlerMap["account_info"][self.futureIndex].set_result(info)

    def notifyStockNameByCode(self, name):
        logger.debug("")
        self.requestHandlerMap["stock_name_by_code"][self.futureIndex].set_result(name)

    def notifyStockList(self, stockList):
        logger.debug("")
        self.requestHandlerMap["stock_list"][self.futureIndex].set_result(stockList)

    def notifyStockBasicInfo(self, info):
        logger.debug("")
        self.requestHandlerMap["stock_basic_info"][self.futureIndex].set_result(info)

    def notifyStockPriceReal(self, data):
        # logger.debug("")
        self.realDataQueue.put(("stock_price_real", data))

    def notifyConditionList(self, conditionList):
        logger.debug("")
        self.requestHandlerMap["condition_load"][self.futureIndex].set_result(conditionList)

    def notifyStocksInfo(self, info):
        logger.debug("")
        self.requestHandlerMap["stocks_info"][self.futureIndex].set_result(info)

    def notifyConditionInfo(self, info):
        logger.debug("")
        self.requestHandlerMap["condition_info"][self.futureIndex].set_result(info)

    def notifyWeeklyChart(self, info):
        # logger.debug(f"info:{info}")
        self.requestHandlerMap["weekly_chart"][self.futureIndex].set_result(info)

    def notifyDailyChart(self, info):
        # logger.debug(f"info:{info}")
        self.requestHandlerMap["daily_chart"][self.futureIndex].set_result(info)

    def notifyMinuteChart(self, info):
        # logger.debug(f"info:{info}")
        self.requestHandlerMap["minute_chart"][self.futureIndex].set_result(info)

    def notifyConditionInfoReal(self, data):
        # logger.debug("")
        self.realDataQueue.put(("condition_info_real", data))

    def notifyHogaRemainsReal(self, data):
        self.realDataQueue.put(("hoga_remains_real", data))

    def notifyHoga(self, data):
        self.requestHandlerMap["hoga"][self.futureIndex].set_result(data)

    def notifySendOrderResult(self, result: int):
        self.requestHandlerMap["send_order"][self.futureIndex].set_result(result)

    def notifyOrderChegyeolData(self, data: dict):
        self.chejanDataQueue.put(("주문체결", data))

    def notifyChejanData(self, data: dict):
        self.chejanDataQueue.put(("잔고", data))

    def notifyMichegyeolInfo(self, info: list):
        self.requestHandlerMap["michegyeol_info"][self.futureIndex].set_result(info)

    """
    request handler
    """
    async def handle_login(self, _):
        logger.debug("")
        await self.manager.commConnect()

    async def handle_login_info(self, _):
        logger.debug("")
        await self.manager.getLoginInfo()

    async def handle_account_info(self, data):
        logger.debug(data)
        await self.manager.getAccountInfo(data)

    async def handle_stock_name_by_code(self, data):
        logger.debug(data)
        await self.manager.getStockNameByCode(data)

    async def handle_stock_list(self, _):
        logger.debug("")
        await self.manager.getStockList()

    async def handle_stock_basic_info(self, data):
        logger.debug(data)
        await self.manager.getStockBasicInfo(data)

    async def handle_stock_price_real(self, data):
        logger.debug(data)
        await self.manager.getStockPriceRealData(data)

    async def handle_stop_stock_price_real(self, data):
        logger.debug(data)
        await self.manager.stopStockPriceRealData(data)

    async def handle_condition_load(self, _):
        logger.debug("")
        await self.manager.getConditionLoad()

    async def handle_stocks_info(self, data):
        logger.debug("")
        await self.manager.getStocksInfo(data)

    async def handle_condition_info(self, data):
        logger.debug("")
        await self.manager.sendCondition(data)

    async def handle_stop_condition_info(self, data):
        logger.debug("")
        await self.manager.sendConditionStop(data)

    async def handle_weekly_chart(self, data):
        logger.debug("")
        await self.manager.getWeeklyChart(data)

    async def handle_daily_chart(self, data):
        logger.debug("")
        await self.manager.getDailyChart(data)

    async def handle_minute_chart(self, data):
        logger.debug("")
        await self.manager.getMinuteChart(data)

    async def handle_send_order(self, data):
        logger.debug("")
        await self.manager.sendOrder(data)

    async def handle_hoga(self, data):
        logger.debug("")
        await self.manager.getHoga(data)

    async def handle_michegyeol_info(self, data):
        logger.debug("")
        await self.manager.getMichegyeolInfo(data)
