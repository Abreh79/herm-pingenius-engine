#!/usr/bin/env python3
"""
PinGenius Web UI Dashboard v2.5
FastAPI Server with SQLite Campaign Persistence & Webhook Automation Dispatch
"""

import os
import json
import uvicorn
import urllib.request
from fastapi import FastAPI, Request, Form, Header
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

from pingenius_url_importer import fetch_and_parse_url
from pingenius_batch_engine import generate_batch_bundle, OUTPUT_DIR
from pingenius_trust_shield import generate_dispatch_plan
from pingenius_publisher import publish_pin_to_pinterest
from pingenius_db import (
    init_db,
    create_user,
    validate_key,
    deduct_credits,
    save_campaign,
    get_recent_campaigns
)

app = FastAPI(title="PinGenius Studio")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize SQLite Database
init_db()

# Mount generated image assets static directory & frontend static assets
os.makedirs(OUTPUT_DIR, exist_ok=True)
STATIC_DIR = os.path.join(BASE_DIR, "static")
os.makedirs(STATIC_DIR, exist_ok=True)

app.mount("/dist", StaticFiles(directory=OUTPUT_DIR), name="dist")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PinGenius Studio | On-Demand Pinterest Generator</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            darkMode: 'class',
            theme: {
                extend: {
                    colors: {
                        brand: '#E60023',
                        dark: '#0F172A',
                    }
                }
            }
        }
    </script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Plus Jakarta Sans', sans-serif; }
        .font-mono { font-family: 'JetBrains Mono', monospace; }
    </style>
