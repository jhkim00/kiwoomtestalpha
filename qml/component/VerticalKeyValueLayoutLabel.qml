import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {
    id: root
    height: 40
    Layout.fillWidth: true
    Layout.preferredWidth: 100

    property string keyText
    property string valueText
    property var keyColor: 'white'
    property var valueColor: 'white'

    Item {
        x: 10
        width: parent.width - x
        height: 14
        Text {
            anchors.verticalCenter: parent.verticalCenter
            text: keyText
            font.pixelSize: 12
            color: keyColor
        }
    }
    Item {
        x: 10
        y: 20
        width: parent.width - x
        height: 18
        Text {
            anchors.verticalCenter: parent.verticalCenter
            text: valueText
            font.pixelSize: 18
            font.bold: true
            color: valueColor
        }
    }
}