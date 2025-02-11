import logging

from PyQt5.QtCore import QObject, pyqtSlot, pyqtProperty, pyqtSignal, QVariant
from client import Client
from .dbHelper import DbHelper

logger = logging.getLogger()

class FavoriteStockViewModel(QObject):
    stockListChanged = pyqtSignal()

    def __init__(self, qmlContext, parent=None):
        logger.debug("")
        super().__init__(parent)
        self.qmlContext = qmlContext
        self.qmlContext.setContextProperty("favoriteStockViewModel", self)

        self._stockList = []

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
        logger.debug(rows)
        for item in rows:
            stockList.append({'name': item[0], 'code': item[1]})

        logger.debug(stockList)

        self.stockList = stockList

    @pyqtSlot(str, str)
    def add(self, name: str, code: str):
        for stock in self._stockList:
            if stock["code"] == code:
                return

        DbHelper.getInstance().insertStockToTableFavorite(name, code)

        stock = {"name": name, "code": code}

        self._stockList.append(stock)
        logger.debug(self._stockList)
        self.stockListChanged.emit()

    @pyqtSlot(str)
    def delete(self, code: str):
        stockToRemove = None
        for stock in self._stockList:
            if stock['code'] == code:
                DbHelper.getInstance().deleteStockFromTableFavorite(code)
                stockToRemove = stock
                break

        self._stockList.remove(stockToRemove)
        logger.debug(self._stockList)
        self.stockListChanged.emit()

    @pyqtSlot(str, result=bool)
    def isFavoriteStock(self, code):
        for stock in self._stockList:
            if stock['code'] == code:
                return True
        return False
