import QtQuick 2.15
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.4
import QtQuick.Layouts 1.15
import "../../Globals.js" as Globals

Rectangle {
    id: root
    height: 50
    border.color: 'black'
    border.width: 1

    property var listView
    property bool simpleVersion: false

    Rectangle {
        anchors.fill: parent
        color: listView.currentIndex === index ? "lightsteelblue" : "transparent"
        opacity: 0.5
    }

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
    RowLayout {
        id: priceRow
        x: 120
        width: parent.width - x
        height: parent.height
        //anchors.verticalCenter: parent.verticalCenter

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
            if (numberStr === '') {
                return ''
            }

            // 기호(+,-) 추출
            var sign = '';
            if (numberStr[0] === '+' || numberStr[0] === '-') {
                sign = numberStr[0];
                numberStr = numberStr.slice(1); // 기호를 제외한 숫자만 처리
            }

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

            // 최종 결과 반환 (기호 유지)
            return sign + formattedInt + decimalPart;
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

        CandleStick {
            height: 40
            Layout.fillWidth: true
            Layout.preferredWidth: 20
            open: Math.abs(parseInt(priceRow.startPrice))
            high: Math.abs(parseInt(priceRow.highPrice))
            low: Math.abs(parseInt(priceRow.lowPrice))
            close: Math.abs(parseInt(priceRow.currentPrice))
        }
        VerticalKeyValueLayoutLabel {
            Layout.preferredWidth: 80
            keyText: '현재가'
            valueText: Globals.formatStringPrice(priceRow.currentPrice)
            keyColor: 'black'
            valueColor: priceRow.priceColor
        }
        VerticalKeyValueLayoutLabel {
            Layout.preferredWidth: 40
            keyText: ''
            valueText: priceRow.getDiffSignSymbol()
            keyColor: 'black'
            valueColor: priceRow.priceColor
        }
        VerticalKeyValueLayoutLabel {
            Layout.preferredWidth: 80
            keyText: '등락률'
            valueText: priceRow.numberStrToNonAbsFormated(priceRow.diffRate) + ' %'
            keyColor: 'black'
            valueColor: priceRow.priceColor
        }
        VerticalKeyValueLayoutLabel {
            Layout.preferredWidth: 80
            keyText: '시가'
            valueText: Globals.formatStringPrice(priceRow.startPrice)
            keyColor: 'black'
            valueColor: priceRow.getPriceColor(priceRow.startPrice, priceRow.refPrice)
        }
        VerticalKeyValueLayoutLabel {
            Layout.preferredWidth: 80
            keyText: '고가'
            valueText: Globals.formatStringPrice(priceRow.highPrice)
            keyColor: 'black'
            valueColor: priceRow.getPriceColor(priceRow.highPrice, priceRow.refPrice)
        }
        VerticalKeyValueLayoutLabel {
            Layout.preferredWidth: 80
            keyText: '저가'
            valueText: Globals.formatStringPrice(priceRow.lowPrice)
            keyColor: 'black'
            valueColor: priceRow.getPriceColor(priceRow.lowPrice, priceRow.refPrice)
        }
        VerticalKeyValueLayoutLabel {
            Layout.preferredWidth: 80
            keyText: '기준가'
            valueText: Globals.formatStringPrice(priceRow.refPrice)
            keyColor: 'black'
            valueColor: 'black'
            visible: !root.simpleVersion
        }
        VerticalKeyValueLayoutLabel {
            Layout.preferredWidth: 80
            keyText: '전일대비'
            valueText: Globals.formatStringPrice(priceRow.diffPrice)
            keyColor: 'black'
            valueColor: priceRow.priceColor
            visible: !root.simpleVersion
        }
        VerticalKeyValueLayoutLabel {
            keyText: '거래량'
            valueText: Globals.formatStringPrice(priceRow.volume)
            keyColor: 'black'
            valueColor: 'black'
            visible: !root.simpleVersion
        }
        VerticalKeyValueLayoutLabel {
            keyText: '거래대비'
            valueText: Globals.formatStringPrice(priceRow.volumeRate) + ' %'
            keyColor: 'black'
            valueColor: priceRow.getPriceColor(priceRow.volumeRate, 100)
        }
        VerticalKeyValueLayoutLabel {
            keyText: '거래대금'
            valueText: Globals.formatStringPrice(priceRow.tradingValue)
            keyColor: 'black'
            valueColor: 'black'
        }
    }
    MouseArea {
        id: listViewItemMouseArea
        anchors.fill: parent
        onClicked: {
            listView.itemClicked(index)
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