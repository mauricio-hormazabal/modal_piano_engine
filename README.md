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

$y_k(t) = A_k e^{-\alpha_k t} \cos(2\pi f_k t + \phi_k)yk(t)$

### 🎵 What Is Inharmonicity?
In an ideal string (like in a textbook), the vibration modes are harmonics:
f$n= n \cdot f_1fn$
where f1f_1f1 is the fundamental frequency, and nnn is an integer. This is what you'd get from a massless, perfectly flexible string under tension.
But real piano strings are stiff, not ideal. That stiffness causes the overtones to be sharply instead of exactly integer multiples of the fundamental. This effect is called inharmonicity.

