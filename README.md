modal_piano_engine
# Modal Piano Engine

## NOTE

This project is in an early alpha version (no release). It doesn't sound good, nor does it aim to or allow real-time play, but it provides a theoretical and practical basis for understanding this type of synthesis and how it relates to real piano parameters, such as inharmonicity, resonance gain, duration, etc.

It is functional in terms of MIDI interface and receives NOTE ON and NOTE OFF events from any type of MIDI controller.

The source code is not structured in the best way, nor does it incorporate major optimizations other than precalculating some cosines and exponentials.

## Project Overview
### Objective

To create a real-time physical synthesis engine for a grand piano, with an emphasis on sound fidelity.

Key features to implement:

1. Modal model of the strings (per key)
2. Inharmonicity modeling (string tension and stiffness)
3. Sympathetic resonances between strings
4. Interaction with the soundboard
5. Cabinet resonance (cabinet response)
6. Support for full polyphony (88 keys)
7. Control via keyboard scanning (MIDI interface or other hardware)
8. Run in real time (low resource consumption)
9. Features 1, 2, 3, 6, 7, and 8 are present in an initial, basic but functional version. Rather than sounding like a grand piano, it resembles the "bright" piano models found in 1980s synthesizers.

### What is Modal Synthesis?
Modal synthesis represents a vibrating object (such as a string) as a sum of its eigenmodes (natural resonances). Each mode is a damped oscillator with its own frequency, gain, and damping coefficient.

$y_k(t) = A_k e^{-\alpha_k t} \cos(2\pi f_k t + \phi_k)$

### 🎵 What Is Inharmonicity?
In an ideal string (like in a textbook), the vibration modes are harmonics:
$fn = n \cdot f_1$
where f1 is the fundamental frequency, and n is an integer. This is what you'd get from a massless, perfectly flexible string under tension.
But real piano strings are stiff, not ideal. That stiffness causes the overtones to be sharply instead of exactly integer multiples of the fundamental. This effect is called inharmonicity.

### Why Is This Important in a Piano?
Piano strings are made of steel and under great tension. The stiffness shifts the resonances upwards. Higher notes are slightly affected, but low and mid-range strings (especially wound bass strings) are very inharmonic.
Inharmonicity gives the piano its "metallic" richness and makes each piano unique.

### The Formula
Inharmonicity shifts the harmonic frequencies by a factor that depends on nnn, the overtone number.
🎻 Inharmonic modal frequency:
$f_n = f_1 \cdot n \cdot \sqrt{1 + B \cdot n^2}$
Where:
•	f1: Fundamental frequency of the string (e.g., 440 Hz)
•	n: Overtone or mode number (1 = fundamental, 2 = first overtone, etc.)
•	B: Inharmonicity coefficient (depends on string stiffness, diameter, tension, etc.)
 
#### 🔧 How is B calculated in theory?
If you're modeling physically (optional), you can calculate:
$B = \frac{\pi^3 E r^4}{8 T L^2}$
Where:
* EEE: Young's modulus (stiffness of the material)
* rrr: radius of the string
* TTT: tension
* LLL: string length

But in practice, you can use measured or estimated values of BBB, which for pianos usually range:
* For bass: $B \approx 0.0004 to 0.001$
* For mid-range: $B \approx to 0.0004$
* For high notes: $B \approx 0.00002$

IMAGEN

### Hammer-String Interaction
The real physical interaction is non-linear: the hammer is in contact with the string for only milliseconds, momentarily altering the vibration. Detailed models simulate this with coupled differential equations (Chaigne & Askenfelt), but here we will use a modal approximation.

#### Simplification:

* The hammer excites certain modes more than others, depending on the contact point.
* The contact point xxx in [0, 1] affects each mode n by a factor.

#### Hammer Contact Point vs Note
The hammer contact point is different for each note in a real piano, and it significantly affects the sound.

* In a grand piano, hammers strike the string somewhere between 1/6 and 1/10 of the string length from the end (near the keyboard).
* This location affects which overtones get emphasized or suppressed.
* Lower notes are longer, so the contact point (in physical distance) is farther out — but proportionally, it tends to be closer to the end of the string.
* Higher notes have hammers that strike more centrally (in proportion), exciting more harmonics.

#### Why it matters in modal synthesis:
Each modal frequency fn is shaped by $\sin(n \pi x)$, where:
*	$x \in (0, 1)$: position of the hammer along the string.
* This term becomes zero for some modes if the hammer hits a node of the mode shape (i.e., it doesn't excite that mode at all).

So the contact point modifies the harmonic profile, e.g.:
* Closer to the bridge → fewer high harmonics
* Closer to the center → brighter, more harmonic-rich sound

#### Example contact points (approximate, normalized):
|MIDI |Note	Note Name	|Contact Point (x)|
|---|----|------|
|21	|A0	|0.10|
|36	|C2	|0.13|
|48	|C3	|0.15|
|60	|C4	|0.17|
|72	|C5	|0.19|
|84	|C6	|0.21|
|96	|C7	|0.23|

### What is sympathetic resonance?
Sympathetic resonance occurs when an unstruck string begins to vibrate because another nearby string was excited and they share common partial frequencies.

In a piano:

* If you play a note (e.g., C4), and then press another (e.g., G4) without striking it, G4 may resonate because of the shared frequencies.
* The effect is more noticeable when the sustain pedal is pressed (because the unstruck strings are “free” to vibrate).
* The strings vibrate passively through coupling via the soundboard.

#### Base Teórica
##### Acoplamiento Modal
Cada cuerda no excitada j puede responder a la vibración de otra cuerda i, si comparten modos $f_{n_i} \approx f_{m_j}$
Respuesta simpática:
$s_j(t) = \sum_{m} G_{ijm} \cdot x_{i,n}(t) \cdot H_{m}(t)$
* $G_{ijm}$: ganancia de acoplamiento modal
* $x_{i,n}(t)$: modo excitado de la cuerda activa
* $H_{m}(t)$: filtro resonante del modo de la cuerda receptora

##### Filtro Resonante Pasivo
La cuerda simpatizante no tiene ataque, solo resuena como un filtro modal:
$y(t) = A \cdot e^{-\alpha t} \cdot \cos(2\pi f t + \phi)$

Con amplitud muy baja, pero perceptible.

##### Condición para resonancia simpática
* El pedal de sustain debe estar presionado o la nota simpatizante debe estar “liberada” (sin apagador).
* La frecuencia de algún modo debe estar lo suficientemente cercana:
$\left| \frac{f_i}{f_j} - \frac{n}{m} \right| < \epsilon$

#### Implementation Approach

* Take a list of active notes (with their modes)

* Take a list of “free” notes (sustain ON or keys pressed without striking)

* Add passive resonant response from those strings

* Calculate sympathetic resonances for unstruck but free strings (by pedal or pressed key).

* Compare modal frequencies of the active notes and the free strings.

* If a free string has modes close to those of an active string, a damped passive response is generated.

* Return an audio signal to be added to the main audio.












