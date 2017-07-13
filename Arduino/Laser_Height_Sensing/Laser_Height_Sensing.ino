// July 06 - working with laser + height

#include <avr/wdt.h>


// declarations

const int  L1_pin = A0;     // using Analog pins on UNO to read status of photo-transistor outputs
const int  L2_pin = A1;    
//const int  L1_pin = 10;  
//const int  L2_pin = 11;   

const int CamRecord = 7;
const int rcrd_out =8;
const int snd_out =9;
const int reset_out =10;

const int entryIndicatorPin = 11; // send a high pulse on this pin to let the other uC know that valid entry is made and update entry count, and clear it after session ends
const int exitIndicatorPin = 12;  // send a high pulse on this pin to let the other uC know that valid exit is made and update exit count, and clear it after session ends

const int led_pin = 13;       // led for T.S

// Variables:
volatile int led_state = LOW;

/*

long lastDebounceTime1 = 0;  // the last time the output pin was toggled
long lastDebounceTime2 = 0;  // the last time the output pin was toggled
long debounceDelay = 50;    // the debounce time; increase if the output flickers

*/

//long current_time = 0;    // time -> system time derived from millis function
volatile long A = 0;  // A,B,C,D --> time instants
volatile long B = 0;
volatile long C = 0;
volatile long D = 0;

long  entry_t1= 0;
long  entry_t2= 0;
long  exit_t1= 0;
long  exit_t2= 0;

int people_count = 0; 

long th1, handCut =  100; //75;
long th2, obstacleCut = 4000;

long singleCutThreshold = 7000;

//long th3, lazyWalker = 11000;

boolean checkForSingleCut_flag = false;
long singleCutInstant = 0;


int d_milli = 100; // delay
int d_micro = 100; // delay



//int L1_Counter = 0;   // counter for the number of L1 cuts
volatile int L1_State = 0;         // current state of the L1  // buttonState1
volatile int prev_L1_State = 0;     // previous state of the L1  // lastbuttonState1

//int L2_Counter = 0;   // counter for the number of L2 cuts
volatile int L2_State = 0;         // current state of the L2  // buttonState1
volatile int prev_L2_State = 0;     // previous state of the L2 // lastbuttonState1


// new variables as of June 19
int L1_flag = LOW;
int L2_flag = LOW;

int possible_entry = LOW;
int possible_exit = LOW;
int valid_entry = LOW;
int valid_exit = LOW;

int entry_count = 0;
int exit_count = 0;


long loopStart = 0;
long loopEnd = 0;


//volatile long updateA = LOW;
//volatile long updateB = LOW;
//volatile long updateC = LOW;
//volatile long updateD = LOW;


void setup() {
  
	wdt_enable(WDTO_4S); // wdt timer threshold 4sec

	Serial.begin(9600);

	// initialising pins
	Serial.println("Initialising.......");

	pinMode(led_pin, OUTPUT);
	pinMode(L1_pin, INPUT_PULLUP);
	pinMode(L2_pin, INPUT_PULLUP);

	pinMode(rcrd_out, OUTPUT);
	pinMode(snd_out, OUTPUT);
	pinMode(reset_out, OUTPUT);
	pinMode(CamRecord, OUTPUT);
	
	pinMode(entryIndicatorPin, OUTPUT);
	pinMode(exitIndicatorPin, OUTPUT);

	digitalWrite(led_pin, led_state);     // set initial LED state

	Serial.println("Initialisation complete.");

}
/* -------------------------------------------------------  */
void loop() 
{
	wdt_reset(); 

	loopStart = micros(); // for timimg one cycle of loop()
	digitalWrite(led_pin, led_state);  

	//poll L1 and L2 for change in state
	L1_State = digitalRead(L1_pin);  // read if L1 is high or low
	L2_State = digitalRead(L2_pin);  // read if L2 is high or low

	/* ISR code shifted here - end // effect of doing so = arduino does not freeze by repeated isr calls */ 

	if(L1_State != prev_L1_State) // if L1 has changed after one cycle
		{
		led_blink();

		if (  L1_State == HIGH )
			{    
			//updateA = HIGH;
			A = millis();
			Serial.print("A ");		Serial.println(A);
			}
		else if ( L1_State == LOW)
			{ 
			//updateB = HIGH;
			B = millis();
			Serial.print("B ");	Serial.println(B);	Serial.print(" diff B-A ");	Serial.println(B - A);  
			}

		L1ChangeCode();

		}

	if(L2_State != prev_L2_State) // if L2 has changed after one cycle
		{
		led_blink();

		if (  L2_State == HIGH)
		{
		// updateC = HIGH;
		C = millis();
		Serial.print("C ");		Serial.println(C);
		}
		else if ( L2_State == LOW)
		{
		// updateD = HIGH;
		D = millis();
		Serial.print("D ");	Serial.println(D);	Serial.print("diff D-C ");	Serial.println(D-C);
		}

		L2ChangeCode();

		}

	if(checkForSingleCut_flag == true)	{	checkForSingleCut(); 	}


	prev_L1_State = L1_State;  // store state of L1 as prev state before new loop cycle begins
	prev_L2_State = L2_State;

	loopEnd = micros();
	// Serial.println("loop time in uSec ");
	//Serial.println(loopEnd - loopStart);
	//delay(d_milli*10);

}


