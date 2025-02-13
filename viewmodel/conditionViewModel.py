import logging

from PyQt5.QtCore import QObject, pyqtSlot, pyqtProperty, pyqtSignal, QVariant

from client import Client
from .stockPriceItemData import StockPriceItemData

logger = logging.getLogger()

class ConditionViewModel(QObject):
    conditionListChanged = pyqtSignal()
    conditionStockListChanged = pyqtSignal()
    priceInfoKeys_ = ['시가', '고가', '저가', '현재가', '기준가', '전일대비기호', '전일대비', '등락율', '거래량', '전일거래량대비']

    def __init__(self, qmlContext, parent=None):
        super().__init__(parent)
        self.qmlContext = qmlContext
        self.qmlContext.setContextProperty('conditionViewModel', self)

        self._conditionList = []
        self._conditionInfoDict = {}
        self._currentConditionCode = ''

        Client.getInstance().registerEventCallback("condition_load", self.onConditionList)

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
        return self._conditionInfoDict[self._currentConditionCode]

    """
    method for qml side
    """
    @pyqtSlot()
    def load(self):
        logger.debug("")
        Client.getInstance().condition_load()

    @pyqtSlot(str, str)
    def conditionInfo(self, name, code):
        logger.debug("")
        found = False
        for cond in self._conditionList:
            if code == cond["code"]:
                found = True
                break
        if not found:
            logger.error(f"condition is not found name:{name}, code:{code}")
            return

        result = Client.getInstance().condition_info(name, code, "1004")
        logger.debug(f"result:{result}")
        if int(result["cond_index"]) != int(code):
            logger.error(f"result[cond_index]:{result['cond_index']}, code:{code}")
            raise Exception

        codeList = result["code_list"]
        stockPriceList = self.__getStockPriceList(codeList)
        logger.debug(f"stockPriceList:{stockPriceList}")
        self._conditionInfoDict[code] = stockPriceList
        self._currentConditionCode = code
        self.conditionStockListChanged.emit()
        logger.debug(f"self._conditionInfoDict:{self._conditionInfoDict}")

    """
    client model event
    """
    def onConditionList(self, result: list):
        logger.debug(f"result:{result}")
        self.conditionList = [{'code': x[0], 'name': x[1]} for x in result]
        logger.debug(f"self.conditionList:{self.conditionList}")
        self._currentConditionCode = self.conditionList[0]['code']

    """
    private method
    """
    def __getStockPriceList(self, codeList):
        result = Client.getInstance().stocks_info(codeList, "1004")
        logger.debug(f"result:{result}")
        stockPriceList = []
        for info in result:
            priceInfo = {key: info[key] for key in self.priceInfoKeys_ if key in info}
            priceItemData = StockPriceItemData(info['종목명'], info['종목코드'], priceInfo, fromSingleInfo=False)
            logger.debug(priceItemData)
            stockPriceList.append(priceItemData)

        return stockPriceList
