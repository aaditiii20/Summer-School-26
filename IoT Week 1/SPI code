#include <SPI.h>

volatile byte receivedData;

void setup() {
  Serial.begin(9600);

  pinMode(MISO, OUTPUT);
  SPCR |= _BV(SPE);

  SPI.attachInterrupt();
}

ISR(SPI_STC_vect) {
  receivedData = SPDR;
}

void loop() {
  Serial.println((char)receivedData);
  delay(1000);
}
