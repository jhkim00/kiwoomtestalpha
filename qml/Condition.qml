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
        boundsBehavior: Flickable.StopAtBounds
        model: conditionViewModel.conditionStockList

        signal itemClicked(variant itemData)

        delegate: StockPriceDelegate {
            listView: stockPriceListView
            width: stockPriceListView.width
        }

        onItemClicked: {
            console.log('Market.qml onItemClicked ' + itemData.name + ', '+ itemData.code)
            marketViewModel.setCurrentStock({'name': itemData.name, 'code': itemData.code})
        }
    }
}
