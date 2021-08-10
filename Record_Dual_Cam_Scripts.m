
function [teensy, cam_1_video_input_object, cam_2_video_input_object] = Record_Dual_Cam_Scripts(mouse_name) 
    
    %Disconnect if already connected
    try
        stop(cam_1_video_input_object);
        stop(cam_2_video_input_object);   
        stoppreview(cam_1_video_input_object);
        stoppreview(cam_2_video_input_object);
    catch    
    end
    
    
    %Connect To Teensy
    teensy = serial("COM8");
    fopen(teensy);
    pause(2);
    
    %Connect To Cameras
    cam_1_video_input_object = videoinput('tisimaq_r2013_64', 2, 'Y800 (640x480)');   %Create Video Input Object for Cam 1
    cam_2_video_input_object = videoinput('tisimaq_r2013_64', 1, 'Y800 (320x240)');   %Create Video Input Object for Cam 1

    cam_1_video_source = getselectedsource(cam_1_video_input_object); %Connect This Object To The Camera
    cam_2_video_source = getselectedsource(cam_2_video_input_object); %Connect This Object To The Camera


    % Set Camera Properties
    cam_1_video_source.Gain = 30; %Set Camera to Have Gain of 63 (max)  
    cam_2_video_source.Gain = 63; %Set Camera to Have Gain of 63 (max)

    cam_1_video_source.Exposure = 0.002  
    cam_2_video_source.Exposure = 0.01; 

    cam_1_video_source.Brightness = 30;
    cam_2_video_source.Brightness = 30;

    cam_1_video_source.Contrast = 10;
    cam_2_video_source.Contrast = 10;

    cam_1_video_source.FrameRate = '87.00'; %Set Framerate - Even when triggered externally if the frame rate is not set high it will drop frames
    cam_2_video_source.FrameRate = '160.00'; %Set Framerate - Even when triggered externally if the frame rate is not set high it will drop frames


    % Set External Trigger
    cam_1_video_source.Trigger = 'Enable';
    cam_2_video_source.Trigger = 'Enable';

    triggerconfig(cam_1_video_input_object, 'hardware', 'hardware', 'hardware');  %Set Camera To Use Hardware Trigger
    triggerconfig(cam_2_video_input_object, 'hardware', 'hardware', 'hardware');  %Set Camera To Use Hardware Trigger

    cam_1_video_input_object.FramesPerTrigger = 1; %Tell Camera To Capture 1 Frame Per Trigger    
    cam_2_video_input_object.FramesPerTrigger = 1; %Tell Camera To Capture 1 Frame Per Trigger    

    cam_1_video_input_object.TriggerRepeat = Inf; %Tell Camera To Expect Potential Infinite Number Of Triggers
    cam_2_video_input_object.TriggerRepeat = Inf; %Tell Camera To Expect Potential Infinite Number Of Triggers

    cam_1_video_source.Exposure = 0.002  ; %Set Exposure Time Of Camera
    cam_2_video_source.Exposure = 0.01; %Set Exposure Time Of Camera


     %Setup Saving On The Camera
    save_directory = 'C:\Eye_Cam_Recordings\'
    timestamp = datestr(now,'yyyy-mm-dd-HH-MM-SS');  %Get Current Time
    cam_1_full_file_path = strcat(save_directory, mouse_name, "_", timestamp, "_cam_1.mp4");     %Create Full Filename Of Video
    cam_2_full_file_path = strcat(save_directory, mouse_name, "_", timestamp, "_cam_2.mp4");     %Create Full Filename Of Videocam_1_full_file_path = 
     
    cam_1_video_input_object.LoggingMode = 'disk'; %Tell The Camera To Save To Disk
    cam_2_video_input_object.LoggingMode = 'disk'; %Tell The Camera To Save To Disk

    cam_1_diskLogger = VideoWriter(cam_1_full_file_path, 'MPEG-4');  %Create A "Disk Logger" This is how the image acquistion toolbox saves files
    cam_2_diskLogger = VideoWriter(cam_2_full_file_path, 'MPEG-4');  %Create A "Disk Logger" This is how the image acquistion toolbox saves files

    cam_1_diskLogger.Quality = 75;
    cam_2_diskLogger.Quality = 75;

    cam_1_video_input_object.DiskLogger = cam_1_diskLogger; %Tell the camera to use the disk logger we just made
    cam_2_video_input_object.DiskLogger = cam_2_diskLogger; %Tell the camera to use the disk logger we just made


    
    %Start Recording
    preview(cam_1_video_input_object);
    preview(cam_2_video_input_object);
    
    start(cam_1_video_input_object);  %Start Recording
    start(cam_2_video_input_object);  %Start Recording

    %Send Start Trigger To Teensy
    flushoutput(teensy);
    fprintf(teensy, "2/n");                                                                 %Send The Number 2 To The Teesy, this is the signal to start strobing
    flushoutput(teensy);
