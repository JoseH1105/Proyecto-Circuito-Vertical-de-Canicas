#include <Servo.h>

Servo motor;
int angulo = 90;  // posición inicial (centro)

void setup() {
  Serial.begin(9600);
  motor.attach(9);  // pin de señal del servo
  motor.write(angulo);
  Serial.println("Servo listo para recibir comandos...");
}

void loop() {
  if (Serial.available() > 0) {
    String comando = Serial.readStringUntil('\n');
    comando.trim();

    if (comando == "UP") {
      angulo += 10;
      if (angulo > 180) angulo = 180;
      Serial.println("Girando arriba");

    } else if (comando == "DOWN") {
      angulo -= 10;
      if (angulo < 0) angulo = 0;
      Serial.println("Girando abajo");

    } else if (comando == "LEFT") {
      angulo = 45;  // posición ejemplo
      Serial.println("Girando izquierda");

    } else if (comando == "RIGHT") {
      angulo = 135; // posición ejemplo
      Serial.println("Girando derecha");
    }

    motor.write(angulo);
    delay(300);

    // Confirmación al Python (opcional)
    Serial.print("Ángulo actual: ");
    Serial.println(angulo);
  }
}
