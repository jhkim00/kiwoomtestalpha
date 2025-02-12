import logging

from PyQt5.QtCore import QAbstractListModel, Qt, QVariant

logger = logging.getLogger()

class AccountStockInfoModel(QAbstractListModel):
    NameRole = Qt.UserRole + 1
    CurrentPriceRole = Qt.UserRole + 2
    BuyPriceRole = Qt.UserRole + 3
    ProfitRateRole = Qt.UserRole + 4
    ProfitRole = Qt.UserRole + 5
    CountRole = Qt.UserRole + 6
    CurrentValueRole = Qt.UserRole + 7

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
        if role == self.NameRole:
            return item["종목명"]
        elif role == self.CurrentPriceRole:
            return item["현재가"]
        elif role == self.BuyPriceRole:
            return item["평균단가"]
        elif role == self.ProfitRateRole:
            return item["손익율"]
        elif role == self.ProfitRole:
            return item["손익금액"]
        elif role == self.CountRole:
            return item["보유수량"]
        elif role == self.CurrentValueRole:
            return item["평가금액"]

        return QVariant()

    def roleNames(self):
        return {
            self.NameRole: b"name",
            self.CurrentPriceRole: b"currentPrice",
            self.BuyPriceRole: b"buyPrice",
            self.ProfitRateRole: b"profitRate",
            self.ProfitRole: b"profit",
            self.CountRole: b"count",
            self.CurrentValueRole: b"currentValue"
        }
