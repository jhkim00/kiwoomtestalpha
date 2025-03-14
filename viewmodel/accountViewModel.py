import logging

from PyQt5.QtCore import QObject, pyqtSlot, pyqtProperty, pyqtSignal, QVariant, QModelIndex
from client import Client
from .accountStockInfoModel import AccountStockInfoModel
from .michegyeolOrderModel import MichegyeolOrderModel

logger = logging.getLogger()

class AccountViewModel(QObject):
    accountListChanged = pyqtSignal()
    currentAccountChanged = pyqtSignal(str)
    currentAccountInfoChanged = pyqtSignal()
    currentAccountStockInfoChanged = pyqtSignal()
    currentMichegyeolOrderModelChanged = pyqtSignal()
    michegyeolInfoReceived = pyqtSignal(list)
    orderChegyeolDataReceived = pyqtSignal(dict)

    def __init__(self, marketViewModel, qmlContext, parent=None):
        super().__init__(parent)
        self.qmlContext = qmlContext
        self.qmlContext.setContextProperty('accountViewModel', self)

        self._accountList = []
        self._currentAccount = ""
        self._currentAccountInfo = []
        self._currentAccountStockInfo = AccountStockInfoModel()
        self._currentMichegyeolOrderModel = MichegyeolOrderModel()
        self._orderList = []

        self.marketViewModel = marketViewModel

        Client.getInstance().registerEventCallback("account_info", self.onAccountInfo)
        Client.getInstance().registerEventCallback("michegyeol_info", self.onMichegyeolInfo)
        Client.getInstance().registerChejanDataCallback("주문체결", self.__onOrderChegyeolData)
        Client.getInstance().registerChejanDataCallback("잔고", self.__onChejanData)

        marketViewModel.loadCompleted.connect(self.__onMarketViewModelLoadCompleted)
        self.michegyeolInfoReceived.connect(self.__onMichegyeolInfo)
        self.orderChegyeolDataReceived.connect(self.__onOrderChegyeolDataReceived)

    @pyqtProperty(list, notify=accountListChanged)
    def accountList(self):
        return self._accountList

    @accountList.setter
    def accountList(self, val: list):
        self._accountList = val
        self.accountListChanged.emit()

    @pyqtProperty(str, notify=currentAccountChanged)
    def currentAccount(self):
        return self._currentAccount

    @currentAccount.setter
    def currentAccount(self, val: str):
        if self._currentAccount != val:
            logger.debug(f"currentAccount changed: {val}")
            self._currentAccount = val
            self.currentAccountChanged.emit(val)

            self.account_info()
            self.michegyeol_info()

    @pyqtProperty(list, notify=currentAccountInfoChanged)
    def currentAccountInfo(self):
        return self._currentAccountInfo

    @currentAccountInfo.setter
    def currentAccountInfo(self, val: list):
        if self._currentAccountInfo != val:
            logger.debug(f"currentAccountInfo changed: {val}")
            self._currentAccountInfo = val
            self.currentAccountInfoChanged.emit()

    @pyqtProperty(AccountStockInfoModel, notify=currentAccountStockInfoChanged)
    def currentAccountStockInfo(self):
        return self._currentAccountStockInfo

    @currentAccountStockInfo.setter
    def currentAccountStockInfo(self, val: AccountStockInfoModel):
        if self._currentAccountStockInfo != val:
            logger.debug(f"currentAccountStockInfo changed: {val}")
            self._currentAccountStockInfo = val
            self.currentAccountStockInfoChanged.emit()

    @pyqtProperty(MichegyeolOrderModel, notify=currentMichegyeolOrderModelChanged)
    def currentMichegyeolOrderModel(self):
        return self._currentMichegyeolOrderModel

    @currentMichegyeolOrderModel.setter
    def currentMichegyeolOrderModel(self, val):
        if self._currentMichegyeolOrderModel != val:
            logger.debug(f"currentMichegyeolOrderModel changed: {val}")
            self._currentMichegyeolOrderModel = val
            self.currentMichegyeolOrderModelChanged.emit()

    @pyqtProperty(list)
    def currentAccountInfoKeys(self):
        return ["계좌명", "예수금", "D+2추정예수금", "유가잔고평가액", "예탁자산평가액", "총매입금액", "추정예탁자산"]

    @pyqtProperty(list)
    def currentAccountStockInfoKeys(self):
        return ['종목명', '현재가', '평균단가', '손익율', '손익금액', '보유수량', '평가금액']

    """
    method for qml side
    """
    @pyqtSlot()
    def login_info(self):
        logger.debug("")
        self.accountList = Client.getInstance().login_info()
        if len(self.accountList) > 0:
            self.currentAccount = self.accountList[0]

    @pyqtSlot()
    def account_info(self):
        logger.debug("")
        Client.getInstance().account_info(self.currentAccount, "1001")

    @pyqtSlot()
    def michegyeol_info(self):
        logger.debug("")
        Client.getInstance().michegyeol_info(self.currentAccount, "1001")

    """
    client model event
    """
    def onAccountInfo(self, result):
        if len(result) > 0:
            self.currentAccountInfo = [[key, result[0][key]] for key in self.currentAccountInfoKeys if key in result[0]]
            logger.debug(self.currentAccountInfo)

        temp_list = []
        for i in range(len(result[1])):
            temp_list.append({key: result[1][i][key] for key in self.currentAccountStockInfoKeys if key in result[1][i]})

        self.currentAccountStockInfo = AccountStockInfoModel(temp_list)

    def onMichegyeolInfo(self, result: list):
        logger.debug(f'{result}')
        self.michegyeolInfoReceived.emit(result)

    def __onOrderChegyeolData(self, data: dict):
        # logger.debug(f'{data}')
        self.orderChegyeolDataReceived.emit(data)

    def __onChejanData(self, data: dict):
        logger.debug(f'{data}')

    """
    private method
    """
    @pyqtSlot()
    def __onMarketViewModelLoadCompleted(self):
        logger.debug("")
        self.login_info()

    @pyqtSlot(list)
    def __onMichegyeolInfo(self, result: list):
        logger.debug(f'{result}')
        temp_list = []
        for i in range(len(result)):
            temp_list.append({key: result[i][key] for key in MichegyeolOrderModel.keys if key in result[i]})

        self.currentMichegyeolOrderModel = MichegyeolOrderModel(temp_list)

    @pyqtSlot(dict)
    def __onOrderChegyeolDataReceived(self, data: dict):
        logger.debug(f'{data}')
        if data['계좌번호'] == self._currentAccount:
            for i in range(len(self._currentMichegyeolOrderModel._data)):
                order = self._currentMichegyeolOrderModel._data[i]
                if order['주문번호'] == data['주문번호']:
                    if data['미체결수량'] == '0':
                        logger.debug('111111111111111')
                        self._currentMichegyeolOrderModel.removeOrder(i, order)
                    else:
                        logger.debug('222222222222222')
                        self._currentMichegyeolOrderModel.updateOrder(
                            i,
                            {
                                '종목명': data['종목명'],
                                '종목코드': data['종목코드_업종코드'][1:],
                                '주문번호': data['주문번호'],
                                '매매구분': data['매매구분'],
                                '주문수량': data['주문수량'],
                                '주문가격': data['주문가격'],
                                '주문구분': data['주문구분'],
                                '미체결수량': data['미체결수량']
                            }
                        )
                    return

            logger.debug('33333333333333')
            self._currentMichegyeolOrderModel.appendOrder({
                '종목명': data['종목명'],
                '종목코드': data['종목코드_업종코드'][1:],
                '주문번호': data['주문번호'],
                '매매구분': data['매매구분'],
                '주문수량': data['주문수량'],
                '주문가격': data['주문가격'],
                '주문구분': data['주문구분'],
                '미체결수량': data['미체결수량']
            })
