# PinGenius Engine v2.0 (Herm tha Worm Edition)

> **On-Demand Pinterest Campaign Generator, Multi-Layout Canvas Renderer & Automation Dispatch Engine**

PinGenius is a production-grade Pinterest campaign generation suite designed for local trade businesses, KDP authors, and e-commerce brands. It combines Gemini 3.6 Flash AI copy generation, Pillow dynamic visual layout rendering (2:3 aspect ratio), official Pinterest Business Bulk CSV generation, SQLite campaign persistence, and webhook automation dispatches.

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
   - Packaged directly inside the root of exported `.zip` bundles alongside `pin_manifest.json` and rendered PNG assets.

4. **Web UI & Automation Dispatch (`server.py`)**
   - Interactive FastAPI web dashboard on port 8080 with live in-dashboard preview gallery, tabbed navigation (`Static Pins` vs `Carousel Story Pack`), and individual/bulk PNG downloads.
   - **SQLite Campaign Persistence**: Logs all generated campaign runs into `pingenius.db` (`GET /api/campaigns`).
   - **Automation Dispatch**: Webhook integration (`POST /api/dispatch`) to send campaign payloads directly to Zapier, Make, Pabbly, or custom endpoints.

---

## 🚀 Quick Start

### 1. Start the Server
```bash
python3 server.py
```
Server listens on `http://localhost:8080`.

### 2. Generate Campaign via API
```bash
curl -X POST http://localhost:8080/api/generate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: herm_master_key_777" \
  -d '{
    "topic": "Ceramic Coating",
    "niche": "Auto Detailing",
    "url": "https://studio-7106835876-c5253.web.app/mamas-boy-car-detailing.html"
  }'
```

### 3. CLI Usage
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
├── pingenius_db.py             # SQLite Persistence (Users, Credits, Campaigns)
├── pingenius_trust_shield.py   # Anti-Spam Pacing & Hash Shielding
├── pingenius_url_importer.py   # Landing Page Parameter Extractor
└── dist/                       # Output Directory (PNGs, ZIPs, CSVs, Manifests)
```

---

## ⚙️ Environment Variables

- `GEMINI_API_KEY`: Optional Google Gemini API key to activate Gemini 3.6 Flash AI copy generation.
- `HERMES_MODEL`: Default model configuration (`gemini/gemini-3.6-flash`).

---

## 🔒 License & Credits

Built for **Herm tha Worm / Nous Research** • PinGenius v2.0
