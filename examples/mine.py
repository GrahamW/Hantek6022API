import sys
import math
import time

from PyQt5.QtCore import QObject, QUrl, pyqtSignal, QTimer
from PyQt5.QtWidgets import QApplication
from PyQt5.QtQuick import QQuickView

from PyHT6022.LibUsbScope import Oscilloscope
from collections import deque

class ScopeInterface(QObject):
    new_data = pyqtSignal(list)
    def __init__(self, parent=None):
        super(ScopeInterface, self).__init__(parent)
        self.inprogress = False

    def initialize(self):
        self.sample_rate_index = 0x1E
        self.voltage_range = 0x01
        self.data_points = 3 * 1024

        self.scope = Oscilloscope()
        self.scope.setup()
        self.scope.open_handle()
        if (not self.scope.is_device_firmware_present):
            self.scope.flash_firmware()
        self.scope.set_interface(1); # choose ISO
        self.scope.set_num_channels(1)
        self.scope.set_sample_rate(self.sample_rate_index)
        self.scope.set_ch1_voltage_range(self.voltage_range)
        time.sleep(0.1)
        return None

    def capture(self):
        if not self.inprogress:
            self.inprogress = True
            self.initialize()
            data = list(self.get_data())
            self.new_data.emit(data)
            self.inprogress = False

    def extend_callback(self, ch1_data, _):
        self.data.extend(ch1_data)

    def get_data(self):
        self.data = deque(maxlen=2*1024*1024)

        start_time = time.time()
        shutdown_event = self.scope.read_async(self.extend_callback, self.data_points, outstanding_transfers=25)
        print("Clearing FIFO and starting data transfer...")
        i = 0
        self.scope.start_capture()
        time.sleep(0.001)
        self.scope.stop_capture()
        print("Stopping new transfers.")
        shutdown_event.set()
        print("Snooze 1")
        time.sleep(1)
        print("Closing handle")
        self.scope.close_handle()
        print("Handle closed.")
        print("Points in buffer:", len(self.data))
        return self.data

class Trace(QObject):
    new_data = pyqtSignal(list)

    def __init__(self, parent=None):
        super(Trace, self).__init__(parent)
        self.freq = 1.0

    def get_data(self):
        max = 256
        data = list(map(lambda x: int(127 + 127 * math.sin( 2.0 * math.pi * self.freq * x / max)), range(0,max)))
        self.freq *= 1.01
        self.new_data.emit(data)

# Create the application instance.
app = QApplication(sys.argv)

# Create the QML user interface.
view = QQuickView()
view.setSource(QUrl('test.qml'))
#view.setResizeMode(QDeclarativeView.SizeRootObjectToView)
view.showFullScreen()


scope = ScopeInterface()
scope.new_data.connect(view.rootObject().newData)

timer = QTimer()
timer.timeout.connect(scope.capture)
timer.start(1000)

sys.exit(app.exec_())
