#!/usr/bin/env python3
"""
PinGenius - Phase 1: Strategy Brain & AI Engine
Clean, Professional Pinterest SEO & Copy Generator
Powered by Gemini Flash API with Deep SEO & Hashtags
"""

import argparse
import json
import os
import urllib.request
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

SPECIALIZED_NICHE_HOOKS = {
    "auto detailing": [
        "5 Ceramic Coating Mistakes That Ruin Your Clear Coat",
        "How To Restore Faded Paint To Showroom Shine",
        "The Scratch-Free Wash Method Top Detailers Swear By",
        "Stop Using Dish Soap: Do This For Deep Paint Polish",
        "Before & After: 10-Year Paint Restoration Blueprint"
    ],
    "car detailing": [
        "5 Ceramic Coating Mistakes That Ruin Your Clear Coat",
        "How To Restore Faded Paint To Showroom Shine",
        "The Scratch-Free Wash Method Top Detailers Swear By",
        "Stop Using Dish Soap: Do This For Deep Paint Polish",
        "Before & After: 10-Year Paint Restoration Blueprint"
    ],
    "hvac": [
        "7 Warning Signs Your AC Compressor Is About To Fail",
        "How To Lower Your Electric Bill By 30% This Summer",
        "Stop Ignoring This Furnace Sound Before It Costs You $5k",
        "The Air Duct Cleaning Secret That Eliminates Dust Fast",
        "5 DIY Maintenance Steps Every Homeowner Needs"
    ],
    "roofing": [
        "5 Hidden Roof Leaks That Destroy Your Home's Value",
        "How To Spot Storm Damage Before Insurance Expiration",
        "Stop Patching Shingles Wrong: Do This Pro Method Instead",
        "The Complete Metal vs Shingle Roof Cost Comparison",
        "7 Critical Roofing Red Flags You Can't Ignore"
    ],
    "plumbing": [
        "5 Main Line Blockage Warning Signs You Must Know",
        "How To Unclog Any Drain Without Harsh Chemicals",
        "Stop Ignoring Rattling Pipes: Do This Fix Immediately",
        "The Water Heater Flush Secret That Doubles Its Lifespan",
        "7 Emergency Plumbing Fixes Every Homeowner Needs"
    ],
    "phonics": [
        "5 Kindergarten Phonics Hacks That Double Reading Speed",
        "The Handwriting Secret Teachers Wish Every Parent Knew",
        "Stop Forcing Sight Words: Do This Phonics Game Instead",
        "How To Build Early Reading Confidence Step-By-Step",
        "The Ultimate CVC Word Practice Blueprint For Kids"
    ],
    "kdp": [
        "5 Low-Content Book Niche Mistakes Killing Your Sales",
        "How To Research High-Demand KDP Keywords In 10 Mins",
        "Stop Designing Generic Covers: Use This High-CTR Layout",
        "The Phonics & Activity Workbook Blueprint For Amazon KDP",
        "7 KDP Listing Optimization Tricks For Instant Sales"
    ],
    "audit": [
        "5 Hidden Processing Fees Sucking Profits From Your Business",
        "How To Renegotiate Your Interchange Rates In 3 Steps",
        "Stop Paying Junk Fees: Audit Your Merchant Statement Now",
        "The Contractor Invoice Mistake Costing You Thousands",
        "Forensic Audit Blueprint: Uncover Overcharges In 10 Mins"
    ]
}

INTENT_TEMPLATES = {
    "inspiration": {
        "hooks": [
            "5 {topic} Secrets That Will Transform Your {niche}",
            "The Ultimate {topic} Blueprint Every Pro Uses",
            "7 Game-Changing {topic} Trends You Need To Try",
            "Stop Guessing: The Complete {niche} Visual Guide",
            "Unbelievable {topic} Results You Have To See"
        ],
        "cta": "Save this Pin for inspiration!"
    },
    "how_to": {
        "hooks": [
            "5 {topic} Mistakes That Are Ruining Your Results",
            "How To Master {topic} Step-By-Step (Without Pain)",
            "The Secret To Perfect {topic} Made Simple",
            "Stop Doing {topic} Wrong: Do This Instead",
            "Beginner's Guide To Professional {topic}"
        ],
        "cta": "Read the full tutorial here!"
    },
    "proof": {
        "hooks": [
            "How We Got Flawless {topic} Results In 30 Days",
            "The Exact System Behind This {niche} Transformation",
            "Why Top Pros Are Switching To This {topic} Method",
            "Real Results: The {niche} Master Blueprint",
            "Before & After: The Ultimate {topic} Restoration"
        ],
        "cta": "Click to see the case study!"
    },
    "product": {
        "hooks": [
            "5 Essential {topic} Tools You Must Have In {year}",
            "Upgrade Your {niche} Routine With This Game-Changer",
            "Why This {topic} Essential Is Going Viral",
            "The Best {niche} Investment You Can Make Today",
            "Handpicked {topic} Picks That Actually Work"
        ],
        "cta": "Shop now before stock runs out!"
    }
}

