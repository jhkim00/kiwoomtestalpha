.pragma library

var cellWidth = 150
var fontPointSize = 14

function getPriceTextColor(priceText) {
    switch (priceText[0]) {
    case '+':
        return 'red'
    case '-':
        return 'blue'
    default:
        return 'black'
    }
}

function getPriceTextColorByUpDownSign(uDownSign) {
    switch (uDownSign) {
    case '2':
        return 'red'
    case '5':
        return 'blue'
    default:
        return 'black'
    }
}

function formatStringSignedPrice(input) {
    // 음수 여부 확인
    var isNegative = input.trim().startsWith("-");
    var formatted = formatStringPrice(input, true);
    if (isNegative) {
        formatted = '-' + formatted;
    }
    return formatted
}

function formatStringPrice(input, showZero) {
    // '+' 또는 '-' 기호 제거
    var cleaned = input.replace(/[+-]/g, '');

    // 공백 제거
    cleaned = cleaned.trim();

    // 앞에 붙은 0 제거
    cleaned = cleaned.replace(/^0+/, '');

    // cleaned 문자열이 빈 문자열일 경우 '0'으로 대체
    if (cleaned === "") {
        if (!showZero) {
            return ""
        }

        cleaned = "0";
    }

    // 문자열을 숫자로 변환
    var number = parseInt(cleaned, 10);

    // 숫자가 NaN일 경우 0으로 처리
    if (isNaN(number)) {
        number = 0;
    }

    // 숫자를 문자열로 변환
        var numberStr = number.toString();

    // 천단위 구분자 추가 (숫자가 1000 이상일 때만)
    var formatted = "";
    var count = 0;

    // 문자열을 뒤에서부터 순회하면서 천단위 구분자 ',' 추가
    for (var i = numberStr.length - 1; i >= 0; i--) {
        if (count !== 0 && count % 3 === 0) {
            formatted = ',' + formatted;
        }
        formatted = numberStr[i] + formatted;
        count++;
    }

    return formatted;
}

function convertToPercentage(input, keepSign) {
    var isNegative = input.trim().startsWith("-");
    // '+-' 기호 제거
    var cleaned = input.replace(/[+-]/g, '');

    // 소수점 두 자리로 포맷 후 % 기호 추가
    var formatted = parseFloat(cleaned).toFixed(2) + " %";
    if (isNegative) {
        formatted = '-' + formatted;
    }
    return formatted;
}

function formatStringProfitRatio(input, decimalPlaces) {
    // 음수 여부 확인
    var isNegative = input.trim().startsWith("-");
    // '-' 기호 제거
    var cleaned = input.replace(/[-]/g, '');

    var num = parseFloat(cleaned) / Math.pow(10, decimalPlaces);
    var numStr = num.toString();
    if (isNegative) {
        numStr = '-' + numStr;
    }
    return numStr + " %";
}