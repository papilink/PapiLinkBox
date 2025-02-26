import tkinter as tk
import math
import random
from colorsys import hsv_to_rgb
import time

class TurboEqualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Ecualizador Turbo")
        self.root.geometry("1000x800")
        
        # Configuración avanzada
        self.num_bars = 10
        self.speed = 2.0  # Velocidad base aumentada
        self.rhythm_factor = 1.5  # Ritmo más marcado
        self.color_speed = 0.05  # Velocidad de cambio de color
        self.running = False
        self.start_time = time.time()
        
        # Frecuencias más rápidas y variadas
        self.base_frequencies = [random.uniform(1.5, 3.0) for _ in range(self.num_bars)]
        
        # Configuración del lienzo
        self.canvas = tk.Canvas(root, bg='#000000', height=600, width=950)
        self.canvas.pack(pady=20)
        
        # Controles mejorados
        self.create_enhanced_controls()
        self.setup_bars()
        
    def create_enhanced_controls(self):
        control_frame = tk.Frame(self.root, bg='#111111')
        control_frame.pack(pady=15)
        
        # Sliders de control mejorados
        controls = [
            ("Velocidad", 0.5, 20.0, self.speed, self.set_speed),
            ("Ritmo", 0.1, 5.0, self.rhythm_factor, self.set_rhythm),
            ("Color", 0.01, 0.5, self.color_speed, self.set_color_speed),
            ("Saturación", 0.5, 1.0, 0.9, self.set_saturation),
            ("Brillo", 0.5, 1.0, 0.9, self.set_brightness)
        ]
        
        for text, min_val, max_val, default, command in controls:
            slider = tk.Scale(control_frame, from_=min_val, to=max_val, resolution=0.01,
                             label=text, orient=tk.HORIZONTAL,
                             troughcolor='#333333', fg='#FFFFFF', bg='#222222',
                             length=200, command=command)
            slider.set(default)
            slider.pack(side=tk.LEFT, padx=10)
        
        # Botones de control
        btn_frame = tk.Frame(control_frame, bg='#111111')
        btn_frame.pack(side=tk.LEFT, padx=15)
        
        self.start_btn = tk.Button(btn_frame, text="Iniciar", command=self.toggle_animation,
                                  bg='#444444', fg='white', font=('Arial', 10, 'bold'))
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="Randomizar", command=self.randomize,
                bg='#444444', fg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)
        
    def setup_bars(self):
        self.bars = []
        self.colors = []
        bar_width = 80
        spacing = 15
        start_x = (950 - (self.num_bars*(bar_width + spacing))) // 2
        
        for i in range(self.num_bars):
            x0 = start_x + i*(bar_width + spacing)
            height = random.randint(50, 300)
            self.create_bar(x0, height, i)
            
    def create_bar(self, x0, height, index):
        y0 = 580
        x1 = x0 + 80
        y1 = y0 - height
        
        # Patrón de color complejo
        hue = (index/self.num_bars + (time.time() - self.start_time)*self.color_speed) % 1.0
        saturation = 0.8 + math.sin(time.time() * 2) * 0.1
        value = 0.8 + math.sin(time.time() * 3) * 0.1
        
        r, g, b = hsv_to_rgb(hue, saturation, value)
        color = f'#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}'
        
        # Crear barra con efecto de degradado
        bar = self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, width=0)
        self.bars.append(bar)
        self.colors.append(color)
        
    def update_bars(self):
        if not self.running:
            return
            
        current_time = time.time()
        time_delta = current_time - self.start_time
        
        for i, bar in enumerate(self.bars):
            # Movimiento hiperdinámico
            height = 200 + 250 * math.sin(
                time_delta * self.base_frequencies[i] * self.rhythm_factor +
                math.pi * i/self.num_bars
            ) * math.cos(time_delta * 0.5)
            
            # Efecto de color psicodélico
            hue = (i/self.num_bars + time_delta * self.color_speed) % 1.0
            saturation = max(0.6, math.sin(time_delta * 2 + i) * 0.3 + 0.7)
            value = max(0.6, math.cos(time_delta * 3 + i) * 0.3 + 0.7)
            
            r, g, b = hsv_to_rgb(hue, saturation, value)
            color = f'#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}'
            
            # Actualizar barra
            x0, y0, x1, y1 = self.canvas.coords(bar)
            self.canvas.coords(bar, x0, 580 - height, x1, 580)
            self.canvas.itemconfig(bar, fill=color)
            
        self.anim = self.root.after(int(20 / self.speed), self.update_bars)
        
    def set_speed(self, value):
        self.speed = float(value)
        
    def set_rhythm(self, value):
        self.rhythm_factor = float(value)
        
    def set_color_speed(self, value):
        self.color_speed = float(value)
        
    def set_saturation(self, value):
        self.saturation = float(value)
        
    def set_brightness(self, value):
        self.brightness = float(value)
        
    def toggle_animation(self):
        self.running = not self.running
        self.start_btn.config(text="Detener" if self.running else "Iniciar")
        if self.running:
            self.start_time = time.time()
            self.update_bars()
            
    def randomize(self):
        self.base_frequencies = [random.uniform(1.0, 5.0) for _ in range(self.num_bars)]
        self.color_speed = random.uniform(0.01, 0.3)
        self.rhythm_factor = random.uniform(0.5, 3.0)
        self.setup_bars()

if __name__ == "__main__":
    root = tk.Tk()
    app = TurboEqualizer(root)
    root.mainloop()