#!/usr/bin/env python3
"""
objective_function.py

Implementa evaluate_individual en Python puro, replicando la lógica de evaluate_individual_matlab.m
sin depender de MATLAB.

Usa OpenCV para leer imágenes, scikit-image para análisis de regiones, etc.
"""

import os
import numpy as np
import cv2

def red_detection(img, threshold=0.96):
    """
    Detecta áreas rojas en una imagen RGB [0,1].
    Replicando redDetection.m
    """
    red_channel = img[:, :, 0]
    blue_channel = img[:, :, 2]  # OpenCV es BGR, así que blue es 2

    # Equalizar histograma en rojo
    red_uint8 = (red_channel * 255).astype(np.uint8)
    red_eq = cv2.equalizeHist(red_uint8) / 255.0

    red_areas = red_eq > threshold

    # Eliminar fondo negro
    background_mask = (red_channel < 0.05) & (blue_channel < 0.05)
    red_areas[background_mask] = False

    return red_areas.astype(bool)

def objective_function(chromosome, image_folder, prefix, save_path=None):
    """
    Evalúa un cromosoma en Python puro.

    Entradas:
    - chromosome: np.array de 7 elementos 0/1
    - image_folder: str, carpeta con imágenes
    - prefix: str, prefijo (ej 'C0683d')
    - save_path: str opcional, guardar imagen

    Salidas:
    - fitness: float
    - img_combinada: np.array RGB [0,1]
    """
    chromosome = np.asarray(chromosome, dtype=int)
    if chromosome.size != 7:
        raise ValueError('El cromosoma debe tener exactamente 7 elementos')

    # Si todo ceros, seleccionar uno aleatoriamente
    if chromosome.sum() == 0:
        idx = np.random.randint(0, 7)
        chromosome[idx] = 1

    # Cargar imagen base N7
    base_path = os.path.join(image_folder, f'{prefix}_N7_mask.bmp')
    if not os.path.exists(base_path):
        raise FileNotFoundError(f'Imagen base N7 no encontrada: {base_path}')
    img_ref = cv2.imread(base_path).astype(np.float32) / 255.0
    img_ref = cv2.cvtColor(img_ref, cv2.COLOR_BGR2RGB)  # Convertir a RGB

    img_size = img_ref.shape[:2]
    
    # Collect masks and images
    masks_list = []
    images_list = []
    
    hay_capas = False
    
    # Procesar capas seleccionadas
    for i in range(7):
        if chromosome[i] == 0:
            continue
    
        hay_capas = True
        filename = f'{prefix}_N{i+1}_mask.bmp'
        filepath = os.path.join(image_folder, filename)
        if not os.path.exists(filepath):
            print(f'Falta {filepath}, se omite')
            continue
    
        current_img = cv2.imread(filepath).astype(np.float32) / 255.0
        current_img = cv2.cvtColor(current_img, cv2.COLOR_BGR2RGB)
    
        mask = red_detection(current_img)
    
        masks_list.append(mask)
        images_list.append(current_img)
    
    if not hay_capas:
        fitness = -1.0
        img_combinada = img_ref
        if save_path:
            cv2.imwrite(save_path, (img_combinada * 255).astype(np.uint8))
        return fitness, img_combinada
    
    # Fusionar máscaras
    final_mask = np.logical_or.reduce(masks_list)
    
    fusion_color = np.zeros((img_size[0], img_size[1], 3), dtype=np.float32)
    count = np.zeros(img_size, dtype=int)
    
    for mask, img in zip(masks_list, images_list):
        fusion_color += img * mask.astype(float)[:, :, np.newaxis]
        count += mask.astype(int)
    
    # Promediar colores donde hay superposición
    valid = count > 0
    fusion_color[valid] /= count[valid, np.newaxis]
    
    # Combinar con fondo
    img_combinada = img_ref.copy()
    img_combinada[final_mask] = fusion_color[final_mask]

    # Calcular fitness
    total_detected = final_mask.sum()
    if total_detected == 0:
        fitness = 0.0
    else:
        # Extraer valores RGB de píxeles activos
        pixels = img_combinada[final_mask]  # (n_pixels, 3)
        red = pixels[:, 0]
        green = pixels[:, 1]
        blue = pixels[:, 2]

        # Píxeles válidos: rojo entre 60/255 y 1, y rojo > verde y rojo > azul
        valid = (red >= 60/255) & (red > green) & (red > blue)
        valid_count = valid.sum()

        # Puntaje de calidad
        quality = valid_count / total_detected

        # Puntaje de presencia
        presence = valid_count / (valid_count + 50)

        # Fitness ponderado
        fitness = 0.8 * quality + 0.2 * presence

    if save_path:
        img_bgr = cv2.cvtColor(img_combinada, cv2.COLOR_RGB2BGR)
        cv2.imwrite(save_path, (img_bgr * 255).astype(np.uint8))

    return fitness, img_combinada

if __name__ == '__main__':
    # Prueba
    chrom = np.array([1, 0, 1, 1, 0, 0, 0])
    f, img = objective_function(chrom, 'Images/Prueba', 'C0683d')
    print(f'Fitness: {f}')