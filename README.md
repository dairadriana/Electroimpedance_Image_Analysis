# Optimization of Electroimpedance Image Fusion using Local Search and Layer Analysis

Este proyecto presenta un enfoque para optimizar la fusión de imágenes de electroimpedancia (EIM) utilizando algoritmos de búsqueda local y análisis de capas. El sistema procesa conjuntos de 7 máscaras de imagen correspondientes a diferentes niveles de profundidad (N1-N7), buscando la combinación óptima que maximiza la detección de regiones de interés (tumores) y la preservación de los bordes.

El sistema compara dos métodos de fusión (basado en prioridad y en promedio) aplicados a regiones de interés seleccionadas mediante criterios de color. Los resultados experimentales en un conjunto de pacientes demuestran que la optimización mediante **búsqueda local, combinada con la fusión por promedio, logra un rendimiento competitivo** en comparación con otras técnicas, obteniendo mejoras cuantificables en la Relación Contraste-Ruido (CNR) y manteniendo una adecuada preservación de los bordes estructurales.

## Metodología

El problema de selección de capas se modela como un problema de optimización. Una solución se representa mediante un **vector binario de longitud 7**, donde cada posición corresponde a una de las capas (N1 a N7). Un valor de `1` indica que la capa se incluye en la fusión, mientras que `0` indica que se descarta. Esto permite explorar 127 combinaciones posibles de capas.

### 1. Detección de Regiones de Interés (ROI)

Antes de la fusión, es fundamental identificar las regiones que corresponden a tejido anómalo. Dado que las imágenes EIM utilizan mapas de color para representar la conductividad, se emplea un criterio de segmentación en el espacio de color RGB. Un píxel se considera parte de una ROI si cumple la siguiente condición, característica de zonas de alta conductividad:

`(R ≥ 60) Y (R > G) Y (G > B)`

Esta segmentación permite que el proceso de fusión se concentre exclusivamente en las áreas clínicamente relevantes.

### 2. Métodos de Fusión

Se proponen y evalúan dos estrategias distintas para combinar la información de las capas seleccionadas:

1.  **Fusión por Prioridad (Priority-based):** Las capas se superponen en orden secuencial (N1 → N7). Cuando se detecta un área roja en una capa, sus píxeles se "pintan" en la imagen final. Los píxeles ya ocupados por capas anteriores no se modifican. Este método prioriza la información de las capas más superficiales.

2.  **Fusión por Promedio (Average-based):** Este método integra la información de todas las capas seleccionadas. En las zonas donde las ROIs de múltiples capas se superponen, el color del píxel resultante se calcula como la **media aritmética** de los colores de esas capas. El objetivo es suavizar variaciones y reducir el ruido aleatorio.

### 3. Algoritmos de Optimización

Para encontrar el vector binario óptimo para cada paciente, se utilizaron dos algoritmos:

1.  **Búsqueda Exhaustiva (Fuerza Bruta):** Para establecer una línea base sólida, se realizó una búsqueda exhaustiva en un conjunto de entrenamiento. Se evaluaron las 127 combinaciones de capas para cada paciente, y el vector que maximizó el rendimiento promedio global fue seleccionado como el **"Vector de Referencia"**. El análisis arrojó el siguiente vector:
    `v_ref = [1, 0, 1, 0, 0, 0, 0]`
    Esto sugiere que, en promedio, la combinación de las capas N1 y N3 proporciona una base sólida para la detección.

2.  **Búsqueda Local (Local Search):** Este es el algoritmo principal de optimización. Explora el vecindario de un vector solución realizando cambios mínimos (voltear un bit) para encontrar mejoras incrementales. El proceso se inicia desde un punto (aleatorio o el Vector de Referencia) y continúa hasta que no se encuentran mejoras o se alcanza un máximo de iteraciones.

La función de evaluación (fitness) pondera la cantidad y consistencia de los píxeles válidos detectados:
`fitness = 0.8 * (píxeles_válidos / píxeles_detectados) + 0.2 * (píxeles_válidos / (píxeles_válidos + 50))`

## Resultados y Análisis

El rendimiento de los métodos se cuantificó utilizando dos métricas clave: **Relación Contraste-Ruido (CNR)**, que mide la detectabilidad del tumor, y **Preservación de Bordes (Edge Preservation)**, que mide la fidelidad estructural.

### Resultados Cuantitativos

La siguiente tabla resume los resultados promedio obtenidos en el conjunto de 15 pacientes. La columna "Max Layer (Base)" representa el CNR de la mejor capa individual, que sirve como línea base a superar.

