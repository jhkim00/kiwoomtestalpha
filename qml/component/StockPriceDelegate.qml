import QtQuick 2.15
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.4

Rectangle {
    id: root
    height: 50
    border.color: 'black'
    border.width: 1

    property var listView

    Item {
        x: 10
        width: parent.width - x
        height: 18
        Text {
            id: listViewItemTextName
            anchors.verticalCenter: parent.verticalCenter
            text: modelData.name
            font.pixelSize: 16
            color: 'white'
        }
    }
    Item {
        x: 10
        y: 20
        width: parent.width - x
        height: 14
        Text {
            id: listViewItemTextCode
            anchors.verticalCenter: parent.verticalCenter
            text: modelData.code
            font.pixelSize: 12
            font.bold: false
            color: 'white'
        }
    }
    Row {
        id: priceRow
        x: 120
        height: parent.height
        anchors.verticalCenter: parent.verticalCenter

        property var code: modelData.code
        property string startPrice: modelData.startPrice
        property string highPrice: modelData.highPrice
        property string lowPrice: modelData.lowPrice
        property string currentPrice: modelData.currentPrice
        property string refPrice: modelData.refPrice
        property string diffSign: modelData.diffSign
        property string diffPrice: modelData.diffPrice
        property string diffRate: modelData.diffRate
        property string volume: modelData.volume
        property string volumeRate: modelData.volumeRate
        property string tradingValue: modelData.tradingValue
        property string priceColor: getPriceColor(currentPrice, refPrice)

        function numberStrToNonAbsFormated(numberStr) {
            // 소수점이 있는 경우 정수 부분과 소수 부분을 분리
            var parts = numberStr.split('.');
            var intPart = parts[0]; // 정수 부분
            var decimalPart = parts.length > 1 ? '.' + parts[1] : ''; // 소수 부분 (있으면 추가)

            // 정수 부분을 뒤집은 후, 3자리마다 쉼표 추가 후 다시 뒤집기
            var formattedInt = intPart
                .split('')
                .reverse()
                .join('')
                .match(/.{1,3}/g)
                .join(',')
                .split('')
                .reverse()
                .join('');

            // 최종 결과 반환
            return formattedInt + decimalPart;
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
            return 'black'
        }

        function getDiffSignSymbol() {
            switch (diffSign) {
            case '1': return "\u2b61"
            case '2': return "\u25b2"
            case '5': return "\u25bc"
            default: return ""
            }
        }

        VerticalKeyValueLabel {
            width: 80
            keyText: '현재가'
            valueText: priceRow.numberStrToFormated(priceRow.currentPrice)
            keyColor: 'black'
            valueColor: priceRow.priceColor
        }
        VerticalKeyValueLabel {
            width: 40
            keyText: ''
            valueText: priceRow.getDiffSignSymbol()
            keyColor: 'black'
            valueColor: priceRow.priceColor
        }
        VerticalKeyValueLabel {
            width: 80
            keyText: '등락률'
            valueText: priceRow.numberStrToNonAbsFormated(priceRow.diffRate) + ' %'
            keyColor: 'black'
            valueColor: priceRow.priceColor
        }
        VerticalKeyValueLabel {
            width: 80
            keyText: '시가'
            valueText: priceRow.numberStrToFormated(priceRow.startPrice)
            keyColor: 'black'
            valueColor: priceRow.getPriceColor(priceRow.startPrice, priceRow.refPrice)
        }
        VerticalKeyValueLabel {
            width: 80
            keyText: '고가'
            valueText: priceRow.numberStrToFormated(priceRow.highPrice)
            keyColor: 'black'
            valueColor: priceRow.getPriceColor(priceRow.highPrice, priceRow.refPrice)
        }
        VerticalKeyValueLabel {
            width: 80
            keyText: '저가'
            valueText: priceRow.numberStrToFormated(priceRow.lowPrice)
            keyColor: 'black'
            valueColor: priceRow.getPriceColor(priceRow.lowPrice, priceRow.refPrice)
        }
        VerticalKeyValueLabel {
            width: 80
            keyText: '기준가'
            valueText: priceRow.numberStrToFormated(priceRow.refPrice)
            keyColor: 'black'
            valueColor: 'black'
        }
        VerticalKeyValueLabel {
            width: 80
            keyText: '전일대비'
            valueText: priceRow.numberStrToFormated(priceRow.diffPrice)
            keyColor: 'black'
            valueColor: priceRow.priceColor
        }
        VerticalKeyValueLabel {
            keyText: '거래량'
            valueText: priceRow.numberStrToFormated(priceRow.volume)
            keyColor: 'black'
            valueColor: 'black'
        }
        VerticalKeyValueLabel {
            keyText: '거래대비'
            valueText: priceRow.numberStrToFormated(priceRow.volumeRate) + ' %'
            keyColor: 'black'
            valueColor: priceRow.getPriceColor(priceRow.volumeRate, 100)
        }
        VerticalKeyValueLabel {
            keyText: '거래대금'
            valueText: priceRow.numberStrToFormated(priceRow.tradingValue)
            keyColor: 'black'
            valueColor: 'black'
        }
    }
    MouseArea {
        id: listViewItemMouseArea
        anchors.fill: parent
        onClicked: {
            console.log('StockPriceDelegate.qml onClicked %1'.arg(root.color))
            listView.itemClicked(modelData)
        }
    }

    states: [
        State {
            name: "normal"
            when: !listViewItemMouseArea.containsPress
            PropertyChanges { target: root; color: "white" }
            PropertyChanges { target: listViewItemTextName; color: "black" }
            PropertyChanges { target: listViewItemTextCode; color: "black" }
        },
        State {
            name: "pressed"
            when: listViewItemMouseArea.containsPress
            PropertyChanges { target: root; color: "lightskyblue" }
            PropertyChanges { target: listViewItemTextName; color: "white" }
            PropertyChanges { target: listViewItemTextCode; color: "white" }
        }
    ]
}