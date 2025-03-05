import logging

from PyQt5.QtCore import QObject, pyqtSlot, pyqtProperty, pyqtSignal, QVariant

from client import Client

logger = logging.getLogger()

class TradeViewModel(QObject):
    orderTypeChanged = pyqtSignal()
    hogaTypeChanged = pyqtSignal()

    def __init__(self, qmlContext, parent=None):
        super().__init__(parent)
        self.qmlContext = qmlContext
        self.qmlContext.setContextProperty('tradeViewModel', self)

        self._currentAccount = ''
        self._currentStockCode = ''
        self._orderType = 1     # 1:신규매수, 2:신규매도 3:매수취소, 4:매도취소, 5:매수정정, 6:매도정정
        self._hogaType = 0      # 00 : 지정가, 03 : 시장가

    @pyqtProperty(int, notify=orderTypeChanged)
    def orderType(self):
        return self._orderType

    @orderType.setter
    def orderType(self, val: int):
        if self._orderType != val:
            self._orderType = val
            self.orderTypeChanged.emit()

    @pyqtProperty(int, notify=hogaTypeChanged)
    def hogaType(self):
        return self._hogaType

    @hogaType.setter
    def hogaType(self, val: int):
        if self._hogaType != val:
            self._hogaType = val
            self.hogaTypeChanged.emit()

    """
    method for qml side
    """
    @pyqtSlot()
    def buy(self):
        logger.debug("")
        Client.getInstance().send_order(
            self._currentAccount,
            order_type=1,
            stock_no=self._currentStockCode,
            quantity=1,
            price=0,
            hoga='03',
            order_no='',
            screen_no="1006"
        )

    @pyqtSlot()
    def sell(self):
        logger.debug("")
        Client.getInstance().send_order(
            self._currentAccount,
            order_type=2,
            stock_no=self._currentStockCode,
            quantity=1,
            price=0,
            hoga='03',
            order_no='',
            screen_no="1006"
        )

    @pyqtSlot(str)
    def setCurrentAccount(self, account):
        self._currentAccount = account

    @pyqtSlot(str, str)
    def setCurrentStock(self, name, code):
        self._currentStockCode = code

    """
    client model event
    """
