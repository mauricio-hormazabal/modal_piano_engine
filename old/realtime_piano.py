from core.piano_engine import PianoEngine
from midi.midi_interface import MIDIEngineInterface
import time

# Instanciar el motor de síntesis
engine = PianoEngine(fs=44100, duration=2.0)

# Instanciar la interfaz MIDI, usando el primer puerto disponible
midi = MIDIEngineInterface(engine)

# Iniciar escucha MIDI
midi.start()

print("🎹 Esperando eventos MIDI en tiempo real (Ctrl+C para salir)...")

try:
    while True:
        time.sleep(0.5)
except KeyboardInterrupt:
    print("\n🛑 Terminando...")
    midi.stop()
