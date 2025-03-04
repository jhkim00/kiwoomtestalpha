import QtQuick 2.15
import QtQuick.Controls 2.15
import "../../Globals.js" as Globals

Rectangle {
    property var textHeight: height / 7
    property var chegyeolProvider

    Text {
        width: parent.width
        height: textHeight
        anchors.left: parent.left
        anchors.leftMargin: 10
        verticalAlignment: Text.AlignVCenter
        horizontalAlignment: Text.AlignLeft
        font.pointSize: Globals.fontPointSize
        text: "시가 " + Globals.formatStringPrice(chegyeolProvider.openPrice)
    }

    Text {
        width: parent.width
        height: textHeight
        y: textHeight
        anchors.left: parent.left
        anchors.leftMargin: 10
        verticalAlignment: Text.AlignVCenter
        horizontalAlignment: Text.AlignLeft
        font.pointSize: Globals.fontPointSize
        text: "고가 " + Globals.formatStringPrice(chegyeolProvider.highPrice)
    }

    Text {
        width: parent.width
        height: textHeight
        y: textHeight * 2
        anchors.left: parent.left
        anchors.leftMargin: 10
        verticalAlignment: Text.AlignVCenter
        horizontalAlignment: Text.AlignLeft
        font.pointSize: Globals.fontPointSize
        text: "저가 " + Globals.formatStringPrice(chegyeolProvider.lowPrice)
    }

    Text {
        width: parent.width
        height: textHeight
        y: textHeight * 3
        anchors.left: parent.left
        anchors.leftMargin: 10
        verticalAlignment: Text.AlignVCenter
        horizontalAlignment: Text.AlignLeft
        font.pointSize: Globals.fontPointSize
        text: "현재 " + Globals.formatStringPrice(chegyeolProvider.currentPrice)
        color: Globals.getPriceTextColorByUpDownSign(chegyeolProvider.upDownType)
    }

    Text {
        width: parent.width
        height: textHeight
        y: textHeight * 4
        anchors.left: parent.left
        anchors.leftMargin: 10
        verticalAlignment: Text.AlignVCenter
        horizontalAlignment: Text.AlignLeft
        font.pointSize: Globals.fontPointSize
        text: "등락률 " + Globals.convertToPercentage(chegyeolProvider.changeRate, false)
        color: Globals.getPriceTextColorByUpDownSign(chegyeolProvider.upDownType)
    }

    Text {
        width: parent.width
        height: textHeight
        y: textHeight * 5
        anchors.left: parent.left
        anchors.leftMargin: 10
        verticalAlignment: Text.AlignVCenter
        horizontalAlignment: Text.AlignLeft
        font.pointSize: Globals.fontPointSize
        text: "거래량 " + Globals.formatStringPrice(chegyeolProvider.volume)
    }

    Text {
        width: parent.width
        height: textHeight
        y: textHeight * 6
        anchors.left: parent.left
        anchors.leftMargin: 10
        verticalAlignment: Text.AlignVCenter
        horizontalAlignment: Text.AlignLeft
        font.pointSize: Globals.fontPointSize
        text: "거래대금 " + Globals.formatStringPrice(chegyeolProvider.tradingValue)
    }
}