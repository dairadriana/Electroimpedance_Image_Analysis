#!/usr/bin/env python3
"""
local_search.py

Implementa una búsqueda local (hill-climbing / first-improvement) sobre el
espacio de vectores binarios de 7 bits. La evaluación se realiza usando
`evaluate_individual.evaluate_individual`, que replica `multipleImageProcessing.m`.

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
from datetime import datetime

from evaluate_individual import evaluate_individual
from utils_matlab_io import save_chromosome_mat


def random_initial_chromosome() -> np.ndarray:
    chrom = np.random.randint(0, 2, size=(7,), dtype=int)
    if chrom.sum() == 0:
        chrom[np.random.randint(0, 7)] = 1
    return chrom


def neighbors(chrom: np.ndarray):
    # Genera vecinos con Hamming distance = 1, evita el vector todo-ceros
    neighs = []
    for i in range(7):
        n = chrom.copy()
        n[i] = 1 - n[i]
        if n.sum() == 0:
            # evitar vecinos inválidos que sean todo ceros
            continue
        neighs.append(n)
    return neighs


def hill_climbing(image_folder: str, prefix: str, out_dir: str, max_iters: int = 1000):
    if not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    # Inicializar
    current = random_initial_chromosome()
    current_score, current_img = evaluate_individual(current, image_folder=image_folder, prefix=prefix)
    print(f'Initial: {current} -> {current_score:.6f}')

    best = current.copy()
    best_score = current_score
    iter_count = 0
    improved = True

    while improved and iter_count < max_iters:
        improved = False
        iter_count += 1

        # Explorar vecinos (orden fijo) - first-improvement
        for n in neighbors(current):
            score_n, img_n = evaluate_individual(n, image_folder=image_folder, prefix=prefix)
            if score_n > best_score:
                best = n.copy()
                best_score = score_n
                current = n.copy()
                current_score = score_n
                print(f'Iter {iter_count}: new best {best} -> {best_score:.6f}')
                improved = True
                break
        # Si no encontramos mejora, terminamos

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    chrom_path = os.path.join(out_dir, f'best_chrom_{timestamp}.mat')
    img_path = os.path.join(out_dir, f'best_img_{timestamp}.png')

    # Guardar cromosoma y la imagen resultante final
    save_chromosome_mat(best, chrom_path)
    # Guardamos la imagen final con evaluate_individual (pedimos la imagen)
    final_score, final_img = evaluate_individual(best, image_folder=image_folder, prefix=prefix, save_path=img_path)

    print('\n=== RESULTADO FINAL ===')
    print(f'Best chromosome: {best} (fitness: {best_score:.6f})')
    print(f'Chromosome saved: {chrom_path}')
    print(f'Image saved: {img_path}')

    return best, best_score, chrom_path, img_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--image_folder', type=str, default='/home/ashley/projects/Electroimpedance_Image_Analysis/Images/Prueba')
    parser.add_argument('--prefix', type=str, default='C0683d')
    parser.add_argument('--out_dir', type=str, default='results')
    parser.add_argument('--max_iters', type=int, default=200)
    args = parser.parse_args()

    hill_climbing(args.image_folder, args.prefix, args.out_dir, max_iters=args.max_iters)


if __name__ == '__main__':
    main()
