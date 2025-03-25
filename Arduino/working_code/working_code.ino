#define t0Pin 2
#define simuPin 3
#define TriggPin 9
#define DPin 8
#define APin 4
#define CPin 5
#define EPin 6
#define FPin 7

const unsigned int sizeSequenceMax = 800;
char sequence[sizeSequenceMax + 1]; // +1 car on doit avoir un caractère de fin de chaîne, le '\0'

const unsigned int sizeTimeMax = 800;
char countDarkTime[sizeTimeMax];
byte indexDarkTime = 0;
float darkTime = 0;

const unsigned long sizeTimeIntervalMax = 400000;
char timeInterval[sizeTimeIntervalMax];

boolean sequenceAvailable() {
  static byte indexSequence = 0; // static pour se souvenir de cette variable entre 2 appels consécutifs. initialisée qu'une seule fois.
  boolean sequenceFull = false;
  int c = Serial.read();
  if (c != -1) {
    switch (c) {
      case '\r':
      case ' ':
        break;
        
      case '\n':// marqueur de fin de commande
        sequence[indexSequence] = '\0'; // on termine la c-string
        indexSequence = 0; // on se remet au début pour la prochaine fois
        sequenceFull = true;
        break;
      
      default: // on ajoute s'il reste de la place
        if (indexSequence < sizeSequenceMax){
          sequence[indexSequence++] = toupper((char) c); // on stocke le caractère EN MAJUSCULE et on passe à la case suivante
        }
        break;
    }
  }
  return sequenceFull;
}

void setup() {
  Serial.begin(115200);
  pinMode(DPin, OUTPUT);
  digitalWrite(DPin, LOW);

  pinMode(simuPin, OUTPUT);
  digitalWrite(simuPin, HIGH);

  pinMode(TriggPin, OUTPUT);
  digitalWrite(TriggPin, LOW);
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
  
  if (sequenceAvailable()) {
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
          // Ordre de la sequence : nombre d experiences | temps entre experiences | nombre d experiences a supprimer | acquisition separees ou non | sequence a utiliser
          digitalWrite(t0Pin,HIGH);
          delayMicroseconds(50);
          digitalWrite(t0Pin,LOW);
        
        for (int i = 0; i <= strlen(sequence); i++) {
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
              digitalWrite(DPin, HIGH);
              delayMicroseconds(15);
              digitalWrite(DPin, LOW);
              digitalWrite(TriggPin, LOW);
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
              Serial.println(darkTime);
              break;
          }
        }
        Serial.print(F("J'ai reçu [")); Serial.print(sequence); Serial.println(F("]"));
    }
  }
} 
