import numpy as np
import sounddevice as sd
import threading
from .util.precomputed_modal_bank import PrecomputedModalBank as modalBank

from queue import Queue

from core.base_synthesis import generate_realistic_modal_signal
from core.sympathetic_resonance import generate_sympathetic_response
from scipy.signal import lfilter, butter

from .util.engine_functions import precalculate_inharmonicity_matrix, precalculate_hammer_shape_matrix, adaptive_num_modes, precalculate_gain_decay



# === Voz de Nota Precargada ===
class NoteVoice:
    def __init__(self, midi_note, velocity, fs, signal):
        self.midi_note = midi_note
        self.velocity = velocity
        self.fs = fs
        self.signal = signal
        self.position = 0
        self.length = len(signal)
        self.done = False

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

# === Motor de Audio Optimizado ===
class AudioEngine:
    def __init__(self, fs=44100, blocksize=2048, use_soft_clip=False):
        self.fs = fs
        self.blocksize = blocksize
        self.use_soft_clip = use_soft_clip
        self.voices = []
        self.lock = threading.Lock()
        self.note_queue = Queue()
        # Pre carga
        self.inharmonicity_matrix = precalculate_inharmonicity_matrix()
        self.inharmonicity_matrix_res = precalculate_inharmonicity_matrix(0.0001) # B=0.0001
        self.hammer_matrix = precalculate_hammer_shape_matrix()
        self.hammer_gain_decay = precalculate_gain_decay()
        #notas activas
        self.active_notes = []
        self.modal_bank = modalBank(
            samplerate=fs, 
            duration=2.5, 
            num_modes=14 #debe coincidir con adaptive num modes
        )

        self.stream = sd.OutputStream(
            channels=1,
            samplerate=fs,
            blocksize=blocksize,
            latency='low',
            callback=self.callback
        )
        self.stream.start()

        self.thread = threading.Thread(target=self.worker_thread)
        self.thread.daemon = True
        self.thread.start()

    def note_on(self, midi_note, velocity):
        self.note_queue.put((midi_note, velocity))
        #notas activas
        self.active_notes.append(midi_note)
        #if velocity==0:
        #    self.note_off(midi_note)

    def note_off(self, midi_note):
        #notas activas
        self.active_notes.remove(midi_note)


    def stop(self):
        self.stream.stop()
        self.stream.close()

    def worker_thread(self):
        while True:
            midi_note, velocity = self.note_queue.get()
            n_modes = adaptive_num_modes(midi_note)
            #signal = generate_realistic_modal_signal(midi_note, fs=self.fs,
            #                                        num_modes=n_modes, velocity=velocity)
            signal = generate_realistic_modal_signal(midi_note, fs=self.fs,
                                                    num_modes=n_modes, velocity=velocity,
                                                    inh_matrix=self.inharmonicity_matrix,
                                                    gd_values=self.hammer_gain_decay,
                                                    mod_bank=self.modal_bank,
                                                    hammer_matrix=self.hammer_matrix)
            

            resonance = generate_sympathetic_response(self.fs, midi_note, velocity, 
                                                      self.active_notes, self.inharmonicity_matrix_res,
                                                      gd_values=self.hammer_gain_decay, 
                                                      mod_bank=self.modal_bank,
                                                      gain=0.012) #gain original 0.01 #0.05 Ok

            #b_cb, a_cb = butter(N=2, Wn=2050, btype='low', fs=self.fs)
            #signal_res_cab = lfilter(b_cb, a_cb, (resonance + signal))

            """"      
            b_sb, a_sb = butter(N=2, Wn=[80, 2000], btype='bandpass', fs=self.fs)
            b_cb, a_cb = butter(N=2, Wn=150, btype='low', fs=self.fs)

            signal = lfilter(b_sb, a_sb, signal)
            signal = lfilter(b_cb, a_cb, signal)
            """

            voice = NoteVoice(midi_note, velocity, self.fs, signal)
            res_voice = NoteVoice(midi_note, velocity, self.fs, resonance)
            #rc_voice = NoteVoice(midi_note, velocity, self.fs, signal_res_cab)
            with self.lock:
                self.voices.append(voice)
                self.voices.append(res_voice)
                #self.voices.append(rc_voice)

    def callback(self, outdata, frames, time_info, status):
        buffer = np.zeros(frames)
        with self.lock:
            for voice in self.voices:
                buffer += voice.get_samples(frames)
            self.voices = [v for v in self.voices if not v.done]

        outdata[:, 0] = buffer
