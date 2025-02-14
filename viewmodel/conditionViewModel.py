import logging
import time
from PyQt5.QtCore import QObject, pyqtSlot, pyqtProperty, pyqtSignal, QVariant

from client import Client
from .stockPriceItemData import StockPriceItemData

logger = logging.getLogger()

class ConditionViewModel(QObject):
    conditionListChanged = pyqtSignal()
    conditionStockListChanged = pyqtSignal()
    priceInfoKeys_ = ['시가', '고가', '저가', '현재가', '기준가', '전일대비기호', '전일대비', '등락율', '거래량', '전일거래량대비']
    max_realtime_condition_count = 5

    def __init__(self, qmlContext, parent=None):
        super().__init__(parent)
        self.qmlContext = qmlContext
        self.qmlContext.setContextProperty('conditionViewModel', self)

        self._conditionList = []
        self._conditionInfoDict = {}
        self._currentConditionCode = -1

        Client.getInstance().registerEventCallback("condition_load", self.onConditionList)
        Client.getInstance().registerRealDataCallback("stock_price_real", self.__onStockPriceReal)

    @pyqtProperty(list, notify=conditionListChanged)
    def conditionList(self):
        return self._conditionList

    @conditionList.setter
    def conditionList(self, val):
        if self._conditionList != val:
            self._conditionList = val
            self.conditionListChanged.emit()

    @pyqtProperty(list, notify=conditionStockListChanged)
    def conditionStockList(self):
        if self._currentConditionCode >= 0:
            return self._conditionInfoDict[self._currentConditionCode]
        else:
            return []

    """
    method for qml side
    """
    @pyqtSlot()
    def load(self):
        logger.debug("")
        Client.getInstance().condition_load()

    @pyqtSlot(str, int)
    def conditionInfo(self, name, code):
        logger.debug("")
        found = False
        for cond in self._conditionList:
            if code == cond["code"]:
                found = True
                break
        if not found:
            logger.error(f"condition is not found. name:{name}, code:{code}")
            return

        if code in self._conditionInfoDict:
            self._currentConditionCode = code
            self.conditionStockListChanged.emit()
            return

        if len(self._conditionInfoDict) >= self.max_realtime_condition_count:
            stop_cond_key = next(iter(self._conditionInfoDict))
            stop_cond_name = ''
            for cond in self._conditionList:
                if cond['code'] == stop_cond_key:
                    stop_cond_name = cond['name']
                    break

            if len(stop_cond_name) == 0:
                logger.error(f"condition {code} name is not found.")
                raise Exception

            del self._conditionInfoDict[stop_cond_key]
            logger.debug(f"stop {stop_cond_key}:{stop_cond_name} condition info")
            Client.getInstance().stop_condition_info(stop_cond_name, stop_cond_key, "1004")

        result = Client.getInstance().condition_info(name, code, "1004")
        logger.debug(f"result:{result}")
        if int(result["cond_index"]) != code:
            logger.error(f"result[cond_index]:{result['cond_index']}, code:{code}")
            raise Exception

        codeList = result["code_list"]
        stockPriceList = self.__getStockPriceList(codeList)
        # logger.debug(f"stockPriceList:{stockPriceList}")
        self._conditionInfoDict[code] = stockPriceList
        self._currentConditionCode = code
        self.conditionStockListChanged.emit()
        # logger.debug(f"self._conditionInfoDict:{self._conditionInfoDict}")

    """
    client model event
    """
    def onConditionList(self, result: list):
        logger.debug(f"result:{result}")
        self.conditionList = [{'code': int(x[0]), 'name': x[1]} for x in result]
        logger.debug(f"self.conditionList:{self.conditionList}")        

    @pyqtSlot(tuple)
    def __onStockPriceReal(self, data):
        # logger.debug(f"data:{data}")
        for stock in self.conditionStockList:
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
                break

    """
    private method
    """
    def __getStockPriceList(self, codeList):
        result = Client.getInstance().stocks_info(codeList, "1004")
        # logger.debug(f"result:{result}")
        stockPriceList = []
        for info in result:
            priceInfo = {key: info[key] for key in self.priceInfoKeys_ if key in info}
            priceItemData = StockPriceItemData(info['종목명'], info['종목코드'], priceInfo, fromSingleInfo=False)
            logger.debug(priceItemData)
            stockPriceList.append(priceItemData)

        return stockPriceList