</head>
<body class="bg-dark text-slate-100 min-h-screen flex flex-col antialiased">

    <!-- Navigation Header -->
    <header class="border-b border-slate-800 bg-slate-900/50 backdrop-blur sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
            <div class="flex items-center space-x-3">
                <div class="w-10 h-10 rounded-xl bg-brand flex items-center justify-center font-bold text-white text-xl shadow-lg shadow-brand/20">
                    P
                </div>
                <div>
                    <h1 class="font-extrabold text-lg tracking-tight">PinGenius <span class="text-xs px-2 py-0.5 rounded bg-brand/10 text-brand border border-brand/20 ml-2">Studio v2.5</span></h1>
                </div>
            </div>

            <!-- Header Controls -->
            <div class="flex items-center space-x-4">
                <!-- API Key Input -->
                <div class="flex items-center space-x-2 bg-slate-950/80 border border-slate-800 px-3 py-1.5 rounded-xl">
                    <span class="text-xs font-bold uppercase text-slate-400">API Key:</span>
                    <input type="text" id="apiKeyInput" value="" placeholder="Enter API Key..." class="bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-amber-400 font-mono w-56 focus:outline-none focus:border-brand">
                    <button onclick="checkAccount()" class="text-xs text-slate-400 hover:text-white underline">Check</button>
                </div>

                <!-- Gemini Flash API Key Field -->
                <div class="flex items-center space-x-2 bg-slate-950/80 border border-slate-800 px-3 py-1.5 rounded-xl">
                    <span class="text-xs font-bold uppercase text-slate-400">Gemini Key (Optional):</span>
                    <input type="password" id="geminiKeyInput" placeholder="AIzaSy... (Unlocks Gemini AI)" class="bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-300 font-mono w-64 focus:outline-none focus:border-brand">
                </div>

                <!-- History Drawer Button -->
                <button onclick="openHistoryDrawer()" class="bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold px-3 py-2 rounded-xl transition flex items-center space-x-2 border border-slate-700">
                    <svg class="w-4 h-4 text-brand" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                    <span>Campaign History</span>
                </button>
            </div>
        </div>
    </header>

    <!-- Main Workspace -->
    <main class="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        <!-- Generator Form Card -->
        <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 sm:p-8 shadow-2xl relative overflow-hidden">
            <div class="max-w-3xl space-y-6">
                <div>
                    <h2 class="text-2xl font-bold tracking-tight">Generate Pinterest Assets</h2>
                    <p class="text-slate-400 text-sm mt-1">Input a URL or enter custom topic details to render high-converting static pins, carousels, kinetic MP4 video, and bulk CSV files.</p>
                </div>

                <form id="genForm" onsubmit="event.preventDefault(); handleGenerate(event);" class="space-y-4">
                    <div>
                        <label class="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">Option A: Auto-Extract from URL</label>
                        <input type="url" id="urlInput" placeholder="https://example.com/landing-page" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-200 focus:outline-none focus:border-brand font-mono">
                    </div>

                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <div>
                            <label class="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">Option B: Topic</label>
                            <input type="text" id="topicInput" placeholder="e.g. Paint Correction Guide" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-200 focus:outline-none focus:border-brand">
                        </div>
                        <div>
                            <label class="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">Niche / Domain</label>
                            <input type="text" id="nicheInput" placeholder="e.g. Auto Detailing" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-200 focus:outline-none focus:border-brand">
                        </div>
                    </div>

                    <div class="pt-2">
                        <button type="submit" id="submitBtn" class="bg-brand hover:bg-brand/90 text-white font-bold text-sm px-6 py-3.5 rounded-xl shadow-lg shadow-brand/20 transition active:scale-95 flex items-center space-x-2">
                            <span>Generate Campaign Artwork & Bulk CSV</span>
                        </button>
                    </div>
                </form>
            </div>
        </div>

        <!-- Output Container -->
        <div id="outputSection" class="hidden space-y-8">
            <!-- Results Header & Action Bar -->
            <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 flex flex-wrap items-center justify-between gap-4">
                <div>
                    <span id="aiBadge" class="text-xs font-bold uppercase tracking-wider px-2.5 py-1 rounded-md bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">AI Engine Ready</span>
                    <h3 id="campaignTitle" class="text-xl font-bold mt-2">Campaign Outputs</h3>
                    <p id="trustShieldStatus" class="text-xs font-mono text-slate-400 mt-1"></p>
                </div>
                <div class="flex items-center space-x-3">
                    <a id="downloadCsvBtn" href="#" class="bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold px-4 py-2.5 rounded-xl border border-slate-700 transition flex items-center space-x-2">
                        <svg class="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
                        <span>Download Pinterest Bulk CSV</span>
                    </a>
                    <a id="downloadZipBtn" href="#" class="bg-brand hover:bg-brand/90 text-white text-xs font-bold px-4 py-2.5 rounded-xl shadow-lg shadow-brand/20 transition flex items-center space-x-2">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
                        <span>Download Complete ZIP Archive</span>
                    </a>
                </div>
            </div>

            <!-- Tab Switcher -->
            <div class="border-b border-slate-800 flex space-x-6">
                <button onclick="switchTab('static')" id="tabStatic" class="pb-3 text-sm font-bold border-b-2 border-brand text-brand transition">Static Pins (5 Variants)</button>
                <button onclick="switchTab('carousel')" id="tabCarousel" class="pb-3 text-sm font-bold border-b-2 border-transparent text-slate-400 hover:text-slate-200 transition">Carousel Story (5 Slides)</button>
                <button onclick="switchTab('video')" id="tabVideo" class="pb-3 text-sm font-bold border-b-2 border-transparent text-slate-400 hover:text-slate-200 transition">Video / Idea Pin (MP4)</button>
            </div>

            <!-- Static Pins Gallery -->
            <div id="galleryStatic" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-6"></div>

            <!-- Carousel Gallery -->
            <div id="galleryCarousel" class="hidden grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-6"></div>

            <!-- Video Pin Tab -->
            <div id="galleryVideo" class="hidden max-w-xl mx-auto bg-slate-900 border border-slate-800 rounded-2xl p-6 text-center space-y-4">
                <div id="videoContainer"></div>
            </div>
        </div>
    </main>

    <!-- History Drawer Modal -->
    <div id="historyModal" class="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 hidden flex justify-end">
        <div class="w-full max-w-md bg-slate-900 h-full border-l border-slate-800 p-6 space-y-6 overflow-y-auto">
            <div class="flex items-center justify-between border-b border-slate-800 pb-4">
                <h3 class="font-bold text-lg">Campaign History</h3>
                <button onclick="closeHistoryDrawer()" class="text-slate-400 hover:text-white font-bold">&times;</button>
            </div>
            <div id="historyList" class="space-y-4"></div>
        </div>
    </div>

    <script src="/static/app.js?v=2.1"></script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def index():
    return HTMLResponse(content=HTML_TEMPLATE, headers={"Cache-Control": "no-cache, no-store, must-revalidate"})

