import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Shapes 1.15

Item {
    id: root

    // 캔들 데이터 (외부에서 바인딩 가능)
    property var open: 100
    property var high: 120
    property var low: 80
    property var close: 90

    // 색상 설정
    property color bullishColor: "red"  // 상승봉 (Close > Open)
    property color bearishColor: "blue"    // 하락봉 (Close < Open)

    // 캔들 색상 결정
    property color candleColor: close > open ? bullishColor : (close < open ? bearishColor : "black")

    // y축 기준점 계산 (정규화)
    function normalize(value) {
        var range = high - low;
        if (range === 0) {
            return height / 2;  // high와 low가 같다면 중간값 위치로 설정
        }
        return height - ((value - low) / range * height);
    }

    // 심지 (Wick)
    Rectangle {
        id: wick
        width: 2
        height: root.high === root.low ? 2 : (normalize(root.low) - normalize(root.high))
        anchors.horizontalCenter: parent.horizontalCenter
        y: root.high === root.low ? root.height / 2 : normalize(root.high)
        color: root.candleColor
    }

    // 본체 (Body)
    Rectangle {
        id: body
        width: root.width / 2
        height: root.open === root.close ? 2 : Math.abs(normalize(root.open) - normalize(root.close))
        anchors.horizontalCenter: parent.horizontalCenter
        y: root.high === root.low ? root.height / 2 : Math.min(normalize(root.open), normalize(root.close))
        color: root.candleColor
    }
}
