import os
from rembg import remove
from PIL import Image
import sys

input_folder = "ekipmanlar"
skip_files = ["anakart.png", "mouse.png"]

# First pass: identify files to process
to_process = []
for filename in os.listdir(input_folder):
    if filename in skip_files:
        continue
    if filename.endswith(".jpg") or filename.endswith(".png"):
        to_process.append(filename)

print(f"Found {len(to_process)} images to process.")

for filename in to_process:
    input_path = os.path.join(input_folder, filename)
    base_name, ext = os.path.splitext(filename)
    output_filename = base_name + ".png"
    output_path = os.path.join(input_folder, output_filename)
    
    print(f"Processing {filename}...")
    try:
        with open(input_path, 'rb') as i:
            input_data = i.read()
            
        output_data = remove(input_data)
        
        # If the output is successfully created, we can delete the old one if it was a .jpg
        # Or if it was a .png, we just overwrite
        with open(output_path, 'wb') as o:
            o.write(output_data)
            
        if ext.lower() in [".jpg", ".jpeg"]:
            os.remove(input_path)
            print(f"Deleted old {filename}")
            
        print(f"Saved {output_path}")
    except Exception as e:
        print(f"Error processing {filename}: {e}")
