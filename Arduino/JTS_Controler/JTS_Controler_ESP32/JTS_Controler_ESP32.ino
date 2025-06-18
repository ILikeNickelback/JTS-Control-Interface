#include <math.h>
#include <Arduino.h>

// Pin Definitions for ESP32
#define TriggPin 25     // GPIO25
#define DPin 26         // GPIO26
#define APin 27         // GPIO27 (PWM)
#define ledPin 2        // Built-in LED (debug optional)

// Sequence Markers
#define startMarker '<'
#define endMarker '>'
#define continuesMarker '#'
#define frequencyAcquisitionMarker 'F'
#define constantLightMarker 'O'

// Constants
const int pwmChannel = 0;
const int resolution = 9;
const int pwmFreq = 156000;
const int acquisition_frequency = 10;
const int max_amp = pow(2, resolution) - 1;

const unsigned int sizeSequenceMax = 15000;
const unsigned int maxFrequency = 100;

// Global Variables
char sequence[sizeSequenceMax + 1];
int bytesRecvd = 0;
bool inProgress = false;
bool allReceived = false;

int frequency = 0;
int nbrOfPeriods = 0;
int amplitude = 0;
int offset = 0;
int preDetection = 0;
int postDetection = 0;
int darkTime = 0;

unsigned long t = 0;
int PWM_value = 0;
unsigned long startMillis = 0;
int max_time = 0;

char continuesFlashingFrequency[maxFrequency];
float timeBetweenFlash = 0.0;

// --- Utility Functions ---
float extractInt(const char* seq, int& i) {
  char buffer[32];
  int index = 0;
  while (seq[++i] != '^') buffer[index++] = seq[i];
  buffer[index] = '\0';
  return atoi(buffer);
}

float extractFloat(const char* seq, int& i) {
  char buffer[32];
  int index = 0;
  while (seq[++i] != '^') buffer[index++] = seq[i];
  buffer[index] = '\0';
  return atof(buffer);
}

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

void constantLight() {
  if (sequence[0] == constantLightMarker) {
    for (int i = 0; i < strlen(sequence); i++) {
      offset = extractFloat(sequence, i);
      break;
    }

    while (sequence[0] == constantLightMarker) {
      ledcWrite(pwmChannel, offset);
      getSerialData();
    }
  }
}

void triggerAtInterval(float duration_ms, float trigger_interval_ms) {
  startMillis = millis();
  t = 0;
  float lastTrigger = -trigger_interval_ms;  // Ensure first trigger happens at 0

  while (t < duration_ms) {
    t = millis() - startMillis;
    if (t - lastTrigger >= trigger_interval_ms) {
      digitalWrite(TriggPin, HIGH);
      delayMicroseconds(5);
      digitalWrite(TriggPin, LOW);
      lastTrigger = t;
    }
  }
}s

void processSequenceAcquisition() {
  if (sequence[0] != continuesMarker && allReceived && !inProgress && sequence[0] != frequencyAcquisitionMarker) {
    delay(50);

    for (int i = 0; i < strlen(sequence); i++) {
      if (sequence[i] == 'D') {
        digitalWrite(TriggPin, HIGH); delayMicroseconds(5); digitalWrite(TriggPin, LOW);
        digitalWrite(DPin, HIGH); delayMicroseconds(15);
        digitalWrite(TriggPin, HIGH); delayMicroseconds(5); digitalWrite(TriggPin, LOW);
        digitalWrite(DPin, LOW);

        darkTime = extractFloat(sequence, i);
        if (darkTime < 2) delayMicroseconds(darkTime * 1000);
        else delay(darkTime);
      }
    }

    allReceived = false;
    memset(sequence, 0, sizeof(sequence));
  }
}


void processFrequencyAcquisition() {
  if (sequence[0] == frequencyAcquisitionMarker && allReceived && !inProgress && sequence[0] != continuesMarker) {
    delay(50);

    for (int i = 0; i < strlen(sequence); i++) {
      switch (sequence[i]) {
        case 'T': frequency = (1 / extractFloat(sequence, i)) * 1000; break;
        case 'N': nbrOfPeriods = extractInt(sequence, i); break;
        case 'A': amplitude = extractInt(sequence, i); break;
        case 'O': offset = extractFloat(sequence, i); break;
        case 'P': preDetection = extractFloat(sequence, i); break;
        case 'D': postDetection = extractFloat(sequence, i); break;
      }
    }

    float period_ms = 1000.0 / frequency;
    float trigger_interval = period_ms / acquisition_frequency;

    float preDetection_time = preDetection * period_ms;
    float signal_time = nbrOfPeriods * period_ms;
    float postDetection_time = postDetection * period_ms;

    // --- Pre-detection Phase ---
    triggerAtInterval(preDetection_time, trigger_interval);

    // --- Signal Output Phase ---
    startMillis = millis();
    t = 0;
    float lastTrigger = 0;
    bool firstTriggerDone = false;
    float min_point = 0.75 * period_ms;

    while (t < signal_time) {
      t = millis() - startMillis;
      PWM_value = round((amplitude * sin(2 * PI * (frequency / 1000.0) * t)) + (offset * amplitude));
      ledcWrite(pwmChannel, PWM_value);

      if (!firstTriggerDone && t >= min_point) {
        digitalWrite(TriggPin, HIGH); delayMicroseconds(5); digitalWrite(TriggPin, LOW);
        lastTrigger = t;
        firstTriggerDone = true;
      } else if (firstTriggerDone && (t - lastTrigger >= trigger_interval)) {
        digitalWrite(TriggPin, HIGH); delayMicroseconds(5); digitalWrite(TriggPin, LOW);
        lastTrigger += trigger_interval;
      }

      delay(1);
    }

    // --- Post-detection Phase ---
    triggerAtInterval(postDetection_time, trigger_interval);

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

  ledcAttach(APin, pwmFreq, resolution);
}

void loop() {
  getSerialData();
  continuesFlashing();
  constantLight();
  processSequenceAcquisition();
  processFrequencyAcquisition();
}
