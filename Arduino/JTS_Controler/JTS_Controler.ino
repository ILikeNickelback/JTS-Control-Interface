//Define pin names according to usage
#define t0Pin 2 //?
#define DPin 8 //Detecting LED
#define APin 4  //Auxiliary
#define CPin 5  //??
#define EPin 6  //Laser green
#define FPin 7  //Laser IR

const unsigned int sizeSequenceMax = 800; //Acquistion sequence (defined on UI)
char sequence[sizeSequenceMax + 1]; // +1 car on doit avoir un caractère de fin de chaîne, le '\0'

byte numberOfExperiment;
unsigned int timeBetweenExperiment;

const unsigned int sizeTimeMax = 800;
char countDarkTime[sizeTimeMax];
byte indexDarkTime = 0;
float darkTime = 0;

const unsigned long sizeTimeIntervalMax = 400000;
char timeInterval[sizeTimeIntervalMax];

// Function to control pin behavior
void controlPin(byte pin) {
  digitalWrite(pin, HIGH);
  delay(1000);
  digitalWrite(pin, LOW);
  darkTime = 0;
}

//Check if sequence is available?
boolean sequenceAvailable() {
  static byte indexSequence = 0; // static pour se souvenir de cette variable entre 2 appels consécutifs. initialisée qu'une seule fois.
  boolean sequenceFull = false;

   // Read from Serial buffer only if there is data available.
   while (Serial.available() > 0) {
       int c = Serial.read();  // Read the incoming byte

       // If we read a valid character, process it.
       if (c != -1) {
           if (c == '\n') { // End of sequence
               sequence[indexSequence] = '\0'; // Null terminate the string
               indexSequence = 0; // Reset index for next sequence
               sequenceFull = true; // Sequence is complete
           } else {
               if (indexSequence < sizeSequenceMax) {
                   sequence[indexSequence++] = toupper((char)c); // Store the character
               }
           }
       }
   }
   return sequenceFull;
}

char* getSequence(){
    static byte indexSequence = 0; // static pour se souvenir de cette variable entre 2 appels consécutifs. initialisée qu'une seule fois.
    boolean sequenceFull = false;

    // Read from Serial buffer only if there is data available.
    while (Serial.available() > 0) {
        int c = Serial.read();  // Read the incoming byte

        // If we read a valid character, process it.
        if (c != -1) {
            if (c == '\n') { // End of sequence
                sequence[indexSequence] = '\0'; // Null terminate the string
                indexSequence = 0; // Reset index for next sequence
                sequenceFull = true; // Sequence is complete
            } else {
                if (indexSequence < sizeSequenceMax) {
                    sequence[indexSequence++] = toupper((char)c); // Store the character
                }
            }
        }
    }
 
    return sequence;
}

//Set pins
void setup() {
  Serial.begin(115200);
  pinMode(DPin, OUTPUT);
  digitalWrite(DPin, LOW);
  /*
  pinMode(t0Pin, OUTPUT);
  pinMode(DPin, OUTPUT);
  pinMode(APin, OUTPUT);
  pinMode(CPin, OUTPUT);
  pinMode(EPin, OUTPUT);
  pinMode(FPin, OUTPUT);

  digitalWrite(t0Pin,LOW);
  digitalWrite(DPin,LOW);
  digitalWrite(APin,LOW);
  digitalWrite(CPin,LOW);
  digitalWrite(EPin,LOW);
  digitalWrite(FPin,LOW);
  */
}


void loop() {
  if (Serial.available() > 0) {  // Check if there's data in the serial buffer
    getSequence();
  }

//Detecting light once
  if (sequence[0] == '#'){
    digitalWrite(DPin, HIGH);
    delay(2000);
  }

//Turn off detecting light
  if (sequence[0] == '@'){
    digitalWrite(DPin,LOW);
  }
    
  digitalWrite(t0Pin,HIGH);
  delayMicroseconds(50);
  digitalWrite(t0Pin,LOW);
  
  for (int i = 0; i <= strlen(sequence); i++) {
    switch (sequence[i]) {
      case 'A': controlPin(APin); break;
      case 'C': controlPin(CPin); break;
      case 'D': controlPin(DPin); break;
      case 'E': controlPin(EPin); break;
      case 'F': controlPin(FPin); break;
      case '&':
        Serial.print(sequence[i+1]);
        delay(sequence[i+1]);
        break;
      }
    }
  }
