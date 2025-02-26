import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.cm import get_cmap
from matplotlib.colors import LinearSegmentedColormap

# Configuración
n_bandas = 24
grupo_size = 3  # Barras por grupo
n_grupos = n_bandas // grupo_size
fps = 60
duracion = 12

# Frecuencias y colores
frecuencias = np.logspace(np.log10(20), np.log10(20000), n_bandas)
colores = LinearSegmentedColormap.from_list('metal', ['#00008B', '#1E90FF', '#FF4500'])
cmap = get_cmap(colores)

# Inicializar figura
fig, ax = plt.subplots(figsize=(18, 8))
ax.set_facecolor('#000000')
fig.patch.set_facecolor('#000000')
bars = ax.bar(range(n_bandas), np.zeros(n_bandas), color='#1E90FF', edgecolor='cyan', lw=0.7)

# Ajustes visuales
ax.set_xticks([])
ax.set_yticks([])
ax.set_ylim(0, 1.2)  # Altura reducida al 75%
ax.set_xlim(-1, 24)

# Generar datos por grupos (8 grupos de 3 barras)
def generar_ritmo_metal(frames):
    np.random.seed(42)
    data = np.zeros((frames, n_grupos))  # 8 grupos
    
    for grupo in range(n_grupos):
        t = np.linspace(0, 4 * np.pi, frames)
        # Graves (primeros 3 grupos)
        if grupo < 3:
            perlin = np.sin(0.7 * t + 2 * np.pi * np.random.rand()) * 0.5
            impulsos = np.random.uniform(0, 1.5, frames) * (np.random.rand(frames) > 0.95)
        # Medios y agudos
        else:
            perlin = np.sin(1.2 * t + 2 * np.pi * np.random.rand()) * 0.3
            impulsos = np.random.uniform(0, 1.0, frames) * (np.random.rand(frames) > 0.98)
        
        heavy_distortion = np.sin((0.5 + grupo * 0.2) * t)**3
        data[:, grupo] = np.clip((perlin + impulsos + 0.4 * heavy_distortion) / 2.5, 0, 1.5)
    
    # Repetir cada valor del grupo para 3 barras
    return np.repeat(data, grupo_size, axis=1) * 0.75  # Altura al 75%

# Generar y escalar datos
frames = fps * duracion
ritmo = generar_ritmo_metal(frames)

# Animación
def animate(frame):
    for grupo in range(n_grupos):
        # Índices de las 3 barras del grupo
        idx_inicio = grupo * grupo_size
        idx_fin = idx_inicio + grupo_size
        
        # Valor y color del grupo
        valor_grupo = ritmo[frame % frames, idx_inicio]
        color_val = np.clip(valor_grupo / 1.2, 0, 1)
        color = cmap(color_val)
        
        # Actualizar las 3 barras
        for idx in range(idx_inicio, idx_fin):
            bars[idx].set_height(valor_grupo)
            bars[idx].set_color(color)
            bars[idx].set_edgecolor('#00FFFF' if valor_grupo > 0.9 else '#1E90FF')
    
    # Efecto de "vibrato" en graves
    if frame % 6 == 0:
        for grupo in range(3):  # Solo primeros 3 grupos (graves)
            for idx in range(grupo * 3, (grupo + 1) * 3):
                bars[idx].set_x(bars[idx].get_x() + np.random.uniform(-0.03, 0.03))
    
    return bars

ani = animation.FuncAnimation(fig, animate, frames=frames, interval=1000//fps, blit=True)

# Añadir texto de estilo metal
ax.text(12, 1.1, 'ROCK EQUALIZER', color='#FF4500', ha='center', va='center', 
        fontsize=24, fontweight='bold', alpha=0.7)

plt.show()