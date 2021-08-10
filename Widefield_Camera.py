from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import sys
import PySpin
import pyqtgraph as pg
import os
import serial
import tables
import matlab.engine
import time


pg.setConfigOptions(imageAxisOrder='row-major')

save_base_directory = "M:\\Widefield_Imaging\\"
save_full_directory = save_base_directory

led_1_directory = save_full_directory + "LED_1\\"
led_2_directory = save_full_directory + "LED_2\\"

image_height = 600
image_width  = 608


def setup_camera():
    global system
    global nodemap

    #Run Matlab Setup Script
    matlab_engine = matlab.engine.start_matlab()
    matlab_engine.cam_setup(nargout=0)
    time.sleep(4)
    matlab_engine.quit()

    system = PySpin.System.GetInstance()

    cam_list = system.GetCameras()
    camera = cam_list[0]
    camera.Init()

    nodemap = camera.GetNodeMap()
    sNodemap = camera.GetTLStreamNodeMap()

    node_bufferhandling_mode = PySpin.CEnumerationPtr(sNodemap.GetNode('StreamBufferHandlingMode'))
    node_newestonly = node_bufferhandling_mode.GetEntryByName('OldestFirst')
    node_newestonly_mode = node_newestonly.GetValue()
    node_bufferhandling_mode.SetIntValue(node_newestonly_mode)

    disable_triggers()

    # Set acquisition mode to continuous
    camera.AcquisitionMode.SetValue(PySpin.AcquisitionMode_Continuous)

    # Set Camera Frame Rate


    #Set The Camera Exposure Time
    camera.ExposureAuto.SetValue(PySpin.ExposureAuto_Off)
    camera.ExposureTime.SetValue(10572)


    #Set Resolutionse
    camera.Width.SetValue(image_width) #960
    camera.Height.SetValue(image_height) #600
    camera.OffsetX.SetValue(176)
    camera.OffsetY.SetValue(0)

    #Set Gain
    camera.GainAuto.SetValue(PySpin.GainAuto_Off)
    camera.Gain.SetValue(12)

    #Set File Format
    #camera.PixelFormat.SetValue(PySpin.PixelFormat_Mono16)

    return camera


def set_trigger_mode():
    node_trigger_mode = PySpin.CEnumerationPtr(nodemap.GetNode('TriggerMode'))
    node_trigger_mode_on = node_trigger_mode.GetEntryByName('On')
    node_trigger_mode.SetIntValue(node_trigger_mode_on.GetValue())

    node_trigger_source = PySpin.CEnumerationPtr(nodemap.GetNode('TriggerSource'))
    node_trigger_source_hardware = node_trigger_source.GetEntryByName('Line0')
    node_trigger_source.SetIntValue(node_trigger_source_hardware.GetValue())

    node_trigger_edge = PySpin.CEnumerationPtr(nodemap.GetNode('TriggerActivation'))
    node_trigger_edge_rising = node_trigger_edge.GetEntryByName('RisingEdge')
    node_trigger_edge.SetIntValue(node_trigger_edge_rising.GetValue())


def disable_triggers():
    node_trigger_mode = PySpin.CEnumerationPtr(nodemap.GetNode('TriggerMode'))
    node_trigger_mode_on = node_trigger_mode.GetEntryByName('Off')
    node_trigger_mode.SetIntValue(node_trigger_mode_on.GetValue())




