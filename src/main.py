# Bibliotecas necesarias para la interfaz gráfica, comunicación serial, cálculos matemáticos,
# manejo de archivos, sonidos del sistema y fechas
import serial
import tkinter as tk
from tkinter import ttk
import csv
import time
import threading
import math
import winsound
from datetime import datetime

# -------------------- CONFIGURACIONES DEL EXPERIMENTO --------------------
# Se definen los parámetros clave para la adquisición de datos y el entorno gráfico
PUERTO = 'COM5'               # Puerto serial al que está conectado el microcontrolador
BAUDRATE = 115200             # Velocidad de transmisión
SENSIBILIDAD = 20             # Sensibilidad del cursor en píxeles por unidad de inclinación
ANCHO, ALTO = 800, 600        # Dimensiones del canvas de dibujo
ARCHIVO_CSV = "ID_Sesion_TipoTrazo.csv"  # Archivo donde se registran los datos
FPS = 100                     # Frecuencia de muestreo deseada
VEL_MIN = 20                  # Velocidad mínima válida para registrar (evita registros accidentales)
VEL_MAX = 400                 # Velocidad máxima válida
ANCHO_TRAZO_PX = 20           # Grosor de la línea guía

# -------------------- VARIABLES GLOBALES --------------------
# Controlan el estado del puntero, trazos y fases del experimento
pos_x, pos_y = ANCHO // 2, ALTO // 2
corriendo = True
registrando = False
conteo_restante = 0
canvas = None
label_estado = None
combo_trazo = None
tipo_trazo = "Linea Horizontal"
punto_inicio = (0, 0)
punto_final = (0, 0)
repeticiones = 0
fase_familiarizacion = True
ultimo_tiempo = time.time()
ultima_pos = (pos_x, pos_y)
invertir_sentido = False  # Permite cambiar la dirección del trazo para análisis de lateralidad

# -------------------- FUNCIONES PRINCIPALES --------------------

# Guarda las coordenadas registradas junto con metadatos relevantes
def guardar_dato(x, y):
    timestamp = datetime.now().strftime("%d/%m/%Y\t%I:%M %p").lower().replace("am", "a. m.").replace("pm", "p. m.")
    with open(ARCHIVO_CSV, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, tipo_trazo, repeticiones, x, y])

# Calcula la distancia entre dos puntos (para estimar velocidad)
def distancia(p1, p2):
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

