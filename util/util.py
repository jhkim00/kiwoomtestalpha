import re


def formatStringPrice(inputStr: str, showZero: bool = True):
    """
    문자열 inputStr 받아서 천 단위 구분자(,)를 추가한 가격 문자열을 반환합니다.
    만약 문자열이 빈 문자열이면 show_zero 값에 따라 "" 또는 "0"을 반환합니다.
    """
    # '+' 또는 '-' 기호 제거
    cleaned = re.sub(r'[+-]', '', inputStr)

    # 공백 제거
    cleaned = cleaned.strip()

    # 앞에 붙은 0 제거
    cleaned = re.sub(r'^0+', '', cleaned)

    # cleaned 문자열이 빈 문자열일 경우 처리
    if cleaned == "":
        if not showZero:
            return ""
        cleaned = "0"

    # 문자열을 숫자로 변환 (문자열이 숫자가 아닐 경우 0으로 처리)
    try:
        number = int(cleaned)
    except ValueError:
        number = 0

    # 숫자를 문자열로 변환
    number_str = str(number)

    # 천단위 구분자 추가 (문자열을 뒤에서부터 순회하면서)
    formatted = ""
    count = 0
    for i in range(len(number_str) - 1, -1, -1):
        if count != 0 and count % 3 == 0:
            formatted = ',' + formatted
        formatted = number_str[i] + formatted
        count += 1

    return formatted