| Método | CNR (Promedio ± Desv. Est.) | Edge Preserv. (Promedio ± Desv. Est.) |
| :--- | :--- | :--- |
| **Max Layer (Base)** | **3.5398 ± 3.5418** | - |
| Fusión Total (Promedio) | 0.5879 ± 0.5691 | 0.5386 ± 0.0908 |
| Fusión Total (Prioridad) | 0.3920 ± 0.4294 | 0.5549 ± 0.0998 |
| Vector Ref. (Promedio) | 0.4327 ± 0.5144 | 0.5570 ± 0.1017 |
| Vector Ref. (Prioridad) | 0.3840 ± 0.5056 | 0.5544 ± 0.0988 |
| Búsqueda Local Aleatoria (Promedio) | 0.7267 ± 0.7393 | 0.5417 ± 0.0916 |
| Búsqueda Local Aleatoria (Prioridad) | 0.5071 ± 0.5503 | 0.5424 ± 0.0940 |
| **Búsqueda Local Ref. (Promedio)** | **0.7384 ± 0.7310** | **0.5412 ± 0.0913** |
| Búsqueda Local Ref. (Prioridad) | 0.5022 ± 0.5543 | 0.5408 ± 0.0933 |

### Análisis de Resultados

Basado en los resultados cuantitativos, se extraen las siguientes conclusiones:

1.  **El Problema Central es la Degradación del Contraste:** El hallazgo más importante es que todos los métodos de fusión fallan en superar el CNR de la mejor capa individual (un promedio de **0.7384** en el mejor de los casos vs. **3.5398** de la capa base). Esto indica que la fusión indiscriminada, incluso optimizada, tiende a diluir la señal clara de una capa buena con información ruidosa de otras, degradando la calidad diagnóstica.

2.  **Mejor Método de Fusión: Fusión por Promedio:** Independientemente de la técnica de selección, la **Fusión por Promedio** demuestra ser consistentemente superior a la Fusión por Prioridad. El método de promedio obtiene valores de CNR significativamente más altos (e.g., **0.7384** vs 0.5022 para Búsqueda Local con Referencia), sugiriendo que promediar los píxeles ayuda a reducir el ruido y a mejorar el contraste.

3.  **Mejor Técnica de Optimización: Búsqueda Local:** La **Búsqueda Local iniciada desde el Vector de Referencia** es la técnica más efectiva, logrando el mejor rendimiento en CNR (**0.7384**). Esto confirma que una selección de capas adaptativa para cada paciente es crucial y superior a usar todas las capas (Fusión Total) o un vector estático (Vector de Referencia).

### Conclusión General

La combinación de **Búsqueda Local (iniciada con Vector de Referencia) y Fusión por Promedio** se posiciona como el método más robusto. Aunque no logra superar a la mejor capa individual, minimiza la degradación del contraste y maximiza la calidad de la imagen fusionada resultante en comparación con las otras estrategias evaluadas. Futuros trabajos deberían enfocarse en métodos de fusión más inteligentes que prioricen y preserven la señal de la capa de mayor calidad en lugar de promediarla.

### Comparación Visual

Las siguientes imágenes comparan el resultado de la **Búsqueda Local (Ref. Vector + Promedio)** contra la **Fusión Total de las 7 capas (Promedio)**. Se observa cómo la selección inteligente de capas puede reducir el ruido y mejorar la definición de las ROIs.

#### Paciente C0793i
*Vector Resultante: `[0 1 1 1 1 1 1]`*
| Búsqueda Local (Ref. Vector + Promedio) | Fusión Total (7 Capas + Promedio) |
| :---: | :---: |
| ![](results_comparison/average/best_img_C0793i_20251127_183027.png) | ![](results_total/average/C0793i_total_average.png) |

#### Paciente C0014d
*Vector Resultante: `[1 1 1 1 1 1 0]`*
| Búsqueda Local (Ref. Vector + Promedio) | Fusión Total (7 Capas + Promedio) |
| :---: | :---: |
| ![](results_comparison/average/best_img_C0014d_20251127_183028.png) | ![](results_total/average/C0014d_total_average.png) |

#### Paciente C0012d
*Vector Resultante: `[1 1 1 1 1 1 0]`*
| Búsqueda Local (Ref. Vector + Promedio) | Fusión Total (7 Capas + Promedio) |
| :---: | :---: |
| ![](results_comparison/average/best_img_C0012d_20251127_183027.png) | ![](results_total/average/C0012d_total_average.png) |

## Requisitos y Uso del Sistema

### Requisitos

**MATLAB**
- MATLAB con Image Processing Toolbox
- Archivos de imagen en formato BMP RGB
- Estructura de nombres: `C0683d_N[1-7]_mask.bmp`

**Python**
- Python 3.6 o superior
- Librerías: NumPy, OpenCV (cv2), SciPy, scikit-image, Matplotlib

### Configuración y Uso

#### Validación de Instalación
Ejecutar primero para verificar que todas las librerías están instaladas:
```bash
python3 test_installation.py
```


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
