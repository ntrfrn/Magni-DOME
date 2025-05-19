// FILE NAME: uartAR.ino
// VERSION: 1.0.0
// LAST MODIFICATION: 21 MAR 2025

// Arduino Nano Code

/* emag pins reference
   emag | pwm | fwd | rev 
     1  |  11 |  12 |  14 
     2  |  10 |  15 |   9
     3  |   6 |   8 |   5
     4  |   3 |   2 |   7
*/

const uint8_t DEBUG = 0;  // debug mode [0: OFF | 1: ON]

// define control mode
const uint8_t MANUAL = 1;
const uint8_t PREDEF = 2;

// define predefined control mode
const uint8_t STOP = 0;
const uint8_t SONIC = 1;
const uint8_t VORTEX = 2;
const uint8_t XROLL = 3;
const uint8_t YROLL = 4;
const uint8_t SWIM = 5;
const uint8_t FLAP = 6;

// init analog output pins
const uint8_t PWM[4] = {11, 10, 6, 3};

// init digital output pins
const uint8_t FWD[4] = {12, 15, 8, 2};
const uint8_t REV[4] = {14, 9, 5, 7};

// init parameters
// global parameters
const float pi = 3.14;
uint8_t rxData = 0;
uint8_t mode = 0;
uint8_t request = 0;
uint8_t controlMode = 0;
uint8_t predefMode = 0;

// temp magnetic field calculation parameters
float bLocal = 0;
float theta = 0;

// counter parameters
int tempCnt = 0;
int coilCnt = 0;
uint8_t msgCnt = 0;
uint8_t uartCnt = 0;
uint8_t debugCnt = 0;

// coil parameters
const float iMax = 750;           // max input current (mA)
float nCoil = 1324;               // solenoid turn
float rCoil = 21.5*pow(10, -3);   // radius of the coil (m)
float u0 = 4*3.14*pow(10, -7);    // core permeability
float z = 43.5*pow(10, -3);       // distance from coil center to workspace (m)

// buffer arrays (see reference.txt)
uint8_t bufferUart[37] = {0};      // buffer for uart receiving
// manual control parameter array
uint8_t bufferManual[8] = {0};
// predefined control parameter arrays
int bufferPreDef[4] = {0};
int coilArray[4][36] = {0};       // coil power array

void setup(){
  // uart protocal setup
  Serial.begin(9600);
  
  // pins mode setup
  for(coilCnt = 0; coilCnt < 4; coilCnt++){
    pinMode(PWM[coilCnt], OUTPUT);
    pinMode(FWD[coilCnt], OUTPUT);
    pinMode(REV[coilCnt], OUTPUT);

    // init 0 to all pin output
    analogWrite(PWM[coilCnt], 0);
    digitalWrite(FWD[coilCnt], LOW);
    digitalWrite(REV[coilCnt], LOW);
  }
}

// receiving uart transmission function
void receiveEvent(){
  while(Serial.available()){
    rxData = Serial.read() - '0';   // decoding to binary | refers to ASCII table

    if(uartCnt < 2){
      mode = mode+rxData;
      if(uartCnt < 1){
        mode = mode << 1;
      }
    }

    bufferUart[uartCnt] = rxData;   // store input in the buffer array
    uartCnt++;                      // bit count

    // reset count
    if(uartCnt == 38){
      uartCnt = 0;
      request = 1;
    }
  }
}

