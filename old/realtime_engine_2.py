import numpy as np
import sounddevice as sd
import threading
import time
from core.base_synthesis import generate_realistic_modal_signal

def normalize_audio(buffer, soft_clip=False):
    if soft_clip:
        return np.tanh(buffer)
    else:
        peak = np.max(np.abs(buffer)) + 1e-6
        return buffer / peak


class NoteVoice:
    def __init__(self, midi_note, velocity, fs, duration=2.0):
        self.fs = fs
        self.position = 0
        self.n_modes = self.adaptive_num_modes(midi_note)
        self.signal = generate_realistic_modal_signal(midi_note, fs, num_modes=self.n_modes, velocity=velocity)
        self.length = len(self.signal)
        self.done = False

    def adaptive_num_modes(self, midi_note):
        if midi_note < 40: return 14  # graves
        elif midi_note < 60: return 10
        elif midi_note < 75: return 6
        else: return 4

    def get_samples(self, frames):
        if self.position >= self.length:
            self.done = True
            return np.zeros(frames)
        end = min(self.position + frames, self.length)
        chunk = self.signal[self.position:end]
        if len(chunk) < frames:  # <-- si el trozo de signal es menor que los frames requeridos, se rellena de 0's
            chunk = np.pad(chunk, (0, frames - len(chunk)))
            self.done = True # <--se marca la voz como terminado (se maneja en el callback)
        self.position = end
        return chunk

class AudioEngine:
    def __init__(self, fs=44100, blocksize=512, use_soft_clip=False):
        self.fs = fs
        self.blocksize = blocksize
        self.voices = []
        self.lock = threading.Lock()
        self.use_soft_clip = use_soft_clip
        self.stream = sd.OutputStream(channels=1,
                                      samplerate=fs,
                                      blocksize=blocksize,
                                      callback=self.callback)
        self.stream.start()

    def callback(self, outdata, frames, time_info, status):
        # Relleno con ceros un buffer de tamaño frames
        buffer = np.zeros(frames)
        with self.lock: # <-- Aquí se adquiere y libera automáticamente el lock
            for voice in self.voices: # <-- para cada voz 
                buffer += voice.get_samples(frames) # <-- se obtienen frames muestras (frames x 1, audio mono)
            self.voices = [v for v in self.voices if not v.done] # <-- elimina las voces que ya han terminado
        # Mezcla segura: normaliza o aplica soft clip
        buffer = normalize_audio(buffer, soft_clip=self.use_soft_clip)
        #buffer /= max(np.max(np.abs(buffer)), 1.0)
        outdata[:, 0] = buffer

    def note_on(self, midi_note, velocity):
        with self.lock:
            self.voices.append(NoteVoice(midi_note, velocity, self.fs))

    def note_off(self, midi_note):
        pass

    def stop(self):
        self.stream.stop()
        self.stream.close()
