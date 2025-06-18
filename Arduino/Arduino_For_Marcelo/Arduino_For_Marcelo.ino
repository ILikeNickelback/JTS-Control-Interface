#define TriggPin 9  //Trigger pin
#define DPin 10      //Detection pin
#define APin 11

//Variables for the received sequence
#define startMarker '<'
#define endMarker '>'
#define continuesMarker '#'
#define frequencyAcquisitionMarker 'F'



//Max number of bytes in sequence (according to available flash memory of arduino ==> Arduino R4 = 32kB)
const unsigned int sizeSequenceMax = 15000;
char sequence[sizeSequenceMax + 1];

//Number of bytes received to index command array (Use int and note byte!!!!)
int bytesRecvd = 0;

//Variables for frequency aquisition
char countFrequency[256];
byte indexFrequency = 0;
float frequency = 0;

char countNbrOfPoints[256];
byte indexNbrOfPoints = 0;
float numberOfPoints = 0;


//Variables for dark time (time between detections)
const unsigned int sizeTimeMax = 800;
char countDarkTime[sizeTimeMax];
byte indexDarkTime = 0;
float darkTime = 0;

//Variables for continues flashing
const unsigned int maxFrequency = 100;
char continuesFlashingFrequency[maxFrequency];
float timeBetweenFlash = 0.0;

//Booleans to tell arduino when everything has been received and to start the series of commands
bool inProgress = false;
bool allReceived = false;
bool continuesFlashinginProgress = false;


//Function to get commands sent via Python serial. The sequence will be processed once everything has been received
void getSerialData() {
  while(Serial.available() > 0) {
    char c = Serial.read();
    if (c == startMarker) {
      bytesRecvd = 0;
      inProgress = true;
    }

    else if (c == endMarker){
      sequence[bytesRecvd++] = '\0';
      bytesRecvd = 0;
      inProgress = false;
      allReceived = true;
      }

    else{
      sequence[bytesRecvd++] = c;
      }
    }
}

//Function to make the LED Flash continuously (at 1Hz)
void continuesFlashing(){
  while (sequence[0] == continuesMarker){
      digitalWrite(TriggPin, HIGH);
      delayMicroseconds(5);
      digitalWrite(TriggPin, LOW);

      //Detection activation
      digitalWrite(DPin, HIGH);
      delayMicroseconds(20);
      digitalWrite(DPin, LOW);

    delay(1000);
    getSerialData();
      }
  } 


//Function to process the sequence once everything has been received
void processSequenceAcquisition() {
  if (sequence[0] != continuesMarker && allReceived && !inProgress && sequence[0] != frequencyAcquisitionMarker){
    delay(50); //Just to make sure everything has had time to arrive correctly (Probably don't need this)
    for (int i = 0; i < strlen(sequence); i++) {
        switch (sequence[i]) {
          case 'A':
            digitalWrite(APin, HIGH);
            delayMicroseconds(15);
            digitalWrite(APin,LOW);
            darkTime = 0;
            break;

          case 'C':
            digitalWrite(CPin, HIGH);
            delayMicroseconds(2000);
            digitalWrite(CPin,LOW);
            darkTime = 0;
            break;

          case 'D':
            //Trigger pin activation
            digitalWrite(TriggPin, HIGH);
            delayMicroseconds(5);
            digitalWrite(TriggPin, LOW);


            //Detection activation
            digitalWrite(DPin, HIGH);
            delayMicroseconds(15);
            
            digitalWrite(TriggPin, HIGH);
            delayMicroseconds(5);
            digitalWrite(TriggPin, LOW);

            digitalWrite(DPin, LOW);

            //             //Trigger pin activation
            // digitalWrite(TriggPin, HIGH);
            // delayMicroseconds(5);
            // digitalWrite(TriggPin, LOW);

            darkTime = 0;
            break;
            
          case 'E':
            digitalWrite(EPin, HIGH);
            delayMicroseconds(15);
            digitalWrite(EPin,LOW);
            darkTime = 0;
            break;

          case 'F':
            digitalWrite(FPin, HIGH);
            delayMicroseconds(15);
            digitalWrite(FPin,LOW);
            darkTime = 0;
            break;
          case 'N':
            break;
          case '&':
            indexDarkTime = 0;
            while (sequence[i] != '^'){
              countDarkTime[indexDarkTime++] = sequence[i];
              i++;
            }
            countDarkTime[indexDarkTime] = '\0';
            for(int i = 0; i <= strlen(countDarkTime); i++){
              countDarkTime[i] = countDarkTime[i+1];
            }
            darkTime = atof(countDarkTime);
            if(darkTime < 2) {
              delayMicroseconds(darkTime*1000);
            }
            else{
              delay(darkTime);
            }

            break;
        }
    }
    allReceived = false; 
    memset(sequence, 0, sizeof(sequence)); //Empty sequence for next time
    }
}
//Function to process the sequence in the frequency domain once everything has been received (for Marcelo but not working yet)
void processFrequencyAcquisition() {
  if (sequence[0] == frequencyAcquisitionMarker && allReceived && !inProgress && sequence[0] != continuesMarker){
    delay(50); //Just to make sure everything has had time to arrive correctly (Probably don't need this)
    
    for (int i = 0; i < strlen(sequence); i++) {
      switch (sequence[i]) {
        case 'T':
          indexFrequency = 0;
          i++; // Move past 'T'
          while (sequence[i] != '^' && i < strlen(sequence)) {
            countFrequency[indexFrequency++] = sequence[i++];
          }
          countFrequency[indexFrequency] = '\0';
          frequency = (1/atof(countFrequency)*1000);
          break;


        case 'N':
          indexNbrOfPoints = 0;
          i++; // Move past 'N'
          while (sequence[i] != '^' && i < strlen(sequence)) {
            countNbrOfPoints[indexNbrOfPoints++] = sequence[i++];
          }
          countNbrOfPoints[indexNbrOfPoints] = '\0';
          numberOfPoints = atoi(countNbrOfPoints);
          break;
        }
    }

    startMillis = millis();
    t = 0;
    max_time = numberOfPoints * (1/frequency) * 1000;
    while (t < max_time ){
      t = (millis() - startMillis);   
      PWM_value = round((amp_fact * max_amp * sin(2 * PI *(frequency/1000)* t) + offset_fact * max_amp));
      analogWrite(ledChannel, PWM_value)
      delay(1);
      
      digitalWrite(TriggPin, HIGH);
      delayMicroseconds(5);
      digitalWrite(TriggPin, LOW);

      delay((1/frequency) * 1000 * 10);
    }
    allReceived = false; 
    memset(sequence, 0, sizeof(sequence)); //Empty sequence for next time
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(DPin, OUTPUT);
  digitalWrite(DPin, LOW);

  pinMode(TriggPin, OUTPUT);
  digitalWrite(TriggPin, LOW);
}

void loop() {
  getSerialData();
  continuesFlashing();
  processSequenceAcquisition();
  processFrequencyAcquisition();

}

