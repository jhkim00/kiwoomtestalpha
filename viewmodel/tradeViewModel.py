import logging

from PyQt5.QtCore import QObject, pyqtSlot, pyqtProperty, pyqtSignal, QVariant

from client import Client

logger = logging.getLogger()

class TradeViewModel(QObject):
    orderTypeChanged = pyqtSignal()
    hogaTypeChanged = pyqtSignal()
    orderPriceChanged = pyqtSignal()
    orderQuantityChanged = pyqtSignal()

    def __init__(self, qmlContext, parent=None):
        super().__init__(parent)
        self.qmlContext = qmlContext
        self.qmlContext.setContextProperty('tradeViewModel', self)

        self._currentAccount = ''
        self._currentStockCode = ''
        self._orderType = 1     # 1:신규매수, 2:신규매도 3:매수취소, 4:매도취소, 5:매수정정, 6:매도정정
        self._hogaType = 0      # 00 : 지정가, 03 : 시장가
        self._orderPrice = 0
        self._orderQuantity = 0

        self._orderList = []

        Client.getInstance().registerChejanDataCallback("주문체결", self.__onOrderChegyeolData)
        Client.getInstance().registerChejanDataCallback("잔고", self.__onChejanData)

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

    @pyqtProperty(int, notify=orderPriceChanged)
    def orderPrice(self):
        return self._orderPrice

    @orderPrice.setter
    def orderPrice(self, val: int):
        if self._orderPrice != val:
            self._orderPrice = val
            self.orderPriceChanged.emit()

    @pyqtProperty(int, notify=orderQuantityChanged)
    def orderQuantity(self):
        return self._orderQuantity

    @orderQuantity.setter
    def orderQuantity(self, val: int):
        if self._orderQuantity != val:
            self._orderQuantity = val
            self.orderQuantityChanged.emit()

    """
    method for qml side
    """
    @pyqtSlot()
    def buyAsMarketPrice(self):
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
    def buy(self):
        logger.debug("")
        Client.getInstance().send_order(
            self._currentAccount,
            order_type=self._orderType,
            stock_no=self._currentStockCode,
            quantity=self._orderQuantity,
            price=self._orderPrice,
            hoga='00' if self._hogaType == 0 else '03',
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
    def __onOrderChegyeolData(self, data: dict):
        logger.debug(f'{data}')
        for order in self._orderList:
            if order['주문번호'] == data['주문번호']:
                self._orderList.remove(order)
                break
        self._orderList.append(data)

    def __onChejanData(self, data: dict):
        logger.debug(f'{data}')
