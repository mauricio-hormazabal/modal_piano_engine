import numpy as np

def excite_free_strings_via_soundboard(active_notes, soundboard_modes,
                                       fs, duration,
                                       gain=0.08, num_modes=10,
                                       tolerance=0.02, decay=6.0): #4.5 decay
    """Excita cuerdas libres que coinciden con modos del soundboard."""
    t = np.linspace(0, duration, int(fs * duration))
    signal = np.zeros_like(t)

    # Cuerdas libres: todas menos las activas
    all_notes = list(range(21, 109))
    notes_actives = [note for note, _ in active_notes]
    free_notes = [n for n in all_notes if n not in notes_actives]

    # Filtrar cuerdas libres relevantes
    resonant_notes = find_strings_resonant_with_soundboard_modes(soundboard_modes,
                                                                 free_notes,
                                                                 tolerance,
                                                                 num_modes)

    for note in resonant_notes:
        f0 = 440.0 * (2 ** ((note - 69) / 12))
        B = 0.0001  # o usar tabla real
        phase = np.pi / 2
        for n in range(1, num_modes + 1):
            f_n = f0 * n * np.sqrt(1 + B * n**2)
            alpha = decay * n
            A =  gain / n 
            mode = A * np.exp(-alpha * t) * np.cos(2 * np.pi * f_n * t + phase)
            signal += mode

    return signal

# deberia devolver la energia acumulada de los modos del soundboard que está en soundboard_modes, para excitar ls cuerdas
# libres (A)
def find_strings_resonant_with_soundboard_modes(soundboard_modes, free_notes,
                                                 tolerance=0.02, max_modes=10):
    """Encuentra cuerdas libres cuya frecuencia modal coincide con modos del soundboard."""
    resonant_strings = set()

    for note in free_notes:
        f0 = 440.0 * (2 ** ((note - 69) / 12))
        B = 0.0001  # o puedes usar la tabla real de B
        for n in range(1, max_modes + 1):
            f_n = f0 * n * np.sqrt(1 + B * n**2)

            for f_sb, energy in soundboard_modes:  
                rel_diff = abs(f_n - f_sb) / f_sb
                #print(f"{rel_diff} para modo {n} y freq de soundboard {f_sb} y una enrgia de {energy}")
                if rel_diff < tolerance:
                    resonant_strings.add(note) 
                    break  # basta con que un modo coincida

    return sorted(resonant_strings)
