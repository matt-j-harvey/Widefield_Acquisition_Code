//Pin 2 - Blue LED
//Pin 3 - Violet LED
//Pin 5 - Camera Trigger

//LED State 1 - Blue LED On
//LED State 2 - LEDs Off, Last LED On Was Blue
//LED State 3 - Violet LED On
//LED State 4 - LEDs Off, Last LED Was Violet

//Recording State 1 - Not Recording, Not Sent Trigger
//Recording State 2 - Not Recording, Sending Trigger
//Recording State 3 - Recording, Trigger Sent
//Recording State 4 - Finished Recording, no more trigger will be sent 

int recording_state = 1;
int blue_led        = 2;
int violet_led      = 3;
int camera_trigger  = 4; 


void setup() {
Serial.begin(9600);
pinMode(blue_led,       OUTPUT);
pinMode(violet_led,     OUTPUT);
pinMode(camera_trigger, OUTPUT);

digitalWrite(blue_led,       LOW);
digitalWrite(violet_led,     LOW);
digitalWrite(camera_trigger, LOW);
}


void loop() { 

  if (Serial.available() > 0) {recording_state = Serial.parseInt();}

  if (recording_state == 1){
      digitalWrite(camera_trigger, LOW);
      digitalWrite(blue_led,       LOW);
      digitalWrite(violet_led,     LOW);
  }

  if (recording_state == 2){
      digitalWrite(camera_trigger, LOW);
      digitalWrite(blue_led,       LOW);
      digitalWrite(violet_led,     LOW);
      delay(3000);
      recording_state = 3;
  }
  

  if (recording_state == 3){
  
  //Strobe LED 1
  digitalWrite(violet_led, HIGH);
  delay(1); 
  digitalWrite(camera_trigger, HIGH);
  delay(2);
  digitalWrite(camera_trigger, LOW);
  delay(13);
  if (Serial.available() > 0) {recording_state = Serial.parseInt();}
  digitalWrite(violet_led, LOW); 
  delay(2);

  //Strobe LED 2
  digitalWrite(blue_led, HIGH); 
  delay(1); 
  digitalWrite(camera_trigger, HIGH);
  delay(2);
  digitalWrite(camera_trigger, LOW);
  delay(13);
  if (Serial.available() > 0) {recording_state = Serial.parseInt();}
  digitalWrite(blue_led, LOW); 
  delay(2);

  }

 if (recording_state == 4){
  
  digitalWrite(blue_led,       LOW); 
  digitalWrite(violet_led,     LOW);
  digitalWrite(camera_trigger, LOW);
  
  Serial.print("Thats the last frame captin!");
  Serial.print("\n");
  delay(1000);
  recording_state = 0;
 }
}
