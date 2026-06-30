Commands:
RED ON
RED OFF
GREEN ON
GREEN OFF
ALL OFF
STATUS
HELP
-------------------------------------------
*/

const int RED_LED = 8;
const int GREEN_LED = 9;

bool redState = false;
bool greenState = false;

void setup() {

  pinMode(RED_LED, OUTPUT);
  pinMode(GREEN_LED, OUTPUT);

  Serial.begin(9600);

  Serial.println("=== Serial Command Interface ===");
  Serial.println("Type HELP for available commands");
}

void loop() {

  if (Serial.available()) {

    String command = Serial.readStringUntil('\n');
    command.trim();
    command.toUpperCase();

    if (command == "RED ON") {
      digitalWrite(RED_LED, HIGH);
      redState = true;
      Serial.println("Red LED ON");
    }

    else if (command == "RED OFF") {
      digitalWrite(RED_LED, LOW);
      redState = false;
      Serial.println("Red LED OFF");
    }

    else if (command == "GREEN ON") {
      digitalWrite(GREEN_LED, HIGH);
      greenState = true;
      Serial.println("Green LED ON");
    }

    else if (command == "GREEN OFF") {
      digitalWrite(GREEN_LED, LOW);
      greenState = false;
      Serial.println("Green LED OFF");
    }

    else if (command == "ALL OFF") {
      digitalWrite(RED_LED, LOW);
      digitalWrite(GREEN_LED, LOW);

      redState = false;
      greenState = false;

      Serial.println("All LEDs OFF");
    }

    else if (command == "STATUS") {

      Serial.println("----- STATUS -----");

      Serial.print("Red LED: ");
      Serial.println(redState ? "ON" : "OFF");

      Serial.print("Green LED: ");
      Serial.println(greenState ? "ON" : "OFF");
    }

    else if (command == "HELP") {

      Serial.println("Available Commands:");
      Serial.println("RED ON");
      Serial.println("RED OFF");
      Serial.println("GREEN ON");
      Serial.println("GREEN OFF");
      Serial.println("ALL OFF");
      Serial.println("STATUS");
      Serial.println("HELP");
    }

    else {
      Serial.println("Invalid Command");
      Serial.println("Type HELP");
    }
  }
}
