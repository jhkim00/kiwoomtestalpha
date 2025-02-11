import QtQuick 2.15
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.4

TextField {
    id: root
    placeholderText: "종목명 or 종목코드"
    textColor: 'black'

    property var stockListView

    signal returnPressed()

    style: TextFieldStyle {
        background: Rectangle {
            radius: 2
            color: 'lightgray'
            border.color: 'black'
            border.width: 1
        }
    }
    Keys.onUpPressed: {
        console.log("onUpPressed")
        if (typeof(stockListView) === 'undefined') {
            return
        }
        if (stockListView.currentIndex > 0) {
            --stockListView.currentIndex
        }
        console.log(stockListView.currentIndex)
    }

    Keys.onDownPressed: {
        console.log("onDownPressed");
        if (typeof(stockListView) === 'undefined') {
            return
        }
        if (stockListView.currentIndex < stockListView.model.length - 1) {
            ++stockListView.currentIndex
        }
        console.log(stockListView.currentIndex)
    }
    Keys.onReturnPressed: {
        console.log("onReturnPressed")
        if (typeof(stockListView) === 'undefined') {
            return
        }
        root.returnPressed()
    }

    TextButton {
        width: 30
        height: 30
        anchors.right: parent.right
        anchors.verticalCenter: parent.verticalCenter
        anchors.rightMargin: 10
        text: "x"
        textSize: 20
        normalColor: 'grey'
        radius: 10
        onBtnClicked: {
            console.log('x button clicked.')
            root.text = ''
        }
    }
}