import logging

from PyQt5.QtCore import QObject, pyqtSlot, pyqtProperty, pyqtSignal, QVariant
from client import Client
from .stockPriceItemData import StockPriceItemData
from .marketViewModel import MarketViewModel

logger = logging.getLogger()

class MonitoringStockViewModel(QObject):
    stockListChanged = pyqtSignal()
    tradingValueListChanged = pyqtSignal()
    maxTradingValueChanged = pyqtSignal()
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

        self.mainViewModel = mainViewModel
        self.marketViewModel = marketViewModel

        Client.getInstance().registerRealDataCallback("stock_price_real", self.__onStockPriceReal)

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

        self.__updateStockList([x.code for x in self._stockList] + [code])
        self.__updateTradingValueList()

        logger.debug(f"{self.stockList}")

    @pyqtSlot(str)
    def delete(self, code: str):
        codeList = [x.code for x in self._stockList]
        self.__updateStockList([x for x in codeList if x not in [code]])
        self.__updateTradingValueList()

        logger.debug(f"{self.stockList}")

    @pyqtSlot(str, result=bool)
    def isMonitoringStock(self, code):
        for stock in self._stockList:
            if stock.code == code:
                return True
        return False

    def __updateStockList(self, codeList):
        stockPriceList = []

        if self.mainViewModel.testFlag:
            for code in codeList:
                priceItemData = StockPriceItemData('', code)
                stockPriceList.append(priceItemData)
        else:
            result = Client.getInstance().stocks_info(codeList, "1007")
            logger.debug(f"result:{result}")

            for info in result:
                priceInfo = {key: info[key] for key in self.priceInfoKeys_ if key in info}
                priceItemData = StockPriceItemData(info['종목명'], info['종목코드'], priceInfo, fromSingleInfo=False)
                logger.debug(priceItemData)
                stockPriceList.append(priceItemData)

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

    @pyqtSlot(tuple)
    def __onStockPriceReal(self, data):
        # logger.debug(f"data:{data}")
        for stock in self._stockList:
            if data[0] == stock.code:
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

                self.__updateTradingValueList()
                break
