import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {
    anchors.fill: parent
    color: parent.focus ? "transparent" : "black"
    opacity: 0.2
    border.width: parent.focus ? 2 : 0
    border.color: "black"
}