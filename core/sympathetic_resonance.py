import numpy as np
from .util.synth_functions import midi_to_freq, estimated_duration, attack_envelope


def find_resonant_free_notes(midi_note, free_notes, harmonic_range=10, tolerance=0.005): #tolerance 0.02
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
                                  gd_values = [],
                                  gain=0.01, #0.01 gain, HR=10, NM=10, DEC=3.5
                                  harmonic_range=6, tolerance=0.02,
                                  num_modes=6, decay=1.5): #3.5 decay

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
            #A = gain / n  #(1.0 / n) * np.exp(-0.3 * n) * velocity # gain*pre-g*velocity
            A = gain * gd_values[n] * velocity
            mode = A * np.exp(-alpha * t) * np.cos(2 * np.pi * f_n * t + phase)
            response += mode

    envelope = attack_envelope(fs, duration, velocity, fade_min=0.008, fade_max=0.02 ) #Valores de prueba, ajustar
    response *= envelope
    return response

"""
def OLD_find_resonant_free_notes(active_notes, free_notes, harmonic_range=10, tolerance=0.005): #tolerance 0.02

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
"""