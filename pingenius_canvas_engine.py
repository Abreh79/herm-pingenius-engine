#!/usr/bin/env python3
"""
PinGenius - Phase 2: Canvas Rendering Engine v2.1
Refined Typography, Unobstructed Vehicle Framing & Smart Center-Crop
"""

import argparse
import io
import json
import os
import urllib.request
from PIL import Image, ImageDraw, ImageFont, ImageOps

# Canvas Dimensions
WIDTH = 1000
HEIGHT = 1500

CURATED_STOCK_MAP = {
    "auto detailing": "https://images.unsplash.com/photo-1605559424843-9e4c228bf1c2?w=1000&q=80",
    "car detailing": "https://images.unsplash.com/photo-1605559424843-9e4c228bf1c2?w=1000&q=80",
    "ceramic coating": "https://images.unsplash.com/photo-1520340356584-f9917d1eea6f?w=1000&q=80",
    "hvac": "https://images.unsplash.com/photo-1621905251189-08b45d6a269e?w=1000&q=80",
    "roofing": "https://images.unsplash.com/photo-1590069261209-f8e9b8642343?w=1000&q=80",
    "plumbing": "https://images.unsplash.com/photo-1585704032915-c3400ca199e7?w=1000&q=80",
    "phonics": "https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=1000&q=80",
    "kdp": "https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=1000&q=80",
    "finance": "https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?w=1000&q=80",
    "audit": "https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?w=1000&q=80",
    "real estate": "https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=1000&q=80"
}

THEMES = {
    "dark_bold": {
        "bg_color": (15, 23, 42),
        "card_color": (30, 41, 59, 225),
        "default_accent": (230, 0, 35),    # Pinterest Red
        "text_main": (255, 255, 255),
        "text_sub": (203, 213, 225),
        "button_text": (255, 255, 255)
    },
    "clean_light": {
        "bg_color": (248, 250, 252),
        "card_color": (255, 255, 255, 235),
        "default_accent": (15, 118, 110),  # Deep Teal
        "text_main": (15, 23, 42),
        "text_sub": (71, 85, 105),
        "button_text": (255, 255, 255)
    },
    "vibrant_gold": {
        "bg_color": (15, 23, 42),
        "card_color": (30, 41, 59, 225),
        "default_accent": (245, 158, 11),  # Warm Amber
        "text_main": (255, 255, 255),
        "text_sub": (203, 213, 225),
        "button_text": (15, 23, 42)
    }
}

def get_font(size, is_bold=False):
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if is_bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if is_bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf" if is_bold else "/usr/share/fonts/truetype/freefont/FreeSans.ttf"
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    return ImageFont.load_default()

def extract_dominant_accent(img, default_accent=(230, 0, 35)):
    """Sample the dominant vibrant color from background image using Pillow color quantization."""
    try:
        small_img = img.resize((60, 60))
        quantized = small_img.quantize(colors=12)
        palette = quantized.getpalette()
        colors = quantized.getcolors()
        if not colors or not palette:
            return default_accent
        
        colors.sort(key=lambda x: x[0], reverse=True)
        for count, idx in colors:
            r = palette[idx * 3]
            g = palette[idx * 3 + 1]
            b = palette[idx * 3 + 2]
            brightness = (r * 299 + g * 587 + b * 114) / 1000
            if 40 < brightness < 220:
                max_c = max(r, g, b)
                min_c = min(r, g, b)
                if (max_c - min_c) > 25:
                    return (r, g, b)
        return default_accent
    except Exception:
        return default_accent

