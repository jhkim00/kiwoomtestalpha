import logging

import pandas as pd
from datetime import datetime
from PyQt5.QtCore import QObject, pyqtSlot, pyqtProperty, pyqtSignal, QVariant
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView

from lightweight_charts.widgets import QtChart

from client import Client

logger = logging.getLogger()

class ChartViewModel(QObject):
    weeklyChartReceived = pyqtSignal(tuple)
    dailyChartReceived = pyqtSignal(list)
    minuteChartReceived = pyqtSignal(list)
    stockPriceRealReceived = pyqtSignal(tuple)

    def __init__(self, qmlContext, parent=None):
        super().__init__(parent)
        self.qmlContext = qmlContext
        self.qmlContext.setContextProperty('chartViewModel', self)

        self.stockName = ''
        self.stockCode = ''
        self.currentTimeSelection = 'day'

        self.chart = None

        self.window = QMainWindow()
        self.layout = QVBoxLayout()
        self.widget = QWidget()
        self.widget.setLayout(self.layout)
        self.window.resize(1920, 720)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.mChart = [None, None]

        self.df = None
        self.line_5 = None
        self.line_20 = None
        self.line_60 = None
        self.line_120 = None

        self.mDf = [None, None]
        self.currentMinuteChartIndex = 0
        self.currentMinute = 0

        self.loadWholeChart = True
        self.receiving = False
        self.needUpdate = False

        Client.getInstance().registerEventCallback("weekly_chart", self.onWeeklyChart)
        Client.getInstance().registerEventCallback("daily_chart", self.onDailyChart)
        Client.getInstance().registerEventCallback("minute_chart", self.onMinuteChart)
        Client.getInstance().registerRealDataCallback("stock_price_real", self.__onStockPriceReal)

        self.weeklyChartReceived.connect(self.__onWeeklyChartReceived)
        self.dailyChartReceived.connect(self.__onDailyChartReceived)
        self.minuteChartReceived.connect(self.__onMinuteChartReceived)
        self.stockPriceRealReceived.connect(self.__onStockPriceRealReceived)

    """
    method for qml side
    """
    @pyqtSlot()
    def closeChart(self):
        logger.debug("")
        if self.window:
            self.window.close()

    @pyqtSlot()
    def load(self, loadWholeChart=True):
        logger.debug("")
        if len(self.stockCode) == 0:
            return

        self.receiving = True
        self.loadWholeChart = loadWholeChart

        if self.currentTimeSelection == 'week':
            Client.getInstance().weekly_chart(self.stockCode, datetime.today().strftime("%Y%m%d"), "1005")
        elif self.currentTimeSelection == 'day':
            Client.getInstance().daily_chart(self.stockCode, "1005")

    @pyqtSlot()
    def loadMinuteChart(self, minute):
        logger.debug(f"minute:{minute}")
        if len(self.stockCode) == 0:
            return

        if self.chart is None:
            return

        Client.getInstance().minute_chart(self.stockCode, minute, "1005")

    @pyqtSlot(str, str)
    def setStock(self, name, code):
        logger.debug(f"name:{name}, code:{name}, receiving:{self.receiving}, needUpdate:{self.needUpdate}")
        self.stockName = name
        self.stockCode = code
        if not self.window.isVisible():
            return
        if self.receiving:
            self.needUpdate = True
            return
        if self.chart:
            self.load()

    """
    client model event
    """
    def onWeeklyChart(self, result):
        self.weeklyChartReceived.emit(result)

    def onDailyChart(self, result):
        self.dailyChartReceived.emit(result)

    def onMinuteChart(self, result):
        self.minuteChartReceived.emit(result)

    @pyqtSlot(tuple)
    def __onStockPriceReal(self, data):
        # logger.debug(f"data:{data}")
        if not self.window.isVisible():
            return
        self.stockPriceRealReceived.emit(data)

    """
    private method
    """
    def createChart(self):
        logger.debug("")
        if self.chart is None:
            self.chart = QtChart(self.widget, toolbox=True, inner_width=1, inner_height=0.5)
            self.chart.topbar.textbox('symbol')
            self.chart.topbar.switcher('timeframe', ('day', 'week', 'month'), default='day',
                                       func=self.onTimeframeSelection)
            self.chart.candle_style(up_color='#ff0000', down_color='#0000ff')
            self.chart.legend(visible=True)

            for i in range(2):
                chart = self.mChart[i]
                if chart is None:
                    chart = self.chart.create_subchart(position='left', width=0.5, height=0.5)
                    chart.topbar.textbox('symbol')
                    chart.candle_style(up_color='#ff0000', down_color='#0000ff')
                    chart.legend(visible=True)
                    self.mChart[i] = chart

            self.layout.addWidget(self.chart.get_webview())
            self.window.setCentralWidget(self.widget)
            self.window.show()

    @classmethod
    def __calculate_sma(cls, df, period: int = 50):
        return pd.DataFrame({
            'time': df['time'],
            f'SMA {period}': df['close'].rolling(window=period).mean()
        }).dropna()

    def onTimeframeSelection(self, chart):
        logger.debug(f"{chart.topbar['symbol'].value}:{chart.topbar['timeframe'].value}")
        self.currentTimeSelection = chart.topbar['timeframe'].value
        self.load(loadWholeChart=False)

    @pyqtSlot(tuple)
    def __onWeeklyChartReceived(self, data):
        filtered_data = [{key: d[key] for key in ["일자", "시가", "고가", "저가", "현재가", "거래량"]} for d in data[1]]
        df = pd.DataFrame(filtered_data)
        # logger.debug(f"df:{df}")
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

        self.createChart()

        self.chart.topbar['symbol'].set(self.stockName)
        self.chart.set(df)

        self.df = df

        if self.loadWholeChart:
            self.currentMinuteChartIndex = 0
            self.currentMinute = 1
            self.loadMinuteChart(1)
        else:
            self.receiving = False
            if self.needUpdate:
                self.needUpdate = False
                self.load()

    @pyqtSlot(list)
    def __onDailyChartReceived(self, data):
        filtered_data = [{key: d[key] for key in ["일자", "시가", "고가", "저가", "현재가", "거래량"]} for d in data]
        df = pd.DataFrame(filtered_data)
        # logger.debug(f"df:{df}")
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

        self.createChart()

        self.chart.topbar['symbol'].set(self.stockName)
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

        if self.loadWholeChart:
            self.currentMinuteChartIndex = 0
            self.currentMinute = 1
            self.loadMinuteChart(1)

    @pyqtSlot(list)
    def __onMinuteChartReceived(self, data):
        filtered_data = [{key: d[key] for key in ['현재가', '거래량', '체결시간', '시가', '고가', '저가']} for d in data]
        df = pd.DataFrame(filtered_data)
        # logger.debug(f"df:{df}")
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
        i = self.currentMinuteChartIndex
        self.mChart[i].topbar['symbol'].set(f'{self.currentMinute} min')
        self.mChart[i].set(df)
        self.mDf[i] = df

        if self.currentMinuteChartIndex == 0:
            self.currentMinuteChartIndex = 1
            self.currentMinute = 5
            self.loadMinuteChart(5)
        else:
            self.window.show()
            self.receiving = False
            if self.needUpdate:
                self.needUpdate = False
                self.load()

    @pyqtSlot(tuple)
    def __onStockPriceRealReceived(self, data):
        # logger.debug(f"data:{data}")
        if self.receiving:
            return

        if self.currentTimeSelection == 'day' and self.df is not None:
            if data[0] == self.stockCode:
                tick = pd.Series(
                    {
                        'time': self.df.iloc[-1]['time'],
                        'price': abs(int(data[1]['10'])),
                        'volume': abs(int(data[1]['13'])),
                    }
                )

                # print(f"{self.df.iloc[-1]}")
                self.chart.update_from_tick(tick)

        for i in range(0, len(self.mDf)):
            df = self.mDf[i]
            if df is not None:
                if data[0] == self.stockCode:
                    dateStr = datetime.strptime(df.iloc[-1]['time'], "%Y-%m-%d %H:%M").strftime("%Y-%m-%d")
                    timeStr = datetime.strptime(data[1]['20'], "%H%M%S").strftime("%H:%M")
                    tick = pd.Series(
                        {
                            'time': f"{dateStr} {timeStr}",
                            'price': abs(int(data[1]['10'])),
                            'volume': abs(int(data[1]['15'])),
                        }
                    )
                    self.mChart[i].update_from_tick(tick, cumulative_volume=True)
