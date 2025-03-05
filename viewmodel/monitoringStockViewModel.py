import logging
from collections import deque
from datetime import datetime, timedelta

from PyQt5.QtCore import QObject, pyqtSlot, pyqtProperty, pyqtSignal, QVariant
from client import Client
from .stockPriceItemData import StockPriceItemData
from .marketViewModel import MarketViewModel
from .logViewModel import LogViewModel

logger = logging.getLogger()

class MonitoringStockViewModel(QObject):
    stockListChanged = pyqtSignal()
    tradingValueListChanged = pyqtSignal()
    maxTradingValueChanged = pyqtSignal()
    tradingValueInTimeListChanged = pyqtSignal()
    stockPriceRealReceived = pyqtSignal(tuple)
    priceInfoKeys_ = ['시가', '고가', '저가', '현재가', '기준가', '전일대비기호', '전일대비', '등락율', '거래량', '전일거래량대비', '거래대금']
    maxCount = 10

    def __init__(self, mainViewModel, marketViewModel, qmlContext, parent=None):
        logger.debug("")
        super().__init__(parent)
        self.qmlContext = qmlContext
        self.qmlContext.setContextProperty("monitoringStockViewModel", self)

        self._stockList = []
        self._tradingValueList = []
        self._maxTradingValue = '0'
        self._tradingValueInTimeDataList = []
        self._tradingValueInTimeList = []
        self._chegyeolBuyTradingValueInTimeList = []
        self._chegyeolSellTradingValueInTimeList = []

        self.mainViewModel = mainViewModel
        self.marketViewModel = marketViewModel

        Client.getInstance().registerRealDataCallback("stock_price_real", self.__onStockPriceReal)

        self.stockPriceRealReceived.connect(self.__onStockPriceRealReceived)

    @pyqtProperty(list, notify=stockListChanged)
    def stockList(self):
        return self._stockList

    @stockList.setter
    def stockList(self, val):
        if self._stockList != val:
            self._stockList = val
            self.stockListChanged.emit()

    @pyqtProperty(list, notify=tradingValueListChanged)
    def tradingValueList(self):
        return self._tradingValueList

    @tradingValueList.setter
    def tradingValueList(self, val):
        if self._tradingValueList != val:
            self._tradingValueList = val
            self.tradingValueListChanged.emit()

    @pyqtProperty(list, notify=tradingValueInTimeListChanged)
    def tradingValueInTimeList(self):
        return self._tradingValueInTimeList

    @tradingValueInTimeList.setter
    def tradingValueInTimeList(self, val):
        if self._tradingValueInTimeList != val:
            self._tradingValueInTimeList = val
            self.tradingValueInTimeListChanged.emit()

    @pyqtProperty(list)
    def chegyeolBuyTradingValueInTimeList(self):
        return self._chegyeolBuyTradingValueInTimeList

    @pyqtProperty(list)
    def chegyeolSellTradingValueInTimeList(self):
        return self._chegyeolSellTradingValueInTimeList

    @pyqtProperty(str, notify=maxTradingValueChanged)
    def maxTradingValue(self):
        return self._maxTradingValue

    @maxTradingValue.setter
    def maxTradingValue(self, val):
        if self._maxTradingValue != val:
            self._maxTradingValue = val
            self.maxTradingValueChanged.emit()

    """
    method for qml side
    """
    @pyqtSlot(str, str)
    def add(self, name: str, code: str):
        if len(self._stockList) >= MonitoringStockViewModel.maxCount:
            return

        for stock in self._stockList:
            if stock.code == code:
                return
        Client.getInstance().stock_price_real(code, "1007", discard_old_stocks=False)
        self.__addStock(code)
        self.__updateTradingValueList()

        logger.debug(f"{self.stockList}")

    @pyqtSlot(str)
    def delete(self, code: str):
        self.__deleteStock(code)
        self.__updateTradingValueList()
        Client.getInstance().stop_stock_price_real(code, "1007")

        logger.debug(f"{self.stockList}")

    @pyqtSlot(str, result=bool)
    def isMonitoringStock(self, code):
        for stock in self._stockList:
            if stock.code == code:
                return True
        return False

    """
    client model event
    """
    def __onStockPriceReal(self, data: tuple):
        # logger.debug(f"data:{data}")
        self.stockPriceRealReceived.emit(data)

    """
    private method
    """
    def __addStock(self, code):
        codeList = [x.code for x in self._stockList] + [code]
        self._tradingValueInTimeDataList.append((code, deque()))
        self._tradingValueInTimeList.append('0')
        self._chegyeolBuyTradingValueInTimeList.append('0')
        self._chegyeolSellTradingValueInTimeList.append('0')
        self.__updateStockList(codeList)

    def __deleteStock(self, code):
        codeList = [x.code for x in self._stockList]
        codeList_ = [x for x in codeList if x not in [code]]
        self.__updateStockList(codeList_)
        for i in range(len(self._tradingValueInTimeDataList)):
            if self._tradingValueInTimeDataList[i][0] == code:
                del self._tradingValueInTimeDataList[i]
                del self._tradingValueInTimeList[i]
                del self._chegyeolBuyTradingValueInTimeList[i]
                del self._chegyeolSellTradingValueInTimeList[i]
                break

    def __updateStockList(self, codeList):
        stockPriceList = []

        if self.mainViewModel.testFlag:
            for code in codeList:
                priceItemData = StockPriceItemData('', code)
                stockPriceList.append(priceItemData)
        else:
            for code in codeList:
                stockPriceItemData = self.marketViewModel.getStockPriceItemDataByCode(code)
                stockPriceList.append(stockPriceItemData)

        self.stockList = stockPriceList

    def __updateTradingValueList(self):
        maxTradingValue = 0
        tradingValueList = []
        tradingValueRatioList = []
        for stock in self._stockList:
            tradingValue = 0 if stock.tradingValue == '' else int(stock.tradingValue)
            tradingValueList.append(tradingValue)
            maxTradingValue = max(int(maxTradingValue), tradingValue)

        if maxTradingValue == 0:
            return

        for i in range(len(self._stockList)):
            tradingValueRatioList.append(tradingValueList[i] / maxTradingValue)

        self.maxTradingValue = str(maxTradingValue)
        self.tradingValueList = tradingValueRatioList

    def __updateTradingValueInTimeList(self, stock: StockPriceItemData):
        # tradingValueInTimeList, chegyeolBuyTradingValueInTimeList, chegyeolSellTradingValueInTimeList는 종목 순서가 일치
        tradingValueInTimeList = self._tradingValueInTimeList
        chegyeolBuyTradingValueInTimeList = self._chegyeolBuyTradingValueInTimeList
        chegyeolSellTradingValueInTimeList = self._chegyeolSellTradingValueInTimeList

        for i in range(len(self._tradingValueInTimeDataList)):
            item = self._tradingValueInTimeDataList[i]
            if item[0] == stock.code:
                tradingValue = 0 if stock.tradingValue == '' else int(stock.tradingValue)
                chegyeolTradingValue = abs(int(stock.currentPrice)) * int(stock.chegyeolVolume)

                item[1].append((stock.chegyeolTime, tradingValue, chegyeolTradingValue))

                # 3천만원 이상 매수체결을 로그창에 출력
                if chegyeolTradingValue > 30000000:
                    log = f"\n[{stock.chegyeolTime}][대량매수체결]({stock.name}:{chegyeolTradingValue})"
                    with open("대량매수체결.txt", "a", encoding="utf-8") as f:
                        f.write(log)
                    LogViewModel.getInstance().log(log)

                # 가장 오래된 데이터가 1분 이상 차이 나면 삭제 (최적화된 while 루프)
                newChegyeolTime = self.timeToSeconds(stock.chegyeolTime)
                while item[1]:
                    firsTime = self.timeToSeconds(item[1][0][0])
                    if (newChegyeolTime - firsTime) > 60:
                        item[1].popleft()
                    else:
                        break

                tradingValueInTime = item[1][-1][1] - item[1][0][1] if len(item[1]) > 0 else 0
                tradingValueInTimeList[i] = str(tradingValueInTime)

                buySum = 0
                sellSum = 0
                # tradingValueInTimeData의 deque 전체를 순회하며 매수거래대금과 매도거래대금을 합하여 1분간 매수거래대금 및 매도거래대금을 계산한다.
                for t in item[1]:  # item[1]: tradingValueInTimeData의 deque, t: deque 내의 아이템
                    if t[2] > 0:  # t[0]: 체결시각(str), t[1]: 누적거래대금(int), t[2]: 체결거래대금(int)
                        buySum += t[2]
                    elif t[2] < 0:
                        sellSum += t[2]

                chegyeolBuyTradingValueInTimeList[i] = str(buySum)
                chegyeolSellTradingValueInTimeList[i] = str(abs(sellSum))
                break

        # logger.debug(f"chegyeolBuyTradingValueInTimeList:{chegyeolBuyTradingValueInTimeList}")
        # logger.debug(f"chegyeolSellTradingValueInTimeList:{chegyeolSellTradingValueInTimeList}")

        # self.tradingValueInTimeListChanged.emit()

    @pyqtSlot(tuple)
    def __onStockPriceRealReceived(self, data):
        for stock in self._stockList:
            if data[0] == stock.code:
                if stock.volume != data[1]['13']:
                    stock.currentPrice = data[1]['10']
                    stock.diffPrice = data[1]['11']
                    stock.diffRate = data[1]['12']
                    stock.volume = data[1]['13']
                    stock.startPrice = data[1]['16']
                    stock.highPrice = data[1]['17']
                    stock.lowPrice = data[1]['18']
                    stock.diffSign = data[1]['25']
                    stock.volumeRate = data[1]['30']
                    stock.tradingValue = data[1]['14']
                    stock.chegyeolTime = data[1]['20']
                    stock.chegyeolVolume = data[1]['15']

                self.__updateTradingValueList()
                self.__updateTradingValueInTimeList(stock)
                break

    @staticmethod
    def timeToSeconds(timeStr: str) -> int:
        # "HHMMSS" 형식의 문자열을 시간, 분, 초로 변환하여 초 단위로 반환
        return int(timeStr[:2]) * 3600 + int(timeStr[2:4]) * 60 + int(timeStr[4:6])
