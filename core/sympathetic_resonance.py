import numpy as np
from .util.synth_functions import midi_to_freq, estimated_duration


def OLD_find_resonant_free_notes(active_notes, free_notes, harmonic_range=10, tolerance=0.005): #tolerance 0.02
    """Encuentra cuerdas libres que resuenan simpáticamente con las activas."""
    resonant_notes = set()
    for midi_note in active_notes:
        f0 = midi_to_freq(midi_note)
        for n in range(1, harmonic_range + 1):
            f_harm = f0 * n
            for free_note in free_notes:
                f_free = midi_to_freq(free_note)
                rel_diff = abs(f_free - f_harm) / f_harm
                if rel_diff < tolerance:
                    resonant_notes.add(free_note)
    return sorted(resonant_notes)

def find_resonant_free_notes(midi_note, free_notes, harmonic_range=10, tolerance=0.005): #tolerance 0.02
    """Encuentra cuerdas libres que resuenan simpáticamente con las activas."""
    resonant_notes = set()

    f0 = midi_to_freq(midi_note)
    for n in range(1, harmonic_range + 1):
        f_harm = f0 * n
        for free_note in free_notes:
            f_free = midi_to_freq(free_note)
            rel_diff = abs(f_free - f_harm) / f_harm
            if rel_diff < tolerance:
                resonant_notes.add(free_note)
    return sorted(resonant_notes)

def generate_sympathetic_response(fs, midi_note, velocity, active_notes, 
                                  inh_matrix = [],
                                  gain=0.005, #0.1 gain, HR=10, NM=10, DEC=3.5
                                  harmonic_range=6, tolerance=0.02,
                                  num_modes=4, decay=1.5): #3.5 decay

    duration = estimated_duration(midi_note, velocity)
    t = np.linspace(0, duration, int(fs * duration)) # ver como calcular esto en forma mas precisa.
    response = np.zeros_like(t)

    # Cuerdas libres: todas menos las activas
    all_notes = list(range(21, 109))
    #notes_actives = [note for note in active_notes]
    free_notes = [n for n in all_notes if n not in active_notes]

    # Buscar solo las cuerdas libres relevantes
    #resonant_notes = find_resonant_free_notes(active_notes, free_notes,
    #                                          harmonic_range, tolerance)
    resonant_notes = find_resonant_free_notes(midi_note, free_notes,
                                            harmonic_range, tolerance)

    for free_note in resonant_notes:

        f0 = midi_to_freq(free_note)
        phase = np.pi / 2

        for n in range(1, num_modes + 1):
            f_n = f0 * n * inh_matrix[midi_note][n]
            alpha = decay * n
            A = gain / n
            mode = A * np.exp(-alpha * t) * np.cos(2 * np.pi * f_n * t + phase)
            response += mode

   # envelope = attack_envelope(fs, duration, velocity)
   # response *= envelope
    return response

"""
def estimated_duration(midi_note, velocity):
    base = 1.0 + (1.0 - velocity) * 2.0
    if midi_note < 40:
        return base + 3.0
    elif midi_note < 60:
        return base + 2.2 # 2.0
    elif midi_note < 75:
        return base + 1.5 # 1.0
    else:
        return base
"""

def attack_envelope(fs, duration, velocity, fade_min=0.002, fade_max=0.008): # min = 0.002 y max= 0.01
    """
    Devuelve un vector de envolvente de ataque basado en la velocidad.
    - velocity: entre 0 y 1
    - fade_min: duración mínima del ataque (en segundos)
    - fade_max: duración máxima del ataque (en segundos)
    """
    fade_duration = fade_max - velocity * (fade_max - fade_min)
    fade_len = int(fs * fade_duration)
    envelope = np.ones(int(fs * duration))
    """
    Es 0.5 porque tiene que terminar amplificando por 1 el fade (Cos desplazado, amp = 2) para mantener
    la continuidad con la envolvente que despues del fade in, tiene un valor de 1.
    Porque la forma del medio ciclo de coseno invertido (desde 0 hasta π) tiene solo valores positivos,
    """
    fade = 0.5 * (1 - np.cos(np.pi * np.linspace(0, 1, fade_len)))  #
    envelope[:fade_len] = fade
    return envelope