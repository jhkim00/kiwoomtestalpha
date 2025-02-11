import QtQuick 2.15
import QtQuick.Controls 2.15
import "./component"

ApplicationWindow {
    visible: true
    x: 0
    y: 480
    width: fixedWidth
    height: fixedHeight
    minimumWidth: fixedWidth
    maximumWidth: fixedWidth
    minimumHeight: fixedHeight
    maximumHeight: fixedHeight
    title: "Market"

    property var fixedWidth: 840
    property var fixedHeight: 480

    Component.onCompleted: {
        console.log("market component completed")
        marketViewModel.load()
    }

    StockInputField {
        id: stockInputField
        y: 10
        width: 200
        height: 40

        stockListView: _stockListView

        onReturnPressed: {
            console.log("stockInputField onReturnPressed")
            var stock = stockListView.getCurrentStock()
            if (typeof(stock) !== 'undefined') {
                marketViewModel.setCurrentStock(stock)
            }
        }

        onDisplayTextChanged: {
            console.log('stockInputField onDisplayTextChanged ' + displayText)
            marketViewModel.setInputText(displayText)
        }
    }

    StockListView {
        id: _stockListView
        anchors.top: stockInputField.bottom
        anchors.topMargin: 2
        width: 200
        height: 200
        model: marketViewModel.searchedStockList
    }

    TextButton {
        id: btnTest
        anchors.right: parent.right
        width: 200
        height: 30
        text: "test"
        textSize: 20
        normalColor: 'lightsteelblue'
        radius: 4
        onBtnClicked: {
            console.log('btnTest clicked')
            marketViewModel.test()
        }
    }
}