void checkForSingleCut()
{
	if( (millis() - singleCutInstant) > singleCutThreshold )
	{
	clearFalseParameters(); // clear saved state information
	signal(2); // send stop record command
	delay(100); //added
	// send reset pulse
	signal(5);
	delay(5);
	signal(6);
	checkForSingleCut_flag = false;
	}
}



void led_blink()  // for visualising interrupts
{
	led_state = !led_state;  
	// digitalWrite(led_pin, led_state); // this statement can be removed if similar statement present in main(); let's try keeping it here
}

void clearFalseParameters() 
// using same fn for clearing false parameters of both entry and exit  can use separate fn for better control 
// assumption : either single entry or exit at a time
{
  
	possible_entry = LOW;
	possible_exit = LOW;    
	entry_t1= 0; 
	entry_t2= 0;
	exit_t1= 0;
	exit_t2= 0;
}

void resetValidParameters() 
// using same fn for clearing valid parameters of both entry and exit  can use separate fn for better control 
// assumption : either single entry or exit at a time
{
	possible_entry = LOW;
	possible_exit = LOW;
	valid_entry = LOW;
	valid_exit = LOW;
	entry_t1= 0; 
	entry_t2= 0;
	exit_t1= 0;
	exit_t2= 0;

}



void signal(int a)
{
	if(a == 1)
		{
		digitalWrite(rcrd_out, HIGH);
		Serial.println("sending rcrd signal");
		}
	if(a == 2)
		{digitalWrite(rcrd_out, LOW);  
		Serial.println("disabling rcrd signal");  
		}

	if(a == 3)
		{
		digitalWrite(snd_out, HIGH);
		Serial.println("sending snd signal");  
		}
	if(a == 4)
		{
		digitalWrite(snd_out, LOW);  
		Serial.println("disabling snd signal");  
		}

	if(a == 5)
		{
		digitalWrite(reset_out, HIGH);
		Serial.println("sending reset signal");  
		}
	if(a == 6)
		{
		digitalWrite(reset_out, LOW);  
		Serial.println("disabling reset signal"); 
		Serial.println(); 
		}
	if(a==7)
		{
		digitalWrite(CamRecord, HIGH);
		}
	if(a==8)
		{
		digitalWrite(CamRecord, LOW);
		}

}

