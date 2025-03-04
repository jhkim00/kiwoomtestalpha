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
    title: "Monitoring Stocks"

    property var fixedWidth: 1200
    property var fixedHeight: 480

    function getColorByTrandingValue(value) {
        var intVal = parseInt(value)
        if (intVal > 1000000) {
            return "darkred"
        }
        if (intVal > 500000) {
            return "firebrick"
        }
        if (intVal > 100000) {
            return "red"
        }
        if (intVal > 50000) {
            return "salmon"
        }
        return "orange"
    }

    Canvas {
        id: canvas
        anchors.margins: 10
        anchors.fill: parent
        onPaint: {
            var ctx = getContext("2d")
            ctx.fillStyle = "lightgrey"
            ctx.fillRect(0, 0, width, height)
            ctx.font = "14px sans-serif"

            var stockList = monitoringStockViewModel.stockList
            var tradingValueList = monitoringStockViewModel.tradingValueList
            var tradingValueInTimeList = monitoringStockViewModel.tradingValueInTimeList
            var chegyeolBuyTradingValueInTimeList = monitoringStockViewModel.chegyeolBuyTradingValueInTimeList
            var chegyeolSellTradingValueInTimeList = monitoringStockViewModel.chegyeolSellTradingValueInTimeList
            var barHeight = height / stockList.length

            for (var i = 0; i < stockList.length; i++) {
                var barWidth = (tradingValueList[i] * width) * 0.9
                var y = i * barHeight
                var stock = stockList[i]

                ctx.fillStyle = root.getColorByTrandingValue(stock.tradingValue)
                ctx.fillRect(0, y, barWidth, barHeight - 5)

                //console.log("%1 %2".arg(stock.name).arg(tradingValueInTimeList[i]))

                ctx.fillStyle = "black"
                ctx.fillText(
                    "%1 %2 (%3)    |    %4 (%5, %6, %7)"
                    .arg(stock.name)
                    .arg(Globals.formatStringPrice(stock.currentPrice))
                    .arg(Globals.convertToPercentage(stock.diffRate, true))
                    .arg(Globals.formatStringPrice(stock.tradingValue))
                    .arg(Globals.formatStringPrice(tradingValueInTimeList[i], true))
                    .arg(Globals.formatStringPrice(chegyeolBuyTradingValueInTimeList[i], true))
                    .arg(Globals.formatStringPrice(chegyeolSellTradingValueInTimeList[i], true)),
                    10, y + barHeight / 2
                )
            }
        }
    }

    MouseArea {
        anchors.fill: parent
        onClicked: (mouse) => {
            var stockList = monitoringStockViewModel.stockList
            var barHeight = canvas.height / stockList.length

            var index = Math.floor(mouse.y / barHeight)
            if (index >= 0 && index < stockList.length) {
                var selectedStock = stockList[index]
                console.log("Clicked stock:", selectedStock.name, selectedStock.tradingValue)
                marketViewModel.setCurrentStock({'code': selectedStock.code, 'name': selectedStock.name})
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