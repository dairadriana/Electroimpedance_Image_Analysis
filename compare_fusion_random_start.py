#!/usr/bin/env python3
"""
compare_fusion_random_start.py

Compara los dos métodos de fusión (prioridad vs promedio) ejecutando búsqueda local
en los 15 pacientes de validación con VECTORES INICIALES ALEATORIOS.

Diferencia con compare_fusion_methods.py:
- compare_fusion_methods.py: Usa el vector general como punto de partida
- compare_fusion_random_start.py: Usa vectores aleatorios como punto de partida

Resultados se guardan en:
- results_comparison_random/priority/
- results_comparison_random/average/
"""

import os
import glob
import random
import numpy as np
import time
from datetime import datetime

# Importar ambas funciones de fusión
from objective_function_priority import objective_function_priority
from objective_function import objective_function

# Importar utilidades
from utils_matlab_io import save_chromosome_mat


def get_all_prefixes(image_folder):
    """Scans the image_folder to find all unique patient prefixes."""
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
    """Returns the 15 validation patients using the same logic as main.py."""
    all_prefixes = get_all_prefixes(image_folder)
    total_patients = len(all_prefixes)
    
    if total_patients < 35:
        print("Warning: Less than 35 patients found. Using all available as validation.")
        return all_prefixes
        
    random.seed(42)  # Must match find_general_vector.py
    random.shuffle(all_prefixes)
    
    # First 35 are training, last 15 are validation
    val_prefixes = all_prefixes[35:]
    return val_prefixes


def find_patient_folder(base_folder, prefix):
    """Finds the subfolder containing images for the given patient prefix."""
    for subdir in glob.glob(os.path.join(base_folder, '*')):
        if os.path.isdir(subdir):
            if glob.glob(os.path.join(subdir, f'{prefix}_*.bmp')):
                return subdir
    return None


def random_initial_chromosome():
    """Genera un cromosoma inicial aleatorio con al menos un 1."""
    chrom = np.random.randint(0, 2, size=7, dtype=int)
    # Asegurar que al menos un bit esté en 1
    if chrom.sum() == 0:
        chrom[np.random.randint(0, 7)] = 1
    return chrom


def single_swap_custom(chromosome, image_folder, prefix, objective_func, time_limit=1800):
    """
    Búsqueda local con función objetivo personalizable.
    
    Args:
        chromosome: Vector inicial
        image_folder: Carpeta de imágenes
        prefix: Prefijo del paciente
        objective_func: Función objetivo a usar (priority o average)
        time_limit: Límite de tiempo en segundos
    """
    start_ls = time.time()
    
    # Lo mejor hasta ahora
    x_best = chromosome.copy()
    f_best, _ = objective_func(x_best, image_folder=image_folder, prefix=prefix)

    # Bandera
    mejora = True
    n = len(chromosome)
    indices = random.sample(range(n), n)

    while mejora and (time.time() - start_ls < time_limit):
        mejora = False

        for i in indices:
            x_temp = x_best.copy()
            x_temp[i] = 1 - x_best[i]

            if np.sum(x_temp) > 0:
                if time.time() - start_ls > time_limit:
                    break

                f_temp, _ = objective_func(x_temp, image_folder=image_folder, prefix=prefix)
                
                if f_temp > f_best:
                    x_best = x_temp.copy()
                    f_best = f_temp
                    mejora = True

                    indices = random.sample(list(range(i + 1, n)) + list(range(0, i)), n - 1)
                    break

    return x_best, f_best


