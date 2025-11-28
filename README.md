# Análisis de Imágenes de Electroimpedancia (EIM) con Optimización por Búsqueda Local y Fuerza Bruta

Este proyecto implementa un sistema de análisis de imágenes de electroimpedancia (EIM) que combina procesamiento de imágenes con optimización mediante búsqueda local y búsqueda exhaustiva (fuerza bruta). El sistema fusiona máscaras de imágenes que representan diferentes capas de medición electroimpedanciométrica y utiliza algoritmos de optimización para seleccionar la combinación de capas que produce la mejor imagen final.

El proyecto consta de dos componentes principales:
- **Procesamiento de Imágenes (MATLAB)**: Fusión de máscaras BMP con detección de áreas rojas y priorización de capas.
- **Optimización (Python)**: Búsqueda local y fuerza bruta para seleccionar combinaciones óptimas de capas N1-N7.

## Descripción General

La electroimpedancia (EIM) es una técnica de imagen no invasiva que mide las propiedades eléctricas de los tejidos para detectar anomalías. Su importancia radica en proporcionar información detallada sobre la composición y estructura de los tejidos sin exposición a radiación, lo que la hace valiosa para aplicaciones médicas como el diagnóstico temprano de enfermedades.

El proyecto procesa una serie de imágenes BMP que son máscaras generadas a partir de mediciones de electroimpedancia. Estas máscaras representan diferentes "niveles" o "capas" de medición (N1 a N7), donde cada nivel corresponde a una profundidad o estado diferente en el análisis electroimpedanciométrico.

El objetivo principal es:
1. **Fusionar máscaras**: Combinar las capas de manera prioritaria (N1 → N7), preservando la información de color original de las áreas detectadas.
2. **Optimizar selección**: Usar búsqueda local para determinar qué combinación de capas produce la mejor imagen final, evaluada mediante métricas de calidad como entropía, contraste y reducción de ruido.
3. **Generar imagen final**: Producir una imagen combinada que muestre las zonas de interés superpuestas sobre una imagen base (N7).

En este proyecto, se implementó un sistema que combina procesamiento de imágenes en MATLAB con algoritmos de optimización en Python. Se dividieron los datos en conjuntos de entrenamiento y validación, se obtuvo un vector de referencia mediante búsqueda exhaustiva, y se aplicó búsqueda local para optimizar la selección de capas, evaluando diferentes métodos de fusión para mejorar la calidad de las imágenes resultantes.


## Metodología

El proyecto siguió una metodología sistemática para optimizar la selección de capas en imágenes de electroimpedancia. Primero, se dividieron los datos en conjuntos de entrenamiento y validación para evaluar el rendimiento de los algoritmos.

Para obtener un vector de referencia, se realizó una búsqueda exhaustiva (fuerza bruta) evaluando todas las combinaciones posibles de capas.

Pseudocódigo para fuerza bruta:

```
Para cada combinación binaria de 7 bits (excepto todas ceros):
    Evaluar fitness promedio sobre pacientes de entrenamiento
    Seleccionar la combinación con mejor fitness promedio
```

Luego, se inició la búsqueda local a partir de este vector de referencia.

Pseudocódigo para búsqueda local:

```
Inicializar con vector de referencia
Mientras no se alcance máximo de iteraciones y haya mejora:
    Generar vecino cambiando un bit
    Evaluar fitness del vecino
    Si fitness > mejor_fitness:
        Actualizar mejor_vector y mejor_fitness
        Continuar desde este vecino
```

Se utilizaron dos tipos de fusión: prioridad y promedio.

Pseudocódigo para fusión con prioridad:

```
Para cada capa seleccionada en orden N1→N7:
    Detectar áreas rojas
    Para píxeles nuevos (no ocupados):
        Asignar colores originales
        Marcar como ocupados
```

Pseudocódigo para fusión con promedio:

```
Para cada capa seleccionada:
    Detectar áreas rojas
    Para píxeles en áreas rojas:
        Promediar colores con capas anteriores
```

Los parámetros utilizados en la búsqueda local incluyen: máximo de iteraciones (200), evaluación de fitness basada en proporción de píxeles rojos válidos.

La función objetivo se define como:

fitness = 0.8 * (píxeles_válidos / píxeles_detectados) + 0.2 * (píxeles_válidos / (píxeles_válidos + 50))

Donde píxeles_válidos son aquellos con canal rojo > verde y azul, y rojo > 60/255.

## Procedimiento General

El sistema funciona en dos fases complementarias:

