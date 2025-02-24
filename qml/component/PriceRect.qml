import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {
    property alias textColor: priceText.color
    property alias text: priceText.text
    property alias textPointSize: priceText.font.pointSize

    width: 150
    border.color: "grey"
    border.width: 1
    Text {
        id: priceText
        anchors.fill: parent
        verticalAlignment: Text.AlignVCenter
        horizontalAlignment: Text.AlignHCenter
        font.pointSize: 14
    }
}