def run_comparison_random(image_folder, time_limit, out_base_dir, random_seed=None):
    """
    Ejecuta la comparación completa entre ambos métodos de fusión
    usando vectores iniciales ALEATORIOS.
    """
    print("=" * 80)
    print("FUSION METHOD COMPARISON: Priority vs Average (RANDOM START)")
    print("=" * 80)
    
    # Configurar semilla aleatoria si se proporciona
    if random_seed is not None:
        np.random.seed(random_seed)
        random.seed(random_seed)
        print(f"\nRandom Seed: {random_seed}")
    
    print(f"Time Limit per Patient: {time_limit}s")
    
    # Obtener pacientes de validación
    val_patients = get_validation_patients(image_folder)
    print(f"\nValidation Patients ({len(val_patients)}): {val_patients}\n")
    
    # Crear directorios de salida
    priority_dir = os.path.join(out_base_dir, 'priority')
    average_dir = os.path.join(out_base_dir, 'average')
    os.makedirs(priority_dir, exist_ok=True)
    os.makedirs(average_dir, exist_ok=True)
    
    results = []
    
    for i, patient in enumerate(val_patients, 1):
        print(f"\n{'=' * 80}")
        print(f"[{i}/{len(val_patients)}] Processing patient: {patient}")
        print(f"{'=' * 80}")
        
        # Encontrar carpeta del paciente
        patient_folder = find_patient_folder(image_folder, patient)
        if patient_folder is None:
            print(f"ERROR: Could not find folder for patient {patient}")
            continue
            
        print(f"Located in: {patient_folder}")
        
        # Generar vector inicial aleatorio (MISMO para ambos métodos)
        initial_chrom = random_initial_chromosome()
        print(f"\nRandom Initial Vector: {initial_chrom}")
        
        # ========== PRIORITY FUSION ==========
        print(f"\n--- Running with PRIORITY fusion ---")
        start_time = time.time()
        
        best_priority, fitness_priority = single_swap_custom(
            initial_chrom.copy(), 
            patient_folder, 
            patient, 
            objective_function_priority,
            time_limit
        )
        
        priority_time = time.time() - start_time
        
        # Guardar resultados priority
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        chrom_path_p = os.path.join(priority_dir, f'best_chrom_{patient}_{timestamp}.mat')
        img_path_p = os.path.join(priority_dir, f'best_img_{patient}_{timestamp}.png')
        
        save_chromosome_mat(best_priority, chrom_path_p)
        _, _ = objective_function_priority(best_priority, image_folder=patient_folder, 
                                          prefix=patient, save_path=img_path_p)
        
        print(f"Priority - Fitness: {fitness_priority:.6f}, Time: {priority_time:.2f}s")
        print(f"Priority - Chromosome: {best_priority}")
        
        # ========== AVERAGE FUSION ==========
        print(f"\n--- Running with AVERAGE fusion ---")
        start_time = time.time()
        
        best_average, fitness_average = single_swap_custom(
            initial_chrom.copy(), 
            patient_folder, 
            patient, 
            objective_function,
            time_limit
        )
        
        average_time = time.time() - start_time
        
        # Guardar resultados average
        chrom_path_a = os.path.join(average_dir, f'best_chrom_{patient}_{timestamp}.mat')
        img_path_a = os.path.join(average_dir, f'best_img_{patient}_{timestamp}.png')
        
        save_chromosome_mat(best_average, chrom_path_a)
        _, _ = objective_function(best_average, image_folder=patient_folder, 
                                 prefix=patient, save_path=img_path_a)
        
        print(f"Average - Fitness: {fitness_average:.6f}, Time: {average_time:.2f}s")
        print(f"Average - Chromosome: {best_average}")
        
        # Comparación
        diff = fitness_priority - fitness_average
        winner = "PRIORITY" if diff > 0 else ("AVERAGE" if diff < 0 else "TIE")
        print(f"\n>>> Winner: {winner} (Δ = {diff:+.6f})")
        
        results.append({
            'patient': patient,
            'initial_chrom': initial_chrom,
            'fitness_priority': fitness_priority,
            'fitness_average': fitness_average,
            'chrom_priority': best_priority,
            'chrom_average': best_average,
            'time_priority': priority_time,
            'time_average': average_time,
            'winner': winner
        })
    
    # ========== GENERAR RESUMEN ==========
    print(f"\n{'=' * 80}")
    print("COMPARISON SUMMARY")
    print(f"{'=' * 80}\n")
    
    summary_path = os.path.join(out_base_dir, f'COMPARISON_SUMMARY_RANDOM_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt')
    
    with open(summary_path, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("FUSION METHOD COMPARISON RESULTS (RANDOM START)\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Random Seed: {random_seed if random_seed is not None else 'None (system time)'}\n")
        f.write(f"Time Limit: {time_limit}s per patient\n")
        f.write(f"Validation Patients: {val_patients}\n\n")
        
        f.write("=" * 80 + "\n")
        f.write("DETAILED RESULTS\n")
        f.write("=" * 80 + "\n\n")
        
        priority_wins = 0
        average_wins = 0
        ties = 0
        
        for r in results:
            f.write(f"Patient: {r['patient']}\n")
            f.write(f"  Initial:  {r['initial_chrom']}\n")
            f.write(f"  Priority: {r['fitness_priority']:.6f} | {r['chrom_priority']}\n")
            f.write(f"  Average:  {r['fitness_average']:.6f} | {r['chrom_average']}\n")
            f.write(f"  Winner:   {r['winner']} (Δ = {r['fitness_priority'] - r['fitness_average']:+.6f})\n")
            f.write(f"  Time:     Priority {r['time_priority']:.2f}s, Average {r['time_average']:.2f}s\n\n")
            
            if r['winner'] == 'PRIORITY':
                priority_wins += 1
            elif r['winner'] == 'AVERAGE':
                average_wins += 1
            else:
                ties += 1
        
        # Estadísticas
        fitness_p = [r['fitness_priority'] for r in results]
        fitness_a = [r['fitness_average'] for r in results]
        
        f.write("=" * 80 + "\n")
        f.write("STATISTICAL SUMMARY\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Total Patients: {len(results)}\n\n")
        f.write(f"Wins:\n")
        f.write(f"  Priority: {priority_wins} ({priority_wins/len(results)*100:.1f}%)\n")
        f.write(f"  Average:  {average_wins} ({average_wins/len(results)*100:.1f}%)\n")
        f.write(f"  Ties:     {ties} ({ties/len(results)*100:.1f}%)\n\n")
        f.write(f"Fitness Statistics:\n")
        f.write(f"  Priority - Mean: {np.mean(fitness_p):.6f}, Std: {np.std(fitness_p):.6f}\n")
        f.write(f"  Average  - Mean: {np.mean(fitness_a):.6f}, Std: {np.std(fitness_a):.6f}\n")
        f.write(f"  Difference Mean: {np.mean(fitness_p) - np.mean(fitness_a):+.6f}\n")
    
    print(f"Summary saved to: {summary_path}")
    print(f"\nPriority Wins: {priority_wins}/{len(results)}")
    print(f"Average Wins:  {average_wins}/{len(results)}")
    print(f"Ties:          {ties}/{len(results)}")
    
    return results


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Compare priority vs average fusion methods with random start')
    parser.add_argument('--image_folder', type=str, default='Images', 
                       help='Base folder containing patient images')
    parser.add_argument('--time_limit', type=int, default=1800,
                       help='Time limit in seconds per patient per method')
    parser.add_argument('--out_dir', type=str, default='results_comparison_random',
                       help='Output directory for comparison results')
    parser.add_argument('--random_seed', type=int, default=None,
                       help='Random seed for reproducibility (optional)')
    args = parser.parse_args()
    
    run_comparison_random(args.image_folder, args.time_limit, args.out_dir, args.random_seed)


if __name__ == '__main__':
    main()
