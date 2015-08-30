import QtQuick 2.0
import QtQuick.Controls 1.1
import QtQuick.Layouts 1.1

Item {
    id: container
    width: 1920
    height: 1080

    property var traceData

    function newData(data) {
        traceData = data
        canvas.requestPaint()
    }

    ColumnLayout {
        spacing:5
        anchors.fill: parent
        anchors.topMargin: 12

        Text {
            font.pointSize: 24
            font.bold: true
            text: "Hantek 6022BE"
            anchors.horizontalCenter: parent.horizontalCenter
            color: "#777"
        }

        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Canvas {
                id:canvas
                Layout.fillWidth: true
                Layout.fillHeight: true
                onScaleChanged:requestPaint();

                onPaint: {
                    var ctx = canvas.getContext('2d');
                    ctx.save();
                    ctx.clearRect(0, 0, canvas.width, canvas.height);

                    ctx.beginPath();
                    var max = container.traceData.length
                    var xf = canvas.width / max
                    var x = 0
                    var yf = canvas.height / 256.0
                    for (var x=0; x < max; x++) {
                        ctx.lineTo(x * xf, container.traceData[x] * yf);
                    }
                    ctx.stroke();

                    ctx.restore();
                }
            }

            ColumnLayout {
                Button {
                    text: "Exit"
                }
            }
        }
    }
}
