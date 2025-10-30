import tkinter as tk
from tkinter import messagebox
import serial
import time

# === CONFIGURACIÓN DEL PUERTO SERIAL ===
PORT = "COM3"          # Cambia este valor por el puerto de tu Arduino
BAUDRATE = 9600

try:
    arduino = serial.Serial(PORT, BAUDRATE, timeout=1)
    time.sleep(2)  # Espera que el Arduino reinicie
    print(f"Conectado al Arduino en {PORT}")
except Exception as e:
    messagebox.showerror("Error de conexión", f"No se pudo conectar al Arduino:\n{e}")
    arduino = None


# === FUNCIÓN PARA ENVIAR COMANDOS ===
def enviar_comando(comando):
    if arduino is None:
        messagebox.showwarning("Sin conexión", "No hay conexión con el Arduino.")
        return

    try:
        arduino.write((comando + "\n").encode())
        print(f"→ Enviado: {comando}")
        estado_label.config(text=f"Último comando: {comando}")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo enviar el comando:\n{e}")


# === INTERFAZ PRINCIPAL ===
root = tk.Tk()
root.title("Control de Servomotor - UART")
root.geometry("400x400")
root.resizable(False, False)
root.configure(bg="#1e1e1e")

# === ESTILOS ===
boton_color = "#4CAF50"
boton_hover = "#45a049"
texto_color = "#ffffff"
fuente_titulo = ("Segoe UI", 16, "bold")
fuente_normal = ("Segoe UI", 12)

# === FUNCIONES DE INTERFAZ ===
def on_key_press(event):
    tecla = event.keysym
    if tecla == "Up":
        enviar_comando("UP")
    elif tecla == "Down":
        enviar_comando("DOWN")
    elif tecla == "Left":
        enviar_comando("LEFT")
    elif tecla == "Right":
        enviar_comando("RIGHT")

def salir():
    if arduino and arduino.is_open:
        arduino.close()
    root.destroy()

# === WIDGETS ===
titulo_label = tk.Label(
    root, text="Control de Servomotor", bg="#1e1e1e", fg=texto_color, font=fuente_titulo
)
titulo_label.pack(pady=15)

instruccion_label = tk.Label(
    root,
    text="Usa los botones o las flechas del teclado\npara mover el servomotor.",
    bg="#1e1e1e",
    fg="#bbbbbb",
    font=fuente_normal,
)
instruccion_label.pack(pady=5)

frame_botones = tk.Frame(root, bg="#1e1e1e")
frame_botones.pack(pady=30)

# Botones direccionales
btn_up = tk.Button(frame_botones, text="↑", font=("Segoe UI", 18), width=4, height=2, bg=boton_color, fg="white", command=lambda: enviar_comando("UP"))
btn_left = tk.Button(frame_botones, text="←", font=("Segoe UI", 18), width=4, height=2, bg=boton_color, fg="white", command=lambda: enviar_comando("LEFT"))
btn_right = tk.Button(frame_botones, text="→", font=("Segoe UI", 18), width=4, height=2, bg=boton_color, fg="white", command=lambda: enviar_comando("RIGHT"))
btn_down = tk.Button(frame_botones, text="↓", font=("Segoe UI", 18), width=4, height=2, bg=boton_color, fg="white", command=lambda: enviar_comando("DOWN"))

btn_up.grid(row=0, column=1, padx=5, pady=5)
btn_left.grid(row=1, column=0, padx=5, pady=5)
btn_right.grid(row=1, column=2, padx=5, pady=5)
btn_down.grid(row=2, column=1, padx=5, pady=5)

estado_label = tk.Label(root, text="Último comando: —", bg="#1e1e1e", fg="#aaaaaa", font=fuente_normal)
estado_label.pack(pady=10)

btn_salir = tk.Button(root, text="Salir", bg="#e53935", fg="white", font=fuente_normal, width=10, command=salir)
btn_salir.pack(pady=10)

# === EVENTOS DEL TECLADO ===
root.bind("<Up>", on_key_press)
root.bind("<Down>", on_key_press)
root.bind("<Left>", on_key_press)
root.bind("<Right>", on_key_press)

# === LOOP PRINCIPAL ===
root.mainloop()

# === LIMPIEZA FINAL ===
if arduino and arduino.is_open:
    arduino.close()
