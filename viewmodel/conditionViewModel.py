import logging
import time
from datetime import datetime
from PyQt5.QtCore import QObject, pyqtSlot, pyqtProperty, pyqtSignal, QVariant, Qt, QAbstractListModel, QModelIndex

from client import Client
from .stockPriceItemData import StockPriceItemData
from .logViewModel import LogViewModel
from .marketViewModel import MarketViewModel

logger = logging.getLogger()

class ConditionModel(QAbstractListModel):
    NameRole = Qt.UserRole + 1
    CodeRole = Qt.UserRole + 2
    MonitoringRole = Qt.UserRole + 3

    def __init__(self, data=None):
        super().__init__()
        self.data = data or []
        logger.debug(f"data:{data}")

    def rowCount(self, parent=None):
        return len(self.data)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or index.row() >= len(self.data):
            return QVariant()

        item = self.data[index.row()]
        if role == self.NameRole:
            logger.debug(f"{item['name']}")
            return item['name']
        elif role == self.CodeRole:
            logger.debug(f"{item['code']}")
            return item['code']
        elif role == self.MonitoringRole:
            logger.debug(f"{item['monitoring']}")
            return item['monitoring']

        return QVariant()

    def roleNames(self):
        return {
            self.NameRole: b"name",
            self.CodeRole: b"code",
            self.MonitoringRole: b"monitoring"
        }

    def addItem(self, item):
        """ 리스트에 아이템을 추가하는 메서드 """
        self.beginInsertRows(QModelIndex(), len(self.data), len(self.data))
        self.data.append(item)
        self.endInsertRows()

    def removeItem(self, item):
        """ 리스트에서 아이템을 찾아 삭제하는 메서드 """
        if item in self.data:
            index = self.data.index(item)
            self.beginRemoveRows(QModelIndex(), index, index)
            self.data.remove(item)
            self.endRemoveRows()

    def setItemValue(self, item, role, value):
        """ 특정 아이템의 값을 설정하는 메서드 """
        logger.debug(f"item:{item}, role:{role}, value:{value}")
        if item in self.data:
            index = self.data.index(item)
            if role == self.NameRole:
                item["name"] = value
            elif role == self.CodeRole:
                item["code"] = value
            elif role == self.MonitoringRole:
                item["monitoring"] = value
            else:
                return False  # 지원되지 않는 역할일 경우 False 반환

            self.dataChanged.emit(self.index(index), self.index(index), [role])
            return True
        return False  # 아이템이 존재하지 않으면 False 반환

