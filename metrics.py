#!/usr/bin/env python3
"""
metrics.py

Implementa la función de Relación Contraste-Ruido (CNR) según las especificaciones del usuario.

Reglas de Segmentación:
1. Color: R >= 60, R > G > B.
2. Región: Componente conectado más grande.
3. Fallback: Si no hay región, círculo de 10x10 en el centro.
4. Fondo: Anillo alrededor de la máscara del tumor.

Cálculo:
- CNR = |Mean_tumor - Mean_background| / Std_background
- Se calcula para las 7 capas originales y la imagen fusionada.
- Retorna: (Max_CNR_capas, CNR_fusionada)
"""

import numpy as np
import cv2
from skimage import measure

def get_tumor_mask(img_rgb):
    """
    Genera la máscara del tumor basada en reglas de color y componentes conectados.
    img_rgb: Imagen en formato RGB con valores [0, 255] o [0, 1].
             Se asume [0, 255] para los umbrales (R>=60).
    """
    # Asegurar rango 0-255
    if img_rgb.max() <= 1.0:
        img_uint8 = (img_rgb * 255).astype(np.uint8)
    else:
        img_uint8 = img_rgb.astype(np.uint8)
        
    R = img_uint8[:, :, 0]
    G = img_uint8[:, :, 1]
    B = img_uint8[:, :, 2]
    
    # 1. Criterio de color fijo
    # R >= 60, R > G, G > B
    mask = (R >= 60) & (R > G) & (G > B)
    
    # 2. Componentes conectados
    labels = measure.label(mask, connectivity=2)
    
    if labels.max() > 0:
        # Encontrar el componente más grande
        largest_component = 0
        max_size = 0
        for region in measure.regionprops(labels):
            if region.area > max_size:
                max_size = region.area
                largest_component = region.label
        
        tumor_mask = (labels == largest_component)
    else:
        # 3. Fallback: Círculo 10x10 en el centro
        h, w = img_rgb.shape[:2]
        center_y, center_x = h // 2, w // 2
        Y, X = np.ogrid[:h, :w]
        dist_from_center = np.sqrt((X - center_x)**2 + (Y - center_y)**2)
        # Radio 5 para diámetro 10 aprox
        tumor_mask = dist_from_center <= 5
        
    return tumor_mask

def get_background_mask(tumor_mask, dilation_iter=10):
    """
    Genera una máscara de fondo como un anillo alrededor del tumor.
    Usa dilatación morfológica.
    """
    kernel = np.ones((3,3), np.uint8)
    
    # Dilatar la máscara del tumor para crear el borde exterior del anillo
    dilated = cv2.dilate(tumor_mask.astype(np.uint8), kernel, iterations=dilation_iter)
    
    # El anillo es la dilatación MENOS la máscara original
    background_mask = dilated.astype(bool) & ~tumor_mask
    
    # Si el anillo está vacío (ej. tumor ocupa casi todo), usar todo lo que no es tumor
    if background_mask.sum() == 0:
        background_mask = ~tumor_mask
        
    return background_mask

