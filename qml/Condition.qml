import QtQuick 2.15
import QtQuick.Controls 2.15
import "./component"

ApplicationWindow {
    visible: true
    x: 0
    y: 480
    width: fixedWidth
    height: fixedHeight
    title: "Condition"

    property var fixedWidth: 1200
    property var fixedHeight: 480

    Component.onCompleted: {
        console.log("market component completed")
        conditionViewModel.load()
    }

    ConditionListView {
        id: conditionListView
        width: 200
        height: parent.height
        model: conditionViewModel.conditionList

        onItemClicked: {
            console.log('conditionListView onItemClicked ' + itemData.name + ', '+ itemData.code)
            conditionViewModel.conditionInfo(itemData.name, itemData.code)
        }
    }

    ListView {
        id: stockPriceListView
        anchors.top: parent.top
        anchors.right: parent.right
        width: parent.width - conditionListView.width
        height: parent.height
        clip: true
        focus: true
        boundsBehavior: Flickable.StopAtBounds
        model: conditionViewModel.conditionStockList

        signal itemClicked(real index)

        header: StockPriceHeader {
            width: stockPriceListView.width
            height: 20
            simpleVersion: true
        }

        delegate: StockPriceDelegate {
            listView: stockPriceListView
            width: stockPriceListView.width
            height: 40
            simpleVersion: true
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
    }
}
