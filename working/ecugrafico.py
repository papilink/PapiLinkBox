import numpy as np
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class SimuladorEcualizador:
    def __init__(self, master):
        self.master = master
        master.title("Simulador de Ecualizador Gráfico")
        
        # Configuración de bandas
        self.bandas = [31, 62, 125, 250, 500, 1000, 2000, 4000, 8000, 16000]
        self.ganancias = {freq: tk.DoubleVar(value=0.0) for freq in self.bandas}
        
        # Crear interfaz
        self.crear_controles()
        self.crear_grafico()
        
        # Actualización inicial
        self.actualizar_grafico()

    def crear_controles(self):
        # Frame para controles deslizantes
        controles_frame = ttk.Frame(self.master)
        controles_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        # Crear sliders para cada banda
        for freq in self.bandas:
            frame = ttk.Frame(controles_frame)
            frame.pack(pady=5)
            
            ttk.Label(frame, text=f"{freq} Hz").pack()
            ttk.Scale(
                frame,
                from_=-12,
                to=12,
                variable=self.ganancias[freq],
                orient=tk.VERTICAL,
                length=150,
                command=lambda v, f=freq: self.actualizar_grafico()
            ).pack()
        
        # Botón de reset
        ttk.Button(controles_frame, text="Reset", command=self.resetear).pack(pady=10)

    def crear_grafico(self):
        # Configurar gráfico matplotlib
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Configurar ejes
        self.ax.set_xscale('log')
        self.ax.set_xlim(20, 20000)
        self.ax.set_ylim(-12, 12)
        self.ax.set_xlabel('Frecuencia (Hz)')
        self.ax.set_ylabel('Ganancia (dB)')
        self.ax.grid(True, which='both', linestyle='--')
        
        # Línea inicial
        self.line, = self.ax.plot([], [], 'b-', lw=2)

    def calcular_respuesta(self):
        # Crear curva de respuesta suavizada
        frecuencias = np.logspace(np.log10(20), np.log10(20000), 500)
        respuesta = np.zeros_like(frecuencias)
        
        for freq, gain_var in self.ganancias.items():
            ganancia = gain_var.get()
            # Aplicar filtro simulado (campana)
            q = 1  # Ancho de banda
            respuesta += ganancia * np.exp(-(np.log(frecuencias/freq)**2)/(2*(np.log(q))**2))
        
        return frecuencias, respuesta

    def actualizar_grafico(self, event=None):
        frecuencias, respuesta = self.calcular_respuesta()
        self.line.set_data(frecuencias, respuesta)
        self.ax.relim()
        self.ax.autoscale_view(scaley=False)
        self.canvas.draw()

    def resetear(self):
        for gain_var in self.ganancias.values():
            gain_var.set(0.0)
        self.actualizar_grafico()

if __name__ == "__main__":
    root = tk.Tk()
    app = SimuladorEcualizador(root)
    root.mainloop()