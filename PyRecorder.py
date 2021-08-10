from PyDAQmx import DAQmxTypes, DAQmxConstants, DAQmxFunctions, DAQmxCallBack
import numpy as np
import pyqtgraph as pg
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import sys
import tables
import threading
import time

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

display_buffer = np.zeros((16,5000))

global recording
recording = False

class ai_window(QWidget):

    def __init__(self,parent=None):
        super(ai_window, self).__init__(parent)


        #Setup Window
        self.setWindowTitle("PyI Recorder")
        self.setGeometry(0,0,1000,500)
        self.setStyleSheet("background-color: white;")

        self.save_directory = "M:\\PyRecorder_Data\\"

        # Create Graph Displays
        self.graph_0_widget = pg.PlotWidget()
        self.graph_0_widget.setYRange(0,5)
        self.graph_0_label = QLabel("Photodiode")
        self.graph_0_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        self.graph_1_widget = pg.PlotWidget()
        self.graph_1_widget.setYRange(0,5)
        self.graph_1_label = QLabel("Reward")
        self.graph_1_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        self.graph_2_widget = pg.PlotWidget()
        self.graph_2_widget.setYRange(0,2)
        self.graph_2_label = QLabel("Lick Signal")
        self.graph_2_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        self.graph_3_widget = pg.PlotWidget()
        self.graph_3_widget.setYRange(0,5)
        self.graph_3_label = QLabel("Stimulus 1")
        self.graph_3_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        self.graph_4_widget = pg.PlotWidget()
        self.graph_4_widget.setYRange(0,5)
        self.graph_4_label = QLabel("Stimulus 2")
        self.graph_4_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        self.graph_5_widget = pg.PlotWidget()
        self.graph_5_widget.setYRange(0,5)
        self.graph_5_label = QLabel("Odour 1")
        self.graph_5_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        self.graph_6_widget = pg.PlotWidget()
        self.graph_6_widget.setYRange(0, 5)
        self.graph_6_label = QLabel("Odour 2")
        self.graph_6_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        self.graph_7_widget = pg.PlotWidget()
        self.graph_7_widget.setYRange(0, 1)
        self.graph_7_label = QLabel("Irrelevance")
        self.graph_7_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        self.graph_8_widget = pg.PlotWidget()
        self.graph_8_widget.setYRange(0.4, 1)
        self.graph_8_label = QLabel("Running Speed")
        self.graph_8_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        self.graph_9_widget = pg.PlotWidget()
        self.graph_9_widget.setYRange(0, 5)
        self.graph_9_label = QLabel("Trial End")
        self.graph_9_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        self.graph_10_widget = pg.PlotWidget()
        self.graph_10_widget.setYRange(2, 4)
        self.graph_10_widget.setXRange(0, 1000)
        self.graph_10_label = QLabel("Camera Trigger")
        self.graph_10_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        self.graph_11_widget = pg.PlotWidget()
        self.graph_11_widget.setYRange(2.8, 3.2)
        self.graph_11_widget.setXRange(0, 1000)
        self.graph_11_label = QLabel("Camera Frames")
        self.graph_11_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        self.graph_12_widget = pg.PlotWidget()
        self.graph_12_widget.setYRange(2, 4)
        self.graph_12_widget.setXRange(0, 1000)
        self.graph_12_label = QLabel("LED 1")
        self.graph_12_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        self.graph_13_widget = pg.PlotWidget()
        self.graph_13_widget.setYRange(2, 4)
        self.graph_13_widget.setXRange(0, 1000)
        self.graph_13_label = QLabel("LED 2")
        self.graph_13_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        self.graph_14_widget = pg.PlotWidget()
        self.graph_14_widget.setYRange(4, 6)
        self.graph_14_widget.setXRange(0, 1000)
        self.graph_14_label = QLabel("Mouse Cam")
        self.graph_14_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        self.graph_15_widget = pg.PlotWidget()
        self.graph_15_widget.setYRange(4, 6)
        self.graph_15_widget.setXRange(0, 1000)
        self.graph_15_label = QLabel("Optogenetics")
        self.graph_15_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)


        #Create Start Stop Buttons
        self.recording_state = False
        self.recording_button = QPushButton("Start Recording")
        self.recording_button.clicked.connect(self.toggle_recording)

        #Create Directory Selection Button
        self.directory_selection_button = QPushButton("Select Save Directory")
        self.directory_selection_button.clicked.connect(self.select_save_directory)

        #Create Recording Location Label
        self.save_directory_label = QLabel(str(self.save_directory))
        self.save_directory_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        # Create Timer To Update Display
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_display)
        self.timer.start()

        #Add Widgets To Layout
        self.main_layout = QGridLayout()


        self.main_layout.addWidget(self.graph_0_label,                  0,  0, 1, 2)
        self.main_layout.addWidget(self.graph_0_widget,                  1,  0, 2, 2)

        self.main_layout.addWidget(self.graph_1_label,                  3,  0, 1, 2)
        self.main_layout.addWidget(self.graph_1_widget,                 4,  0, 2, 2)

        self.main_layout.addWidget(self.graph_2_label,                  6,  0, 1, 2)
        self.main_layout.addWidget(self.graph_2_widget,                 7,  0, 2, 2)

        self.main_layout.addWidget(self.graph_3_label,                  9,  0, 1, 2)
        self.main_layout.addWidget(self.graph_3_widget,                 10, 0, 2, 2)

        self.main_layout.addWidget(self.graph_4_label,                  0,  2, 1, 2)
        self.main_layout.addWidget(self.graph_4_widget,                 1,  2, 2, 2)

        self.main_layout.addWidget(self.graph_5_label,                  3,  2, 1, 2)
        self.main_layout.addWidget(self.graph_5_widget,                 4,  2, 2, 2)

        self.main_layout.addWidget(self.graph_6_label,                  6,  2, 1, 2)
        self.main_layout.addWidget(self.graph_6_widget,                 7,  2, 2, 2)

        self.main_layout.addWidget(self.graph_7_label,                  9,  2, 1, 2)
        self.main_layout.addWidget(self.graph_7_widget,                 10, 2, 2, 2)


        self.main_layout.addWidget(self.graph_8_label,                  0,  4, 1, 2)
        self.main_layout.addWidget(self.graph_8_widget,                 1,  4, 2, 2)

        self.main_layout.addWidget(self.graph_9_label,                  3,  4, 1, 2)
        self.main_layout.addWidget(self.graph_9_widget,                 4,  4, 2, 2)

        self.main_layout.addWidget(self.graph_10_label,                 6,  4, 1, 2)
        self.main_layout.addWidget(self.graph_10_widget,                7,  4, 2, 2)

        self.main_layout.addWidget(self.graph_11_label,                 9,  4, 1, 2)
        self.main_layout.addWidget(self.graph_11_widget,                10, 4, 2, 2)


        self.main_layout.addWidget(self.graph_12_label,                 0,  6, 1, 2)
        self.main_layout.addWidget(self.graph_12_widget,                1,  6, 2, 2)

        self.main_layout.addWidget(self.graph_13_label,                 3,  6, 1, 2)
        self.main_layout.addWidget(self.graph_13_widget,                4,  6, 2, 2)

        self.main_layout.addWidget(self.graph_14_label,                 6,  6, 1, 2)
        self.main_layout.addWidget(self.graph_14_widget,                7,  6, 2, 2)

        self.main_layout.addWidget(self.graph_15_label,                 9,  6, 1, 2)
        self.main_layout.addWidget(self.graph_15_widget,                10, 6, 2, 2)


        self.main_layout.addWidget(self.save_directory_label,           12, 0, 1, 2)
        self.main_layout.addWidget(self.recording_button,               13, 0, 1, 2)
        self.main_layout.addWidget(self.directory_selection_button,     14, 0, 1, 2)

        self.setLayout(self.main_layout)

    def toggle_recording(self):

        if self.recording_state == False:
            self.start_recording()
        elif self.recording_state == True:
            self.stop_recording()


    def start_recording(self):
        global recording
        global data_storage
        global storage_file

        self.recording_button.setText("Stop Recording")
        self.recording_state = True



        timestamp = time.strftime("%Y%m%d-%H%M%S")

        storage_path = self.save_directory + "/" + timestamp + ".h5"
        print("Storage Path", storage_path)


        storage_file = tables.open_file(storage_path, mode='w')
        dimensions = (0, 16, 1000)
        data_storage = storage_file.create_earray(storage_file.root, 'Data', tables.Float64Atom(), shape=dimensions)
        recording = True

    def stop_recording(self):
        global recording
        self.recording_state = False
        self.recording_button.setText("Start Recording")
        recording = False
        storage_file.close()

    def select_save_directory(self):
        self.save_directory = QFileDialog.getExistingDirectory()
        self.save_directory_label.setText(str(self.save_directory))

    def update_display(self):
        global display_buffer

        self.graph_0_widget.clear()
        self.graph_0_widget.plot(display_buffer[0], pen=pen)

        self.graph_1_widget.clear()
        self.graph_1_widget.plot(display_buffer[1], pen=pen)

        self.graph_2_widget.clear()
        self.graph_2_widget.plot(display_buffer[2], pen=pen)

        self.graph_3_widget.clear()
        self.graph_3_widget.plot(display_buffer[3], pen=pen)

        self.graph_4_widget.clear()
        self.graph_4_widget.plot(display_buffer[4], pen=pen)

        self.graph_5_widget.clear()
        self.graph_5_widget.plot(display_buffer[5], pen=pen)

        self.graph_6_widget.clear()
        self.graph_6_widget.plot(display_buffer[6], pen=pen)

        self.graph_7_widget.clear()
        self.graph_7_widget.plot(display_buffer[7], pen=pen)

        self.graph_8_widget.clear()
        self.graph_8_widget.plot(display_buffer[8], pen=pen)

        self.graph_9_widget.clear()
        self.graph_9_widget.plot(display_buffer[9], pen=pen)

        self.graph_10_widget.clear()
        self.graph_10_widget.plot(display_buffer[10], pen=pen)

        self.graph_11_widget.clear()
        self.graph_11_widget.plot(display_buffer[11], pen=pen)

        self.graph_12_widget.clear()
        self.graph_12_widget.plot(display_buffer[12], pen=pen)

        self.graph_13_widget.clear()
        self.graph_13_widget.plot(display_buffer[13], pen=pen)

        self.graph_14_widget.clear()
        self.graph_14_widget.plot(display_buffer[14], pen=pen)

        self.graph_15_widget.clear()
        self.graph_15_widget.plot(display_buffer[15], pen=pen)

        app.processEvents()