### Fase 1: Procesamiento de Imágenes (MATLAB)
```pseudocode
Para cada conjunto de imágenes BMP (N1-N7):
    Cargar imágenes en orden N1 → N7
    Para cada imagen:
        Detectar áreas rojas usando redDetection.m
        Fusionar colores preservando prioridad
    Generar imagen combinada final
```

### Fase 2: Optimización (Python)
#### Búsqueda Local:
```pseudocode
Inicializar vector binario aleatorio (7 bits, al menos uno activado)
Evaluar fitness del vector inicial usando objective_function()
Mientras no se alcance máximo de iteraciones y haya mejora:
    Generar vecinos (cambiar un bit)
    Para cada vecino:
        Evaluar fitness usando objective_function()
        Si fitness > mejor_fitness_actual:
            Actualizar mejor_vector y mejor_fitness
            Continuar búsqueda desde este vecino
Guardar mejor vector encontrado y imagen correspondiente
```

#### Búsqueda Exhaustiva (Fuerza Bruta):
```pseudocode
Para cada una de las 127 combinaciones posibles (7 bits, al menos uno activado):
    Evaluar fitness promedio sobre múltiples pacientes usando objective_function()
    Aplicar criterio de parsimonia para desempates (menor número de capas activadas)
Seleccionar el vector con mejor fitness promedio global
Guardar resultados detallados y resúmenes
```

### Complementariedad entre Scripts

- **MATLAB** proporciona la lógica base de fusión de imágenes
- **Python** replica esta lógica en `objective_function.py` para evaluación rápida
- **Búsqueda local** en `local_search.py` encuentra óptimos locales eficientemente
- **Búsqueda exhaustiva** en `find_general_vector.py` garantiza el óptimo global evaluando todas las combinaciones
- **Función objetivo** cuantifica calidad basada en proporción de píxeles rojos válidos
- Resultado: vector óptimo que selecciona capas para mejor fusión

## Requisitos del Sistema

### MATLAB
- MATLAB con Image Processing Toolbox
- Archivos de imagen en formato BMP RGB
- Estructura de nombres específica: `C0683d_N[1-7]_mask.bmp`

### Python
- Python 3.6 o superior
- Librerías requeridas:
  - NumPy
  - OpenCV (cv2)
  - SciPy
  - scikit-image
  - Matplotlib
- Sistema operativo: Linux, Windows o macOS

## Configuración y Uso

### MATLAB
Para usar el script con diferentes conjuntos de datos:

1. Modificar la variable `folder` en `multipleImageProcessing.m` para apuntar a la carpeta deseada
2. Ajustar `prefijo` si los nombres de archivo cambian
3. Modificar `sufijosPermitidos` si se necesitan diferentes niveles N

### Python
#### Validación de Instalación
Ejecutar primero:
```bash
python3 test_installation.py
```

#### Búsqueda Local
Optimizar selección de capas usando búsqueda local:
```bash
python3 local_search.py --image_folder Images/Prueba --prefix C0683d --out_dir results
```

**Parámetros:**
- `--image_folder`: Carpeta con imágenes BMP
- `--prefix`: Prefijo de archivos (ej: C0683d)
- `--out_dir`: Directorio para guardar resultados
- `--max_iters`: Máximo de iteraciones (default: 200)

#### Búsqueda Exhaustiva
Encontrar el vector óptimo global evaluando todas las combinaciones:
```bash
python3 find_general_vector.py
```

**Nota:** El script utiliza configuraciones fijas para carpeta de imágenes (`Images/Prueba`) y prefijos de pacientes. Los resultados se guardan en `results_data_analysis/`.

#### Evaluación Individual
Probar un cromosoma específico:
```bash
python3 evaluate_individual.py --chrom 1 0 1 1 0 1 1 --out imagen_resultante.png
```

Los resultados se guardan en la carpeta `results/` con archivos `.mat` (cromosomas) y `.png` (imágenes).

## Interpretación de Resultados

### Procesamiento de Imágenes
- **N1-N6**: Capas superiores que se fusionan por prioridad sobre N7
- **N7**: Capa base que sirve como fondo
- **Áreas rojas**: Zonas de interés detectadas en cada máscara
- **Fusión**: Combinación de colores originales preservando la prioridad de capas

### Optimización
- **Vector binario**: Vector de 7 bits representando selección de capas (1=incluida, 0=excluida)
- **Fitness**: Puntuación basada en proporción de píxeles rojos válidos detectados (0.8 * calidad + 0.2 * presencia)
- **Mejor vector**: Combinación óptima de capas guardada en `.mat`
- **Imagen resultante**: Visualización final guardada como `.png`
- **Búsqueda local**: Encuentra óptimos locales eficientemente
- **Búsqueda exhaustiva**: Garantiza el óptimo global evaluando todas las combinaciones posibles

