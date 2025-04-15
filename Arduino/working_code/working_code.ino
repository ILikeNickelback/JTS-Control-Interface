#define t0Pin 2
#define simuPin 3
#define TriggPin 9

#define DPin 8
#define APin 4
#define CPin 5
#define EPin 6
#define FPin 7

#define startMarker '<'
#define endMarker '>'

int bytesRecvd = 0;

const unsigned int sizeSequenceMax = 15000;
char sequence[sizeSequenceMax + 1]; // 1 car on doit avoir un caractère de fin de chaîne, le '\0'

static byte indexSequence = 0; // static pour se souvenir de cette variable entre 2 appels consécutifs. initialisée qu'une seule fois.
bool sequenceFull = false;

const unsigned int sizeTimeMax = 800;
char countDarkTime[sizeTimeMax];
byte indexDarkTime = 0;
float darkTime = 0;

bool inProgress = false;
bool startFound = false;
bool allReceived = false;

//const unsigned long sizeTimeIntervalMax = 4000;
//char timeInterval[sizeTimeIntervalMax];

void getSerialData() {
  while(Serial.available() > 0) {
    char c = Serial.read();
    if (c == startMarker) {
      bytesRecvd = 0;
      inProgress = true;
    }

    if (c == endMarker){
      sequence[bytesRecvd++] = '\0'; // on termine la c-string
      bytesRecvd = 0; // on se remet au début pour la prochaine fois
      inProgress = false;
      allReceived = true;
      }

    else{
      sequence[bytesRecvd++] = c; // on stocke le caractère EN MAJUSCULE et on passe à la case suivante
    }
  }
  }

void processSequence() {
  if (allReceived && !inProgress){
    delay(1000);
    if (sequence[0] == '#'){
      digitalWrite(DPin, HIGH);
      delayMicroseconds(25);
      digitalWrite(DPin, LOW);
      delay(500);
      }

    if (sequence[0] == '@'){
      digitalWrite(DPin,LOW);
      }

    else {
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
              digitalWrite(TriggPin, HIGH);
              delayMicroseconds(5);
              digitalWrite(TriggPin, LOW);

              digitalWrite(DPin, HIGH);
              delayMicroseconds(20);
              digitalWrite(DPin, LOW);
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
              while (sequence [i] != '^'){
                countDarkTime[indexDarkTime++] = sequence[i];
                i++;
              }
              countDarkTime[indexDarkTime] = '\0';
              for(int i = 0; i <= strlen(countDarkTime); i++){
                countDarkTime[i] = countDarkTime[i+1];
              }
              darkTime = atof(countDarkTime);
              if (darkTime <= 2){
                delayMicroseconds(darkTime*1000);
              }
              else {
                delay(darkTime);
              }
              break;
          }
    }
    allReceived = false; 
    memset(sequence, 0, sizeof(sequence));
    }
  }
}


void setup() {
  Serial.begin(115200);
  pinMode(DPin, OUTPUT);
  digitalWrite(DPin, LOW);

  pinMode(simuPin, OUTPUT);
  digitalWrite(simuPin, HIGH);

  pinMode(TriggPin, OUTPUT);
  digitalWrite(TriggPin, LOW);
}



void loop() {
  getSerialData();
  processSequence();
}

