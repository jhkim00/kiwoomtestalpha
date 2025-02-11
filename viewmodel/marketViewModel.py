import logging

from PyQt5.QtCore import QObject, pyqtSlot, pyqtProperty, pyqtSignal, QVariant
from PyQt5.QtQml import QJSValue
from client import Client

logger = logging.getLogger()

class MarketViewModel(QObject):
    stockListChanged = pyqtSignal()
    searchedStockListChanged = pyqtSignal()
    currentStockChanged = pyqtSignal()

    def __init__(self, qmlContext, parent=None):
        logger.debug("")
        super().__init__(parent)
        self.qmlContext = qmlContext
        self.qmlContext.setContextProperty('marketViewModel', self)

        self._stockList = []
        self._searchedStockList = []
        self._currentStock = None

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

    """
    method for qml side
    """
    @pyqtSlot()
    def test(self):
        logger.debug("")
        result = Client.getInstance().stock_basic_info(self.currentStock["code"], "1002")
        logger.debug(f"result:{result}")

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
