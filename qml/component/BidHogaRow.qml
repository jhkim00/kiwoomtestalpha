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
        width: volumeBar.width
        height: rowHeight
    }
    PriceRect {
        id: rectPrice
        width: root.width / 3
        height: rowHeight
        textColor: Globals.getPriceTextColor(hogaProvider.bidPriceList[9- rowIndex])
        text: Globals.formatStringPrice(hogaProvider.bidPriceList[9- rowIndex], true)

        property var intPrice: parseInt(hogaProvider.bidPriceList[9- rowIndex])
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
        id: volumeBar
        width: (root.width - rectPrice.width) / 2
        height: rowHeight

        VolumeRect {
            id: rectVolume
            width: parent.width / 2
            height: rowHeight
            text: hogaProvider.bidVolumeList[9- rowIndex]
        }
        VolumeRect {
            id: rectVolumeChange
            width: parent.width / 2
            height: rowHeight
            anchors.left: rectVolume.right
            textColor: Globals.getPriceTextColor(hogaProvider.bidVolumeChangeList[9- rowIndex])
            text: Globals.formatStringPrice(hogaProvider.bidVolumeChangeList[9- rowIndex], false)
        }
        Rectangle {
            anchors.left: parent.left
            width: parent.width * hogaProvider.bidVolumeRatioList[9- rowIndex]
            height: rowHeight
            color: 'red'
            opacity: 0.5
        }
    }
}