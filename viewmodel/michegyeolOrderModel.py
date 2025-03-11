import logging

from PyQt5.QtCore import QAbstractListModel, Qt, QVariant

logger = logging.getLogger()

class MichegyeolOrderModel(QAbstractListModel):
    StockNameRole = Qt.UserRole + 1
    OrderNumberRole = Qt.UserRole + 2
    GubunRole = Qt.UserRole + 3
    OrderQuantityRole = Qt.UserRole + 4
    OrderPriceRole = Qt.UserRole + 5
    OrderTypeRole = Qt.UserRole + 6
    MichegyeolQuantityRole = Qt.UserRole + 7

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
        if role == self.StockNameRole:
            return item["종목명"]
        elif role == self.OrderNumberRole:
            return item["주문번호"]
        elif role == self.GubunRole:
            return item["매매구분"]
        elif role == self.OrderQuantityRole:
            return item["주문수량"]
        elif role == self.OrderPriceRole:
            return item["주문가격"]
        elif role == self.OrderTypeRole:
            return item["주문구분"]
        elif role == self.MichegyeolQuantityRole:
            return item["미체결수량"]

        return QVariant()

    def roleNames(self):
        return {
            self.StockNameRole: b"stockName",
            self.OrderNumberRole: b"orderNumber",
            self.GubunRole: b"gubun",
            self.OrderQuantityRole: b"orderQuantity",
            self.OrderPriceRole: b"orderPrice",
            self.OrderTypeRole: b"orderType",
            self.MichegyeolQuantityRole: b"michegyeolQuantity"
        }
