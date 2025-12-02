#!/usr/bin/env python3
"""
Perform an exhaustive search (brute force) on the 127 possible combinations.
Outputs in ‘results_data_analysis/’:
1. SUMMARY_AVERAGES_...txt: Average fitness of all vectors (sorted).
2. DETAILS_{patient}_...txt: 10 files with the performance of all vectors for each patient.
3. BEST_GLOBAL_...: .mat and .png files of the global winning vector (using parsimony criteria).
"""

import os
import numpy as np
import itertools
from objective_function import objective_function as evaluate_individual
from utils_matlab_io import save_chromosome_mat
import time
import glob
import random

def get_all_prefixes(image_folder):
    """
    Scans the image_folder to find all unique patient prefixes.
    Assumes structure: image_folder/Prefix_N#_mask.bmp or image_folder/*/Prefix_N#_mask.bmp
    """
    prefixes = set()
    # Search in subdirectories (e.g., Images/Prueba/*.bmp)
    search_path = os.path.join(image_folder, '*', '*.bmp')
    files = glob.glob(search_path)
    
    for file_path in files:
        filename = os.path.basename(file_path)
        # Split by underscore to get the prefix
        parts = filename.split('_')
        if len(parts) >= 1:
            prefixes.add(parts[0])
            
    return sorted(list(prefixes))