class ConditionViewModel(QObject):
    conditionListChanged = pyqtSignal()
    conditionStockListChanged = pyqtSignal()
    conditionRealReceived = pyqtSignal(dict)

    priceInfoKeys_ = ['시가', '고가', '저가', '현재가', '기준가', '전일대비기호', '전일대비', '등락율', '거래량', '전일거래량대비', '거래대금']
    max_realtime_condition_count = 5

    def __init__(self, marketViewModel, qmlContext, parent=None):
        super().__init__(parent)
        self.qmlContext = qmlContext
        self.qmlContext.setContextProperty('conditionViewModel', self)

        self._conditionList = ConditionModel()
        self._conditionInfoDict = {}
        self._currentConditionCode = -1

        self.marketViewModel = marketViewModel

        Client.getInstance().registerEventCallback("condition_load", self.onConditionList)
        Client.getInstance().registerRealDataCallback("stock_price_real", self.__onStockPriceReal)
        Client.getInstance().registerRealDataCallback("condition_info_real", self.__onConditionInfoReal)

        self.conditionRealReceived.connect(self.__onConditionInfoRealReceived)

        self.marketViewModel.stockPriceInfoChanged.connect(self.__stockPriceInfoChanged)

    @pyqtProperty(ConditionModel, notify=conditionListChanged)
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
        logger.debug(f"name:{name}, code:{code}")
        foundCond = None
        for cond in self._conditionList.data:
            if code == cond["code"]:
                foundCond = cond
                break
        if foundCond is None:
            logger.error(f"condition is not found.")
            return

        if code in self._conditionInfoDict:
            self._currentConditionCode = code
            self.conditionStockListChanged.emit()
            return

        if len(self._conditionInfoDict) >= self.max_realtime_condition_count:
            LogViewModel.getInstance().log(f'condition count reached max count({self.max_realtime_condition_count})')
            stop_cond_key = next(iter(self._conditionInfoDict))

            stopCond = None
            for cond in self._conditionList.data:
                if cond['code'] == stop_cond_key:
                    stopCond = cond
                    break

            if stopCond is None or len(stopCond['name']) == 0:
                logger.error(f"condition {code} name is not found.")
                raise Exception

            del self._conditionInfoDict[stop_cond_key]

            self._conditionList.setItemValue(stopCond, ConditionModel.MonitoringRole, False)

            logger.debug(f"stop {stop_cond_key}:{stopCond['name']} condition info")
            LogViewModel.getInstance().log(f"stop condition:{stopCond['name']})")
            Client.getInstance().stop_condition_info(stopCond['name'], stop_cond_key, "1004")

        self._conditionList.setItemValue(foundCond, ConditionModel.MonitoringRole, True)

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
        self.conditionList = ConditionModel([{'code': int(x[0]), 'name': x[1], 'monitoring': False} for x in result])
        logger.debug(f"self.conditionList:{self.conditionList.data}")

    @pyqtSlot(tuple)
    def __onStockPriceReal(self, data):
        # logger.debug(f"data[0]:{data[0]}")
        for key in self._conditionInfoDict:
            stockPriceList = self._conditionInfoDict[key]
            for stock in stockPriceList:
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

    @pyqtSlot(dict)
    def __onConditionInfoReal(self, data):
        logger.debug("")
        self.conditionRealReceived.emit(data)

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
            # logger.debug(priceItemData)
            stockPriceList.append(priceItemData)

        return stockPriceList

    @pyqtSlot(dict)
    def __onConditionInfoRealReceived(self, data):
        logger.debug(f"data:{data}")
        # code: str, id_type: str, cond_name: str, cond_index: str
        cond_index = int(data["cond_index"])
        stockPriceList = self._conditionInfoDict[cond_index]
        codeList = [stockPrice.code for stockPrice in stockPriceList]

        stockName = ''

        if data["id_type"] == 'I':  # 종목편입
            codeList.append(data['code'])
            stock = self.marketViewModel.getStockPriceItemDataByCode(data['code'])
            stockName = stock.name
            stockPriceList.append(stock)
            if stock.priceInfoReceived:
                Client.getInstance().stock_price_real([stock.code], "1004", discard_old_stocks=False)
            else:
                Client.getInstance().stock_basic_info(stock.code, "1004")

        elif data["id_type"] == 'D':  # 종목이탈
            Client.getInstance().stop_stock_price_real(data['code'], "1004")
            codeList.remove(data['code'])
            for stock in stockPriceList:
                if stock.code == data['code']:
                    stockName = stock.name
                    stockPriceList.remove(stock)
                    break

        self._conditionInfoDict[cond_index] = stockPriceList
        if cond_index == self._currentConditionCode:
            self.conditionStockListChanged.emit()

        formattedTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log = ''
        if data["id_type"] == 'I':
            log = f"\n[{formattedTime}][종목편입]({data['cond_name']}:{data['code']}:{stockName})"
        elif data["id_type"] == 'D':
            log = f"\n[{formattedTime}][종목이탈]({data['cond_name']}:{data['code']}:{stockName})"

        if len(log) > 0:
            with open("실시간검색.txt", "a", encoding="utf-8") as f:
                f.write(log)
            LogViewModel.getInstance().log(log)

    @pyqtSlot(str, dict)
    def __stockPriceInfoChanged(self, stockCode, priceInfo):
        changedStock = self.marketViewModel.getStockPriceItemDataByCode(stockCode)
        for key in self._conditionInfoDict:
            stockPriceList = self._conditionInfoDict[key]
            for stock in stockPriceList:
                if stock.code == changedStock:
                    stock.setPriceInfo(priceInfo, True)
