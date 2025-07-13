import numpy as np

def default_soundboard_modes():
    # Frecuencias y amortiguamiento de modos de la tabla armónica (simulados)
    return [
        (140, 1.5),
        (280, 3.0),
        (420, 4.5),
        (560, 6.0),
        (700, 7.0),
        (900, 8.0),
        (1200, 9.0),
        (1600, 10.0),
        (2100, 11.0),
        (2800, 12.0),
        (3500, 14.0),
        (4200, 15.0)
    ]

def simulate_soundboard_response(fs, duration, active_notes,
                                  num_modes=12, resonance_gain=0.2):  #0.2
    """
    active_notes: list of (midi_note, velocity)
    Returns: audio signal of the soundboard response
    """
    """
    Ver si aplica el numero dinamico de modos activos
    """
    t = np.linspace(0, duration, int(fs * duration))
    signal = np.zeros_like(t)
    tabla_modes = default_soundboard_modes()

    # Buscar coincidencias modales con modos de las cuerdas activas
    for midi_note, velocity in active_notes:
        f0 = 440.0 * (2 ** ((midi_note - 69) / 12))
        for n in range(1, num_modes + 1):
            f_n = f0 * n * np.sqrt(1 + empirical_inharmonicity(midi_note) * n**2)

            for f_s, decay_s in tabla_modes:
                # Si hay coincidencia modal cercana
                if abs(f_n - f_s) / f_s < 0.03:
                    A = resonance_gain * velocity / n
                    alpha = decay_s
                    phase = np.pi / 2  # start at zero
                    signal += A * np.exp(-alpha * t) * np.cos(2 * np.pi * f_s * t + phase)
                    break

    return signal

def empirical_inharmonicity(midi_note):
    if midi_note <= 31:
        return 0.0010
    elif midi_note <= 43:
        return 0.0006
    elif midi_note <= 55:
        return 0.0003
    elif midi_note <= 67:
        return 0.00015
    elif midi_note <= 79:
        return 0.00007
    elif midi_note <= 89:
        return 0.00003
    else:
        return 0.000015

def extract_excited_soundboard_modes(active_notes, num_modes=12, gain=0.2):
    tabla_modes = default_soundboard_modes()
    mode_energies = {f: 0.0 for f, _ in tabla_modes}

    for midi_note, velocity in active_notes:
        f0 = 440.0 * (2 ** ((midi_note - 69) / 12))
        B = empirical_inharmonicity(midi_note)

        for n in range(1, num_modes + 1):
            f_n = f0 * n * np.sqrt(1 + B * n**2)
            for f_s, _ in tabla_modes:
                if abs(f_n - f_s) / f_s < 0.03:
                    mode_energies[f_s] += gain * velocity / n
                    break  # un solo acople por modo

    # Convertir dict a lista (solo los modos con energía significativa)
    return [(f, A) for f, A in mode_energies.items() if A > 1e-5]
