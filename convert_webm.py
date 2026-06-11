from moviepy import VideoFileClip

try:
    print("Loading video...")
    clip = VideoFileClip("GIF.mp4")
    
    duration = clip.duration
    start = min(1.0, duration / 2) if duration > 2 else 0
    end = min(start + 4.0, duration)
    
    print(f"Trimming from {start} to {end}...")
    subclip = clip.subclipped(start, end)
    
    subclip = subclip.resized(width=400)
    
    print("Writing WEBM...")
    # Use libvpx for webm compatibility in Opera/Firefox
    subclip.write_videofile("ekipmanlar/kasa_video.webm", fps=30, codec="libvpx", audio=False)
    print("Done!")
except Exception as e:
    print(f"Error: {e}")