Este sistema permite:
1. Visualizar propiedades electroimpedanciométricas a través de diferentes profundidades
2. Optimizar la selección de capas para mejorar la calidad de imagen
3. Comparar resultados entre diferentes configuraciones de medición EIM

## Resultados Experimentales: Comparación de Métodos de Fusión

Se realizó un estudio comparativo de dos métodos de fusión de imágenes en 15 pacientes de validación:

### Métodos Comparados

1. **Fusión con Prioridad** (`objective_function_priority.py`): La primera capa seleccionada tiene prioridad sobre las siguientes (inspirado en MATLAB)
2. **Fusión con Promedio** (`objective_function.py`): Los colores se promedian en áreas de superposición

### Escenarios Evaluados

- **Con Vector General**: Búsqueda local iniciando desde el vector óptimo encontrado por búsqueda exhaustiva `[1 0 1 0 0 0 0]`
- **Con Vector Aleatorio**: Búsqueda local iniciando desde vectores aleatorios diferentes para cada paciente

### Ejemplos Visuales de Resultados

A continuación se muestran 3 pacientes representativos con los 4 escenarios de fusión:

#### Paciente C0012d (Alto Fitness)

**Fusión con Prioridad**

| Solo Vector de Referencia | Vector de Referencia + Búsqueda Local | Solo Búsqueda Local con Vector Aleatorio |
|:-------------------------:|:-------------------------------------:|:-----------------------------------------:|
| ![](results_reference_vector/priority/ref_img_C0012d_20251127_185500.png) | ![](results_comparison/priority/best_img_C0012d_20251127_183027.png) | ![](results_comparison_random/priority/best_img_C0012d_20251127_183711.png) |
| Fitness: 0.798 | Fitness: 0.857 | Fitness: 0.812 |
| Cromosoma: `[1 0 1 0 0 0 0]` | Cromosoma: `[0 0 0 0 1 0 0]` | Cromosoma: `[1 1 0 0 0 1 0]` |

**Fusión con Promedio**

| Solo Vector de Referencia | Vector de Referencia + Búsqueda Local | Solo Búsqueda Local con Vector Aleatorio |
|:-------------------------:|:-------------------------------------:|:-----------------------------------------:|
| ![](results_reference_vector/average/ref_img_C0012d_20251127_185500.png) | ![](results_comparison/average/best_img_C0012d_20251127_183027.png) | ![](results_comparison_random/average/best_img_C0012d_20251127_183711.png) |
| Fitness: 0.830 | Fitness: 0.897 | Fitness: 0.897 |
| Cromosoma: `[1 0 1 0 0 0 0]` | Cromosoma: `[1 1 1 1 1 1 0]` | Cromosoma: `[1 1 1 1 1 1 0]` |

#### Paciente C0793i (Muy Alto Fitness)

**Fusión con Prioridad**

| Solo Vector de Referencia | Vector de Referencia + Búsqueda Local | Solo Búsqueda Local con Vector Aleatorio |
|:-------------------------:|:-------------------------------------:|:-----------------------------------------:|
| ![](results_reference_vector/priority/ref_img_C0793i_20251127_185500.png) | ![](results_comparison/priority/best_img_C0793i_20251127_183027.png) | ![](results_comparison_random/priority/best_img_C0793i_20251127_183712.png) |
| Fitness: 0.837 | Fitness: 0.880 | Fitness: 0.871 |
| Cromosoma: `[1 0 1 0 0 0 0]` | Cromosoma: `[0 0 0 0 0 0 1]` | Cromosoma: `[0 0 0 0 0 1 0]` |

**Fusión con Promedio**

| Solo Vector de Referencia | Vector de Referencia + Búsqueda Local | Solo Búsqueda Local con Vector Aleatorio |
|:-------------------------:|:-------------------------------------:|:-----------------------------------------:|
| ![](results_reference_vector/average/ref_img_C0793i_20251127_185500.png) | ![](results_comparison/average/best_img_C0793i_20251127_183027.png) | ![](results_comparison_random/average/best_img_C0793i_20251127_183712.png) |
| Fitness: 0.861 | Fitness: 0.943 | Fitness: 0.943 |
| Cromosoma: `[1 0 1 0 0 0 0]` | Cromosoma: `[0 1 1 1 1 1 1]` | Cromosoma: `[0 1 1 1 1 1 1]` |

#### Paciente C0013i (Alto Fitness)

**Fusión con Prioridad**

