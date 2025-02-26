
import tkinter as tk
from tkinter import ttk
import numpy as np
import pyaudio
from scipy.fft import rfft, rfftfreq, irfft
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class Equalizer24Band:
    def __init__(self, master):
        self.master = master
        master.title("24-Band Equalizer")
        
        # Configuración de frecuencias ISO para 24 bandas
        self.bands = [
            25, 31, 40, 50, 63, 80, 100, 125, 160, 200,
            250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000,
            2500, 3150, 4000, 5000, 6300, 8000, 10000, 12500, 16000, 20000
        ][:24]  # Aseguramos 24 bandas
        
        # Configuración de audio
        self.CHUNK = 4096
        self.FORMAT = pyaudio.paFloat32
        self.CHANNELS = 1
        self.RATE = 48000
        self.p = pyaudio.PyAudio()
        
        # Variables de control
        self.gains = {freq: tk.DoubleVar(value=1.0) for freq in self.bands}
        self.stream = None
        
        # Interfaz gráfica
        self.create_gui()
        self.init_audio_stream()
        
        # Configurar actualización del gráfico
        self.update_interval = 50
        self.update_plot()

    def create_gui(self):
        main_frame = ttk.Frame(self.master)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Panel de controles con scroll
        control_canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=control_canvas.yview)
        scroll_frame = ttk.Frame(control_canvas)
        
        control_canvas.configure(yscrollcommand=scrollbar.set)
        control_canvas.pack(side=tk.LEFT, fill=tk.Y)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        control_canvas.create_window((0,0), window=scroll_frame, anchor="nw")
        
        scroll_frame.bind("<Configure>", lambda e: control_canvas.configure(
            scrollregion=control_canvas.bbox("all")))
        
        scroll_frame.bind("<Configure>", lambda e: control_canvas.configure(
            scrollregion=control_canvas.bbox("all")))
        for idx, freq in enumerate(self.bands):
            frame = ttk.Frame(scroll_frame) 
            frame.grid(row=idx//4, column=idx%4, padx=5, pady=5)
            ttk.Label(frame, text=f"{freq} Hz").pack()
            ttk.Scale(
                frame,
                from_=0.0,
                to=2.0,
                variable=self.gains[freq],
                orient=tk.VERTICAL,
                length=150,
                command=lambda v, f=freq: self.update_filter(f)
            ).pack()
        
        # Panel de visualización
        vis_frame = ttk.Frame(main_frame)
        vis_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=vis_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.line, = self.ax.semilogx([], [])
        self.ax.set_xlim(20, 20000)
        self.ax.set_ylim(0, 2)
        self.ax.set_xlabel('Frequency (Hz)')
        self.ax.set_ylabel('Gain')

    def init_audio_stream(self):
        self.stream = self.p.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            output=True,
            frames_per_buffer=self.CHUNK,
            stream_callback=self.audio_callback
        )

    def audio_callback(self, in_data, frame_count, time_info, status):
        try:
            # Convertir datos de audio a numpy array
            audio_data = np.frombuffer(in_data, dtype=np.float32)
            
            # Aplicar FFT
            fft_data = rfft(audio_data)
            freqs = rfftfreq(len(audio_data), 1/self.RATE)
            
            # Aplicar ganancias por banda
            for freq, gain_var in self.gains.items():
                lower = freq * 0.707
                upper = freq * 1.414
                mask = (freqs >= lower) & (freqs <= upper)
                fft_data[mask] *= gain_var.get()
            
            # Convertir de vuelta a señal temporal
            processed = irfft(fft_data).astype(np.float32)
            return (processed.tobytes(), pyaudio.paContinue)
        except Exception as e:
            print("Error:", e)
            return (None, pyaudio.paAbort)

    def update_plot(self):
        try:
            x = np.array(self.bands)
            y = [gain.get() for gain in self.gains.values()]
            self.line.set_data(x, y)
            self.ax.relim()
            self.ax.autoscale_view(scaley=False)
            self.canvas.draw()
        except Exception as e:
            print("Plot error:", e)
        
        self.master.after(self.update_interval, self.update_plot)

    def update_filter(self, freq):
        # Actualizar filtro en tiempo real
        pass  # El procesamiento ya se hace en audio_callback

    def close(self):
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.p.terminate()
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    eq = Equalizer24Band(root)
    root.protocol("WM_DELETE_WINDOW", eq.close)
    root.mainloop()