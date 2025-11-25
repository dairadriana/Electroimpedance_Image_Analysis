#!/usr/bin/env python3
"""
utils_matlab_io.py

Funciones utilitarias para compatibilidad con MATLAB:
 - save_chromosome_mat(chromosome, path): guarda el cromosoma en un .mat
 - load_chromosome_mat(path): carga un cromosoma desde .mat

Se usa `scipy.io.savemat` para generar archivos que MATLAB puede leer con `load()`.
"""

import numpy as np
from scipy.io import savemat, loadmat
from typing import Any


def save_chromosome_mat(chromosome: np.ndarray, path: str) -> None:
    """Guardar cromosoma como variable 'chromosome' en un .mat"""
    chromosome = np.asarray(chromosome).astype(np.uint8).reshape((1, -1))
    savemat(path, {'chromosome': chromosome})


def load_chromosome_mat(path: str) -> Any:
    """Cargar archivo .mat y retornar la variable 'chromosome' si existe"""
    data = loadmat(path)
    if 'chromosome' in data:
        arr = np.asarray(data['chromosome']).astype(int).flatten()
        return arr
    # intentar otras claves
    for k in ['chrom', 'cromosoma', 'x']:
        if k in data:
            return np.asarray(data[k]).astype(int).flatten()
    raise KeyError('Variable "chromosome" no encontrada en el .mat')


if __name__ == '__main__':
    # Test rápido
    import numpy as np
    arr = np.array([1,0,1,1,0,0,0], dtype=int)
    save_chromosome_mat(arr, 'test_chrom.mat')
    print('Guardado test_chrom.mat')
    loaded = load_chromosome_mat('test_chrom.mat')
    print('Cargado:', loaded)
