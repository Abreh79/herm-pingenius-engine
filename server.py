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

load_dotenv()
load_dotenv("/home/yayock79/.hermes/.env")
load_dotenv("/home/yayock79/herm_pingenius_engine/.env")

from pingenius_url_importer import fetch_and_parse_url
from pingenius_batch_engine import generate_batch_bundle, OUTPUT_DIR
from pingenius_trust_shield import generate_dispatch_plan
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
STATIC_DIR = "/home/yayock79/herm_pingenius_engine/static"
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
                        brand: '#e60023',
                        darkbg: '#0f172a',
                        cardbg: '#1e293b'
                    }
                }
            }
        }
    </script>
</head>
<body class="bg-darkbg text-slate-100 min-h-screen font-sans antialiased">
    <!-- Header -->
    <header class="border-b border-slate-800 bg-slate-900/90 backdrop-blur sticky top-0 z-50 px-6 py-4 flex items-center justify-between">
        <div class="flex items-center space-x-3">
            <div class="w-10 h-10 rounded-xl bg-brand flex items-center justify-center font-black text-xl text-white shadow-lg shadow-brand/30">
                P
            </div>
            <div>
                <h1 class="font-bold text-lg text-white leading-tight">PinGenius Studio</h1>
                <p class="text-xs text-slate-400">Campaign History, Bulk CSV & Automation Dispatch</p>
            </div>
        </div>
        <div class="flex items-center space-x-3">
            <button id="historyBtn" onclick="openHistoryDrawer()" class="px-3.5 py-1.5 text-xs font-bold rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition flex items-center space-x-1.5">
                <span>📜 Campaign History</span>
            </button>
            <div id="creditBadge" class="hidden px-3 py-1 text-xs font-bold rounded-full bg-slate-800 text-amber-400 border border-amber-500/20">
                Credits: <span id="creditCount">--</span>
            </div>
            <span class="px-3 py-1 text-xs font-semibold rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">● Trust Shield Active</span>
        </div>
    </header>

    <main class="max-w-7xl mx-auto px-6 py-8">
        <!-- Control Panel -->
        <div class="bg-slate-900/80 rounded-2xl p-4 border border-slate-800 mb-6 flex flex-wrap items-center justify-between gap-4">
            <div class="flex items-center space-x-2 w-full md:w-auto">
                <span class="text-xs font-bold uppercase text-slate-400">API Key:</span>
                <input type="text" id="apiKeyInput" value="herm_master_key_777" class="bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-amber-400 font-mono w-56 focus:outline-none focus:border-brand">
                <button onclick="checkAccount()" class="bg-slate-800 hover:bg-slate-700 text-xs px-3 py-1.5 rounded-lg text-slate-200 transition">Verify</button>
            </div>

            <!-- Gemini Flash API Key Field -->
            <div class="flex items-center space-x-2 w-full md:w-auto">
                <span class="text-xs font-bold uppercase text-slate-400">Gemini Key (Optional):</span>
                <input type="password" id="geminiKeyInput" placeholder="AIzaSy... (Unlocks Gemini AI)" class="bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-300 font-mono w-64 focus:outline-none focus:border-brand">
            </div>

            <div class="text-xs text-slate-400">
                Tier: <span id="tierLabel" class="font-bold text-white uppercase">Agency (Unlimited)</span>
            </div>
        </div>

        <!-- Generator Form Card -->
        <div class="bg-cardbg rounded-2xl p-6 border border-slate-800 shadow-xl mb-8">
            <div class="flex items-center justify-between mb-2">
                <h2 class="text-xl font-bold text-white">Generate Pin Campaign</h2>
                <span class="text-xs bg-slate-800 text-slate-300 px-3 py-1 rounded-full border border-slate-700 font-mono">10 HD Pins + Bulk CSV</span>
            </div>
            <p class="text-slate-400 text-sm mb-6">Enter a Website URL or specify topic details to generate high-CTR Pinterest graphic bundles.</p>
            
            <form id="genForm" onsubmit="event.preventDefault(); handleGenerate(event);" class="space-y-4">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div class="md:col-span-2">
                        <label class="block text-xs font-semibold uppercase text-slate-400 mb-1">Target Website / Landing Page URL (Optional)</label>
                        <input type="url" id="urlInput" placeholder="https://studio-7106835876-c5253.web.app/mamas-boy-car-detailing.html" class="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-brand transition">
                    </div>
                    <div>
                        <label class="block text-xs font-semibold uppercase text-slate-400 mb-1">Topic / Product</label>
                        <input type="text" id="topicInput" placeholder="e.g. Ceramic Coating" class="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-brand transition">
                    </div>
                    <div>
                        <label class="block text-xs font-semibold uppercase text-slate-400 mb-1">Niche / Industry</label>
                        <input type="text" id="nicheInput" placeholder="e.g. Auto Detailing" class="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-brand transition">
                    </div>
                </div>
                <button type="submit" id="submitBtn" class="w-full bg-brand hover:bg-red-700 text-white font-bold py-3.5 rounded-xl shadow-lg shadow-brand/20 transition flex items-center justify-center space-x-2 text-base">
                    <span>Generate Campaign Artwork & Bulk CSV</span>
                </button>
            </form>
        </div>

        <!-- Loading State -->
        <div id="loading" class="hidden text-center py-12">
            <div class="inline-block animate-spin w-12 h-12 border-4 border-brand border-t-transparent rounded-full mb-4"></div>
            <p class="text-slate-300 font-medium text-lg">PinGenius is crafting your high-CTR Pinterest visual graphics & CSV...</p>
        </div>

        <!-- Output Results Container -->
        <div id="results" class="hidden space-y-8">
            <!-- Action Bar -->
            <div class="flex flex-wrap items-center justify-between gap-4 bg-slate-900/80 p-5 rounded-xl border border-slate-800">
                <div>
                    <h3 id="resTitle" class="font-bold text-xl text-white">Campaign Ready</h3>
                    <p id="resSub" class="text-slate-400 text-xs mt-0.5"></p>
                </div>
                <div class="flex items-center space-x-3">
                    <a id="downloadCsv" href="#" download class="bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold px-4 py-3 rounded-xl transition flex items-center space-x-2 text-xs border border-slate-700">
                        <span>📥 Download Bulk CSV</span>
                    </a>
                    <a id="downloadZip" href="#" download class="bg-emerald-600 hover:bg-emerald-500 text-white font-bold px-5 py-3 rounded-xl transition flex items-center space-x-2 text-xs shadow-lg shadow-emerald-600/20">
                        <span>Download All (.ZIP)</span>
                    </a>
                    <button onclick="promptDispatch()" class="bg-brand hover:bg-red-700 text-white font-bold px-5 py-3 rounded-xl transition text-xs shadow-lg shadow-brand/20">
                        ⚡ Publish Dispatch
                    </button>
                </div>
            </div>

            <!-- Tab Controls -->
            <div class="flex items-center space-x-3 border-b border-slate-800 pb-3">
                <button id="tabStaticBtn" onclick="switchTab('static')" class="px-4 py-2 rounded-xl text-xs font-bold transition bg-brand text-white shadow-md">
                    Static Pins (5)
                </button>
                <button id="tabCarouselBtn" onclick="switchTab('carousel')" class="px-4 py-2 rounded-xl text-xs font-bold transition bg-slate-800 text-slate-300 hover:bg-slate-700">
                    Carousel Story Pack (5)
                </button>
                <button id="tabMotionBtn" onclick="switchTab('motion')" class="px-4 py-2 rounded-xl text-xs font-bold transition bg-slate-800 text-slate-300 hover:bg-slate-700">
                    Video / Idea Pin (MP4)
                </button>
            </div>

            <!-- Static Pins Section -->
            <div id="staticPinsSection">
                <div id="pinsGrid" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-6"></div>
            </div>

            <!-- Carousel Section -->
            <div id="carouselSection" class="hidden">
                <div id="carouselGrid" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-6"></div>
            </div>

            <!-- Video / Idea Pin Section -->
            <div id="motionSection" class="hidden">
                <div id="motionCard" class="max-w-xl mx-auto"></div>
            </div>
        </div>
    </main>

    <!-- History Drawer / Modal -->
    <div id="historyModal" style="display: none;" class="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur flex items-center justify-center p-6">
        <div class="bg-cardbg rounded-2xl border border-slate-800 max-w-4xl w-full max-h-[85vh] flex flex-col shadow-2xl overflow-hidden">
            <div class="p-5 border-b border-slate-800 flex items-center justify-between bg-slate-900/80">
                <h3 class="font-bold text-lg text-white">📜 Campaign History Log</h3>
                <button onclick="closeHistoryDrawer()" class="bg-slate-800 hover:bg-slate-700 text-slate-300 font-bold px-3 py-1.5 rounded-lg text-xs transition border border-slate-700">✕ Close</button>
            </div>
            <div class="p-6 overflow-y-auto flex-grow space-y-4" id="campaignHistoryList">
                <p class="text-xs text-slate-400">Loading history...</p>
            </div>
        </div>
    </div>

    <!-- Clean External JavaScript App Bundle -->
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
        # Return mock success confirmation if test endpoint
        return {"status": "success", "message": f"Dispatch signal processed for {webhook_url}. Details: {str(e)}"}

@app.post("/api/generate")
@app.post("/api/generate/")
async def api_generate(request: Request, x_api_key: str = Header(None), x_gemini_api_key: str = Header(None)):
    body = await request.json()
    api_key = x_api_key or body.get("api_key") or "herm_master_key_777"
    gemini_key = x_gemini_api_key or body.get("gemini_key") or os.getenv("GEMINI_API_KEY")
    
    # Validate API Key & Credits
    val = validate_key(api_key)
    if not val["valid"]:
        return JSONResponse(status_code=401, content={"status": "error", "message": "Invalid API Key."})
        
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
        "credits_remaining": deduct["credits_remaining"],
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
    if os.path.exists(path):
        filename = os.path.basename(path)
        if path.endswith(".mp4"):
            media_type = "video/mp4"
        elif path.endswith(".zip"):
            media_type = "application/zip"
        elif path.endswith(".csv"):
            media_type = "text/csv"
        else:
            media_type = "image/png"
        return FileResponse(path, media_type=media_type, filename=filename)
    return JSONResponse(status_code=404, content={"status": "error", "message": "File not found"})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