// coil control function
void coilControl(){
  switch(controlMode){
    case MANUAL:
      for(coilCnt = 0; coilCnt < 4; coilCnt++){
        // reverse direction
        if(bufferManual[4+coilCnt] == 1){
          digitalWrite(FWD[coilCnt], LOW);
          digitalWrite(REV[coilCnt], HIGH);
          analogWrite(PWM[coilCnt], bufferManual[coilCnt]);
        }
        // forward direction
        else{
          digitalWrite(FWD[coilCnt], HIGH);
          digitalWrite(REV[coilCnt], LOW);
          analogWrite(PWM[coilCnt], bufferManual[coilCnt]);
        }
      }
    break;  // case MANUAL break

    case PREDEF:
      switch(bufferPreDef[0]){
        case STOP:
          for(coilCnt = 0; coilCnt < 4; coilCnt++){
            digitalWrite(FWD[coilCnt], LOW);
            digitalWrite(REV[coilCnt], LOW);
            analogWrite(PWM[coilCnt], 0);
          }
        break;  // case STOP break

        case SONIC:
          for(tempCnt = 0; tempCnt < 360/bufferPreDef[3]; tempCnt++){
            for(coilCnt = 0; coilCnt < 4; coilCnt++){
              if(coilArray[coilCnt][tempCnt] < 0){
                digitalWrite(FWD[coilCnt], LOW);
                digitalWrite(REV[coilCnt], HIGH);
                analogWrite(PWM[coilCnt], abs(coilArray[coilCnt][tempCnt]));
              }
              else{
                digitalWrite(FWD[coilCnt], HIGH);
                digitalWrite(REV[coilCnt], LOW);
                analogWrite(PWM[coilCnt], abs(coilArray[coilCnt][tempCnt]));
              }
            }
            delay(1000/((360/bufferPreDef[3])*bufferPreDef[2]));
          }
        break;    // case SONIC break

        case VORTEX:
          for(tempCnt = 0; tempCnt < 360/bufferPreDef[3]; tempCnt++){
            for(coilCnt = 0; coilCnt < 4; coilCnt++){
              if(coilArray[coilCnt][tempCnt] < 0){
                digitalWrite(FWD[coilCnt], LOW);
                digitalWrite(REV[coilCnt], HIGH);
                analogWrite(PWM[coilCnt], abs(coilArray[coilCnt][tempCnt]));
              }
              else{
                digitalWrite(FWD[coilCnt], HIGH);
                digitalWrite(REV[coilCnt], LOW);
                analogWrite(PWM[coilCnt], abs(coilArray[coilCnt][tempCnt]));
              }
            }
            delay(1000/((360/bufferPreDef[3])*bufferPreDef[2]));
          }
        break;    // case VORTEX break

        case SWIM:
          for(tempCnt = 0; tempCnt < 70/bufferPreDef[3]; tempCnt++){
            for(coilCnt = 0; coilCnt < 4; coilCnt++){
              if(coilArray[coilCnt][tempCnt] < 0){
                digitalWrite(FWD[coilCnt], LOW);
                digitalWrite(REV[coilCnt], HIGH);
                analogWrite(PWM[coilCnt], 255);
              }
              else{
                digitalWrite(FWD[coilCnt], HIGH);
                digitalWrite(REV[coilCnt], LOW);
                analogWrite(PWM[coilCnt], 255);
              }
            }
            delay(1000/((70/bufferPreDef[3])*bufferPreDef[2]));
          }
        break;    // case SWIM break

        case FLAP:
          for(tempCnt = 0; tempCnt < 180/bufferPreDef[3]; tempCnt++){
            for(coilCnt = 0; coilCnt < 4; coilCnt++){
              if(coilArray[coilCnt][tempCnt] < 0){
                digitalWrite(FWD[coilCnt], LOW);
                digitalWrite(REV[coilCnt], HIGH);
                analogWrite(PWM[coilCnt], 255);
              }
              else{
                digitalWrite(FWD[coilCnt], HIGH);
                digitalWrite(REV[coilCnt], LOW);
                analogWrite(PWM[coilCnt], 255);
              }
            }
            delay(1000/((180/bufferPreDef[3])*bufferPreDef[2]));
          }
        break;    // case FLAP break
      }
    break;    // case PREDEF break
  }
}

// electromagnet power calculation
int emagCal(float bCoil){
  float iCoil = 0;
  int iAnalog = 0;

  iCoil = 2*pow(sqrt(pow(rCoil, 2)+pow(z, 2)), 3)*bCoil/(u0*nCoil*pow(rCoil, 2));
  // debug mode
  if(DEBUG == 1){
    Serial.print("[");
    Serial.print(iCoil*pow(10, 3));
    Serial.print(" mA] ");
  }
  iAnalog = iCoil*pow(10, 3)*255/iMax;
  // set maximum output
  if(iAnalog > 255){
    iAnalog = 255;
  }
  else if(iAnalog < ((-1)*255)){
    iAnalog = (-1)*255;
  }
  else{
    iAnalog = iAnalog;
  }
  // return analog output | 0-255
  return iAnalog;
}

