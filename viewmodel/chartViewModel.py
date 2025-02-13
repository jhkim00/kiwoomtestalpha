import logging
from lightweight_charts import Chart
import pandas as pd

from PyQt5.QtCore import QObject, pyqtSlot, pyqtProperty, pyqtSignal, QVariant

from client import Client
from .candleStickModel import CandleStickModel

logger = logging.getLogger()

class ChartViewModel(QObject):
    dailyChartModelChanged = pyqtSignal()

    def __init__(self, qmlContext, parent=None):
        super().__init__(parent)
        self.qmlContext = qmlContext
        self.qmlContext.setContextProperty('chartViewModel', self)

        self._dailyChartModel = CandleStickModel()

    @pyqtProperty(CandleStickModel, notify=dailyChartModelChanged)
    def dailyChartModel(self):
        return self._dailyChartModel

    @dailyChartModel.setter
    def dailyChartModel(self, val):
        if self._dailyChartModel != val:
            self._dailyChartModel = val
            self.dailyChartModelChanged.emit()

    """
    method for qml side
    """
    @pyqtSlot(str)
    def load(self, code):
        logger.debug("")
        result = Client.getInstance().daily_chart(code, "1005")
        # logger.debug(f"result:{result}")
        self._dailyChartModel._data = result
        self.dailyChartModelChanged.emit()

    @pyqtSlot()
    def test(self):
        data = {
            "time": ["2024-02-10", "2024-02-11", "2024-02-12", "2024-02-13", "2024-02-14"],
            "open": [100, 105, 102, 108, 110],
            "high": [110, 112, 107, 115, 118],
            "low": [95, 100, 98, 105, 108],
            "close": [105, 108, 103, 112, 115]
        }
        df = pd.DataFrame(data) # DataFrame 생성

        chart = Chart()
        chart.set(df)
        chart.show()

    """
    client model event
    """

    """
    private method
    """
