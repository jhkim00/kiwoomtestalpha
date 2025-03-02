import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../../Globals.js" as Globals

Item {
    id: root
    Layout.fillWidth: true
    Layout.preferredWidth: 100

    property string text: ''
    property var fontSize: Globals.fontPointSize
    property var fontColor: 'black'

    Text {
        anchors.left: parent.left
        anchors.leftMargin: 10
        anchors.verticalCenter: parent.verticalCenter
        text: root.text
        font.pixelSize: root.fontSize
        font.bold: true
        color: root.fontColor
    }
}