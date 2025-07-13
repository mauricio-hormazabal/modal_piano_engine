import numpy as np
from .synth_functions import midi_to_freq, empirical_inharmonicity

def compute_resonance_strength(active_modes_freqs, free_modes_freqs, bandwidth=3.0):
    """
    Evalúa coincidencias modales entre modos activos y modos de una cuerda libre.
    Devuelve un peso global ∈ [0, 1].
    """
    strength = 0.0
    for f_free in free_modes_freqs:
        min_diff = min(abs(f_free - f_act) for f_act in active_modes_freqs)
        if min_diff < bandwidth:
            strength += np.exp(-(min_diff / bandwidth)**2)
    return min(1.0, strength / len(free_modes_freqs))

def compute_mode_by_mode_weights(active_modes_freqs, free_modes_freqs, bandwidth=3.0):
    """
    Devuelve un vector de pesos (uno por modo libre), evaluando coincidencia con los modos activos.
    """
    weights = []
    for f_free in free_modes_freqs:
        min_diff = min(abs(f_free - f_act) for f_act in active_modes_freqs)
        if min_diff < bandwidth:
            w = np.exp(-(min_diff / bandwidth)**2)
        else:
            w = 0.0
        weights.append(w)
    return np.array(weights)

def generate_sympathetic_string_signal(note_free, active_modes_freqs, fs, duration=2.0, num_modes=10, velocity=0.6):
    """
    Genera una señal de cuerda libre con peso global de resonancia.
    """
    f0 = midi_to_freq(note_free)
    B = empirical_inharmonicity(note_free)
    t = np.linspace(0, duration, int(fs * duration))
    signal = np.zeros_like(t)
    free_modes_freqs = [f0 * n * np.sqrt(1 + B * n**2) for n in range(1, num_modes + 1)]
    weight = compute_resonance_strength(active_modes_freqs, free_modes_freqs)
    phase = np.pi / 2
    for n, f_n in enumerate(free_modes_freqs, start=1):
        A = (1.0 / n) * np.exp(-0.3 * n) * velocity
        alpha = 4.0 * n
        signal += weight * A * np.exp(-alpha * t) * np.cos(2 * np.pi * f_n * t + phase)
    return signal

def generate_modewise_sympathetic_signal(note_free, active_modes_freqs, fs, duration=2.0, num_modes=10, velocity=0.6):
    """
    Genera una señal de cuerda libre excitada modo a modo con pesos individuales.
    """
    f0 = midi_to_freq(note_free)
    B = empirical_inharmonicity(note_free)
    t = np.linspace(0, duration, int(fs * duration))
    signal = np.zeros_like(t)
    free_modes_freqs = [f0 * n * np.sqrt(1 + B * n**2) for n in range(1, num_modes + 1)]
    weights = compute_mode_by_mode_weights(active_modes_freqs, free_modes_freqs)
    phase = np.pi / 2
    for n, (f_n, w) in enumerate(zip(free_modes_freqs, weights), start=1):
        if w < 1e-4:
            continue
        A = w * (1.0 / n) * np.exp(-0.3 * n) * velocity
        alpha = 4.0 * n
        signal += A * np.exp(-alpha * t) * np.cos(2 * np.pi * f_n * t + phase)
    return signal

def get_active_modes_freqs(active_notes, num_modes=10):
    """
    Calcula las frecuencias modales de todas las notas activas.
    active_notes = lista de tuplas (midi_note, velocity)
    """
    all_modes = []
    for note, _ in active_notes:
        f0 = midi_to_freq(note)
        B = empirical_inharmonicity(note)
        modes = [f0 * n * np.sqrt(1 + B * n**2) for n in range(1, num_modes + 1)]
        all_modes.extend(modes)
    return all_modes
