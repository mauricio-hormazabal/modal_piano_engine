modal_piano_engine
# Modal Piano Engine

## Visión General del Proyecto
### Objetivo
Crear un motor de síntesis física de piano de cola en tiempo real, con énfasis en fidelidad sonora.

Características clave a implementar:
1.	Modelo modal de las cuerdas (por tecla) 
2.	Modelado de inarmonía (tensión y rigidez de cuerdas)
3.	Resonancias simpáticas entre cuerdas
4.	Interacción con tabla armónica (soundboard)
5.	Resonancia de caja (cabinet response)
6.	Soporte para polifonía completa (88 teclas)
7.	Control desde un escaneo de teclado (interfaz MIDI u otro hardware)
8.	Ejecutarse en tiempo real (bajo consumo)

1, 2, 3, 6, 7 y 8 se encuentran en una primera versión básica, pero funcional. Mas que un piano de cola, suena similar a los modelos de piano "brillante" de los sintetizadores de los años 80s.

### ¿Qué es la Síntesis Modal?
La síntesis modal representa un objeto vibrante (como una cuerda) como una suma de modos propios (resonancias naturales). Cada modo es un oscilador amortiguado con una frecuencia, ganancia e índice de amortiguamiento.

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

### Interacción martillo-cuerda
La interacción física real es no lineal: el martillo está en contacto con la cuerda por milisegundos, alterando momentáneamente la vibración. Modelos detallados lo simulan con ecuaciones diferenciales acopladas (Chaigne & Askenfelt), pero aquí usaremos una aproximación modal:

#### Simplificación:
* El martillo excita ciertos modos más que otros, según el punto de contacto.
* Punto de contacto xxx en [0, 1] afecta cada modo n por un factor.
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

### ¿Qué es la resonancia simpática?
La resonancia simpática ocurre cuando una cuerda no golpeada comienza a vibrar porque otra cuerda cercana fue excitada, y comparten frecuencias parciales comunes. 

En un piano:
* Si tocas una nota (ej. C4), y luego presionas otra (ej. G4) sin golpearla, G4 puede resonar por las frecuencias compartidas.
* El efecto es más notable cuando el pedal de sustain está presionado (porque las cuerdas no golpeadas están “libres” para vibrar).
* Las cuerdas vibran pasivamente por acoplamiento a través de la tabla armónica (soundboard).

#### Base Teórica
1. Acoplamiento Modal
Cada cuerda no excitada j puede responder a la vibración de otra cuerda i, si comparten modos $f_{n_i} \approx f_{m_j}$
Respuesta simpática:
$s_j(t) = \sum_{m} G_{ijm} \cdot x_{i,n}(t) \cdot H_{m}(t)$
* $G_{ijm}$: ganancia de acoplamiento modal
* $x_{i,n}(t)$: modo excitado de la cuerda activa
* $H_{m}(t)$: filtro resonante del modo de la cuerda receptora










