// 2016Nov23 - working with laser + height + weight

#include <avr/wdt.h>

#include "HX711.h"  /* kj : adapted from weightTrial.ino */

//HX711 scale(A1, A0); //****nova weighing machine A1 - dout, A0 - sck /* kj : adapted from weightTrial.ino */  // A1 and A0 are the input pins
HX711 scale(A3, A2); //****nova weighing machine A3 - dout, A2 - sck // A3 and A2 are the input pins; 
/*changed from (A1,A0) to (A3,A2) bcoz A1 pin in MEGA board was obstructed due to some broken pin inside*/


//for weight readings
float w = 0;
float wMax = 0;

//const int hw_reset_out_slave = 11; // pin to send active low reset signal to slave device when the master reboots // connected to physical RESET pin of slave device

/*
const int rcrd_input=5;
const int snd_input=6;
const int reset_input=7;


boolean flagrcrd = false;
boolean flagsnd = false;
boolean flagreset = false;
*/

/*-------------- <adapted from heightSensor.ino file> ---------*/ // <common to both height and weight>
volatile boolean record_flag= false;
volatile boolean send_flag= false;
volatile boolean reset_flag= false;

volatile boolean prev_send_flag = false;


//Communication with controller - pin config

//int RCRD_PIN = 5;
//int SND_PIN = 6;
//int RESET_PIN = 7;

int RCRD_PIN = 18;
int SND_PIN = 19;
int RESET_PIN = 20;
int CAM_PIN = 21;

const int entryIndicatorPin = 3; //check for a high pulse on this pin to know that valid entry is made and send appropriate string
const int exitIndicatorPin = 4;  //check for a high pulse on this pin to know that valid exit is made and send appropriate string
char c = 'Z';

//</common to both height and weight>

//Ultrasonic sensor pin Config
int TRIG_PIN=12;
int ECHO_PIN=13;

//for height readings
float smartDoorHeight = 215.0f; //268.0f ;


//float hVals[300];
//int hVals_count=0;

float h = 0;
float hMax = 0;

float d = 0;

float h1 = 0;
float h1Max = 0;
float seilHeight = 300.0f;
/*-------------- </adapted from heightSensor.ino file> ---------*/

//new variables
int ping_calls = 0; // no. of pings till record pin is high
long pulseIn_timeout = 5000; //10000; //100000; //10000 //5000; // timeout after 1000 microseconds i.e wait for max 1000 uSec.

void setup()
{
  //wdt_enable(WDTO_8S); // wdt timer threshold 8sec
  
  Serial.begin(9600);
  Serial.println("wait..");  
  
  weight();    /* kj : adapted from weightTrial.ino ; called only once in setup() to initialise weight sensor value to 0 */
  wMax = 0;
  Serial.println("Weight initialised!");  
  
  wdt_enable(WDTO_8S); // shifted wdt enable here as weight() function is taking 
  // significant time to execute completely.
  
  pinMode(entryIndicatorPin, INPUT);
  pinMode(exitIndicatorPin, INPUT);
  
/*-------------- <adapted from heightSensor.ino file> ---------*/
  record_flag=false;
  send_flag=false;
  reset_flag=false;  
  hMax = 0;
  
  pinMode(RCRD_PIN, INPUT);  
  pinMode(SND_PIN, INPUT);  
  pinMode(RESET_PIN, INPUT);  
  pinMode(CAM_PIN, INPUT);

  pinMode(ECHO_PIN, INPUT);
  pinMode(TRIG_PIN, OUTPUT);
  Serial.println("Height initialised!");
  
  // enabling interrupt on interrupt pins of arduino MEGA 
  attachInterrupt(5,RCRD_ISR,CHANGE); //INT5 on PIN 18
  attachInterrupt(4,SND_ISR,CHANGE); //INT4 on PIN 19
  attachInterrupt(3,RESET_ISR,CHANGE); //INT3 on PIN 20
  attachInterrupt(2,CAM_ISR,RISING); //INT2 on PIN 21
/*-------------- </adapted from heightSensor.ino file> ---------*/
  
  
  /*
  pinMode(rcrd_input, INPUT);  
  pinMode(snd_input, INPUT);  
  pinMode(reset_input, INPUT);  
  */
  
  Serial.println("Serial Weight and Height monitor connected ");

}