class intrinsic_imaging_window(QWidget):

    def __init__(self, camera, parent=None):
        super(intrinsic_imaging_window, self).__init__(parent)

        #Setup Window
        self.setWindowTitle("Field Mouse")
        self.setGeometry(0,0,875,500)
        self.logo_directory = "C:\\Users\\KhanLab\\Pictures\\PyField_Logo.ico"
        self.setWindowIcon(QIcon(self.logo_directory))

        #Initialise Variables
        self.previewing = False
        self.recording = False
        self.mouse_set = False
        self.frame_index = 0
        self.mouse_name = "Lord Whiskers Of Squeeksbury"
        self.save_directory = save_base_directory
        self.save_base_directory = save_base_directory
        self.ser = serial.Serial("COM3", 9600)

        #Create Mouse Name Field
        self.mouse_name_input = QLineEdit("Mouse Name and Title")
        self.mouse_name_input.setMaximumWidth(450)

        self.save_directory_label = QLabel(save_full_directory)

        self.set_mouse_button = QPushButton("Set Mouse")
        #self.set_mouse_button.setMaximumWidth(100)
        self.set_mouse_button.clicked.connect(self.set_mouse)

        # Create Display Image View
        self.led_1_widget = pg.GraphicsLayoutWidget()
        self.led_1_viewbox = self.led_1_widget.addViewBox(invertY=False)
        self.led_1_image = pg.ImageItem()
        self.led_1_viewbox.addItem(self.led_1_image)
        self.led_1_viewbox.setAspectLocked(True)
        self.led_1_viewbox.setRange(xRange=[0, image_width], yRange=[0, image_height], padding=0)
        self.led_1_widget.ci.layout.setContentsMargins(0,0,0,0)
        self.led_1_widget.ci.layout.setSpacing(0)

        self.led_2_widget = pg.GraphicsLayoutWidget()
        self.led_2_viewbox = self.led_2_widget.addViewBox(invertY=False)
        self.led_2_image = pg.ImageItem()
        self.led_2_viewbox.addItem(self.led_2_image)
        self.led_2_viewbox.setAspectLocked(True)
        self.led_2_viewbox.setRange(xRange=[0, image_width], yRange=[0, image_height], padding=0)
        self.led_2_widget.ci.layout.setContentsMargins(0,0,0,0)
        self.led_2_widget.ci.layout.setSpacing(0)

        #Create Preview Button
        self.preview_button = QPushButton("Preview")
        self.preview_button.clicked.connect(self.preview)

        #Create Record Button
        self.record_button = QPushButton("Start Recording")
        self.record_button.clicked.connect(self.record)
        self.record_button.setDisabled(True)

        #Create Camera Info Button
        self.info_label = QLabel("")
        self.info_label.setMaximumWidth(100)


        #Create Gain Spinbox
        self.gain_spinner = QDoubleSpinBox()
        self.gain_spinner.setMaximum(28)
        self.gain_label = QLabel("Gain: ")
        self.gain_spinner.setValue(12)
        self.gain_spinner.valueChanged.connect(self.gain_changed)
        self.gain_spinner.setSingleStep(0.1)

        self.x_offset_spinner = QSpinBox()
        self.x_offset_spinner.setSingleStep(4)
        self.x_offset_spinner.setMaximum(352)
        self.x_offset_spinner.setValue(176)
        self.x_offset_spinner.valueChanged.connect(self.x_offset_changed)


        #Add Widgets To Layout
        self.main_layout = QGridLayout()
        self.main_layout.addWidget(self.mouse_name_input,       0, 0, 1, 1)
        self.main_layout.addWidget(self.set_mouse_button,       0, 1, 1, 1)
        self.main_layout.addWidget(self.save_directory_label,   1, 0, 1, 2)
        self.main_layout.addWidget(self.led_1_widget,           2, 0, 1, 1)
        self.main_layout.addWidget(self.led_2_widget,           2, 1, 1, 1)
        self.main_layout.addWidget(self.preview_button,         3, 0, 1, 2)
        self.main_layout.addWidget(self.record_button,          4, 0, 1, 2)

        self.main_layout.addWidget(self.gain_label,             2, 2, 1, 1)
        self.main_layout.addWidget(self.gain_spinner,           2, 3, 1, 1)
        self.main_layout.addWidget(self.x_offset_spinner,       3, 3, 1, 1)


        self.setLayout(self.main_layout)

    def x_offset_changed(self):
        offset = self.x_offset_spinner.value()
        print("x offset", offset)
        camera.OffsetX.SetValue(offset)

    def y_offset_changed(self):
        offset = self.y_offset_spinner.value()
        print("y offset", offset)
        camera.OffsetY.SetValue(offset)

    def height_changed(self):
        height = self.height_spinner.value()
        print("height", height)
        camera.Height.SetValue(height)

    def width_changed(self):
        width = self.width_spinner.value()
        print("width", width)
        camera.Width.SetValue(width)


    def gain_changed(self):
        gain = self.gain_spinner.value()
        print("Gain", gain)
        camera.Gain.SetValue(gain)

    def display_mouse_name_error(self):
        warning_message = QMessageBox()
        warning_message.setText("Please Set Mouse Name")
        warning_message.setWindowTitle(" :( ")
        warning_message.setWindowTitle(" :( ")
        warning_message.exec()


    def set_mouse(self):
        print("Setting Mouse")

        self.mouse_name = self.mouse_name_input.text()

        if self.mouse_name == "Mouse Name and Title":
            self.display_mouse_name_error()

        else:

            #Is This A Brand New Mouse?
            if not os.path.isdir(self.save_base_directory + self.mouse_name):
                print("Brand new Mouse!")
                print("Making direcotry ", save_base_directory + self.mouse_name)
                os.mkdir(save_base_directory + self.mouse_name)


                self.save_directory = self.save_base_directory + self.mouse_name + "\\" + str(1) + "\\"
                print("Save Directory", self.save_directory)
                os.mkdir(self.save_directory)

            # Mouse Has Been Imaged Before - What Number Session Is This?
            else:
                looking_for_directory = True
                session_number = 1
                while looking_for_directory == True:
                    self.save_directory = self.save_base_directory + self.mouse_name + "\\" + str(session_number) + "\\"
                    if os.path.isdir(self.save_directory):
                        session_number += 1
                    else:
                        looking_for_directory = False

            self.save_directory_label.setText(self.save_directory)
            self.mouse_set = True
            self.record_button.setDisabled(False)


    def preview_images(self, camera):

        #Make Sure We Are Not Already Recording
        try:
            camera.EndAcquisition()
        except:
            pass


        #Preview Images

        frame_count = 0
        current_led = 1
        camera.BeginAcquisition()
        print("beginning ")


        while self.previewing == True:

            image_result = camera.GetNextImage()
            if image_result.IsIncomplete():
                pass

            else:
                image_data = image_result.GetNDArray()

                if current_led == 1:
                    #print(np.max(image_data))
                    window_instance.led_1_image.setImage(image_data, autoLevels=False, levels=(0, 65536))
                    current_led = 2
                else:
                    window_instance.led_2_image.setImage(image_data, autoLevels=False, levels=(0, 65536))
                    current_led = 1


                image_result.Release()
            print(frame_count)
            frame_count += 1
            app.processEvents()


    def save_image_with_timeout(self, camera, blue_storage, violet_storage):
        try:
            image_result = camera.GetNextImage(2)

            if image_result.IsIncomplete():
                pass
            else:
                image_data = image_result.GetNDArray()
                if self.frame_index % 2 == 0:
                    blue_storage.append([image_data])
                    window_instance.led_1_image.setImage(image_data, autoLevels=False, levels=(0, 65536))

                else:
                    violet_storage.append([image_data])
                    window_instance.led_2_image.setImage(image_data, autoLevels=False, levels=(0, 65536))
                    storage_file.flush()
                    app.processEvents()

                image_result.Release()

                self.frame_index += 1

        except:
            return 2


    def record_images(self, camera):

        number_of_frames_to_capture = 1080002

        #Get Current Timestamp
        timestamp = time.strftime("%Y%m%d-%H%M%S")

        print("Recording! ")
        dimensions = (0, 600, 608)
        storage_path = self.save_directory + self.mouse_name + "_" + timestamp + "_widefield.h5"
        print("Storage path", storage_path)
        storage_file = tables.open_file(storage_path, mode='w')

        print("Storage file", storage_path)
        blue_storage   = storage_file.create_earray(storage_file.root, 'blue', tables.UInt16Atom(), shape=dimensions,  expectedrows=number_of_frames_to_capture/2)
        violet_storage = storage_file.create_earray(storage_file.root, 'violet', tables.UInt16Atom(), shape=dimensions,  expectedrows=number_of_frames_to_capture/2)

        print("Starting acqusition")

        camera.BeginAcquisition()

        #Capture Frames
        frame_index = 0
        self.frame_index = 0

        while self.recording == True:
            image_result = camera.GetNextImage()

            if image_result.IsIncomplete():
               pass

            else:
                image_data = image_result.GetNDArray()

                if frame_index % 2 == 0:
                    blue_storage.append([image_data])
                    window_instance.led_1_image.setImage(image_data, autoLevels=False, levels=(0, 65536))

                else:
                    violet_storage.append([image_data])
                    window_instance.led_2_image.setImage(image_data, autoLevels=False, levels=(0, 65536))
                    storage_file.flush()
                    app.processEvents()


                image_result.Release()

                frame_index += 1

        self.frame_index = frame_index
        #Send Stop Signal
        print("Sending stop signal", b"4")
        self.ser.write(b"4")

        #Wait For Confirmation Teensy Stopped
        print("Waiting for message: ")
        message = self.ser.readline()
        print("Message", message)

        if message == b'Thats the last frame captin!\n':
            print("Okay were done!")

        #Capture last few Frames
            buffer_empty = False
            while buffer_empty == False:
                result = self.save_image_with_timeout(camera, blue_storage, violet_storage)
                if result == 2:
                    buffer_empty = True

        #Shut Down Recording
        camera.EndAcquisition()
        self.record_button.setText("Record")
        self.recording = False
        storage_file.close()
        print("Finished recording")


    def preview(self):

        global storage_file

        if self.previewing == True:
            print("Stopping Preview")
            self.previewing = False
            camera.EndAcquisition()
            print("sending 1")
            self.ser.write(b"1")
            self.preview_button.setText("Preview")

            if self.mouse_set == True:
                self.record_button.setDisabled(False)

        else:
            print("Previewing")
            self.previewing = True
            self.preview_button.setText("Stop Previewing")
            self.record_button.setDisabled(True)

            set_trigger_mode()
            self.ser.write(b"2")
            self.preview_images(camera)


    def record(self):
        global recording
        global storage_file

        if self.recording == True:
            self.recording = False

        else:
            self.recording = True
            set_trigger_mode()
            self.ser.write(b"2")
            self.record_button.setText("Stop Recording")

            self.record_images(camera)




if __name__ == '__main__':
    app = QApplication(sys.argv)

    print("Setting up camera")
    camera = setup_camera()

    print("Creating Window")
    window_instance = intrinsic_imaging_window(camera)
    window_instance.show()


    sys.exit(app.exec_())


