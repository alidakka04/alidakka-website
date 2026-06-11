from moviepy import VideoFileClip

try:
    print("Loading video...")
    clip = VideoFileClip("GIF.mp4")
    
    duration = clip.duration
    start = min(1.0, duration / 2) if duration > 2 else 0
    end = min(start + 4.0, duration)
    
    print(f"Trimming from {start} to {end}...")
    subclip = clip.subclipped(start, end)
    
    # Resize to 1080p (super high resolution for a web element)
    subclip = subclip.resized(width=1080)
    
    print("Writing high-res MP4...")
    subclip.write_videofile("ekipmanlar/kasa_video.mp4", fps=30, codec="libx264", audio=False, ffmpeg_params=["-pix_fmt", "yuv420p"])
    
    print("Writing high-res WEBM...")
    subclip.write_videofile("ekipmanlar/kasa_video.webm", fps=30, codec="libvpx", audio=False)
    
    print("Done!")
except Exception as e:
    print(f"Error: {e}")
