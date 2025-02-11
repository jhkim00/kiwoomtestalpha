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

    property var fixedWidth: 1200
    property var fixedHeight: 480

    Component.onCompleted: {
        console.log("market component completed")
        marketViewModel.load()
        favoriteStockViewModel.load()
    }

    StockInfo {
        id: stockInfo
        width: parent.width
        height: 100
    }

    StockInputField {
        id: stockInputField
        anchors.top: stockInfo.bottom
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

    ListView {
        id: favoriteListView
        anchors.top: stockInfo.bottom
        anchors.right: parent.right
        width: parent.width - _stockListView.width
        height: parent.height - stockInfo.height
        clip: true
        boundsBehavior: Flickable.StopAtBounds
        model: favoriteStockViewModel.stockList

        signal itemClicked(variant itemData)

        delegate: StockPriceDelegate {
            listView: favoriteListView
            width: favoriteListView.width
        }

        onItemClicked: {
            console.trace()
            console.log('onItemClicked ' + itemData.name + ', '+ itemData.code)
            marketViewModel.setCurrentStock({'name': itemData.name, 'code': itemData.code})
        }
    }

    TextButton {
        id: btnTest
        anchors.bottom: parent.bottom
        anchors.left: parent.left
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
