import QtQuick 2.15
import QtQuick.Controls 2.15
import "./component"
import "../Globals.js" as Globals

ApplicationWindow {
    id: root
    visible: true
    x: 0
    y: 0
    width: fixedWidth
    height: fixedHeight
    minimumWidth: fixedWidth
    maximumWidth: fixedWidth
    minimumHeight: fixedHeight
    maximumHeight: fixedHeight
    title: "Monitoring Stocks"

    property var fixedWidth: 1200
    property var fixedHeight: 480

    Canvas {
        id: canvas
        anchors.margins: 10
        anchors.fill: parent
        onPaint: {
            var ctx = getContext("2d")
            ctx.fillStyle = "lightgrey"
            ctx.fillRect(0, 0, width, height)
            ctx.font = "14px sans-serif"
            ctx.fillStyle = "red"

            var stockList = monitoringStockViewModel.stockList
            var tradingValueList = monitoringStockViewModel.tradingValueList
            var barHeight = height / stockList.length

            for (var i = 0; i < stockList.length; i++) {
                var barWidth = (tradingValueList[i] * width) * 0.9
                var y = i * barHeight
                ctx.fillRect(0, y, barWidth, barHeight - 5)

                ctx.fillStyle = "black"
                ctx.fillText("%1 %2".arg(stockList[i].name).arg(Globals.formatStringPrice(stockList[i].tradingValue)), 10, y + barHeight / 2)
                ctx.fillStyle = "red"
            }
        }
    }

    Text {
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.margins: 20
        horizontalAlignment: Text.AlignRight
        text: Globals.formatStringPrice(monitoringStockViewModel.maxTradingValue)
        font.pixelSize: 20
        font.bold: true
        color: "black"
    }

    Connections {
        target: monitoringStockViewModel
        function onStockListChanged() {
            canvas.requestPaint()
        }
        function onTradingValueListChanged() {
            canvas.requestPaint()
        }
    }
}