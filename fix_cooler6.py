import os
from rembg import remove, new_session

input_path = "ekipmanlar/sogutucu.png"

try:
    print(f"Loading {input_path}")
    with open(input_path, "rb") as i:
        input_data = i.read()
        
    print("Removing background artifacts with alpha matting...")
    session = new_session("u2net")
    output_data = remove(input_data, session=session, alpha_matting=True, alpha_matting_foreground_threshold=240, alpha_matting_background_threshold=10, alpha_matting_erode_size=10)
    
    with open(input_path, "wb") as o:
        o.write(output_data)
        
    print("Done! Re-processed sogutucu.png")
except Exception as e:
    print(f"Error: {e}")
