#!/usr/bin/env python3
"""
test_installation.py - Validar que todo esté instalado correctamente

Ejecuta este script para verificar que todas las dependencias están OK
"""

import sys
import subprocess
from pathlib import Path

def test_python_version():
    """Verificar versión de Python."""
    print("\n✓ Verificando Python...")
    try:
        if sys.version_info.major < 3 or sys.version_info.minor < 6:
            print(f"  ❌ Python {sys.version_info.major}.{sys.version_info.minor} (se requiere 3.6+)")
            return False
        print(f"  ✓ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        return True
    except:
        print("  ❌ Error verificando Python")
        return False


def test_imports():
    """Verificar que todas las librerías se pueden importar."""
    print("\n✓ Verificando librerías...")
    
    libraries = {
        'numpy': 'NumPy',
        'cv2': 'OpenCV',
        'scipy.stats': 'SciPy',
        'skimage.measure': 'scikit-image',
        'matplotlib.pyplot': 'Matplotlib'
    }
    
    all_ok = True
    for lib, name in libraries.items():
        try:
            parts = lib.split('.')
            mod = __import__(lib)
            for part in parts[1:]:
                mod = getattr(mod, part)
            print(f"  ✓ {name}")
        except ImportError:
            print(f"  ❌ {name} (no instalado)")
            all_ok = False
        except Exception as e:
            print(f"  ❌ {name} (error: {e})")
            all_ok = False
    
    return all_ok


def test_files():
    """Verificar que archivos necesarios existen."""
    print("\n✓ Verificando archivos...")
    
    files = [
        'config.py',
        'algoritmo_evolutivo_v2.py',
        'utils_ga.py',
        'ALGORITMO_EVOLUTIVO_README.md',
        'ESPECIFICACION_TECNICA.md',
    ]
    
    all_ok = True
    for filename in files:
        if Path(filename).exists():
            print(f"  ✓ {filename}")
        else:
            print(f"  ❌ {filename} (no encontrado)")
            all_ok = False
    
    return all_ok


def test_images():
    """Verificar que las imágenes existen."""
    print("\n✓ Verificando imágenes...")
    
    image_folder = Path('Images/Prueba')
    if not image_folder.exists():
        print(f"  ❌ Carpeta {image_folder} no encontrada")
        return False
    
    all_ok = True
    for i in range(1, 8):
        img_path = image_folder / f'C0683d_N{i}_mask.bmp'
        if img_path.exists():
            print(f"  ✓ C0683d_N{i}_mask.bmp")
        else:
            print(f"  ❌ C0683d_N{i}_mask.bmp (no encontrado)")
            all_ok = False
    
    return all_ok


def test_config():
    """Verificar que config.py es válido."""
    print("\n✓ Verificando configuración...")
    
    try:
        import config
        config.validar_configuracion()
        print(f"  ✓ config.py válido")
        print(f"    - POPULATION_SIZE: {config.POPULATION_SIZE}")
        print(f"    - GENERATIONS: {config.GENERATIONS}")
        print(f"    - IMAGE_FOLDER: {config.IMAGE_FOLDER}")
        return True
    except Exception as e:
        print(f"  ❌ Error en config.py: {e}")
        return False


def test_import_modules():
    """Verificar que se pueden importar los módulos principales."""
    print("\n✓ Verificando módulos principales...")
    
    try:
        from algoritmo_evolutivo_v2 import ImageLayerGAv2
        print(f"  ✓ algoritmo_evolutivo_v2.ImageLayerGAv2")
    except Exception as e:
        print(f"  ❌ Error importando ImageLayerGAv2: {e}")
        return False
    
    try:
        from utils_ga import visualizar_cromosoma
        print(f"  ✓ utils_ga.visualizar_cromosoma")
    except Exception as e:
        print(f"  ❌ Error importando utils_ga: {e}")
        return False
    
    return True


def main():
    """Función principal."""
    print("\n" + "="*70)
    print("VALIDACIÓN DE INSTALACIÓN - Algoritmo Evolutivo EIM")
    print("="*70)
    
    tests = [
        ("Python 3.6+", test_python_version),
        ("Librerías Python", test_imports),
        ("Archivos necesarios", test_files),
        ("Imágenes de prueba", test_images),
        ("Configuración", test_config),
        ("Módulos principales", test_import_modules),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"  ❌ Error: {e}")
            results[test_name] = False
    
    # Resumen
    print("\n" + "="*70)
    print("RESUMEN")
    print("="*70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"\nPruebas pasadas: {passed}/{total}")
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "❌ FAIL"
        print(f"  {status}: {test_name}")
    
    if passed == total:
        print("\n✅ ¡INSTALACIÓN CORRECTA!")
        print("\nPuedes ejecutar:")
        print("  python3 algoritmo_evolutivo_v2.py")
        print("  o")
        print("  python3 quickstart.py")
        return 0
    else:
        print(f"\n❌ {total - passed} prueba(s) fallaron")
        print("\nAcciones recomendadas:")
        if not results.get("Librerías Python"):
            print("  1. Instalar dependencias:")
            print("     bash INSTALACION.sh")
        if not results.get("Imágenes de prueba"):
            print("  2. Verificar que existen las 7 imágenes en Images/Prueba/")
        if not results.get("Configuración"):
            print("  3. Revisar config.py")
        return 1


if __name__ == '__main__':
    sys.exit(main())
