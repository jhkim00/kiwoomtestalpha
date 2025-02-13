import logging

from PyQt5.QtCore import QObject, pyqtSlot, pyqtProperty, pyqtSignal, QVariant

from client import Client
from .stockPriceItemData import StockPriceItemData

logger = logging.getLogger()

class ChartViewModel(QObject):
    dailyChartChanged = pyqtSignal()

    def __init__(self, qmlContext, parent=None):
        super().__init__(parent)
        self.qmlContext = qmlContext
        self.qmlContext.setContextProperty('chartViewModel', self)

    """
    method for qml side
    """
    @pyqtSlot(str)
    def load(self, code):
        logger.debug("")
        result = Client.getInstance().daily_chart(code, "1005")

    """
    client model event
    """

    """
    private method
    """
