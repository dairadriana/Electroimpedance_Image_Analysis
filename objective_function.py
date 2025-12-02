#!/usr/bin/env python3
"""
Implements evaluate_individual in pure Python, replicating the logic of evaluate_individual_matlab.m
without relying on MATLAB.

Uses OpenCV to read images, scikit-image for region analysis, etc.
"""

import os
import numpy as np
import cv2

def red_detection(img, threshold=0.96):
    """
    Detects red areas in an RGB image [0,1].
    Replicating redDetection.m
    """
    red_channel = img[:, :, 0]
    blue_channel = img[:, :, 2]  # OpenCV is BGR, so blue is 2

    # Equalize histogram in red
    red_uint8 = (red_channel * 255).astype(np.uint8)
    red_eq = cv2.equalizeHist(red_uint8) / 255.0

    red_areas = red_eq > threshold

    # Remove black background
    background_mask = (red_channel < 0.05) & (blue_channel < 0.05)
    red_areas[background_mask] = False

    return red_areas.astype(bool)

def objective_function(chromosome, image_folder, prefix, save_path=None):
  
    chromosome = np.asarray(chromosome, dtype=int)
    if chromosome.size != 7:
        raise ValueError('El cromosoma debe tener exactamente 7 elementos')

    # If all zeros, select one randomly
    if chromosome.sum() == 0:
        idx = np.random.randint(0, 7)
        chromosome[idx] = 1

    # Load base image N7
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
    
    # Process selected layers
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
    
    # Merge masks
    final_mask = np.logical_or.reduce(masks_list)
    
    fusion_color = np.zeros((img_size[0], img_size[1], 3), dtype=np.float32)
    count = np.zeros(img_size, dtype=int)
    
    for mask, img in zip(masks_list, images_list):
        fusion_color += img * mask.astype(float)[:, :, np.newaxis]
        count += mask.astype(int)
    
    # Average colors where there is overlap
    valid = count > 0
    fusion_color[valid] /= count[valid, np.newaxis]
    
    # Combine with background
    img_combinada = img_ref.copy()
    img_combinada[final_mask] = fusion_color[final_mask]

    total_detected = final_mask.sum()
    if total_detected == 0:
        fitness = 0.0
    else:
        # Extract RGB values of active pixels
        pixels = img_combinada[final_mask]  # (n_pixels, 3)
        red = pixels[:, 0]
        green = pixels[:, 1]
        blue = pixels[:, 2]

        # Valid pixels: red between 60/255 and 1, and red > green and red > blue
        valid = (red >= 60/255) & (red > green) & (red > blue)
        valid_count = valid.sum()

        # Quality score
        quality = valid_count / total_detected

        # Presence score
        presence = valid_count / (valid_count + 50)

        # Weighted fitness
        fitness = 0.8 * quality + 0.2 * presence

    if save_path:
        img_bgr = cv2.cvtColor(img_combinada, cv2.COLOR_RGB2BGR)
        cv2.imwrite(save_path, (img_bgr * 255).astype(np.uint8))

    return fitness, img_combinada

if __name__ == '__main__':
    # Test
    chrom = np.array([1, 0, 1, 1, 0, 0, 0])
    f, img = objective_function(chrom, 'Images/Prueba', 'C0683d')
    print(f'Fitness: {f}')