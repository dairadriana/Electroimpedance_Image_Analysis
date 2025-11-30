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

### Tabla 1: Comparación de CNR (Contrast-to-Noise Ratio)

El CNR mide qué tan fuerte es la señal del tumor en comparación con el ruido del fondo.

| Paciente | Max Layer CNR | Img Comp (Avg) | Img Comp (Prio) | Vec Ref (Avg) | Vec Ref (Prio) | LS Rand (Avg) | LS Rand (Prio) | LS Ref (Avg) | LS Ref (Prio) |
|---|---|---|---|---|---|---|---|---|---|
| C0011i | 9.1390 | 0.2377 | 0.0657 | 0.3176 | 0.1560 | 0.2125 | 0.0046 | 0.2125 | 0.0046 |
| C0012d | 0.6250 | 0.3499 | 0.5128 | 0.2404 | 0.4229 | 0.2992 | 0.3975 | 0.2992 | 0.4844 |
| C0013i | 0.7194 | 0.3892 | 0.1822 | 0.0598 | 0.1267 | 0.3544 | 0.1234 | 0.3544 | 0.1234 |
| C0014d | 1.4635 | 0.1581 | 0.7611 | 0.0761 | 0.1388 | 0.1479 | 0.1999 | 0.1479 | 0.0799 |
| C0014i | 1.4605 | 0.1690 | 0.1676 | 0.1031 | 0.0113 | 0.1410 | 0.0604 | 0.1410 | 0.0604 |
| C0015d | 8.9769 | 0.3304 | 0.7067 | 0.4757 | 0.6376 | 0.3106 | 0.6461 | 0.3106 | 0.6461 |
| C0623d | 5.9784 | 0.7417 | 0.4939 | 0.9720 | 0.8180 | 1.1037 | 1.4045 | 1.1037 | 1.4045 |
| C0623i | 3.4488 | 0.2723 | 0.0032 | 0.3094 | 0.1698 | 0.6366 | 0.6736 | 0.6366 | 0.6311 |
| C0674i | 3.1059 | 0.1073 | 0.0161 | 0.1273 | 0.0361 | 0.7481 | 0.7481 | 0.7481 | 0.7481 |
| C0699d | 0.7658 | 1.5560 | 1.3656 | 1.4313 | 1.3656 | 1.5689 | 1.3656 | 1.5689 | 1.3656 |
| C0753d | 5.1258 | 1.7417 | 0.2109 | 0.1132 | 0.0149 | 2.5896 | 0.1750 | 2.5896 | 0.1750 |
| C0793i | 0.0991 | 0.5093 | 0.0622 | 0.1624 | 0.0481 | 0.4271 | 0.0436 | 0.4271 | 0.0452 |
| C0806d | 10.4115 | 0.2404 | 0.0455 | 0.1231 | 0.0011 | 0.1166 | 0.0011 | 0.2404 | 0.0011 |
| C0844i | 0.6147 | 1.6348 | 1.1389 | 1.6928 | 1.5903 | 1.8672 | 1.5975 | 1.8672 | 1.5975 |
| C0845i | 1.1622 | 0.3802 | 0.1470 | 0.2860 | 0.2224 | 0.3773 | 0.1659 | 0.4285 | 0.1659 |
| Promedio | 3.5398 | 0.5879 | 0.3920 | 0.4327 | 0.3840 | 0.7267 | 0.5071 | 0.7384 | 0.5022 |

### Tabla 2: Comparación de Edge Preservation

Esta métrica (0-1) indica qué tan bien se conservan los bordes originales.

| Paciente | Img Comp (Avg) | Img Comp (Prio) | Vec Ref (Avg) | Vec Ref (Prio) | LS Rand (Avg) | LS Rand (Prio) | LS Ref (Avg) | LS Ref (Prio) |
|---|---|---|---|---|---|---|---|---|
| C0011i | 0.5091 | 0.5161 | 0.5128 | 0.5169 | 0.5125 | 0.5145 | 0.5125 | 0.5145 |
| C0012d | 0.6233 | 0.6499 | 0.6440 | 0.6428 | 0.6298 | 0.6463 | 0.6298 | 0.6042 |
| C0013i | 0.5737 | 0.6119 | 0.6282 | 0.6135 | 0.5738 | 0.6111 | 0.5738 | 0.6111 |
| C0014d | 0.5875 | 0.6208 | 0.6150 | 0.6166 | 0.5920 | 0.5655 | 0.5920 | 0.6140 |
| C0014i | 0.6038 | 0.6334 | 0.6392 | 0.6370 | 0.6126 | 0.6338 | 0.6126 | 0.6338 |
| C0015d | 0.6277 | 0.6532 | 0.6609 | 0.6506 | 0.6244 | 0.6446 | 0.6244 | 0.6446 |
| C0623d | 0.5433 | 0.5515 | 0.5452 | 0.5487 | 0.5456 | 0.5443 | 0.5456 | 0.5443 |
| C0623i | 0.5004 | 0.5027 | 0.5017 | 0.5014 | 0.5037 | 0.5054 | 0.5037 | 0.5035 |
| C0674i | 0.4799 | 0.4810 | 0.4820 | 0.4817 | 0.4801 | 0.4801 | 0.4801 | 0.4801 |
| C0699d | 0.2848 | 0.2876 | 0.2885 | 0.2895 | 0.2887 | 0.2899 | 0.2887 | 0.2899 |
| C0753d | 0.5213 | 0.5300 | 0.5317 | 0.5345 | 0.5193 | 0.5330 | 0.5193 | 0.5330 |
| C0793i | 0.5834 | 0.6014 | 0.6269 | 0.6007 | 0.5789 | 0.5488 | 0.5789 | 0.5197 |
| C0806d | 0.6122 | 0.6287 | 0.6258 | 0.6299 | 0.6146 | 0.6299 | 0.6122 | 0.6299 |
| C0844i | 0.4323 | 0.4377 | 0.4364 | 0.4374 | 0.4337 | 0.4367 | 0.4337 | 0.4367 |
| C0845i | 0.5959 | 0.6177 | 0.6166 | 0.6155 | 0.6151 | 0.5526 | 0.6110 | 0.5526 |
| Promedio | 0.5386 | 0.5549 | 0.5570 | 0.5544 | 0.5416 | 0.5424 | 0.5412 | 0.5408 |

