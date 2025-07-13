import numpy as np
from .util.synth_functions import midi_to_freq, estimated_duration, base_damping_for_note, attack_envelope
from scipy.signal import lfilter, butter


def generate_realistic_modal_signal(midi_note, fs,
                                    num_modes=12, velocity=1.0,
                                    inh_matrix = [],
                                    hammer_matrix=[],
                                    gd_values ={},
                                    mod_bank = [],
                                    threshold=1e-5, silence_db_threshold=-60.0):
    
    f0 = midi_to_freq(midi_note)
    #duration = estimated_duration(midi_note, velocity)
    duration = 2.0 #prueba precomputed, se deberia obtener del mismo modal bank.
    #t = np.linspace(0, duration, int(fs * duration)) #prueba precomputed
    t = mod_bank.get_time_vector() #prueba precomputed
    signal = np.zeros_like(t)
    phase = np.pi / 2 

    for n in range(1, num_modes + 1):
        
       #f_n = f0 * n * inh_matrix[midi_note][n] ##  inharmonicity precalculada

        hammer = gd_values[n] * velocity ## precalculos de la ganancia y decaimiento por golpe del martillo
        shape = hammer_matrix[midi_note][n] ## forma del "golpe", precalculada a partir num modo y del contact point para cada nota.
        
        A = hammer * shape
        
        if np.abs(A) < threshold:
            continue
        base_alpha = base_damping_for_note(midi_note)
        alpha = base_alpha * (1 + 0.15 * n)
        #signal += A * np.exp(-alpha * t) * np.cos(2 * np.pi * f_n * t + phase)
        signal += A * np.exp(-alpha * t) * mod_bank.get_mode_wave(midi_note, n) #prueba precomputed
        #signal += A * np.exp(-alpha * t) * np.sin(2 * np.pi * f_n * t)

    """
    # Cortar la señal si cae por debajo de cierto umbral (e.g., -60 dB)
    rms = np.sqrt(np.mean(signal**2))
    if rms > 0:
        threshold_lin = 10**(silence_db_threshold / 20)
        above = np.abs(signal) > threshold_lin
        if np.any(above):
            last_idx = np.max(np.where(above))
            signal = signal[:last_idx + 1]
    """

    envelope = attack_envelope(fs, duration, velocity)
    signal *= envelope

    return signal

