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
    title: "Monitoring Stocks Chegyeol Graph"

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

            var stockList = monitoringStockViewModel.stockList
            var chegyeolBuyTradingValueInTimeList = monitoringStockViewModel.chegyeolBuyTradingValueInTimeList
            var chegyeolSellTradingValueInTimeList = monitoringStockViewModel.chegyeolSellTradingValueInTimeList
            var barHeight = 0.5 * height / stockList.length

            for (var i = 0; i < stockList.length; i++) {
                var buyVal = chegyeolBuyTradingValueInTimeList[i]
                var sellVal = chegyeolSellTradingValueInTimeList[i]
                var buyUi = buyVal > 5000000000 ? 1 : buyVal / 5000000000
                var sellUi = sellVal > 5000000000 ? 1 : sellVal / 5000000000
                var barWidth_buy = (buyUi * width) * 0.9
                var barWidth_sell = (sellUi * width) * 0.9
                var y = i * barHeight * 2
                var stock = stockList[i]

                ctx.fillStyle = "red"
                ctx.fillRect(0, y, barWidth_buy, barHeight - 5)
                ctx.fillStyle = "blue"
                ctx.fillRect(0, y + barHeight, barWidth_sell, barHeight - 5)

                //console.log("%1 %2".arg(stock.name).arg(buyVal))
                //console.log("%1 %2".arg(stock.name).arg(sellVal))

                ctx.fillStyle = "black"
                ctx.fillText(
                    "%1 %2"
                    .arg(stock.name)
                    .arg(Globals.formatStringPrice(buyVal, true)),
                    10, y + 0.5 * barHeight
                )
                ctx.fillText(
                    "%1"
                    .arg(Globals.formatStringPrice(sellVal, true)),
                    10, y + 1.5 * barHeight
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

    Connections {
        target: monitoringStockViewModel
        function onStockListChanged() {
            canvas.requestPaint()
        }
        /*function onTradingValueInTimeListChanged() {
            canvas.requestPaint()
        }*/
    }

    Timer {
        interval: 400     // 1000밀리초 = 1초
        repeat: true       // 반복 실행
        running: true      // 타이머 자동 시작
        onTriggered: {
            //console.log("타이머 트리거됨!")
            canvas.requestPaint()
        }
    }
}