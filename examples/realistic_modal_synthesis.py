import numpy as np
from scipy.io.wavfile import write
from sympathetic_resonance import generate_sympathetic_response
from soundboard_model import simulate_soundboard_response, extract_excited_soundboard_modes
from soundboard_sympathetic import excite_free_strings_via_soundboard, find_strings_resonant_with_soundboard_modes

def hammer_contact_point(midi_note):
    return 0.10 + (midi_note / 127.0) * 0.13

def midi_to_freq(midi_note):
    return 440.0 * (2 ** ((midi_note - 69) / 12))

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

def  generate_realistic_modal_signal(midi_note, duration, fs,
                                    num_modes=12, decay=4.0, velocity=1.0, threshold=1e-5):
    f0 = midi_to_freq(midi_note)
    contact_point = hammer_contact_point(midi_note)
    B = empirical_inharmonicity(midi_note)
    t = np.linspace(0, duration, int(fs * duration))
    signal = np.zeros_like(t)
    phase = np.pi / 2  # Start at zero crossing

    for n in range(1, num_modes + 1):
        f_n = f0 * n * np.sqrt(1 + B * n**2)
        hammer = (1.0 / n) * np.exp(-0.2 * n) * velocity
        shape = np.sin(np.pi * n * contact_point)
        A = hammer * shape
        # Umbral modal
        if np.abs(A) < threshold:
            continue
        # test alfa segun modo
        base_alpha = base_damping_for_note(midi_note) 
        alpha = base_alpha * (1 + 0.15 * n)
        #alpha = decay * n
        signal += A * np.exp(-alpha * t) * np.cos(2 * np.pi * f_n * t + phase)

    return signal

# === Example usage ===

# Notas activas: [(midi_note, velocity)]
active_notes = [(21, 0.8)]  

# Notas libres: no golpeadas, pero sin apagador (por pedal u otras teclas presionadas)
# free_notes = [53, 54, 62, 69, 81]


fs = 44100
duration = 2.0
midi_note = 21  
velocity = 0.8

def adaptive_num_modes(midi_note):
    if midi_note < 40: return 14  # graves
    elif midi_note < 60: return 10
    elif midi_note < 75: return 6
    else: return 4

def base_damping_for_note(midi_note):
    if midi_note <= 35:
        return 1.5
    elif midi_note <= 59:
        return 2.0
    elif midi_note <= 71:
        return 3.0
    elif midi_note <= 84:
        return 4.5
    else:
        return 6.0

def synthesize_note_with_resonances(midi_note, velocity, active_notes, fs, duration):

    n_modes = adaptive_num_modes(midi_note)

    sb_modes = extract_excited_soundboard_modes(active_notes, num_modes=n_modes) # soundboard_model
    
    main_modal = generate_realistic_modal_signal(midi_note, duration, fs, num_modes=n_modes, velocity=velocity)

    #sympathetic_direct = generate_sympathetic_response(fs=44100,
    #                                    duration=2.0,
    #                                    active_notes=active_notes,
    #                                    free_notes=free_notes, num_modes=n_modes)
    sympathetic_direct = generate_sympathetic_response(fs, duration, active_notes=active_notes, num_modes=n_modes)

    soundboard_response = simulate_soundboard_response(fs, duration, active_notes=active_notes, num_modes=n_modes)

    #sympathetic_via_board = excite_free_strings_via_soundboard(free_notes,
    #                                                tabla_modes_activados,
    #                                                fs=44100,
    #                                                duration=2.0, num_modes=n_modes)

    sympathetic_via_board = excite_free_strings_via_soundboard(active_notes, sb_modes, fs, duration)

    final_signal = main_modal + sympathetic_direct + soundboard_response + sympathetic_via_board


    return final_signal

signal = synthesize_note_with_resonances(midi_note, velocity, active_notes, fs, duration)



# Normalize and export
max_val = np.max(np.abs(signal))
if max_val > 0:
    signal /= max_val

#scale    
scaled_signal = np.int16(signal * 32767)
write("signal_symp_sb.wav", fs, scaled_signal)

print("Saved: signal_symp_sb.wav")
###