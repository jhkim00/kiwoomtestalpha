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
    minimumWidth: fixedWidth
    maximumWidth: fixedWidth
    title: "Chegyeol"

    property var fixedWidth: 480
    property var fixedHeight: 720

    ListView {
        id: listView
        model: chegyeolViewModel.chegyeolModel
        width: parent.width - 20
        height: root.height
        anchors.horizontalCenter: parent.horizontalCenter
        clip: true

        property var itemHeight: 20
        property bool showTime: true

        delegate: Row {
            width: listView.width
            height: listView.itemHeight
            Rectangle {
                visible: listView.showTime

                width: parent.width / 3
                height: parent.height
                border.color: "grey"
                border.width: 1

                Text {
                    anchors.fill: parent
                    verticalAlignment: Text.AlignVCenter
                    horizontalAlignment: Text.AlignHCenter
                    font.pointSize: 14
                    color: "black"
                    text: modelData.time
                }
            }
            Rectangle {
                width: parent.width / 3
                height: parent.height
                border.color: "grey"
                border.width: 1

                Text {
                    anchors.fill: parent
                    verticalAlignment: Text.AlignVCenter
                    horizontalAlignment: Text.AlignHCenter
                    font.pointSize: 14
                    color: Globals.getPriceTextColorByUpDownSign(modelData.upDownType)
                    text: Globals.formatStringPrice(modelData.price)
                }
            }
            Rectangle {
                width: parent.width / 3
                height: listView.itemHeight
                border.color: "grey"
                border.width: 1

                Text {
                    anchors.fill: parent
                    verticalAlignment: Text.AlignVCenter
                    horizontalAlignment: Text.AlignHCenter
                    font.pointSize: Globals.fontPointSize
                    color: Globals.getPriceTextColor(modelData.volume)
                    text: Globals.formatStringPrice(modelData.volume)
                }
            }
        }

        onCountChanged: {
            positionViewAtIndex(0, ListView.Beginning)
        }
    }
}
