import sys
import logging
import asyncio
import util

from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal
from model.kiwoom import Kiwoom
from .coolDown import CoolDown

logger = logging.getLogger()

class Manager(QObject):

    def __init__(self):
        super().__init__()
        self.kw = Kiwoom.getInstance()
        self.kw.loginResult.connect(self.onLoginResult)

        self.kw.trCallbacks["opt10001"] = self.__onStockBasicInfo
        self.kw.trCallbacks["OPW00004"] = self.__onAccountInfo
        self.kw.trCallbacks["OPTKWFID"] = self.__onStocksInfo
        self.kw.trCallbacks["opt10082"] = self.__onWeeklyChart
        self.kw.trCallbacks["opt10081"] = self.__onDailyChart
        self.kw.trCallbacks["opt10080"] = self.__onMinuteChart
        self.kw.trCallbacks["opt10004"] = self.__onHoga
        self.kw.trCallbacks["opt10075"] = self.__onMichegyeol
        self.kw.trCallbacks["KOA_NORMAL_BUY_KQ_ORD"] = self.__onSendOrder
        self.kw.realDataCallbacks["주식체결"] = self.__onStockPriceReal
        self.kw.realDataCallbacks["주식호가잔량"] = self.__onStockHogaRemains
        self.kw.conditionVerCallback = self.__onReceiveConditionVer
        self.kw.trConditionCallback = self.__onReceiveTrCondition
        self.kw.realConditionCallback = self.__onReceiveRealCondition
        self.kw.chejanDataCallback = self.__onReceiveChejanData

        self.notifyLoginResult = None
        self.notifyLoginInfo = None
        self.notifyAccountInfo = None
        self.notifyStockNameByCode = None
        self.notifyStockList = None
        self.notifyStockBasicInfo = None
        self.notifyStockPriceReal = None
        self.notifyConditionList = None
        self.notifyStocksInfo = None
        self.notifyConditionInfo = None
        self.notifyWeeklyChart = None
        self.notifyDailyChart = None
        self.notifyMinuteChart = None
        self.notifyConditionInfoReal = None
        self.notifyHogaRemainsReal = None
        self.notifyHoga = None
        self.notifySendOrderResult = None
        self.notifyOrderChegyeolData = None
        self.notifyChejanData = None
        self.notifyMichegyeolInfo = None

        self.stock_price_real_data_fid_list = [
            '20',   # 체결시간
            '10',   # 현재가
            '11',   # 전일대비
            '12',   # 등락율
            '13',   # 누적거래량
            '14',   # 누적거래대금
            '15',   # 거래량(+는 매수체결, -는 매도체결)
            '16',   # 시가
            '17',   # 고가
            '18',   # 저가
            '25',   # 전일대비기호
            '30'    # 전일거래량대비(비율)
        ]

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
        self.kw.SetInputValue(id="거래소구분", value="")     # 거래소구분 = KRX:한국거래소 시세 데이터, NXT:대체거래소 시세 데이터, 공백시 한국거래소 시세 데이터
        await self.coolDown.call()
        while True:
            ret = self.kw.CommRqData(rqname="계좌평가현황요청", trcode="OPW00004", next=0, screen=data["screen_no"])
            if ret != Kiwoom.ERROR_QUERY_RATE_LIMIT_EXCEEDED:
                break
            if ret == Kiwoom.ERROR_QUERY_COUNT_EXCEEDED:
                logger.error(f"error:{ret}")
                raise Exception

            await asyncio.sleep(1)

    async def getStockNameByCode(self, data: dict):
        name = self.kw.GetMasterCodeName(data["stock_no"])
        self.notifyStockNameByCode(name)

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
        while True:
            ret = self.kw.CommRqData(rqname="주식기본정보", trcode="opt10001", next=0, screen=data["screen_no"])
            if ret != Kiwoom.ERROR_QUERY_RATE_LIMIT_EXCEEDED:
                break
            if ret == Kiwoom.ERROR_QUERY_COUNT_EXCEEDED:
                logger.error(f"error:{ret}")
                raise Exception

            await asyncio.sleep(1)

    async def getStockPriceRealData(self, data: dict):
        logger.debug("")
        self.kw.SetRealReg(
            screen=data["screen_no"],
            code_list=";".join(data["code_list"]),
            fid_list=";".join(self.stock_price_real_data_fid_list),
            opt_type=data["opt_type"]
        )

    async def stopStockPriceRealData(self, data: dict):
        logger.debug("")
        self.kw.SetRealRemove(
            screen=data["screen_no"],
            del_code=data["code"]
        )

    async def getStocksInfo(self, data: dict):
        logger.debug("")
        await self.coolDown.call()
        while True:
            ret = self.kw.CommKwRqData(
                arr_code=";".join(data["code_list"]),
                next=0,
                code_count=len(data["code_list"]),
                type=0,
                rqname="복수종목정보요청",
                screen=data["screen_no"]
            )
            if ret != Kiwoom.ERROR_QUERY_RATE_LIMIT_EXCEEDED:
                break
            if ret == Kiwoom.ERROR_QUERY_COUNT_EXCEEDED:
                logger.error(f"error:{ret}")
                raise Exception

            await asyncio.sleep(1)

    async def getConditionLoad(self):
        logger.debug("")
        self.kw.GetConditionLoad()

    async def sendCondition(self, data):
        logger.debug("")
        await self.coolDown.call()
        while True:
            ret = self.kw.SendCondition(
                screen=data["screen_no"],
                cond_name=data["name"],
                cond_index=data["code"],
                search=1
            )
            if ret != Kiwoom.ERROR_QUERY_RATE_LIMIT_EXCEEDED:
                break
            if ret == Kiwoom.ERROR_QUERY_COUNT_EXCEEDED:
                logger.error(f"error:{ret}")
                raise Exception

            await asyncio.sleep(1)

    async def sendConditionStop(self, data):
        logger.debug("")
        await self.coolDown.call()
        self.kw.SendConditionStop(
            screen=data["screen_no"],
            cond_name=data["name"],
            cond_index=data["code"]
        )

    async def getWeeklyChart(self, data):
        logger.debug("")
        self.kw.SetInputValue(id="종목코드", value=data["stock_no"])
        self.kw.SetInputValue(id="기준일자", value=data["ref_day"])
        self.kw.SetInputValue(id="끝일자", value="")
        self.kw.SetInputValue(id="수정주가구분", value="1")
        await self.coolDown.call()
        while True:
            ret = self.kw.CommRqData(rqname="주식주봉차트", trcode="opt10082", next=0, screen=data["screen_no"])
            if ret != Kiwoom.ERROR_QUERY_RATE_LIMIT_EXCEEDED:
                break
            if ret == Kiwoom.ERROR_QUERY_COUNT_EXCEEDED:
                logger.error(f"error:{ret}")
                raise Exception

            await asyncio.sleep(1)

    async def getDailyChart(self, data):
        logger.debug("")
        self.kw.SetInputValue(id="종목코드", value=data["stock_no"])
        self.kw.SetInputValue(id="수정주가구분", value="1")
        await self.coolDown.call()
        while True:
            ret = self.kw.CommRqData(rqname="주식일봉차트", trcode="opt10081", next=0, screen=data["screen_no"])
            if ret != Kiwoom.ERROR_QUERY_RATE_LIMIT_EXCEEDED:
                break
            if ret == Kiwoom.ERROR_QUERY_COUNT_EXCEEDED:
                logger.error(f"error:{ret}")
                raise Exception

            await asyncio.sleep(1)

    async def getMinuteChart(self, data):
        logger.debug("")
        self.kw.SetInputValue(id="종목코드", value=data["stock_no"])
        self.kw.SetInputValue(id="틱범위", value=data["tick_range"])
        await self.coolDown.call()
        while True:
            ret = self.kw.CommRqData(rqname="주식분봉차트", trcode="opt10080", next=0, screen=data["screen_no"])
            if ret != Kiwoom.ERROR_QUERY_RATE_LIMIT_EXCEEDED:
                break
            if ret == Kiwoom.ERROR_QUERY_COUNT_EXCEEDED:
                logger.error(f"error:{ret}")
                raise Exception

            await asyncio.sleep(1)

    async def sendOrder(self, data):
        logger.debug(f"{data}")
        await self.coolDown.call()
        ret = self.kw.SendOrder(
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
        self.notifySendOrderResult(ret)

    async def getHoga(self, data):
        logger.debug(f"{data}")
        self.kw.SetInputValue(id="종목코드", value=data["stock_no"])
        await self.coolDown.call()
        while True:
            ret = self.kw.CommRqData(rqname="주식호가요청", trcode="opt10004", next=0, screen=data["screen_no"])
            if ret != Kiwoom.ERROR_QUERY_RATE_LIMIT_EXCEEDED:
                break
            if ret == Kiwoom.ERROR_QUERY_COUNT_EXCEEDED:
                logger.error(f"error:{ret}")
                raise Exception

            await asyncio.sleep(1)

    async def getMichegyeol(self, data):
        logger.debug(f"{data}")
        self.kw.SetInputValue(id="계좌번호", value=data["account_no"])
        self.kw.SetInputValue(id="전체종목구분", value="0")  # 0:전체, 1:종목
        self.kw.SetInputValue(id="매매구분", value="0")  # 0:전체, 1:매도, 2:매수
        # 시세별 종목코드 (KRX:039490, NXT:039490_NX, 통합:039490_AL) (공백허용, 공백입력시 전체종목구분 "0" 입력하여 전체 종목 대상으로 조회)
        self.kw.SetInputValue(id="종목코드", value="0")
        self.kw.SetInputValue(id="체결구분", value="1")  # 0:전체, 2:체결, 1:미체결
        # 0:통합, 1:KRX, 2:NXT (시세데이터 표시용 구분, 0은 통합시세, 1은 KRX시세, 2은 NXT시세, 공백시 KRX시세)
        self.kw.SetInputValue(id="거래소구분", value="0")
        await self.coolDown.call()
        while True:
            ret = self.kw.CommRqData(rqname="미체결요청", trcode="opt10075", next=0, screen=data["screen_no"])
            if ret != Kiwoom.ERROR_QUERY_RATE_LIMIT_EXCEEDED:
                break
            if ret == Kiwoom.ERROR_QUERY_COUNT_EXCEEDED:
                logger.error(f"error:{ret}")
                raise Exception

            await asyncio.sleep(1)

    """
    slot for kiwoom
    """
    @pyqtSlot(int)
    def onLoginResult(self, result):
        logger.debug(f"result:{result}")
        self.notifyLoginResult(result)

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
            single_data_keys = ['종목코드', '신용비율', '시가총액', 'PER', 'PBR', '매출액', '영업이익', '당기순이익', '유통주식', '유통비율',
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

    def __onWeeklyChart(self, screen, rqname, trcode, record, next):
        logger.debug(f"screen:{screen}, rqname:{rqname}, trcode:{trcode}")
        if rqname == "주식주봉차트":
            single_data_keys = ['종목코드']
            multi_data_keys = ['현재가', '거래량', '거래대금', '일자', '시가', '고가', '저가', '수정주가구분', '수정비율',
                               '수정주가이벤트', '전일종가']
            code, outList = self.__getCommDataByKeys(trcode, rqname, single_data_keys, multi_data_keys)

            self.notifyWeeklyChart((code, outList))

    def __onDailyChart(self, screen, rqname, trcode, record, next):
        logger.debug(f"screen:{screen}, rqname:{rqname}, trcode:{trcode}")
        if rqname == "주식일봉차트":
            single_data_keys = []
            multi_data_keys = ['종목코드', '현재가', '거래량', '거래대금', '일자', '시가', '고가', '저가', '수정주가구분',
                               '수정비율', '수정주가이벤트', '전일종가']
            _, outList = self.__getCommDataByKeys(trcode, rqname, single_data_keys, multi_data_keys)

            self.notifyDailyChart(outList)

    def __onMinuteChart(self, screen, rqname, trcode, record, next):
        logger.debug(f"screen:{screen}, rqname:{rqname}, trcode:{trcode}")
        if rqname == "주식분봉차트":
            single_data_keys = []
            multi_data_keys = ['현재가', '거래량', '체결시간', '시가', '고가', '저가']
            _, outList = self.__getCommDataByKeys(trcode, rqname, single_data_keys, multi_data_keys)

            self.notifyMinuteChart(outList)

    def __onHoga(self, screen, rqname, trcode, record, next):
        logger.debug(f"screen:{screen}, rqname:{rqname}, trcode:{trcode}")
        if rqname == "주식호가요청":
            single_data_keys = []
            multi_data_keys = ["호가잔량기준시간",
                 "매도10차선잔량대비", "매도10차선잔량", "매도10차선호가",
                 "매도9차선잔량대비", "매도9차선잔량", "매도9차선호가",
                 "매도8차선잔량대비", "매도8차선잔량", "매도8차선호가",
                 "매도7차선잔량대비", "매도7차선잔량", "매도7차선호가",
                 "매도6차선잔량대비", "매도6우선잔량", "매도6차선호가",
                 "매도5차선잔량대비", "매도5차선잔량", "매도5차선호가",
                 "매도4차선잔량대비", "매도4차선잔량", "매도4차선호가",
                 "매도3차선잔량대비", "매도3차선잔량", "매도3차선호가",
                 "매도2차선잔량대비", "매도2차선잔량", "매도2차선호가",
                 "매도1차선잔량대비", "매도최우선잔량", "매도최우선호가",
                 "매수1차선잔량대비", "매수최우선잔량", "매수최우선호가",
                 "매수2차선잔량대비", "매수2차선잔량", "매수2차선호가",
                 "매수3차선잔량대비", "매수3차선잔량", "매수3차선호가",
                 "매수4차선잔량대비", "매수4차선잔량", "매수4차선호가",
                 "매수5차선잔량대비", "매수5차선잔량", "매수5차선호가",
                 "매수6차선잔량대비", "매수6우선잔량", "매수6우선호가",
                 "매수7차선잔량대비", "매수7차선잔량", "매수7차선호가",
                 "매수8차선잔량대비", "매수8차선잔량", "매수8차선호가",
                 "매수9차선잔량대비", "매수9차선잔량", "매수9차선호가",
                 "매수10차선잔량대비", "매수10차선잔량", "매수10차선호가",
                 "총매도잔량", "총매수잔량", "총매수잔량직전대비",
                 "시간외매도잔량대비", "시간외매도잔량", "시간외매수잔량", "시간외매수잔량대비"]

            _, outList = self.__getCommDataByKeys(trcode, rqname, single_data_keys, multi_data_keys)
            self.notifyHoga(outList[0])

    def __onMichegyeol(self, screen, rqname, trcode, record, next):
        logger.debug(f"screen:{screen}, rqname:{rqname}, trcode:{trcode}")
        if rqname == "미체결요청":
            single_data_keys = []
            multi_data_keys = [
                "계좌번호",
                "주문번호",
                "종목코드",
                "종목명",
                "주문상태",
                "주문수량",
                "주문가격",
                "미체결수량",
                "원주문번호",
                "주문구분",
                "매매구분",
                "시간",
                "체결번호",
                "체결가",
                "체결량"
            ]

            _, outList = self.__getCommDataByKeys(trcode, rqname, single_data_keys, multi_data_keys)
            self.notifyMichegyeolInfo(outList)

    def __onSendOrder(self, screen, rqname, trcode, record, next):
        logger.debug(f"screen:{screen}, rqname:{rqname}, trcode:{trcode}, record:{record}")
        if rqname == "주식주문":
            strData = self.kw.GetCommData(trcode, rqname, 0, '주문번호')
            logger.debug(f"{strData}")
            if strData == "":
                self.notifySendOrderResult(-10)

    """
    real data callbacks
    """
    def __onStockPriceReal(self, code, rtype, data):
        # logger.debug(f"code:{code}")
        dataList = data.split("\t")
        dataKeys = ("체결시간",
                    "현재가",
                    "전일대비",
                    "등락율",
                    "(최우선)매도호가",
                    "(최우선)매수호가",
                    "거래량",
                    "누적거래량",
                    "누적거래대금",
                    "시가",
                    "고가",
                    "저가",
                    "전일대비기호",
                    "전일거래량대비(계약,주)",
                    "거래대금증감",
                    "전일거래량대비(비율)",
                    "거래회전율",
                    "거래비용",
                    "체결강도",
                    "시가총액(억)",
                    "장구분",
                    "KO접근도",
                    "상한가발생시간",
                    "하한가발생시간")
        dataDict = dict()
        dataDict["code"] = code
        for i, key in enumerate(dataKeys):
            dataDict[key] = dataList[i]
        # logger.debug(f"dataDict:{dataDict}")

        data = {}
        for fid in self.stock_price_real_data_fid_list:
            val = self.kw.GetCommRealData(code, int(fid))
            data[fid] = val
        self.notifyStockPriceReal((code, data))

    def __onStockHogaRemains(self, code, rtype, data):
        # logger.debug(f"code:{code}")
        dataList = data.split("\t")
        dataKeys = ("호가시간",
                     "매도호가1", "매도호가수량1", "매도호가직전대비1", "매수호가1", "매수호가수량1", "매수호가직전대비1",
                     "매도호가2", "매도호가수량2", "매도호가직전대비2", "매수호가2", "매수호가수량2", "매수호가직전대비2",
                     "매도호가3", "매도호가수량3", "매도호가직전대비3", "매수호가3", "매수호가수량3", "매수호가직전대비3",
                     "매도호가4", "매도호가수량4", "매도호가직전대비4", "매수호가4", "매수호가수량4", "매수호가직전대비4",
                     "매도호가5", "매도호가수량5", "매도호가직전대비5", "매수호가5", "매수호가수량5", "매수호가직전대비5",
                     "매도호가6", "매도호가수량6", "매도호가직전대비6", "매수호가6", "매수호가수량6", "매수호가직전대비6",
                     "매도호가7", "매도호가수량7", "매도호가직전대비7", "매수호가7", "매수호가수량7", "매수호가직전대비7",
                     "매도호가8", "매도호가수량8", "매도호가직전대비8", "매수호가8", "매수호가수량8", "매수호가직전대비8",
                     "매도호가9", "매도호가수량9", "매도호가직전대비9", "매수호가9", "매수호가수량9", "매수호가직전대비9",
                     "매도호가10", "매도호가수량10", "매도호가직전대비10", "매수호가10", "매수호가수량10", "매수호가직전대비10",
                     "매도호가총잔량", "매도호가총잔량직전대비", "매수호가총잔량", "매수호가총잔량직전대비",
                     )
        dataDict = dict()
        dataDict["code"] = code
        for i, key in enumerate(dataKeys):
            dataDict[key] = dataList[i]
        # logger.debug(f"dataDict:{dataDict}")

        self.notifyHogaRemainsReal(dataDict)

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

    def __onReceiveChejanData(self, gubun, item_cnt, fid_list):
        logger.debug("")
        fidList = fid_list.strip(";").split(";")
        data = {}
        for fid in fidList:
            strData = self.kw.GetChejanData(fid)
            fidName = util.getFidName(fid)
            logger.debug(f"{fid}:{fidName}:{strData}")
            data[fidName] = strData

        if gubun == "0":  # 접수와 체결시
            self.notifyOrderChegyeolData(data)
        elif gubun == "1":  # 국내주식 잔고변경
            self.notifyChejanData(data)

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
