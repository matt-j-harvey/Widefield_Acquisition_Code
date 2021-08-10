import numpy as np
import matplotlib.pyplot as plt
import h5py
import tables
from scipy import signal, ndimage, stats
from sklearn.linear_model import LinearRegression
from skimage.morphology import white_tophat
from PIL import Image
from time import clock
import os
import cv2


def load_arrays(video_file):
    table = tables.open_file(video_file, mode='r')
    blue_array = table.root.blue
    violet_array = table.root.violet

    return blue_array, violet_array


def get_frame_means(array):

    sums = []
    number_of_frames = np.shape(array)[0]
    for frame in range(number_of_frames):
        print(frame)
        sums.append(np.mean(array[frame]))

    return sums

def recreate_frames(array):

    figure_1 = plt.figure()
    axis_1 = figure_1.add_subplot(1,1,1)

    video_name = home_directory + "/original_reconstruction_1min.avi"
    video_codec = cv2.VideoWriter_fourcc(*'DIVX')
    video = cv2.VideoWriter(video_name, video_codec, frameSize=(608, 600), fps=30)

    for x in range(1800):
        frame=array[x]


        frame = np.ndarray.reshape(frame, (600,608))
        frame = np.ndarray.astype(frame, np.uint8)
        frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)


        video.write(frame)

    cv2.destroyAllWindows()
    video.release()




def create_stimuli_dictionary():
    channel_index_dictionary = {
        "Photodiode": 0,
        "Reward": 1,
        "Lick": 2,
        "Visual 1": 3,
        "Visual 2": 4,
        "Odour 1": 5,
        "Odour 2": 6,
        "Irrelevance": 7,
        "Running": 8,
        "Trial End": 9,
        "Camera Trigger": 10,
        "Camera Frames": 11,
        "LED 1": 12,
        "LED 2": 13,
        "Mousecam": 14,
        "Optogenetics": 15,
    }
    return channel_index_dictionary


def load_ai_recorder_file(ai_recorder_file_location):
    table = tables.open_file(ai_recorder_file_location, mode='r')
    data = table.root.Data

    number_of_seconds = np.shape(data)[0]
    number_of_channels = np.shape(data)[1]
    sampling_rate = np.shape(data)[2]

    data_matrix = np.zeros((number_of_channels, number_of_seconds * sampling_rate))

    for second in range(number_of_seconds):
        data_window = data[second]
        start_point = second * sampling_rate

        for channel in range(number_of_channels):
            data_matrix[channel, start_point:start_point + sampling_rate] = data_window[channel]

    data_matrix = np.clip(data_matrix, a_min=0, a_max=None)
    return data_matrix


def get_step_onsets(trace, threshold=2, window=100):
    state = 0
    number_of_timepoints = len(trace)
    onset_times = []
    time_below_threshold = 0

    onset_line = []

    for timepoint in range(number_of_timepoints):
        if state == 0:
            if trace[timepoint] > threshold:
                state = 1
                onset_times.append(timepoint)
                time_below_threshold = 0
            else:
                pass
        elif state == 1:
            if trace[timepoint] > threshold:
                time_below_threshold = 0
            else:
                time_below_threshold += 1
                if time_below_threshold > window:
                    state = 0
                    time_below_threshold = 0
        onset_line.append(state)

    return onset_times, onset_line





#Assign File Location
home_directory      = r"M:\Widefield_Imaging\new_Pyrecorder_Test\1"
video_file          = home_directory + "\\new_Pyrecorder_Test_20210526-172814_widefield.h5"
ai_recorder_file    = home_directory + "\\20210526-172813.h5"


# Load Widefield Data
blue_array, violet_array = load_arrays(video_file)
print("Blue Video Frames: ", np.shape(blue_array)[0])
print("Violet Video Frames: ", np.shape(violet_array)[0])


# Load Ai Recorder Data
data_matrix = load_ai_recorder_file(ai_recorder_file)
stimuli_dictionary = create_stimuli_dictionary()
led_data = data_matrix[stimuli_dictionary["LED 1"]]
step_onsets, onset_line = get_step_onsets(led_data, threshold=3, window=2)

print("Number of Triggers recordered on AI recorder: ", len(step_onsets))

if np.shape(blue_array)[0] == len(step_onsets):
    print("Files Match! Hiperdepiep Hoera!")


# Check Mousecam Frames
mousecam_trace = data_matrix[stimuli_dictionary["Mousecam"]]
mousecam_step_onsets, mousecam_onset_line = get_step_onsets(mousecam_trace, threshold=3, window=2)
print("Mousecam Triggers: ", len(mousecam_step_onsets))