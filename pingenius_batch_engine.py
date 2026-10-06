#!/usr/bin/env python3
"""
PinGenius - Phase 3: Multi-Format Batch Engine v3.0
Generates Static Pins, Carousel Story Bundles, and Official Pinterest Bulk CSV
"""

import argparse
import csv
import json
import os
import zipfile
from pingenius_strategy_brain import analyze_and_generate
from pingenius_canvas_engine import generate_pin_canvas, THEMES

OUTPUT_DIR = "/home/yayock79/herm_pingenius_engine/dist"

LAYOUT_ROTATION = [
    ("editorial_vignette", "dark_bold"),
    ("split_screen", "clean_light"),
    ("frosted_card", "vibrant_gold"),
    ("editorial_vignette", "dark_bold"),
    ("split_screen", "clean_light")
]

def generate_batch_bundle(topic, niche, brand_name="PinGenius.io", target_url=None, intent=None, gemini_key=None):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 1. Run Strategy Brain (Phase 1)
    strategy = analyze_and_generate(topic, niche, intent=intent, gemini_key=gemini_key)
    
    hooks = strategy["overlay_hooks"]
    meta = strategy["pin_metadata"]
    intent_bucket = strategy["intent_bucket"]
    ai_engine = strategy.get("ai_engine", "PinGenius High-CTR Engine")
    pin_seo_items = strategy.get("pin_seo_items", [])
    hashtags_str = " " + " ".join(strategy.get("hashtags", []))
    keywords_str = ", ".join(strategy.get("seo_keywords", [niche.lower(), topic.lower()]))
    
    link_url = target_url or f"https://pingenius.io/{niche.lower().replace(' ', '-')}"
    
    generated_pins = []
    
    # 2. Render 5 Static Pins rotating across 3 Layout Archetypes
    for idx, hook in enumerate(hooks[:5]):
        layout_type, theme_name = LAYOUT_ROTATION[idx % len(LAYOUT_ROTATION)]
        filename = f"pin_variant_{idx + 1}_{theme_name}.png"
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        generate_pin_canvas(
            hook_text=hook,
            niche=niche,
            cta_text=meta["cta_text"],
            brand_name=brand_name,
            theme_name=theme_name,
            layout_type=layout_type,
            output_path=filepath
        )
        
        # Get specific SEO item or fall back
        pin_seo = pin_seo_items[idx] if idx < len(pin_seo_items) else {}
        pin_title = pin_seo.get("title", f"{hook} | {niche}")
        pin_desc = pin_seo.get("description", f"{hook}. {meta['description']}")
        if hashtags_str not in pin_desc:
            pin_desc += hashtags_str
        pin_kw = pin_seo.get("keywords", keywords_str)
        
        generated_pins.append({
            "variant_id": idx + 1,
            "hook": hook,
            "theme": theme_name,
            "layout": layout_type,
            "file_path": filepath,
            "title": pin_title,
            "description": pin_desc,
            "keywords": pin_kw
        })

    # 3. Build 5 Progress-Badged Carousel Slides ('Step X of 5')
    carousel_slides = [
        {
            "slide": 1,
            "text": hooks[0],
            "cta": "Swipe for Next Tip ->",
            "layout": "frosted_card",
            "theme": "dark_bold"
        },
        {
            "slide": 2,
            "text": f"1. Audit Your Current {niche} Workflow & Identify Bottlenecks",
            "cta": "Swipe for Next Tip ->",
            "layout": "split_screen",
            "theme": "clean_light"
        },
        {
            "slide": 3,
            "text": f"2. Implement Proven {topic} Best Practices For Max Impact",
            "cta": "Swipe for Next Tip ->",
            "layout": "frosted_card",
            "theme": "vibrant_gold"
        },
        {
            "slide": 4,
            "text": f"3. Eliminate The #1 Mistake That Costs Time & Profits",
            "cta": "Swipe for Final Tip ->",
            "layout": "split_screen",
            "theme": "clean_light"
        },
        {
            "slide": 5,
            "text": f"Master {topic} With Our Step-By-Step Guide",
            "cta": meta["cta_text"],
            "layout": "editorial_vignette",
            "theme": "dark_bold"
        }
    ]
    
    carousel_pins = []
    for slide in carousel_slides:
        filename = f"carousel_slide_{slide['slide']}.png"
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        generate_pin_canvas(
            hook_text=slide["text"],
            niche=niche,
            cta_text=slide["cta"],
            brand_name=brand_name,
            theme_name=slide["theme"],
            layout_type=slide["layout"],
            progress_badge=f"Step {slide['slide']} of 5",
            output_path=filepath
        )
        carousel_pins.append({"slide": slide["slide"], "file_path": filepath, "text": slide["text"]})

    # 4. Generate Official Pinterest Business Bulk CSV (pinterest_bulk_create.csv)
    csv_path = os.path.join(OUTPUT_DIR, "pinterest_bulk_create.csv")
    with open(csv_path, mode="w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        # Pinterest Business Bulk Upload Headers
        writer.writerow(["Title", "Description", "Media File Name", "Link URL", "Keywords"])
        
        # Write Static Pin Rows
        for pin in generated_pins:
            media_filename = os.path.basename(pin["file_path"])
            writer.writerow([
                pin["title"],
                pin["description"],
                media_filename,
                link_url,
                pin["keywords"]
            ])

        # Write Carousel Cover Row
        if carousel_pins:
            media_filename = os.path.basename(carousel_pins[0]["file_path"])
            writer.writerow([
                f"{topic} Carousel Story Pack | {niche}",
                meta["description"] + hashtags_str,
                media_filename,
                link_url,
                keywords_str
            ])

    # 5. Package Master Export JSON & Zip Archive
    manifest = {
        "pingenius_engine": "PinGenius Studio Canvas Engine v3.0",
        "version": "3.0.0",
        "ai_engine": ai_engine,
        "topic": topic,
        "niche": niche,
        "brand_name": brand_name,
        "link_url": link_url,
        "intent_bucket": intent_bucket,
        "seo_metadata": meta,
        "seo_keywords": strategy["seo_keywords"],
        "hashtags": strategy.get("hashtags", []),
        "bulk_csv": csv_path,
        "static_pin_variants": generated_pins,
        "carousel_bundle": carousel_pins
    }
    
    manifest_path = os.path.join(OUTPUT_DIR, "pin_manifest.json")
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
        
    zip_path = os.path.join(OUTPUT_DIR, f"{niche.lower().replace(' ', '_')}_pin_bundle.zip")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(manifest_path, arcname="pin_manifest.json")
        zipf.write(csv_path, arcname="pinterest_bulk_create.csv")
        for pin in generated_pins:
            zipf.write(pin["file_path"], arcname=os.path.basename(pin["file_path"]))
        for slide in carousel_pins:
            zipf.write(slide["file_path"], arcname=os.path.basename(slide["file_path"]))
            
    return {
        "manifest": manifest_path,
        "bulk_csv": csv_path,
        "zip_bundle": zip_path,
        "static_pin_variants": generated_pins,
        "carousel_bundle": carousel_pins,
        "total_static_pins": len(generated_pins),
        "total_carousel_slides": len(carousel_pins),
        "ai_engine": ai_engine
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PinGenius Batch Engine CLI")
    parser.add_argument("--topic", required=True, help="Target topic")
    parser.add_argument("--niche", required=True, help="Target niche")
    parser.add_argument("--brand", default="PinGenius.io", help="Brand name")
    parser.add_argument("--url", help="Landing page target URL")
    parser.add_argument("--gemini-key", help="Gemini API Key")
    
    args = parser.parse_args()
    res = generate_batch_bundle(args.topic, args.niche, args.brand, target_url=args.url, gemini_key=args.gemini_key)
    print(f"Generated {res['total_static_pins']} Pins + {res['total_carousel_slides']} Carousel Slides + CSV via {res['ai_engine']}. ZIP: {res['zip_bundle']}")
