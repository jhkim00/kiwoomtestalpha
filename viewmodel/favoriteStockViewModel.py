import logging

from PyQt5.QtCore import QObject, pyqtSlot, pyqtProperty, pyqtSignal, QVariant
from client import Client
from .dbHelper import DbHelper
from .stockPriceItemData import StockPriceItemData
from .marketViewModel import MarketViewModel

logger = logging.getLogger()

class FavoriteStockViewModel(QObject):
    stockListChanged = pyqtSignal()
    priceInfoKeys_ = ['시가', '고가', '저가', '현재가', '기준가', '전일대비기호', '전일대비', '등락율', '거래량', '전일거래량대비', '거래대금']

    def __init__(self, mainViewModel, marketViewModel, qmlContext, parent=None):
        logger.debug("")
        super().__init__(parent)
        self.qmlContext = qmlContext
        self.qmlContext.setContextProperty("favoriteStockViewModel", self)

        self._stockList = []

        self.mainViewModel = mainViewModel
        self.marketViewModel = marketViewModel

        Client.getInstance().registerRealDataCallback("stock_price_real", self.__onStockPriceReal)

        marketViewModel.loadCompleted.connect(self.__onMarketViewModelLoadCompleted)

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

        self.__updateStockList([x["code"] for x in stockList])

        if len(stockList) > 0 and self.marketViewModel.currentStock is None:
            self.marketViewModel.currentStock = {"code": self.stockList[0].code, "name": self.stockList[0].name}

    @pyqtSlot(str, str)
    def add(self, name: str, code: str):
        for stock in self._stockList:
            if stock.code == code:
                return

        DbHelper.getInstance().insertStockToTableFavorite(name, code)

        self.__updateStockList([x.code for x in self._stockList] + [code])

    @pyqtSlot(str)
    def delete(self, code: str):
        for stock in self._stockList:
            if stock.code == code:
                DbHelper.getInstance().deleteStockFromTableFavorite(code)
                break

        codeList = [x.code for x in self._stockList]
        self.__updateStockList([x for x in codeList if x not in [code]])

    @pyqtSlot(str, result=bool)
    def isFavoriteStock(self, code):
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
            result = Client.getInstance().stocks_info(codeList, "1003")
            logger.debug(f"result:{result}")

            for info in result:
                priceInfo = {key: info[key] for key in self.priceInfoKeys_ if key in info}
                priceItemData = StockPriceItemData(info['종목명'], info['종목코드'], priceInfo, fromSingleInfo=False)
                logger.debug(priceItemData)
                stockPriceList.append(priceItemData)

        self.stockList = stockPriceList

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
                break

    """
    private method
    """
    @pyqtSlot()
    def __onMarketViewModelLoadCompleted(self):
        logger.debug("")
        self.load()