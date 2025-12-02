#!/usr/bin/env python3
"""
local_search.py

Implementa una búsqueda local basada en single swap con orden aleatorio y reinicio
sobre el espacio de vectores binarios de 7 bits. La evaluación se realiza usando
`objective_function`, que procesa imágenes de impedancia eléctrica
para calcular el fitness del individuo.

Salida:
 - Guarda el mejor cromosoma en un archivo .mat para compatibilidad con MATLAB
 - Guarda la imagen resultante (PNG)
 - Imprime en consola el mejor cromosoma y su fitness

Uso:
    python3 local_search.py --image_folder PATH --prefix C0683d --out_dir results

"""

import os
import argparse
import numpy as np
import random
import time
import glob
from datetime import datetime

from objective_function import objective_function
from utils_matlab_io import save_chromosome_mat, load_chromosome_mat


def single_swap(chromosome: np.ndarray, image_folder: str, prefix: str, time_limit: int = 1800):
    """
    Implements a local search using single-bit flips in random order.
    Starts with the given chromosome, evaluates individual flips, accepts improvements, and resets
    the search order. Continues until no improvements are found or the time limit is reached.
    Returns the best chromosome found and its fitness.
    """
    start_ls = time.time()
    
    # Best so far
    x_best = chromosome[:]
    f_best, _ = objective_function(x_best, image_folder=image_folder, prefix=prefix)

    mejora = True
    n = len(chromosome)
    indices = random.sample(range(n), n)  # Permutación

    while mejora and (time.time() - start_ls < time_limit):
        mejora = False

        for i in indices:
            x_temp = x_best[:]
            x_temp[i] = 1 - x_best[i]  # Swap 0 <-> 1

            # Check feasibility (at least one 1)
            if np.sum(x_temp) > 0:
                # Compare solutions and decide whether to keep the change
                if time.time() - start_ls > time_limit:
                    break  # If time limit exceeded before calculating error, break while

                f_temp, _ = objective_function(x_temp, image_folder=image_folder, prefix=prefix)
                
                if f_temp > f_best:
                    x_best = x_temp[:]
                    f_best = f_temp
                    mejora = True  # There was an improvement, continue iterating

                    # Circular random change on the new solution
                    indices = random.sample(list(range(i + 1, n)) + list(range(0, i)), n - 1)
                    break  # Restart iteration with the new best solution
    return x_best, f_best


def local_search(image_folder: str, prefix: str, out_dir: str, initial_vector_path: str, time_limit: int = 1800):
    if not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    # Initialize
    """
    Runs the local search with an initial chromosome loaded from a file, saves the result
    in .mat and .png files, and prints the best chromosome and its fitness.
    """
    initial_chrom = load_chromosome_mat(initial_vector_path)
    print(f'Initial: {initial_chrom}')

    best, best_score = single_swap(initial_chrom, image_folder, prefix, time_limit)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    chrom_path = os.path.join(out_dir, f'best_chrom_{prefix}_{timestamp}.mat')
    img_path = os.path.join(out_dir, f'best_img_{prefix}_{timestamp}.png')

    save_chromosome_mat(best, chrom_path)
    final_score, final_img = objective_function(best, image_folder=image_folder, prefix=prefix, save_path=img_path)

    print('\n=== RESULTADO FINAL ===')
    print(f'Best chromosome: {best} (fitness: {best_score:.6f})')
    print(f'Chromosome saved: {chrom_path}')
    print(f'Image saved: {img_path}')

    return best, best_score, chrom_path, img_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--image_folder', type=str, required=True, help='Path to the folder containing patient images')
    parser.add_argument('--prefix', type=str, required=True, help='Patient prefix (e.g., C0683d)')
    parser.add_argument('--out_dir', type=str, default='results_local_search')
    parser.add_argument('--initial_vector', type=str, required=True, help='Path to .mat file containing the initial chromosome')
    parser.add_argument('--time_limit', type=int, default=1800, help='Time limit in seconds')
    args = parser.parse_args()

    local_search(args.image_folder, args.prefix, args.out_dir, args.initial_vector, time_limit=args.time_limit)


if __name__ == '__main__':
    main()
