#!/usr/bin/env python3
"""
PinGenius - Kinetic Motion Engine v1.0
Compiles Carousel Slide PNGs into a 10-Second Vertical MP4 Video Pin (1080x1920, 30fps, H.264)
Features progressive accent progress bar rendered on each slide.
"""

import os
import subprocess
import tempfile
from PIL import Image, ImageDraw

def add_progressive_accent_bar(image_path, output_path, slide_index, total_slides=5, bar_height=12, bar_color=(230, 0, 35)):
    """
    Overlays a subtle progressive accent bar at the bottom of the slide.
    bar_color defaults to Pinterest Red (230, 0, 35)
    """
    img = Image.open(image_path).convert("RGBA")
    width, height = img.size
    
    # Create overlay for dark background track and progress fill
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    # Bottom track background (semi-transparent dark)
    track_y0 = height - bar_height
    track_y1 = height
    draw.rectangle([0, track_y0, width, track_y1], fill=(15, 23, 42, 180))
    
    # Progress fill
    progress_ratio = slide_index / total_slides
    fill_width = int(width * progress_ratio)
    if fill_width > 0:
        draw.rectangle([0, track_y0, fill_width, track_y1], fill=bar_color + (255,))
        
    # Composite overlay onto original image
    composited = Image.alpha_composite(img, overlay).convert("RGB")
    composited.save(output_path, "PNG")
    return output_path

def generate_motion_pin(slide_paths, output_mp4_path, duration_per_slide=2.0, fps=30):
    """
    Compiles list of slide PNG paths into a vertical MP4 video using ffmpeg.
    Each slide gets a progressive accent bar and runs for duration_per_slide seconds.
    """
    if not slide_paths:
        raise ValueError("No slide paths provided for motion pin generation.")
        
    os.makedirs(os.path.dirname(os.path.abspath(output_mp4_path)), exist_ok=True)
    
    total_slides = len(slide_paths)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        processed_slides = []
        for idx, slide_p in enumerate(slide_paths, start=1):
            tmp_out = os.path.join(tmpdir, f"slide_bar_{idx}.png")
            add_progressive_accent_bar(slide_p, tmp_out, idx, total_slides=total_slides)
            processed_slides.append(tmp_out)
            
        # Create FFmpeg concat manifest file
        concat_txt_path = os.path.join(tmpdir, "concat.txt")
        with open(concat_txt_path, "w", encoding="utf-8") as f:
            for p in processed_slides:
                f.write(f"file '{p}'\n")
                f.write(f"duration {duration_per_slide}\n")
            # Repeat last file to ensure FFmpeg concat handles last frame duration properly
            f.write(f"file '{processed_slides[-1]}'\n")
            
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_txt_path,
            "-vf", f"fps={fps},scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2",
            "-c:v", "libx264",
            "-preset", "fast",
            "-pix_fmt", "yuv420p",
            output_mp4_path
        ]
        
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg motion pin generation failed: {result.stderr}")
            
    return output_mp4_path

if __name__ == "__main__":
    print("[pingenius_motion_engine] Kinetic Motion Engine module ready.")