@app.get("/api/account")
def get_account(api_key: str):
    return validate_key(api_key)

@app.get("/api/campaigns")
def get_campaigns():
    campaigns = get_recent_campaigns(limit=15)
    return {"status": "success", "campaigns": campaigns}

@app.post("/api/register")
def register_user(email: str = Form(...), tier: str = Form("free")):
    return create_user(email, tier)

@app.post("/api/dispatch")
async def dispatch_webhook(request: Request):
    body = await request.json()
    webhook_url = body.get("webhook_url")
    campaign_data = body.get("campaign")
    
    if not webhook_url:
        return JSONResponse(status_code=400, content={"status": "error", "message": "Webhook URL is required."})
        
    try:
        req = urllib.request.Request(
            webhook_url,
            data=json.dumps({"event": "pingenius.campaign.published", "data": campaign_data}).encode("utf-8"),
            headers={"Content-Type": "application/json", "User-Agent": "PinGenius-Webhook-Dispatcher/2.0"}
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            return {"status": "success", "message": f"Webhook dispatched successfully. Response code: {resp.status}"}
    except Exception as e:
        return JSONResponse(
            status_code=502,
            content={"status": "error", "message": f"Webhook dispatch failed: {str(e)}"}
        )

@app.post("/api/publish")
async def publish_pin(request: Request):
    token = os.getenv("PINTEREST_ACCESS_TOKEN")
    if not token:
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": "PINTEREST_ACCESS_TOKEN environment variable is not configured."}
        )
    
    body = await request.json()
    board_id = body.get("board_id")
    title = body.get("title", "")
    description = body.get("description", "")
    link_url = body.get("link_url", "")
    image_url = body.get("image_url", "")
    alt_text = body.get("alt_text", "")
    
    if not board_id:
        return JSONResponse(status_code=400, content={"status": "error", "message": "board_id is required."})
    if not image_url:
        return JSONResponse(status_code=400, content={"status": "error", "message": "image_url is required."})
        
    result = publish_pin_to_pinterest(token, board_id, title, description, link_url, image_url, alt_text)
    if result.get("status") == "error":
        return JSONResponse(status_code=400 if result.get("code") else 502, content=result)
    return result