def generate_via_gemini_flash(topic, niche, gemini_key, intent="how_to", year="2026"):
    if not gemini_key:
        return None

    models_to_try = [
        "models/gemini-3.6-flash",
        "models/gemini-3.5-flash",
        "models/gemini-flash-latest",
        "models/gemini-2.5-flash"
    ]

    prompt_text = f"""
Act as a professional Pinterest Copywriter & SEO Specialist.
Generate a deep, SEO-grounded Pinterest strategy for Topic: '{topic}', Niche: '{niche}'.

Return ONLY a raw valid JSON object with NO markdown formatting:
{{
  "intent_bucket": "{intent}",
  "overlay_hooks": [
    "Hook 1: High curiosity headline",
    "Hook 2: Warning mistake headline",
    "Hook 3: Step-by-step tutorial headline",
    "Hook 4: Before and after transformation headline",
    "Hook 5: Professional guide headline"
  ],
  "seo_title": "{topic} | Ultimate {niche} Guide ({year})",
  "seo_keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5", "keyword6", "keyword7", "keyword8"],
  "hashtags": ["#{niche.lower().replace(' ', '')}", "#{topic.lower().replace(' ', '')}", "#tips", "#guide", "#ideas", "#hacks", "#strategy", "#{year}"],
  "description": "Natural-language 150-word Pinterest description loaded with high-intent keywords and clear CTAs.",
  "cta_text": "Click to Read the Full Guide!",
  "pin_seo_items": [
    {{
      "variant_id": 1,
      "title": "{topic}: Hook 1 SEO Title",
      "description": "Comprehensive description for pin variant 1 with keywords and hashtags.",
      "alt_text": "High-contrast visual pin graphic showing {topic} for {niche}.",
      "keywords": "keyword1, keyword2, keyword3"
    }},
    {{
      "variant_id": 2,
      "title": "{topic}: Hook 2 SEO Title",
      "description": "Comprehensive description for pin variant 2 with keywords and hashtags.",
      "alt_text": "Split screen photo pin showing {topic} for {niche}.",
      "keywords": "keyword2, keyword4, keyword5"
    }},
    {{
      "variant_id": 3,
      "title": "{topic}: Hook 3 SEO Title",
      "description": "Comprehensive description for pin variant 3 with keywords and hashtags.",
      "alt_text": "Translucent card graphic detailing {topic} steps.",
      "keywords": "keyword1, keyword3, keyword6"
    }},
    {{
      "variant_id": 4,
      "title": "{topic}: Hook 4 SEO Title",
      "description": "Comprehensive description for pin variant 4 with keywords and hashtags.",
      "alt_text": "Editorial full bleed pin showcasing {topic} results.",
      "keywords": "keyword4, keyword7, keyword8"
    }},
    {{
      "variant_id": 5,
      "title": "{topic}: Hook 5 SEO Title",
      "description": "Comprehensive description for pin variant 5 with keywords and hashtags.",
      "alt_text": "Professional guide pin for {topic} in {niche}.",
      "keywords": "keyword2, keyword5, keyword8"
    }}
  ]
}}
"""

    for model_path in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/{model_path}:generateContent?key={gemini_key}"
        payload_data = {
            "contents": [{
                "parts": [{"text": prompt_text}]
            }]
        }
        
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload_data).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                res_data = json.loads(resp.read().decode("utf-8"))
                text_out = res_data["candidates"][0]["content"]["parts"][0]["text"].strip()
                if text_out.startswith("```"):
                    text_out = text_out.split("```")[1]
                    if text_out.startswith("json"):
                        text_out = text_out[4:].strip()
                parsed = json.loads(text_out)
                print(f"[StrategyBrain] Successfully generated via Gemini Flash ({model_path})!")
                return parsed
        except Exception as e:
            print(f"[StrategyBrain] Warning for {model_path}: {e}")
            continue

    return None

