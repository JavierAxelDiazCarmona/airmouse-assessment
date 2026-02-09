#include <Wire.h>  // Biblioteca para comunicación I2C, usada para interactuar con el sensor MPU6050

// Dirección I2C del módulo MPU6050
const int MPU = 0x68;

// Variables para almacenar datos crudos del acelerómetro y giroscopio
int16_t accX, accY, accZ;
int16_t gyroX, gyroY, gyroZ;

// Variables para almacenar los ángulos calculados
float pitch, roll, yaw;

// Acumulador para el ángulo de yaw calculado por integración
float gyroYaw = 0;

// Variable para controlar el tiempo de muestreo
unsigned long prevTime;

void setup() {
  Wire.begin();  // Inicializa la comunicación I2C

  // Configuración inicial del MPU6050: se despierta el módulo escribiendo 0 al registro 0x6B
  Wire.beginTransmission(MPU);
  Wire.write(0x6B);  
  Wire.write(0);
  Wire.endTransmission();

  // Inicialización de la comunicación serial para envío de datos
  Serial.begin(115200);

  // Se guarda el tiempo inicial de ejecución
  prevTime = millis();
}

void loop() {
  // -------------------- Lectura del Acelerómetro --------------------
  // Se leen los registros correspondientes a los ejes X, Y y Z del acelerómetro (6 bytes)
  Wire.beginTransmission(MPU);
  Wire.write(0x3B);  // Dirección del primer registro del acelerómetro
  Wire.endTransmission(false);
  Wire.requestFrom(MPU, 6);
  if (Wire.available() == 6) {
    accX = Wire.read() << 8 | Wire.read();
    accY = Wire.read() << 8 | Wire.read();
    accZ = Wire.read() << 8 | Wire.read();
  }

  // -------------------- Lectura del Giroscopio --------------------
  // Se leen los registros correspondientes a los ejes X, Y y Z del giroscopio (6 bytes)
  Wire.beginTransmission(MPU);
  Wire.write(0x43);  // Dirección del primer registro del giroscopio
  Wire.endTransmission(false);
  Wire.requestFrom(MPU, 6);
  if (Wire.available() == 6) {
    gyroX = Wire.read() << 8 | Wire.read();
    gyroY = Wire.read() << 8 | Wire.read();
    gyroZ = Wire.read() << 8 | Wire.read();
  }

  // -------------------- Cálculo de Pitch y Roll --------------------
  // Se convierten los datos crudos del acelerómetro a valores en 'g'
  float ax = accX / 16384.0;
  float ay = accY / 16384.0;
  float az = accZ / 16384.0;

  // Se calculan los ángulos pitch y roll usando trigonometría y el modelo de inclinación estática
  pitch = atan2(ay, sqrt(ax * ax + az * az)) * 180.0 / PI;
  roll  = atan2(ax, sqrt(ay * ay + az * az)) * 180.0 / PI;

  // -------------------- Cálculo de Yaw por integración --------------------
  // Se calcula el tiempo transcurrido entre dos muestras
  unsigned long currentTime = millis();
  float dt = (currentTime - prevTime) / 1000.0;  // Se convierte a segundos
  prevTime = currentTime;

  // El giroscopio mide velocidad angular: se convierte a grados/segundo
  float gyroZ_dps = gyroZ / 131.0;  // 131 LSB por grado/segundo para el rango por defecto ±250°/s

  // Se integra la velocidad angular para estimar el ángulo de yaw acumulado
  gyroYaw += gyroZ_dps * dt;
  yaw = gyroYaw;

  // -------------------- Transmisión de Datos --------------------
  // Se envían los valores de roll, pitch y yaw a través del puerto serial
  Serial.print(roll, 2); Serial.print(",");
  Serial.print(pitch, 2); Serial.print(",");
  Serial.println(yaw, 2);

  // Pequeño retraso para mantener una frecuencia de muestreo de ~50 Hz
  delay(20);
}