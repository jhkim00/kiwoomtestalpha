import QtQuick 2.15
import QtQuick.Controls 2.15
import "./component"

ApplicationWindow {
    id: root
    visible: true
    width: fixedWidth
    height: fixedHeight
    minimumWidth: fixedWidth
    maximumWidth: fixedWidth
    minimumHeight: fixedHeight
    maximumHeight: fixedHeight
    title: "Chart"

    property var fixedWidth: 240
    property var fixedHeight: 480

    Column {
        width: parent.width
        y: 10
        spacing: 10

        TextButton {
            id: btnDailyChart
            width: 200
            height: 30
            anchors.horizontalCenter: parent.horizontalCenter
            text: "daily chart"
            textSize: 20
            normalColor: 'lightsteelblue'
            radius: 4
            onBtnClicked: {
                console.log('btnDailyChart clicked')
                chartViewModel.load(marketViewModel.currentStock['code'])
            }
        }
    }
}
