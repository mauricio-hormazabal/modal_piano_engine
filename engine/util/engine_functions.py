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

def empirical_inharmonicity(midi_note):
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

def precalculate_hammer_gain_decay():
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

def hammer_contact_point_yamaha(midi_note):
    return 0.11 + (midi_note / 127.0) * 0.015


# Adapta el numero de modos de cada nota según rango en que se encuentra.
def adaptive_num_modes(midi_note):
    if midi_note < 40: return 14 # 14
    elif midi_note < 60: return 10 # 10
    elif midi_note < 75: return 8 # 6
    else: return 6 #4