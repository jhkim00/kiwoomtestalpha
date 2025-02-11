import logging

from PyQt5.QtCore import QObject, pyqtSlot, pyqtProperty, pyqtSignal, QVariant
from client import Client
from .accountStockInfoModel import AccountStockInfoModel

logger = logging.getLogger()

class AccountViewModel(QObject):
    accountListChanged = pyqtSignal()
    currentAccountChanged = pyqtSignal()
    currentAccountInfoChanged = pyqtSignal()
    currentAccountStockInfoChanged = pyqtSignal()

    def __init__(self, qmlContext, parent=None):
        super().__init__(parent)
        self.qmlContext = qmlContext
        self.qmlContext.setContextProperty('accountViewModel', self)

        self._accountList = []
        self._currentAccount = ""
        self._currentAccountInfo = []
        self._currentAccountStockInfo = AccountStockInfoModel()

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
            self.currentAccountChanged.emit()

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

    @pyqtSlot()
    def account_info(self):
        logger.debug("")
        result = Client.getInstance().account_info(self.currentAccount, "1001")

        if len(result) > 0:
            self.currentAccountInfo = [[key, result[0][key]] for key in self.currentAccountInfoKeys if key in result[0]]
            logger.debug(self.currentAccountInfo)

        temp_list = []
        for i in range(len(result[1])):
            temp_list.append({key: result[1][i][key] for key in self.currentAccountStockInfoKeys if key in result[1][i]})

        self.currentAccountStockInfo = AccountStockInfoModel(temp_list)
