from engine.realtime_engine import AudioEngine
from midi.midi_interface import MIDIEngineInterface
import time


class PianoWrapper:
    def __init__(self):
        self.engine = AudioEngine(use_soft_clip=True, blocksize=512, fs=11025)

    def handle_note_on(self, midi_note, velocity):
        self.engine.note_on(midi_note, velocity)

    def handle_note_off(self, midi_note):
        self.engine.note_off(midi_note)

    def handle_sustain(self, is_pressed):
        pass  # se puede implementar si se desea

if __name__ == '__main__':
    try:
        print("Iniciando Real-Time Audio Engine y conexión MIDI...")
        piano = PianoWrapper()
        midi = MIDIEngineInterface(piano)
        try:
            midi.start()
        except RuntimeError:
            print("MIDI: No se encontraron dispositivos MIDI.")
            exit()

        print("MIDI conectado. Esperando eventos (Ctrl+C para salir)...")
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        print("\nInterrupción detectada. Cerrando motor...")
        midi.stop()
        print("Apagado completo.")