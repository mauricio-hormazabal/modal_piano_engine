import numpy as np
import sounddevice as sd
from collections import defaultdict
from core.base_synthesis import generate_realistic_modal_signal, generate_sympathetic_response
from core.sympathetic_resonance2 import generate_sympathetic_response
from core.soundboard_model import simulate_soundboard_response, extract_excited_soundboard_modes
from core.soundboard_sympathetic2 import excite_free_strings_via_soundboard, find_strings_resonant_with_soundboard_modes

class PianoEngine:
    def __init__(self, fs=44100, duration=2.0):
        self.fs = fs
        self.duration = duration
        self.active_notes = {}
        self.sustain = False

    def handle_note_on(self, midi_note, velocity):
        print(f"[Note ON] {midi_note} vel={velocity:.2f}")
        self.active_notes[midi_note] = velocity
        self._synthesize()

    def handle_note_off(self, midi_note):
        print(f"[Note OFF] {midi_note}")
        if midi_note in self.active_notes:
            del self.active_notes[midi_note]
        if not self.sustain:
            self._synthesize()

    def handle_sustain(self, is_pressed):
        print(f"[Sustain] {'ON' if is_pressed else 'OFF'}")
        self.sustain = is_pressed
        if not is_pressed:
            self._synthesize()

    # Numero de modos dependiendo de la nota
    def adaptive_num_modes(midi_note):
        if midi_note < 40: return 14  # graves
        elif midi_note < 60: return 10
        elif midi_note < 75: return 6
        else: return 4

    def _synthesize(self):
        if not self.active_notes:
            return

        
        # Generar señal base de notas activas
        signals = []
        active_list = list(self.active_notes.items())
        for note, velocity in active_list:
            # numero de modos
            #n_modes = self.adaptive_num_modes(note)
            sig = generate_realistic_modal_signal(note, self.duration, self.fs, num_modes=10, velocity=velocity)
            signals.append(sig)
        signal = np.sum(signals, axis=0)

        # Determinar cuerdas libres
        all_notes = set(range(21, 109))
        notes_down = set(self.active_notes.keys())
        if self.sustain:
            free_notes = list(all_notes - notes_down)
        else:
            free_notes = []

        # Resonancia simpática
        sympathetic = generate_sympathetic_response(fs=self.fs,
                                                    duration=self.duration,
                                                    active_notes=active_list)

        # Soundboard (modos de tabla + respuesta de tabla)
        tabla_modes_activados = extract_excited_soundboard_modes(active_list)
        soundboard = simulate_soundboard_response(fs=self.fs,
                                                  duration=self.duration,
                                                  active_notes=active_list)

        # Resonancia cruzada tabla → cuerdas
        symp_board = excite_free_strings_via_soundboard(active_list,    # no son las free_notes, son las active
                                                        tabla_modes_activados,
                                                        fs=self.fs,
                                                        duration=self.duration)

        full = signal + sympathetic + soundboard + symp_board

        full /= np.max(np.abs(full)) + 1e-6
        sd.play(full, self.fs)
