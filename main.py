import sys
import logging
import time
import multiprocessing

from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import *
from PyQt5.QtQml import QQmlApplicationEngine
from PyQt5.QtCore import QCoreApplication

from model import Server
from client import Client

from viewmodel import (MainViewModel, AccountViewModel, MarketViewModel, FavoriteStockViewModel, ConditionViewModel,
                       ChartViewModel)

logger = logging.getLogger()
requestQueue = multiprocessing.Queue()
responseQueue = multiprocessing.Queue()
eventQueue = multiprocessing.Queue()
realDataQueue = multiprocessing.Queue()

def _handleQmlWarnings(warnings):
    for warning in warnings:
        print("QML Warning:", warning.toString())

def __onExit():
    logger.debug("")
    requestQueue.put(("finish",))
    eventQueue.put(("finish", ""))
    realDataQueue.put(("finish", ""))

if __name__ == "__main__":
    logger.setLevel(logging.DEBUG)
    logger.propagate = 0
    formatter = logging.Formatter('[%(asctime)s][%(levelname)s][%(thread)d][%(filename)s:%(funcName)s:%(lineno)d]'
                                  ' %(message)s')
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(formatter)
    logger.addHandler(streamHandler)

    app = QApplication(sys.argv)
    app.aboutToQuit.connect(__onExit)
    server = Server(requestQueue, responseQueue, eventQueue, realDataQueue)
    server.start()

    client = Client().getInstance()
    client.init(requestQueue, responseQueue, eventQueue, realDataQueue)

    # """
    # GUI start
    # """
    engine = QQmlApplicationEngine()
    engine.warnings.connect(_handleQmlWarnings)

    mainViewModel = MainViewModel(engine.rootContext(), app)
    accountViewModel = AccountViewModel(engine.rootContext(), app)
    marketViewModel = MarketViewModel(engine.rootContext(), app)
    favoriteStockViewModel = FavoriteStockViewModel(engine.rootContext(), app)
    conditionViewModel = ConditionViewModel(engine.rootContext(), app)
    chartViewModel = ChartViewModel(engine.rootContext(), app)

    marketViewModel.currentStockChanged.connect(chartViewModel.setStock)

    engine.load(QUrl.fromLocalFile("qml/Main.qml"))

    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec_())
