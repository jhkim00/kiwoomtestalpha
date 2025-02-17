import logging

from PyQt5.QtCore import QObject, pyqtSlot, pyqtProperty, pyqtSignal, QVariant, Qt, QAbstractListModel, QModelIndex

from client import Client

logger = logging.getLogger()

class LogModel(QAbstractListModel):
    def __init__(self, data=None):
        super().__init__()
        self._data = data or []
        logger.debug(f"data:{data}")

    def rowCount(self, parent=None):
        return len(self._data)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or index.row() >= len(self._data):
            return QVariant()

        item = self._data[index.row()]
        if role == Qt.DisplayRole:
            logger.debug(f'{item}')
            return item

        return QVariant()

    def roleNames(self):
        return {
            Qt.DisplayRole: b"display"
        }

    def addItem(self, item):
        """ 리스트에 아이템을 추가하는 메서드 """
        # self.beginInsertRows(self.createIndex(len(self._data), 0), len(self._data), len(self._data))
        self.beginInsertRows(QModelIndex(), len(self._data), len(self._data))
        self._data.append(item)
        self.endInsertRows()

        logger.debug(f'{self._data}')

class LogViewModel(QObject):
    logModelChanged = pyqtSignal()

    def __init__(self, qmlContext, parent=None):
        super().__init__(parent)
        self.qmlContext = qmlContext
        self.qmlContext.setContextProperty('logViewModel', self)

        self._logModel = LogModel()

    @pyqtProperty(LogModel, notify=logModelChanged)
    def logModel(self):
        return self._logModel

    @logModel.setter
    def logModel(self, val):
        if self._logModel != val:
            self._logModel = val
            self.logModelChanged.emit()

    def appendLog(self, log: str):
        self._logModel.addItem(log)

    """
    method for qml side
    """
    @pyqtSlot(str)
    def log(self, log):
        logger.debug(f'{log}')
        self.appendLog(log)
