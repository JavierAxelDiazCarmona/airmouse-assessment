# Sistema de Registro y Entrenamiento de Motricidad Fina de Muñeca

![Status](https://img.shields.io/badge/Estado-Finalizado-brightgreen)
![Python](https://img.shields.io/badge/Python-3.x-blue)
![Arduino](https://img.shields.io/badge/Hardware-Arduino%20Nano-teal)

Este proyecto implementa un dispositivo mecatrónico de bajo costo diseñado para la rehabilitación y el entrenamiento del movimiento fino de la muñeca. El sistema combina hardware embebido para la captura de movimiento inercial y software de escritorio para la visualización de trayectorias y registro de datos clínicos.

Desarrollado en la **Facultad de Ingeniería de la UNAM**.

## 📋 Características Principales

* **Adquisición de Datos:** Captura de aceleración y velocidad angular en 6 ejes utilizando el sensor MPU6050.
* **Procesamiento en Tiempo Real:** Cálculo de ángulos de Euler (Roll, Pitch, Yaw) mediante integración numérica en el microcontrolador.
* **Interfaz de Biofeedback:** Aplicación en Python (Tkinter) que permite al usuario controlar un puntero mediante movimientos de muñeca para seguir trazos geométricos (líneas, círculos, triángulos).
* **Registro de Desempeño:** Exportación automática de sesiones a archivos `.csv` incluyendo timestamp, tipo de figura, repeticiones y coordenadas (X, Y) para análisis clínico.
* **Diseño Ergonómico:** Soporte impreso en 3D (PLA) adaptable al dorso de la mano.

## 🛠️ Hardware

El sistema se basa en la comunicación serial entre un sistema embebido y una PC.

| Componente | Especificación | Función |
| :--- | :--- | :--- |
| **Microcontrolador** | Arduino Nano (ATmega328P) | Procesamiento de señales y comunicación Serial. |
| **Sensor IMU** | MPU6050 | Acelerómetro y Giroscopio de 6 grados de libertad. |
| **Comunicación** | Protocolo I2C | Interfaz entre sensor y microcontrolador. |
| **Estructura** | Impresión 3D (PLA) | Soporte ligero y no invasivo. |

### Conexiones (Pinout)
Conexión I2C entre MPU6050 y Arduino Nano:

* `VCC` -> `3.3V`
* `GND` -> `GND`
* `SCL` -> `A5`
* `SDA` -> `A4`

## 💻 Software y Dependencias

### Firmware (Arduino)
Ubicado en la carpeta `/firmware`.
* Requiere la librería `Wire.h` (nativa).
* Muestreo configurado a ~50 Hz.
* Baudrate: **115200**.

### Interfaz de Usuario (Python)
Ubicado en la carpeta `/src`.
El script de Python gestiona la interfaz gráfica y el registro de datos.

**Librerías necesarias:**
```bash
pip install pyserial tk