@app.post("/api/generate")
@app.post("/api/generate/")
async def api_generate(request: Request, x_api_key: str = Header(None), x_gemini_api_key: str = Header(None)):
    body = await request.json()
    api_key = x_api_key or body.get("api_key")
    gemini_key = x_gemini_api_key or body.get("gemini_key") or os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        return JSONResponse(status_code=401, content={"status": "error", "message": "API key required."})

    # Validate API Key & Credits
    val = validate_key(api_key)
    if not val.get("valid"):
        return JSONResponse(status_code=401, content={"status": "error", "message": val.get("message", "Invalid API key.")})
        
    url = body.get("url")
    topic = body.get("topic")
    niche = body.get("niche")
    
    brand = "PinGenius.io"
    
    if url:
        parsed = fetch_and_parse_url(url)
        if parsed.get("status") == "success":
            if not topic:
                topic = parsed["inferred_params"]["topic"]
            if not niche:
                niche = parsed["inferred_params"]["niche"]
            if parsed.get("brand_name"):
                brand = f"@{parsed['brand_name']}"
                
    if not topic or not niche:
        return JSONResponse(status_code=400, content={"status": "error", "message": "Specify a URL or topic & niche."})
        
    # Deduct 1 Credit
    deduct = deduct_credits(api_key, 1, topic, niche)
    if deduct["status"] == "error":
        return JSONResponse(status_code=402, content={"status": "error", "message": deduct["message"]})
        
    batch_res = generate_batch_bundle(topic, niche, brand, target_url=url, gemini_key=gemini_key)
    shield_res = generate_dispatch_plan(batch_res["manifest"])
    
    with open(batch_res["manifest"]) as f:
        manifest_data = json.load(f)

    # Persist campaign to SQLite
    campaign_id = save_campaign(
        api_key=api_key,
        topic=topic,
        niche=niche,
        url=url,
        ai_engine=batch_res["ai_engine"],
        zip_path=batch_res["zip_bundle"],
        csv_path=batch_res["bulk_csv"],
        manifest_data=manifest_data
    )

    # Format static pins with public image URLs & direct download URLs
    formatted_pins = []
    for pin in manifest_data.get("static_pin_variants", []):
        filename = os.path.basename(pin["file_path"])
        formatted_pins.append({
            "variant_id": pin.get("variant_id"),
            "hook": pin.get("hook"),
            "theme": pin.get("theme"),
            "layout": pin.get("layout", "standard"),
            "file_path": pin.get("file_path"),
            "image_url": f"/dist/{filename}",
            "download_url": f"/api/download?path={pin.get('file_path')}"
        })

    # Format carousel slides with public image URLs & direct download URLs
    formatted_carousel = []
    for slide in manifest_data.get("carousel_bundle", []):
        filename = os.path.basename(slide["file_path"])
        formatted_carousel.append({
            "slide": slide.get("slide"),
            "hook": slide.get("text", f"Carousel Slide {slide.get('slide')}"),
            "file_path": slide.get("file_path"),
            "image_url": f"/dist/{filename}",
            "download_url": f"/api/download?path={slide.get('file_path')}"
        })
        
    # Format motion video pin if present
    formatted_motion_pin = None
    motion_info = manifest_data.get("motion_pin", {})
    if motion_info and motion_info.get("file_path") and os.path.exists(motion_info["file_path"]):
        filename = os.path.basename(motion_info["file_path"])
        formatted_motion_pin = {
            "title": motion_info.get("title"),
            "description": motion_info.get("description"),
            "file_path": motion_info.get("file_path"),
            "video_url": f"/dist/{filename}",
            "download_url": f"/api/download?path={motion_info.get('file_path')}",
            "link_url": motion_info.get("link_url")
        }

    return {
        "status": "success",
        "campaign_id": campaign_id,
        "credits_remaining": deduct["remaining_credits"],
        "summary": {
            "topic": topic,
            "niche": niche,
            "brand": brand,
            "ai_engine": batch_res["ai_engine"],
            "bundle_zip": batch_res["zip_bundle"],
            "zip_download_url": f"/api/download?path={batch_res['zip_bundle']}",
            "csv_download_url": f"/api/download?path={batch_res['bulk_csv']}"
        },
        "trust_shield_status": shield_res["account_trust_rating"],
        "pins": formatted_pins,
        "carousel": formatted_carousel,
        "motion_pin": formatted_motion_pin
    }

@app.get("/api/download")
def download_file(path: str):
    if not path:
        return JSONResponse(status_code=404, content={"status": "error", "message": "Path required"})
    target_path = os.path.abspath(path)
    output_dir_abs = os.path.abspath(OUTPUT_DIR)
    try:
        common = os.path.commonpath([target_path, output_dir_abs])
    except ValueError:
        common = ""
    if common == output_dir_abs and os.path.exists(target_path) and os.path.isfile(target_path):
        filename = os.path.basename(target_path)
        if target_path.endswith(".mp4"):
            media_type = "video/mp4"
        elif target_path.endswith(".zip"):
            media_type = "application/zip"
        elif target_path.endswith(".csv"):
            media_type = "text/csv"
        else:
            media_type = "image/png"
        return FileResponse(target_path, media_type=media_type, filename=filename)
    return JSONResponse(status_code=404, content={"status": "error", "message": "File not found"})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
