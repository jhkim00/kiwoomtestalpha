import logging

from PyQt5.QtCore import QObject, pyqtSlot, pyqtProperty, pyqtSignal, QVariant, Qt, QAbstractListModel, QModelIndex

logger = logging.getLogger()

class CandleStickModel(QAbstractListModel):
    DateRole, OpenRole, HighRole, LowRole, CloseRole = range(Qt.UserRole, Qt.UserRole + 5)

    def __init__(self, data=None, parent=None):
        super().__init__(parent)
        self._data = data or []

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or index.row() >= len(self._data):
            return QVariant()

        item = self._data[index.row()]
        if role == self.DateRole:
            return int(item['일자'])
        elif role == self.OpenRole:
            return float(item['시가'])
        elif role == self.HighRole:
            return float(item['고가'])
        elif role == self.LowRole:
            return float(item['저가'])
        elif role == self.CloseRole:
            return float(item['현재가'])
        return QVariant()

    def roleNames(self):
        return {
            self.DateRole: b"date",
            self.OpenRole: b"open",
            self.HighRole: b"high",
            self.LowRole: b"low",
            self.CloseRole: b"close"
        }
