#include <IRremote.h>

IRsend irsend;

void setup() {
  Serial.begin(9600);
}

void loop() {
        //irsend.sendNEC(1286832510, 32);
      irsend.sendNEC(0x7E81CD32, 32);
      delay(30);

}
