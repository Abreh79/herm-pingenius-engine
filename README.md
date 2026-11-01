# PinGenius Engine v2.5 (Herm tha Worm Edition)

> **On-Demand Pinterest Campaign Generator, Multi-Layout Canvas Renderer & Automation Dispatch Engine**

PinGenius is a production-grade Pinterest campaign generation suite designed for local trade businesses, KDP authors, and e-commerce brands. It combines Gemini 3.6 Flash AI copy generation, Pillow dynamic visual layout rendering (2:3 aspect ratio), FFmpeg kinetic motion video pins, official Pinterest Business Bulk CSV generation, SQLite campaign persistence, and webhook automation dispatches.

---

## 🌟 Key Features

1. **Gemini 3.6 Flash AI Strategy Brain (`pingenius_strategy_brain.py`)**
   - Generates high-intent, curiosity-driven Pinterest hooks, SEO titles, natural-language descriptions, image alt-text, and 8–10 trending hashtags per campaign.
   - Built-in fallback rule engine for specialized local service niches (Auto Detailing, HVAC, Roofing, Plumbing, Phonics/KDP, Merchant Auditing).

2. **Multi-Layout Canvas Engine (`pingenius_canvas_engine.py`)**
   - Renders 1000x1500 (2:3 aspect ratio) HD Pinterest visual assets across 3 distinct visual layout archetypes:
     - **Layout A (Full-Bleed Editorial)**: Unobstructed upper 60% with heavy lower dark gradient vignette (`rgba(0,0,0,0.75)`).
     - **Layout B (Split-Screen Modern)**: Top 52% smart center-cropped photo frame + bottom 48% editorial block.
     - **Layout C (Frosted Minimalist Card)**: Translucent glassmorphic card container with 75% opacity and crisp drop shadow.
   - **Dynamic Color Harmonization**: Uses Pillow color quantization to extract the dominant vibrant accent color directly from fetched Unsplash stock background images.

3. **Official Pinterest Bulk CSV Export (`pingenius_batch_engine.py`)**
   - Compiles `pinterest_bulk_create.csv` formatted according to official Pinterest Business bulk upload standards (`Title`, `Description`, `Media File Name`, `Link URL`, `Keywords`).
   - Packaged directly inside the root of exported `.zip` bundles alongside `pin_manifest.json` and rendered PNG/MP4 assets.

4. **FFmpeg Kinetic Motion Video Pins (`pingenius_motion_engine.py`)**
   - Compiles 5-slide carousel bundles into a 10-second vertical 1080x1920 MP4 video pin with progressive accent motion bars.

5. **Web UI & Automation Dispatch (`server.py`)**
   - Interactive FastAPI web dashboard on port 8080 with live in-dashboard preview gallery, tabbed navigation (`Static Pins`, `Carousel Story Pack`, `Video Pin MP4`), and individual/bulk PNG/MP4 downloads.
   - **SQLite Campaign Persistence**: Logs all generated campaign runs into `pingenius.db` (`GET /api/campaigns`).
   - **Automation Dispatch**: Webhook integration (`POST /api/dispatch`) to send campaign payloads directly to Zapier, Make, Pabbly, or custom endpoints.
   - **Direct Pinterest API v5 Publisher**: Endpoint (`POST /api/publish`) to publish pins directly to official Pinterest boards using `PINTEREST_ACCESS_TOKEN`. Note: Pinterest API requires a publicly reachable image URL, so direct publishing works when the server is publicly accessible.

---

## 🚀 Quick Start

### 1. System Prerequisites
PinGenius requires system **FFmpeg** installed for kinetic video pin rendering:
```bash
# Ubuntu / Debian
sudo apt update && sudo apt install -y ffmpeg

# macOS
brew install ffmpeg
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Start the Server
```bash
python3 server.py
```
Server listens on `http://localhost:8080`.

### 4. Generate Campaign via API
```bash
curl -X POST http://localhost:8080/api/generate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{
    "topic": "Ceramic Coating",
    "niche": "Auto Detailing",
    "url": "https://studio-7106835876-c5253.web.app/mamas-boy-car-detailing.html"
  }'
```

### 5. CLI Usage
```bash
python3 pingenius.py --topic "Ceramic Coating" --niche "Auto Detailing" --brand "Mama's Boy Detailing"
```

---

## 📂 Project Architecture

```
herm_pingenius_engine/
├── server.py                   # FastAPI Server, Web Dashboard & Endpoints
├── pingenius.py                # Master Orchestrator CLI
├── pingenius_strategy_brain.py  # Gemini Flash AI Strategy Engine & SEO Prompts
├── pingenius_canvas_engine.py  # 2:3 Canvas Renderer (3 Layouts, Color Sampling)
├── pingenius_batch_engine.py   # Multi-Format Batch Bundler & Bulk CSV Exporter
├── pingenius_motion_engine.py  # FFmpeg Kinetic Motion MP4 Generator
├── pingenius_publisher.py      # Pinterest API v5 Publisher
├── pingenius_db.py             # SQLite Persistence (Users, Credits, Campaigns)
├── pingenius_trust_shield.py   # Anti-Spam Pacing & Hash Shielding
├── pingenius_url_importer.py   # Landing Page Parameter Extractor
├── requirements.txt            # Python Dependencies
└── dist/                       # Output Directory (PNGs, MP4s, ZIPs, CSVs, Manifests)
```

---

## ⚙️ Environment Variables

Configure environment variables in `.env`:

- `MASTER_API_KEY`: Master API key for administrative access and unlimited generation.
- `GEMINI_API_KEY`: Google Gemini API key to activate Gemini 3.6 Flash AI copy generation.
- `PINTEREST_ACCESS_TOKEN`: Official Pinterest API v5 access token for direct pin publishing (`POST /api/publish`).

---

## 🔒 License & Credits

Built for **Herm tha Worm / Nous Research** • PinGenius v2.5
