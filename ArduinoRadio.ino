#include <LiquidCrystal.h>
#include <LCDKeypad.h>

LCDKeypad lcd;
String serialIn;
String serialOut;
boolean serialComplete = false;
int buttonActive;
int counter = 0;

void setup(){
  Serial.begin(9600);
  
  lcd.begin(16,2);
  lcd.clear();
  lcd.print("Arduino Radio");
  lcd.setCursor(0,1);
  lcd.print("V 0.1");
  serialIn.reserve(200);
  
  Serial.println("INITOK"); 
}

void loop(){
  buttonActive = buttonPressed();
  
  if(serialComplete){
     if (serialIn.startsWith("UP")){
       lcd.setCursor(0,0);
       lcd.print("                ");
       lcd.setCursor(0,0);
       lcd.print(serialIn.substring(3));
       
       Serial.println("OK UP");
     }
     
     else if (serialIn.startsWith("DW")){;
       lcd.setCursor(0,1);
       lcd.print("                ");
       lcd.setCursor(0,1);
       lcd.print(serialIn.substring(3));
       
       Serial.println("OK DW");
     }
     
     else{
       Serial.println("NOT DEFINED");
     }
     
     serialIn = "";
     serialComplete = false;
  }
  
  // Checking buttons
  if(buttonActive!=KEYPAD_NONE){
    if(buttonActive == KEYPAD_SELECT){
      Serial.println("BTNSEL");
    }
    else if(buttonActive == KEYPAD_RIGHT){
      Serial.println("BTNRGT");
    }
    else if(buttonActive == KEYPAD_LEFT){
      Serial.println("BTNLFT");
    }
    else if(buttonActive == KEYPAD_UP){
      Serial.println("BTNUP");
    }
    else if(buttonActive == KEYPAD_DOWN){
      Serial.println("BTNDWN");
    }
  }
}


// Reads the serial input and stores in serialIn
void serialEvent() {
  while (Serial.available()) {
    // get the new byte:
    char inChar = (char)Serial.read(); 
    // add it to the inputString:
    if(inChar != '\n'){
      serialIn += inChar;
    }
    // if the incoming character is a newline, set a flag
    // so the main loop can do something about it:
    if (inChar == '\n') {
      serialComplete = true;
    }
  }
}

// Returns the pressed button
int buttonPressed(){
  int aux = lcd.button();
  if(aux != KEYPAD_NONE){
    while(lcd.button() != KEYPAD_NONE){
    }
    delay(30);
    return aux;
  }
  return KEYPAD_NONE;
}

