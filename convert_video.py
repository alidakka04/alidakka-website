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
    
    print("Writing MP4 with yuv420p...")
    # yuv420p is mandatory for HTML5 video compatibility across all browsers (Opera, Safari, Mobile)
    subclip.write_videofile("ekipmanlar/kasa_video.mp4", fps=30, codec="libx264", audio=False, ffmpeg_params=["-pix_fmt", "yuv420p"])
    print("Done!")
except Exception as e:
    print(f"Error: {e}")
