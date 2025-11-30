import os
import glob

def parse_file(filename):
    data = {}
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    start_reading = False
    for line in lines:
        if '---' in line:
            start_reading = True
            continue
        if not start_reading:
            continue
        if not line.strip():
            continue
            
        parts = line.split('|')
        if len(parts) < 4: continue
        
        if 'AVERAGE' in line:
            patient = 'Promedio'
        else:
            patient = parts[0].strip()
            
        max_layer = float(parts[1].strip())
        fused_cnr = float(parts[2].strip())
        edge = float(parts[3].strip())
        data[patient] = {'max_layer': max_layer, 'cnr': fused_cnr, 'edge': edge}
    return data

files = {
    'Img Comp (Avg)': 'metrics_results/complete_fusion_average.txt',
    'Img Comp (Prio)': 'metrics_results/complete_fusion_priority.txt',
    'Vec Ref (Avg)': 'metrics_results/vector_reference_average.txt',
    'Vec Ref (Prio)': 'metrics_results/vector_reference_priority.txt',
    'LS Rand (Avg)': 'metrics_results/LS_average.txt',
    'LS Rand (Prio)': 'metrics_results/LS_priority.txt',
    'LS Ref (Avg)': 'metrics_results/LS_vector_reference_average.txt',
    'LS Ref (Prio)': 'metrics_results/LS_vector_reference_priority.txt'
}

# Load all data
all_data = {}
patients = []

for col_name, filepath in files.items():
    file_data = parse_file(filepath)
    all_data[col_name] = file_data
    if not patients:
        patients = [p for p in file_data.keys() if p != 'Promedio']

patients.sort()
patients.append('Promedio')

# Generate CNR Table
print("### Tabla 1: Comparación de CNR (Contrast-to-Noise Ratio)")
print("\nEl CNR mide qué tan fuerte es la señal del tumor en comparación con el ruido del fondo.\n")
header = "| Paciente | Max Layer CNR | " + " | ".join(files.keys()) + " |"
print(header)
print("|" + "---|" * (len(files) + 2))

for p in patients:
    # Obtener Max Layer CNR del primer dataset (es igual para todos)
    max_layer_val = all_data['Img Comp (Avg)'][p]['max_layer']
    
    row = f"| {p} | {max_layer_val:.4f} |"
    for col in files.keys():
        val = all_data[col][p]['cnr']
        row += f" {val:.4f} |"
    print(row)

print("\n### Tabla 2: Comparación de Edge Preservation")
print("\nEsta métrica (0-1) indica qué tan bien se conservan los bordes originales.\n")
header = "| Paciente | " + " | ".join(files.keys()) + " |"
print(header)
print("|" + "---|" * (len(files) + 1))

for p in patients:
    row = f"| {p} |"
    for col in files.keys():
        val = all_data[col][p]['edge']
        row += f" {val:.4f} |"
    print(row)
