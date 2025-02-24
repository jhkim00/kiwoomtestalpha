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
    title: "HogaWindow"

    property var fixedWidth: 480
    property var fixedHeight: 480

    Column {
        id: col

        property var cellFloorCount: 22
        property var cellHeight: parent.height / cellFloorCount

        Repeater {
            id: askHogaRepeater
            model: 10

            AskHogaRow {
                hogaProvider: hogaViewModel
                chegyeolProvider: chegyeolViewModel
                width: root.width
                rowIndex: index
                rowHeight: col.cellHeight
            }
        }
        Repeater {
            id: bidHogaRepeater
            anchors.top: askHogaRepeater.bottom
            model: 10

            BidHogaRow {
                hogaProvider: hogaViewModel
                chegyeolProvider: chegyeolViewModel
                width: root.width
                rowIndex: index
                rowHeight: col.cellHeight
            }
        }
        Row {
            anchors.horizontalCenter: root.horizontalCenter
            VolumeRect {
                id: rectAskVolume
                width: (root.width - rectTime.width) / 2
                height: col.cellHeight
                text: Globals.formatStringPrice(hogaViewModel.totalAskVolume, true)
            }
            PriceRect {
                id: rectTime
                width: root.width / 3
                height: col.cellHeight
                textColor: 'black'
                text: hogaViewModel.currentTime
            }
            VolumeRect {
                id: rectBidVolume
                width: rectAskVolume.width
                height: col.cellHeight
                text: Globals.formatStringPrice(hogaViewModel.totalBidVolume, true)
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
                hogaViewModel.getHoga()
            }
        }
    }

    TradeInfo {
        width: col.childrenRect.width / 3
        height: col.cellHeight * 10
        x: col.childrenRect.width * 2 / 3
        chegyeolProvider: chegyeolViewModel

        Rectangle {
            anchors.fill: parent
            color: "transparent"
            border.width: 4
            border.color: "grey"
        }
    }
}