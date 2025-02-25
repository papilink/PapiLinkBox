import tkinter as tk
import math
from time import strftime, localtime

class VintageBlueClock:
    def __init__(self, root):
        self.root = root
        self.root.title("Reloj Vintage Azul")
        self.root.configure(bg='#1A2F4B')  # Fondo azul oscuro
        
        # Crear lienzo para el reloj
        self.canvas = tk.Canvas(root, width=400, height=430, bg='#1A2F4B', 
                              highlightthickness=0)
        self.canvas.pack(pady=20)
        
        # Inicializar variables para las agujas
        self.hour_hand = None
        self.minute_hand = None
        self.second_hand = None
        self.center_pin = None
        
        # Dibujar elementos estáticos
        self.draw_clock_face()
        self.draw_decorations()
        self.draw_roman_numerals()
        
        self.update_clock()
    
    def draw_clock_face(self):
        # Círculo principal del reloj (azul claro desgastado)
        self.canvas.create_oval(50, 50, 350, 350, outline='#3A5F7F', 
                               width=8, fill='#D3E5F5')
        
        # Anillo interior decorativo
        self.canvas.create_oval(70, 70, 330, 330, outline='#2B4A6B', width=4)
    
    def draw_roman_numerals(self):
        roman_numerals = [
            'XII', 'I', 'II', 'III', 'IV', 'V',
            'VI', 'VII', 'VIII', 'IX', 'X', 'XI'
        ]
        
        center_x, center_y = 200, 200
        radius = 130
        
        for i in range(12):
            angle = math.radians(i * 30 - 90)
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            
            self.canvas.create_text(x, y, text=roman_numerals[i], 
                                  font=('Times New Roman', 14, 'bold'),
                                  fill='#2B4A6B')
    
    def draw_decorations(self):
        # Patrones decorativos en azul más oscuro
        self.canvas.create_line(50, 200, 350, 200, fill='#2B4A6B', width=2)
        self.canvas.create_line(200, 50, 200, 350, fill='#2B4A6B', width=2)
        
        # Detalles en las esquinas (remaches metálicos)
        for x, y in [(50, 50), (350, 50), (50, 350), (350, 350)]:
            self.canvas.create_oval(x-10, y-10, x+10, y+10, 
                                  fill='#3A5F7F', outline='#2B4A6B')
    
    def update_clock(self):
        current_time = localtime()
        hours = current_time.tm_hour % 12
        minutes = current_time.tm_min
        seconds = current_time.tm_sec
        
        # Calcular ángulos
        hour_angle = math.radians((hours * 30) + (minutes * 0.5) - 90)
        minute_angle = math.radians((minutes * 6) + (seconds * 0.1) - 90)
        second_angle = math.radians((seconds * 6) - 90)
        
        # Longitudes de las agujas
        lengths = {
            'hour': 70,
            'minute': 100,
            'second': 110
        }
        
        center_x, center_y = 200, 200
        
        # Eliminar agujas anteriores
        for hand in [self.hour_hand, self.minute_hand, self.second_hand]:
            if hand:
                self.canvas.delete(hand)
        
        # Dibujar nuevas agujas
        self.hour_hand = self.draw_hand(center_x, center_y, hour_angle, 
                                      lengths['hour'], '#2B4A6B', 8)
        self.minute_hand = self.draw_hand(center_x, center_y, minute_angle, 
                                        lengths['minute'], '#3A5F7F', 5)
        self.second_hand = self.draw_hand(center_x, center_y, second_angle, 
                                        lengths['second'], '#C00000', 2)
        
        # Actualizar centro del reloj
        if self.center_pin:
            self.canvas.delete(self.center_pin)
        self.center_pin = self.canvas.create_oval(195, 195, 205, 205, 
                                                fill='#C00000', outline='#2B4A6B')
        
        # Programar próxima actualización
        self.root.after(1000, self.update_clock)
    
    def draw_hand(self, x, y, angle, length, color, width):
        end_x = x + length * math.cos(angle)
        end_y = y + length * math.sin(angle)
        return self.canvas.create_line(x, y, end_x, end_y,
                                     width=width, fill=color,
                                     arrow='last', arrowshape=(16, 20, 6))

if __name__ == "__main__":
    root = tk.Tk()
    clock = VintageBlueClock(root)
    root.mainloop()