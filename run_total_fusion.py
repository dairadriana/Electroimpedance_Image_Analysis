#!/usr/bin/env python3
"""
run_total_fusion.py

Ejecuta la fusión de imágenes seleccionando TODAS las 7 capas (cromosoma de unos)
para los pacientes de validación, usando ambos métodos:
1. Prioridad (objective_function_priority)
2. Promedio (objective_function)

Guarda los resultados en:
- results_total/priority/
- results_total/average/
"""

import os
import glob
import random
import numpy as np
from datetime import datetime

# Importar funciones de fusión
from objective_function_priority import objective_function_priority
from objective_function import objective_function

def get_all_prefixes(image_folder):
    """Scans the image_folder to find all unique patient prefixes."""
    prefixes = set()
    # Buscar archivos .bmp en subcarpetas
    search_path = os.path.join(image_folder, '*', '*.bmp')
    files = glob.glob(search_path)
    
    for file_path in files:
        filename = os.path.basename(file_path)
        parts = filename.split('_')
        if len(parts) >= 1:
            prefixes.add(parts[0])
            
    return sorted(list(prefixes))

def get_validation_patients(image_folder):
    """
    Retorna los pacientes de validación.
    Si hay < 35 pacientes, usa todos.
    Si hay >= 35, usa los que están después del índice 35 (validación).
    """
    all_prefixes = get_all_prefixes(image_folder)
    total_patients = len(all_prefixes)
    
    if total_patients < 35:
        print(f"Aviso: Se encontraron {total_patients} pacientes (menos de 35). Usando TODOS para validación.")
        return all_prefixes
        
    random.seed(42)
    random.shuffle(all_prefixes)
    
    # Los últimos (total - 35) son validación. 
    # Si total=47, 47-35=12 pacientes.
    val_prefixes = all_prefixes[35:]
    return val_prefixes

def find_patient_folder(base_folder, prefix):
    """Encuentra la carpeta del paciente dado su prefijo."""
    for subdir in glob.glob(os.path.join(base_folder, '*')):
        if os.path.isdir(subdir):
            if glob.glob(os.path.join(subdir, f'{prefix}_*.bmp')):
                return subdir
    return None

def run_total_fusion(image_folder='Images', out_base_dir='results_total'):
    print("=" * 80)
    print("RUNNING TOTAL FUSION (All 7 Layers) on Validation Patients")
    print("=" * 80)
    
    # Definir cromosoma con todas las capas activas
    full_chromosome = np.ones(7, dtype=int)
    print(f"Chromosome: {full_chromosome}")
    
    # Obtener pacientes
    val_patients = get_validation_patients(image_folder)
    print(f"Validation Patients ({len(val_patients)}): {val_patients}\n")
    
    # Directorios de salida
    priority_dir = os.path.join(out_base_dir, 'priority')
    average_dir = os.path.join(out_base_dir, 'average')
    os.makedirs(priority_dir, exist_ok=True)
    os.makedirs(average_dir, exist_ok=True)
    
    results = []
    
    for i, patient in enumerate(val_patients, 1):
        print(f"[{i}/{len(val_patients)}] Processing {patient}...")
        
        patient_folder = find_patient_folder(image_folder, patient)
        if not patient_folder:
            print(f"  ERROR: Folder not found for {patient}")
            continue
            
        # --- Priority Fusion ---
        img_name_p = f'{patient}_total_priority.png'
        save_path_p = os.path.join(priority_dir, img_name_p)
        
        f_p, _ = objective_function_priority(full_chromosome, patient_folder, patient, save_path=save_path_p)
        
        # --- Average Fusion ---
        img_name_a = f'{patient}_total_average.png'
        save_path_a = os.path.join(average_dir, img_name_a)
        
        f_a, _ = objective_function(full_chromosome, patient_folder, patient, save_path=save_path_a)
        
        print(f"  Priority Fitness: {f_p:.6f}")
        print(f"  Average Fitness:  {f_a:.6f}")
        
        results.append({
            'Patient': patient,
            'Fitness_Priority': f_p,
            'Fitness_Average': f_a,
            'Difference': f_p - f_a
        })

    # Guardar resumen en CSV y TXT
    if results:
        import csv
        
        # Guardar CSV
        csv_path = os.path.join(out_base_dir, 'total_fusion_results.csv')
        keys = results[0].keys()
        with open(csv_path, 'w', newline='') as f:
            dict_writer = csv.DictWriter(f, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(results)
        print(f"\nResults saved to {csv_path}")
        
        # Calcular promedios
        avg_p = sum(r['Fitness_Priority'] for r in results) / len(results)
        avg_a = sum(r['Fitness_Average'] for r in results) / len(results)
        
        # Resumen de texto
        txt_path = os.path.join(out_base_dir, 'summary.txt')
        with open(txt_path, 'w') as f:
            f.write("TOTAL FUSION RESULTS (All 7 Layers)\n")
            f.write("===================================\n\n")
            
            # Header
            header = f"{'Patient':<15} | {'Fitness_Priority':<18} | {'Fitness_Average':<18} | {'Difference':<12}"
            f.write(header + "\n")
            f.write("-" * len(header) + "\n")
            
            for r in results:
                line = f"{r['Patient']:<15} | {r['Fitness_Priority']:<18.6f} | {r['Fitness_Average']:<18.6f} | {r['Difference']:<12.6f}"
                f.write(line + "\n")
                
            f.write("\n")
            f.write(f"Average Priority Fitness: {avg_p:.6f}\n")
            f.write(f"Average Average Fitness:  {avg_a:.6f}\n")
        print(f"Summary text saved to {txt_path}")

if __name__ == '__main__':
    run_total_fusion()
