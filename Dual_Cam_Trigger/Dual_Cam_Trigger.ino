//Recording State 1 - Not Recording, Not Sent Trigger
//Recording State 2 - Not Recording, Sending Trigger
//Recording State 3 - Recording, Trigger Sent
//Recording State 4 - Finished Recording, no more trigger will be sent 

int recording_state = 1;
int camera_pin_1 = 8;
int camera_pin_2 = 9;
int led_pin = 11;
int exposure_time = 30;

void setup() {
  Serial.begin(9600);

  pinMode(camera_pin_1, OUTPUT);
  pinMode(camera_pin_2, OUTPUT); 
  pinMode(led_pin,      OUTPUT); 

  digitalWrite(camera_pin_1, LOW);
  digitalWrite(camera_pin_2, LOW);
  digitalWrite(led_pin,      LOW);

}


void loop() {

  //Checlk What Matlab Wants Us To Do
 

  //We Are Waiting For A Trigger
  if (recording_state == 1){
      digitalWrite(camera_pin_1, LOW);
      digitalWrite(camera_pin_2, LOW);
      digitalWrite(led_pin,      LOW);
      check_for_signal();
      }

  //We've Detected A Trigger!
  if (recording_state == 2){
      delay(500);
      recording_state = 3;
      }

  //We're Recording!
  if (recording_state == 3){
    
      digitalWrite(led_pin,      HIGH);
      digitalWrite(camera_pin_1, HIGH);
      digitalWrite(camera_pin_2, HIGH);
      delay(exposure_time);
      digitalWrite(led_pin,      LOW);
      digitalWrite(camera_pin_1, LOW);
      digitalWrite(camera_pin_2, LOW);
      delay(3);

      digitalWrite(led_pin,      LOW);
      digitalWrite(camera_pin_1, HIGH);
      digitalWrite(camera_pin_2, HIGH);
      delay(exposure_time);
      digitalWrite(led_pin,      LOW);
      digitalWrite(camera_pin_1, LOW);
      digitalWrite(camera_pin_2, LOW);
      delay(3);

      check_for_signal();
      }

  //Weve Finished Recording - Send Last Trigger and Give Matlab time to Collect Outstanding Frames
   if (recording_state == 4){
      digitalWrite(led_pin,      LOW);
      digitalWrite(camera_pin_1, LOW);
      digitalWrite(camera_pin_2, LOW);
      delay(1000); 
      Serial.print("Thats the last frame captin!");
      Serial.print("\n");      
      
      recording_state = 1;
      }
 
}



void check_for_signal(){
  if (Serial.available() > 0) { 
      int message = Serial.parseInt();
      //flush_serial_buffer();
      if (message!= 0){recording_state = message;}
    }
}

void flush_serial_buffer(){  
    while (Serial.available()) {int dump = Serial.read();} //Clear input buffer} 
    Serial.flush();
}
