import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Controls 1.4
import QtQuick.Layouts 1.15
import "./component"
import "../Globals.js" as Globals

ApplicationWindow {
    id: root
    visible: true
    width: fixedWidth
    height: fixedHeight
    //minimumWidth: fixedWidth
    //maximumWidth: fixedWidth
    //minimumHeight: fixedHeight
    //maximumHeight: fixedHeight
    title: "Account"

    property var fixedWidth: 840
    property var fixedHeight: 300

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
        }
    }

    TabView {
        id: tabView
        anchors.top: accountComboBox.bottom
        anchors.topMargin: 10
        width: parent.width
        height: parent.height - accountComboBox.height - 20

        Tab {
            title: "잔고"

            Item {
                GridView {
                    id: accountInfoGridView
                    width: tabView.width
                    height: contentHeight
                    cellWidth: 100
                    cellHeight: 50
                    model: accountViewModel.currentAccountInfo

                    delegate: Column {
                        width: accountInfoGridView.cellWidth
                        Rectangle {
                            anchors.horizontalCenter: parent.horizontalCenter
                            width: parent.width - 1
                            height: 25
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
                            height: 25
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
                    id: accountRemainsTableView
                    anchors.top: accountInfoGridView.bottom
                    anchors.topMargin: 10
                    width: accountInfoGridView.width
                    height: 120

                    model: accountViewModel.currentAccountStockInfo

                    property var cellWidth: 100

                    TableViewColumn {
                        role: "name"; title: "종목명"; width: accountRemainsTableView.cellWidth
                    }
                    TableViewColumn {
                        role: "currentPrice"; title: "현재가"; width: accountRemainsTableView.cellWidth
                        delegate: Text {
                            text: Globals.formatStringPrice(styleData.value)
                            horizontalAlignment: Text.AlignRight
                            rightPadding: 10
                        }
                    }
                    TableViewColumn {
                        role: "buyPrice"; title: "평균단가"; width: accountRemainsTableView.cellWidth
                        delegate: Text {
                            text: Globals.formatStringPrice(styleData.value)
                            horizontalAlignment: Text.AlignRight
                            rightPadding: 10
                        }
                    }
                    TableViewColumn {
                        role: "profitRate"; title: "손익율"; width: accountRemainsTableView.cellWidth
                        delegate: Text {
                            text: Globals.formatStringProfitRatio(styleData.value, 4)
                            horizontalAlignment: Text.AlignRight
                            rightPadding: 10
                        }
                    }
                    TableViewColumn {
                        role: "profit"; title: "손익금액"; width: accountRemainsTableView.cellWidth
                        delegate: Text {
                            text: Globals.formatStringSignedPrice(styleData.value)
                            horizontalAlignment: Text.AlignRight
                             rightPadding: 10
                        }
                    }
                    TableViewColumn {
                        role: "count"; title: "보유수량"; width: accountRemainsTableView.cellWidth
                        delegate: Text {
                            text: Globals.formatStringPrice(styleData.value)
                            horizontalAlignment: Text.AlignRight
                             rightPadding: 10
                        }
                    }
                    TableViewColumn {
                        role: "currentValue"; title: "평가금액"; width: accountRemainsTableView.cellWidth
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
        }

        Tab {
            title: "미체결"
            Item {
                TableView {
                    id: accountMichegyeolOrderTableView
                    width: tabView.width
                    height: parent.height

                    model: accountViewModel.currentMichegyeolOrderModel

                    property var cellWidth: 100

                    TableViewColumn {
                        role: "stockName"; title: "종목명"; width: accountMichegyeolOrderTableView.cellWidth
                    }
                    TableViewColumn {
                        role: "orderNumber"; title: "주문번호"; width: accountMichegyeolOrderTableView.cellWidth
                    }
                    TableViewColumn {
                        role: "hogaGubun"; title: "매매구분"; width: accountMichegyeolOrderTableView.cellWidth
                    }
                    TableViewColumn {
                        role: "orderQuantity"; title: "주문수량"; width: accountMichegyeolOrderTableView.cellWidth
                        delegate: Text {
                            text: Globals.formatStringSignedPrice(styleData.value)
                            horizontalAlignment: Text.AlignRight
                            rightPadding: 10
                        }
                    }
                    TableViewColumn {
                        role: "orderPrice"; title: "주문가격"; width: accountMichegyeolOrderTableView.cellWidth
                        delegate: Text {
                            text: Globals.formatStringSignedPrice(styleData.value)
                            horizontalAlignment: Text.AlignRight
                             rightPadding: 10
                        }
                    }
                    TableViewColumn {
                        role: "count"; title: "보유수량"; width: accountMichegyeolOrderTableView.cellWidth
                        delegate: Text {
                            text: Globals.formatStringPrice(styleData.value)
                            horizontalAlignment: Text.AlignRight
                             rightPadding: 10
                        }
                    }
                    TableViewColumn {
                        role: "orderType"; title: "주문구분"; width: accountMichegyeolOrderTableView.cellWidth
                        delegate: Text {
                            text: Globals.formatStringPrice(styleData.value)
                            horizontalAlignment: Text.AlignRight
                            rightPadding: 10
                        }
                    }
                    TableViewColumn {
                        role: "michegyeolQuantity"; title: "미체결수량"; width: accountMichegyeolOrderTableView.cellWidth
                        delegate: Text {
                            text: Globals.formatStringPrice(styleData.value)
                            horizontalAlignment: Text.AlignRight
                            rightPadding: 10
                        }
                    }

                    onModelChanged: {
                        console.log("accountViewModel.currentMichegyeolOrderModel changed!!!!!!!!")
                        console.log(model)
                    }
                }
            }
            /*Rectangle {
                color: "lightblue"
                width: parent.width
                height: parent.height
                Text {
                    text: "Content of Tab 2"
                    anchors.centerIn: parent
                }
            }*/
        }
    }
}
