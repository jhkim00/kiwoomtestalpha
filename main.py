import sys
import logging
import time
import multiprocessing
from multiprocessing import Process, Queue

from PyQt5.QtCore import QUrl, QObject, pyqtSlot
from PyQt5.QtWidgets import *
from PyQt5.QtQml import QQmlApplicationEngine
from PyQt5.QtCore import QCoreApplication

from model import Server
from client import Client

from viewmodel import MainViewModel, AccountViewModel

logger = logging.getLogger()
requestQueue = multiprocessing.Queue()
responseQueue = multiprocessing.Queue()
eventQueue = multiprocessing.Queue()

def _handleQmlWarnings(warnings):
    for warning in warnings:
        print("QML Warning:", warning.toString())

g_isLogin = False
def handleLoginEvent(*param):
    logger.debug("")
    global g_isLogin
    g_isLogin = True

def __onExit():
    logger.debug("")
    requestQueue.put(("finish",))

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
    server = Server(requestQueue, responseQueue, eventQueue)
    server.start()

    client = Client().getInstance()
    client.init(requestQueue, responseQueue, eventQueue)
    # client.login(handleLoginEvent)
    #
    # while not g_isLogin:
    #     logger.debug('waiting login')
    #     time.sleep(1)
    #
    # result = client.login_info()
    # logger.debug(f"typeof result: {type(result)}")
    # logger.debug(f"result: {result}")
    # accountList = result
    #
    # result = client.account_info(accountList[0], "1000")
    # logger.debug(f"typeof result: {type(result)}")
    # logger.debug(f"result: {result}")
    #
    # result = client.stock_list()
    # logger.debug(f"typeof result: {type(result)}")
    # logger.debug(f"result: {result}")
    #
    # result = client.stock_basic_info("000250", "1000")
    # logger.debug(f"typeof result: {type(result)}")
    # logger.debug(f"result: {result}")
    #
    # requestQueue.put(("finish",))

    # """
    # GUI start
    # """
    engine = QQmlApplicationEngine()
    engine.warnings.connect(_handleQmlWarnings)

    mainViewModel = MainViewModel(engine.rootContext(), app)
    accountViewModel = AccountViewModel(engine.rootContext(), app)
    # marketViewModel = MarketViewModel(engine.rootContext(), app)

    engine.load(QUrl.fromLocalFile("qml/Main.qml"))

    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec_())
