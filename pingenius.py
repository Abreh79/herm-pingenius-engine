#!/usr/bin/env python3
"""
PinGenius - Master On-Demand Pinterest Automation System (Herm tha Worm Edition)
Fuses 15 years of Pinterest DNA across 4 core phases + URL Importer.
"""

import argparse
import json
import os
import sys

from pingenius_url_importer import fetch_and_parse_url
from pingenius_strategy_brain import analyze_and_generate
from pingenius_canvas_engine import generate_pin_canvas
from pingenius_batch_engine import generate_batch_bundle
from pingenius_trust_shield import generate_dispatch_plan

def main():
    parser = argparse.ArgumentParser(description="PinGenius - Herm tha Worm Edition")
    parser.add_argument("--url", help="Target Website or Landing Page URL to Auto-Import")
    parser.add_argument("--topic", help="Topic / Subject")
    parser.add_argument("--niche", help="Industry / Niche")
    parser.add_argument("--brand", default="Herm tha Worm PinGenius", help="Brand handle or website URL")
    parser.add_argument("--intent", choices=["inspiration", "how_to", "proof", "product"], help="Intent Bucket Override")
    
    args = parser.parse_args()
    
    topic = args.topic
    niche = args.niche
    brand = args.brand
    imported_url_data = None
    
    # URL Importer Pipeline
    if args.url:
        print(f"[Herm tha Worm PinGenius] Scraping & Inspecting URL: {args.url}...")
        parsed_url = fetch_and_parse_url(args.url)
        if parsed_url.get("status") == "success":
            imported_url_data = parsed_url["extracted_data"]
            if not topic:
                topic = parsed_url["inferred_params"]["topic"]
            if not niche:
                niche = parsed_url["inferred_params"]["niche"]
            if args.brand == "Herm tha Worm PinGenius" and parsed_url.get("brand_name"):
                brand = f"@{parsed_url['brand_name']}"
            print(f"[Herm tha Worm PinGenius] Auto-Extracted -> Topic: '{topic}' | Niche: '{niche}' | Brand: '{brand}'")
        else:
            print(f"[Warning] URL import failed, falling back to manual inputs. Error: {parsed_url.get('message')}")

    if not topic or not niche:
        print("Error: You must provide either a valid --url OR both --topic and --niche.")
        sys.exit(1)
        
    print(f"[Herm tha Worm PinGenius] Initializing Batch Engine for '{topic}' ({niche})...")
    
    # Run Batch Engine (Phase 1, 2, 3)
    batch_res = generate_batch_bundle(topic, niche, brand, args.intent)
    
    # Run Trust Shield (Phase 4)
    shield_res = generate_dispatch_plan(batch_res["manifest"])
    
    output = {
        "status": "success",
        "engine": "PinGenius Engine v1.0 (Herm tha Worm Edition)",
        "signature_seal": "Herm tha Worm Certified",
        "url_import": {
            "source_url": args.url if args.url else "N/A (Manual Entry)",
            "extracted_headings": imported_url_data.get("headings", []) if imported_url_data else []
        },
        "summary": {
            "topic": topic,
            "niche": niche,
            "brand": brand,
            "total_assets_generated": batch_res["total_static_pins"] + batch_res["total_carousel_slides"],
            "bundle_zip": batch_res["zip_bundle"],
            "manifest": batch_res["manifest"]
        },
        "trust_shield_status": shield_res["account_trust_rating"],
        "dispatch_queue_sample": shield_res["dispatch_queue"][:2]
    }
    
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
