import sys
import logging
import time
import multiprocessing

from PyQt5.QtCore import QUrl, QT_VERSION_STR
from PyQt5.QtWidgets import *
from PyQt5.QtQml import QQmlApplicationEngine
from PyQt5.QtCore import QCoreApplication, Qt

QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)

from model import Server
from client import Client

from viewmodel import (MainViewModel, AccountViewModel, MarketViewModel, FavoriteStockViewModel, ConditionViewModel,
                       ChartViewModel, TradeViewModel, LogViewModel, HogaViewModel, ChegyeolViewModel, MonitoringStockViewModel)

logger = logging.getLogger()
requestQueue = multiprocessing.Queue(maxsize=5)
responseQueue = multiprocessing.Queue()
eventQueue = multiprocessing.Queue()
realDataQueue = multiprocessing.Queue()
chejanDataQueue = multiprocessing.Queue()
logQueue = multiprocessing.Queue()

def _handleQmlWarnings(warnings):
    for warning in warnings:
        print("QML Warning:", warning.toString())

def __onExit():
    logger.debug("")
    requestQueue.put(("finish",))
    eventQueue.put(("finish", ""))
    realDataQueue.put(("finish", ""))
    chejanDataQueue.put(("finish", ""))
    logQueue.put(("finish", ""))

if __name__ == "__main__":
    logger.setLevel(logging.DEBUG)
    logger.propagate = 0
    formatter = logging.Formatter('[%(asctime)s][%(levelname)s][%(thread)d][%(filename)s:%(funcName)s:%(lineno)d]'
                                  ' %(message)s')
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(formatter)
    logger.addHandler(streamHandler)

    logger.debug(f"Qt version:{QT_VERSION_STR}")

    app = QApplication(sys.argv)
    app.aboutToQuit.connect(__onExit)
    server = Server(requestQueue, responseQueue, eventQueue, realDataQueue, chejanDataQueue)
    server.start()

    client = Client().getInstance()
    client.init(requestQueue, responseQueue, eventQueue, realDataQueue, chejanDataQueue)

    # """
    # GUI start
    # """
    engine = QQmlApplicationEngine()
    engine.warnings.connect(_handleQmlWarnings)

    mainViewModel = MainViewModel(engine.rootContext(), app)
    marketViewModel = MarketViewModel(mainViewModel, engine.rootContext(), app)
    accountViewModel = AccountViewModel(marketViewModel, engine.rootContext(), app)
    favoriteStockViewModel = FavoriteStockViewModel(mainViewModel, marketViewModel, engine.rootContext(), app)
    conditionViewModel = ConditionViewModel(marketViewModel, engine.rootContext(), app)
    monitoringStockViewModel = MonitoringStockViewModel(mainViewModel, marketViewModel, engine.rootContext(), app)
    chartViewModel = ChartViewModel(engine.rootContext(), app)
    tradeViewModel = TradeViewModel(engine.rootContext(), app)
    hogaViewModel = HogaViewModel(marketViewModel, engine.rootContext(), app)
    chegyeolViewModel = ChegyeolViewModel(marketViewModel, engine.rootContext(), app)
    logViewModel = LogViewModel.getInstance()
    logViewModel.queue = logQueue
    engine.rootContext().setContextProperty('logViewModel', logViewModel)

    marketViewModel.currentStockChanged.connect(chartViewModel.setStock)
    marketViewModel.currentStockChanged.connect(tradeViewModel.setCurrentStock)
    accountViewModel.currentAccountChanged.connect(tradeViewModel.setCurrentAccount)

    engine.load(QUrl.fromLocalFile("qml/Main.qml"))

    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec_())
