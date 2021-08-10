
function [] = Stop_Dual_Cam_Scripts(teensy, cam_1_video_input_object, cam_2_video_input_object)

    %Send Stop signal to teensy
    flushoutput(teensy)
    fprintf(teensy, "4/n"); %Send The Number 2 To The Teesy, this is the signal to start strobing
    flushoutput(teensy)
      
    message = fscanf(teensy,'%s\n')

      if message == 'Thatsthelastframecaptin!'
         stop(cam_1_video_input_object); %Stop The Recording
         stop(cam_2_video_input_object); %Stop The Recording
         
         closepreview(cam_1_video_input_object);
         closepreview(cam_2_video_input_object);
      end
                        
    fclose(teensy);