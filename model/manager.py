import sys
import logging

from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal
from model.kiwoom import Kiwoom

logger = logging.getLogger()

class Manager(QObject):

    def __init__(self):
        super().__init__()
        self.kw = Kiwoom.getInstance()
        self.kw.loginCompleted.connect(self.onLoginCompleted)

        self.notifyLoginCompleted = None
        self.notifyLoginInfo = None
        self.notifyAccountInfo = None
        self.notifyStockList = None
        self.notifyStockBasicInfo = None

    @pyqtSlot()
    def commConnect(self):
        logger.debug("")
        self.kw.CommConnect()

    @pyqtSlot()
    def getLoginInfo(self):
        logger.debug("")
        data = self.kw.GetLoginInfo("ACCNO")
        logger.debug(data)
        self.notifyLoginInfo(data)

    @pyqtSlot(dict)
    def getAccountInfo(self, data):
        logger.debug("")
        self.kw.trCallbacks["OPW00004"] = self.__onAccountInfo
        self.kw.SetInputValue(id="계좌번호", value=data["account_no"])
        self.kw.SetInputValue(id="비밀번호", value="")
        self.kw.SetInputValue(id="상장폐지조회구분", value="0")
        self.kw.SetInputValue(id="비밀번호입력매체구분", value="00")
        self.kw.CommRqData(rqname="계좌평가현황요청", trcode="OPW00004", next=0, screen=data["screen_no"])

    @pyqtSlot()
    def getStockList(self):
        logger.debug("")
        kospi = self.kw.GetCodeListByMarket("0")
        kosdaq = self.kw.GetCodeListByMarket("10")
        # logger.debug(f"kospi:{kospi}")
        # logger.debug(f"kosdaq:{kosdaq}")
        entire_stock_list = []
        for code in (kospi + kosdaq):
            name = self.kw.GetMasterCodeName(code)
            entire_stock_list.append({'code': code, 'name': name})
        self.notifyStockList(entire_stock_list)

    @pyqtSlot(dict)
    def getStockBasicInfo(self, data):
        logger.debug("")
        self.kw.trCallbacks["opt10001"] = self.__onStockBasicInfo
        self.kw.SetInputValue(id="종목코드", value=data["stock_no"])
        self.kw.CommRqData(rqname="주식기본정보", trcode="opt10001", next=0, screen=data["screen_no"])

    """
    slot for kiwoom
    """
    @pyqtSlot(bool)
    def onLoginCompleted(self, result):
        logger.debug(f"result:{result}")
        self.notifyLoginCompleted(result)

    """
    tr callbacks
    """
    def __onAccountInfo(self, screen, rqname, trcode, record, next):
        logger.debug("")
        if rqname == "계좌평가현황요청":
            single_data_keys = ['계좌명', '예수금', 'D+2추정예수금', '유가잔고평가액', '예탁자산평가액', '총매입금액', '추정예탁자산']
            multi_data_keys = ['종목코드', '종목명', '보유수량', '평균단가', '현재가', '평가금액', '손익금액', '손익율']
            self.notifyAccountInfo(
                self.__getCommDataByKeys(trcode, rqname, single_data_keys, multi_data_keys)
            )

    def __onStockBasicInfo(self, screen, rqname, trcode, record, next):
        logger.debug("")
        if rqname == "주식기본정보":
            single_data_keys = ['신용비율', '시가총액', 'PER', 'PBR', '매출액', '영업이익', '당기순이익', '유통주식', '유통비율',
                '시가', '고가', '저가', '현재가', '기준가', '대비기호', '전일대비', '등락율', '거래량', '거래대비']
            outList = self.__getCommDataByKeys(trcode, rqname, single_data_keys)
            self.notifyStockBasicInfo(outList)

    """
    private method
    """
    def __getCommDataByKeys(self, trcode, rqname, single_data_keys, multi_data_keys=[]):
        logger.debug("")
        cnt = self.kw.GetRepeatCnt(trcode, rqname)
        logger.debug(f"cnt:{cnt}")
        single_data = {}
        multi_data = []
        for key in single_data_keys:
            strData = self.kw.GetCommData(trcode, rqname, 0, key)
            logger.debug(f"{key}:{strData}")
            single_data[key] = strData

        if len(multi_data_keys) > 0:
            cnt = self.kw.GetRepeatCnt(trcode, rqname)
            logger.debug(f"repeat_cnt:{cnt}, len(multi_data_keys):{len(multi_data_keys)}")
            for i in range(cnt):
                outDict = {}
                for key in multi_data_keys:
                    strData = self.kw.GetCommData(trcode, rqname, i, key)
                    logger.debug(f"{key}:{strData}")
                    outDict[key] = strData
                multi_data.append(outDict)
        return single_data, multi_data
