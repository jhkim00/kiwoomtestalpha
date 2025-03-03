import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Controls 1.4
import QtQuick.Layouts 1.15
import "./component"
import "../Globals.js" as Globals

ApplicationWindow {
    visible: true
    width: fixedWidth
    height: fixedHeight
    minimumWidth: fixedWidth
    maximumWidth: fixedWidth
    minimumHeight: fixedHeight
    maximumHeight: fixedHeight
    title: "Account"

    property var fixedWidth: 840
    property var fixedHeight: 240

    Component.onCompleted: {
        console.trace()
    }

    onVisibleChanged: {
        console.trace()
        if (visible) {
            accountViewModel.login_info()
        }
    }

    ComboBox {
        id: accountComboBox
        width: 200
        y: 10
        model: accountViewModel.accountList

        onCurrentTextChanged: {
            console.log("account combobox onCurrentTextChanged")
            accountViewModel.currentAccount = currentText
            accountViewModel.account_info()
        }
    }

    GridView {
        id: accountInfoGridView
        anchors.top: accountComboBox.bottom
        anchors.topMargin: 10
        width: parent.width
        height: 50
        cellWidth: 120
        cellHeight: 50
        model: accountViewModel.currentAccountInfo

        delegate: Column {
            width: 120
            spacing: 1
            Rectangle {
                anchors.horizontalCenter: parent.horizontalCenter
                width: parent.width - 1
                height: 24
                border.width: 1
                color: "lightgrey"
                Text {
                    text: modelData[0]
                    anchors.fill: parent
                    verticalAlignment: Text.AlignVCenter
                    horizontalAlignment: Text.AlignHCenter
                }
            }
            Rectangle {
                anchors.horizontalCenter: parent.horizontalCenter
                width: parent.width - 1
                height: 24
                border.width: 1
                Text {
                    text: Globals.formatStringPrice(modelData[1])
                    anchors.fill: parent
                    verticalAlignment: Text.AlignVCenter
                    horizontalAlignment: Text.AlignHCenter
                }
            }
        }

        onModelChanged: {
            console.log("model changed")
            console.log(model)
        }
    }

    TableView {
        anchors.top: accountInfoGridView.bottom
        anchors.topMargin: 10
        width: parent.width
        height: 120

        model: accountViewModel.currentAccountStockInfo

        TableViewColumn {
            role: "name"; title: "종목명"; width: 120
        }
        TableViewColumn {
            role: "currentPrice"; title: "현재가"; width: 120
            delegate: Text {
                text: Globals.formatStringPrice(styleData.value)
                horizontalAlignment: Text.AlignRight
                rightPadding: 10
            }
        }
        TableViewColumn {
            role: "buyPrice"; title: "평균단가"; width: 120
            delegate: Text {
                text: Globals.formatStringPrice(styleData.value)
                horizontalAlignment: Text.AlignRight
                rightPadding: 10
            }
        }
        TableViewColumn {
            role: "profitRate"; title: "손익율"; width: 120
            delegate: Text {
                text: Globals.formatStringProfitRatio(styleData.value, 4)
                horizontalAlignment: Text.AlignRight
                rightPadding: 10
            }
        }
        TableViewColumn {
            role: "profit"; title: "손익금액"; width: 120
            delegate: Text {
                text: Globals.formatStringSignedPrice(styleData.value)
                horizontalAlignment: Text.AlignRight
                 rightPadding: 10
            }
        }
        TableViewColumn {
            role: "count"; title: "보유수량"; width: 120
            delegate: Text {
                text: Globals.formatStringPrice(styleData.value)
                horizontalAlignment: Text.AlignRight
                 rightPadding: 10
            }
        }
        TableViewColumn {
            role: "currentValue"; title: "평가금액"; width: 120
            delegate: Text {
                text: Globals.formatStringPrice(styleData.value)
                horizontalAlignment: Text.AlignRight
                rightPadding: 10
            }
        }

        onModelChanged: {
            console.log("accountViewModel.currentAccountStockInfo changed!!!!!!!!")
            console.log(model)
        }
    }
}
