import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.cm import get_cmap
from matplotlib.colors import LinearSegmentedColormap

# Configuración inicial
n_bandas = 24
fps = 60  # Más FPS para fluidez
duracion = 15  # Duración en segundos

# Frecuencias (20 Hz a 20 kHz)
frecuencias = np.logspace(np.log10(20), np.log10(20000), n_bandas)

# Paleta de colores: Azul eléctrico a Rojo (para picos)
colores = LinearSegmentedColormap.from_list('metal', ['#00008B', '#1E90FF', '#FF4500'])
cmap = get_cmap(colores)

# Inicializar figura
fig, ax = plt.subplots(figsize=(18, 8))
ax.set_facecolor('#000000')
fig.patch.set_facecolor('#000000')
bars = ax.bar(range(n_bandas), np.zeros(n_bandas), color='#1E90FF', edgecolor='cyan', lw=1)

# Configuración estética
ax.set_xticks([])
ax.set_yticks([])
ax.set_ylim(0, 1.5)
ax.set_xlim(-1, 24)

# Efecto de "distorsión" para graves (0-7)
def generar_ritmo_metal (frames):
    np.random.seed(42)
    data = np.zeros((frames, n_bandas))
    
    # Generar ritmos caóticos
    for i in range(n_bandas):
        t = np.linspace(0, 4 * np.pi, frames)
        
        # Base: Ruido Perlin (suave)
        perlin = np.sin(0.5 * t + 2 * np.pi * np.random.rand()) * 0.3
        
        # Impulsos aleatorios (más intensos en graves)
        impulsos = np.random.uniform(0, 1.2, frames) * (np.random.rand(frames) > 0.97)
        
        # Frecuencia dependiente de la banda
        freq_factor = 0.5 + i * 0.1
        heavy_distortion = np.sin(freq_factor * t + np.random.randn())**3
        
        # Combinar efectos
        data[:, i] = (perlin + impulsos + 0.5 * heavy_distortion) / 2.5
        
        # Aumentar intensidad en graves (primeras 8 bandas)
        if i < 8:
            data[:, i] *= 1.5 + 0.5 * np.sin(0.8 * t)
    
    return np.clip(data, 0, 1.5)

# Generar datos
frames = fps * duracion
ritmo = generar_ritmo_metal(frames)

# Función de animación
def animate(frame):
    for idx, bar in enumerate(bars):
        valor = ritmo[frame % frames, idx]
        
        # Color dinámico (azul a rojo en picos)
        color_val = np.clip(valor / 1.5, 0, 1)
        bar.set_height(valor)
        bar.set_color(cmap(color_val))
        bar.set_edgecolor('#00FFFF' if valor > 1.0 else '#1E90FF')
        
    # Efecto de "vibrato" en la posición horizontal (opcional)
    if frame % 5 == 0:
        for bar in bars:
            bar.set_x(bar.get_x() + np.random.uniform(-0.02, 0.02))
    
    return bars

# Animación
ani = animation.FuncAnimation(
    fig, animate,
    frames=frames,
    interval=1000//fps,
    blit=True
)

# Añadir fondo de gradiente (opcional)
gradient = np.linspace(0, 1, 256).reshape(1, -1)
ax.imshow(gradient, aspect='auto', cmap='Blues', extent=(-1, 24, 0, 1.5), alpha=0.1)

plt.show()