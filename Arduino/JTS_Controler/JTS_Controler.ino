#include <math.h>
#include <Arduino.h>

// Pin Definitions for ESP32
#define TriggPin 25     // GPIO25
#define DPin 26         // GPIO26
#define APin 27         // GPIO27 (PWM)
#define ledPin 2        // Built-in LED (can also use as debug)

// Pi
#define PI 3.1415926535

// Sequence Markers
#define startMarker '<'
#define endMarker '>'
#define continuesMarker '#'
#define frequencyAcquisitionMarker 'F'

// Constants
const int pwmChannel = 0;
const int resolution = 12;                   // 12-bit PWM resolution (0-4095)
const int pwmFreq = 5000;                    // PWM frequency
const int max_amp = pow(2, resolution) - 1;  // Max amplitude for PWM
const float offset_fact = 1.0;

const unsigned int sizeSequenceMax = 15000;
const unsigned int sizeTimeMax = 800;
const unsigned int maxFrequency = 100;

// Global Variables
char sequence[sizeSequenceMax + 1];
int bytesRecvd = 0;

char countFrequency[256];
byte indexFrequency = 0;
float frequency = 0;

char countNbrOfPoints[256];
byte indexNbrOfPoints = 0;
float numberOfPoints = 0;

char countDarkTime[sizeTimeMax];
byte indexDarkTime = 0;
float darkTime = 0;

char continuesFlashingFrequency[maxFrequency];
float timeBetweenFlash = 0.0;

unsigned long t = 0;
int PWM_value = 0;
unsigned long startMillis = 0;
int max_time = 0;

bool inProgress = false;
bool allReceived = false;

void getSerialData() {
  while (Serial.available() > 0) {
    char c = Serial.read();
    if (c == startMarker) {
      bytesRecvd = 0;
      inProgress = true;
    } else if (c == endMarker) {
      sequence[bytesRecvd++] = '\0';
      bytesRecvd = 0;
      inProgress = false;
      allReceived = true;
    } else {
      sequence[bytesRecvd++] = c;
    }
  }
}

void continuesFlashing() {
  while (sequence[0] == continuesMarker) {
    digitalWrite(TriggPin, HIGH);
    delayMicroseconds(5);
    digitalWrite(TriggPin, LOW);

    digitalWrite(DPin, HIGH);
    delayMicroseconds(20);
    digitalWrite(DPin, LOW);

    delay(1000);
    getSerialData();
  }
}

void processSequenceAcquisition() {
  if (sequence[0] != continuesMarker &&
      allReceived &&
      !inProgress &&
      sequence[0] != frequencyAcquisitionMarker) {

    delay(50);
    for (int i = 0; i < strlen(sequence); i++) {
      switch (sequence[i]) {
        case 'D':
          digitalWrite(TriggPin, HIGH);
          delayMicroseconds(5);
          digitalWrite(TriggPin, LOW);

          digitalWrite(DPin, HIGH);
          delayMicroseconds(15);
          digitalWrite(TriggPin, HIGH);
          delayMicroseconds(5);
          digitalWrite(TriggPin, LOW);
          digitalWrite(DPin, LOW);

          darkTime = 0;

          indexDarkTime = 0;
          while (sequence[++i] != '^') {
            countDarkTime[indexDarkTime++] = sequence[i];
          }
          countDarkTime[indexDarkTime] = '\0';

          for (int j = 0; j < strlen(countDarkTime); j++) {
            countDarkTime[j] = countDarkTime[j + 1];
          }

          darkTime = atof(countDarkTime);
          if (darkTime < 2) {
            delayMicroseconds(darkTime * 1000);
          } else {
            delay(darkTime);
          }
          break;
      }
    }

    allReceived = false;
    memset(sequence, 0, sizeof(sequence));
  }
}

void processFrequencyAcquisition() {
  if (sequence[0] == frequencyAcquisitionMarker &&
      allReceived &&
      !inProgress &&
      sequence[0] != continuesMarker) {

    delay(50);
    for (int i = 0; i < strlen(sequence); i++) {
      switch (sequence[i]) {
        case 'T':
          indexFrequency = 0;
          while (sequence[++i] != '^') {
            countFrequency[indexFrequency++] = sequence[i];
          }
          countFrequency[indexFrequency] = '\0';
          frequency = (1 / atof(countFrequency)) * 1000;
          break;

        case 'N':
          indexNbrOfPoints = 0;
          while (sequence[++i] != '^') {
            countNbrOfPoints[indexNbrOfPoints++] = sequence[i];
          }
          countNbrOfPoints[indexNbrOfPoints] = '\0';
          numberOfPoints = atoi(countNbrOfPoints);
          break;
      }
    }

    startMillis = millis();
    t = 0;
    max_time = numberOfPoints * (1 / frequency) * 1000;

    while (t < max_time) {
      t = millis() - startMillis;
      PWM_value = round((max_amp * sin(2 * PI * (frequency / 1000) * t)) + (offset_fact * max_amp));
      ledcWrite(pwmChannel, PWM_value);

      if (PWM_value % 25 == 0) {
        digitalWrite(TriggPin, HIGH);
        delayMicroseconds(5);
        digitalWrite(TriggPin, LOW);
      }

      delay(1);
    }

    allReceived = false;
    memset(sequence, 0, sizeof(sequence));
  }
}

void setup() {
  Serial.begin(115200);

  pinMode(DPin, OUTPUT);
  pinMode(TriggPin, OUTPUT);
  pinMode(APin, OUTPUT);

  digitalWrite(DPin, LOW);
  digitalWrite(TriggPin, LOW);
  digitalWrite(APin, LOW);

  // Setup PWM for ESP32
  ledcSetup(pwmChannel, pwmFreq, resolution);
  ledcAttachPin(APin, pwmChannel);
}

void loop() {
  getSerialData();
  continuesFlashing();
  processSequenceAcquisition();
  processFrequencyAcquisition();
}
