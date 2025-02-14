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
        self.chart = None

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
        filtered_data = [{key: d[key] for key in ["일자", "시가", "고가", "저가", "현재가"]} for d in result]
        df = pd.DataFrame(filtered_data)
        logger.debug(f"df:{df}")
        df.rename(
            columns={"일자": "time", "시가": "open",
                     "고가": "high", "저가": "low", "현재가": "close"},
            inplace=True
        )
        df["time"] = pd.to_datetime(df["time"], format="%Y%m%d").dt.strftime("%Y-%m-%d")
        df["open"] = df["open"].astype(int)
        df["high"] = df["high"].astype(int)
        df["low"] = df["low"].astype(int)
        df["close"] = df["close"].astype(int)
        df = df.sort_values("time")
        # logger.debug(f"df:{df}")
        if self.chart is None:
            self.chart = Chart()

        self.chart.set(df)
        self.chart.show()

    @pyqtSlot(str, str)
    def setStock(self, name, code):
        if self.chart is None:
            return
        self.load(code)

    """
    client model event
    """

    """
    private method
    """
