import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {
    property alias textColor: volumeText.color
    property alias text: volumeText.text

    width: 150//Globals.cellWidth
    border.color: "grey"
    border.width: 1
    Text {
        id: volumeText
        anchors.fill: parent
        verticalAlignment: Text.AlignVCenter
        horizontalAlignment: Text.AlignRight
        rightPadding: 20
        font.pointSize: 14
        color: 'black'
    }
}