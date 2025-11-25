#!/usr/bin/env python3
"""
calcular_fitness.py

Implementa `calcular_fitness(img_fusionada)` en Python siguiendo la idea
que compartiste: usar el canal rojo, entropía, desviación estándar y penalización
por ruido disperso.

Entrada:
 - img_fusionada: numpy array RGB en rango [0,1]
Salida:
 - score (float)
"""

import numpy as np
from scipy.stats import entropy
from skimage.measure import label, regionprops


def calcular_fitness(img_fusionada: np.ndarray,
                      w1: float = 1.0,
                      w2: float = 2.0,
                      w3: float = 0.01,
                      noise_threshold: float = 0.1,
                      min_area: int = 5) -> float:
    """
    Calcular el fitness de una imagen fusionada.
    """
    if img_fusionada is None:
        return -1.0

    red_channel = img_fusionada[:, :, 0]

    # Entropía: calcular histograma en 256 bins
    red_8bit = (np.clip(red_channel, 0, 1) * 255).astype(np.uint8)
    hist, _ = np.histogram(red_8bit, bins=256, range=(0, 256))
    total = hist.sum()
    if total == 0:
        e = 0.0
    else:
        p = hist.astype(float) / total
        # Evitar ceros para la entropía
        p_nonzero = p[p > 0]
        e = entropy(p_nonzero, base=None)  # natural log, comparable

    # Desviación estándar (contraste global)
    s = float(np.std(red_channel))

    # Penalización por ruido disperso
    binary = red_channel > noise_threshold
    labeled = label(binary)
    props = regionprops(labeled)

    ruido = 0.0
    if props:
        areas = np.array([p.area for p in props])
        ruido = float(np.sum(areas[areas < min_area]))

    score = (w1 * e) + (w2 * s) - (w3 * ruido)

    return float(score)


if __name__ == '__main__':
    # Prueba rápida (imagen negra)
    import numpy as np
    img = np.zeros((100, 100, 3), dtype=float)
    print('Fitness imagen negra:', calcular_fitness(img))
