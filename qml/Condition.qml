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
        width: 240
        height: parent.height
        model: conditionViewModel.conditionList

        onItemClicked: {
            console.log('conditionListView onItemClicked ' + itemData['name'] + ', '+ itemData['code'])
        }
    }
}
