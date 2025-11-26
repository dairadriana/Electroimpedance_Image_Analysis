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
from datetime import datetime

from objective_function import objective_function
from utils_matlab_io import save_chromosome_mat, load_chromosome_mat


# def random_initial_chromosome() -> np.ndarray:
#     chrom = np.random.randint(0, 2, size=(7,), dtype=int)
#     if chrom.sum() == 0:
#         chrom[np.random.randint(0, 7)] = 1
#     return chrom


def single_swap(chromosome: np.ndarray, image_folder: str, prefix: str, time_limit: int = 1800):
    """
    Implementa una búsqueda local mediante flips de un solo bit en orden aleatorio.
    Comienza con el cromosoma dado, evalúa flips individuales, acepta mejoras y reinicia
    el orden de exploración. Continúa hasta no encontrar mejoras o agotar el tiempo límite.
    Devuelve el mejor cromosoma encontrado y su fitness.
    """
    start_ls = time.time()
    
    # Lo mejor hasta ahora
    x_best = chromosome[:]
    f_best, _ = objective_function(x_best, image_folder=image_folder, prefix=prefix)

    # Bandera
    mejora = True
    n = len(chromosome)
    indices = random.sample(range(n), n)  # Permutación

    while mejora and (time.time() - start_ls < time_limit):
        mejora = False

        for i in indices:
            x_temp = x_best[:]
            x_temp[i] = 1 - x_best[i]  # Cambio 0 <-> 1

            # Verificar factibilidad (al menos un 1)
            if np.sum(x_temp) > 0:
                # Comparar soluciones y decidir si mantener el cambio
                if time.time() - start_ls > time_limit:
                    break  # Si antes de calcular el error ya se pasó de tiempo romper while

                f_temp, _ = objective_function(x_temp, image_folder=image_folder, prefix=prefix)
                
                if f_temp > f_best:
                    x_best = x_temp[:]
                    f_best = f_temp
                    mejora = True  # Hubo mejora, seguimos iterando

                    # Cambio aleatorio circular sobre la nueva solución
                    indices = random.sample(list(range(i + 1, n)) + list(range(0, i)), n - 1)
                    break  # Reiniciamos la iteración con la nueva mejor solución

    return x_best, f_best


def local_search(image_folder: str, prefix: str, out_dir: str, time_limit: int = 1800):
    if not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    # Inicializar
    """
    Ejecuta la búsqueda local con un cromosoma inicial cargado desde archivo, guarda el resultado
    en archivos .mat y .png, e imprime el mejor cromosoma y su fitness.
    """
    initial_chrom = load_chromosome_mat('results_data_analysis/BEST_GLOBAL_chrom_20251125_224838.mat')
    print(f'Initial: {initial_chrom}')

    best, best_score = single_swap(initial_chrom, image_folder, prefix, time_limit)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    chrom_path = os.path.join(out_dir, f'best_chrom_{timestamp}.mat')
    img_path = os.path.join(out_dir, f'best_img_{timestamp}.png')

    # Guardar cromosoma y la imagen resultante final
    save_chromosome_mat(best, chrom_path)
    # Guardamos la imagen final con objective_function (pedimos la imagen)
    final_score, final_img = objective_function(best, image_folder=image_folder, prefix=prefix, save_path=img_path)

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
    parser.add_argument('--time_limit', type=int, default=1800, help='Time limit in seconds')
    args = parser.parse_args()

    local_search(args.image_folder, args.prefix, args.out_dir, time_limit=args.time_limit)


if __name__ == '__main__':
    main()
