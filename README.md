# Optimization of Electroimpedance Image Fusion using Local Search and Layer Analysis

Ashley Dafne Aguilar Salinas  
Computer Science Department, INAOE  
Tonantzintla, Puebla, México  
ashleyd.aguilars@inaoep.mx  

Daira Adriana Chavarría Rodríguez  
Computer Science Department, INAOE  
Tonantzintla, Puebla, México  
daira.chavarriar@inaoep.mx  

## Abstract

This paper presents an approach for optimizing the fusion of electroimpedance images (EIM) using local search algorithms and layer analysis. The proposed system processes sets of 7 image masks corresponding to different depth levels (N1-N7), seeking the optimal combination that maximizes the detection of regions of interest (tumors) and edge preservation. Two fusion methods are compared: priority-based and average-based, applied to regions of interest selected via color criteria. Experimental results on a set of patients demonstrate that optimization using local search, combined with average fusion, achieves competitive performance compared to other fusion techniques, such as the total combination of all 7 layers, obtaining quantifiable improvements in Contrast-to-Noise Ratio (CNR) and maintaining adequate preservation of structural edges.

## Keywords

Electroimpedance, Image Fusion, Local Search, Optimization, Medical Image Processing.

## Introduction

Electroimpedance (EIM) is a non-invasive medical imaging technique that allows characterizing biological tissues based on their electrical properties, such as conductivity and permittivity [2], [3]. This technique is particularly valuable for early detection of anomalies, such as breast tumors, as malignant tissues often exhibit electrical properties that are significantly different from those of healthy tissues [2]. Unlike other modalities such as X-rays, EIM does not expose the patient to ionizing radiation, making it a safe option for frequent monitoring.

However, the interpretation of EIM images can be complex because relevant information is often distributed across multiple layers or depth levels, and spatial resolution is usually limited compared to anatomical techniques like magnetic resonance imaging. Recent studies have explored various techniques to improve the quality and diagnostic utility of these images, including advanced reconstruction methods and information fusion [4]. In particular, the work presented in [5] (DOI: 10.60647/q3yr-rw85) highlights the importance of considering volumetric information and intelligent data selection to improve pathology detection.

In this project, we address the problem of optimal selection and fusion of EIM image layers. Each patient study consists of 7 layers (N1 to N7), where each layer may contain vital information about the presence and location of anomalies. Indiscriminate fusion of all layers can introduce noise and reduce the contrast of the region of interest. Therefore, there is a need for an intelligent method that selects the most effective combination of layers to generate a high-quality final composite image.

The main objective of this work is to develop and evaluate a system that combines image processing techniques with metaheuristic optimization algorithms to determine the best fusion strategy.

## Methodology

### Individual Representation

To address the layer selection problem as an optimization problem, the solution is modeled using a binary vector v of length 7. In this representation, each position of the vector corresponds to one of the 7 depth layers (N1 to N7). A value of 1 at position i indicates that the i-th layer is included in the fusion process, while a 0 indicates it is discarded. This allows representing 2^7 − 1 = 127 possible layer combinations (excluding the trivial case of the null vector). This compact representation facilitates the application of search algorithms, allowing efficient exploration of the solution space to find the combination that maximizes the resulting image quality.

### Region of Interest Detection

Before proceeding to fusion, it is fundamental to identify regions that potentially correspond to anomalous tissue (tumors) in each of the selected layers. Since EIM images typically use color maps to represent conductivity, an RGB color space-based segmentation criterion is employed. Specifically, pixels with a predominant red component are sought, which is characteristic of high conductivity zones in the used color map. A pixel is considered part of the region of interest if it meets the condition: (R ≥ 60) ∧ (R > G) ∧ (G > B). This segmentation allows focusing the fusion process exclusively on clinically relevant areas, preventing background noise or artifacts present in other image zones from degrading the final result.

The choice of red-dominant pixel segmentation is guided by the specific color map used in EIM systems, where red tones typically indicate higher conductivity values. This colorimetric encoding is consistent across the dataset, allowing reliable identification of high-contrast zones that potentially correspond to pathological regions.

### Fusion Methods

Two distinct strategies are proposed and evaluated to combine the information from selected layers, to determine which best preserves tumor characteristics:

#### Priority Fusion

In this method, layers are processed in a predefined sequential order, from the most superficial layer (N1) to the deepest (N7). The underlying idea is to simulate a physical superposition, where information from a higher layer takes precedence over lower ones. If a pixel at position (x,y) is identified as part of a region of interest in a higher layer, its value overwrites any information from lower layers at that same position. This approach seeks to preserve the original intensity of the strongest detected signal.

#### Average Fusion

Unlike the previous method, average fusion seeks to integrate information from all selected layers that detect an anomaly at the same location. In zones where multiple layers overlap, the resulting pixel color is calculated as the arithmetic mean of the colors of those layers: C_final(x,y) = 1/K ∑_{i∈S} C_i(x,y), where S is the set of active layers and K is its cardinality. This technique aims to smooth abrupt variations and reduce random noise, producing a more homogeneous representation of the region of interest.

### Optimization Algorithms

#### Reference Vector (Brute Force)

To start the local search from a promising and non-random point, an exhaustive search (brute force) was first performed on a representative training set. All 127 possible layer combinations were evaluated for each patient in the training set, and their average performance was calculated. The vector that maximized the global average fitness was selected as the "Reference Vector". The analysis yielded the vector:

v_ref = [1, 0, 1, 0, 0, 0, 0]

This vector suggests that, on average, the combination of layers N1 and N3 provides a solid basis for detection and serves as an initial seed to refine the solution via local search for each specific patient.

