#!/usr/bin/env python3
"""
PinGenius Database & Campaign Persistence Layer
SQLite storage for user keys, tiered credit metering, and campaign history
"""

import json
import sqlite3
import time

DB_PATH = "/home/yayock79/herm_pingenius_engine/pingenius.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Users & API Keys Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        api_key TEXT UNIQUE NOT NULL,
        tier TEXT NOT NULL DEFAULT 'free',
        credits INTEGER NOT NULL DEFAULT 10,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Usage Metering Logs Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usage_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        topic TEXT NOT NULL,
        niche TEXT NOT NULL,
        pins_generated INTEGER NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """)

    # Campaign History Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS campaigns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        api_key TEXT,
        topic TEXT NOT NULL,
        niche TEXT NOT NULL,
        url TEXT,
        ai_engine TEXT,
        zip_path TEXT,
        csv_path TEXT,
        manifest_json TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Seed Master Admin Key if not present
    cursor.execute("SELECT COUNT(*) FROM users WHERE api_key = 'herm_master_key_777'")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO users (email, api_key, tier, credits) VALUES (?, ?, ?, ?)",
            ("admin@pingenius.io", "herm_master_key_777", "agency", 999999)
        )
        
    conn.commit()
    conn.close()

def validate_key(api_key):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, tier, credits FROM users WHERE api_key = ?", (api_key,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            "valid": True,
            "user_id": row[0],
            "email": row[1],
            "tier": row[2],
            "credits": row[3]
        }
    return {"valid": False, "message": "Invalid API key"}

def create_user(email, tier="free"):
    credits_map = {"free": 10, "pro": 100, "agency": 999999}
    credits = credits_map.get(tier, 10)
    api_key = f"pg_{tier}_{int(time.time())}"
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (email, api_key, tier, credits) VALUES (?, ?, ?, ?)",
            (email, api_key, tier, credits)
        )
        conn.commit()
        conn.close()
        return {"status": "success", "api_key": api_key, "tier": tier, "credits": credits}
    except sqlite3.IntegrityError:
        conn.close()
        return {"status": "error", "message": "User email already registered"}

def deduct_credits(api_key, amount=1, topic="N/A", niche="N/A"):
    val = validate_key(api_key)
    if not val["valid"]:
        return {"status": "error", "message": "Invalid API key"}
        
    if val["tier"] == "agency":
        # Unlimited Tier
        return {"status": "success", "credits_remaining": 999999}
        
    if val["credits"] < amount:
        return {"status": "error", "message": "Insufficient credits. Please upgrade your tier."}
        
    new_credits = val["credits"] - amount
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET credits = ? WHERE id = ?", (new_credits, val["user_id"]))
    cursor.execute(
        "INSERT INTO usage_logs (user_id, topic, niche, pins_generated) VALUES (?, ?, ?, ?)",
        (val["user_id"], topic, niche, 10)
    )
    conn.commit()
    conn.close()
    return {"status": "success", "credits_remaining": new_credits}

def save_campaign(api_key, topic, niche, url, ai_engine, zip_path, csv_path, manifest_data):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO campaigns (api_key, topic, niche, url, ai_engine, zip_path, csv_path, manifest_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (api_key, topic, niche, url, ai_engine, zip_path, csv_path, json.dumps(manifest_data))
    )
    campaign_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return campaign_id

def get_recent_campaigns(limit=10):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, topic, niche, url, ai_engine, zip_path, csv_path, timestamp
        FROM campaigns
        ORDER BY id DESC LIMIT ?
        """,
        (limit,)
    )
    rows = cursor.fetchall()
    conn.close()
    
    campaigns = []
    for r in rows:
        campaigns.append({
            "id": r[0],
            "topic": r[1],
            "niche": r[2],
            "url": r[3],
            "ai_engine": r[4],
            "zip_path": r[5],
            "csv_path": r[6],
            "zip_download_url": f"/api/download?path={r[5]}",
            "csv_download_url": f"/api/download?path={r[6]}",
            "timestamp": r[7]
        })
    return campaigns

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
