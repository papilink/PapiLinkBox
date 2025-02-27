import tkinter as tk
import time
import threading
from pythonosc.udp_client import SimpleUDPClient

client = SimpleUDPClient("127.0.0.1", 57110)

# Lista de notas seleccionadas
sequence = []

# Flag to control playback
playing = False

# Agregar nota a la secuencia
def add_note(note):
    sequence.append(note)

# Reproducir secuencia en bucle
def play_sequence():
    global playing
    playing = True
    while playing:
        for note in sequence:
            if not playing:
                break
            client.send_message("/s_new", ["sineSynth", -1, 0, 1, "freq", note, "amp", 0.3, "dur", 0.5])
            time.sleep(0.5)

# Detener la reproducción
def stop_sequence():
    global playing
    playing = False

# Limpiar la secuencia
def clear_sequence():
    global sequence
    sequence = []

# Interfaz gráfica
root = tk.Tk()
root.title("Secuenciador DAW")

notes = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25]

for note in notes:
    btn = tk.Button(root, text=str(note), command=lambda n=note: add_note(n))
    btn.pack(pady=5)

play_btn = tk.Button(root, text="Play", command=lambda: threading.Thread(target=play_sequence).start())
play_btn.pack()

stop_btn = tk.Button(root, text="Stop", command=stop_sequence)
stop_btn.pack()

clear_btn = tk.Button(root, text="Clear", command=clear_sequence)
clear_btn.pack()

root.mainloop()