void loop()
{
  wdt_reset(); 
  
  //checkISRs();
  
  weightCode();
  
  heightCode();
  //sendValues();
  
}

    
void sendValues()
{  
   //Serial.println("In send loop");
   // check if it was entry or exit
   if( (digitalRead(entryIndicatorPin) == 1) )
   {
     c='I';   
   }
   else if((digitalRead(exitIndicatorPin) == 1) )
   {
     c='O';
   }
   
   // send values
  if(send_flag == true)
  {
      //Serial.println("SENDING DATA");
      //Serial.println("***");
      //Serial.println(wMax);
  Serial.print(c); Serial.print("/"); 
  Serial.print(wMax); Serial.print("/"); Serial.print(hMax);    //Serial.print('/'); Serial.print(h1Max);
  Serial.println();
  //Serial.println("###");
  
  //clear values after sending
  wMax = 0;w = 0;
  hMax = 0; h = 0 ; h1Max = 0; h1 = 0;
  c='Z';
  }

}

void checkISRs()
{
  RCRD_ISR();
  SND_ISR();
  RESET_ISR();
}


void getData()  // to be used later
{

}

void weight()
{
  //Serial.println("Before setting up the scale_v:");
  //Serial.print("read_v: \t\t");
  //Serial.println();			// print a raw reading from the ADC
  scale.read();
//  Serial.print("read average_v: \t\t");
//  Serial.println();  	// print the average of 20 readings from the ADC
  scale.read_average(20);
//  Serial.print("get value_v: \t\t");
//  Serial.println();		// print the average of 5 readings from the ADC minus the tare weight (not set yet)
  scale.get_value(5);
  //Serial.print("get units_v: \t\t");
//  Serial.println();	// print the average of 5 readings from the ADC minus tare weight (not set) divided 
  scale.get_units(5);						// by the scale_ parameter (not set yet)  

  scale.set_scale(2280.f);                      // this value is obtained by calibrating the scale_ with known weights; see the README for details
  scale.tare();				        // reset the scale_ to 0

  //Serial.println("After setting up the scale_v:");

//  Serial.print("read_v: \t\t");
  //Serial.println();                 // print a raw reading from the ADC
  scale.read();
//  Serial.print("read average_v: \t\t");
  //Serial.println();       // print the average of 20 readings from the ADC
  scale.read_average(20);
//  Serial.print("get value_v: \t\t");
  //Serial.println();		// print the average of 5 readings from the ADC minus the tare weight, set with tare()
  scale.get_value(5);
//  Serial.print("get units_v: \t\t");
  //Serial.println(, 1);        // print the average of 5 readings from the ADC minus tare weight, divided 
  scale.get_units(5);						// by the scale_ parameter set with set_scale_

 // Serial.println("Readings_v:");
}

void weightCode()
{
   
  if(record_flag == true)   // uncomment to wait for RCRD_PIN to go high to start recording weight values 
    {
      //float value ;
      //Serial.println(value,DEC) ; 

      //w = (scale.get_units(1)/10)*1.04; //calibrate here //for standing true weight
      //w = (scale.get_units(1)/10)*0.99; //calibrate here //for walking approximate true weight //calibrated as of 2016Nov22     
      w = (scale.get_units(1)/10)*1.0; //for walking approximate true weight //sending raw value, will process in RPi //changed as of 2016Nov23     
      
      //Serial.print("w = ");
      //Serial.println(w,DEC);
      //Serial.println(w) ;
      
    //}    
    
    /*
    if(h > 145 && h <  227 )//200)  //height thresholds
    {
      //Serial.print("New Val in range: ");
      //Serial.println(h);
      hVals[hVals_count++] = h;  
      
    }
    */  
    
    //if(record_flag == true)   // uncomment to wait for RCRD_PIN to go high to start updating wMax values 
    //if(w > 40 && w < 100)
    if(w > 0 && w < 150)        //weight thresholds
    {
      if(w > wMax)
      {
        wMax = w;
        //Serial.print("wMax: ");
        //Serial.println(wMax);
      }   
      
    //whole = wMax;
    //fract = (wMax-whole)*100;   
    } 
    
  }
  
  if(send_flag == true)
  {
    
    //Send to Master uC
    Serial.flush();
    //Serial.print("MAX Weight : ");
    //Serial.println(wMax);

    //Wire.write(dist);
  
    //heightVals.clear();
    //hVals_count = 0;
    
    //wMax = 0;
    
    //hVals.clear();
    
  }
  
  if(reset_flag == true)
  {
    w = 0;
    wMax = 0;
  }
  
}


