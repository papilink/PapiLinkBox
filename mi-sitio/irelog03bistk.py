import tkinter as tk
import math
from time import strftime, localtime

class VintageClock:
    def __init__(self, root):
        self.root = root
        self.root.title("Reloj Antiguo")
        self.root.configure(bg='#2E1E0F')  # Color fondo marrón oscuro
        
        # Crear lienzo para el reloj
        self.canvas = tk.Canvas(root, width=400, height=430, bg='#2E1E0F', 
                              highlightthickness=0, relief='ridge')
        self.canvas.pack(pady=20)
        
        # Dibujar elementos estáticos
        self.draw_clock_face()
        self.draw_decorations()
        self.draw_roman_numerals()
        
        # Inicializar agujas
        self.hour_hand = None
        self.minute_hand = None
        self.second_hand = None
        self.center_pin = None
        
        self.update_clock()
    
    def draw_clock_face(self):
        # Círculo principal del reloj
        self.canvas.create_oval(50, 50, 350, 350, outline='#8B7355', 
                               width=8, fill='#F5DEB3')  # Beige antiguo
        
        # Anillo interior decorativo
        self.canvas.create_oval(70, 70, 330, 330, outline='#654321', 
                               width=4)







                               
    
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
            
            # Dibujar números romanos
            self.canvas.create_text(x, y, text=roman_numerals[i], 
                                  font=('Times New Roman', 14, 'bold'),
                                  fill='#4D2E0A')
    
    def draw_decorations(self):
        # Patrones decorativos
        self.canvas.create_line(50, 200, 350, 200, fill='#654321', width=2)
        self.canvas.create_line(200, 50, 200, 350, fill='#654321', width=2)
        
        # Detalles en las esquinas
        for x, y in [(50, 50), (350, 50), (50, 350), (350, 350)]:
            self.canvas.create_oval(x-10, y-10, x+10, y+10, 
                                  fill='#8B7355', outline='#654321')
    
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
        hour_length = 70
        minute_length = 100
        second_length = 110
        
        center_x, center_y = 200, 200
        
        # Actualizar agujas
        self.draw_hand(center_x, center_y, hour_angle, hour_length, '#4D2E0A', 8, self.hour_hand)
        self.draw_hand(center_x, center_y, minute_angle, minute_length, '#654321', 5, self.minute_hand)
        self.draw_hand(center_x, center_y, second_angle, second_length, '#8B0000', 2, self.second_hand)
        
        # Centro del reloj
        if self.center_pin:
            self.canvas.delete(self.center_pin)
        self.center_pin = self.canvas.create_oval(195, 195, 205, 205, 
                                                fill='#8B0000', outline='#4D2E0A')
        
        # Actualizar cada segundo
        self.root.after(1000, self.update_clock)
    
    def draw_hand(self, x, y, angle, length, color, width, hand):
        end_x = x + length * math.cos(angle)
        end_y = y + length * math.sin(angle)
        
        if hand:
            self.canvas.delete(hand)
        return self.canvas.create_line(x, y, end_x, end_y, 
                                     width=width, fill=color, 
                                     arrow='last', arrowshape=(16, 20, 6))

if __name__ == "__main__":
    root = tk.Tk()
    clock = VintageClock(root)
    root.mainloop()