import tkinter as tk
from time import strftime

class StylishClock:
    def __init__(self, root):
        self.root = root
        self.root.title("Reloj Estilizado")
        self.root.configure(bg='#2C3E50')  # Color de fondo oscuro
        self.root.resizable(False, False)
        
        # Marco principal con efecto de relieve
        self.frame = tk.Frame(root, bg='#34495E', bd=5, relief='ridge')
        self.frame.pack(padx=20, pady=20)
        
        # Etiqueta para la hora
        self.time_label = tk.Label(self.frame, 
                                 font=('Helvetica', 80, 'bold'),
                                 fg='#ECF0F1',
                                 bg='#34495E')
        self.time_label.pack(pady=10, padx=20)
        
        # Etiqueta para AM/PM
        self.ampm_label = tk.Label(self.frame,
                                  font=('Helvetica', 20),
                                  fg='#BDC3C7',
                                  bg='#34495E')
        self.ampm_label.pack()
        
        # Etiqueta para la fecha
        self.date_label = tk.Label(root,
                                 font=('Helvetica', 18),
                                 fg='#BDC3C7',
                                 bg='#2C3E50')
        self.date_label.pack(pady=10)
        
        # Botón de salida estilizado
        self.close_btn = tk.Button(root,
                                 text="Cerrar",
                                 font=('Helvetica', 12, 'bold'),
                                 bg='#E74C3C',
                                 fg='white',
                                 activebackground='#C0392B',
                                 command=root.destroy)
        self.close_btn.pack(pady=10)
        
        self.update_time()
        self.create_animations()

    def update_time(self):
        # Obtener hora actual en formato 12 horas
        time_string = strftime('%I:%M:%S')
        am_pm = strftime('%p')
        date_string = strftime('%A, %d %B %Y')
        
        # Actualizar etiquetas
        self.time_label.config(text=time_string)
        self.ampm_label.config(text=am_pm)
        self.date_label.config(text=date_string)
        
        # Programar próxima actualización
        self.time_label.after(1000, self.update_time)

    def create_animations(self):
        # Animación de cambio de color suave
        self.animate_label(self.time_label, ['#ECF0F1', '#BDC3C7'], 0)
        
        # Efecto hover para el botón
        self.close_btn.bind("<Enter>", lambda e: self.close_btn.config(bg='#C0392B'))
        self.close_btn.bind("<Leave>", lambda e: self.close_btn.config(bg='#E74C3C'))

    def animate_label(self, widget, colors, index):
        widget.config(fg=colors[index])
        next_index = (index + 1) % len(colors)
        widget.after(500, lambda: self.animate_label(widget, colors, next_index))

if __name__ == "__main__":
    root = tk.Tk()
    clock = StylishClock(root)
    root.mainloop()