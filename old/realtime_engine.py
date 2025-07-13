
import numpy as np
import sounddevice as sd
import threading
import time

from core.base_synthesis import generate_realistic_modal_signal

class NoteVoice:
    def __init__(self, midi_note, velocity, fs, duration=2.0):
        self.fs = fs
        self.position = 0
        self.n_modes = self.adaptive_num_modes(midi_note)
        self.signal = generate_realistic_modal_signal(midi_note, duration, fs, num_modes=self.n_modes, velocity=velocity)
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
        if len(chunk) < frames:
            chunk = np.pad(chunk, (0, frames - len(chunk)))
            self.done = True
        self.position = end
        return chunk

class AudioEngine:
    def __init__(self, fs=44100, blocksize=512):
        self.fs = fs
        self.blocksize = blocksize
        self.voices = []
        self.lock = threading.Lock()
        self.stream = sd.OutputStream(channels=1,
                                      samplerate=fs,
                                      blocksize=blocksize,
                                      callback=self.callback)
        self.stream.start()

    def callback(self, outdata, frames, time_info, status):
        buffer = np.zeros(frames)
        with self.lock:
            for voice in self.voices:
                buffer += voice.get_samples(frames)
            self.voices = [v for v in self.voices if not v.done]
        outdata[:, 0] = buffer

    def note_on(self, midi_note, velocity):
        with self.lock:
            self.voices.append(NoteVoice(midi_note, velocity, self.fs))

    def note_off(self, midi_note):
        pass  # No acción necesaria en esta versión básica

    def stop(self):
        self.stream.stop()
        self.stream.close()
