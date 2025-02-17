import logging

from PyQt5.QtCore import QObject, pyqtSlot, pyqtProperty, pyqtSignal, QVariant

from client import Client

logger = logging.getLogger()

class TradeViewModel(QObject):

    def __init__(self, qmlContext, parent=None):
        super().__init__(parent)
        self.qmlContext = qmlContext
        self.qmlContext.setContextProperty('tradeViewModel', self)

        self._currentAccount = ''
        self._currentStockCode = ''

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
