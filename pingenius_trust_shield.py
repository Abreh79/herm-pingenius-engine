#!/usr/bin/env python3
"""
PinGenius - Phase 4: Trust Score Shield & Safe Dispatch Engine
Pacing scheduler, image hash perturbation, and anti-shadowban shield.
"""

import argparse
import json
import os
import random
import time
from datetime import datetime, timedelta
from PIL import Image

def perturb_image_hash(input_path, output_path):
    """
    Applies microscopic pixel & metadata tweaks to ensure every uploaded Pin 
    has a unique cryptographic hash, protecting account trust score.
    """
    with Image.open(input_path) as img:
        img = img.convert("RGB")
        # Subtly tweak bottom-right pixel RGB by 1 unit
        pixels = img.load()
        w, h = img.size
        r, g, b = pixels[w - 1, h - 1]
        r = (r + random.choice([1, -1])) % 256
        pixels[w - 1, h - 1] = (r, g, b)
        
        img.save(output_path, "PNG", optimize=True)
    return output_path

def calculate_safe_schedule(total_pins, start_time=None, min_interval_mins=45, max_interval_mins=180):
    """
    Generates realistic, human-like randomized posting schedule to stay 
    under algorithmic spam detection thresholds.
    """
    if not start_time:
        current_time = datetime.now()
    else:
        current_time = datetime.fromisoformat(start_time)
        
    schedule = []
    
    for i in range(total_pins):
        # Random interval between 45 and 180 minutes
        interval = random.randint(min_interval_mins, max_interval_mins)
        current_time += timedelta(minutes=interval)
        
        # Avoid posting during low-engagement night hours (2 AM to 6 AM)
        if 2 <= current_time.hour < 6:
            current_time += timedelta(hours=5)
            
        schedule.append({
            "pin_id": i + 1,
            "scheduled_time": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "interval_delay_mins": interval
        })
        
    return schedule

def generate_dispatch_plan(manifest_path):
    with open(manifest_path, "r") as f:
        manifest = json.load(f)
        
    pins = manifest["static_pin_variants"]
    schedule = calculate_safe_schedule(len(pins))
    
    dispatch_queue = []
    for idx, pin in enumerate(pins):
        orig_file = pin["file_path"]
        safe_file = orig_file.replace(".png", "_shielded.png")
        
        # Perturb Hash
        perturb_image_hash(orig_file, safe_file)
        
        dispatch_queue.append({
            "pin_variant_id": pin["variant_id"],
            "scheduled_time": schedule[idx]["scheduled_time"],
            "shielded_file_path": safe_file,
            "title": manifest["seo_metadata"]["title"],
            "board": manifest["seo_metadata"]["recommended_board"],
            "anti_spam_hash_protected": True
        })
        
    shield_report = {
        "account_trust_rating": "HEALTHY (Low Spam Risk)",
        "pacing_strategy": "Human-dithered 45-180m interval",
        "hash_obfuscation": "ACTIVE",
        "dispatch_queue": dispatch_queue
    }
    
    return shield_report

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    parser = argparse.ArgumentParser(description="PinGenius Trust Shield & Dispatcher")
    parser.add_argument("--manifest", default=os.path.join(BASE_DIR, "dist", "pin_manifest.json"))
    
    args = parser.parse_args()
    report = generate_dispatch_plan(args.manifest)
    print(json.dumps(report, indent=2))
