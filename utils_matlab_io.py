#!/usr/bin/env python3
"""
Utility functions for MATLAB compatibility:
 - save_chromosome_mat(chromosome, path): saves the chromosome to a .mat file
 - load_chromosome_mat(path): loads a chromosome from a .mat file

Uses `scipy.io.savemat` to generate files that MATLAB can read with `load()`.
"""

import numpy as np
from scipy.io import savemat, loadmat
from typing import Any


def save_chromosome_mat(chromosome: np.ndarray, path: str) -> None:
    # Save chromosome as variable 'chromosome' in a .mat file
    chromosome = np.asarray(chromosome).astype(np.uint8).reshape((1, -1))
    savemat(path, {'chromosome': chromosome})


def load_chromosome_mat(path: str) -> Any:
    # Load .mat file and return the variable 'chromosome' if it exists
    data = loadmat(path)
    if 'chromosome' in data:
        arr = np.asarray(data['chromosome']).astype(int).flatten()
        return arr
    # try other keys
    for k in ['chrom', 'cromosoma', 'x']:
        if k in data:
            return np.asarray(data[k]).astype(int).flatten()
    raise KeyError('Variable "chromosome" no encontrada en el .mat')


if __name__ == '__main__':
    import numpy as np
    arr = np.array([1,0,1,1,0,0,0], dtype=int)
    save_chromosome_mat(arr, 'test_chrom.mat')
    print('Guardado test_chrom.mat')
    loaded = load_chromosome_mat('test_chrom.mat')
    print('Cargado:', loaded)
