import logging

from PyQt5.QtCore import QObject, pyqtSlot, pyqtProperty, pyqtSignal, QVariant, Qt, QAbstractListModel, QModelIndex, QThread

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
            # logger.debug(f'{item}')
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

class LogWorker(QThread):
    def __init__(self, queue):
        super().__init__()
        logger.debug("")
        self.queue = queue

    def run(self):
        while True:
            # logger.debug(f".")
            fileName, log = self.queue.get()
            logger.debug(f"{fileName}: {log}")
            if fileName == "finish":
                logger.debug(f"finish received")
                break
            with open(fileName, "a", encoding="utf-8") as f:
                f.write(log)

class LogViewModel(QObject):
    instance = None
    logModelChanged = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._logModel = LogModel()
        self._logWorker = None
        self.queue = None

    @classmethod
    def getInstance(cls):
        if cls.instance is None:
            cls.instance = LogViewModel()
        return cls.instance

    @pyqtProperty(LogModel, notify=logModelChanged)
    def logModel(self):
        return self._logModel

    @logModel.setter
    def logModel(self, val):
        if self._logModel != val:
            self._logModel = val
            self.logModelChanged.emit()

    """
    method for qml side
    """
    @pyqtSlot(str)
    def log(self, log):
        logger.debug(f'{log}')
        self._logModel.addItem(log)

    @pyqtSlot(str, str)
    def logToFile(self, log, fileName):
        if self._logWorker is None:
            self._logWorker = LogWorker(self.queue)
            self._logWorker.start()

        self.queue.put((fileName, log))
