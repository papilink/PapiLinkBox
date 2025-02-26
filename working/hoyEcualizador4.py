import tkinter as tk
import math
import random
from colorsys import hsv_to_rgb
import time

class MetalEqualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Metal Equalizer 🤘")
        self.root.geometry("1200x600")
        self.root.configure(bg='#000000')

        # Configuración de grupos
        self.num_bars = 24
        self.bpm = 140  # Velocidad base (beats por minuto)
        self.beat_strength = 1.0
        self.running = True
        
        # Frecuencias específicas para metal
        self.frequencies = self.generate_metal_frequencies()
        
        # Lienzo
        self.canvas = tk.Canvas(root, bg='#000000', height=400, width=1150)
        self.canvas.pack(pady=20)
        
        self.setup_bars()
        self.update_bars()

    def generate_metal_frequencies(self):
        """Genera frecuencias específicas para sonido metalero"""
        freqs = []
        # Bajos (6 primeras barras)
        freqs.extend([random.uniform(0.8, 1.2) * 0.7 for _ in range(6)])
        # Medios (12 barras centrales)
        freqs.extend([random.uniform(1.5, 2.5) * 1.2 for _ in range(12)])
        # Agudos (6 últimas barras)
        freqs.extend([random.uniform(3.0, 4.5) * 1.5 for _ in range(6)])
        return freqs

    def setup_bars(self):
        self.bars = []
        self.start_time = time.time()
        bar_width = 30
        spacing = 8
        start_x = (1150 - (self.num_bars * (bar_width + spacing))) // 2

        # Colores iniciales (escala de fuego)
        self.color_phases = [random.uniform(0, 1) for _ in range(self.num_bars)]

        for i in range(self.num_bars):
            x0 = start_x + i * (bar_width + spacing)
            self.create_metal_bar(x0, i)

    def create_metal_bar(self, x0, index):
        """Crea una barra con estilo metalero"""
        y0 = 380
        x1 = x0 + 30
        y1 = y0 - random.randint(50, 100)

        # Color inicial (rojo/anaranjado)
        hue = 0.05 + index * 0.005
        r, g, b = hsv_to_rgb(hue, 0.9, 0.8)
        color = f'#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}'

        bar = self.canvas.create_rectangle(x0, y0, x1, y1, 
                                         fill=color, width=0,
                                         outline='')
        self.bars.append(bar)

    def update_bars(self):
        if not self.running:
            return

        current_time = time.time()
        beat_phase = (current_time % (60 / self.bpm)) * 2 * math.pi

        for i, bar in enumerate(self.bars):
            # Movimiento específico por grupo
            if i < 6:  # Bajos - movimiento potente y sincronizado
                height = self.calculate_bass_height(i, beat_phase)
            elif i < 18:  # Medios - vibración constante
                height = self.calculate_mid_height(i, current_time)
            else:  # Agudos - movimiento rápido y agresivo
                height = self.calculate_treble_height(i, current_time)

            # Actualizar color y posición
            self.update_bar_appearance(bar, i, height, current_time)

        self.root.after(10, self.update_bars)

    def calculate_bass_height(self, index, phase):
        """Movimiento sincronizado con el beat"""
        base_height = 150
        beat_impact = math.sin(phase) ** 3 * 200 * self.beat_strength
        random_jitter = random.uniform(-10, 10)  # Pequeña variación aleatoria
        return base_height + beat_impact + random_jitter

    def calculate_mid_height(self, index, time):
        """Vibración constante con modulación*/
        base = 120
        vibration = math.sin(time * self.frequencies[index]) * 80
        distortion = math.sin(time * 10) * 15  # Efecto de distorsión
        return base + vibration + distortion

    def calculate_treble_height(self, index, time):
        """Movimiento rápido con picos aleatorios"""
        base = 80
        speed_factor = 3.0
        main_move = math.sin(time * self.frequencies[index] * speed_factor) * 60
        random_spike = random.choice([0, 0, 0, 40])  # Picos aleatorios
        return base + main_move + random_spike

    def update_bar_appearance(self, bar, index, height, time):
        """Actualiza color y posición con efecto de 'overdrive'"""
        # Efecto de color dinámico
        hue = (0.05 + math.sin(time * 0.5 + index) * 0.05) % 1.0
        saturation = 0.8 + math.sin(time * 2) * 0.1
        brightness = 0.7 + (height / 350) * 0.3  # Brillo proporcional a la altura

        # Efecto de distorsión visual
        if height > 300:
            brightness = min(1.0, brightness + 0.2)
            saturation = max(0.5, saturation - 0.2)

        r, g, b = hsv_to_rgb(hue, saturation, brightness)
        color = f'#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}'

        # Actualizar posición
        x0, y0, x1, y1 = self.canvas.coords(bar)
        new_y0 = 380 - height
        self.canvas.coords(bar, x0, new_y0, x1, 380)
        self.canvas.itemconfig(bar, fill=color)

    def toggle_animation(self):
        self.running = not self.running
        if self.running:
            self.update_bars()

if __name__ == "__main__":
    root = tk.Tk()
    eq = MetalEqualizer(root)
    root.mainloop()