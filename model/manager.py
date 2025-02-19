import sys
import logging

from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal
from model.kiwoom import Kiwoom
from .coolDown import CoolDown

logger = logging.getLogger()

class Manager(QObject):

    def __init__(self):
        super().__init__()
        self.kw = Kiwoom.getInstance()
        self.kw.loginCompleted.connect(self.onLoginCompleted)

        self.kw.trCallbacks["opt10001"] = self.__onStockBasicInfo
        self.kw.trCallbacks["OPW00004"] = self.__onAccountInfo
        self.kw.trCallbacks["OPTKWFID"] = self.__onStocksInfo
        self.kw.trCallbacks["opt10081"] = self.__onDailyChart
        self.kw.trCallbacks["opt10080"] = self.__onMinuteChart
        self.kw.realDataCallbacks["주식체결"] = self.__onStockPriceReal
        self.kw.conditionVerCallback = self.__onReceiveConditionVer
        self.kw.trConditionCallback = self.__onReceiveTrCondition
        self.kw.realConditionCallback = self.__onReceiveRealCondition

        self.notifyLoginCompleted = None
        self.notifyLoginInfo = None
        self.notifyAccountInfo = None
        self.notifyStockList = None
        self.notifyStockBasicInfo = None
        self.notifyStockPriceReal = None
        self.notifyConditionList = None
        self.notifyStocksInfo = None
        self.notifyConditionInfo = None
        self.notifyDailyChart = None
        self.notifyMinuteChart = None
        self.notifyConditionInfoReal = None

        self.stock_price_real_data_fid_list = ['20', '10', '11', '12', '13', '14', '15', '16', '17', '18', '25', '30']

        self.coolDown = CoolDown(limit=5)

    async def commConnect(self):
        logger.debug("")
        self.kw.CommConnect()

    async def getLoginInfo(self):
        logger.debug("")
        data = self.kw.GetLoginInfo("ACCNO")
        logger.debug(data)
        self.notifyLoginInfo(data)

    async def getAccountInfo(self, data: dict):
        logger.debug("")
        self.kw.SetInputValue(id="계좌번호", value=data["account_no"])
        self.kw.SetInputValue(id="비밀번호", value="")
        self.kw.SetInputValue(id="상장폐지조회구분", value="0")
        self.kw.SetInputValue(id="비밀번호입력매체구분", value="00")
        await self.coolDown.call()
        self.kw.CommRqData(rqname="계좌평가현황요청", trcode="OPW00004", next=0, screen=data["screen_no"])

    async def getStockList(self):
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

    async def getStockBasicInfo(self, data: dict):
        logger.debug("")
        self.kw.SetInputValue(id="종목코드", value=data["stock_no"])
        await self.coolDown.call()
        self.kw.CommRqData(rqname="주식기본정보", trcode="opt10001", next=0, screen=data["screen_no"])

    async def getStockPriceRealData(self, data: dict):
        logger.debug("")
        self.kw.SetRealReg(
            screen=data["screen_no"],
            code_list=data["code_list"],
            fid_list=self.stock_price_real_data_fid_list,
            opt_type=data["opt_type"]
        )

    async def getStocksInfo(self, data: dict):
        logger.debug("")
        await self.coolDown.call()
        self.kw.CommKwRqData(
            arr_code=";".join(data["code_list"]),
            next=0,
            code_count=len(data["code_list"]),
            type=0,
            rqname="복수종목정보요청",
            screen=data["screen_no"]
        )

    async def getConditionLoad(self):
        logger.debug("")
        self.kw.GetConditionLoad()

    async def sendCondition(self, data):
        logger.debug("")
        await self.coolDown.call()
        self.kw.SendCondition(
            screen=data["screen_no"],
            cond_name=data["name"],
            cond_index=data["code"],
            search=1
        )

    async def sendConditionStop(self, data):
        logger.debug("")
        await self.coolDown.call()
        self.kw.SendConditionStop(
            screen=data["screen_no"],
            cond_name=data["name"],
            cond_index=data["code"]
        )

    async def getDailyChart(self, data):
        logger.debug("")
        self.kw.SetInputValue(id="종목코드", value=data["stock_no"])
        await self.coolDown.call()
        self.kw.CommRqData(rqname="주식일봉차트", trcode="opt10081", next=0, screen=data["screen_no"])

    async def getMinuteChart(self, data):
        logger.debug("")
        self.kw.SetInputValue(id="종목코드", value=data["stock_no"])
        self.kw.SetInputValue(id="틱범위", value=data["tick_range"])
        await self.coolDown.call()
        self.kw.CommRqData(rqname="주식분봉차트", trcode="opt10080", next=0, screen=data["screen_no"])

    async def sendOrder(self, data):
        logger.debug(f"{data}")
        await self.coolDown.call()
        self.kw.SendOrder(
            rqname="주식주문",
            screen=data["screen_no"],
            accno=data["account_no"],
            order_type=data["order_type"],
            code=data["stock_no"],
            quantity=data["quantity"],
            price=data["price"],
            hoga=data["hoga"],
            order_no=data["order_no"]
        )

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
            outList, _ = self.__getCommDataByKeys(trcode, rqname, single_data_keys)
            self.notifyStockBasicInfo(outList)

    def __onStocksInfo(self, screen, rqname, trcode, record, next):
        logger.debug(f"screen:{screen}, rqname:{rqname}, trcode:{trcode}")
        if rqname == "복수종목정보요청":
            single_data_keys = []
            multi_data_keys = ['종목명', '종목코드', '시가', '고가', '저가', '현재가', '기준가', '전일대비기호', '전일대비', '등락율',
                               '거래량', '전일거래량대비', '거래대금']
            _, outList = self.__getCommDataByKeys(trcode, rqname, single_data_keys, multi_data_keys)

            # logger.debug(f"outList{outList}")
            self.notifyStocksInfo(outList)

    def __onDailyChart(self, screen, rqname, trcode, record, next):
        logger.debug(f"screen:{screen}, rqname:{rqname}, trcode:{trcode}")
        if rqname == "주식일봉차트":
            single_data_keys = []
            multi_data_keys = ['종목코드', '현재가', '거래량', '거래대금', '일자', '시가', '고가', '저가', '수정주가구분', '수정비율', '대업종구분',
                       '소업종구분', '종목정보', '수정주가이벤트', '전일종가']
            _, outList = self.__getCommDataByKeys(trcode, rqname, single_data_keys, multi_data_keys)

            self.notifyDailyChart(outList)

    def __onMinuteChart(self, screen, rqname, trcode, record, next):
        logger.debug(f"screen:{screen}, rqname:{rqname}, trcode:{trcode}")
        if rqname == "주식분봉차트":
            single_data_keys = []
            multi_data_keys = ['현재가', '거래량', '체결시간', '시가', '고가', '저가']
            _, outList = self.__getCommDataByKeys(trcode, rqname, single_data_keys, multi_data_keys)

            self.notifyMinuteChart(outList)

    """
    real data callbacks
    """
    def __onStockPriceReal(self, code, rtype, data):
        # logger.debug("")
        data = {}
        for fid in self.stock_price_real_data_fid_list:
            val = self.kw.GetCommRealData(code, int(fid))
            data[fid] = val
        self.notifyStockPriceReal((code, data))

    """
    etc callbacks
    """
    def __onReceiveConditionVer(self, ret, msg):
        logger.debug(f"ret:{ret}, msg:{msg}")
        if ret == 1:
            result = self.kw.GetConditionNameList()
            # logger.debug(f"result:{result}")
            self.notifyConditionList(result)

    def __onReceiveTrCondition(self, screen_no, code_list, cond_name, cond_index, next):
        logger.debug(f"screen:{screen_no}, code_list:{code_list}, cond_name:{cond_name}, cond_index:{cond_index}, next:{next}")
        self.notifyConditionInfo(
            {"code_list": code_list.strip(";").split(";"), "cond_name": cond_name, "cond_index": cond_index}
        )

    def __onReceiveRealCondition(self, code: str, id_type: str, cond_name: str, cond_index: str):
        logger.debug("")
        self.notifyConditionInfoReal(
            {"code": code, "id_type": id_type, "cond_name": cond_name, "cond_index": cond_index, }
        )

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
                    # logger.debug(f"{key}:{strData}")
                    outDict[key] = strData
                multi_data.append(outDict)
        return single_data, multi_data
