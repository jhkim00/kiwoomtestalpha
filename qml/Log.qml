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
    property var fixedHeight: 720

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
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.left: parent.left
                    anchors.leftMargin: 5
                    text: model.display
                    color: 'black'
                    font.pixelSize: 10
                }
            }

            onCountChanged: {
                positionViewAtEnd()
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

            property var cnt: 0

            onBtnClicked: {
                console.trace()
                btnTest.cnt++
                logViewModel.log('test test test test test test test test test test test test %1'.arg(btnTest.cnt))
                listView.update()
            }
        }
    }
}
