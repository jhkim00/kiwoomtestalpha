import QtQuick 2.15
import QtQuick.Controls 2.15
import "./component"

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
    title: "kiwoomtestalpha"

    property var fixedWidth: 240
    property var fixedHeight: 480

    property var accountWindow: null
    property var marketWindow: null
    property var conditionWindow: null
    property var logWindow: null
    property var hogaWindow: null
    property var chegyeolWindow: null

    onClosing: {
        console.log("Application is closing")
        if (accountWindow) {
            accountWindow.close()
            accountWindow.destroy()
        }
        if (marketWindow) {
            marketWindow.close()
            marketWindow.destroy()
        }
        if (conditionWindow) {
            conditionWindow.close()
            conditionWindow.destroy()
        }
        if (logWindow) {
            logWindow.close()
            logWindow.destroy()
        }
        if (hogaWindow) {
            hogaWindow.close()
            hogaWindow.destroy()
        }
        if (chegyeolWindow) {
            chegyeolWindow.close()
            chegyeolWindow.destroy()
        }
    }

    Column {
        width: parent.width
        y: 10
        spacing: 10

        TextButton {
            id: btnLogin
            width: 200
            height: 30
            anchors.horizontalCenter: parent.horizontalCenter
            text: "Login"
            textSize: 20
            normalColor: 'lightsteelblue'
            radius: 4
            onBtnClicked: {
                console.trace()
                mainViewModel.login()
            }
        }

        TextButton {
            id: btnOpenAccountInfo
            width: 200
            height: 30
            anchors.horizontalCenter: parent.horizontalCenter
            text: "Account info"
            textSize: 20
            normalColor: 'lightsteelblue'
            radius: 4
            enabled: mainViewModel.login_completed
            onBtnClicked: {
                console.log('btnOpenAccountInfo clicked')
                if (root.accountWindow === null) {
                    var component = Qt.createComponent("Account.qml")
                    if (component.status === Component.Ready) {
                        root.accountWindow = component.createObject()
                    }
                }
                root.accountWindow.show()
            }
        }

        TextButton {
            id: btnOpenCurrentPrice
            width: 200
            height: 30
            anchors.horizontalCenter: parent.horizontalCenter
            text: "Current price"
            textSize: 20
            normalColor: 'lightsteelblue'
            radius: 4
            enabled: mainViewModel.login_completed
            onBtnClicked: {
                console.log('btnOpenCurrentPrice clicked')

                if (root.marketWindow === null) {
                    var component = Qt.createComponent("Market.qml")
                    if (component.status === Component.Ready) {
                        root.marketWindow = component.createObject()
                    }
                }
                root.marketWindow.show()
            }
        }

        TextButton {
            id: btnOpenCondition
            width: 200
            height: 30
            anchors.horizontalCenter: parent.horizontalCenter
            text: "Condition"
            textSize: 20
            normalColor: 'lightsteelblue'
            radius: 4
            enabled: mainViewModel.login_completed
            onBtnClicked: {
                console.log('btnOpenCondition clicked')

                if (root.conditionWindow === null) {
                    var component = Qt.createComponent("Condition.qml")
                    if (component.status === Component.Ready) {
                        root.conditionWindow = component.createObject()
                    }
                }
                root.conditionWindow.show()
            }
        }

        TextButton {
            id: btnOpenChart
            width: 200
            height: 30
            anchors.horizontalCenter: parent.horizontalCenter
            text: "Chart"
            textSize: 20
            normalColor: 'lightsteelblue'
            radius: 4
            enabled: mainViewModel.login_completed
            onBtnClicked: {
                console.log('btnOpenChart clicked')

                chartViewModel.load()
            }
        }

        TextButton {
            id: btnBuy
            width: 200
            height: 30
            anchors.horizontalCenter: parent.horizontalCenter
            text: "Buy"
            textSize: 20
            normalColor: 'lightsteelblue'
            radius: 4
            enabled: mainViewModel.login_completed
            onBtnClicked: {
                console.log('btnBuy clicked')

                tradeViewModel.buy()
            }
        }

        TextButton {
            id: btnSell
            width: 200
            height: 30
            anchors.horizontalCenter: parent.horizontalCenter
            text: "Sell"
            textSize: 20
            normalColor: 'lightsteelblue'
            radius: 4
            enabled: mainViewModel.login_completed
            onBtnClicked: {
                console.log('btnSell clicked')

                tradeViewModel.sell()
            }
        }

        TextButton {
            id: btnLog
            width: 200
            height: 30
            anchors.horizontalCenter: parent.horizontalCenter
            text: "Log"
            textSize: 20
            normalColor: 'lightsteelblue'
            radius: 4
            onBtnClicked: {
                console.log('btnLog clicked')

                if (root.logWindow === null) {
                    var component = Qt.createComponent("Log.qml")
                    if (component.status === Component.Ready) {
                        root.logWindow = component.createObject()
                    }
                }
                root.logWindow.show()
            }
        }

        TextButton {
            id: btnHoga
            width: 200
            height: 30
            anchors.horizontalCenter: parent.horizontalCenter
            text: "Hoga"
            textSize: 20
            normalColor: 'lightsteelblue'
            radius: 4
            onBtnClicked: {
                console.log('btnHoga clicked')

                if (root.hogaWindow === null) {
                    var component = Qt.createComponent("HogaWindow.qml")
                    if (component.status === Component.Ready) {
                        root.hogaWindow = component.createObject()
                    }
                }
                root.hogaWindow.show()
            }
        }

        TextButton {
            id: btnChegyeol
            width: 200
            height: 30
            anchors.horizontalCenter: parent.horizontalCenter
            text: "Chegyeol"
            textSize: 20
            normalColor: 'lightsteelblue'
            radius: 4
            onBtnClicked: {
                console.log('btnChegyeol clicked')

                if (root.chegyeolWindow === null) {
                    var component = Qt.createComponent("Chegyeol.qml")
                    if (component.status === Component.Ready) {
                        root.chegyeolWindow = component.createObject()
                    }
                }
                root.chegyeolWindow.show()
            }
        }
    }
}