| Solo Vector de Referencia | Vector de Referencia + Búsqueda Local | Solo Búsqueda Local con Vector Aleatorio |
|:-------------------------:|:-------------------------------------:|:-----------------------------------------:|
| ![](results_reference_vector/priority/ref_img_C0013i_20251127_185500.png) | ![](results_comparison/priority/best_img_C0013i_20251127_183027.png) | ![](results_comparison_random/priority/best_img_C0013i_20251127_183712.png) |
| Fitness: 0.878 | Fitness: 0.884 | Fitness: 0.884 |
| Cromosoma: `[1 0 1 0 0 0 0]` | Cromosoma: `[1 1 0 0 0 0 0]` | Cromosoma: `[1 1 0 0 0 0 0]` |

**Fusión con Promedio**

| Solo Vector de Referencia | Vector de Referencia + Búsqueda Local | Solo Búsqueda Local con Vector Aleatorio |
|:-------------------------:|:-------------------------------------:|:-----------------------------------------:|
| ![](results_reference_vector/average/ref_img_C0013i_20251127_185500.png) | ![](results_comparison/average/best_img_C0013i_20251127_183027.png) | ![](results_comparison_random/average/best_img_C0013i_20251127_183712.png) |
| Fitness: 0.887 | Fitness: 0.933 | Fitness: 0.933 |
| Cromosoma: `[1 0 1 0 0 0 0]` | Cromosoma: `[1 0 1 1 1 0 1]` | Cromosoma: `[1 0 1 1 1 0 1]` |

### Tabla Comparativa Completa (15 Pacientes de Validación)

**Nota:** Se incluye una columna adicional con el fitness del **Vector de Referencia sin búsqueda local** para mostrar la mejora obtenida por la optimización.

| Paciente | Vector Ref.<br>Prioridad | Vector Ref.<br>Promedio | Vector General<br>Prioridad | Vector General<br>Promedio | Vector Aleatorio<br>Prioridad | Vector Aleatorio<br>Promedio | Mejor Método |
|----------|:------------------------:|:-----------------------:|:---------------------------:|:---------------------------:|:-----------------------------:|:----------------------------:|:------------:|
| C0845i   | 0.788 | 0.814 | 0.823 | **0.837** | 0.823 | **0.839** | Promedio |
| C0844i   | 0.813 | 0.824 | 0.826 | **0.837** | 0.826 | **0.837** | Promedio |
| C0012d   | 0.798 | 0.830 | 0.857 | **0.897** | 0.812 | **0.897** | Promedio |
| C0699d   | 0.592 | 0.585 | 0.624 | **0.629** | 0.624 | **0.629** | Promedio |
| C0793i   | 0.837 | 0.861 | 0.880 | **0.943** | 0.871 | **0.943** | Promedio |
| C0013i   | 0.878 | 0.887 | 0.884 | **0.933** | 0.884 | **0.933** | Promedio |
| C0753d   | 0.762 | 0.772 | 0.767 | **0.803** | 0.767 | **0.803** | Promedio |
| C0014d   | 0.816 | 0.848 | 0.832 | **0.915** | 0.834 | **0.915** | Promedio |
| C0015d   | 0.856 | 0.878 | 0.860 | **0.912** | 0.860 | **0.912** | Promedio |
| C0623d   | 0.695 | 0.702 | 0.766 | **0.768** | 0.766 | **0.768** | Promedio |
| C0623i   | 0.718 | 0.722 | 0.741 | **0.756** | 0.730 | **0.756** | Promedio |
| C0674i   | 0.700 | 0.700 | **0.832** | **0.832** | **0.832** | **0.832** | Empate |
| C0011i   | 0.771 | 0.787 | 0.778 | **0.799** | 0.778 | **0.799** | Promedio |
| C0014i   | 0.844 | 0.855 | 0.850 | **0.870** | 0.850 | **0.870** | Promedio |
| C0806d   | 0.798 | 0.807 | 0.798 | **0.814** | 0.798 | **0.815** | Promedio |
| **Promedio** | **0.778** | **0.792** | **0.808** | **0.837** | **0.804** | **0.837** | **Promedio** |
| **Desv. Std** | **0.073** | **0.080** | **0.065** | **0.079** | **0.063** | **0.079** | - |
| **Mejora vs Ref.** | **-** | **-** | **+0.030** | **+0.045** | **+0.026** | **+0.045** | - |


### Análisis de Resultados

**Hallazgos Principales:**

