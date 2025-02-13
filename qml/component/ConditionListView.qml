import QtQuick 2.15
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.4


ListView {
    id: root

    clip: true
    boundsBehavior: Flickable.StopAtBounds

    signal itemClicked(variant itemData)

    function getCurrentCondition() {
        if (model != null && currentIndex >= 0 && currentIndex < model.length) {
            return model[currentIndex]
        }
    }

    onModelChanged: {
        if (typeof(model) !== 'undefined' && model.length > 0) {
            console.log("onModelChanged")
            currentIndex = 0
        }
    }

    Keys.onUpPressed: {
        console.log("onUpPressed")
        if (currentIndex > 0) {
            --currentIndex
        }
        console.log(currentIndex)
    }

    Keys.onDownPressed: {
        console.log("onDownPressed");
        if (currentIndex < model.length - 1) {
            ++currentIndex
        }
        console.log(currentIndex)
    }

    delegate: Rectangle {
        id: listViewItem
        width: root.width
        height: 30
        border.color: 'black'
        border.width: 1

        Item {
            x: 10
            width: parent.width - x
            height: parent.height
            Text {
                id: listViewItemTextName
                anchors.verticalCenter: parent.verticalCenter
                text: modelData['name']
                font.pixelSize: 16
                color: 'white'
            }
        }
        MouseArea {
            id: listViewItemMouseArea
            anchors.fill: parent
            onClicked: {
                root.itemClicked(modelData)

                root.currentIndex = index
            }
        }

        states: [
            State {
                name: "normal"
                when: !listViewItemMouseArea.containsPress && root.currentIndex != index
                PropertyChanges { target: listViewItem; color: "white" }
                PropertyChanges { target: listViewItemTextName; color: "black" }
            },
            State {
                name: "pressed"
                when: listViewItemMouseArea.containsPress
                PropertyChanges { target: listViewItem; color: "lightskyblue" }
                PropertyChanges { target: listViewItemTextName; color: "white" }
            },
            State {
                name: "focused"
                when: root.currentIndex == index
                PropertyChanges { target: listViewItem; color: "lightsteelblue" }
                PropertyChanges { target: listViewItemTextName; color: "white" }
            }
        ]
    }
}