// transmitted messages unpacking function
void msgUnpack(){
  // check mode // [0: manual | 1: predefined]
  switch(mode){
    case MANUAL:    // manual mode
      // clean array before use
      for(msgCnt = 0; msgCnt < 8; msgCnt++){
        bufferManual[msgCnt] = 0;
      }
      // unpack coil power
      for(msgCnt = 0; msgCnt < 8; msgCnt++){
        bufferManual[0] = bufferManual[0] + bufferUart[9-msgCnt];
        bufferManual[1] = bufferManual[1] + bufferUart[17-msgCnt];
        bufferManual[2] = bufferManual[2] + bufferUart[25-msgCnt];
        bufferManual[3] = bufferManual[3] + bufferUart[33-msgCnt];
        if(msgCnt < 7){
          bufferManual[0] = bufferManual[0] << 1;
          bufferManual[1] = bufferManual[1] << 1;
          bufferManual[2] = bufferManual[2] << 1;
          bufferManual[3] = bufferManual[3] << 1;
        }
      }
      // unpack coil direction
      for(msgCnt = 0; msgCnt < 4; msgCnt++){
        bufferManual[4+msgCnt] = bufferUart[34+msgCnt];
      }
      // debug mode
      if(DEBUG == 1){
        Serial.println("##msgUnpack.MANUAL");
        for(debugCnt = 0; debugCnt <4; debugCnt++){
          Serial.print("coil: ");
          Serial.print(debugCnt);
          Serial.print(" power: ");
          Serial.print(bufferManual[debugCnt]);
          Serial.print(" dir: ");
          Serial.println(bufferManual[4+debugCnt]);
        }
      }
      // setup control mode
      controlMode = MANUAL;
      break;    // case MANUAL break

    case PREDEF:    // predefined mode
      // clean array before use
      for(msgCnt = 0; msgCnt < 4; msgCnt++){
        bufferPreDef[msgCnt] = 0;
      }
      // unpack result magnetic field
      for(msgCnt = 0; msgCnt < 16; msgCnt++){
        bufferPreDef[1] = bufferPreDef[1] + bufferUart[17-msgCnt];
        if(msgCnt < 15){
          bufferPreDef[1] = bufferPreDef[1] << 1;
        }
      }
      // unpack frequency and angle step
      for(msgCnt = 0; msgCnt < 8; msgCnt++){
        bufferPreDef[2] = bufferPreDef[2] + bufferUart[25-msgCnt];
        bufferPreDef[3] = bufferPreDef[3] + bufferUart[33-msgCnt];
        if(msgCnt < 7){
          bufferPreDef[2] = bufferPreDef[2] << 1;
          bufferPreDef[3] = bufferPreDef[3] << 1;
        }
      }
      // unpack predefined mode
      for(msgCnt = 0; msgCnt < 4; msgCnt++){
        bufferPreDef[0] = bufferPreDef[0] + bufferUart[37-msgCnt];
        if(msgCnt < 3){
          bufferPreDef[0] = bufferPreDef[0] << 1;
        }
      }
      // debug mode
      if(DEBUG == 1){
        Serial.println("##msgUnpack.PREDEF");
        Serial.print("mode: ");
        Serial.println(bufferPreDef[0]);
        Serial.print("field(mT): ");
        Serial.println(bufferPreDef[1]*pow(10, -3));
        Serial.print("freq(Hz): ");
        Serial.println(bufferPreDef[2]);
        Serial.print("step angle(deg): ");
        Serial.println(bufferPreDef[3]);
      }
      // store coil power to array
      switch(bufferPreDef[0]){
        case STOP:    // stop moving (default mode)
          coilArray[4][36] = {0};
        break;        // case STOP break

        case SONIC:   // sonicate mode
          bLocal = 0;   // reset bLocal before use
          bLocal = ((float((bufferPreDef[1])/4))/(cos(55*pi/180)))*pow(10, -6);
          // debug mode
          if(DEBUG == 1){
            Serial.println("##msgUnpack.PREDEF.sonicMode");
            Serial.print("coil field(mT): ");
            Serial.println(bLocal*pow(10, 3));
          }
          // calculate current for each coil
          for(coilCnt = 0; coilCnt < 4; coilCnt++){
            // debug mode
            if(DEBUG == 1){
              Serial.print("coil: ");
              Serial.print(coilCnt);
              Serial.print(" | ");
            }
            for(tempCnt = 0; tempCnt < 360/bufferPreDef[3]; tempCnt++){
              coilArray[coilCnt][tempCnt] = emagCal(bLocal*pow(-1, tempCnt));
              // debug mode
              if(DEBUG == 1){
                Serial.print(coilArray[coilCnt][tempCnt]);
                Serial.print(" > ");
                Serial.print(bLocal*pow(10, 3));
                Serial.print(" | ");
              }
            }
            // debug mode
            if(DEBUG == 1){
              Serial.println(" ");
            }
          }
        break;        // case SONIC break

        case VORTEX:  // vortex mode
          // reset all local parameters
          bLocal = 0;
          theta = 0;
          // debug mode
          if(DEBUG == 1){
            Serial.println("##msgUnpack.PREDEF.vortexMode");
          }
          for(coilCnt = 0; coilCnt < 4; coilCnt++){
            // debug mode
            if(DEBUG == 1){
              Serial.print("coil: ");
              Serial.print(coilCnt);
              Serial.print(" | ");
            }
            for(tempCnt = 0; tempCnt < (360/bufferPreDef[3]); tempCnt++){
              theta = ((bufferPreDef[3]*tempCnt)-(90*coilCnt))*pi/180;  // vortex direction
              bLocal = (((float(bufferPreDef[1])*pow(10, -6))*cos(theta))/2)/cos(55*pi/180);
              //bLocal = (((float(bufferPreDef[1])/cos(theta))/cos(45*pi/180))/2)*pow(10, -6);
              //bLocal = (((float(bufferPreDef[1])*pow(10, -6))*cos(3*pi/4))/4)*cos(theta);
              coilArray[coilCnt][tempCnt] = emagCal(bLocal*(-1));
              // debug mode
              if(DEBUG == 1){
                Serial.print(coilArray[coilCnt][tempCnt]);
                Serial.print(" > ");
                Serial.print(bLocal*pow(10, 3));
                Serial.print(" | ");
              }
            }
            // debug mode
            if(DEBUG == 1){
              Serial.println(" ");
            }
          }
        break;        // case VORTEX break

        case SWIM:  // swimming mode
          // reset all local parameters
          bLocal = 0;
          theta = 0;
          for(coilCnt = 0; coilCnt < 4; coilCnt++){
            for(tempCnt = 0; tempCnt < (70/bufferPreDef[3]); tempCnt++){
              if(coilCnt%2 == 0){
                theta = bufferPreDef[3]*pi/180;
              }
              else{
                theta = (90-((bufferPreDef[3]*pi/180)*pow(-1, tempCnt)))*pi/180;
              }
              bLocal = ((float(bufferPreDef[1])*pow(10, -6))*cos(theta))/2;
              coilArray[coilCnt][tempCnt] = emagCal(bLocal);
            }
          }
        break;        // case SWIM break

        case FLAP:  // flapping mode
          // reset all local parameters
          bLocal = 0;
          theta = 55*pi/180;
          for(coilCnt = 0; coilCnt < 4; coilCnt++){
            for(tempCnt = 0; tempCnt < (180/bufferPreDef[3]); tempCnt++){
              bLocal = ((float(bufferPreDef[1])*pow(10, -6))*cos(((-90*tempCnt)+(90*coilCnt))*pi/180))/(2*sin(theta));
              coilArray[coilCnt][tempCnt] = emagCal(bLocal);
            }
          }
        break;        // case SWIM break
      }
      controlMode = PREDEF;
      break;    // case PREDEF break
  }
}

void loop(){
  receiveEvent();     // checking uart transmission 
  // receiving new transmission data
  if(request == 1){
    msgUnpack();
    // clear interruption cmd
    request = 0;
    mode = 0;
  }

  // normal loop
  else{
    coilControl();
  }
}
