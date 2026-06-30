States:
Distance > 50cm
  -> SAFE

20cm - 50cm
  -> Yellow LED
  -> Buzzer every 500ms

10cm - 20cm
  -> Red LED
  -> Buzzer every 200ms

Distance < 10cm
  -> All LEDs flash rapidly
  -> Continuous buzzer

Uses millis() for non-blocking timing.
------------------------------------------------------
*/

const int trigPin = 9;
const int echoPin = 10;

const int greenLED = 2;
const int yellowLED = 3;
const int redLED = 4;

const int buzzer = 5;

unsigned long previousBlink = 0;
bool buzzerState = false;
bool ledFlashState = false;

void setup() {

  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);

  pinMode(greenLED, OUTPUT);
  pinMode(yellowLED, OUTPUT);
  pinMode(redLED, OUTPUT);

  pinMode(buzzer, OUTPUT);

  Serial.begin(9600);
}

void loop() {

  // Trigger ultrasonic pulse
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);

  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);

  digitalWrite(trigPin, LOW);

  long duration = pulseIn(echoPin, HIGH);

  float distance = (duration * 0.034) / 2;

  Serial.print("Distance: ");
  Serial.print(distance);
  Serial.println(" cm");

  unsigned long currentMillis = millis();

  // Reset outputs
  digitalWrite(greenLED, LOW);
  digitalWrite(yellowLED, LOW);
  digitalWrite(redLED, LOW);

  noTone(buzzer);

  //----------------------------------------
  // SAFE
  //----------------------------------------
  if(distance > 50) {

    Serial.println("SAFE");
  }

  //----------------------------------------
  // Warning Zone
  //----------------------------------------
  else if(distance > 20) {

    digitalWrite(yellowLED, HIGH);

    if(currentMillis - previousBlink >= 500) {
      previousBlink = currentMillis;

      buzzerState = !buzzerState;

      if(buzzerState)
        tone(buzzer,1000);
      else
        noTone(buzzer);
    }
  }

  //----------------------------------------
  // Danger Zone
  //----------------------------------------
  else if(distance > 10) {

    digitalWrite(redLED, HIGH);

    if(currentMillis - previousBlink >= 200) {
      previousBlink = currentMillis;

      buzzerState = !buzzerState;

      if(buzzerState)
        tone(buzzer,1000);
      else
        noTone(buzzer);
    }
  }

  //----------------------------------------
  // Critical Zone
  //----------------------------------------
  else {

    tone(buzzer,1000);

    if(currentMillis - previousBlink >= 100) {

      previousBlink = currentMillis;

      ledFlashState = !ledFlashState;

      digitalWrite(greenLED, ledFlashState);
      digitalWrite(yellowLED, ledFlashState);
      digitalWrite(redLED, ledFlashState);
    }
  }
}