Given the limited dimensionality of the problem (2^7 = 128 possible combinations), exhaustive evaluation remains computationally feasible. However, the proposed local search algorithm lays the foundation for scaling to higher dimensions or for incorporating more complex fusion strategies that may arise in extended applications.

#### Local Search

Local Search explores the neighborhood of the current vector by making minimal changes (bit flip) to find incremental improvements. The pseudocode of the implemented algorithm is:

```
v_best ← v_initial
f_best ← Evaluate(v_best)
improvement ← TRUE
while improvement AND iter < MAX_ITER do
    improvement ← FALSE
    for i ← 1 to 7 do
        v_neighbor ← FlipBit(v_best, i)
        f_neighbor ← Evaluate(v_neighbor)
        if f_neighbor > f_best then
            v_best ← v_neighbor
            f_best ← f_neighbor
            improvement ← TRUE
            break
        end if
    end for
end while
return v_best
```

The evaluation function (fitness) weights the quantity of valid pixels detected and their consistency, favoring solutions that clearly highlight the zone of interest.

By optimizing the selection of layers per patient, the proposed method avoids the need to fuse all 7 layers indiscriminately, thus reducing informational redundancy. The adaptiveness of the approach ensures that the selected configuration is tailored to each patient's specific impedance profile, aligning with the objective of maximizing diagnostically relevant content while minimizing unnecessary data integration.

## Results

### Evaluation Metrics

To quantify the performance of the fusion methods, two main metrics were used:

#### Contrast-to-Noise Ratio (CNR)

CNR measures the ability to distinguish the region of interest (tumor) from the background. It is calculated as:

CNR = |μ_tumor − μ_background| / σ_background

Where μ_tumor and μ_background are the mean signal intensities in the tumor and background regions, respectively, and σ_background is the standard deviation of the background. A higher value indicates better detectability.

#### Edge Preservation

A metric based on Sobel edge information (proposed by Xydeas and Petrovic) was used to evaluate how well the fused image preserves the edges present in the original layers. The value ranges between 0 and 1, where 1 indicates perfect preservation.

### Quantitative Results

Table I summarizes the results obtained (Mean ± Standard Deviation) for the different configurations evaluated on the set of 15 patients.

| Method | CNR | Edge Preserv. |
|--------|-----|---------------|
| Max Layer (Base) | 3.5398 ± 3.5418 | - |
| Total Fusion (Avg) | 0.5879 ± 0.5691 | 0.5386 ± 0.0908 |
| Total Fusion (Prio) | 0.3920 ± 0.4294 | 0.5549 ± 0.0998 |
| Ref. Vector (Avg) | 0.4327 ± 0.5144 | 0.5570 ± 0.1017 |
| Ref. Vector (Prio) | 0.3840 ± 0.5056 | 0.5544 ± 0.0988 |
| LS Random (Avg) | 0.7267 ± 0.7393 | 0.5417 ± 0.0916 |
| LS Random (Prio) | 0.5071 ± 0.5503 | 0.5424 ± 0.0940 |
| LS Ref (Avg) | **0.7384 ± 0.7310** | 0.5412 ± 0.0913 |
| LS Ref (Prio) | 0.5022 ± 0.5543 | 0.5408 ± 0.0933 |

It is observed that the combination of Local Search starting with Reference Vector and Average Fusion (LS Ref Avg) achieves the best performance in CNR (0.7384), significantly outperforming total fusion (0.5879) and priority methods. Edge preservation remains consistent around 0.54−0.55 across all methods, indicating that the improvement in contrast does not sacrifice image structure.


## Conclusions

This work has demonstrated the feasibility and efficacy of applying metaheuristic optimization techniques, specifically local search, to the problem of electroimpedance image fusion. The results obtained indicate that intelligent layer selection, rather than indiscriminate fusion, allows for significantly improving the quality of diagnostic images, increasing the contrast between tumor tissue and the background without sacrificing edge integrity. The Local Search strategy starting with a Reference Vector, combined with average fusion, positions itself as the most robust method, achieving the best performance in Contrast-to-Noise Ratio (CNR).

As future work, the exploration of alternative color spaces, such as HSL (Hue, Saturation, Lightness), is proposed for the segmentation stage. It is possible that separating chrominance and luminance information allows for more robust detection of regions of interest, especially in the presence of variable lighting conditions or color artifacts. Likewise, the integration of more complex optimization algorithms, such as genetic algorithms or particle swarm optimization, could be investigated to explore the search space more globally, although the current local search approach has proven to be efficient and effective for the dimensionality of the problem addressed.

It is possible to modify the objective function of the local search since, according to the statistics, an individual layer (from N1 to N7) can have a better Contrast-to-Noise Ratio (CNR) than the fusion of layers.

## Acknowledgments

The authors thank INAOE for the support and resources provided for the realization of this research.

## References

[1] Xydeas, C. S., & Petrovic, V. (2000). Objective image fusion performance measure. Electronics letters, 36(4), 308-309.

[2] Holder, D. S. (2004). Electrical impedance tomography: methods, history and applications. CRC press.

[3] Grimnes, S., & Martinsen, O. G. (2014). Bioimpedance and bioelectricity basics. Academic press.

[4] Adler, A., & Boyle, A. (2017). Electrical impedance tomography: tissue properties to image measures. IEEE Transactions on Biomedical Engineering, 64(11), 2494-2504.

[5] Jazmín, A. G., Hayde, P. B., Irazú, H. F. D., & O, M. B. (2025). Mamografía Por Impedancia Eléctrica: Una Tecnología No Invasiva Para La Detección Del Cáncer De Mama. Physos. https://doi.org/10.60647/q3yr-rw85
