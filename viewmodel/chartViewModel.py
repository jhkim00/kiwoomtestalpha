import logging
from lightweight_charts import Chart
import pandas as pd

from PyQt5.QtCore import QObject, pyqtSlot, pyqtProperty, pyqtSignal, QVariant

from client import Client

logger = logging.getLogger()

class ChartViewModel(QObject):
    dailyChartModelChanged = pyqtSignal()

    def __init__(self, qmlContext, parent=None):
        super().__init__(parent)
        self.qmlContext = qmlContext
        self.qmlContext.setContextProperty('chartViewModel', self)

        self.stockCode = ''
        self.chart = None
        self.df = None
        self.line_5 = None
        self.line_20 = None
        self.line_60 = None
        self.line_120 = None

        Client.getInstance().registerRealDataCallback("stock_price_real", self.__onStockPriceReal)

    """
    method for qml side
    """
    @pyqtSlot()
    def load(self):
        logger.debug("")
        if len(self.stockCode) == 0:
            return

        result = Client.getInstance().daily_chart(self.stockCode, "1005")
        filtered_data = [{key: d[key] for key in ["일자", "시가", "고가", "저가", "현재가", "거래량"]} for d in result]
        df = pd.DataFrame(filtered_data)
        logger.debug(f"df:{df}")
        df.rename(
            columns={"일자": "time", "시가": "open", "고가": "high", "저가": "low", "현재가": "close", "거래량": "volume"},
            inplace=True
        )
        df["time"] = pd.to_datetime(df["time"], format="%Y%m%d").dt.strftime("%Y-%m-%d")
        df["open"] = df["open"].astype(int)
        df["high"] = df["high"].astype(int)
        df["low"] = df["low"].astype(int)
        df["close"] = df["close"].astype(int)
        df["volume"] = df["volume"].astype(int)
        df = df.sort_values("time")
        # logger.debug(f"df:{df}")
        if self.chart is None:
            self.chart = Chart()

        self.chart.set(df)

        # if self.line_5 is None:
        #     self.line_5 = self.chart.create_line(name='SMA 5', color='blue')
        # sma_data_5 = self.__calculate_sma(df, period=5)
        # self.line_5.set(sma_data_5)
        #
        # if self.line_20 is None:
        #     self.line_20 = self.chart.create_line(name='SMA 20', color='yellow')
        # sma_data_20 = self.__calculate_sma(df, period=20)
        # self.line_20.set(sma_data_20)
        #
        # if self.line_60 is None:
        #     self.line_60 = self.chart.create_line(name='SMA 60', color='green')
        # sma_data_60 = self.__calculate_sma(df, period=60)
        # self.line_60.set(sma_data_60)
        #
        # if self.line_120 is None:
        #     self.line_120 = self.chart.create_line(name='SMA 120', color='purple')
        # sma_data_120 = self.__calculate_sma(df, period=120)
        # self.line_120.set(sma_data_120)

        self.df = df
        self.chart.show()

    @pyqtSlot(str, str)
    def setStock(self, name, code):
        self.stockCode = code
        if self.chart is None:
            return
        self.load(code)

    """
    client model event
    """

    @pyqtSlot(tuple)
    def __onStockPriceReal(self, data):
        logger.debug(f"data:{data}")
        if self.df is None:
            return
        if data[0] == self.stockCode:
            self.df.iloc[-1, self.df.columns.get_loc('close')] = abs(int(data[1]['10']))
            self.df.iloc[-1, self.df.columns.get_loc('volume')] = abs(int(data[1]['13']))
            self.df.iloc[-1, self.df.columns.get_loc('open')] = abs(int(data[1]['16']))
            self.df.iloc[-1, self.df.columns.get_loc('high')] = abs(int(data[1]['17']))
            self.df.iloc[-1, self.df.columns.get_loc('low')] = abs(int(data[1]['18']))

            logger.debug(f"tick:{self.df.iloc[-1]}")

            # for i, tick in self.df.iterrows():
                # logger.debug(f"tick:{tick}")
                # self.chart.update_from_tick(tick)

    """
    private method
    """
    @classmethod
    def __calculate_sma(cls, df, period: int = 50):
        return pd.DataFrame({
            'time': df['time'],
            f'SMA {period}': df['close'].rolling(window=period).mean()
        }).dropna()
