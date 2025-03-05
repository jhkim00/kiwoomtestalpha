import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "./component"
import "../Globals.js" as Globals

ApplicationWindow {
    id: root
    visible: true
    x: 0
    y: 0
    width: fixedWidth
    height: fixedHeight
    minimumWidth: fixedWidth
    maximumWidth: fixedWidth
    minimumHeight: fixedHeight
    maximumHeight: fixedHeight
    title: "Order"

    property var fixedWidth: 240
    property var fixedHeight: 480

    function getHogaSizeByPrice(price) {
        if (price < 1000) {
            return 1
        }
        if (price >= 1000 && price < 5000) {
            return 5
        }
        if (price >= 5000 && price < 10000) {
            return 10
        }
        if (price >= 10000 && price < 50000) {
            return 50
        }
        if (price >= 50000 && price < 100000) {
            return 100
        }
        if (price >= 100000 && price < 500000) {
            return 500
        }
        return 1000
    }

    ColumnLayout {
        id: columnLayout
        width: parent.width - 100
        y: 10
        spacing: 10

        property var childWidth: 100
        property var childHeight: 30

        TextLabelLayout {
            Layout.fillWidth: true
            Layout.preferredWidth: columnLayout.childWidth
            Layout.preferredHeight: columnLayout.childHeight
            text: marketViewModel.currentStock['name']
        }

        ComboBox {
            id: oderTypeComboBox
            Layout.fillWidth: true
            Layout.preferredWidth: columnLayout.childWidth
            Layout.preferredHeight: columnLayout.childHeight

            model: ['신규매수', '신규매도', '매수취소', '매수정정', '매도정정']

            onCurrentIndexChanged: {
                console.log("order type combobox onCurrentIndexChanged %1".arg(currentText))
                tradeViewModel.orderType = currentIndex + 1
            }
        }

        ComboBox {
            id: hogaTypeComboBox
            Layout.fillWidth: true
            Layout.preferredWidth: columnLayout.childWidth
            Layout.preferredHeight: columnLayout.childHeight
            model: ['지정가', '시장가']

            onCurrentIndexChanged: {
                console.log("hoga type combobox onCurrentIndexChanged %1".arg(currentText))
                tradeViewModel.hogaType = currentIndex === 0 ? 0 : 3
            }
        }

        SpinBox {
            id: priceInput
            Layout.fillWidth: true
            Layout.preferredWidth: columnLayout.childWidth
            Layout.preferredHeight: columnLayout.childHeight

            editable: true
            from: 0          // 최소값
            to: 1000000          // 최대값
            value: Math.abs(Number(marketViewModel.priceInfo['현재가']))         // 초기값
            stepSize: root.getHogaSizeByPrice(value)      // 증감 단위 (기본값은 1)
        }

        SpinBox {
            id: quantityInput
            Layout.fillWidth: true
            Layout.preferredWidth: columnLayout.childWidth
            Layout.preferredHeight: columnLayout.childHeight

            editable: true
            from: 0          // 최소값
            to: 1000000          // 최대값
            value: 0         // 초기값
            stepSize: 1
        }
    }
}