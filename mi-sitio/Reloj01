import tkinter as tk
import math
import time

# Configuración de la ventana
root = tk.Tk()
root.title("Reloj Militar Analógico")
root.attributes("-fullscreen", True)  # Pantalla completa
width = root.winfo_screenwidth()  # Ancho de la pantalla
height = root.winfo_screenheight()  # Alto de la pantalla

# Crear un lienzo para dibujar el reloj
canvas = tk.Canvas(root, width=width, height=height, bg="black")
canvas.pack()

# Función para dibujar el reloj
def draw_clock():
    canvas.delete("all")  # Limpiar el lienzo

    # Obtener la hora actual
    current_time = time.localtime()
    hours = current_time.tm_hour
    minutes = current_time.tm_min
    seconds = current_time.tm_sec

    # Ajustar las horas al formato de 12 horas para el reloj analógico
    hours = hours % 12

    # Calcular ángulos para las manecillas
    hour_angle = math.radians((hours * 30) + (minutes * 0.5) - 90)
    minute_angle = math.radians((minutes * 6) - 90)
    second_angle = math.radians((seconds * 6) - 90)

    # Dibujar el círculo del reloj
    clock_radius = min(width, height) * 0.4
    canvas.create_oval(
        width / 2 - clock_radius,
        height / 2 - clock_radius,
        width / 2 + clock_radius,
        height / 2 + clock_radius,
        outline="white",
        width=2,
    )

    # Dibujar los números del reloj (formato 24 horas)
    for i in range(1, 25):
        angle = math.radians((i * 15) - 90)  # 24 horas = 360 grados / 24 = 15 grados por hora
        x = width / 2 + (clock_radius * 0.85) * math.cos(angle)
        y = height / 2 + (clock_radius * 0.85) * math.sin(angle)
        canvas.create_text(x, y, text=str(i), font=("Arial", 12), fill="white")

    # Dibujar la manecilla de las horas
    hour_length = clock_radius * 0.5
    hour_x = width / 2 + hour_length * math.cos(hour_angle)
    hour_y = height / 2 + hour_length * math.sin(hour_angle)
    canvas.create_line(
        width / 2, height / 2, hour_x, hour_y, fill="white", width=6
    )

    # Dibujar la manecilla de los minutos
    minute_length = clock_radius * 0.7
    minute_x = width / 2 + minute_length * math.cos(minute_angle)
    minute_y = height / 2 + minute_length * math.sin(minute_angle)
    canvas.create_line(
        width / 2, height / 2, minute_x, minute_y, fill="white", width=4
    )

    # Dibujar la manecilla de los segundos
    second_length = clock_radius * 0.8
    second_x = width / 2 + second_length * math.cos(second_angle)
    second_y = height / 2 + second_length * math.sin(second_angle)
    canvas.create_line(
        width / 2, height / 2, second_x, second_y, fill="red", width=2
    )

    # Actualizar el reloj cada segundo
    root.after(1000, draw_clock)

# Iniciar el reloj
draw_clock()

# Salir de la pantalla completa con la tecla "Esc"
def exit_fullscreen(event):
    root.attributes("-fullscreen", False)

root.bind("<Escape>", exit_fullscreen)

# Ejecutar la aplicación
root.mainloop()