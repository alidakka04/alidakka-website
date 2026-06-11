import os
from rembg import remove, new_session

input_dir = "ekipmanlar"
input_path = None
for f in os.listdir(input_dir):
    if "sogutma.jpg" in f:
        input_path = os.path.join(input_dir, f)
        break

output_path = "ekipmanlar/sogutucu.png"

try:
    print(f"Loading {input_path}")
    with open(input_path, "rb") as i:
        input_data = i.read()
        
    print("Removing background from new cooler image...")
    session = new_session("u2net")
    output_data = remove(input_data, session=session)
    
    with open(output_path, "wb") as o:
        o.write(output_data)
        
    print("Done! Saved to sogutucu.png")
except Exception as e:
    print(f"Error: {e}")
