import logging

from PyQt5.QtCore import QObject, pyqtSlot, pyqtProperty, pyqtSignal, QVariant

from client import Client

logger = logging.getLogger()

class MainViewModel(QObject):
    loginResultSignal = pyqtSignal(bool)
    login_completedChanged = pyqtSignal()

    def __init__(self, qmlContext, parent=None):
        super().__init__(parent)
        self.qmlContext = qmlContext
        self.qmlContext.setContextProperty('mainViewModel', self)

        self._login_completed = False

        self.loginResultSignal.connect(self.__loginResult)

        Client.getInstance().registerEventCallback("login", self.onLoginResult)

    @pyqtProperty(bool, notify=login_completedChanged)
    def login_completed(self):
        return self._login_completed

    @login_completed.setter
    def login_completed(self, val):
        if self._login_completed != val:
            self._login_completed = val
            self.login_completedChanged.emit()

    """
    method for qml side
    """
    @pyqtSlot()
    def login(self):
        logger.debug("")
        Client.getInstance().login()

    """
    client model event
    """
    def onLoginResult(self, result):
        logger.debug(f"result:{result}")
        self.loginResultSignal.emit(result)
        Client.getInstance().condition_load()

    def __loginResult(self, result):
        self.login_completed = result
