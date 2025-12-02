import cv2
import glob
import os

# Define the directory where the BMP files are located
directory = "overleaf/figures/"

# Find all .bmp files in the specified directory
bmp_files = glob.glob(os.path.join(directory, "*.bmp"))

for bmp_file_path in bmp_files:
    # Read the BMP image
    img = cv2.imread(bmp_file_path)

    if img is not None:
        # Create the corresponding PNG file path
        # Splits the path into (root, ext) and replaces .bmp with .png
        png_file_path = os.path.splitext(bmp_file_path)[0] + ".png"

        # Write the image as a PNG file
        cv2.imwrite(png_file_path, img)
        print(f"Converted {bmp_file_path} to {png_file_path}")
    else:
        print(f"Failed to load image: {bmp_file_path}")
