from moviepy import VideoFileClip

try:
    print("Loading video...")
    clip = VideoFileClip("GIF.mp4")
    
    duration = clip.duration
    start = 0
    end = min(4.0, duration)
    
    print(f"Trimming from {start} to {end}...")
    subclip = clip.subclipped(start, end)
    
    subclip = subclip.resized(width=300)
    
    print("Writing GIF...")
    subclip.write_gif("ekipmanlar/kasa_video.gif", fps=12)
    print("Done!")
except Exception as e:
    print(f"Error: {e}")
