#!/usr/bin/env python3
"""
Apply the general reference vector directly to the 15 validation patients
without local search, to compare the baseline fitness of the general vector.

Results are saved to:
- results_reference_vector/priority/
- results_reference_vector/average/
"""

import os
import glob
import random
import numpy as np
from datetime import datetime

from objective_function_priority import objective_function_priority
from objective_function import objective_function
from utils_matlab_io import save_chromosome_mat, load_chromosome_mat


def get_all_prefixes(image_folder):
    # Scans the image_folder to find all unique patient prefixes.
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
    # Returns the 15 validation patients using the same logic as main.py.
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
    """Finds the subfolder containing images for the given patient prefix."""
    for subdir in glob.glob(os.path.join(base_folder, '*')):
        if os.path.isdir(subdir):
            if glob.glob(os.path.join(subdir, f'{prefix}_*.bmp')):
                return subdir
    return None


def apply_reference_vector(image_folder, reference_vector_path, out_base_dir):
    print("=" * 80)
    print("APPLYING REFERENCE VECTOR (NO LOCAL SEARCH)")
    print("=" * 80)
    
    # Load reference vector
    reference_chrom = load_chromosome_mat(reference_vector_path)
    print(f"\nReference Vector: {reference_chrom}")
    
    # Get validation patients
    val_patients = get_validation_patients(image_folder)
    print(f"\nValidation Patients ({len(val_patients)}): {val_patients}\n")
    
    # Output directories
    priority_dir = os.path.join(out_base_dir, 'priority')
    average_dir = os.path.join(out_base_dir, 'average')
    os.makedirs(priority_dir, exist_ok=True)
    os.makedirs(average_dir, exist_ok=True)
    
    results = []
    
    for i, patient in enumerate(val_patients, 1):
        print(f"\n{'=' * 80}")
        print(f"[{i}/{len(val_patients)}] Processing patient: {patient}")
        print(f"{'=' * 80}")
        
        patient_folder = find_patient_folder(image_folder, patient)
        if patient_folder is None:
            print(f"ERROR: Could not find folder for patient {patient}")
            continue
            
        print(f"Located in: {patient_folder}")
        
        # PRIORITY FUSION 
        print(f"\n--- Applying with PRIORITY fusion ---")
        
        fitness_priority, img_priority = objective_function_priority(
            reference_chrom, 
            image_folder=patient_folder, 
            prefix=patient
        )
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        chrom_path_p = os.path.join(priority_dir, f'ref_chrom_{patient}_{timestamp}.mat')
        img_path_p = os.path.join(priority_dir, f'ref_img_{patient}_{timestamp}.png')
        
        save_chromosome_mat(reference_chrom, chrom_path_p)
        _, _ = objective_function_priority(reference_chrom, image_folder=patient_folder, 
                                          prefix=patient, save_path=img_path_p)
        
        print(f"Priority - Fitness: {fitness_priority:.6f}")
        
        # AVERAGE FUSION 
        print(f"\n--- Applying with AVERAGE fusion ---")
        
        fitness_average, img_average = objective_function(
            reference_chrom, 
            image_folder=patient_folder, 
            prefix=patient
        )
        
        chrom_path_a = os.path.join(average_dir, f'ref_chrom_{patient}_{timestamp}.mat')
        img_path_a = os.path.join(average_dir, f'ref_img_{patient}_{timestamp}.png')
        
        save_chromosome_mat(reference_chrom, chrom_path_a)
        _, _ = objective_function(reference_chrom, image_folder=patient_folder, 
                                 prefix=patient, save_path=img_path_a)
        
        print(f"Average - Fitness: {fitness_average:.6f}")
        
        diff = fitness_priority - fitness_average
        winner = "PRIORITY" if diff > 0 else ("AVERAGE" if diff < 0 else "TIE")
        print(f"\n>>> Winner: {winner} (Δ = {diff:+.6f})")
        
        results.append({
            'patient': patient,
            'fitness_priority': fitness_priority,
            'fitness_average': fitness_average,
            'winner': winner
        })
    
    print(f"\n{'=' * 80}")
    print("SUMMARY")
    print(f"{'=' * 80}\n")
    
    summary_path = os.path.join(out_base_dir, f'SUMMARY_REFERENCE_VECTOR_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt')
    
    with open(summary_path, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("REFERENCE VECTOR APPLICATION RESULTS (NO LOCAL SEARCH)\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Reference Vector: {reference_chrom}\n")
        f.write(f"Validation Patients: {val_patients}\n\n")
        
        f.write("=" * 80 + "\n")
        f.write("DETAILED RESULTS\n")
        f.write("=" * 80 + "\n\n")
        
        priority_wins = 0
        average_wins = 0
        ties = 0
        
        for r in results:
            f.write(f"Patient: {r['patient']}\n")
            f.write(f"  Priority: {r['fitness_priority']:.6f}\n")
            f.write(f"  Average:  {r['fitness_average']:.6f}\n")
            f.write(f"  Winner:   {r['winner']} (Δ = {r['fitness_priority'] - r['fitness_average']:+.6f})\n\n")
            
            if r['winner'] == 'PRIORITY':
                priority_wins += 1
            elif r['winner'] == 'AVERAGE':
                average_wins += 1
            else:
                ties += 1
        
        # Statistics
        fitness_p = [r['fitness_priority'] for r in results]
        fitness_a = [r['fitness_average'] for r in results]
        
        f.write("=" * 80 + "\n")
        f.write("STATISTICAL SUMMARY\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Total Patients: {len(results)}\n\n")
        f.write(f"Wins:\n")
        f.write(f"  Priority: {priority_wins} ({priority_wins/len(results)*100:.1f}%)\n")
        f.write(f"  Average:  {average_wins} ({average_wins/len(results)*100:.1f}%)\n")
        f.write(f"  Ties:     {ties} ({ties/len(results)*100:.1f}%)\n\n")
        f.write(f"Fitness Statistics:\n")
        f.write(f"  Priority - Mean: {np.mean(fitness_p):.6f}, Std: {np.std(fitness_p):.6f}\n")
        f.write(f"  Average  - Mean: {np.mean(fitness_a):.6f}, Std: {np.std(fitness_a):.6f}\n")
        f.write(f"  Difference Mean: {np.mean(fitness_p) - np.mean(fitness_a):+.6f}\n")
    
    print(f"Summary saved to: {summary_path}")
    print(f"\nPriority Wins: {priority_wins}/{len(results)}")
    print(f"Average Wins:  {average_wins}/{len(results)}")
    print(f"Ties:          {ties}/{len(results)}")
    
    return results


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Apply reference vector to validation patients')
    parser.add_argument('--image_folder', type=str, default='Images', 
                       help='Base folder containing patient images')
    parser.add_argument('--reference_vector', type=str, required=True,
                       help='Path to .mat file containing the reference chromosome')
    parser.add_argument('--out_dir', type=str, default='results_reference_vector',
                       help='Output directory for results')
    args = parser.parse_args()
    
    apply_reference_vector(args.image_folder, args.reference_vector, args.out_dir)


if __name__ == '__main__':
    main()
