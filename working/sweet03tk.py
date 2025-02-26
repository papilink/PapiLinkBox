import tkinter as tk
from tkinter import Canvas, messagebox
import pygame
import numpy as np
from PIL import Image, ImageTk
import sys

# Configuración avanzada de audio
pygame.mixer.init(buffer=1024)  # Reduce la latencia
pygame.mixer.set_num_channels(8)  # Permite múltiples notas simultáneas

class GuitarSimulator:
    def __init__(self, master):
        self.master = master
        self.master.title("Guitar Simulator Pro - Sweet Child O' Mine")
        self.master.geometry("1024x768")
        self.master.configure(bg="#2c3e50")
        
        # Variables de estado
        self.active_notes = set()
        self.volume = 0.5
        self.sustain = False
        
        # Configuración de la interfaz
        self.setup_ui()
        self.load_assets()
        self.bind_events()
        
        # Precarga de sonidos
        self.sonidos_pygame = self.preload_sounds()
        
    def setup_ui(self):
        """Configura los elementos de la interfaz gráfica"""
        self.canvas = Canvas(self.master, bg="#2c3e50", width=1024, height=768)
        self.canvas.pack()
        
        # Panel de control
        self.control_frame = tk.Frame(self.master, bg="#34495e")
        self.control_frame.place(relx=0.05, rely=0.05, relwidth=0.2, relheight=0.2)
        
        # Controles de volumen
        tk.Label(self.control_frame, text="Volumen:", bg="#34495e", fg="white").pack()
        self.volume_scale = tk.Scale(self.control_frame, from_=0, to=1, resolution=0.1,
                                    orient=tk.HORIZONTAL, command=self.set_volume)
        self.volume_scale.set(0.5)
        self.volume_scale.pack()
        
    def load_assets(self):
        """Carga recursos gráficos con manejo mejorado de errores"""
        try:
            self.guitar_img = Image.open("guitar_template.png")
            self.guitar_img = self.guitar_img.resize((1024, 768), Image.Resampling.LANCZOS)
            self.guitar_photo = ImageTk.PhotoImage(self.guitar_img)
            self.canvas.create_image(0, 0, anchor="nw", image=self.guitar_photo)
        except Exception as e:
            self.show_error(f"Error cargando imagen: {str(e)}")
            self.draw_fallback_gui()
            
    def draw_fallback_gui(self):
        """Interfaz alternativa si falla la carga de imagen"""
        self.canvas.create_rectangle(200, 150, 824, 618, fill="#3b4a5f", outline="#2c3e50")
        # Dibujar cuerdas
        for y in range(250, 550, 100):
            self.canvas.create_line(200, y, 824, y, fill="#7f8c8d", width=2)
        
    def bind_events(self):
        """Configura los eventos del teclado usando Tkinter"""
        self.master.bind("<KeyPress>", self.on_key_press)
        self.master.bind("<KeyRelease>", self.on_key_release)
        self.master.bind("<Escape>", lambda e: self.quit_app())
        
    def preload_sounds(self):
        """Precarga y optimiza los sonidos"""
        acordes = {
            "a": [293.66, 369.99, 440.00],  # D (Re)
            "s": [261.63, 329.63, 392.00],  # C (Do)
            "d": [196.00, 246.94, 293.66],  # G (Sol)
            "f": [220.00, 277.18, 329.63]   # A (La)
        }
        
        return {tecla: self.generate_guitar_sound(freqs) for tecla, freqs in acordes.items()}
    
    def generate_guitar_sound(self, frequencies, duration=2.0):
        """Genera sonidos con mejor calidad y optimización"""
        sample_rate = 44100
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        # Mezcla compleja con más armónicos
        wave = sum(
            0.6/(i+1) * np.sin(2 * np.pi * (freq * (i+1)) * t)
            for i, freq in enumerate(frequencies)
        )
        
        # Envolvente mejorada
        envelope = np.ones_like(t)
        attack = int(0.02 * sample_rate)
        envelope[:attack] = np.linspace(0, 1, attack)
        envelope[-int(0.1*sample_rate):] *= np.linspace(1, 0, int(0.1*sample_rate))
        
        wave *= envelope * self.volume
        stereo_wave = np.repeat(wave.reshape(-1, 1), 2, axis=1)
        return pygame.sndarray.make_sound(np.ascontiguousarray(stereo_wave * 32767).astype(np.int16))
    
    def on_key_press(self, event):
        """Maneja eventos de teclado con estado persistente"""
        tecla = event.keysym.lower()
        if tecla in self.sonidos_pygame and tecla not in self.active_notes:
            self.active_notes.add(tecla)
            self.play_note(tecla)
            self.highlight_fret(tecla, "#e74c3c")
            
    def on_key_release(self, event):
        """Maneja liberación de teclas"""
        tecla = event.keysym.lower()
        if tecla in self.active_notes:
            self.active_notes.remove(tecla)
            if not self.sustain:
                self.stop_note(tecla)
            self.highlight_fret(tecla, "#34495e")
    
    def play_note(self, tecla):
        """Reproduce una nota con gestión de canales"""
        channel = pygame.mixer.find_channel()
        if channel:
            channel.play(self.sonidos_pygame[tecla])
            
    def stop_note(self, tecla):
        """Detiene una nota suavemente"""
        for channel in pygame.mixer.get_busy():
            if channel.get_sound() == self.sonidos_pygame[tecla]:
                channel.fadeout(200)
                
    def highlight_fret(self, tecla, color):
        """Resaltado visual mejorado"""
        posiciones = {
            "a": 250, "s": 400, 
            "d": 550, "f": 700
        }
        x = posiciones.get(tecla, 0)
        self.canvas.delete(f"highlight_{tecla}")
        if x > 0:
            self.canvas.create_oval(
                x-30, 300, x+30, 360,
                fill=color, outline="#2c3e50",
                width=2, tags=f"highlight_{tecla}"
            )
    
    def set_volume(self, value):
        """Control de volumen en tiempo real"""
        self.volume = float(value)
        pygame.mixer.music.set_volume(self.volume)
        
    def show_error(self, message):
        """Muestra errores de forma elegante"""
        messagebox.showerror("Error", message)
        
    def quit_app(self):
        """Cierre seguro de la aplicación"""
        pygame.mixer.quit()
        self.master.destroy()
        sys.exit()

if __name__ == "__main__":
    root = tk.Tk()
    app = GuitarSimulator(root)
    root.mainloop()