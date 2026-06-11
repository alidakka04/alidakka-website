import sys
from PIL import Image

print("Fixing logo.png...")
try:
    img = Image.open("logo.png").convert("RGBA")
    datas = img.getdata()
    newData = []
    for item in datas:
        # threshold for black background (making it transparent)
        if item[0] < 30 and item[1] < 30 and item[2] < 30:
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)
    img.putdata(newData)
    img.save("logo.png", "PNG")
    print("Fixed logo.png successfully.")
except Exception as e:
    print(f"Error fixing logo: {e}")
