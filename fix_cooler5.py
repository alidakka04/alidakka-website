import os
from rembg import remove, new_session
from PIL import Image

input_path = r"C:\Users\user\.gemini\antigravity-ide\brain\0c9f5e48-f50e-4e7d-9e3a-bd6365aaabce\white_aio_cooler_1781112882213.png"
output_path = "ekipmanlar/sogutucu.png"

try:
    print(f"Loading {input_path}")
    with open(input_path, "rb") as i:
        input_data = i.read()
        
    print("Removing background with alpha matting...")
    session = new_session("u2net")
    output_data = remove(input_data, session=session, alpha_matting=True, alpha_matting_foreground_threshold=240, alpha_matting_background_threshold=10, alpha_matting_erode_size=10)
    
    with open(output_path, "wb") as o:
        o.write(output_data)
        
    print("Done! Replaced sogutucu.png")
except Exception as e:
    print(f"Error: {e}")
