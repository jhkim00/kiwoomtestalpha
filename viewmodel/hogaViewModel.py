import logging

from PyQt5.QtCore import QObject, pyqtSlot, pyqtProperty, pyqtSignal, QVariant

from client import Client
from .marketViewModel import MarketViewModel

logger = logging.getLogger()

class HogaViewModel(QObject):
    askPriceListChanged = pyqtSignal()
    askVolumeListChanged = pyqtSignal()
    askVolumeChangeListChanged = pyqtSignal()
    askVolumeRatioListChanged = pyqtSignal()
    bidPriceListChanged = pyqtSignal()
    bidVolumeListChanged = pyqtSignal()
    bidVolumeChangeListChanged = pyqtSignal()
    bidVolumeRatioListChanged = pyqtSignal()
    totalAskVolumeChanged = pyqtSignal()
    totalBidVolumeChanged = pyqtSignal()
    currentTimeChanged = pyqtSignal()
    hogaReceived = pyqtSignal(dict)
    hogaRemainsRealReceived = pyqtSignal(dict)
    
    def __init__(self, marketViewModel, qmlContext, parent=None):
        super().__init__(parent)
        self.qmlContext = qmlContext
        self.qmlContext.setContextProperty('hogaViewModel', self)

        self._receiveHoga = False

        self._askPriceList = []
        self._askVolumeList = []
        self._askVolumeChangeList = []
        self._askVolumeRatioList = []
        self._bidPriceList = []
        self._bidVolumeList = []
        self._bidVolumeChangeList = []
        self._bidVolumeRatioList = []
        self._totalAskVolume = '0'
        self._totalBidVolume = '0'
        self._currentTime = '00:00:00'

        self.marketViewModel = marketViewModel

        for _ in range(10):
            self._askPriceList.append('0')
            self._askVolumeList.append('0')
            self._askVolumeChangeList.append('0')
            self._bidPriceList.append('0')
            self._bidVolumeList.append('0')
            self._bidVolumeChangeList.append('0')

        Client.getInstance().registerEventCallback("hoga", self.onHoga)
        Client.getInstance().registerRealDataCallback("hoga_remains_real", self.__onHogaRemainsReal)

        self.hogaReceived.connect(self.__onHogaReceived)
        self.hogaRemainsRealReceived.connect(self.__onHogaRemainsRealReceived)

    @pyqtProperty(list, notify=askPriceListChanged)
    def askPriceList(self):
        return self._askPriceList

    @askPriceList.setter
    def askPriceList(self, val: list):
        self._askPriceList = val
        self.askPriceListChanged.emit()

    @pyqtProperty(list, notify=askVolumeListChanged)
    def askVolumeList(self):
        return self._askVolumeList

    @askVolumeList.setter
    def askVolumeList(self, val: list):
        self._askVolumeList = val
        self.askVolumeListChanged.emit()

    @pyqtProperty(list, notify=askVolumeChangeListChanged)
    def askVolumeChangeList(self):
        return self._askVolumeChangeList

    @askVolumeChangeList.setter
    def askVolumeChangeList(self, val: list):
        self._askVolumeChangeList = val
        self.askVolumeChangeListChanged.emit()

    @pyqtProperty(list, notify=askVolumeRatioListChanged)
    def askVolumeRatioList(self):
        return self._askVolumeRatioList

    @askVolumeRatioList.setter
    def askVolumeRatioList(self, val: list):
        self._askVolumeRatioList = val
        self.askVolumeRatioListChanged.emit()

    @pyqtProperty(list, notify=bidPriceListChanged)
    def bidPriceList(self):
        return self._bidPriceList

    @bidPriceList.setter
    def bidPriceList(self, val: list):
        self._bidPriceList = val
        self.bidPriceListChanged.emit()

    @pyqtProperty(list, notify=bidVolumeListChanged)
    def bidVolumeList(self):
        return self._bidVolumeList

    @bidVolumeList.setter
    def bidVolumeList(self, val: list):
        self._bidVolumeList = val
        self.bidVolumeListChanged.emit()

    @pyqtProperty(list, notify=bidVolumeChangeListChanged)
    def bidVolumeChangeList(self):
        return self._bidVolumeChangeList

    @bidVolumeChangeList.setter
    def bidVolumeChangeList(self, val: list):
        self._bidVolumeChangeList = val
        self.bidVolumeChangeListChanged.emit()

    @pyqtProperty(list, notify=bidVolumeRatioListChanged)
    def bidVolumeRatioList(self):
        return self._bidVolumeRatioList

    @bidVolumeRatioList.setter
    def bidVolumeRatioList(self, val: list):
        self._bidVolumeRatioList = val
        self.bidVolumeRatioListChanged.emit()

    @pyqtProperty(str, notify=totalAskVolumeChanged)
    def totalAskVolume(self):
        return self._totalAskVolume

    @totalAskVolume.setter
    def totalAskVolume(self, val: str):
        self._totalAskVolume = val
        self.totalAskVolumeChanged.emit()

    @pyqtProperty(str, notify=totalBidVolumeChanged)
    def totalBidVolume(self):
        return self._totalBidVolume

    @totalBidVolume.setter
    def totalBidVolume(self, val: str):
        self._totalBidVolume = val
        self.totalBidVolumeChanged.emit()

    @pyqtProperty(str, notify=currentTimeChanged)
    def currentTime(self):
        return self._currentTime

    @currentTime.setter
    def currentTime(self, val: str):
        self._currentTime = val
        self.currentTimeChanged.emit()

    """
    method for qml side
    """
    @pyqtSlot()
    def getHoga(self):
        logger.debug("")
        self._receiveHoga = True
        Client.getInstance().get_hoga(self.marketViewModel.currentStock['code'], "1006")

    @pyqtSlot()
    def stopReceivingHoga(self):
        logger.debug("")
        self._receiveHoga = False

    """
    client model event
    """
    def onHoga(self, result: dict):
        # logger.debug(f"result:{result}")
        self.hogaReceived.emit(result)

    def __onHogaRemainsReal(self, data):
        # logger.debug(f"{data}")
        self.hogaRemainsRealReceived.emit(data)

    """
    private method
    """
    @pyqtSlot(dict)
    def __onHogaReceived(self, result: dict):
        askPriceList = []
        askVolumeList = []
        askVolumeIntList = []
        askVolumeChangeList = []
        askVolumeRatioList = []
        bidPriceList = []
        bidVolumeList = []
        bidVolumeIntList = []
        bidVolumeChangeList = []
        bidVolumeRatioList = []
        maxVolume = 0
        for i in range(10, 1, -1):
            key = f"매도{i}차선호가"
            askPriceList.append(result[key])

            key_2 = f"매도{i}우선잔량" if i == 6 else f"매도{i}차선잔량"
            askVolumeList.append(result[key_2])

            key_3 = f"매도{i}차선잔량대비"
            askVolumeChangeList.append(result[key_3])

            key_4 = f"매수{i}우선호가" if i == 6 else f"매수{i}차선호가"
            bidPriceList.append(result[key_4])

            key_5 = f"매수{i}우선잔량" if i == 6 else f"매수{i}차선잔량"
            bidVolumeList.append(result[key_5])

            key_6 = f"매수{i}차선잔량대비"
            bidVolumeChangeList.append(result[key_6])

            askVolumeInt = abs(int(result[key_2]))
            askVolumeIntList.append(askVolumeInt)
            bidVolumeInt = abs(int(result[key_5]))
            bidVolumeIntList.append(bidVolumeInt)
            maxVolume = max(maxVolume, max(askVolumeInt, bidVolumeInt))

        askPriceList.append(result["매도최우선호가"])
        bidPriceList.append(result["매수최우선호가"])
        askVolumeList.append(result["매도최우선잔량"])
        bidVolumeList.append(result["매수최우선잔량"])
        askVolumeChangeList.append(result["매도1차선잔량대비"])
        bidVolumeChangeList.append(result["매수1차선잔량대비"])

        askVolumeInt = abs(int(result["매도최우선잔량"]))
        askVolumeIntList.append(askVolumeInt)
        bidVolumeInt = abs(int(result["매수최우선잔량"]))
        bidVolumeIntList.append(bidVolumeInt)
        maxVolume = max(maxVolume, max(askVolumeInt, bidVolumeInt))

        for i in range(0, 10):
            askVolumeRatio = 0 if maxVolume == 0 else askVolumeIntList[i] / maxVolume
            bidVolumeRatio = 0 if maxVolume == 0 else bidVolumeIntList[i] / maxVolume
            askVolumeRatioList.append(askVolumeRatio)
            bidVolumeRatioList.append(bidVolumeRatio)

        self.askPriceList = askPriceList
        self.askVolumeList = askVolumeList
        self.askVolumeChangeList = askVolumeChangeList
        self.askVolumeRatioList = askVolumeRatioList
        self.bidPriceList = bidPriceList
        self.bidVolumeList = bidVolumeList
        self.bidVolumeChangeList = bidVolumeChangeList
        self.bidVolumeRatioList = bidVolumeRatioList

        self.totalAskVolume = result['총매도잔량']
        self.totalBidVolume = result['총매수잔량']
        timeStr = result['호가잔량기준시간']
        self.currentTime = f"{timeStr[:2]}:{timeStr[2:4]}:{timeStr[4:]}"

    @pyqtSlot(dict)
    def __onHogaRemainsRealReceived(self, data):
        # logger.debug(f"{data}")
        if not self._receiveHoga:
            return
        if self.marketViewModel.currentStock and data['code'] == self.marketViewModel.currentStock['code']:
            askPriceList = []
            askVolumeList = []
            askVolumeIntList = []
            askVolumeChangeList = []
            askVolumeRatioList = []
            bidPriceList = []
            bidVolumeList = []
            bidVolumeIntList = []
            bidVolumeChangeList = []
            bidVolumeRatioList = []
            maxVolume = 0
            for i in range(10, 0, -1):
                key = f"매도호가{i}"
                askPriceList.append(data[key])

                key_2 = f"매도호가수량{i}"
                askVolumeList.append(data[key_2])

                key_3 = f"매도호가직전대비{i}"
                askVolumeChangeList.append(data[key_3])

                key_4 = f"매수호가{i}"
                bidPriceList.append(data[key_4])

                key_5 = f"매수호가수량{i}"
                bidVolumeList.append(data[key_5])

                key_6 = f"매수호가직전대비{i}"
                bidVolumeChangeList.append(data[key_6])

                askVolumeInt = abs(int(data[key_2]))
                askVolumeIntList.append(askVolumeInt)
                bidVolumeInt = abs(int(data[key_5]))
                bidVolumeIntList.append(bidVolumeInt)
                maxVolume = max(maxVolume, max(askVolumeInt, bidVolumeInt))

            for i in range(0, 10):
                askVolumeRatio = 0 if maxVolume == 0 else askVolumeIntList[i] / maxVolume
                bidVolumeRatio = 0 if maxVolume == 0 else bidVolumeIntList[i] / maxVolume
                askVolumeRatioList.append(askVolumeRatio)
                bidVolumeRatioList.append(bidVolumeRatio)

            self.askPriceList = askPriceList
            self.askVolumeList = askVolumeList
            self.askVolumeChangeList = askVolumeChangeList
            self.askVolumeRatioList = askVolumeRatioList
            self.bidPriceList = bidPriceList
            self.bidVolumeList = bidVolumeList
            self.bidVolumeChangeList = bidVolumeChangeList
            self.bidVolumeRatioList = bidVolumeRatioList

            self.totalAskVolume = data['매도호가총잔량']
            self.totalBidVolume = data['매수호가총잔량']
            timeStr = data['호가시간']
            self.currentTime = f"{timeStr[:2]}:{timeStr[2:4]}:{timeStr[4:]}"

            # logger.debug(f"askVolumeList:{self.askVolumeList}")
            # logger.debug(f"bidVolumeList:{self.bidVolumeList}")
