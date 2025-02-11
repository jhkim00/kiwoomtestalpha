import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Controls 1.4
import QtQuick.Layouts 1.15
import "./component"

ApplicationWindow {
    visible: true
    x: 0
    y: 0
    width: fixedWidth
    height: fixedHeight
    minimumWidth: fixedWidth
    maximumWidth: fixedWidth
    minimumHeight: fixedHeight
    maximumHeight: fixedHeight
    title: "Account"

    property var fixedWidth: 840
    property var fixedHeight: 480

    Component.onCompleted: {
        console.log("account component completed")
        accountViewModel.login_info()
    }

    ComboBox {
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
        y: 60
        width: parent.width
        height: 100
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
                    text: modelData[1]
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
        height: 200

        model: accountViewModel.currentAccountStockInfo

        TableViewColumn {
            role: "name"; title: "종목명"; width: 120
        }
        TableViewColumn {
            role: "currentPrice"; title: "현재가"; width: 120
        }
        TableViewColumn {
            role: "buyPrice"; title: "평균단가"; width: 120
        }
        TableViewColumn {
            role: "profitRate"; title: "손익율"; width: 120
        }
        TableViewColumn {
            role: "profit"; title: "손익금액"; width: 120
        }
        TableViewColumn {
            role: "count"; title: "보유수량"; width: 120
        }
        TableViewColumn {
            role: "currentValue"; title: "평가금액"; width: 120
        }

        onModelChanged: {
            console.log("accountViewModel.currentAccountStockInfo changed!!!!!!!!")
            console.log(model)
        }
    }
}
