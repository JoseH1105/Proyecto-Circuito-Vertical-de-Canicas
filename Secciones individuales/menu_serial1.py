import tkinter as tk
from tkinter import font as tkfont
import serial
import time
from tkinter import messagebox

# === CONFIGURACIÓN DEL PUERTO SERIAL ===
PORT = "COM3"          # Cambia este valor según el puerto donde esté tu Arduino
BAUDRATE = 9600

try:
    arduino = serial.Serial(PORT, BAUDRATE, timeout=1)
    time.sleep(2)
    print(f"Conectado al Arduino en {PORT}")
except Exception as e:
    messagebox.showerror("Error de conexión", f"No se pudo conectar al Arduino:\n{e}")
    arduino = None


# === FUNCIÓN PARA ENVIAR COMANDOS AL ARDUINO ===
def enviar_comando(comando):
    """Envía un comando por el puerto serial al Arduino."""
    if arduino is None:
        messagebox.showwarning("Sin conexión", "No hay conexión con el Arduino.")
        return

    try:
        arduino.write((comando + "\n").encode())
        print(f"→ Enviado: {comando}")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo enviar el comando:\n{e}")


class MarbleApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Sistema de Control de Canicas")
        self.geometry("700x500")
        self.configure(bg="#f0f0f0")

        self.title_font = tkfont.Font(family="Segoe UI", size=20, weight="bold")
        self.button_font = tkfont.Font(family="Segoe UI", size=14)
        self.text_font = tkfont.Font(family="Consolas", size=12)

        container = tk.Frame(self, bg="#f0f0f0")
        container.pack(fill="both", expand=True)

        self.frames = {}
        for F in (MenuPrincipal, ModoManual, ModoAutomatico, RutaFrame):
            frame = F(parent=container, controller=self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(MenuPrincipal)

    def show_frame(self, cont, *args):
        """Muestra el frame seleccionado."""
        frame = self.frames[cont]
        frame.tkraise()

        # Si se cambia al frame de Ruta, se actualiza el número de ruta
        if cont == RutaFrame and args:
            frame.update_ruta(args[0])

        # Notificar a los frames si se está entrando o saliendo del modo manual
        for f in self.frames.values():
            if hasattr(f, "on_hide"):
                f.on_hide()
        if hasattr(frame, "on_show"):
            frame.on_show()


class MenuPrincipal(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f0f0f0")
        self.controller = controller

        title = tk.Label(self, text="Menú Principal", font=controller.title_font, bg="#f0f0f0")
        title.pack(pady=40)

        btn_auto = tk.Button(
            self, text="Modo Automático", font=controller.button_font, width=20, height=2,
            bg="#007acc", fg="white", relief="flat",
            command=lambda: controller.show_frame(ModoAutomatico)
        )
        btn_auto.pack(pady=15)

        btn_manual = tk.Button(
            self, text="Modo Manual", font=controller.button_font, width=20, height=2,
            bg="#28a745", fg="white", relief="flat",
            command=lambda: controller.show_frame(ModoManual)
        )
        btn_manual.pack(pady=15)


class ModoManual(tk.Frame):
    """Frame del modo manual: solo aquí se capturan las teclas de movimiento."""
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f0f0f0")
        self.controller = controller

        title = tk.Label(self, text="Modo Manual", font=controller.title_font, bg="#f0f0f0")
        title.pack(pady=20)

        instr = tk.Label(
            self,
            text="Use las flechas del teclado para mover la canica.\nPresione 'Regresar' para volver al menú principal.",
            bg="#f0f0f0", font=controller.button_font
        )
        instr.pack(pady=10)

        self.matriz_frame = tk.Frame(self, bg="white", relief="solid", bd=1)
        self.matriz_frame.pack(pady=15)

        self.pos_x, self.pos_y = 1, 1
        self.matriz_label = tk.Label(
            self.matriz_frame, text=self.generar_matriz(), font=controller.text_font,
            bg="white", justify="left"
        )
        self.matriz_label.pack(padx=10, pady=10)

        back_btn = tk.Button(
            self, text="Regresar", font=controller.button_font,
            bg="#dc3545", fg="white", relief="flat",
            command=lambda: controller.show_frame(MenuPrincipal)
        )
        back_btn.pack(pady=20)

    def on_show(self):
        """Se ejecuta al entrar al modo manual: activa los controles de teclado."""
        self.controller.bind_all("<Up>", self.mover_arriba)
        self.controller.bind_all("<Down>", self.mover_abajo)
        self.controller.bind_all("<Left>", self.mover_izquierda)
        self.controller.bind_all("<Right>", self.mover_derecha)
        print("Controles manuales ACTIVADOS")

    def on_hide(self):
        """Se ejecuta al salir del modo manual: desactiva los controles de teclado."""
        self.controller.unbind_all("<Up>")
        self.controller.unbind_all("<Down>")
        self.controller.unbind_all("<Left>")
        self.controller.unbind_all("<Right>")
        print("Controles manuales DESACTIVADOS")

    def generar_matriz(self):
        matriz = ""
        for i in range(3):
            for j in range(3):
                matriz += " X " if (i, j) == (self.pos_y, self.pos_x) else " O "
            matriz += "\n"
        return matriz

    def actualizar_matriz(self):
        self.matriz_label.config(text=self.generar_matriz())

    def mover_arriba(self, event):
        if self.pos_y > 0:
            self.pos_y -= 1
            self.actualizar_matriz()
            # === SECCIÓN PARA ENVÍO SERIAL (modo manual) ===
            # enviar_comando("UP")

    def mover_abajo(self, event):
        if self.pos_y < 2:
            self.pos_y += 1
            self.actualizar_matriz()
            # === SECCIÓN PARA ENVÍO SERIAL (modo manual) ===
            # enviar_comando("DOWN")

    def mover_izquierda(self, event):
        if self.pos_x > 0:
            self.pos_x -= 1
            self.actualizar_matriz()
            # === SECCIÓN PARA ENVÍO SERIAL (modo manual) ===
            enviar_comando("LEFT")

    def mover_derecha(self, event):
        if self.pos_x < 2:
            self.pos_x += 1
            self.actualizar_matriz()
            # === SECCIÓN PARA ENVÍO SERIAL (modo manual) ===
            enviar_comando("RIGHT")


class ModoAutomatico(tk.Frame):
    """Frame del modo automático."""
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f0f0f0")
        self.controller = controller

        title = tk.Label(self, text="Modo Automático", font=controller.title_font, bg="#f0f0f0")
        title.pack(pady=20)

        instr = tk.Label(
            self, text="Seleccione la ruta que desea ejecutar:",
            bg="#f0f0f0", font=controller.button_font
        )
        instr.pack(pady=10)

        rutas_frame = tk.Frame(self, bg="#f0f0f0")
        rutas_frame.pack(pady=20)

        for i in range(1, 5):
            btn = tk.Button(
                rutas_frame, text=f"Ruta {i}", font=controller.button_font,
                width=15, height=2, bg="#007acc", fg="white", relief="flat",
                command=lambda n=i: controller.show_frame(RutaFrame, n)
            )
            btn.pack(pady=10)

        back_btn = tk.Button(
            self, text="Regresar", font=controller.button_font,
            bg="#dc3545", fg="white", relief="flat",
            command=lambda: controller.show_frame(MenuPrincipal)
        )
        back_btn.pack(pady=20)


class RutaFrame(tk.Frame):
    """Frame para ejecutar una ruta automática."""
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f0f0f0")
        self.controller = controller
        self.ruta_num = tk.IntVar(value=1)

        self.title_label = tk.Label(self, text="", font=controller.title_font, bg="#f0f0f0")
        self.title_label.pack(pady=20)

        self.matriz_frame = tk.Frame(self, bg="white", relief="solid", bd=1)
        self.matriz_frame.pack(pady=15)

        self.matriz_label = tk.Label(self.matriz_frame, text="", font=controller.text_font, bg="white", justify="left")
        self.matriz_label.pack(padx=10, pady=10)

        self.iniciar_btn = tk.Button(
            self, text="Iniciar Secuencia", font=controller.button_font,
            bg="#28a745", fg="white", relief="flat",
            command=self.iniciar_secuencia
        )
        self.iniciar_btn.pack(pady=10)

        self.status_label = tk.Label(self, text="", font=controller.button_font, bg="#f0f0f0", fg="#333333")
        self.status_label.pack(pady=10)

        self.back_btn = tk.Button(
            self, text="Regresar", font=controller.button_font,
            bg="#dc3545", fg="white", relief="flat",
            command=lambda: controller.show_frame(ModoAutomatico)
        )
        self.back_btn.pack(pady=20)

    def update_ruta(self, num):
        self.ruta_num.set(num)
        self.title_label.config(text=f"Ejecutando Ruta {num}")
        self.matriz_label.config(text=self.generar_matriz(num))
        self.status_label.config(text="")

    def generar_matriz(self, num):
        matriz = ""
        for i in range(3):
            for j in range(3):
                matriz += " X " if (i + j) % 3 == num % 3 else " O "
            matriz += "\n"
        return matriz

    def iniciar_secuencia(self):
        self.status_label.config(text=f"Secuencia de la Ruta {self.ruta_num.get()} iniciada.")
        # === SECCIÓN PARA ENVÍO SERIAL (modo automático) ===
        # enviar_comando(f"RUTA_{self.ruta_num.get()}")


if __name__ == "__main__":
    app = MarbleApp()
    app.mainloop()

    if arduino and arduino.is_open:
        arduino.close()
