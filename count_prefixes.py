import os
import glob

def get_unique_prefixes(base_dir):
    prefixes = set()
    # Search in all subdirectories of Images
    # Pattern: Images/*/*.bmp
    # We assume filename format: Prefix_N#_mask.bmp
    
    search_path = os.path.join(base_dir, '*', '*.bmp')
    files = glob.glob(search_path)
    
    print(f"Found {len(files)} bmp files.")
    
    for file_path in files:
        filename = os.path.basename(file_path)
        # Split by underscore to get the prefix (e.g., C0011d from C0011d_N1_mask.bmp)
        parts = filename.split('_')
        if len(parts) >= 1:
            prefixes.add(parts[0])
            
    return sorted(list(prefixes))

base_dir = 'Images'
unique_prefixes = get_unique_prefixes(base_dir)

print(f"\nTotal unique prefixes found: {len(unique_prefixes)}")
print("Prefixes:")
print(unique_prefixes)
