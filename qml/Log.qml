import QtQuick 2.15
import QtQuick.Controls 2.15
import "./component"

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
    title: "Log"

    property var fixedWidth: 480
    property var fixedHeight: 1080

    property var accountWindow: null
    property var marketWindow: null
    property var conditionWindow: null

    Column {
        width: parent.width
        y: 10
        spacing: 10

        ListView {
            id: listView
            model: logViewModel.logModel
            width: parent.width - 20
            height: root.height - 50
            anchors.horizontalCenter: parent.horizontalCenter
            clip: true

            delegate: Rectangle {
                width: listView.width
                height: 30
                border.width: 1
                color: 'transparent'
                Text {
                    anchors.fill: parent
                    text: model.display
                    color: 'black'
                    font.pixelSize: 20
                    verticalAlignment: Text.AlignVCenter
                    horizontalAlignment: Text.AlignLeft
                }
            }
        }

        TextButton {
            id: btnTest
            width: 200
            height: 30
            anchors.horizontalCenter: parent.horizontalCenter
            text: "test"
            textSize: 20
            normalColor: 'lightsteelblue'
            radius: 4
            onBtnClicked: {
                console.trace()
                logViewModel.log('test test test test test test test test test test test test')
                listView.update()
            }
        }
    }
}
