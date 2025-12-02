#!/usr/bin/env python3
"""
Orchestrates the local search on all 15 validation patients.
Uses the same patient split logic as find_general_vector.py (seed 42).
Calls local_search.py for each patient.
"""

import os
import glob
import random
import subprocess
import argparse
from datetime import datetime


def get_all_prefixes(image_folder):
    """
    Scans the image_folder to find all unique patient prefixes.
    Assumes structure: image_folder/*/Prefix_N#_mask.bmp
    """
    prefixes = set()
    search_path = os.path.join(image_folder, '*', '*.bmp')
    files = glob.glob(search_path)
    
    for file_path in files:
        filename = os.path.basename(file_path)
        parts = filename.split('_')
        if len(parts) >= 1:
            prefixes.add(parts[0])
            
    return sorted(list(prefixes))


def get_validation_patients(image_folder):
    # Returns the 15 validation patients using the same logic as find_general_vector.py.
    all_prefixes = get_all_prefixes(image_folder)
    total_patients = len(all_prefixes)
    
    if total_patients < 35:
        print("Warning: Less than 35 patients found. Using all available as validation.")
        return all_prefixes
        
    random.seed(42)  # Must match find_general_vector.py
    random.shuffle(all_prefixes)
    
    # First 35 are training, last 15 are validation
    val_prefixes = all_prefixes[35:]
    return val_prefixes


def find_patient_folder(base_folder, prefix):
    """
    Finds the subfolder containing images for the given patient prefix.
    """
    for subdir in glob.glob(os.path.join(base_folder, '*')):
        if os.path.isdir(subdir):
            if glob.glob(os.path.join(subdir, f'{prefix}_*.bmp')):
                return subdir
    return None


def main():
    parser = argparse.ArgumentParser(description='Run local search on all 15 validation patients')
    parser.add_argument('--image_folder', type=str, default='Images', help='Base folder containing patient images')
    parser.add_argument('--initial_vector', type=str, required=True, help='Path to .mat file containing the initial chromosome')
    parser.add_argument('--time_limit', type=int, default=1800, help='Time limit in seconds per patient')
    parser.add_argument('--out_dir', type=str, default='results_local_search', help='Output directory for results')
    args = parser.parse_args()

    print("=" * 60)
    print("VALIDATION SET LOCAL SEARCH")
    print("=" * 60)
    
    # Get validation patients
    val_patients = get_validation_patients(args.image_folder)
    print(f"\nFound {len(val_patients)} validation patients:")
    print(val_patients)
    print()
    
    results = []
    
    for i, patient in enumerate(val_patients, 1):
        print(f"\n{'=' * 60}")
        print(f"[{i}/{len(val_patients)}] Processing patient: {patient}")
        print(f"{'=' * 60}")
        
        # Find patient folder
        patient_folder = find_patient_folder(args.image_folder, patient)
        if patient_folder is None:
            print(f"ERROR: Could not find folder for patient {patient}")
            continue
            
        print(f"Located in: {patient_folder}")
        
        # Run local_search.py as subprocess
        cmd = [
            'python3', 'local_search.py',
            '--image_folder', patient_folder,
            '--prefix', patient,
            '--initial_vector', args.initial_vector,
            '--time_limit', str(args.time_limit),
            '--out_dir', args.out_dir
        ]
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(result.stdout)
            
            # Try to extract fitness from output
            for line in result.stdout.split('\n'):
                if 'fitness:' in line.lower():
                    # Extract fitness value
                    try:
                        fitness_str = line.split('fitness:')[1].strip().rstrip(')')
                        fitness = float(fitness_str)
                        results.append((patient, fitness))
                    except:
                        pass
                        
        except subprocess.CalledProcessError as e:
            print(f"ERROR processing {patient}:")
            print(e.stderr)
    
    # Save summary
    print(f"\n{'=' * 60}")
    print("VALIDATION SEARCH COMPLETED")
    print(f"{'=' * 60}")
    
    summary_path = os.path.join(args.out_dir, f'SUMMARY_VALIDATION_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt')
    with open(summary_path, 'w') as f:
        f.write("Summary of Local Search on Validation Set\n")
        f.write(f"Initial Vector File: {args.initial_vector}\n")
        f.write(f"Time Limit per Patient: {args.time_limit}s\n\n")
        f.write(f"Validation Patients: {val_patients}\n\n")
        f.write("Results:\n")
        for patient, fitness in results:
            f.write(f"  {patient}: {fitness:.6f}\n")
    
    print(f"\nSummary saved to: {summary_path}")
    print(f"Processed {len(results)}/{len(val_patients)} patients successfully")


if __name__ == '__main__':
    main()
