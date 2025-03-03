import sys
import logging
import pythoncom
import time
from PyQt5.QAxContainer import *
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal

logger = logging.getLogger()

class Kiwoom(QObject):
    instance = None
    loginResult = pyqtSignal(int)

    ERROR_QUERY_RATE_LIMIT_EXCEEDED = -200
    ERROR_QUERY_COUNT_EXCEEDED = -209

    def __init__(self):
        super().__init__()
        logger.debug("")
        self.ocx = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")

        self.loginState = 0     # 0: not connected, 1: connecting, 2: connected

        self.ocx.OnEventConnect.connect(self.OnEventConnect)
        self.ocx.OnReceiveTrData.connect(self.OnReceiveTrData)
        self.ocx.OnReceiveChejanData.connect(self.OnReceiveChejanData)
        self.ocx.OnReceiveRealData.connect(self.OnReceiveRealData)
        self.ocx.OnReceiveConditionVer.connect(self.OnReceiveConditionVer)
        self.ocx.OnReceiveTrCondition.connect(self.OnReceiveTrCondition)
        self.ocx.OnReceiveRealCondition.connect(self.OnReceiveRealCondition)
        self.ocx.exception.connect(self.OnException)

        self.trCallbacks = {}
        self.realDataCallbacks = {}
        self.conditionVerCallback = None
        self.trConditionCallback = None
        self.realConditionCallback = None

    @classmethod
    def getInstance(cls):
        if cls.instance is None:
            cls.instance = Kiwoom()
        return cls.instance

    #-------------------------------------------------------------------------------------------------------------------
    # callback functions
    #-------------------------------------------------------------------------------------------------------------------
    def OnEventConnect(self, err_code):
        logger.debug(f"err_code: {err_code}")
        if err_code == 0:
            self.loginState = 2
            self.loginResult.emit(2)
        else:
            self.loginState = 0
            self.loginResult.emit(0)

    def OnReceiveTrData(self, screen, rqname, trcode, record, next):
        logger.debug(f"screen:{screen}, rqname:{rqname}, trcode:{trcode}, next:{next}")
        for key in self.trCallbacks:
            if key == trcode:
                cb = self.trCallbacks[key]
                if cb:
                    logger.debug(f"key:{key}, cb:{cb}")
                    try:
                        cb(screen, rqname, trcode, record, next)
                    except Exception as e:
                        logger.error(f"Error while calling cb: {e}", exc_info=True)
                break

    def OnReceiveChejanData(self, gubun, item_cnt, fid_list):
        """주문접수, 체결, 잔고 변경시 이벤트가 발생

        Args:
            gubun (str): '0': 접수, 체결, '1': 잔고 변경
            item_cnt (int): 아이템 갯수
            fid_list (str): fid list
        """
        logger.debug(f"gubun:{gubun}, item_cnt:{item_cnt}, fid_list:{fid_list}")

    def OnReceiveRealData(self, code, rtype, data):
        # logger.debug(f'code: {code}')
        # logger.debug(f'rtype: {rtype}')
        # logger.debug(f'data: {data}')
        """실시간 데이터를 받는 시점에 콜백되는 메소드입니다.

        Args:
            code (str): 종목코드
            rtype (str): 리얼타입 (주식시세, 주식체결, ...)
            data (str): 실시간 데이터 전문
        """
        # logger.debug(f"code:{code}, rtype:{rtype}")
        for key in self.realDataCallbacks:
            if key == rtype:
                cb = self.realDataCallbacks[key]
                if cb:
                    cb(code, rtype, data)
                    break

    def OnReceiveConditionVer(self, ret, msg):
        logger.debug(f"ret:{ret}, msg:{msg}")
        if self.conditionVerCallback:
            self.conditionVerCallback(ret, msg)

    def OnReceiveTrCondition(self, screen_no, code_list, cond_name, cond_index, next):
        """일반조회 TR에 대한 callback 함수

        Args:
            screen_no (str): 종목코드
            code_list (str): 종목리스트(";"로 구분)
            cond_name (str): 조건명
            cond_index (int): 조건명 인덱스
            next (int): 연속조회(0: 연속조회 없음, 2: 연속조회)
        """
        logger.debug(
            f"screen:{screen_no}, code_list:{code_list}, cond_name:{cond_name}, cond_index:{cond_index}, next:{next}")
        try:
            if self.trConditionCallback:
                self.trConditionCallback(screen_no, code_list, cond_name, cond_index, next)
        except Exception as e:
            logger.error(f"Error while calling cb: {e}", exc_info=True)

    def OnReceiveRealCondition(self, code, id_type, cond_name, cond_index):
        """이벤트 함수로 편입, 이탈 종목이 실시간으로 들어오는 callback 함수

        Args:
            code (str): 종목코드
            id_type (str): 편입('I'), 이탈('D')
            cond_name (str): 조건명
            cond_index (str): 조건명 인덱스
        """
        logger.debug(f"code:{code}, id_type:{id_type}, cond_name:{cond_name}, cond_index:{cond_index}")
        try:
            if self.realConditionCallback:
                self.realConditionCallback(code, id_type, cond_name, cond_index)
        except Exception as e:
            logger.error(f"Error while calling cb: {e}", exc_info=True)

    def OnReceiveMsg(self, screen, rqname, trcode, msg):
        logger.debug(f"screen:{screen}, rqname:{rqname}, trcode:{trcode}, msg:{msg}");

    def OnException(self, code: int, source: str, desc: str, help_: str) -> None:
        logger.error(f"code:{code}, source:{source}, desc:{desc}, help:{help_}")

    #-------------------------------------------------------------------------------------------------------------------
    # OpenAPI+ 메서드
    #-------------------------------------------------------------------------------------------------------------------
    def CommConnect(self):
        logger.debug(f"loginState:{self.loginState}")
        if self.loginState != 0:
            self.loginResult.emit(self.loginState)
            return
        self.loginState = 1
        self.ocx.dynamicCall("CommConnect()")

    def CommRqData(self, rqname, trcode, next, screen):
        """
        TR을 서버로 송신합니다.
        :param rqname: 사용자가 임의로 지정할 수 있는 요청 이름
        :param trcode: 요청하는 TR의 코드
        :param next: 0: 처음 조회, 2: 연속 조회
        :param screen: 화면번호 ('0000' 또는 '0' 제외한 숫자값으로 200개로 한정된 값
        :return: None
        """
        logger.debug(f"rqname:{rqname}, trcode:{trcode}, next:{next}, screen:{screen}")
        ret = self.ocx.dynamicCall("CommRqData(QString, QString, int, QString)", rqname, trcode, next, screen)
        logger.debug(f"ret:{ret}")
        return ret

    def GetLoginInfo(self, tag):
        """
        로그인한 사용자 정보를 반환하는 메서드
        :param tag: ("ACCOUNT_CNT, "ACCNO", "USER_ID", "USER_NAME", "KEY_BSECGB", "FIREW_SECGB")
        :return: tag에 대한 데이터 값
        """
        data = self.ocx.dynamicCall("GetLoginInfo(QString)", tag)

        if tag == "ACCNO":
            return data.split(';')[:-1]
        else:
            return data

    def SendOrder(self, rqname, screen, accno, order_type, code, quantity, price, hoga, order_no):
        """
        주식 주문을 서버로 전송하는 메서드
        시장가 주문시 주문단가는 0으로 입력해야 함 (가격을 입력하지 않음을 의미)
        :param rqname: 사용자가 임의로 지정할 수 있는 요청 이름
        :param screen: 화면번호 ('0000' 또는 '0' 제외한 숫자값으로 200개로 한정된 값
        :param accno: 계좌번호 10자리
        :param order_type: 1: 신규매수, 2: 신규매도, 3: 매수취소, 4: 매도취소, 5: 매수정정, 6: 매도정정
        :param code: 종목코드
        :param quantity: 주문수량
        :param price: 주문단가
        :param hoga: 00: 지정가, 03: 시장가,
                     05: 조건부지정가, 06: 최유리지정가, 07: 최우선지정가,
                     10: 지정가IOC, 13: 시장가IOC, 16: 최유리IOC,
                     20: 지정가FOK, 23: 시장가FOK, 26: 최유리FOK,
                     61: 장전시간외종가, 62: 시간외단일가, 81: 장후시간외종가
        :param order_no: 원주문번호로 신규 주문시 공백, 정정이나 취소 주문시에는 원주문번호를 입력
        :return:
        """
        ret = self.ocx.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                                   [rqname, screen, accno, order_type, code, quantity, price, hoga, order_no])
        return ret

    def SetInputValue(self, id, value):
        """
        TR 입력값을 설정하는 메서드
        :param id: TR INPUT의 아이템명
        :param value: 입력 값
        :return: None
        """
        logger.debug(f"id:{id}, value:{value}")
        self.ocx.dynamicCall("SetInputValue(QString, QString)", id, value)

    def DisconnectRealData(self, screen):
        """
        화면번호에 대한 리얼 데이터 요청을 해제하는 메서드
        :param screen: 화면번호
        :return: None
        """
        self.ocx.dynamicCall("DisconnectRealData(QString)", screen)

    def GetRepeatCnt(self, trcode, rqname):
        """
        멀티데이터의 행(row)의 개수를 얻는 메서드
        :param trcode: TR코드
        :param rqname: 사용자가 설정한 요청이름
        :return: 멀티데이터의 행의 개수
        """
        count = self.ocx.dynamicCall("GetRepeatCnt(QString, QString)", trcode, rqname)
        return count

    def CommKwRqData(self, arr_code, next, code_count, type, rqname, screen):
        """
        여러 종목 (한 번에 100종목)에 대한 TR을 서버로 송신하는 메서드
        :param arr_code: 여러 종목코드 예: '000020:000040'
        :param next: 0: 처음조회
        :param code_count: 종목코드의 개수
        :param type: 0: 주식종목 3: 선물종목
        :param rqname: 사용자가 설정하는 요청이름
        :param screen: 화면번호
        :return:
        """
        ret = self.ocx.dynamicCall("CommKwRqData(QString, bool, int, int, QString, QString)", arr_code, next, code_count, type, rqname, screen);
        return ret

    def GetAPIModulePath(self):
        """
        OpenAPI 모듈의 경로를 반환하는 메서드
        :return: 모듈의 경로
        """
        ret = self.ocx.dynamicCall("GetAPIModulePath()")
        return ret

    def GetCodeListByMarket(self, market):
        """
        시장별 상장된 종목코드를 반환하는 메서드
        :param market: 0: 코스피, 3: ELW, 4: 뮤추얼펀드 5: 신주인수권 6: 리츠
                       8: ETF, 9: 하이일드펀드, 10: 코스닥, 30: K-OTC, 50: 코넥스(KONEX)
        :return: 종목코드 리스트 예: ["000020", "000040", ...]
        """
        data = self.ocx.dynamicCall("GetCodeListByMarket(QString)", market)
        tokens = data.split(';')[:-1]
        return tokens

    def GetConnectState(self):
        """
        현재접속 상태를 반환하는 메서드
        :return: 0:미연결, 1: 연결완료
        """
        ret = self.ocx.dynamicCall("GetConnectState()")
        return ret

    def GetMasterCodeName(self, code):
        """
        종목코드에 대한 종목명을 얻는 메서드
        :param code: 종목코드
        :return: 종목명
        """
        data = self.ocx.dynamicCall("GetMasterCodeName(QString)", code)
        return data

    def GetMasterListedStockCnt(self, code):
        """
        종목에 대한 상장주식수를 리턴하는 메서드
        :param code: 종목코드
        :return: 상장주식수
        """
        data = self.ocx.dynamicCall("GetMasterListedStockCnt(QString)", code)
        return data

    def GetMasterStockState(self, code):
        """
        종목의 종목상태를 반환하는 메서드
        :param code: 종목코드
        :return: 종목상태
        """
        data = self.ocx.dynamicCall("GetMasterStockState(QString)", code)
        return data.split("|")

    def GetDataCount(self, record):
        count = self.ocx.dynamicCall("GetDataCount(QString)", record)
        return count

    def GetOutputValue(self, record, repeat_index, item_index):
        count = self.ocx.dynamicCall("GetOutputValue(QString, int, int)", record, repeat_index, item_index)
        return count

    def GetCommData(self, trcode, rqname, index, item):
        """
        수순 데이터를 가져가는 메서드
        :param trcode: TR 코드
        :param rqname: 요청 이름
        :param index: 멀티데이터의 경우 row index
        :param item: 얻어오려는 항목 이름
        :return:
        """
        data = self.ocx.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, rqname, index, item)
        return data.strip()

    def GetCommRealData(self, code, fid):
        data = self.ocx.dynamicCall("GetCommRealData(QString, int)", code, fid)
        return data

    def GetChejanData(self, fid):
        data = self.ocx.dynamicCall("GetChejanData(int)", fid)
        return data

    def GetThemeGroupList(self, type=1):
        data = self.ocx.dynamicCall("GetThemeGroupList(int)", type)
        tokens = data.split(';')
        if type == 0:
            grp = {x.split('|')[0]:x.split('|')[1] for x in tokens}
        else:
            grp = {x.split('|')[1]: x.split('|')[0] for x in tokens}
        return grp

    def GetThemeGroupCode(self, theme_code):
        data = self.ocx.dynamicCall("GetThemeGroupCode(QString)", theme_code)
        data = data.split(';')
        return [x[1:] for x in data]

    def GetFutureList(self):
        data = self.ocx.dynamicCall("GetFutureList()")
        return data

    def SetRealReg(self, screen, code_list, fid_list, opt_type):
        """
        :param screen:
        :param code_list:
        :param fid_list:
        :param opt_type: 실시간 등록 타입, 0또는 1, 0: 기존 종목들 실시간 해지 & 등록한 종목만 실시간 등록, 1: 기존 종목들 유지
        :return:
        """
        ret = self.ocx.dynamicCall("SetRealReg(QString, QString, QString, QString)", screen, code_list, fid_list, opt_type)
        logger.debug(f"ret:{ret}")
        return ret

    def SetRealRemove(self, screen, del_code):
        ret = self.ocx.dynamicCall("SetRealRemove(QString, QString)", screen, del_code)
        return ret

    def GetConditionLoad(self):
        logger.debug("")
        self.ocx.dynamicCall("GetConditionLoad()")

    def GetConditionNameList(self):
        data = self.ocx.dynamicCall("GetConditionNameList()")
        conditions = data.split(";")[:-1]

        # [('000', 'perpbr'), ('001', 'macd'), ...]
        result = []
        for condition in conditions:
            cond_index, cond_name = condition.split('^')
            result.append((cond_index, cond_name))

        return result

    def SendCondition(self, screen, cond_name, cond_index, search):
        """조건검색 종목조회 TR을 송신

        Args:
            screen (str): 화면번호
            cond_name (str): 조건명
            cond_index (int): 조건명 인덱스
            search (int): 0: 일반조회, 1: 실시간조회, 2: 연속조회

        Returns:
            None: _description_
        """
        return self.ocx.dynamicCall("SendCondition(QString, QString, int, int)", screen, cond_name, cond_index, search)

    def SendConditionStop(self, screen, cond_name, cond_index):
        self.ocx.dynamicCall("SendConditionStop(QString, QString, int)", screen, cond_name, cond_index)

    def GetCommDataEx(self, trcode, rqname):
        data = self.ocx.dynamicCall("GetCommDataEx(QString, QString)", trcode, rqname)
        return data