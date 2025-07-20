import numpy as np

# === Utilidades Buffer ===
"""
Esto no funciona, por que el buffer va leyendo las "voces" para ponerlas en el outpustream. Cuando corta una voz en la mitad
despues se normaliza sobre la otra mitad, que al ser el residuo con mayor decaimiento, vuelve a escalarse a nivel máximo.

"""
def normalize_audio(buffer, soft_clip=False):
    if soft_clip:
        return np.tanh(buffer)
    else:
        peak = np.max(np.abs(buffer)) + 1e-6
        return buffer / (peak*10)

def soft_limiter(signal, threshold=0.8):
    return np.tanh(signal / threshold) * threshold




## Al iniciar el engine se hace una precarga de tablas con precalculos.

def precalculate_inharmonicity_matrix(b_coef=0):
    midi_notes = range(1, 128)  # Todos los posibles valores de notas MIDI
    n_values = range(1, 15)
    matrix = {}

    for midi_note in midi_notes:
        if b_coef == 0:
            B = empirical_inharmonicity(midi_note)
        else:
            B= b_coef

        matrix[midi_note] = {}
        for n in n_values:
            value = np.sqrt(1 + B * n**2)
            matrix[midi_note][n] = value
    
    return matrix

def OLD_empirical_inharmonicity(midi_note):
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

def precalculate_hammer_shape_matrix():
    midi_notes = range(1, 128)  # Todos los posibles valores de notas MIDI
    n_values = range(1, 15)
    matrix = {}

    for midi_note in midi_notes:
        contact_point = hammer_contact_point_bechstein(midi_note)
        matrix[midi_note] = {}
        for n in n_values:
            value = np.sin(np.pi * n * contact_point)
            matrix[midi_note][n] = value
    
    return matrix

def precalculate_gain_decay():
    n_values = range(1, 15)
    gd = {}
    for n in n_values:
        gd[n] = (1.0 / n) * np.exp(-0.2 * n)
    return gd

def hammer_contact_point(midi_note):
    return 0.10 + (midi_note / 127.0) * 0.13

def hammer_contact_point_bechstein(midi_note):
    return 0.12 + (midi_note / 127.0) * 0.08

def hammer_contact_point_steinway(midi_note):
    return 0.11 + (midi_note / 127.0) * 0.03

def hammer_contact_point_yamaha(midi_note):
    return 0.11 + (midi_note / 127.0) * 0.015

def hammer_contact_point_bosendorfer(midi_note):
    return 0.11 + (midi_note / 127.0) * 0.023


# Adapta el numero de modos de cada nota según rango en que se encuentra.
def adaptive_num_modes(midi_note):
    if midi_note < 40: return 14 # 14
    elif midi_note < 60: return 10 # 10
    elif midi_note < 75: return 8 # 6
    else: return 6 #4

def empirical_inharmonicity(midi_note):
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
        return 0.00001

    return B_by_note[midi_note]
