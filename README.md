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

#### The Formula
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
•	EEE: Young's modulus (stiffness of the material)
•	rrr: radius of the string
•	TTT: tension
•	LLL: string length
But in practice, you can use measured or estimated values of BBB, which for pianos usually range:
•	For bass: $B≈0.0004 $B \approx 0.0004B to 0.001$
•	For mid-range: B≈0.0001B \approx 0.0001B≈0.0001 to 0.00040.00040.0004
•	For high notes: B≈0.00002B \approx 0.00002B≈0.00002
We used B=0.0002B = 0.0002B=0.0002 in the example as a reasonable mid-range value.


