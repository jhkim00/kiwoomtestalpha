import QtQuick 2.15
//import QtQuick.Controls 1.4
//import QtQuick.Controls.Styles 1.4

Rectangle {
    id: root

    property alias text: btnText.text
    property alias textSize: btnText.font.pixelSize
    property alias textColor: btnText.color
    property color normalColor: "transparent"
    property color pressedColor: "#55000000"
    property color disabledColor: "darkgrey"

    signal btnClicked()

    Text {
        id: btnText
        anchors.fill: parent
        verticalAlignment: Text.AlignVCenter
        horizontalAlignment: Text.AlignHCenter
    }

    MouseArea {
        id: btnMouseArea
        anchors.fill: parent
        onClicked: root.btnClicked()
    }

    states: [
        State {
            name: "normal"
            when: root.enabled && !btnMouseArea.containsPress
            PropertyChanges { target: root; color: root.normalColor }
        },
        State {
            name: "pressed"
            when: root.enabled && btnMouseArea.containsPress
            PropertyChanges { target: root; color: root.pressedColor }
        },
        State {
            name: "disabled"
            when: !root.enabled
            PropertyChanges { target: root; color: root.disabledColor }
        }
    ]
}