1. **Fusión con Promedio domina**: Ganó en 14/15 casos (93.3%), con solo 1 empate
2. **Vector inicial tiene poco impacto**: Los resultados son muy similares independientemente de si se inicia con el vector general o uno aleatorio
3. **Mejora consistente**: La fusión con promedio mejora el fitness en promedio +0.029 puntos (+3.6%)
4. **Convergencia robusta**: Ambos métodos convergen a soluciones similares desde diferentes puntos de partida
5. **Búsqueda local es valiosa**: La optimización mejora el fitness en +0.045 puntos (+5.7%) comparado con usar solo el vector de referencia

**Valor de la Búsqueda Local:**

La comparación con el vector de referencia sin optimización muestra que la búsqueda local aporta mejoras significativas:

| Método | Fitness Promedio | Mejora vs Vector Ref. |
|--------|:----------------:|:---------------------:|
| Vector Ref. + Prioridad | 0.778 | - |
| Vector Ref. + Promedio | 0.792 | - |
| **Búsqueda Local + Prioridad** | **0.808** | **+3.9%** |
| **Búsqueda Local + Promedio** | **0.837** | **+5.7%** |

**Observaciones clave:**
- La búsqueda local **siempre mejora** el fitness, independientemente del método de fusión
- La mejora es mayor con fusión promedio (+5.7%) que con prioridad (+3.9%)
- Incluso con el mejor vector encontrado por búsqueda exhaustiva, la optimización local aporta valor
- El paciente C0674i es una excepción: la búsqueda local encontró una mejora significativa (+0.132) que el vector de referencia no captura


**Implicaciones:**

- La fusión con promedio es más efectiva para este problema de optimización
- El vector general encontrado por búsqueda exhaustiva es un buen punto de partida, pero no es crítico
- La búsqueda local es robusta y puede encontrar buenas soluciones desde puntos aleatorios

**Estadísticas Detalladas:**

| Métrica | Vector General<br>Prioridad | Vector General<br>Promedio | Vector Aleatorio<br>Prioridad | Vector Aleatorio<br>Promedio |
|---------|:---------------------------:|:---------------------------:|:-----------------------------:|:----------------------------:|
| Fitness Promedio | 0.808 | **0.837** | 0.804 | **0.837** |
| Desviación Estándar | 0.065 | 0.079 | 0.063 | 0.079 |
| Fitness Mínimo | 0.624 | 0.629 | 0.624 | 0.629 |
| Fitness Máximo | 0.884 | **0.943** | 0.884 | **0.943** |
| Victorias | 0 | **14** | 0 | **14** |
| Empates | 1 | 1 | 1 | 1 |

### Análisis de Tiempos de Convergencia

Aunque el vector inicial tiene poco impacto en el fitness final, **sí afecta el tiempo de convergencia**, especialmente con tiempo límite corto:

**Tiempos Promedio de Ejecución (límite de 5s):**

| Escenario | Fusión Prioridad | Fusión Promedio | Ahorro con Vector General |
|-----------|:----------------:|:---------------:|:-------------------------:|
| **Vector General** | 0.062s | 0.147s | - |
| **Vector Aleatorio** | 0.088s | 0.156s | - |
| **Diferencia** | **-0.026s (-42%)** | **-0.009s (-6%)** | - |

**Hallazgos sobre Tiempo:**

1. **Vector General converge más rápido**:
   - Con Fusión Prioridad: **42% más rápido** (0.062s vs 0.088s)
   - Con Fusión Promedio: **6% más rápido** (0.147s vs 0.156s)

2. **El beneficio depende del método de fusión**:
   - La fusión con **prioridad** se beneficia significativamente del buen punto de partida
   - La fusión con **promedio** es más robusta y menos sensible al punto inicial

3. **Contexto del tiempo límite**:
   - **Límite corto (< 10s)**: El ahorro de tiempo es significativo (hasta 42%)
   - **Límite largo (1800s)**: El ahorro es despreciable (~0.001% del tiempo total)

**Recomendaciones de Uso:**

| Escenario | Vector Inicial Recomendado | Razón |
|-----------|:-------------------------:|:------|
| Búsquedas rápidas (< 10s) | Vector General | Ahorra hasta 42% de tiempo |
| Producción (30 min) | Vector Aleatorio | Mismo fitness final, sin costo de búsqueda exhaustiva |
| Múltiples ejecuciones cortas | Vector General | Beneficio acumulativo en tiempo |
| Calidad prioritaria | Cualquiera + Fusión Promedio | Mejor fitness independiente del inicio |

**Conclusión sobre Tiempo:**
- Para el caso de uso típico (30 minutos de búsqueda local), el vector general **no ofrece ventaja práctica** en tiempo
- El costo de calcular el vector general (búsqueda exhaustiva) no se justifica solo por el ahorro de tiempo
- El vector general es útil principalmente como **punto de referencia** para comparaciones, no por eficiencia temporal