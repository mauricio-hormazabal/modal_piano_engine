import numpy as np


class PrecomputedModalBank:
    def __init__(self, samplerate=44100, duration=2.0, num_modes=12):
        self.fs = samplerate
        self.duration = duration
        self.num_modes = num_modes
        self.t = np.linspace(0, duration, int(samplerate * duration))
        self.phase = np.pi / 2  # Start at zero crossing
        self.bank = dict()
        self._generate_bank()

    def _generate_bank(self):
        for midi_note in range(21, 109):
            f0 = self.midi_to_freq(midi_note)
            B = self.empirical_inharmonicity(midi_note)
            for n in range(1, self.num_modes + 1):
                f_n = f0 * n * np.sqrt(1 + B * n**2)
                wave = np.cos(2 * np.pi * f_n * self.t + self.phase)
                self.bank[(midi_note, n)] = wave

    def get_mode_wave(self, midi_note, mode_index):
        return self.bank.get((midi_note, mode_index), np.zeros_like(self.t))

    def get_time_vector(self):
        return self.t
    
    def empirical_inharmonicity(self, midi_note):
        c = 0.6
        if midi_note <= 31:
            return 0.0010*c
        elif midi_note <= 43:
            return 0.0006*c
        elif midi_note <= 55:
            return 0.0003*c
        elif midi_note <= 67:
            return 0.00015*c
        elif midi_note <= 79:
            return 0.00007*c
        elif midi_note <= 89:
            return 0.00003*c
        else:
            return 0.000015*c
        
    def midi_to_freq(self, midi_note):
        return 440.0 * (2 ** ((midi_note - 69) / 12))