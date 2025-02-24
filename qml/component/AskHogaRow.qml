import QtQuick 2.15
import QtQuick.Controls 2.15
import "../../Globals.js" as Globals

Row {
    id: root
    property var hogaProvider
    property var chegyeolProvider
    property var rowIndex
    property var rowHeight

    Item {
        id: volumeBar
        width: (root.width - rectPrice.width) / 2
        height: rowHeight

        VolumeRect {
            id: rectVolumeChange
            width: parent.width / 2
            height: rowHeight
            textColor: Globals.getPriceTextColor(hogaProvider.askVolumeChangeList[rowIndex])
            text: Globals.formatStringPrice(hogaProvider.askVolumeChangeList[rowIndex], false)
        }
        VolumeRect {
            id: rectVolume
            width: parent.width / 2
            height: rowHeight
            anchors.left: rectVolumeChange.right
            text: hogaProvider.askVolumeList[rowIndex]
        }
        Rectangle {
            anchors.right: parent.right
            width: parent.width * hogaProvider.askVolumeRatioList[rowIndex]
            height: rowHeight
            color: 'blue'
            opacity: 0.5
        }
    }
    PriceRect {
        id: rectPrice
        width: root.width / 3
        height: rowHeight
        textColor: Globals.getPriceTextColor(hogaProvider.askPriceList[rowIndex])
        text: Globals.formatStringPrice(hogaProvider.askPriceList[rowIndex], true)

        property var intPrice: parseInt(hogaProvider.askPriceList[rowIndex])
        property var intChegyeolPrice: parseInt(chegyeolProvider.currentPrice)
        property var intHighPrice: parseInt(chegyeolProvider.highPrice)
        property var intLowPrice: parseInt(chegyeolProvider.lowPrice)
        property bool isCurrentPrice: intPrice === intChegyeolPrice
        property bool isHighPrice: intPrice === intHighPrice
        property bool isLowPrice: intPrice === intLowPrice

        border.width: isCurrentPrice ? 2 : 1
        border.color: isCurrentPrice ? "red" : "grey"

        Rectangle {
            anchors.fill: parent
            color: parent.isHighPrice ? "red" : (parent.isLowPrice ? "blue" : "white")
            opacity: 0.3
        }
    }
    Item {
        width: volumeBar.width
        height: rowHeight
    }
}