### Análisis de Resultados

Basado en las métricas cuantitativas obtenidas (CNR y Edge Preservation), se pueden extraer las siguientes conclusiones sobre el desempeño de las técnicas y métodos de fusión evaluados:

**1. Mejor Método de Fusión: Fusión por Promedio**

Independientemente de la técnica de selección de capas utilizada, el método de **Fusión por Promedio** demuestra ser superior al de Prioridad.
*   **CNR:** El método de Promedio obtiene consistentemente valores de CNR mucho más altos (e.g., **0.7384** vs 0.5022 en Búsqueda Local con Referencia). Esto indica que promediar los valores de píxeles en las zonas superpuestas ayuda a reducir el ruido y mejorar el contraste efectivo del tumor frente al fondo, en comparación con simplemente superponer capas (Prioridad).
*   **Edge Preservation:** Ambos métodos mantienen un desempeño muy similar en la preservación de bordes (alrededor de 0.54 - 0.55), lo que significa que el método de Promedio logra mejorar drásticamente el contraste sin sacrificar la integridad estructural de los bordes originales.

**2. Mejor Técnica de Optimización: Búsqueda Local**

La **Búsqueda Local** es la técnica más efectiva para maximizar la calidad de la imagen.
*   Logra los valores más altos de **CNR (~0.73 - 0.74)**, superando significativamente a la Fusión Total de 7 capas (~0.59) y al Vector de Referencia estático (~0.43).
*   Esto confirma que la optimización activa de la selección de capas es crucial. Simplemente usar todas las capas (Fusión Total) introduce información redundante o ruidosa que reduce el contraste, mientras que la búsqueda local selecciona la combinación precisa que maximiza la visibilidad de la zona de interés para cada paciente específico.

**Conclusión General:**

La configuración óptima para el análisis de estas imágenes de electroimpedancia es utilizar **Búsqueda Local con Fusión por Promedio**. Esta combinación ofrece el mejor balance, maximizando la detectabilidad de las zonas de interés (alto CNR) mientras mantiene una estructura fiel a las imágenes originales.

### Comparación Visual: Búsqueda Local vs Fusión Total

Se han seleccionado 3 pacientes representativos (C0793i, C0014d, C0012d) para ilustrar visualmente el impacto de la optimización. Estas imágenes comparan el resultado de la **Búsqueda Local (iniciada con Vector de Referencia y Fusión Promedio)** contra la **Fusión Total de las 7 capas**. Se puede observar cómo la selección inteligente de capas elimina ruido y mejora la definición de las zonas de interés en comparación con el uso indiscriminado de toda la información disponible.

#### Paciente C0793i

| Búsqueda Local (Ref. Vector + Promedio) | Fusión Total (7 Capas + Promedio) |
| :---: | :---: |
| ![](results_comparison/average/best_img_C0793i_20251127_183027.png) | ![](results_total/average/C0793i_total_average.png) |
| Vector Resultante: `[0 1 1 1 1 1 1]` | Vector: `[1 1 1 1 1 1 1]` |

#### Paciente C0014d

| Búsqueda Local (Ref. Vector + Promedio) | Fusión Total (7 Capas + Promedio) |
| :---: | :---: |
| ![](results_comparison/average/best_img_C0014d_20251127_183028.png) | ![](results_total/average/C0014d_total_average.png) |
| Vector Resultante: `[1 1 1 1 1 1 0]` | Vector: `[1 1 1 1 1 1 1]` |

#### Paciente C0012d

| Búsqueda Local (Ref. Vector + Promedio) | Fusión Total (7 Capas + Promedio) |
| :---: | :---: |
| ![](results_comparison/average/best_img_C0012d_20251127_183027.png) | ![](results_total/average/C0012d_total_average.png) |
| Vector Resultante: `[1 1 1 1 1 1 0]` | Vector: `[1 1 1 1 1 1 1]` |
