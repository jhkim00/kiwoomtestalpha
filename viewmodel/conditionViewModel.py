import logging

from PyQt5.QtCore import QObject, pyqtSlot, pyqtProperty, pyqtSignal, QVariant

from client import Client

logger = logging.getLogger()

class ConditionViewModel(QObject):
    conditionListChanged = pyqtSignal()

    def __init__(self, qmlContext, parent=None):
        super().__init__(parent)
        self.qmlContext = qmlContext
        self.qmlContext.setContextProperty('conditionViewModel', self)

        self._conditionList = []

        Client.getInstance().registerEventCallback("condition_load", self.onConditionList)

    @pyqtProperty(list, notify=conditionListChanged)
    def conditionList(self):
        return self._conditionList

    @conditionList.setter
    def conditionList(self, val):
        if self._conditionList != val:
            self._conditionList = val
            self.conditionListChanged.emit()

    """
    method for qml side
    """
    @pyqtSlot()
    def load(self):
        logger.debug("")
        Client.getInstance().condition_load()

    """
    client model event
    """
    def onConditionList(self, result: list):
        logger.debug(f"result:{result}")
        self.conditionList = [{'code': x[0], 'name': x[1]} for x in result]
        logger.debug(f"self.conditionList:{self.conditionList}")