def analyze_and_generate(topic, niche, intent=None, gemini_key=None, year="2026"):
    gemini_key = gemini_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

    if gemini_key:
        ai_res = generate_via_gemini_flash(topic, niche, gemini_key, intent or "how_to", year)
        if ai_res and len(ai_res.get("overlay_hooks", [])) >= 5:
            niche_clean = niche.title()
            topic_clean = topic.title()
            hashtags = ai_res.get("hashtags", [f"#{niche_clean.replace(' ', '')}", f"#{topic_clean.replace(' ', '')}", "#tips", "#guide"])
            
            seo_title = (ai_res.get("seo_title") or f"{topic_clean} | {niche_clean} Guide ({year})")[:100]
            seo_desc = (ai_res.get("description") or f"Discover top {topic_clean} tips for {niche_clean}.")[:800]
            alt_text = ai_res.get("alt_text") or f"Pin graphic for {topic_clean}: {ai_res['overlay_hooks'][0]}"

            cleaned_items = []
            for item in ai_res.get("pin_seo_items", []):
                cleaned_items.append({
                    "variant_id": item.get("variant_id"),
                    "title": (item.get("title") or seo_title)[:100],
                    "description": (item.get("description") or seo_desc)[:800],
                    "alt_text": item.get("alt_text") or alt_text,
                    "keywords": item.get("keywords", "")
                })

            return {
                "status": "success",
                "ai_engine": "Gemini 3.6 Flash AI",
                "intent_bucket": ai_res.get("intent_bucket", intent or "how_to"),
                "niche": niche_clean,
                "topic": topic_clean,
                "hashtags": hashtags,
                "pin_metadata": {
                    "title": seo_title,
                    "description": seo_desc,
                    "alt_text": alt_text,
                    "cta_text": ai_res.get("cta_text", "Click to Learn More!"),
                    "recommended_board": f"{niche_clean} Ideas & Inspiration"
                },
                "overlay_hooks": ai_res["overlay_hooks"],
                "seo_keywords": ai_res.get("seo_keywords", [niche.lower(), topic.lower()]),
                "pin_seo_items": cleaned_items
            }

    niche_lower = niche.lower().strip()
    topic_lower = topic.lower().strip()

    matched_specialized_hooks = None
    for key, hooks_list in SPECIALIZED_NICHE_HOOKS.items():
        if key in niche_lower or key in topic_lower:
            matched_specialized_hooks = hooks_list
            break

    if not intent or intent not in INTENT_TEMPLATES:
        if any(w in topic_lower for w in ["buy", "shop", "product", "best", "deal", "price"]):
            intent = "product"
        elif any(w in topic_lower for w in ["how", "guide", "steps", "tutorial", "learn"]):
            intent = "how_to"
        elif any(w in topic_lower for w in ["case study", "results", "review", "before after"]):
            intent = "proof"
        else:
            intent = "inspiration"

    template_data = INTENT_TEMPLATES[intent]
    niche_clean = niche.title()
    topic_clean = topic.title()

    if matched_specialized_hooks:
        hooks = matched_specialized_hooks
    else:
        hooks = [h.format(niche=niche_clean, topic=topic_clean, year=year) for h in template_data["hooks"]]
    
    keywords = [
        f"{niche.lower()} tips",
        f"how to {niche.lower()}",
        f"best {topic.lower()} guide",
        f"{niche.lower()} mistakes to avoid",
        f"{topic.lower()} tutorial",
        f"{niche.lower()} ideas",
        f"{topic.lower()} hacks",
        f"professional {niche.lower()}"
    ]
    
    hashtags = [
        f"#{niche_clean.replace(' ', '')}",
        f"#{topic_clean.replace(' ', '')}",
        "#tips",
        "#guide",
        "#ideas",
        "#hacks",
        "#strategy",
        f"#{year}"
    ]
    
    seo_title = f"{hooks[0]} | {niche_clean} Guide ({year})"
    description = (
        f"Looking to improve your {niche.lower()} results? Discover {hooks[0].lower()} and "
        f"practical step-by-step tips for {year}. Learn how to optimize your {topic.lower()} "
        f"strategy easily. {template_data['cta']} " + " ".join(hashtags)
    )

    fallback_pin_seo_items = []
    for idx, hk in enumerate(hooks[:5]):
        fallback_pin_seo_items.append({
            "variant_id": idx + 1,
            "title": f"{hk} | {niche_clean} ({year})",
            "description": f"{hk}. Discover top {niche.lower()} insights, step-by-step techniques, and actionable tips for {year}. " + " ".join(hashtags),
            "alt_text": f"Visual pin graphic showing {topic_clean} with headline: {hk}.",
            "keywords": ", ".join(keywords[:5])
        })

    payload = {
        "status": "success",
        "ai_engine": "PinGenius High-CTR Engine",
        "intent_bucket": intent,
        "niche": niche_clean,
        "topic": topic_clean,
        "hashtags": hashtags,
        "pin_metadata": {
            "title": seo_title,
            "description": description,
            "alt_text": f"Visual pin graphic showing {topic_clean} with headline: {hooks[0]}.",
            "cta_text": template_data["cta"],
            "recommended_board": f"{niche_clean} Ideas & Inspiration"
        },
        "overlay_hooks": hooks,
        "seo_keywords": keywords,
        "pin_seo_items": fallback_pin_seo_items
    }
    return payload

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PinGenius Strategy Brain CLI")
    parser.add_argument("--topic", required=True, help="Target topic")
    parser.add_argument("--niche", required=True, help="Target niche")
    parser.add_argument("--gemini-key", help="Gemini API Key")
    parser.add_argument("--intent", choices=["inspiration", "how_to", "proof", "product"], help="Intent bucket")
    
    args = parser.parse_args()
    result = analyze_and_generate(args.topic, args.niche, args.intent, gemini_key=args.gemini_key)
    print(json.dumps(result, indent=2))
