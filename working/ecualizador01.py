import numpy as np
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pyaudio
from scipy.fft import rfft, rfftfreq

class EqualizerApp:
    def __init__(self, master):
        self.master = master
        master.title("Ecualizador Profesional")
        
        # Configuración de audio
        self.CHUNK = 1024 * 4
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.p = pyaudio.PyAudio()
        
        # Crear ventana de visualización
        self.create_visualization_window()
        
        # Crear controles principales
        self.create_controls_frame()
        
        # Inicializar stream de audio
        self.stream = self.p.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            output=True,
            frames_per_buffer=self.CHUNK,
            stream_callback=self.audio_callback
        )
        
        # Configurar actualización de gráfico
        self.update_interval = 50
        self.update_plot()

    def create_visualization_window(self):
        # Ventana secundaria para la visualización
        self.vis_window = tk.Toplevel(self.master)
        self.vis_window.title("Visualización en Tiempo Real")
        
        # Configurar gráfico matplotlib
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.vis_window)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Configurar ejes
        self.x = rfftfreq(self.CHUNK, 1/self.RATE)
        self.line, = self.ax.semilogx(self.x, np.random.rand(self.CHUNK//2 + 1))
        self.ax.set_ylim(0, 5000)
        self.ax.set_xlim(20, self.RATE/2)
        self.ax.set_xlabel('Frecuencia (Hz)')
        self.ax.set_ylabel('Amplitud')

    def create_controls_frame(self):
        # Frame principal para controles
        control_frame = ttk.Frame(self.master)
        control_frame.pack(padx=10, pady=10)
        
        # Controles deslizantes para bandas de frecuencia
        self.bands = {
            'Bajos': {'freq': (20, 200), 'var': tk.DoubleVar(value=1.0)},
            'Medios': {'freq': (200, 2000), 'var': tk.DoubleVar(value=1.0)},
            'Agudos': {'freq': (2000, 20000), 'var': tk.DoubleVar(value=1.0)}
        }
        
        for idx, (name, band) in enumerate(self.bands.items()):
            ttk.Label(control_frame, text=name).grid(row=0, column=idx)
            ttk.Scale(
                control_frame,
                from_=0.0,
                to=2.0,
                variable=band['var'],
                orient=tk.VERTICAL,
                length=200
            ).grid(row=1, column=idx, padx=10)
            
        # Botón de salida
        ttk.Button(control_frame, text="Salir", command=self.close).grid(row=2, columnspan=3)

    def audio_callback(self, in_data, frame_count, time_info, status):
        # Procesamiento de audio en tiempo real
        data = np.frombuffer(in_data, dtype=np.int16)
        fft_data = rfft(data)
        
        # Aplicar ecualización
        freqs = rfftfreq(len(data), 1/self.RATE)
        for band in self.bands.values():
            mask = (freqs >= band['freq'][0]) & (freqs <= band['freq'][1])
            fft_data[mask] *= band['var'].get()
        
        # Convertir de vuelta a señal de audio
        processed_data = np.fft.irfft(fft_data).astype(np.int16)
        return (processed_data.tobytes(), pyaudio.paContinue)

    def update_plot(self):
        # Actualizar gráfico
        try:
            data = self.stream.read(self.CHUNK, exception_on_overflow=False)
            data_np = np.frombuffer(data, dtype=np.int16)
            y = np.abs(rfft(data_np))
            self.line.set_ydata(y)
            self.canvas.draw()
        except Exception as e:
            print("Error:", e)
        
        self.master.after(self.update_interval, self.update_plot)

    def close(self):
        # Limpieza al cerrar
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        self.master.destroy()
        self.vis_window.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = EqualizerApp(root)
    root.mainloop()