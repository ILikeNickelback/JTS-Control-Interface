
//Function to process the sequence once everything has been received
void processSequenceAcquisition() {
  if (sequence[0] != continuesMarker && allReceived && !inProgress && sequence[0] != frequencyAcquisitionMarker){
    delay(50); //Just to make sure everything has had time to arrive correctly (Probably don't need this)
    for (int i = 0; i < strlen(sequence); i++) {
        switch (sequence[i]) {

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
      PWM_value = round((max_amp * sin(2 * PI *(frequency/1000)* t) + offset_fact * max_amp));
      analogWrite(APin, PWM_value);
      delay(1);
      
      if (PWM_value % 25 == 0) {
        digitalWrite(TriggPin, HIGH);
        delayMicroseconds(5);
        digitalWrite(TriggPin, LOW);;
      }

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

