import logging

from PyQt5.QtCore import QObject, pyqtSlot, pyqtProperty, pyqtSignal, QVariant
from client import Client
from .dbHelper import DbHelper
from .stockPriceItemData import StockPriceItemData

logger = logging.getLogger()

class FavoriteStockViewModel(QObject):
    stockListChanged = pyqtSignal()

    def __init__(self, qmlContext, parent=None):
        logger.debug("")
        super().__init__(parent)
        self.qmlContext = qmlContext
        self.qmlContext.setContextProperty("favoriteStockViewModel", self)

        self._stockList = []
        self.priceInfoKeys = ['시가', '고가', '저가', '현재가', '기준가', '대비기호', '전일대비', '등락율', '거래량', '거래대비']

    @pyqtProperty(list, notify=stockListChanged)
    def stockList(self):
        return self._stockList

    @stockList.setter
    def stockList(self, val):
        if self._stockList != val:
            self._stockList = val
            self.stockListChanged.emit()

    """
    method for qml side
    """
    @pyqtSlot()
    def load(self):
        rows = DbHelper.getInstance().selectTableFavorite()
        stockList = []
        stockPriceList = []
        logger.debug(rows)
        for item in rows:
            stockList.append({'name': item[0], 'code': item[1]})

        logger.debug(stockList)

        for stock in stockList:
            result = Client.getInstance().stock_basic_info(stock["code"], "1003")
            if len(result) > 0:
                priceInfo = {key: result[0][key] for key in self.priceInfoKeys if key in result[0]}
                priceItemData = StockPriceItemData(stock['name'], stock['code'], priceInfo)
                logger.debug(priceItemData)
                stockPriceList.append(priceItemData)

        self.stockList = stockPriceList

    @pyqtSlot(str, str)
    def add(self, name: str, code: str):
        for stock in self._stockList:
            if stock.code == code:
                return

        DbHelper.getInstance().insertStockToTableFavorite(name, code)

        result = Client.getInstance().stock_basic_info(code, "1003")
        if len(result) > 0:
            priceInfo = {key: result[0][key] for key in self.priceInfoKeys if key in result[0]}
            priceItemData = StockPriceItemData(name, code, priceInfo)
            self._stockList.append(priceItemData)

        logger.debug(self._stockList)
        self.stockListChanged.emit()

    @pyqtSlot(str)
    def delete(self, code: str):
        stockToRemove = None
        for stock in self._stockList:
            if stock.code == code:
                DbHelper.getInstance().deleteStockFromTableFavorite(code)
                stockToRemove = stock
                break

        self._stockList.remove(stockToRemove)
        logger.debug(self._stockList)
        self.stockListChanged.emit()

    @pyqtSlot(str, result=bool)
    def isFavoriteStock(self, code):
        for stock in self._stockList:
            if stock.code == code:
                return True
        return False
