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

    Item {
        id: stockInputItem
        y: 10
        z: 1
        width: parent.width
        height: root.height - y - 36

        StockInputField {
            id: stockInputField
            width: parent.width
            height: 30

            stockListView: _stockListView

            onReturnPressed: {
                console.log("stockInputField onReturnPressed")
                var stock = stockListView.getCurrentStock()
                if (typeof(stock) === 'undefined') {
                    marketViewModel.showSearchedStockHistory()
                    return
                }
                marketViewModel.setCurrentStock(stock)
            }

            onDisplayTextChanged: {
                console.log('stockInputField onDisplayTextChanged ' + displayText)
                marketViewModel.setInputText(displayText)
            }

            Connections {
                target: marketViewModel
                function onCurrentStockChanged(name, code) {
                    stockInputField.text = name
                }
            }
        }

        StockListView {
            id: _stockListView
            anchors.top: stockInputField.bottom

            anchors.topMargin: 2
            width: stockInputField.width
            height: 400
            model: marketViewModel.searchedStockList
            visible: root.active && model.length > 0
        }
    }

    ColumnLayout {
        id: columnLayout
        y: 50
        width: parent.width
        spacing: 10

        property var childWidth: 100
        property var childHeight: 30

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
            value: 0         // 초기값
            stepSize: root.getHogaSizeByPrice(value)      // 증감 단위 (기본값은 1)

            property bool needUpdatePrice: true

            onValueChanged: {
                tradeViewModel.orderPrice = value
            }

            Connections {
                target: marketViewModel
                function onCurrentStockChanged(name, code) {
                    priceInput.needUpdatePrice = true
                }
                function onPriceInfoChanged() {
                    if (priceInput.needUpdatePrice) {
                        priceInput.value = Math.abs(Number(marketViewModel.priceInfo['현재가']))
                        priceInput.needUpdatePrice = false
                    }
                }
            }
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

            onValueChanged: {
                tradeViewModel.orderQuantity = value
            }
        }

        TextButton {
            id: btnBuy
            width: 200
            height: 30
            Layout.alignment: Qt.AlignHCenter
            text: "Buy"
            textSize: 20
            normalColor: 'lightsteelblue'
            radius: 4
            onBtnClicked: {
                console.log('btnBuy clicked')

                tradeViewModel.buy()
            }
        }
    }
}