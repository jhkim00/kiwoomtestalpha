import QtQuick 2.15
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.4
import QtQuick.Layouts 1.15
import "../../Globals.js" as Globals

Rectangle {
    id: root
    border.color: 'black'
    border.width: 1

    property bool simpleVersion: false
    property real fontSize: 12

    RowLayout {
        id: layout
        x: 120
        width: parent.width - x
        height: parent.height

        Item {
            Layout.fillWidth: true
            Layout.preferredWidth: 20
            height: parent.height
        }
        TextLabelLayout {
            height: parent.height
            Layout.preferredWidth: 80
            text: '현재가'
            fontSize: root.fontSize
        }
        TextLabelLayout {
            height: parent.height
            Layout.preferredWidth: 40
        }
        TextLabelLayout {
            Layout.preferredWidth: 80
            text: '등락률'
            fontSize: root.fontSize
        }
        TextLabelLayout {
            height: parent.height
            Layout.preferredWidth: 80
            text: '시가'
            fontSize: root.fontSize
        }
        TextLabelLayout {
            height: parent.height
            Layout.preferredWidth: 80
            text: '고가'
            fontSize: root.fontSize
        }
        TextLabelLayout {
            height: parent.height
            Layout.preferredWidth: 80
            text: '저가'
            fontSize: root.fontSize
        }
        TextLabelLayout {
            height: parent.height
            Layout.preferredWidth: 80
            text: '기준가'
            fontSize: root.fontSize
        }
        TextLabelLayout {
            height: parent.height
            Layout.preferredWidth: 80
            text: '전일대비'
            fontSize: root.fontSize
        }
        TextLabelLayout {
            height: parent.height
            text: '거래량'
            fontSize: root.fontSize
        }
        TextLabelLayout {
            height: parent.height
            text: '거래대비'
            fontSize: root.fontSize
        }
        TextLabelLayout {
            height: parent.height
            text: '거래대금'
            fontSize: root.fontSize
        }
    }
}