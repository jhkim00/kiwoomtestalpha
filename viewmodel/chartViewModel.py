import logging
from lightweight_charts import Chart
import pandas as pd
from datetime import datetime
from PyQt5.QtCore import QObject, pyqtSlot, pyqtProperty, pyqtSignal, QVariant

from client import Client

logger = logging.getLogger()

class ChartViewModel(QObject):
    dailyChartModelChanged = pyqtSignal()
    stockPriceRealReceived = pyqtSignal(tuple)

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

        self.mChart = None
        self.mDf = None

        Client.getInstance().registerRealDataCallback("stock_price_real", self.__onStockPriceReal)

        self.stockPriceRealReceived.connect(self.__onStockPriceRealReceived)

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
            self.chart = Chart(width=1920, height=1080, x=0, y=0, title='Chart', toolbox=True, inner_height=0.5)

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
        self.loadMinuteChart()

        self.chart.show()

    @pyqtSlot()
    def loadMinuteChart(self):
        logger.debug("")
        if len(self.stockCode) == 0:
            return

        result = Client.getInstance().minute_chart(self.stockCode, 1, "1005")
        logger.debug(f"{result}")
        filtered_data = [{key: d[key] for key in ['현재가', '거래량', '체결시간', '시가', '고가', '저가']} for d in result]
        df = pd.DataFrame(filtered_data)
        logger.debug(f"df:{df}")
        df.rename(
            columns={"체결시간": "time", "시가": "open", "고가": "high", "저가": "low", "현재가": "close", "거래량": "volume"},
            inplace=True
        )
        df["time"] = pd.to_datetime(df["time"], format="%Y%m%d%H%M%S").dt.strftime("%Y-%m-%d %H:%M")
        df["open"] = abs(df["open"].astype(int))
        df["high"] = abs(df["high"].astype(int))
        df["low"] = abs(df["low"].astype(int))
        df["close"] = abs(df["close"].astype(int))
        df["volume"] = df["volume"].astype(int)
        df = df.sort_values("time")
        # logger.debug(f"df:{df}")
        if self.mChart is None:
            self.mChart = self.chart.create_subchart(position='bottom', width=1, height=0.5)

        self.mChart.set(df)
        self.mDf = df

    @pyqtSlot(str, str)
    def setStock(self, name, code):
        self.stockCode = code
        if self.chart:
            self.load()

    """
    client model event
    """

    @pyqtSlot(tuple)
    def __onStockPriceReal(self, data):
        # logger.debug(f"data:{data}")
        self.stockPriceRealReceived.emit(data)

    """
    private method
    """
    @classmethod
    def __calculate_sma(cls, df, period: int = 50):
        return pd.DataFrame({
            'time': df['time'],
            f'SMA {period}': df['close'].rolling(window=period).mean()
        }).dropna()

    @pyqtSlot(tuple)
    def __onStockPriceRealReceived(self, data):
        # logger.debug(f"data:{data}")
        if self.df:
            if data[0] == self.stockCode:
                tick = pd.Series(
                    {
                        'time': self.df.iloc[-1]['time'],
                        'price': abs(int(data[1]['10'])),
                        'volume': abs(int(data[1]['13'])),
                    }
                )

                # logger.debug(f"tick:{self.df.iloc[-1]}")
                self.chart.update_from_tick(tick)

        if self.mDf is not None:
            if data[0] == self.stockCode:

                dateStr = datetime.strptime(self.mDf.iloc[-1]['time'], "%Y-%m-%d %H:%M").strftime("%Y-%m-%d")
                timeStr = datetime.strptime(data[1]['20'], "%H%M%S").strftime("%H:%M")
                tick = pd.Series(
                    {
                        'time': f"{dateStr} {timeStr}",
                        'price': abs(int(data[1]['10'])),
                        'volume': abs(int(data[1]['15'])),
                    }
                )
                self.mChart.update_from_tick(tick, cumulative_volume=True)