# Dibuja la figura guía en pantalla según el tipo de trazo seleccionado
def generar_trazo():
    global punto_inicio, punto_final
    canvas.delete("trazo")
    cx, cy = ANCHO // 2, ALTO // 2

    if tipo_trazo == "Linea Horizontal":
        punto_inicio = (cx - 200, cy)
        punto_final = (cx + 200, cy)
        canvas.create_line(*punto_inicio, *punto_final, fill="blue", width=ANCHO_TRAZO_PX, tags="trazo")
    elif tipo_trazo == "Linea Vertical":
        punto_inicio = (cx, cy - 200)
        punto_final = (cx, cy + 200)
        canvas.create_line(*punto_inicio, *punto_final, fill="blue", width=ANCHO_TRAZO_PX, tags="trazo")
    elif tipo_trazo == "Triángulo":
        punto_inicio = (cx, cy - 150)
        p2 = (cx - 130, cy + 100)
        punto_final = (cx + 130, cy + 100)
        canvas.create_polygon(punto_inicio, p2, punto_final, outline="blue", fill="", width=ANCHO_TRAZO_PX, tags="trazo")
    elif tipo_trazo == "Círculo":
        r = 150
        punto_inicio = (cx, cy - r)
        punto_final = punto_inicio
        canvas.create_oval(cx - r, cy - r, cx + r, cy + r, outline="blue", width=ANCHO_TRAZO_PX, tags="trazo")
    elif tipo_trazo == "S":
        largo = 300
        ancho = 100
        num_puntos = 100
        puntos_s = []
        punto_inicio = (cx, cy - largo // 2)
        punto_final = (cx, cy + largo // 2)
        for i in range(num_puntos + 1):
            t = i / num_puntos
            y = cy - largo / 2 + t * largo
            x = cx + ancho * math.sin(t * 2 * math.pi)
            puntos_s.extend([x, y])
        canvas.create_line(*puntos_s, fill="blue", width=ANCHO_TRAZO_PX, tags="trazo")

    # Se invierte el sentido si se ha activado la opción
    if invertir_sentido:
        punto_inicio, punto_final = punto_final, punto_inicio

    # Marcadores visuales del inicio (verde) y fin (rojo) del trazo
    canvas.create_oval(punto_inicio[0]-5, punto_inicio[1]-5, punto_inicio[0]+5, punto_inicio[1]+5, fill="green", tags="trazo")
    canvas.create_oval(punto_final[0]-5, punto_final[1]-5, punto_final[0]+5, punto_final[1]+5, fill="red", tags="trazo")

# Emite un sonido al iniciar el registro
def emitir_beep():
    winsound.Beep(1000, 300)

# Función principal que recibe y procesa los datos desde el microcontrolador
def leer_serial():
    global pos_x, pos_y, corriendo, registrando, conteo_restante
    global punto_inicio, punto_final, repeticiones, fase_familiarizacion
    global ultimo_tiempo, ultima_pos

    try:
        arduino = serial.Serial(PUERTO, BAUDRATE)
        time.sleep(2)
    except:
        print("No se pudo conectar con Arduino")
        return

    # Inicializa el archivo CSV con encabezados
    with open(ARCHIVO_CSV, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "Figura", "Repetición", "X", "Y"])

    while corriendo:
        try:
            linea = arduino.readline().decode().strip()
            ahora = time.time()
            dt = ahora - ultimo_tiempo

            # Cuenta regresiva entre repeticiones
            if conteo_restante > 0:
                time.sleep(1)
                conteo_restante -= 1
                label_estado.config(text=f"Esperando {conteo_restante}...", fg="orange")
                continue

            # Decodifica los valores de pitch y yaw enviados por el microcontrolador
            if "," in linea:
                partes = linea.split(",")
                if len(partes) == 3:
                    _, pitch_str, yaw_str = partes
                    pitch = float(pitch_str)
                    yaw = float(yaw_str)

                    dx = int(yaw / SENSIBILIDAD)
                    dy = int(pitch / SENSIBILIDAD)

                    nueva_x = max(0, min(ANCHO - 1, pos_x + dx))
                    nueva_y = max(0, min(ALTO - 1, pos_y - dy))
                    velocidad = distancia((nueva_x, nueva_y), ultima_pos) / dt

                    pos_x, pos_y = nueva_x, nueva_y
                    ultima_pos = (pos_x, pos_y)
                    ultimo_tiempo = ahora

                    canvas.create_oval(pos_x-1, pos_y-1, pos_x+1, pos_y+1, fill="red", tags="puntero")

                    # Inicia el registro cuando se entra a la zona verde (inicio)
                    if not registrando and distancia((pos_x, pos_y), punto_inicio) < 10:
                        if not fase_familiarizacion:
                            emitir_beep()
                            registrando = True
                            label_estado.config(text="Tomando datos...", fg="green")
                        else:
                            label_estado.config(text="Familiarización en curso...", fg="gray")

                    # Guarda solo si la velocidad está en el rango esperado
                    if registrando and VEL_MIN <= velocidad <= VEL_MAX:
                        guardar_dato(pos_x, pos_y)

                    # Finaliza el registro al llegar al punto rojo (fin)
                    if registrando and distancia((pos_x, pos_y), punto_final) < 10:
                        registrando = False
                        repeticiones += 1
                        label_estado.config(text=f"Repetición {repeticiones}/5 finalizada", fg="blue")
                        time.sleep(1)

                        # Control de repeticiones y descansos entre sesiones
                        if repeticiones >= 5:
                            repeticiones = 0
                            label_estado.config(text="Descanso de 60s...", fg="purple")
                            time.sleep(60)
                            reset_puntero()
                            fase_familiarizacion = False
                        else:
                            label_estado.config(text="Descanso de 10s...", fg="orange")
                            time.sleep(10)
                            reset_puntero()
        except:
            continue

    arduino.close()

# Reinicia la posición del puntero y actualiza el trazo
def reset_puntero():
    global pos_x, pos_y, registrando, conteo_restante, ultima_pos, ultimo_tiempo
    pos_x, pos_y = ANCHO // 2, ALTO // 2
    ultima_pos = (pos_x, pos_y)
    ultimo_tiempo = time.time()
    registrando = False
    conteo_restante = 5
    canvas.delete("puntero")
    canvas.delete("trazo")
    generar_trazo()
    label_estado.config(text="Reinicio en 5...", fg="orange")

# Actualiza la figura seleccionada desde el combo
def actualizar_trazo(event):
    global tipo_trazo, fase_familiarizacion, repeticiones
    tipo_trazo = combo_trazo.get()
    repeticiones = 0
    fase_familiarizacion = True
    reset_puntero()

# Alterna la dirección del trazo (de inicio a fin o viceversa)
def invertir_direccion():
    global invertir_sentido
    invertir_sentido = not invertir_sentido
    reset_puntero()

# Función principal que lanza la interfaz gráfica y el hilo de lectura
def iniciar_app():
    global canvas, label_estado, combo_trazo

    ventana = tk.Tk()
    ventana.title("AirMouse - Evaluación de Motricidad Fina")
    ventana.geometry(f"{ANCHO}x{ALTO+50}")

    canvas = tk.Canvas(ventana, width=ANCHO, height=ALTO, bg="white")
    canvas.pack()

    label_estado = tk.Label(ventana, text="Esperando inicio...", font=("Arial", 12))
    label_estado.pack()

    frame_controles = tk.Frame(ventana)
    frame_controles.pack()

    combo_trazo = ttk.Combobox(frame_controles, values=["Linea Horizontal", "Linea Vertical", "Triángulo", "Círculo", "S"], state="readonly")
    combo_trazo.current(0)
    combo_trazo.pack(side=tk.LEFT, padx=5)
    combo_trazo.bind("<<ComboboxSelected>>", actualizar_trazo)

    btn_reset = tk.Button(frame_controles, text="Reset Puntero", command=reset_puntero)
    btn_reset.pack(side=tk.LEFT, padx=5)

    btn_invertir = tk.Button(frame_controles, text="Invertir Sentido", command=invertir_direccion)
    btn_invertir.pack(side=tk.LEFT, padx=5)

    generar_trazo()

    hilo = threading.Thread(target=leer_serial, daemon=True)
    hilo.start()

    def al_cerrar():
        global corriendo
        corriendo = False
        ventana.destroy()

    ventana.protocol("WM_DELETE_WINDOW", al_cerrar)
    ventana.mainloop()

# Punto de entrada de la aplicación
if __name__ == '__main__':
    iniciar_app()