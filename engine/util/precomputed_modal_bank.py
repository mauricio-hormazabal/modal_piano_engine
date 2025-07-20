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
    
    def OLD_empirical_inharmonicity(self, midi_note):
        c = 1
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
    
    def get_duration(self):
        return self.duration
    
    def empirical_inharmonicity(self, midi_note):
        """
        Devuelve el coeficiente de inharmonicidad B para una nota MIDI específica (21-108)
        Valores aproximados para un piano de cola Bechstein.
        """
        B_by_note = {
            21: 0.0018,
            22: 0.00175,
            23: 0.00170,
            24: 0.00165,
            25: 0.00160,
            26: 0.00155,
            27: 0.00150,
            28: 0.00145,
            29: 0.00140,
            30: 0.00135,
            31: 0.00130,
            32: 0.00125,
            33: 0.00120,
            34: 0.00113,
            35: 0.00106,
            36: 0.00100,
            37: 0.00094,
            38: 0.00088,
            39: 0.00083,
            40: 0.00078,
            41: 0.00073,
            42: 0.00068,
            43: 0.00063,
            44: 0.00059,
            45: 0.00055,
            46: 0.00051,
            47: 0.00047,
            48: 0.00043,
            49: 0.00040,
            50: 0.00037,
            51: 0.00034,
            52: 0.00031,
            53: 0.00028,
            54: 0.00025,
            55: 0.00022,
            56: 0.00020,
            57: 0.00018,
            58: 0.00016,
            59: 0.00014,
            60: 0.00013,
            61: 0.00012,
            62: 0.00011,
            63: 0.00010,
            64: 0.00009,
            65: 0.00008,
            66: 0.00007,
            67: 0.000065,
            68: 0.000060,
            69: 0.000055,
            70: 0.000050,
            71: 0.000045,
            72: 0.000040,
            73: 0.000036,
            74: 0.000032,
            75: 0.000029,
            76: 0.000026,
            77: 0.000023,
            78: 0.000021,
            79: 0.000019,
            80: 0.000017,
            81: 0.000015,
            82: 0.000014,
            83: 0.000013,
            84: 0.000012,
            85: 0.000011,
            86: 0.000010,
            87: 0.0000095,
            88: 0.0000090,
            89: 0.0000085,
            90: 0.0000080,
            91: 0.0000075,
            92: 0.0000070,
            93: 0.0000066,
            94: 0.0000063,
            95: 0.0000060,
            96: 0.0000057,
            97: 0.0000054,
            98: 0.0000051,
            99: 0.0000049,
            100: 0.0000047,
            101: 0.0000045,
            102: 0.0000043,
            103: 0.0000041,
            104: 0.0000039,
            105: 0.0000037,
            106: 0.0000035,
            107: 0.0000033,
            108: 0.0000032,
        }

        if midi_note < 21 or midi_note > 108:
            raise ValueError("Nota MIDI fuera de rango para piano estándar (21-108).")

        return B_by_note[midi_note]