def fetch_background_image(niche, theme_bg_color):
    niche_lower = niche.lower().strip()
    stock_url = None
    for key, url in CURATED_STOCK_MAP.items():
        if key in niche_lower:
            stock_url = url
            break

    if not stock_url:
        stock_url = "https://picsum.photos/1000/1500"

    try:
        req = urllib.request.Request(stock_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=4) as resp:
            raw_data = resp.read()
            img = Image.open(io.BytesIO(raw_data)).convert("RGB")
            # Smart center-fit with centering=(0.5, 0.5)
            img = ImageOps.fit(img, (WIDTH, HEIGHT), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
            return img
    except Exception:
        return Image.new("RGB", (WIDTH, HEIGHT), theme_bg_color)

def draw_lower_gradient_vignette(width, height):
    """Layout A Vignette: Heavy dark gradient (rgba 0,0,0,0.75+) anchored to lower 35%, upper 60% clear."""
    vignette = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(vignette)
    for y in range(height):
        if y < 140:
            alpha = int(160 * (1.0 - (y / 140.0)))
        elif y >= 900:
            # Lower 35% gradient (y=900 to 1500)
            progress = (y - 900.0) / (height - 900.0)
            alpha = int(190 + (50 * progress)) # 190 to 240 alpha (rgba 0,0,0,0.75 to 0.95)
        else:
            alpha = 0 # Upper 60% unobstructed
        draw.line([(0, y), (width, y)], fill=(0, 0, 0, alpha))
    return vignette

def wrap_text(text, font, max_width, draw):
    words = text.split()
    lines = []
    current_line = []
    
    for word in words:
        current_line.append(word)
        test_str = " ".join(current_line)
        bbox = draw.textbbox((0, 0), test_str, font=font)
        w = bbox[2] - bbox[0]
        if w > max_width and len(current_line) > 1:
            current_line.pop()
            lines.append(" ".join(current_line))
            current_line = [word]
            
    if current_line:
        lines.append(" ".join(current_line))
    return lines

def generate_pin_canvas(
    hook_text,
    niche,
    cta_text,
    brand_name="PinGenius.io",
    theme_name="dark_bold",
    layout_type="frosted_card",
    progress_badge=None,
    output_path="pin_output.png"
):
    theme = THEMES.get(theme_name, THEMES["dark_bold"])
    
    # 1. Fetch Background & Sample Accent Color
    raw_bg = fetch_background_image(niche, theme["bg_color"])
    accent_color = extract_dominant_accent(raw_bg, theme["default_accent"])
    
    badge_label = progress_badge if progress_badge else f"{niche.upper()} TIPS"
    
    if layout_type == "editorial_vignette":
        # =========================================================
        # LAYOUT A: FULL-BLEED EDITORIAL VIGNETTE (Unobstructed Upper 60%)
        # =========================================================
        base_img = raw_bg.convert("RGBA")
        vignette = draw_lower_gradient_vignette(WIDTH, HEIGHT)
        base_img = Image.alpha_composite(base_img, vignette)
        
        draw_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        draw = ImageDraw.Draw(draw_layer)
        
        # High-Contrast Top Pill Badge
        badge_font = get_font(28, is_bold=True)
        badge_bbox = draw.textbbox((0, 0), badge_label, font=badge_font)
        bw, bh = badge_bbox[2] - badge_bbox[0], badge_bbox[3] - badge_bbox[1]
        bp = 20
        bx1 = (WIDTH - bw) // 2 - bp
        by1 = 55
        bx2 = (WIDTH + bw) // 2 + bp
        by2 = by1 + bh + bp
        
        draw.rounded_rectangle([bx1, by1, bx2, by2], radius=24, fill=(15, 23, 42, 235), outline=accent_color + (255,), width=2)
        draw.text(((WIDTH - bw) // 2, by1 + bp // 2), badge_label, fill=accent_color + (255,), font=badge_font)
        
        # Headline Typography anchored to lower 35% (y = 975..1280)
        hook_font = get_font(52, is_bold=True)
        lines = wrap_text(hook_text, hook_font, WIDTH - 120, draw)
        line_height = 70
        total_h = len(lines) * line_height
        start_y = 975 + ((260 - total_h) // 2)
        
        for i, line in enumerate(lines):
            l_bbox = draw.textbbox((0, 0), line, font=hook_font)
            lw = l_bbox[2] - l_bbox[0]
            lx = (WIDTH - lw) // 2
            ly = start_y + (i * line_height)
            # High-contrast drop shadow
            draw.text((lx + 3, ly + 3), line, fill=(0, 0, 0, 240), font=hook_font)
            draw.text((lx, ly), line, fill=(255, 255, 255, 255), font=hook_font)
            
        # Lower CTA Pill Button
        cta_font = get_font(32, is_bold=True)
        c_bbox = draw.textbbox((0, 0), cta_text, font=cta_font)
        cw, ch = c_bbox[2] - c_bbox[0], c_bbox[3] - c_bbox[1]
        cpx, cpy = 40, 16
        cx1 = (WIDTH - cw) // 2 - cpx
        cy1 = 1300
        cx2 = (WIDTH + cw) // 2 + cpx
        cy2 = cy1 + ch + (cpy * 2)
        
        draw.rounded_rectangle([cx1, cy1, cx2, cy2], radius=40, fill=accent_color + (255,))
        draw.text(((WIDTH - cw) // 2, cy1 + cpy), cta_text, fill=(255, 255, 255), font=cta_font)
        
        # Watermark
        brand_font = get_font(26, is_bold=False)
        brand_bbox = draw.textbbox((0, 0), brand_name, font=brand_font)
        brw = brand_bbox[2] - brand_bbox[0]
        draw.text(((WIDTH - brw) // 2, 1425), brand_name, fill=(203, 213, 225, 255), font=brand_font)
        
        final_img = Image.alpha_composite(base_img, draw_layer).convert("RGB")

    elif layout_type == "split_screen":
        # =========================================================
        # LAYOUT B: SPLIT-SCREEN MODERN (Smart Center-Cropped Photo Frame)
        # =========================================================
        split_y = 780
        # Smart center-crop top 52% image box
        photo_frame = ImageOps.fit(raw_bg, (WIDTH, split_y), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
        
        base_img = Image.new("RGBA", (WIDTH, HEIGHT), (15, 23, 42, 255))
        base_img.paste(photo_frame, (0, 0))
        
        draw_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        draw = ImageDraw.Draw(draw_layer)
        
        # Divider Line
        draw.rectangle([0, split_y - 6, WIDTH, split_y], fill=accent_color + (255,))
        
        # Category / Progress Badge inside top photo frame
        badge_font = get_font(28, is_bold=True)
        badge_bbox = draw.textbbox((0, 0), badge_label, font=badge_font)
        bw, bh = badge_bbox[2] - badge_bbox[0], badge_bbox[3] - badge_bbox[1]
        bp = 20
        bx1 = (WIDTH - bw) // 2 - bp
        by1 = 50
        bx2 = (WIDTH + bw) // 2 + bp
        by2 = by1 + bh + bp
        
        draw.rounded_rectangle([bx1, by1, bx2, by2], radius=24, fill=(15, 23, 42, 235), outline=accent_color + (255,), width=2)
        draw.text(((WIDTH - bw) // 2, by1 + bp // 2), badge_label, fill=accent_color + (255,), font=badge_font)
        
        # Bottom Container Editorial Typography
        hook_font = get_font(58, is_bold=True)
        lines = wrap_text(hook_text, hook_font, WIDTH - 100, draw)
        line_height = 76
        total_h = len(lines) * line_height
        start_y = split_y + 40 + ((440 - total_h) // 2)
        
        for i, line in enumerate(lines):
            l_bbox = draw.textbbox((0, 0), line, font=hook_font)
            lw = l_bbox[2] - l_bbox[0]
            lx = (WIDTH - lw) // 2
            ly = start_y + (i * line_height)
            draw.text((lx, ly), line, fill=(255, 255, 255, 255), font=hook_font)
            
        # Bottom CTA Pill
        cta_font = get_font(32, is_bold=True)
        c_bbox = draw.textbbox((0, 0), cta_text, font=cta_font)
        cw, ch = c_bbox[2] - c_bbox[0], c_bbox[3] - c_bbox[1]
        cpx, cpy = 40, 16
        cx1 = (WIDTH - cw) // 2 - cpx
        cy1 = 1300
        cx2 = (WIDTH + cw) // 2 + cpx
        cy2 = cy1 + ch + (cpy * 2)
        
        draw.rounded_rectangle([cx1, cy1, cx2, cy2], radius=40, fill=accent_color + (255,))
        draw.text(((WIDTH - cw) // 2, cy1 + cpy), cta_text, fill=(255, 255, 255), font=cta_font)
        
        # Watermark
        brand_font = get_font(26, is_bold=False)
        brand_bbox = draw.textbbox((0, 0), brand_name, font=brand_font)
        brw = brand_bbox[2] - brand_bbox[0]
        draw.text(((WIDTH - brw) // 2, 1425), brand_name, fill=(148, 163, 184, 255), font=brand_font)
        
        final_img = Image.alpha_composite(base_img, draw_layer).convert("RGB")

    else:
        # =========================================================
        # LAYOUT C: FROSTED MINIMALIST CARD (DEFAULT)
        # =========================================================
        base_img = raw_bg.convert("RGBA")
        overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 100))
        base_img = Image.alpha_composite(base_img, overlay)
        
        draw_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        draw = ImageDraw.Draw(draw_layer)
        
        # Top Accent Header
        draw.rectangle([0, 0, WIDTH, 16], fill=accent_color + (255,))
        
        # Category / Progress Badge
        badge_font = get_font(28, is_bold=True)
        badge_bbox = draw.textbbox((0, 0), badge_label, font=badge_font)
        bw, bh = badge_bbox[2] - badge_bbox[0], badge_bbox[3] - badge_bbox[1]
        bp = 20
        bx1 = (WIDTH - bw) // 2 - bp
        by1 = 65
        bx2 = (WIDTH + bw) // 2 + bp
        by2 = by1 + bh + bp
        
        draw.rounded_rectangle([bx1, by1, bx2, by2], radius=24, fill=(15, 23, 42, 235), outline=accent_color + (255,), width=2)
        draw.text(((WIDTH - bw) // 2, by1 + bp // 2), badge_label, fill=accent_color + (255,), font=badge_font)
        
        # Translucent Container Card
        card_margin = 55
        card_top = 190
        card_bottom = 1180
        
        draw.rounded_rectangle([card_margin, card_top, WIDTH - card_margin, card_bottom], radius=28, fill=(30, 41, 59, 195), outline=accent_color + (200,), width=2)
        draw.line([card_margin + 50, card_top + 36, WIDTH - card_margin - 50, card_top + 36], fill=accent_color + (255,), width=4)

        # Headline Typography inside Card
        hook_font = get_font(60, is_bold=True)
        max_text_w = WIDTH - (card_margin * 2) - 80
        lines = wrap_text(hook_text, hook_font, max_text_w, draw)
        
        line_height = 78
        total_h = len(lines) * line_height
        start_y = card_top + 90 + ((card_bottom - card_top - 220 - total_h) // 2)
        
        for i, line in enumerate(lines):
            l_bbox = draw.textbbox((0, 0), line, font=hook_font)
            lw = l_bbox[2] - l_bbox[0]
            lx = (WIDTH - lw) // 2
            ly = start_y + (i * line_height)
            draw.text((lx, ly), line, fill=theme["text_main"] + (255,), font=hook_font)

        # Bottom Conversion CTA Pill
        cta_font = get_font(32, is_bold=True)
        c_bbox = draw.textbbox((0, 0), cta_text, font=cta_font)
        cw, ch = c_bbox[2] - c_bbox[0], c_bbox[3] - c_bbox[1]
        cpx, cpy = 40, 16
        cx1 = (WIDTH - cw) // 2 - cpx
        cy1 = card_bottom - 110
        cx2 = (WIDTH + cw) // 2 + cpx
        cy2 = cy1 + ch + (cpy * 2)
        
        draw.rounded_rectangle([cx1, cy1, cx2, cy2], radius=40, fill=accent_color + (255,))
        draw.text(((WIDTH - cw) // 2, cy1 + cpy), cta_text, fill=(255, 255, 255), font=cta_font)

        # Watermark
        brand_font = get_font(28, is_bold=False)
        brand_bbox = draw.textbbox((0, 0), brand_name, font=brand_font)
        brw = brand_bbox[2] - brand_bbox[0]
        draw.text(((WIDTH - brw) // 2, 1390), brand_name, fill=theme["text_sub"] + (255,), font=brand_font)

        final_img = Image.alpha_composite(base_img, draw_layer).convert("RGB")

    final_img.save(output_path, "PNG")
    return output_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PinGenius Canvas Renderer")
    parser.add_argument("--hook", required=True, help="Main title text")
    parser.add_argument("--niche", required=True, help="Niche badge text")
    parser.add_argument("--cta", default="Click to Learn More!", help="CTA button text")
    parser.add_argument("--brand", default="PinGenius.io", help="Brand watermark")
    parser.add_argument("--theme", choices=["dark_bold", "clean_light", "vibrant_gold"], default="dark_bold")
    parser.add_argument("--layout", choices=["editorial_vignette", "split_screen", "frosted_card"], default="frosted_card")
    parser.add_argument("--output", default="pin_output.png")
    
    args = parser.parse_args()
    out = generate_pin_canvas(
        hook_text=args.hook,
        niche=args.niche,
        cta_text=args.cta,
        brand_name=args.brand,
        theme_name=args.theme,
        layout_type=args.layout,
        output_path=args.output
    )
    print(json.dumps({"status": "success", "pin_path": out, "dimensions": f"{WIDTH}x{HEIGHT}"}))
