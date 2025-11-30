#!/usr/bin/env python3
"""
run_all_metrics.py

Calcula métricas (CNR, Edge Preservation) para los 15 pacientes de validación
en los 4 experimentos solicitados:
1. Total Fusion (7 capas)
2. Vector de Referencia
3. LS Random Start
4. LS Reference Start

Guarda resultados en metrics_results/*.txt
"""

import os
import glob
import cv2
import numpy as np
import random
from metrics import calculate_cnr_metrics, calculate_edge_preservation

def get_all_prefixes(image_folder):
    prefixes = set()
    search_path = os.path.join(image_folder, '*', '*.bmp')
    files = glob.glob(search_path)
    for file_path in files:
        filename = os.path.basename(file_path)
        parts = filename.split('_')
        if len(parts) >= 1:
            prefixes.add(parts[0])
    return sorted(list(prefixes))

def get_validation_patients(image_folder):
    all_prefixes = get_all_prefixes(image_folder)
    total_patients = len(all_prefixes)
    if total_patients < 35:
        return all_prefixes
    random.seed(42)
    random.shuffle(all_prefixes)
    return all_prefixes[35:]

def find_patient_folder(base_folder, prefix):
    for subdir in glob.glob(os.path.join(base_folder, '*')):
        if os.path.isdir(subdir):
            if glob.glob(os.path.join(subdir, f'{prefix}_*.bmp')):
                return subdir
    return None

def load_layer_images(patient_folder, prefix):
    """Carga las 7 capas originales de un paciente."""
    layers = []
    for i in range(1, 8):
        filename = f'{prefix}_N{i}_mask.bmp'
        path = os.path.join(patient_folder, filename)
        if os.path.exists(path):
            img = cv2.imread(path)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            layers.append(img)
        else:
            # Si falta, usar imagen negra del tamaño de referencia (N7)
            # Asumimos que N7 existe o fallará antes
            ref_path = os.path.join(patient_folder, f'{prefix}_N7_mask.bmp')
            if os.path.exists(ref_path):
                ref = cv2.imread(ref_path)
                layers.append(np.zeros_like(ref))
            else:
                raise FileNotFoundError(f"No se pudo cargar capa ni referencia para {prefix}")
    return layers

def find_fused_image(input_dir, prefix, experiment_type, pattern_prefix='best_img'):
    """
    Encuentra la imagen fusionada según el tipo de experimento.
    """
    if experiment_type == 'total':
        # Patrón: prefix_total_method.png
        method = os.path.basename(input_dir) # average o priority
        filename = f'{prefix}_total_{method}.png'
        path = os.path.join(input_dir, filename)
        if os.path.exists(path):
            return path
            
    else:
        # Patrón: {pattern_prefix}_{prefix}_timestamp.png
        pattern = os.path.join(input_dir, f'{pattern_prefix}_{prefix}_*.png')
        files = glob.glob(pattern)
        if files:
            return sorted(files)[-1]
            
    return None

def process_experiment(experiment_name, input_subpath, output_filename, image_folder='Images', pattern_prefix='best_img'):
    print(f"\nProcessing Experiment: {experiment_name}")
    print(f"Input: {input_subpath} -> Output: {output_filename}")
    
    val_patients = get_validation_patients(image_folder)
    results = []
    
    # Determinar tipo de experimento para búsqueda de archivos
    if 'results_total' in input_subpath:
        exp_type = 'total'
    else:
        exp_type = 'optimization'
        
    full_input_dir = os.path.join(os.getcwd(), input_subpath)
    
    for i, patient in enumerate(val_patients, 1):
        print(f"  [{i}/{len(val_patients)}] {patient}...", end='', flush=True)
        
        # 1. Cargar capas originales
        p_folder = find_patient_folder(image_folder, patient)
        if not p_folder:
            print(" Patient folder not found.")
            continue
            
        try:
            layers = load_layer_images(p_folder, patient)
        except Exception as e:
            print(f" Error loading layers: {e}")
            continue
            
        # 2. Cargar imagen fusionada
        fused_path = find_fused_image(full_input_dir, patient, exp_type, pattern_prefix)
        if not fused_path:
            print(f" Fused image not found (pattern: {pattern_prefix}_{patient}_*).")
            continue
            
        fused_img = cv2.imread(fused_path)
        fused_img = cv2.cvtColor(fused_img, cv2.COLOR_BGR2RGB)
        
        # 3. Calcular métricas
        try:
            max_cnr, fused_cnr = calculate_cnr_metrics(layers, fused_img)
            edge_score = calculate_edge_preservation(layers, fused_img)
            
            results.append({
                'Patient': patient,
                'Max_Layer_CNR': max_cnr,
                'Fused_CNR': fused_cnr,
                'Edge_Preservation': edge_score
            })
            print(" Done.")
            
        except Exception as e:
            print(f" Error calculating metrics: {e}")

    # Guardar resultados
    out_path = os.path.join('metrics_results', output_filename)
    with open(out_path, 'w') as f:
        # Header
        f.write(f"METRICS RESULTS: {experiment_name}\n")
        f.write("=================================================================\n")
        f.write(f"{'Patient':<10} | {'Max_Layer_CNR':<15} | {'Fused_CNR':<15} | {'Edge_Preserv':<15}\n")
        f.write("-" * 65 + "\n")
        
        avg_max_cnr = 0
        avg_fused_cnr = 0
        avg_edge = 0
        
        if results:
            for r in results:
                f.write(f"{r['Patient']:<10} | {r['Max_Layer_CNR']:<15.6f} | {r['Fused_CNR']:<15.6f} | {r['Edge_Preservation']:<15.6f}\n")
                
            avg_max_cnr = sum(r['Max_Layer_CNR'] for r in results) / len(results)
            avg_fused_cnr = sum(r['Fused_CNR'] for r in results) / len(results)
            avg_edge = sum(r['Edge_Preservation'] for r in results) / len(results)
            
        f.write("-" * 65 + "\n")
        f.write(f"{'AVERAGE':<10} | {avg_max_cnr:<15.6f} | {avg_fused_cnr:<15.6f} | {avg_edge:<15.6f}\n")
        
    print(f"Saved results to {out_path}")

def main():
    # 1. Total Fusion (7 capas)
    process_experiment("Total Fusion (Average)", "results_total/average", "complete_fusion_average.txt")
    process_experiment("Total Fusion (Priority)", "results_total/priority", "complete_fusion_priority.txt")
    
    # 2. Vector de Referencia (Solo capas del vector)
    process_experiment("Reference Vector (Average)", "results_reference_vector/average", "vector_reference_average.txt", pattern_prefix='ref_img')
    process_experiment("Reference Vector (Priority)", "results_reference_vector/priority", "vector_reference_priority.txt", pattern_prefix='ref_img')
    
    # 3. LS Random Start
    process_experiment("LS Random Start (Average)", "results_comparison_random/average", "LS_average.txt")
    process_experiment("LS Random Start (Priority)", "results_comparison_random/priority", "LS_priority.txt")
    
    # 4. LS Reference Start (results_comparison)
    process_experiment("LS Reference Start (Average)", "results_comparison/average", "LS_vector_reference_average.txt")
    process_experiment("LS Reference Start (Priority)", "results_comparison/priority", "LS_vector_reference_priority.txt")

if __name__ == '__main__':
    main()