void L1ChangeCode()   /********* Remember to make same corresponding changes in L2ChangeCode() ****************/
{
	if (L1_State == HIGH)  
	{
		if (L1_flag == LOW )
			{
			L1_flag = HIGH;			
			if (B == 0) // check if first cut 
				{
				  Serial.println(" First l1 cut " );		
				}
			}
	}
    
	else if (L1_State == LOW)
	{
	if (L1_flag == HIGH)
		{
		L1_flag = LOW;
		if ( (B-A) < handCut )
			{
			Serial.println("too fast");
			//reset this arduino's flags
			//clearFalseParameters();
			//send reset pulse to other arduino
			//signal(5);
			//delay(1);
			//signal(6);
			}
		else if ((B-A) > obstacleCut)
			{
			Serial.println("too slow");
			//reset this arduino's flags
			//clearFalseParameters();
			//send reset pulse to other arduino
			//signal(5);
			//delay(1);
			//signal(6);
			}
		else
			{

			if (possible_exit == LOW)  // if l1 cut before l2
				{
				Serial.println("possible entry");
				possible_entry = HIGH;
				entry_t1 = A;
				singleCutInstant = entry_t1;
				signal(7);
				signal(1);  // rcrd start
				checkForSingleCut_flag = true;
				signal(8);
				}

			else if (possible_exit == HIGH) // if l1 cut after l2
				{
				  Serial.println("valid exit");
				  valid_exit = HIGH;
				  exit_t2 = B;  				  
				  digitalWrite(exitIndicatorPin, HIGH);				  
				  checkForSingleCut_flag = false;
				  
				  Serial.print("Time for exit "); Serial.println(exit_t2 - exit_t1);
				  exit_count++;
				  Serial.print("exit count "); Serial.println(exit_count);     Serial.println();

				  people_count = entry_count - exit_count;
				  Serial.print("Total people count "); Serial.println(people_count);    Serial.println();  
				  
				  { //this whole block operates as one unit
					resetValidParameters();

					signal(2); // rcrd stop					    
					delay(20); //delay(2);
					signal(3); // send start
					delay(1000); //delay(2000); //delay(20); //delay(10);
					signal(4); // send stop
									
				  }
				  
				  digitalWrite(exitIndicatorPin, LOW);
				  
				  {  //this whole block operates as one unit
					delay(100); //added
					//send reset pulse to other arduino
					signal(5);
					delay(5); //delay(2);
					signal(6);
				  }

				}

			}

		}

	}
}    /********* Remember to make same corresponding changes in L2ChangeCode() ****************/


void L2ChangeCode()  /********* Remember to make same corresponding changes in L1ChangeCode() ****************/
{

	if (L2_State == HIGH)  
		{
		if (L2_flag == LOW )
			{
			L2_flag = HIGH;
			// check if first cut 
			if (D == 0)
				{
				Serial.println(" First l2 cut " );
				}
			}
		}

	else if (L2_State == LOW)
	{
		if (L2_flag == HIGH)
			{
			L2_flag = LOW;

			if ( (D-C) < handCut )
				{
				Serial.println("too fast");
				//reset this arduino's flags
				//clearFalseParameters();
				//send reset pulse to other arduino
				//signal(5);
				//delay(1);
				//signal(6);
				}
			else if ((D-C) > obstacleCut)
				{
				Serial.println("too slow");
				//reset this arduino's flags
				//clearFalseParameters();
				//send reset pulse to other arduino
				//signal(5);
				//delay(1);
				//signal(6);
				}
			else
				{
				if(possible_entry == LOW)  // if l2 cut before l1
					{
					Serial.println("possible exit");
					possible_exit = HIGH;
					exit_t1 = C;
					singleCutInstant = exit_t1;
					signal(1); // rcrd start
					checkForSingleCut_flag = true;

					}

				else if(possible_entry == HIGH)  // if l2 cut after l1
					{
					Serial.println("valid entry");
					valid_entry = HIGH;
					entry_t2 = D;  

					digitalWrite(entryIndicatorPin, HIGH);

					checkForSingleCut_flag = false;

					Serial.print("Time for entry "); Serial.println(entry_t2 - entry_t1);
					entry_count++;
					Serial.print("entry count "); Serial.println(entry_count);     Serial.println();

					people_count = entry_count - exit_count;
					Serial.print("Total people count "); Serial.println(people_count);  Serial.println();

					{ //this whole block operates as one unit
						resetValidParameters();
						signal(2); 	// rcrd stop
						delay(20); 	// delay(2);
						signal(3); 	// send start
						delay(1000); 	// delay(2000); //delay(20); //delay(10);
						signal(4); 	// send stop
						
					}

					digitalWrite(entryIndicatorPin, LOW);

					{  //this whole block operates as one unit
					delay(10); //added
					//send reset pulse to other arduino
					signal(5);
					delay(5); //delay(2);
					signal(6);
					}        
				}
			}
		}
	}
}    /********* Remember to make same corresponding changes in L1ChangeCode() ****************/


