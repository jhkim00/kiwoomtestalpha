import logging

from PyQt5.QtCore import QObject, pyqtSlot, pyqtProperty, pyqtSignal, QVariant, Qt, QAbstractListModel, QModelIndex

from client import Client
from .marketViewModel import MarketViewModel

logger = logging.getLogger()


class ChegyeolInfo(QObject):
    timeChanged = pyqtSignal()
    priceChanged = pyqtSignal()
    volumeChanged = pyqtSignal()
    upDownTypeChanged = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._time = '00:00:00'
        self._price = ''
        self._volume = ''
        self._upDownType = ''

    @pyqtProperty(str, notify=timeChanged)
    def time(self):
        return self._time

    @time.setter
    def time(self, val: str):
        self._time = val
        self.timeChanged.emit()

    @pyqtProperty(str, notify=priceChanged)
    def price(self):
        return self._price

    @price.setter
    def price(self, val: str):
        self._price = val
        self.priceChanged.emit()

    @pyqtProperty(str, notify=volumeChanged)
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, val: str):
        self._volume = val
        self.volumeChanged.emit()

    @pyqtProperty(str, notify=upDownTypeChanged)
    def upDownType(self):
        return self._upDownType

    @upDownType.setter
    def upDownType(self, val: str):
        self._upDownType = val
        self.upDownTypeChanged.emit()

    def __str__(self):
        return (
            f'time:{self.time}\n'
            f'price:{self.price}\n'
            f'volume:{self.volume}\n'
            f'upDownType:{self.upDownType}\n'
        )

class ChegyeolViewModel(QObject):
    chegyeolModelChanged = pyqtSignal()
    currentPriceChanged = pyqtSignal()
    upDownTypeChanged = pyqtSignal()
    changeRateChanged = pyqtSignal()
    volumeChanged = pyqtSignal()
    tradingValueChanged = pyqtSignal()
    openPriceChanged = pyqtSignal()
    highPriceChanged = pyqtSignal()
    lowPriceChanged = pyqtSignal()
    
    def __init__(self, marketViewModel, qmlContext, parent=None):
        super().__init__(parent)
        self.qmlContext = qmlContext
        self.qmlContext.setContextProperty('chegyeolViewModel', self)

        self._chegyeolList = []
        self._currentPrice = ''
        self._upDownType = ''
        self._changeRate = ''
        self._volume = ''
        self._tradingValue = ''
        self._openPrice = ''
        self._highPrice = ''
        self._lowPrice = ''

        self.marketViewModel = marketViewModel        

        Client.getInstance().registerRealDataCallback("stock_price_real", self.__onStockPriceReal)        

    @pyqtProperty(list, notify=chegyeolModelChanged)
    def chegyeolModel(self):
        return self._chegyeolList[-50:][::-1]

    @pyqtProperty(str, notify=currentPriceChanged)
    def currentPrice(self):
        return self._currentPrice

    @currentPrice.setter
    def currentPrice(self, val: str):
        self._currentPrice = val
        self.currentPriceChanged.emit()

    @pyqtProperty(str, notify=upDownTypeChanged)
    def upDownType(self):
        return self._upDownType

    @upDownType.setter
    def upDownType(self, val: str):
        self._upDownType = val
        self.upDownTypeChanged.emit()

    @pyqtProperty(str, notify=changeRateChanged)
    def changeRate(self):
        return self._changeRate

    @changeRate.setter
    def changeRate(self, val: str):
        self._changeRate = val
        self.changeRateChanged.emit()

    @pyqtProperty(str, notify=volumeChanged)
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, val: str):
        self._volume = val
        self.volumeChanged.emit()

    @pyqtProperty(str, notify=tradingValueChanged)
    def tradingValue(self):
        return self._tradingValue

    @tradingValue.setter
    def tradingValue(self, val: str):
        self._tradingValue = val
        self.tradingValueChanged.emit()

    @pyqtProperty(str, notify=openPriceChanged)
    def openPrice(self):
        return self._openPrice

    @openPrice.setter
    def openPrice(self, val: str):
        self._openPrice = val
        self.openPriceChanged.emit()

    @pyqtProperty(str, notify=highPriceChanged)
    def highPrice(self):
        return self._highPrice

    @highPrice.setter
    def highPrice(self, val: str):
        self._highPrice = val
        self.highPriceChanged.emit()

    @pyqtProperty(str, notify=lowPriceChanged)
    def lowPrice(self):
        return self._lowPrice

    @lowPrice.setter
    def lowPrice(self, val: str):
        self._lowPrice = val
        self.lowPriceChanged.emit()

    """
    client model event
    """
    def __onStockPriceReal(self, data):
        # logger.debug(f"{data}")
        if self.marketViewModel.currentStock and data[0] == self.marketViewModel.currentStock['code']:
            timeStr = data[1]['20']
            timeStr = f"{timeStr[:2]}:{timeStr[2:4]}:{timeStr[4:]}"

            self._chegyeolList.append({
                "time": timeStr,
                "price": data[1]['10'],
                "volume": data[1]['15'],
                "upDownType": data[1]['25']
            })
            self.chegyeolModelChanged.emit()
            
            self.currentPrice = data[1]['10']
            self.upDownType = data[1]['25']
            self.changeRate = data[1]['12']
            self.volume = data[1]['13']
            self.tradingValue = data[1]['14']
            self.openPrice = data[1]['16']
            self.highPrice = data[1]['17']
            self.lowPrice = data[1]['18']