void heightCode()
{
  /*-------------- <adapted from heightSensor.ino file> ---------*/
  

  if(record_flag == true)   // start recording only when record command is received
  {
    ping_calls++;
    
    //Serial.print("From ultra = ");
    //Serial.println(getFromUltrasonic());
    //h = smartDoorHeight - getFromUltrasonic();
    d = getFromUltrasonic();
    h = smartDoorHeight - d;
    
    h1 = seilHeight - d;
    //Serial.println("Receiving height");
    
    //Serial.print(" h = ");
    //Serial.println(h);    
    //Serial.println(h);
    //Height from Ultrasonic sensor to ground is 232.5 cm, we only consider heights between 130 and 200.
    //130 => distance reading in sensor = 102.5
    //200 => distance reading in sensor = 32.5
    
    if(h > 120 && h < 200)  // update h only when it lies within practical bounds
    {
      //Serial.print("New Val in range: ");
      //Serial.println(h);
      //hVals[hVals_count++] = h;
      
      if(h > hMax)          // update hMax only when current h exceeds last stored hMax
      {
        hMax = h;
        //Serial.print("hMax: ");
        //Serial.println(hMax);

        
      }
      
      //hVals.add(h);
      //Serial.println("Added");      
      
      //      if(h1 > h1Max)          // update hMax only when current h exceeds last stored hMax
      //      {
      //        h1Max = h1;
      //        //Serial.print("h1Max: ");
      //        //Serial.println(h1Max);
      //
      //        
      //      }
      
    }
      
      
  }
  

  if(send_flag == true)    // send only when send command is received
  {
      //if( prev_send_flag == true)
      //{
        // we have to do nothing here, just change flag status.
        //prev_send_flag = false;
      //}
      //else if(prev_send_flag == false)
      //{
      //prev_send_flag = true;
        
      //Serial.println("Max/Median Computed");
      //Compute Median
      
      //Send to PC
      
      //Serial.println("sadsadasdhaskudhaskdhaskjhdkjhasdkjashdkjahskhdkjashdkjashd");
      
      //Serial.println("Height Values = ");
      //for(int i=0;i<hVals_count;i++)
      //  Serial.println(hVals[i]);
        
      //Serial.print("Height Max = ");
      //Serial.print(hVals.getHighest());
      
      //Serial.print(", Height Median = ");
      //Serial.flush();
      //Serial.println(hVals.getMedian());
      //Serial.println(hVals.getMedian());
      //Serial.println(hVals.getMedian());
      //Serial.println(hVals.getMedian());
      //Serial.println(hVals.getMedian());
      //Serial.print(" MAX Height = ");
      //Serial.println(hMax);
      //Serial.println(hMax);
      //Serial.println(hMax);
      //Serial.println(hMax);
      //Serial.println(hMax);    // emulating sending hMax value via printing
      
      //Serial.println();
      //heightVals.clear();
      //hVals_count = 0;
      
      //hMax = 0; // reset hMax value once it is sent.
      
      //hVals.clear();
      
      //Serial.print("no. of pings = ");
      //Serial.println(ping_calls);
      //ping_calls = 0;
      
    


  }
  
  if(reset_flag == true)
  {
    //heightVals.clear();
    //hVals_count = 0;
    h = 0;
    hMax = 0;
    ping_calls = 0;
    
    //hVals.clear();
  }
  
  //Serial.print("heightVals.size()=");
  //Serial.println(heightVals.size());
  
  //Serial.println();
  
  //Serial.print("hVals_count=");
  //Serial.println(hVals_count);
  
  //Serial.print("hVals count=");
  //Serial.println(hVals.getCount());
  
  //Serial.println(digitalRead(SND_PIN));
  /*-------------- </adapted from heightSensor.ino file> ---------*/

}