class MyList(list):
    pass


def EveryNCallback_py(taskHandle, everyNsamplesEventType, nSamples, callbackData_ptr):
    global display_buffer
    global recording

    #callbackdata = DAQmxCallBack.get_callbackdata_from_id(callbackData_ptr)
    read =  DAQmxTypes.int32()                                                                                                                      #Create An Integer Varaible to Store How Many Data Points Have Been Read
    data = np.zeros(16000)                                                                                                                           #Create A Numpy Array To Store The Read Data
    DAQmxFunctions.DAQmxReadAnalogF64(taskHandle,1000,10.0,DAQmxConstants.DAQmx_Val_GroupByChannel,data,16000,DAQmxTypes.byref(read),None)
    #callbac44kdata.extend(data.tolist())


    data = np.reshape(data, (16,1000))
    display_buffer = np.roll(display_buffer, -1000, axis=1)
    display_buffer[:, 4000:] = data
    #display_buffer = display_data

    if recording == True:
        data_storage.append([data])
        data_storage.flush()

    return 0 # The function should return an integer





if __name__ == '__main__':
    app = QApplication(sys.argv)


    x = np.arange(5000)


    window_instance = ai_window()
    window_instance.show()


    # list where the data are stored
    data = MyList()
    id_data = DAQmxCallBack.create_callbackdata_id(data)
    count = 0

    # Convert the python function to a C function callback
    EveryNCallback = DAQmxTypes.DAQmxEveryNSamplesEventCallbackPtr(EveryNCallback_py)

    #Create Task
    taskHandle = DAQmxTypes.TaskHandle(0)                               #Create A Task Handle
    DAQmxFunctions.DAQmxCreateTask("", DAQmxTypes.byref(taskHandle))    #Create A Task Using This Handle

    #Setup Channels
    DAQmxFunctions.DAQmxCreateAIVoltageChan(taskHandle, "Dev1/ai0",  "", DAQmxConstants.DAQmx_Val_RSE, -10.0,   10.0, DAQmxConstants.DAQmx_Val_Volts, None)
    DAQmxFunctions.DAQmxCreateAIVoltageChan(taskHandle, "Dev1/ai1",  "", DAQmxConstants.DAQmx_Val_RSE, -10.0,   10.0, DAQmxConstants.DAQmx_Val_Volts, None)
    DAQmxFunctions.DAQmxCreateAIVoltageChan(taskHandle, "Dev1/ai2",  "", DAQmxConstants.DAQmx_Val_RSE, -10.0,   10.0, DAQmxConstants.DAQmx_Val_Volts, None)
    DAQmxFunctions.DAQmxCreateAIVoltageChan(taskHandle, "Dev1/ai3",  "", DAQmxConstants.DAQmx_Val_RSE, -10.0,   10.0, DAQmxConstants.DAQmx_Val_Volts, None)
    DAQmxFunctions.DAQmxCreateAIVoltageChan(taskHandle, "Dev1/ai4",  "", DAQmxConstants.DAQmx_Val_RSE, -10.0,   10.0, DAQmxConstants.DAQmx_Val_Volts, None)
    DAQmxFunctions.DAQmxCreateAIVoltageChan(taskHandle, "Dev1/ai5",  "", DAQmxConstants.DAQmx_Val_RSE, -10.0,   10.0, DAQmxConstants.DAQmx_Val_Volts, None)
    DAQmxFunctions.DAQmxCreateAIVoltageChan(taskHandle, "Dev1/ai6",  "", DAQmxConstants.DAQmx_Val_RSE, -10.0,   10.0, DAQmxConstants.DAQmx_Val_Volts, None)
    DAQmxFunctions.DAQmxCreateAIVoltageChan(taskHandle, "Dev1/ai7",  "", DAQmxConstants.DAQmx_Val_RSE, -10.0,   10.0, DAQmxConstants.DAQmx_Val_Volts, None)
    DAQmxFunctions.DAQmxCreateAIVoltageChan(taskHandle, "Dev1/ai8",  "", DAQmxConstants.DAQmx_Val_RSE, -10.0,   10.0, DAQmxConstants.DAQmx_Val_Volts, None)
    DAQmxFunctions.DAQmxCreateAIVoltageChan(taskHandle, "Dev1/ai9",  "", DAQmxConstants.DAQmx_Val_RSE, -10.0,   10.0, DAQmxConstants.DAQmx_Val_Volts, None)
    DAQmxFunctions.DAQmxCreateAIVoltageChan(taskHandle, "Dev1/ai10", "", DAQmxConstants.DAQmx_Val_RSE, -10.0,   10.0, DAQmxConstants.DAQmx_Val_Volts, None)
    DAQmxFunctions.DAQmxCreateAIVoltageChan(taskHandle, "Dev1/ai11", "", DAQmxConstants.DAQmx_Val_RSE, -10.0,   10.0, DAQmxConstants.DAQmx_Val_Volts, None)
    DAQmxFunctions.DAQmxCreateAIVoltageChan(taskHandle, "Dev1/ai12", "", DAQmxConstants.DAQmx_Val_RSE, -10.0,   10.0, DAQmxConstants.DAQmx_Val_Volts, None)
    DAQmxFunctions.DAQmxCreateAIVoltageChan(taskHandle, "Dev1/ai13", "", DAQmxConstants.DAQmx_Val_RSE, -10.0,   10.0, DAQmxConstants.DAQmx_Val_Volts, None)
    DAQmxFunctions.DAQmxCreateAIVoltageChan(taskHandle, "Dev1/ai14", "", DAQmxConstants.DAQmx_Val_RSE, -10.0,   10.0, DAQmxConstants.DAQmx_Val_Volts, None)
    DAQmxFunctions.DAQmxCreateAIVoltageChan(taskHandle, "Dev1/ai15", "", DAQmxConstants.DAQmx_Val_RSE, -10.0,   10.0, DAQmxConstants.DAQmx_Val_Volts, None)

    DAQmxFunctions.DAQmxCfgSampClkTiming(taskHandle, "", 1000.0, DAQmxConstants.DAQmx_Val_Rising, DAQmxConstants.DAQmx_Val_ContSamps, 1000)
    #Configure Buffer
    #DAQmxFunctions.DAQmxCfgOutputBuffer(taskHandle, 1000)


    DAQmxFunctions.DAQmxRegisterEveryNSamplesEvent(taskHandle, DAQmxConstants.DAQmx_Val_Acquired_Into_Buffer, 1000, 0, EveryNCallback, id_data)


    pen = pg.mkPen(color=(100, 100, 200), width=2)

    # DAQmx Start Code
    DAQmxFunctions.DAQmxStartTask(taskHandle)





    sys.exit(app.exec_())

