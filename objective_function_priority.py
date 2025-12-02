#!/usr/bin/env python3
"""
Implements image fusion with LAYER PRIORITY, replicating the logic of
evaluate_individual_matlab.m where the first selected layer has priority
over the following ones (first layer wins in overlaps).

Differences with objective_function.py:
- objective_function.py: Averages colors in overlaps
- objective_function_priority.py: First layer wins (no averaging)
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


def objective_function_priority(chromosome, image_folder, prefix, save_path=None):
    """
    Evaluates a chromosome using LAYER PRIORITY fusion.
    
    The first selected layer (lowest index) has priority over the following ones.
    If a pixel has already been occupied by a previous layer, the following layers do NOT modify it.

    """
    chromosome = np.asarray(chromosome, dtype=int)
    if chromosome.size != 7:
        raise ValueError('El cromosoma debe tener exactamente 7 elementos')

    
    if chromosome.sum() == 0:
        idx = np.random.randint(0, 7)
        chromosome[idx] = 1

    base_path = os.path.join(image_folder, f'{prefix}_N7_mask.bmp')
    if not os.path.exists(base_path):
        raise FileNotFoundError(f'Imagen base N7 no encontrada: {base_path}')
    img_ref = cv2.imread(base_path).astype(np.float32) / 255.0
    img_ref = cv2.cvtColor(img_ref, cv2.COLOR_BGR2RGB)  # Convertir a RGB

    img_size = img_ref.shape[:2]
    
    # Initialize fusion
    fusion_color = np.zeros((img_size[0], img_size[1], 3), dtype=np.float32)
    ocupado_mask = np.zeros(img_size, dtype=bool)  # Mask of already occupied pixels
    
    hay_capas = False
    
    # Process layers IN ORDER (N1 to N7)
    # Layers with lower index have PRIORITY
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
    
        # Detect red areas in this layer
        mask = red_detection(current_img)
    
        # Only NEW pixels (not previously occupied)
        new_pixels = mask & ~ocupado_mask
    
        # Apply fusion only on new pixels
        fusion_color[new_pixels] = current_img[new_pixels]
    
        # Mark these pixels as occupied
        ocupado_mask = ocupado_mask | new_pixels
    
    if not hay_capas:
        fitness = -1.0
        img_combinada = img_ref
        if save_path:
            cv2.imwrite(save_path, (img_combinada * 255).astype(np.uint8))
        return fitness, img_combinada
    
    # Combine with background
    final_mask = np.any(fusion_color > 0, axis=2)
    
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
    # Comparative test
    import matplotlib.pyplot as plt
    
    chrom = np.array([1, 1, 1, 0, 0, 0, 0])
    
    # Version with priority
    f_priority, img_priority = objective_function_priority(chrom, 'Images/Prueba', 'C0683d')
    print(f'Fitness (Priority): {f_priority:.6f}')
    
    # Compare with average version (if exists)
    try:
        from objective_function import objective_function
        f_avg, img_avg = objective_function(chrom, 'Images/Prueba', 'C0683d')
        print(f'Fitness (Average):  {f_avg:.6f}')
        print(f'Diferencia:         {abs(f_priority - f_avg):.6f}')
        
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        axes[0].imshow(img_priority)
        axes[0].set_title(f'Priority Fusion\nFitness: {f_priority:.4f}')
        axes[0].axis('off')
        
        axes[1].imshow(img_avg)
        axes[1].set_title(f'Average Fusion\nFitness: {f_avg:.4f}')
        axes[1].axis('off')

        diff = np.abs(img_priority - img_avg)
        axes[2].imshow(diff)
        axes[2].set_title('Absolute Difference')
        axes[2].axis('off')
        
        plt.tight_layout()
        plt.savefig('fusion_comparison.png', dpi=150, bbox_inches='tight')
        print('Comparación guardada en: fusion_comparison.png')
        
    except ImportError:
        print('objective_function.py no encontrado, solo se probó versión priority')
