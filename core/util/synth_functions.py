import numpy as np

def midi_to_freq(midi_note):
    return 440.0 * (2 ** ((midi_note - 69) / 12))

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
    
def attack_envelope(fs, duration, velocity, fade_min=0.0005, fade_max=0.002): # min = 0.002 y max= 0.008
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

