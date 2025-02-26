import numpy as np
import matplotlib.pyplot as plt
import pyaudio
from scipy.fft import rfft, rfftfreq

# Configuración inicial
CHUNK = 1024 * 4
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

# Inicializar PyAudio
p = pyaudio.PyAudio()

# Configurar stream de audio
stream = p.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    output=True,
    frames_per_buffer=CHUNK
)

# Crear figura para visualización
fig, ax = plt.subplots()
x = rfftfreq(CHUNK, 1/RATE)
line, = ax.semilogx(x, np.random.rand(CHUNK//2 + 1))
ax.set_ylim(0, 1000)
ax.set_xlim(20, RATE/2)

# Función de actualización en tiempo real
def update(frame):
    data = stream.read(CHUNK, exception_on_overflow=False)
    data_np = np.frombuffer(data, dtype=np.int16)
    y = rfft(data_np)
    line.set_ydata(np.abs(y))
    return line,

# Configurar animación
from matplotlib.animation import FuncAnimation
ani = FuncAnimation(fig, update, blit=True, interval=0)
plt.show()