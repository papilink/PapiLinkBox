import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

# Configuración inicial
frecuencias = np.logspace(np.log10(20), np.log10(20000), 24)  # 20 Hz a 20 kHz (24 bandas)
ganancias = np.zeros(24)  # Ganancias iniciales en dB

# Crear la figura y los ejes
fig, ax = plt.subplots(figsize=(15, 6))
plt.subplots_adjust(bottom=0.4)

# Dibujar el ecualizador como barras
bars = ax.bar(range(24), np.zeros(24), color='blue', alpha=0.7)
ax.set_xticks(range(24))
ax.set_xticklabels([f"{frec:.0f} Hz" for frec in frecuencias], rotation=45)
ax.set_ylim(-12, 12)
ax.set_title('Ecualizador de 24 Bandas')
ax.set_ylabel('Ganancia (dB)')

# Crear sliders para cada banda
sliders = []
for i in range(24):
    ax_slider = plt.axes([0.1 + (i % 12) * 0.07, 0.1 + (i // 12) * 0.05, 0.03, 0.03])
    slider = Slider(
        ax=ax_slider,
        label='',
        valmin=-12,
        valmax=12,
        valinit=0,
        orientation='vertical'
    )
    sliders.append(slider)

# Función para actualizar las barras al mover los sliders
def update(val):
    for j in range(24):
        ganancias[j] = sliders[j].val
        color = (
            'red' if frecuencias[j] < 300 else  # Graves (20-300 Hz)
            'green' if 300 <= frecuencias[j] < 4000 else  # Medios (300-4000 Hz)
            'blue'  # Agudos (4000-20000 Hz)
        )
        bars[j].set_height(ganancias[j])
        bars[j].set_color(color)
    fig.canvas.draw_idle()

# Asignar la función de actualización a cada slider
for slider in sliders:
    slider.on_changed(update)

plt.show()