def main():
    image_folder = 'Images'
    epsilon = 0.002
    
    # 1. Get all available patients
    all_prefixes = get_all_prefixes(image_folder)
    total_patients = len(all_prefixes)
    print(f"Total unique patients found: {total_patients}")
    
    if total_patients < 35:
        print("Warning: Less than 35 patients found. Using all available.")
        train_size = total_patients
    else:
        train_size = 35
        
    # 2. Randomly select 35 for training
    random.seed(42) # Fixed seed for reproducibility
    random.shuffle(all_prefixes)
    
    train_prefixes = all_prefixes[:train_size]
    val_prefixes = all_prefixes[train_size:]
    
    print(f"\nSelected {len(train_prefixes)} patients for TRAINING (General Vector Search):")
    print(train_prefixes)
    
    print(f"\nReserved {len(val_prefixes)} patients for VALIDATION (Local Search):")
    print(val_prefixes)
    print("-" * 50)

    best_avg_fitness = float('-inf')
    best_chromosome = None
    all_chromosomes = []  

    total_combinations = 2**7 - 1  
    count = 0

    start_time = time.time()

    for chrom_tuple in itertools.product([0, 1], repeat=7):
        chrom = np.array(chrom_tuple, dtype=int)
        if chrom.sum() == 0:
            continue

        count += 1
        print(f'Evaluating chromosome {count}/{total_combinations}: {chrom}')

        fitnesses = []
        for prefix in train_prefixes:
            try:
                
                f, _ = evaluate_individual(chrom, image_folder=image_folder, prefix=prefix)
                fitnesses.append(f)
            except Exception as e:
                # Fallback: try to find the specific subfolder for this prefix if the generic call fails
                # This is a bit of a hack without seeing objective_function, but let's try to be robust
                found = False
                for subdir in glob.glob(os.path.join(image_folder, '*')):
                    if os.path.isdir(subdir):
                         try:
                            f, _ = evaluate_individual(chrom, image_folder=subdir, prefix=prefix)
                            fitnesses.append(f)
                            found = True
                            break
                         except:
                             continue
                if not found:
                    pass
                continue

        if fitnesses:
            avg_fitness = sum(fitnesses) / len(fitnesses)
            print(f'  Average fitness: {avg_fitness:.6f} (over {len(fitnesses)} patients)')
            if avg_fitness > best_avg_fitness + epsilon:
                best_avg_fitness = avg_fitness
                best_chromosome = chrom.copy()
            elif abs(avg_fitness - best_avg_fitness) <= epsilon:
                if chrom.sum() < best_chromosome.sum():
                    best_avg_fitness = avg_fitness
                    best_chromosome = chrom.copy()

            all_chromosomes.append((avg_fitness, chrom.copy(), fitnesses.copy()))
        else:
            print('  No valid fitnesses')

    end_time = time.time()
    print(f'\nBúsqueda completada en {end_time - start_time:.2f} segundos')

    # Sort all chromosomes by average fitness descending
    all_chromosomes.sort(key=lambda x: -x[0])

    # Create results folder
    out_dir = 'results_data_analysis'
    os.makedirs(out_dir, exist_ok=True)
    timestamp = time.strftime('%Y%m%d_%H%M%S')

    # Save BEST_GLOBAL_chrom_FECHA.mat
    chrom_path = os.path.join(out_dir, f'BEST_GLOBAL_chrom_{len(train_prefixes)}patients_{timestamp}.mat')
    save_chromosome_mat(best_chromosome, chrom_path)
    print(f'Chromosome saved: {chrom_path}')

    # Save BEST_GLOBAL_img_FECHA.png
    # Try to find a valid folder for the first prefix to save the image
    first_prefix = train_prefixes[0]
    img_path = os.path.join(out_dir, f'BEST_GLOBAL_img_{len(train_prefixes)}patients_{timestamp}.png')
    
    saved_img = False
    # Try base folder
    try:
        _, _ = evaluate_individual(best_chromosome, image_folder=image_folder, prefix=first_prefix, save_path=img_path)
        saved_img = True
    except:
        # Try subfolders
        for subdir in glob.glob(os.path.join(image_folder, '*')):
            if os.path.isdir(subdir):
                try:
                    _, _ = evaluate_individual(best_chromosome, image_folder=subdir, prefix=first_prefix, save_path=img_path)
                    saved_img = True
                    break
                except:
                    continue
    
    if saved_img:
        print(f'Image saved: {img_path}')
    else:
        print('Could not save image (path issue)')

    # Save SUMMARY_AVERAGES_FECHA.txt
    summary_path = os.path.join(out_dir, f'SUMMARY_AVERAGES_{len(train_prefixes)}patients_{timestamp}.txt')
    with open(summary_path, 'w') as f:
        f.write(f'Summary of all 127 combinations ordered by average fitness (best to worst) over {len(train_prefixes)} patients:\n\n')
        f.write(f'Training Patients: {train_prefixes}\n')
        f.write(f'Validation Patients: {val_prefixes}\n\n')
        for i, (avg_f, chrom, _) in enumerate(all_chromosomes, 1):
            f.write(f'{i}. Average Fitness: {avg_f:.6f}, Chromosome: {chrom.tolist()}\n')
    print(f'Summary saved: {summary_path}')


    for idx, prefix in enumerate(train_prefixes):
        details_path = os.path.join(out_dir, f'DETAILS_{prefix}_{timestamp}.txt')
        
        valid_entries = []
        for avg_f, chrom, fits in all_chromosomes:
            if idx < len(fits):
                valid_entries.append((avg_f, chrom, fits))
        
        sorted_for_prefix = sorted(valid_entries, key=lambda x: -x[2][idx])
        
        with open(details_path, 'w') as f:
            f.write(f'Details for patient {prefix}, combinations ordered by fitness (best to worst):\n\n')
            for i, (avg_f, chrom, fitnesses) in enumerate(sorted_for_prefix, 1):
                f.write(f'{i}. Fitness: {fitnesses[idx]:.6f}, Average: {avg_f:.6f}, Chromosome: {chrom.tolist()}\n')
        # print(f'Details for {prefix} saved: {details_path}')
    print(f"Saved individual detail files for all {len(train_prefixes)} training patients.")

    if best_chromosome is not None:
        print('\n=== MEJOR VECTOR GENERAL ===')
        print(f'Chromosome: {best_chromosome}')
        print(f'Average fitness: {best_avg_fitness:.6f}')
    else:
        print('No se encontró un cromosoma válido')

if __name__ == '__main__':
    main()