import numpy as np

def midi_to_freq(midi_note):
    return 440.0 * (2 ** ((midi_note - 69) / 12))

def find_resonant_free_notes(active_notes, free_notes, harmonic_range=10, tolerance=0.02):
    """Encuentra cuerdas libres que resuenan simpáticamente con las activas."""
    resonant_notes = set()
    for midi_note, _ in active_notes:
        f0 = midi_to_freq(midi_note)
        for n in range(1, harmonic_range + 1):
            f_harm = f0 * n
            for free_note in free_notes:
                f_free = midi_to_freq(free_note)
                rel_diff = abs(f_free - f_harm) / f_harm
                if rel_diff < tolerance:
                    resonant_notes.add(free_note)
    return sorted(resonant_notes)

def generate_sympathetic_response(fs, duration, active_notes, gain=0.1,
                                  harmonic_range=10, tolerance=0.02,
                                  num_modes=10, decay=6.0): #3.5 decay
    """Genera respuesta simpática de cuerdas libres resonantes."""
    t = np.linspace(0, duration, int(fs * duration))
    response = np.zeros_like(t)

    # Cuerdas libres: todas menos las activas
    all_notes = list(range(21, 109))
    notes_actives = [note for note, _ in active_notes]
    free_notes = [n for n in all_notes if n not in notes_actives]

    # Buscar solo las cuerdas libres relevantes
    resonant_notes = find_resonant_free_notes(active_notes, free_notes,
                                               harmonic_range, tolerance)

    for free_note in resonant_notes:
        f0 = midi_to_freq(free_note)
        B = 0.0001  # valor bajo típico de B para respuesta simpática
        phase = np.pi / 2

        for n in range(1, num_modes + 1):
            f_n = f0 * n * np.sqrt(1 + B * n**2)
            alpha = decay * n
            A = gain / n
            mode = A * np.exp(-alpha * t) * np.cos(2 * np.pi * f_n * t + phase)
            response += mode

    return response