def calculate_single_cnr(img_rgb):
    """Calcula el CNR para una sola imagen."""
    # Asegurar float para cálculos
    if img_rgb.max() > 1.0:
        img_gray = cv2.cvtColor(img_rgb.astype(np.uint8), cv2.COLOR_RGB2GRAY) / 255.0
    else:
        img_gray = cv2.cvtColor((img_rgb * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY) / 255.0
        
    tumor_mask = get_tumor_mask(img_rgb)
    background_mask = get_background_mask(tumor_mask)
    
    # Extraer píxeles
    tumor_pixels = img_gray[tumor_mask]
    bg_pixels = img_gray[background_mask]
    
    if len(tumor_pixels) == 0 or len(bg_pixels) == 0:
        return 0.0
        
    mean_tumor = np.mean(tumor_pixels)
    mean_bg = np.mean(bg_pixels)
    std_bg = np.std(bg_pixels)
    
    if std_bg == 0:
        return 0.0
        
    # Fórmula clásica: Diferencia de señal / Ruido del fondo
    cnr = abs(mean_tumor - mean_bg) / std_bg
    return cnr

def calculate_cnr_metrics(layer_images, fused_image):
    """
    Calcula el CNR para las 7 capas y la imagen fusionada.
    
    Args:
        layer_images: Lista de 7 arrays numpy (RGB).
        fused_image: Array numpy de la imagen fusionada (RGB).
        
    Returns:
        max_layer_cnr: El valor máximo de CNR entre las 7 capas.
        fused_cnr: El valor de CNR de la imagen fusionada.
    """
    layer_cnrs = []
    for img in layer_images:
        cnr = calculate_single_cnr(img)
        layer_cnrs.append(cnr)
        
    max_layer_cnr = max(layer_cnrs) if layer_cnrs else 0.0
    
    fused_cnr = calculate_single_cnr(fused_image)
    
    return max_layer_cnr, fused_cnr

def sobel_gradient(img_gray):
    """
    Calcula magnitud y orientación del gradiente usando Sobel.
    Retorna: (magnitud, orientacion)
    """
    gx = cv2.Sobel(img_gray, cv2.CV_64F, 1, 0, ksize=3)
    gy = cv2.Sobel(img_gray, cv2.CV_64F, 0, 1, ksize=3)
    
    magnitude = np.sqrt(gx**2 + gy**2)
    orientation = np.arctan2(gy, gx) # Radianes [-pi, pi]
    
    return magnitude, orientation

def calculate_edge_preservation(layer_images, fused_image):
    """
    Calcula la métrica de Preservación de Bordes (Edge Preservation).
    
    Algoritmo:
    1. Para cada capa vs fusionada:
       - Calcular Sobel (Magnitud G, Orientación A).
       - Calcular similitud de magnitud (Qg) y orientación (Qa).
       - Q_pixel = Qg * Qa.
       - Score_capa = Promedio ponderado de Q_pixel (peso = G_original).
    2. Promedio aritmético de los 7 scores.
    
    Constantes (Xydeas & Petrovic):
    - Gamma_g = 0.9994, Kappa_g = -15, Sigma_g = 0.5
    - Gamma_a = 0.9879, Kappa_a = -22, Sigma_a = 0.8
    """
    # Constantes estándar para la métrica
    Gamma_g = 0.9994
    Kappa_g = -15
    Sigma_g = 0.5
    
    Gamma_a = 0.9879
    Kappa_a = -22
    Sigma_a = 0.8
    
    # Preparar imagen fusionada
    if fused_image.max() > 1.0:
        fused_gray = cv2.cvtColor(fused_image.astype(np.uint8), cv2.COLOR_RGB2GRAY) / 255.0
    else:
        fused_gray = cv2.cvtColor((fused_image * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY) / 255.0
        
    g_f, a_f = sobel_gradient(fused_gray)
    
    layer_scores = []
    
    for img in layer_images:
        # Preparar imagen de capa
        if img.max() > 1.0:
            img_gray = cv2.cvtColor(img.astype(np.uint8), cv2.COLOR_RGB2GRAY) / 255.0
        else:
            img_gray = cv2.cvtColor((img * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY) / 255.0
            
        g_l, a_l = sobel_gradient(img_gray)
        
        # --- Similitud de Magnitud (Qg) ---
        # Usamos la relación min/max para obtener un valor en [0, 1]
        # Xydeas espera un valor de similitud donde 1 es idéntico.
        numerator = np.minimum(g_l, g_f)
        denominator = np.maximum(g_l, g_f)
        denominator[denominator == 0] = 1e-6 # Evitar división por cero
        
        sim_g = numerator / denominator
        
        Q_g = Gamma_g / (1 + np.exp(Kappa_g * (sim_g - Sigma_g)))
        
        # --- Similitud de Orientación (Qa) ---
        diff_a = np.abs(a_l - a_f)
        # Ajuste cíclico para diferencia angular en rango [0, pi] (Sobel orientation es atan2 [-pi, pi])
        # Pero la orientación de borde es módulo pi? (un borde a 0 es igual a 180?)
        # Xydeas usa bordes direccionados o no?
        # Asumiremos diferencia absoluta normalizada en [0, pi/2] o [0, pi]?
        # atan2 da dirección del gradiente (que tiene signo).
        # La diferencia máxima es pi.
        # Normalizamos: sim_a = 1 - |diff| / pi?
        # Xydeas: A_AF = 1 - |alpha_A - alpha_F| / (pi/2). Esto implica rango pi/2.
        # Si usamos atan2, el rango es pi.
        # Ajustemos a rango [0, 1].
        
        # Diferencia angular mínima
        diff_a = np.minimum(diff_a, 2*np.pi - diff_a) # [0, pi]
        
        # Normalizar a [0, 1]. Si diff es 0 -> 1. Si diff es pi -> 0.
        sim_a = 1.0 - (diff_a / np.pi)
        
        Q_a = Gamma_a / (1 + np.exp(Kappa_a * (sim_a - Sigma_a)))
        
        # --- Score Combinado por Píxel ---
        Q_pixel = Q_g * Q_a
        
        # --- Promedio Ponderado (Peso = Magnitud Original) ---
        weight = g_l
        
        if np.sum(weight) == 0:
            layer_score = 0.0
        else:
            layer_score = np.sum(Q_pixel * weight) / np.sum(weight)
            
        layer_scores.append(layer_score)
        
    # Promedio final de las 7 capas
    final_metric = np.mean(layer_scores) if layer_scores else 0.0
    
    return final_metric

# Bloque de prueba
if __name__ == '__main__':
    # Generar imágenes sintéticas para probar
    print("Probando metrics.py con imágenes sintéticas...")
    
    # Imagen con ruido de fondo (para que std_bg != 0)
    np.random.seed(42)
    img_test = np.random.randint(0, 20, (100, 100, 3), dtype=np.uint8) 
    img_test[40:60, 40:60] = [200, 50, 50] # Rojo válido (Tumor)
    
    # Imagen negra pura (Fallback)
    img_empty = np.zeros((100, 100, 3), dtype=np.uint8)
    
    # Lista de capas (6 vacías + 1 con tumor)
    layers = [img_empty.copy() for _ in range(6)]
    layers.append(img_test)
    
    fused = img_test.copy()
    
    # Prueba CNR
    max_cnr, f_cnr = calculate_cnr_metrics(layers, fused)
    print(f"Max Layer CNR: {max_cnr:.4f}")
    print(f"Fused CNR:     {f_cnr:.4f}")
    
    # Prueba Edge Preservation
    # Debería ser alto para la capa idéntica y 0 para las vacías?
    # Las vacías tienen peso 0, así que score 0.
    # La idéntica debería tener score cercano a 1.
    # Promedio = (0*6 + 1*1)/7 ~= 0.14
    edge_score = calculate_edge_preservation(layers, fused)
    print(f"Edge Preserv:  {edge_score:.4f}")
    
    print("Test completado.")
