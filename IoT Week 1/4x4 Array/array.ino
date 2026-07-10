int rows[] = {2, 3, 4, 5};
int cols[] = {6, 7, 8, 9};

byte pattern[4][4] = {
  {0,1,1,0},
  {1,0,0,1},
  {1,1,1,1},
  {1,0,0,1}
};

void setup() {
  for (int i = 0; i < 4; i++) {
    pinMode(rows[i], OUTPUT);
    pinMode(cols[i], OUTPUT);
    digitalWrite(rows[i], HIGH);
    digitalWrite(cols[i], HIGH);
  }
}

void loop() {
  for (int r = 0; r < 4; r++) {
    for (int i = 0; i < 4; i++)
      digitalWrite(rows[i], HIGH);
    digitalWrite(rows[r], LOW);
    for (int c = 0; c < 4; c++) {
      digitalWrite(cols[c], pattern[r][c] ? LOW : HIGH);
    }
    delay(2);
  }
}
