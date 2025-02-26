import tkinter as tk
import math
import random
from colorsys import hsv_to_rgb

class EqualizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ecualizador Visual 10 Canales")
        self.root.geometry("800x600")
        
        # Configuración inicial
        self.num_bars = 10
        self.speed = 1.0
        self.rhythm_factor = 1.0
        self.color_variation = 0.5
        self.running = False
        
        # Frecuencias base para cada canal
        self.base_frequencies = [0.5 + i*0.2 for i in range(self.num_bars)]
        
        # Crear lienzo
        self.canvas = tk.Canvas(root, bg='black', height=400, width=780)
        self.canvas.pack(pady=10)
        
        # Crear controles
        self.create_controls()
        
        # Inicializar barras
        self.bars = []
        self.colors = []
        self.setup_bars()
        
    def create_controls(self):
        control_frame = tk.Frame(self.root, bg='#222')
        control_frame.pack(pady=10)
        
        # Sliders
        self.speed_slider = tk.Scale(control_frame, from_=0.1, to=5.0, resolution=0.1,
                                    label="Velocidad", orient=tk.HORIZONTAL,
                                    troughcolor='#444', fg='white', bg='#222',
                                    command=self.set_speed)
        self.speed_slider.set(1.0)
        self.speed_slider.pack(side=tk.LEFT, padx=10)
        
        self.rhythm_slider = tk.Scale(control_frame, from_=0.1, to=3.0, resolution=0.1,
                                     label="Ritmo", orient=tk.HORIZONTAL,
                                     troughcolor='#444', fg='white', bg='#222',
                                     command=self.set_rhythm)
        self.rhythm_slider.set(1.0)
        self.rhythm_slider.pack(side=tk.LEFT, padx=10)
        
        self.color_slider = tk.Scale(control_frame, from_=0.0, to=1.0, resolution=0.01,
                                    label="Variación Color", orient=tk.HORIZONTAL,
                                    troughcolor='#444', fg='white', bg='#222',
                                    command=self.set_color_variation)
        self.color_slider.set(0.5)
        self.color_slider.pack(side=tk.LEFT, padx=10)
        
        # Botones
        btn_frame = tk.Frame(control_frame, bg='#222')
        btn_frame.pack(side=tk.LEFT, padx=10)
        
        self.start_btn = tk.Button(btn_frame, text="Iniciar", command=self.toggle_animation,
                                  bg='#333', fg='white')
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        reset_btn = tk.Button(btn_frame, text="Reiniciar", command=self.reset,
                             bg='#333', fg='white')
        reset_btn.pack(side=tk.LEFT, padx=5)
        
    def setup_bars(self):
        bar_width = 70
        spacing = 10
        start_x = (800 - (self.num_bars*(bar_width + spacing))) // 2
        
        for i in range(self.num_bars):
            x0 = start_x + i*(bar_width + spacing)
            y0 = 380
            x1 = x0 + bar_width
            y1 = 380 - random.randint(20, 100)
            
            hue = i/self.num_bars + random.uniform(-0.1, 0.1)
            r, g, b = hsv_to_rgb(hue, 0.8, 0.8)
            color = f'#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}'
            
            bar = self.canvas.create_rectangle(x0, y0, x1, y1, fill=color)
            self.bars.append(bar)
            self.colors.append(color)
            
    def update_bars(self):
        if not self.running:
            return
            
        for i, bar in enumerate(self.bars):
            # Calcular altura dinámica
            height = 50 + 200 * math.sin(
                (self.root.tk.call('after', 'info', self.anim) / 1000) * 
                self.base_frequencies[i] * self.rhythm_factor
            )
            
            # Actualizar color
            hue = (i/self.num_bars + self.color_variation) % 1.0
            r, g, b = hsv_to_rgb(hue, 0.8, 0.8)
            color = f'#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}'
            
            # Actualizar posición y color
            x0, y0, x1, y1 = self.canvas.coords(bar)
            self.canvas.coords(bar, x0, 380 - height, x1, 380)
            self.canvas.itemconfig(bar, fill=color)
            
        self.anim = self.root.after(int(50/self.speed), self.update_bars)
        
    def set_speed(self, value):
        self.speed = float(value)
        
    def set_rhythm(self, value):
        self.rhythm_factor = float(value)
        
    def set_color_variation(self, value):
        self.color_variation = float(value)
        
    def toggle_animation(self):
        self.running = not self.running
        self.start_btn.config(text="Detener" if self.running else "Iniciar")
        if self.running:
            self.update_bars()
            
    def reset(self):
        self.running = False
        self.speed_slider.set(1.0)
        self.rhythm_slider.set(1.0)
        self.color_slider.set(0.5)
        self.setup_bars()
        self.start_btn.config(text="Iniciar")

if __name__ == "__main__":
    root = tk.Tk()
    app = EqualizerApp(root)
    root.mainloop()