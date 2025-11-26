#!/usr/bin/env python3
"""
find_general_vector.py

Realiza una búsqueda exhaustiva (fuerza bruta) sobre las 127 combinaciones posibles.

Salidas en 'results_data_analysis/':
1. SUMMARY_AVERAGES_...txt: Promedio de fitness de todos los vectores (ordenado).
2. DETAILS_{paciente}_...txt: 10 archivos con el desempeño de todos los vectores para cada paciente.
3. BEST_GLOBAL_...: Archivos .mat y .png del vector ganador global (usando criterio de parsimonia).
"""

import os
import numpy as np
import itertools
from objective_function import objective_function as evaluate_individual
from utils_matlab_io import save_chromosome_mat
import time
def main():
    image_folder = 'Images/Prueba'
    prefixes = ['C0011d', 'C0012d', 'C0024d', 'C0030d', 'C0676d', 'C0683d', 'C0685d', 'C0747d', 'C0844d', 'C0845d']
    epsilon = 0.002

    best_avg_fitness = float('-inf')
    best_chromosome = None
    all_chromosomes = []  # Lista de (avg_fitness, chrom, fitnesses)

    total_combinations = 2**7 - 1  # 127
    count = 0

    start_time = time.time()

    for chrom_tuple in itertools.product([0, 1], repeat=7):
        chrom = np.array(chrom_tuple, dtype=int)
        if chrom.sum() == 0:
            continue

        count += 1
        print(f'Evaluating chromosome {count}/{total_combinations}: {chrom}')

        fitnesses = []
        for prefix in prefixes:
            try:
                f, _ = evaluate_individual(chrom, image_folder=image_folder, prefix=prefix)
                fitnesses.append(f)
            except Exception as e:
                print(f"Error evaluating {chrom} on {prefix}: {e}")
                continue

        if fitnesses:
            avg_fitness = sum(fitnesses) / len(fitnesses)
            print(f'  Average fitness: {avg_fitness:.6f}')
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
    chrom_path = os.path.join(out_dir, f'BEST_GLOBAL_chrom_{timestamp}.mat')
    save_chromosome_mat(best_chromosome, chrom_path)
    print(f'Chromosome saved: {chrom_path}')

    # Save BEST_GLOBAL_img_FECHA.png
    img_path = os.path.join(out_dir, f'BEST_GLOBAL_img_{timestamp}.png')
    _, _ = evaluate_individual(best_chromosome, image_folder=image_folder, prefix=prefixes[0], save_path=img_path)
    print(f'Image saved: {img_path}')

    # Save SUMMARY_AVERAGES_FECHA.txt
    summary_path = os.path.join(out_dir, f'SUMMARY_AVERAGES_{timestamp}.txt')
    with open(summary_path, 'w') as f:
        f.write('Summary of all 127 combinations ordered by average fitness (best to worst):\n\n')
        for i, (avg_f, chrom, _) in enumerate(all_chromosomes, 1):
            f.write(f'{i}. Average Fitness: {avg_f:.6f}, Chromosome: {chrom.tolist()}\n')
    print(f'Summary saved: {summary_path}')

    # Save DETAILS for each prefix
    for idx, prefix in enumerate(prefixes):
        details_path = os.path.join(out_dir, f'DETAILS_{prefix}_{timestamp}.txt')
        # Sort by fitness for this prefix descending
        sorted_for_prefix = sorted(all_chromosomes, key=lambda x: -x[2][idx])
        with open(details_path, 'w') as f:
            f.write(f'Details for patient {prefix}, combinations ordered by fitness (best to worst):\n\n')
            for i, (avg_f, chrom, fitnesses) in enumerate(sorted_for_prefix, 1):
                f.write(f'{i}. Fitness: {fitnesses[idx]:.6f}, Average: {avg_f:.6f}, Chromosome: {chrom.tolist()}\n')
        print(f'Details for {prefix} saved: {details_path}')

    if best_chromosome is not None:
        print('\n=== MEJOR VECTOR GENERAL ===')
        print(f'Chromosome: {best_chromosome}')
        print(f'Average fitness: {best_avg_fitness:.6f}')
    else:
        print('No se encontró un cromosoma válido')

if __name__ == '__main__':
    main()