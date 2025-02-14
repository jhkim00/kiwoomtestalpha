import QtQuick 2.15
import QtQuick.Controls 2.15
import "./component"

Rectangle {
    id: root

    color: "#dd333333"
    clip: true

    property string stockName
    property string stockCode

    property string sichong: ''
    property string per: ''
    property string pbr: ''
    property string maechul: ''
    property string operatingProfit: ''
    property string netProfit: ''
    property string yootongNumber: ''
    property string yootongRate: ''
    property string sinyongRate: ''

    property string startPrice: ''
    property string highPrice: ''
    property string lowPrice: ''
    property string currentPrice: ''
    property string refPrice: ''
    property string diffSign: ''
    property string diffPrice: ''
    property string diffRate: ''
    property string volume: ''
    property string volumeRate: ''
    property string priceColor: 'white'
    property bool isFavorite: false

    function updateFavorite() {
        isFavorite = favoriteStockViewModel.isFavoriteStock(stockCode)
    }

    function numberStrToNonAbsFormated(numberStr) {
        var result = '';
        var strLength = numberStr.length;
        var commaIndex = strLength % 3;

        // 소수점의 위치 파악
        var decimalIndex = numberStr.indexOf('.');
        if (decimalIndex === -1) {
            decimalIndex = strLength; // 소수점이 없으면 문자열의 길이로 설정
        }

        for (var i = 0; i < strLength; i++) {
            result += numberStr[i];
            if (i === commaIndex - 1 && i !== strLength - 1 && i < decimalIndex - 1) {
                result += ',';
                commaIndex += 3;
            }
        }

        return result;
    }

    function numberStrToFormated(numberStr) {
        // 숫자 문자열에서 '+' 또는 '-' 기호 제거
        numberStr = numberStr.replace(/^[-+]/, '');

        return numberStrToNonAbsFormated(numberStr)
    }

    function getPriceColor(price, refPrice) {
        var nPrice = parseInt(price)
        var nRef = parseInt(refPrice)
        if (nPrice > nRef) {
            return 'red'
        }
        if (nPrice < nRef) {
            return 'blue'
        }
        return 'white'
    }

    function getDiffSignSymbol() {
        switch (diffSign) {
        case '1': return "\u2b61"
        case '2': return "\u25b2"
        case '5': return "\u25bc"
        default: return ""
        }
    }

    Component.onCompleted: {
        console.log('StockInfo.qml Component.onCompleted.')
    }

    Connections {
        target: marketViewModel
        function onCurrentStockChanged(name, code) {
            console.log("StockInfo.qml onCurrentStockChanged")
            root.stockName = name
            root.stockCode =  code
            marketViewModel.getStockBasicInfo()

            root.updateFavorite()
        }
        function onBasicInfoChanged() {
            console.log('onBasicInfoChanged')

            sichong = target.basicInfo['시가총액']
            per = target.basicInfo['PER']
            pbr = target.basicInfo['PBR']
            maechul = target.basicInfo['매출액']
            operatingProfit = target.basicInfo['영업이익']
            netProfit = target.basicInfo['당기순이익']
            yootongNumber = target.basicInfo['유통주식']
            yootongRate = target.basicInfo['유통비율']
            sinyongRate = target.basicInfo['신용비율']
        }
        function onPriceInfoChanged() {
            console.log('onPriceInfoChanged')

            startPrice = target.priceInfo['시가']
            highPrice = target.priceInfo['고가']
            lowPrice = target.priceInfo['저가']
            currentPrice = target.priceInfo['현재가']
            refPrice = target.priceInfo['기준가']
            diffSign = target.priceInfo['대비기호']
            diffPrice = target.priceInfo['전일대비']
            diffRate = target.priceInfo['등락율']
            volume = target.priceInfo['거래량']
            volumeRate = target.priceInfo['거래대비']

            priceColor = getPriceColor(currentPrice, refPrice)
        }
    }

    Connections {
        target: favoriteStockViewModel
        function onStockListChanged() {
            console.log('StockInfo.qml onStockListChanged')
            updateFavorite()
        }
    }

    Item {
        id: stockNameAndCode
        anchors.verticalCenter: parent.verticalCenter
        width: 150
        height: parent.height

        Item {
            x: 10
            width: parent.width - x
            height: 20
            anchors.bottom: parent.verticalCenter
            Text {
                anchors.verticalCenter: parent.verticalCenter
                text: stockName
                font.pixelSize: 20
                font.bold: true
                color: 'white'
            }
        }
        Item {
            x: 10
            width: parent.width - x
            height: 14
            anchors.top: parent.verticalCenter
            Text {
                anchors.verticalCenter: parent.verticalCenter
                text: stockCode
                font.pixelSize: 12
                font.bold: false
                color: 'white'
            }
        }
        TextButton {
            id: favoriteBtn
            width: 30
            height: 30
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            anchors.rightMargin: 10
            anchors.bottomMargin: 10
            text:  isFavorite ? '-' : '+'
            textSize: 20
            normalColor: 'grey'
            radius: 10
            onBtnClicked: {
                console.trace()
                console.log('%1 button clicked.'.arg(text))

                isFavorite ? favoriteStockViewModel.delete(stockCode)
                           : favoriteStockViewModel.add(stockName, stockCode)
            }
        }
    }

    Row {
        id: basicInfo
        height: parent.height * 0.5 - anchors.topMargin
        anchors.top: parent.top
        anchors.topMargin: 10
        anchors.left: stockNameAndCode.right

        VerticalKeyValueLabel {
            keyText: '시가총액'
            valueText: numberStrToFormated(sichong)
        }
        VerticalKeyValueLabel {
            keyText: 'PER'
            valueText: per
        }
        VerticalKeyValueLabel {
            keyText: 'PBR'
            valueText: pbr
        }
        VerticalKeyValueLabel {
            keyText: '매출액'
            valueText: numberStrToFormated(maechul)
        }
        VerticalKeyValueLabel {
            keyText: '영업이익'
            valueText: numberStrToFormated(operatingProfit)
        }
        VerticalKeyValueLabel {
            keyText: '당기순이익'
            valueText: numberStrToFormated(netProfit)
        }
        VerticalKeyValueLabel {
            keyText: '유통주식'
            valueText: numberStrToFormated(yootongNumber)
        }
        VerticalKeyValueLabel {
            keyText: '유통비율'
            valueText: yootongRate + ' %'
        }
        VerticalKeyValueLabel {
            keyText: '신용비율'
            valueText: numberStrToFormated(sinyongRate) + ' %'
        }
    }

    Row {
        id: priceInfo
        height: basicInfo.height
        anchors.top: basicInfo.bottom
        anchors.topMargin: 10
        anchors.left: basicInfo.left

        VerticalKeyValueLabel {
            keyText: '시가'
            valueText: numberStrToFormated(startPrice)
            valueColor: getPriceColor(startPrice, refPrice)
        }
        VerticalKeyValueLabel {
            keyText: '고가'
            valueText: numberStrToFormated(highPrice)
            valueColor: getPriceColor(highPrice, refPrice)
        }
        VerticalKeyValueLabel {
            keyText: '저가'
            valueText: numberStrToFormated(lowPrice)
            valueColor: getPriceColor(lowPrice, refPrice)
        }
        VerticalKeyValueLabel {
            keyText: '현재가'
            valueText: numberStrToFormated(currentPrice)
            valueColor: priceColor
        }
        VerticalKeyValueLabel {
            keyText: '기준가'
            valueText: numberStrToFormated(refPrice)
        }
        VerticalKeyValueLabel {
            keyText: '대비기호'
            valueText: getDiffSignSymbol()
            valueColor: priceColor
        }
        VerticalKeyValueLabel {
            keyText: '전일대비'
            valueText: numberStrToFormated(diffPrice)
            valueColor: priceColor
        }
        VerticalKeyValueLabel {
            keyText: '등락률'
            valueText: numberStrToNonAbsFormated(diffRate) + ' %'
            valueColor: priceColor
        }
        VerticalKeyValueLabel {
            keyText: '거래량'
            valueText: numberStrToFormated(volume)
        }
        VerticalKeyValueLabel {
            keyText: '거래대비'
            valueText: numberStrToFormated(volumeRate) + ' %'
            valueColor: getPriceColor(volumeRate, 100)
        }
    }
}