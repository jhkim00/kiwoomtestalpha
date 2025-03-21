import QtQuick 2.15
import QtQuick.Controls 2.15
import "./component"

ApplicationWindow {
    id: root
    visible: true
    width: fixedWidth
    height: fixedHeight
    title: "Market"

    property var fixedWidth: 1600
    property var fixedHeight: 480

    Component.onCompleted: {
        console.trace()
    }

    onVisibleChanged: {
        if (visible) {
            marketViewModel.getStockBasicInfo()
        }
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
            if (typeof(stock) === 'undefined') {
                marketViewModel.showSearchedStockHistory()
                return
            }
            marketViewModel.setCurrentStock(stock)
        }

        onDisplayTextChanged: {
            console.log('stockInputField onDisplayTextChanged ' + displayText)
            marketViewModel.setInputText(displayText)
        }

        Keys.onTabPressed: favoriteListView.forceActiveFocus()
    }

    StockListView {
        id: _stockListView
        anchors.top: stockInputField.bottom
        anchors.bottom: parent.bottom
        anchors.topMargin: 2
        width: 200
        model: marketViewModel.searchedStockList
        visible: root.active
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

        signal itemClicked(real index)

        header: StockPriceHeader {
            width: favoriteListView.width
            height: 20
        }

        delegate: StockPriceDelegate {
            listView: favoriteListView
            width: favoriteListView.width
            height: 40
        }

        onItemClicked: {
            console.trace()
            forceActiveFocus()
            currentIndex = index
            if (currentIndex !== -1) {
                var item = model[currentIndex]
                console.log('Market.qml name ' + item.name + ', '+ item.code)
                marketViewModel.setCurrentStock({'name': item.name, 'code': item.code})
            }
        }

        Keys.onReturnPressed: {
            console.trace()
            if (currentIndex !== -1) {
                var item = model[currentIndex]
                console.log('Market.qml name ' + item.name + ', '+ item.code)
                marketViewModel.setCurrentStock({'name': item.name, 'code': item.code})
            }
        }

        Keys.onTabPressed: stockInputField.forceActiveFocus()

        FocusIndicator {}
    }
}
