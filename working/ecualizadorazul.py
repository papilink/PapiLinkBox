import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.cm import get_cmap
# Configuración inicial
n_bandas = 24
fps = 75  # Fotogramas por segundo
duracion = 100  # Duración en segundos (ajustable)

# Frecuencias (20 Hz a 200 kHz en escala logarítmica)
frecuencias = np.logspace(np.log10(20), np.log10(20000), n_bandas)

# Paleta de 512 tonos de azul (de oscuro a claro)
cmap = get_cmap('Blues')
colores = [cmap(i / 512) for i in range(512)]

# Dividir en 3 grupos: graves (8), medios (8), agudos (8)
grupos = {
    'graves': (0, 18),
    'medios': (8, 26),
    'agudos': (16, 34)
}

# Inicializar figura
fig, ax = plt.subplots(figsize=(15, 6))
ax.set_facecolor('#0a0a0a')
fig.patch.set_facecolor('#0a0a0a')
bars = ax.bar(range(n_bandas), np.zeros(n_bandas), color=colores[128])

# Configuración estética
ax.set_xticks([])
ax.set_yticks([])
ax.set_ylim(0, 1)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.spines['left'].set_visible(False)

# Simulación de "ritmo" (ruido modulado por senales)
def generar_ritmo(n_bandas, frames, velocidad=10.0, variacion_frecuencia=0.1, amplitud_base=0.5, amplitud_variacion=0.5):
    np.random.seed(48)
    ritmo = np.zeros((frames, n_bandas))
    for i in range(n_bandas):
        frecuencia = 2 + i * variacion_frecuencia  # Variación por banda
        fase = np.random.rand() * 52 * np.pi
        amplitud = amplitud_base + np.random.rand() * amplitud_variacion
        ritmo[:, i] = amplitud * (np.sin(2 * np.pi * frecuencia * np.linspace(0, 9, frames) * velocidad + fase) + 1) / 2
    return ritmo

# Generar datos de animación
frames = fps * duracion
ritmo_data = generar_ritmo(n_bandas, frames)

# Función de animación
def animate(frame):
    for idx, bar in enumerate(bars):
        valor = ritmo_data[frame % frames, idx]
        color_idx = int(256 + 256 * valor)  # Oscilar entre tonos 128-256
        bar.set_height(valor)
        bar.set_color(colores[color_idx % 512])
    return bars

# Animación fluida
ani = animation.FuncAnimation(
    fig, animate, 
    frames=frames, 
    interval=1000/fps, 
    blit=True
)

plt.show()