// C++ code
//
int leds[]={11,10,9,8,2,3,4,5};

 
void setup(){
  for(int i=0;i<=7;i++){
  pinMode(leds[i],OUTPUT);}
  
  for(int i=0;i<=3;i++){
    digitalWrite(leds[i],HIGH);}

  for(int i=4;i<=7;i++){
    digitalWrite(leds[i],LOW);}

}

void loop(){
for(int j=0;j<=3;j++){
  for(int k=4;k<=7;k++){
    digitalWrite(leds[k],HIGH);
    delay(100);
    digitalWrite(leds[j],LOW);
    delay(1000);
    digitalWrite(leds[k],LOW);
    delay(1000); }
  digitalWrite(leds[j],HIGH);
}
}
