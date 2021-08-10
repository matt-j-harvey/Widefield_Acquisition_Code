

%Disconnect if already connected
try
        stop(cam_1_video_input_object);
        stop(cam_2_video_input_object);   
        stoppreview(cam_1_video_input_object);
        stoppreview(cam_2_video_input_object);
    catch    
 end

%Connect To Cameras
cam_1_video_input_object = videoinput('tisimaq_r2013_64', 2, 'Y800 (640x480)')   %Create Video Input Object for Cam 1
cam_2_video_input_object = videoinput('tisimaq_r2013_64', 1, 'Y800 (320x240)')   %Create Video Input Object for Cam 1
                
cam_1_video_source = getselectedsource(cam_1_video_input_object); %Connect This Object To The Camera
cam_2_video_source = getselectedsource(cam_2_video_input_object); %Connect This Object To The Camera
  
                
% Set Camera Properties
 cam_1_video_source.Gain = 30; %Set Camera to Have Gain of 63 (max)  
 cam_2_video_source.Gain = 63; %Set Camera to Have Gain of 63 (max)
                
 cam_1_video_source.Exposure = 0.002;  
 cam_2_video_source.Exposure = 0.01; 
                
 cam_1_video_source.Brightness = 30;
 cam_2_video_source.Brightness = 30;
                
  cam_1_video_source.Contrast = 10;
  cam_2_video_source.Contrast = 10;
                
  cam_1_video_source.FrameRate = '87.00'; %Set Framerate - Even when triggered externally if the frame rate is not set high it will drop frames
  cam_2_video_source.FrameRate = '160.00'; %Set Framerate - Even when triggered externally if the frame rate is not set high it will drop frames
  
  %Preview Cameras
  preview(cam_1_video_input_object)
  preview(cam_2_video_input_object)