/*
 * ADC with UART interface ATTiny85
 * 30.01.2022   Mexico
 * Lozano Ramirez Angel Ivan
*/

#include  <SoftwareSerial.h>

////////////////////Config//////////////////////
#define   flag_pin    0     //Digital pin
#define   analog_pin  A1    //Analog pin
#define   rx_pin      3     //UART RX pin
#define   tx_pin      4     //UART TX pin
#define   sam_rate    500   //Sampling rate (ms)
////////////////////////////////////////////////

SoftwareSerial port(rx_pin, tx_pin);                //Create serial port

//16bit variables for manipulation
short res_adc = 0;
short res_adc_aux = 0;
short res_adc_aux2 = 0; 

//8bit variables for serial transmission
unsigned char res_adc_H = 0;
unsigned char res_adc_L = 0;

const short mask_H = (B00000011*256) + B00000000;   //Constant for bit masking

void setup() {
  port.begin(9600);                                 //Init serial port
  pinMode(analog_pin, INPUT);                       //Init analog pin
  pinMode(flag_pin, OUTPUT);                        //Init output digital pin
}

void loop() {
  res_adc = analogRead(analog_pin);                 //Read ADC
  res_adc_aux2 = res_adc;                           //Copy the result
  res_adc_L = res_adc_aux2;                         //Get the low byte
  res_adc_aux2 = res_adc_aux2&mask_H;               //Mask and get the 2 higher bit
  res_adc_aux2 = res_adc_aux2>>8;                   //Move 8 bit to right
  res_adc_H = res_adc_aux2;                         //Get the high byte
  port.write(res_adc_H);                            //Send the high byte
  port.write(res_adc_L);                            //Send the low byte
  digitalWrite(flag_pin, LOW);                      //Turn off digital pin
  delay(sam_rate);                                  //Wait for next sample
  digitalWrite(flag_pin, HIGH);                     //Turn on digital pin
}
