#!/usr/bin/env python3
"""
objective_function_priority.py

Implementa la fusión de imágenes con PRIORIDAD DE CAPAS, replicando la lógica de
evaluate_individual_matlab.m donde la primera capa seleccionada tiene prioridad
sobre las siguientes (primera capa gana en superposiciones).

Diferencias con objective_function.py:
- objective_function.py: Promedia colores en superposiciones
- objective_function_priority.py: Primera capa gana (sin promedio)
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


def objective_function_priority(chromosome, image_folder, prefix, save_path=None):
    """
    Evalúa un cromosoma usando fusión con PRIORIDAD DE CAPAS.
    
    La primera capa seleccionada (menor índice) tiene prioridad sobre las siguientes.
    Si un píxel ya fue ocupado por una capa anterior, las capas siguientes NO lo modifican.

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
    
    # Inicializar fusión
    fusion_color = np.zeros((img_size[0], img_size[1], 3), dtype=np.float32)
    ocupado_mask = np.zeros(img_size, dtype=bool)  # Máscara de píxeles ya ocupados
    
    hay_capas = False
    
    # Procesar capas EN ORDEN (N1 a N7)
    # Las capas con menor índice tienen PRIORIDAD
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
    
        # Detectar áreas rojas en esta capa
        mask = red_detection(current_img)
    
        # Solo píxeles NUEVOS (no ocupados previamente)
        # Esta es la clave: las capas anteriores tienen prioridad
        new_pixels = mask & ~ocupado_mask
    
        # Aplicar fusión solo en píxeles nuevos
        fusion_color[new_pixels] = current_img[new_pixels]
    
        # Marcar estos píxeles como ocupados
        ocupado_mask = ocupado_mask | new_pixels
    
    if not hay_capas:
        fitness = -1.0
        img_combinada = img_ref
        if save_path:
            cv2.imwrite(save_path, (img_combinada * 255).astype(np.uint8))
        return fitness, img_combinada
    
    # Combinar con fondo
    # La máscara final es donde hay algún color fusionado
    final_mask = np.any(fusion_color > 0, axis=2)
    
    img_combinada = img_ref.copy()
    img_combinada[final_mask] = fusion_color[final_mask]

    # Calcular fitness (mismo que objective_function.py)
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
    # Prueba comparativa
    import matplotlib.pyplot as plt
    
    chrom = np.array([1, 1, 1, 0, 0, 0, 0])
    
    # Versión con prioridad
    f_priority, img_priority = objective_function_priority(chrom, 'Images/Prueba', 'C0683d')
    print(f'Fitness (Priority): {f_priority:.6f}')
    
    # Comparar con versión promedio (si existe)
    try:
        from objective_function import objective_function
        f_avg, img_avg = objective_function(chrom, 'Images/Prueba', 'C0683d')
        print(f'Fitness (Average):  {f_avg:.6f}')
        print(f'Diferencia:         {abs(f_priority - f_avg):.6f}')
        
        # Visualizar diferencias
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        axes[0].imshow(img_priority)
        axes[0].set_title(f'Priority Fusion\nFitness: {f_priority:.4f}')
        axes[0].axis('off')
        
        axes[1].imshow(img_avg)
        axes[1].set_title(f'Average Fusion\nFitness: {f_avg:.4f}')
        axes[1].axis('off')
        
        # Diferencia absoluta
        diff = np.abs(img_priority - img_avg)
        axes[2].imshow(diff)
        axes[2].set_title('Absolute Difference')
        axes[2].axis('off')
        
        plt.tight_layout()
        plt.savefig('fusion_comparison.png', dpi=150, bbox_inches='tight')
        print('Comparación guardada en: fusion_comparison.png')
        
    except ImportError:
        print('objective_function.py no encontrado, solo se probó versión priority')
