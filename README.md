# Sistema de Registro y Entrenamiento de Motricidad Fina de Muñeca

![Status](https://img.shields.io/badge/Estado-Finalizado-brightgreen)
![Python](https://img.shields.io/badge/Python-3.x-blue)
![Arduino](https://img.shields.io/badge/Hardware-Arduino%20Nano-teal)
![License](https://img.shields.io/badge/Licencia-MIT-lightgrey)

[cite_start]Este proyecto implementa un dispositivo mecatrónico de bajo costo diseñado para la rehabilitación y el entrenamiento del movimiento fino de la muñeca[cite: 1, 5]. El sistema combina hardware embebido para la captura de movimiento inercial y software de escritorio para la visualización de trayectorias y registro de datos clínicos.

[cite_start]Desarrollado en la **Facultad de Ingeniería de la UNAM**.

## 📋 Características Principales

* [cite_start]**Adquisición de Datos:** Captura de aceleración y velocidad angular en 6 ejes utilizando el sensor MPU6050[cite: 35].
* [cite_start]**Procesamiento en Tiempo Real:** Cálculo de ángulos de Euler (Roll, Pitch, Yaw) mediante integración numérica en el microcontrolador[cite: 90].
* [cite_start]**Interfaz de Biofeedback:** Aplicación en Python (Tkinter) que permite al usuario controlar un puntero mediante movimientos de muñeca para seguir trazos geométricos (líneas, círculos, triángulos)[cite: 177, 179].
* [cite_start]**Registro de Desempeño:** Exportación automática de sesiones a archivos `.csv` incluyendo timestamp, tipo de figura, repeticiones y coordenadas (X, Y) para análisis clínico[cite: 178].
* [cite_start]**Diseño Ergonómico:** Soporte impreso en 3D (PLA) adaptable al dorso de la mano[cite: 61, 68].

## 🛠️ Hardware

El sistema se basa en la comunicación serial entre un sistema embebido y una PC.

| Componente | Especificación | Función |
| :--- | :--- | :--- |
| **Microcontrolador** | Arduino Nano (ATmega328P) | [cite_start]Procesamiento de señales y comunicación Serial[cite: 24]. |
| **Sensor IMU** | MPU6050 | [cite_start]Acelerómetro y Giroscopio de 6 grados de libertad[cite: 35]. |
| **Comunicación** | Protocolo I2C | [cite_start]Interfaz entre sensor y microcontrolador[cite: 77]. |
| **Estructura** | Impresión 3D (PLA) | [cite_start]Soporte ligero y no invasivo[cite: 68]. |

### Conexiones (Pinout)
[cite_start]Conexión I2C entre MPU6050 y Arduino Nano[cite: 79, 80, 81, 82]:

* `VCC` -> `3.3V`
* `GND` -> `GND`
* `SCL` -> `A5`
* `SDA` -> `A4`

## 💻 Software y Dependencias

### Firmware (Arduino)
Ubicado en la carpeta `/firmware`.
* [cite_start]Requiere la librería `Wire.h` (nativa)[cite: 98].
* [cite_start]Muestreo configurado a ~50 Hz[cite: 92].
* [cite_start]Baudrate: **115200**[cite: 91].

### Interfaz de Usuario (Python)
Ubicado en la carpeta `/src`.
El script de Python gestiona la interfaz gráfica y el registro de datos.

**Librerías necesarias:**
```bash
pip install pyserial tk
