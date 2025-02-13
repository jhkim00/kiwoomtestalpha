import logging

from PyQt5.QtCore import QObject, pyqtSlot, pyqtProperty, pyqtSignal, QVariant
from PyQt5.QtQml import QJSValue
from client import Client

logger = logging.getLogger()

class MarketViewModel(QObject):
    stockListChanged = pyqtSignal()
    searchedStockListChanged = pyqtSignal()
    currentStockChanged = pyqtSignal()
    basicInfoChanged = pyqtSignal()
    priceInfoChanged = pyqtSignal()

    def __init__(self, qmlContext, parent=None):
        logger.debug("")
        super().__init__(parent)
        self.qmlContext = qmlContext
        self.qmlContext.setContextProperty('marketViewModel', self)

        self._stockList = []
        self._searchedStockList = []
        self._currentStock = None

        self._basicInfo = {
            '신용비율': '',
            '시가총액': '',
            'PER': '',
            'PBR': '',
            '매출액': '',
            '영업이익': '',
            '당기순이익': '',
            '유통주식': '',
            '유통비율': ''
        }
        self._priceInfo = {
            '시가': '',
            '고가': '',
            '저가': '',
            '현재가': '',
            '기준가': '',
            '대비기호': '',
            '전일대비': '',
            '등락율': '',
            '거래량': '',
            '거래대비': ''
        }

        Client.getInstance().registerRealDataCallback("stock_price_real", self.__onStockPriceReal)

    @pyqtProperty(list, notify=stockListChanged)
    def stockList(self):
        return self._stockList

    @stockList.setter
    def stockList(self, val: list):
        self._stockList = val
        self.stockListChanged.emit()

    @pyqtProperty(list, notify=searchedStockListChanged)
    def searchedStockList(self):
        return self._searchedStockList

    @searchedStockList.setter
    def searchedStockList(self, val: list):
        self._searchedStockList = val
        self.searchedStockListChanged.emit()

    @pyqtProperty(QVariant, notify=currentStockChanged)
    def currentStock(self):
        return self._currentStock

    @currentStock.setter
    def currentStock(self, val: dict):
        if self._currentStock != val:
            logger.debug(f"stock:{val}")
            self._currentStock = val
            self.currentStockChanged.emit()

    @pyqtProperty(QVariant, notify=basicInfoChanged)
    def basicInfo(self):
        return self._basicInfo

    @basicInfo.setter
    def basicInfo(self, info: dict):
        if self._basicInfo != info:
            logger.debug(f'basicInfo: {info}')
            self._basicInfo = info
            self.basicInfoChanged.emit()

    @pyqtProperty(QVariant)
    def priceInfo(self):
        return self._priceInfo

    @priceInfo.setter
    def priceInfo(self, info: dict):
        if self._basicInfo != info:
            logger.debug(f'priceInfo: {info}')
            self._priceInfo = info
            self.priceInfoChanged.emit()

    """
    method for qml side
    """
    @pyqtSlot()
    def test(self):
        logger.debug("")
        Client.getInstance().stock_price_real([self.currentStock["code"]], "1002", discard_old_stocks=False)

    @pyqtSlot()
    def load(self):
        logger.debug("")
        self.stockList = Client.getInstance().stock_list()
        if len(self.stockList) > 0:
            self.currentStock = self.stockList[0]

    @pyqtSlot(QVariant)
    def setCurrentStock(self, val):
        if isinstance(val, dict):
            self.currentStock = val
        elif isinstance(val, QJSValue):
            self.currentStock = val.toVariant()

    @pyqtSlot(str)
    def setInputText(self, inputText):
        logger.debug(inputText)

        if len(inputText) == 0 or inputText == ' ':
            self.searchedStockList = []
        else:
            self.searchedStockList = list(map(lambda x: x,
                                              list(filter(lambda x: x["name"].lower().find(inputText.lower()) != -1
                                                                    or x["code"].lower().find(inputText.lower()) != -1,
                                                          self.stockList))))

    @pyqtSlot()
    def getStockBasicInfo(self):
        logger.debug("")
        result = Client.getInstance().stock_basic_info(self.currentStock["code"], "1002")
        if len(result) > 0:
            self.basicInfo = {key: result[key] for key in self.basicInfo if key in result}
            logger.debug(self.basicInfo)

            self.priceInfo = {key: result[key] for key in self.priceInfo if key in result}
            logger.debug(self.priceInfo)

    @pyqtSlot(tuple)
    def __onStockPriceReal(self, data):
        logger.debug(f"data:{data}")
        if self.currentStock is None:
            return
        if data[0] == self.currentStock["code"]:
            self._priceInfo['현재가'] = data[1]['10']
            self._priceInfo['전일대비'] = data[1]['11']
            self._priceInfo['등락율'] = data[1]['12']
            self._priceInfo['거래량'] = data[1]['13']
            self._priceInfo['시가'] = data[1]['16']
            self._priceInfo['고가'] = data[1]['17']
            self._priceInfo['저가'] = data[1]['18']
            self._priceInfo['대비기호'] = data[1]['25']
            self._priceInfo['거래대비'] = data[1]['30']

            self.priceInfoChanged.emit()
