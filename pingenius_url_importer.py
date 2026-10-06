#!/usr/bin/env python3
"""
PinGenius - Upgrade 1: Dynamic URL & Web Page Importer
Fetches any target landing page/website URL, extracts brand assets, title,
meta description, headers, and imagery, then feeds them directly into Strategy Brain.
"""

import argparse
import json
import re
import urllib.request
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def fetch_and_parse_url(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) PinGenius/1.0'}
    req = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8', errors='ignore')
    except Exception as e:
        return {"status": "error", "message": f"Failed to fetch URL: {str(e)}"}
        
    soup = BeautifulSoup(html, 'html.parser')
    
    # 1. Extract Page Title
    title = ""
    if soup.title and soup.title.string:
        title = soup.title.string.strip()
    elif soup.find('h1'):
        title = soup.find('h1').get_text(strip=True)
        
    # 2. Extract Meta Description
    meta_desc = ""
    desc_tag = soup.find('meta', attrs={'name': 'description'}) or soup.find('meta', attrs={'property': 'og:description'})
    if desc_tag and desc_tag.get('content'):
        meta_desc = desc_tag['content'].strip()
        
    # 3. Extract OpenGraph Image
    og_image = ""
    og_img_tag = soup.find('meta', attrs={'property': 'og:image'})
    if og_img_tag and og_img_tag.get('content'):
        og_image = og_img_tag['content'].strip()
        
    # 4. Extract Headings for Hooks Context
    headings = [h.get_text(strip=True) for h in soup.find_all(['h1', 'h2', 'h3']) if len(h.get_text(strip=True)) > 5][:5]
    
    # 5. Extract Domain Brand Name
    parsed_domain = urlparse(url).netloc
    brand_name = parsed_domain.replace("www.", "").capitalize()
    
    # 6. Heuristic Niche / Topic Inference
    full_text = (title + " " + meta_desc + " " + " ".join(headings)).lower()
    
    if "detailing" in full_text or "car" in full_text or "auto" in full_text:
        niche = "Auto Detailing"
    elif "hvac" in full_text or "heating" in full_text or "air conditioning" in full_text:
        niche = "HVAC Services"
    elif "workbook" in full_text or "phonics" in full_text or "kindergarten" in full_text or "book" in full_text:
        niche = "KDP Workbooks"
    elif "invoice" in full_text or "construction" in full_text or "audit" in full_text:
        niche = "Construction Tech"
    else:
        niche = "General Business"

    topic = title if title else "Exclusive Offer & Guide"
    
    return {
        "status": "success",
        "url": url,
        "brand_name": brand_name,
        "extracted_data": {
            "title": title,
            "meta_description": meta_desc,
            "og_image": og_image,
            "headings": headings
        },
        "inferred_params": {
            "topic": topic[:60],
            "niche": niche
        }
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PinGenius URL Importer")
    parser.add_argument("--url", required=True, help="Target URL to inspect & convert into Pins")
    
    args = parser.parse_args()
    parsed = fetch_and_parse_url(args.url)
    print(json.dumps(parsed, indent=2))
