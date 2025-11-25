#!/usr/bin/env python3
"""
evaluate_individual.py

Contiene la función `evaluate_individual(chromosome, image_folder, prefix, save_path=None)`
que replica la lógica de `multipleImageProcessing.m` pero leyendo un vector binario
(7 bits) que define qué capas (N1..N7) deben procesarse para la fusión.

Devuelve: fitness (float) y la imagen fusionada (RGB numpy array en [0,1]).

También hace uso de `calcular_fitness.py` para calcular la puntuación.
"""

import os
import numpy as np
import cv2
from skimage import exposure
from skimage.measure import label, regionprops
from scipy import stats
from typing import Tuple

from calcular_fitness import calcular_fitness


def red_detection(img: np.ndarray, threshold: float = 0.96) -> np.ndarray:
    """
    Detecta zonas rojas siguiendo la lógica de `redDetection.m`.
    img: RGB image in float [0,1]
    Devuelve: máscara booleana (True donde hay rojo)
    """
    # Asegurar rango float
    if img.dtype != np.float64 and img.dtype != np.float32:
        img = img.astype(np.float64) / 255.0

    red_channel = img[:, :, 0]
    blue_channel = img[:, :, 2]

    # Ajustar/igualar histograma en canal rojo similar a imadjust
    red_uint8 = (np.clip(red_channel, 0, 1) * 255).astype(np.uint8)
    red_eq = cv2.equalizeHist(red_uint8).astype(np.float64) / 255.0

    # Umbral fijo (equivalente a redChannelAdj > threshold)
    red_areas = red_eq > threshold

    # Eliminar fondo negro
    background_mask = (red_channel < 0.05) & (blue_channel < 0.05)
    red_areas[background_mask] = False

    return red_areas


def evaluate_individual(chromosome: np.ndarray,
                        image_folder: str = '/home/ashley/projects/Electroimpedance_Image_Analysis/Images/Prueba',
                        prefix: str = 'C0683d',
                        save_path: str = None) -> Tuple[float, np.ndarray]:
    """
    Evaluar un individuo representado por un vector binario de 7 elementos.

    - chromosome: array-like shape (7,), elementos 0/1 (int)
    - image_folder: carpeta donde están las imágenes N1..N7
    - prefix: prefijo de nombre de archivo (ej: 'C0683d')
    - save_path: si se especifica, guardará la imagen fusionada en ese path (PNG)

    Devuelve: (fitness, fusionColor)
    """
    chromosome = np.asarray(chromosome).astype(int).flatten()
    if chromosome.size != 7:
        raise ValueError('El cromosoma debe tener exactamente 7 elementos')

    # Si el cromosoma es todo ceros, no es válido: seleccionar aleatoriamente un bit
    if np.sum(chromosome) == 0:
        idx = np.random.randint(0, 7)
        chromosome[idx] = 1

    # Cargamos una imagen de referencia (N7 como fondo según tu script)
    # También usaremos el tamaño para inicializar fusionColor
    sample_path = os.path.join(image_folder, f"{prefix}_N7_mask.bmp")
    if not os.path.exists(sample_path):
        raise FileNotFoundError(f'No se encontró imagen de referencia: {sample_path}')

    img_ref = cv2.cvtColor(cv2.imread(sample_path, cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)
    img_ref = img_ref.astype(np.float64) / 255.0

    fusionColor = np.zeros_like(img_ref)
    ocupadoMask = np.zeros(img_ref.shape[:2], dtype=bool)

    hayCapas = False

    # Recorrer en orden N1..N7 (prioridad N1 -> N7)
    for i in range(1, 8):
        if chromosome[i - 1] == 0:
            continue

        hayCapas = True
        filename = f"{prefix}_N{i}_mask.bmp"
        filepath = os.path.join(image_folder, filename)
        if not os.path.exists(filepath):
            # Si falta una capa, saltarla (pero avisar)
            print(f"WARNING: falta {filepath}, se omite esa capa")
            continue

        current_img = cv2.cvtColor(cv2.imread(filepath, cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)
        current_img = current_img.astype(np.float64) / 255.0

        mask = red_detection(current_img)
        newPixels = mask & (~ocupadoMask)

        for c in range(3):
            ch = fusionColor[:, :, c]
            ch[newPixels] = current_img[:, :, c][newPixels]
            fusionColor[:, :, c] = ch

        ocupadoMask = ocupadoMask | newPixels

    if not hayCapas:
        # No se seleccionó ninguna capa (aunque ya forzamos 1 bit), devolver fitness muy bajo
        return -1.0, fusionColor

    # Combinar sobre la imagen final (N7) tal como en el .m (ya está considerado en fusionColor)
    # En la versión MATLAB se aplicó la fusión sobre N7; aquí fusionColor ya contiene los pixels
    # colocados, y el fondo (resto) se mantiene en img_ref

    final_mask = np.any(fusionColor > 0, axis=2)
    img_combinada = img_ref.copy()
    for c in range(3):
        ch = img_combinada[:, :, c]
        ch[final_mask] = fusionColor[:, :, c][final_mask]
        img_combinada[:, :, c] = ch

    fitness = calcular_fitness(img_combinada)

    # Guardar si se pidió
    if save_path:
        save_dir = os.path.dirname(save_path)
        if save_dir and not os.path.exists(save_dir):
            os.makedirs(save_dir, exist_ok=True)
        img_uint8 = (np.clip(img_combinada, 0, 1) * 255).astype(np.uint8)
        # OpenCV usa BGR
        cv2.imwrite(save_path, cv2.cvtColor(img_uint8, cv2.COLOR_RGB2BGR))

    return float(fitness), img_combinada


if __name__ == '__main__':
    # Pequeña prueba local (no ejecuta procesamiento pesado)
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--chrom', nargs=7, type=int, help='7 bits (0/1) del cromosoma', required=False)
    parser.add_argument('--out', type=str, help='Ruta para guardar imagen resultante (PNG)', default=None)
    args = parser.parse_args()

    if args.chrom:
        chrom = np.array(args.chrom, dtype=int)
    else:
        chrom = np.random.randint(0, 2, size=(7,))
        if chrom.sum() == 0:
            chrom[np.random.randint(0, 7)] = 1

    score, img = evaluate_individual(chrom, save_path=args.out)
    print(f'Chrom: {chrom} -> Fitness: {score:.6f}')
