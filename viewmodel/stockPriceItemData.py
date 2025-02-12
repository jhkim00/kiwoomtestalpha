import logging

from PyQt5.QtCore import QObject, pyqtProperty, pyqtSignal

logger = logging.getLogger()

class StockPriceItemData(QObject):
    nameChanged = pyqtSignal()
    codeChanged = pyqtSignal()
    startPriceChanged = pyqtSignal()
    highPriceChanged = pyqtSignal()
    lowPriceChanged = pyqtSignal()
    currentPriceChanged = pyqtSignal()
    refPriceChanged = pyqtSignal()
    diffSignChanged = pyqtSignal()
    diffPriceChanged = pyqtSignal()
    diffRateChanged = pyqtSignal()
    volumeChanged = pyqtSignal()
    volumeRateChanged = pyqtSignal()

    def __init__(self, name: str, code: str, priceInfo: dict):
        super().__init__()
        self._name = name
        self._code = code
        self._startPrice = priceInfo["시가"]
        self._highPrice = priceInfo["고가"]
        self._lowPrice = priceInfo["저가"]
        self._currentPrice = priceInfo["현재가"]
        self._refPrice = priceInfo["기준가"]
        self._diffSign = priceInfo["대비기호"]
        self._diffPrice = priceInfo["전일대비"]
        self._diffRate = priceInfo["등락율"]
        self._volume = priceInfo["거래량"]
        self._volumeRate = priceInfo["거래대비"]

    @pyqtProperty(str, notify=nameChanged)
    def name(self):
        return self._name

    @name.setter
    def name(self, val: str):
        if self._name != val:
            self._name = val
            self.nameChanged.emit()

    @pyqtProperty(str, notify=codeChanged)
    def code(self):
        return self._code

    @code.setter
    def code(self, val: str):
        if self._code != val:
            self._code = val
            self.codeChanged.emit()

    @pyqtProperty(str, notify=startPriceChanged)
    def startPrice(self):
        return self._startPrice

    @startPrice.setter
    def startPrice(self, val: str):
        if self._startPrice != val:
            self._startPrice = val
            self.startPriceChanged.emit()

    @pyqtProperty(str, notify=highPriceChanged)
    def highPrice(self):
        return self._highPrice

    @highPrice.setter
    def highPrice(self, val: str):
        if self._highPrice != val:
            self._highPrice = val
            self.highPriceChanged.emit()

    @pyqtProperty(str, notify=lowPriceChanged)
    def lowPrice(self):
        return self._lowPrice

    @lowPrice.setter
    def lowPrice(self, val: str):
        if self._lowPrice != val:
            self._lowPrice = val
            self.lowPriceChanged.emit()

    @pyqtProperty(str, notify=currentPriceChanged)
    def currentPrice(self):
        return self._currentPrice

    @currentPrice.setter
    def currentPrice(self, val: str):
        if self._currentPrice != val:
            self._currentPrice = val
            self.currentPriceChanged.emit()

    @pyqtProperty(str, notify=refPriceChanged)
    def refPrice(self):
        return self._refPrice

    @refPrice.setter
    def refPrice(self, val: str):
        if self._refPrice != val:
            self._refPrice = val
            self.refPriceChanged.emit()

    @pyqtProperty(str, notify=diffSignChanged)
    def diffSign(self):
        return self._diffSign

    @diffSign.setter
    def diffSign(self, val: str):
        if self._diffSign != val:
            self._diffSign = val
            self.diffSignChanged.emit()

    @pyqtProperty(str, notify=diffPriceChanged)
    def diffPrice(self):
        return self._diffPrice

    @diffPrice.setter
    def diffPrice(self, val: str):
        if self._diffPrice != val:
            self._diffPrice = val
            self.diffPriceChanged.emit()

    @pyqtProperty(str, notify=diffRateChanged)
    def diffRate(self):
        return self._diffRate

    @diffRate.setter
    def diffRate(self, val: str):
        if self._diffRate != val:
            self._diffRate = val
            self.diffRateChanged.emit()

    @pyqtProperty(str, notify=volumeChanged)
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, val: str):
        if self._volume != val:
            self._volume = val
            self.volumeChanged.emit()

    @pyqtProperty(str, notify=volumeRateChanged)
    def volumeRate(self):
        return self._volumeRate

    @volumeRate.setter
    def volumeRate(self, val: str):
        if self._volumeRate != val:
            self._volumeRate = val
            self.volumeRateChanged.emit()

    def __repr__(self):
        str_ = "==StockPriceItemData==\n"
        str_ += f"name: {self._name}\n"
        str_ += f"code: {self._code}\n"
        str_ += f"startPrice: {self._startPrice}\n"
        str_ += f"highPrice: {self._highPrice}\n"
        str_ += f"currentPrice: {self._currentPrice}\n"
        str_ += f"refPrice: {self._refPrice}\n"
        str_ += f"diffSign: {self._diffSign}\n"
        str_ += f"diffPrice: {self._diffPrice}\n"
        str_ += f"diffRate: {self._diffRate}\n"
        str_ += f"volume: {self._volume}\n"
        str_ += f"volumeRate: {self._volumeRate}\n"

        return str_