/*-------------- <adapted from heightSensor.ino file> ---------*/

//Ultrasonic Height Measurement
float getFromUltrasonic()
{
  //ping_calls++;
  
  long duration;
  float distance;
  digitalWrite(TRIG_PIN, LOW);  // Added this line
  delayMicroseconds(2); // Added this line
  digitalWrite(TRIG_PIN, HIGH);
  //  delayMicroseconds(1000); - Removed this line
  delayMicroseconds(10); // Added this line
  digitalWrite(TRIG_PIN, LOW);
  
  //duration = pulseIn(ECHO_PIN, HIGH);
  duration = pulseIn(ECHO_PIN, HIGH, pulseIn_timeout);
    
  //duration = pulseIn(ECHO_PIN, HIGH, pulseIn_timeout); // pulseIn() returns the length of the pulse (in microseconds) or 0 if no pulse started before the timeout (unsigned long)
  
  distance = (duration/2) / 29.1;  // taking into account the speed of sound.
  //delay(10);
  delay(1);
  
  return distance;
}


//Interrupt Service Routines

void RCRD_ISR()
{
  int RCRD_val = digitalRead(RCRD_PIN);
  
  if(RCRD_val == 1)
      {
      if(record_flag == false)
      {record_flag = true;
      //Serial.println("started recording");
      }
      }
  else
  {
    if(record_flag == true)
    {
    record_flag = false;
    //Serial.println("stopped recording");
    }
  }
}

void SND_ISR()
{
  int SND_val = digitalRead(SND_PIN);
  
  if(SND_val == 1)
    {
       if(send_flag == false)
      {
          send_flag = true;
          //Serial.println("started sending");
           sendValues();
      }
    }
      else
    {
       if(send_flag == true)
      {
          send_flag = false;
          //Serial.println("stopped sending");
      }
    }
  
}

void RESET_ISR() //Give proper delay between RESET=1 and RESET=0
{
  int RESET_val = digitalRead(RESET_PIN);
  
  if(RESET_val == 1)
    reset_flag = true;
  else
    reset_flag = false; 
}

void CAM_ISR()	{	Serial.println("R/X");	}

/*-------------- </adapted from heightSensor.ino file> ---------*/


/*----------------------------------------------------------------------------*/

// **some useful function to be used for daisy-chaining slave devices //** currently not to be used - 2015July05
/*
void poll_InputPins()
{
   if(digitalRead(rcrd_input) == HIGH)
    {
     if(flagrcrd == false)   // **this flag check done so that the signal() function and corresponding Print statement is executed only once when the record pin goes high or low.
     {  
     signal(1);
     flagrcrd = true;
      }
    }
  if(digitalRead(rcrd_input) == LOW)
    {
      if(flagrcrd == true)
      {
      signal(2);
      flagrcrd = false;
      }
    }
    
  if(digitalRead(snd_input) == HIGH)
    {
     if(flagsnd == false) 
     {
     signal(3);
     flagsnd = true;
     }
   }
    
    
  if(digitalRead(snd_input) == LOW)
    {
      if(flagsnd == true)
      {
      signal(4);
      flagsnd = false;
      }  
    }
 
}

void signal(int a)
{
  if(a == 1)
  {
  Serial.println("received rcrd HIGH"); 
  digitalWrite(rcrd_out, HIGH);
  Serial.println("sending rcrd signal");
  }
  
  if(a == 2)
  {
  Serial.println("received rcrd LOW");
  digitalWrite(rcrd_out, LOW);  
  Serial.println("disabling rcrd signal");  
  }
  if(a == 3)
  {
  Serial.println("received snd HIGH");
  digitalWrite(snd_out, HIGH);
  Serial.println("sending snd signal"); 
  
  getData();     /*********IMP LINE**************/ /*
  
  }
  if(a == 4)
  {
  Serial.println("received snd LOW");
  digitalWrite(snd_out, LOW);  
  Serial.println("disabling snd signal");
  
  clearData_afterSend();
  
  } 
  
 
}


*/
