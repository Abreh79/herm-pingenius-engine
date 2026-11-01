#!/usr/bin/env python3
"""
PinGenius Database & Campaign Persistence Layer
SQLite storage for user keys, tiered credit metering, and campaign history
"""

import json
import os
import sqlite3
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "pingenius.db")

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

    # Campaigns History Table
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
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Seed Master Admin Key if environment variable MASTER_API_KEY or PINGENIUS_MASTER_KEY is configured
    master_key = os.getenv("MASTER_API_KEY") or os.getenv("PINGENIUS_MASTER_KEY")
    if master_key:
        cursor.execute("SELECT COUNT(*) FROM users WHERE api_key = ?", (master_key,))
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                "INSERT INTO users (email, api_key, tier, credits) VALUES (?, ?, ?, ?)",
                ("admin@pingenius.io", master_key, "agency", 999999)
            )

    conn.commit()
    conn.close()

def validate_key(api_key):
    if not api_key:
        return {"valid": False, "message": "API key is required"}

    master_key = os.getenv("MASTER_API_KEY") or os.getenv("PINGENIUS_MASTER_KEY")
    if master_key and api_key == master_key:
        return {"valid": True, "email": "admin@pingenius.io", "tier": "agency", "credits": 999999}

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, tier, credits FROM users WHERE api_key = ?", (api_key,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        user_id, email, tier, credits = row
        if credits <= 0:
            return {"valid": False, "message": "Credit quota exhausted. Please top up."}
        return {
            "valid": True,
            "user_id": user_id,
            "email": email,
            "tier": tier,
            "credits": credits
        }
    return {"valid": False, "message": "Invalid API key"}

def create_user(email, tier="starter", credits=100):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    api_key = f"pg_{tier}_{int(time.time())}"
    
    try:
        cursor.execute(
            "INSERT INTO users (email, api_key, tier, credits) VALUES (?, ?, ?, ?)",
            (email, api_key, tier, credits)
        )
        conn.commit()
        conn.close()
        return {"status": "success", "api_key": api_key, "tier": tier, "credits": credits}
    except Exception as e:
        conn.close()
        return {"status": "error", "message": str(e)}

def deduct_credits(api_key, amount=1, topic="N/A", niche="N/A"):
    val = validate_key(api_key)
    if not val["valid"]:
        return {"status": "error", "message": val.get("message", "Invalid API key")}
        
    master_key = os.getenv("MASTER_API_KEY") or os.getenv("PINGENIUS_MASTER_KEY")
    if master_key and api_key == master_key:
        return {"status": "success", "remaining_credits": 999999}

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET credits = credits - ? WHERE api_key = ?", (amount, api_key))
    cursor.execute(
        "INSERT INTO usage_logs (user_id, topic, niche, pins_generated) VALUES (?, ?, ?, ?)",
        (val["user_id"], topic, niche, amount)
    )
    conn.commit()
    
    cursor.execute("SELECT credits FROM users WHERE api_key = ?", (api_key,))
    new_credits = cursor.fetchone()[0]
    conn.close()
    
    return {"status": "success", "remaining_credits": new_credits}

def save_campaign(api_key, topic, niche, url, ai_engine, zip_path, csv_path, manifest_data):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO campaigns (api_key, topic, niche, url, ai_engine, zip_path, csv_path, manifest_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (api_key, topic, niche, url, ai_engine, zip_path, csv_path, json.dumps(manifest_data)))
    conn.commit()
    conn.close()

def get_recent_campaigns(limit=10):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, topic, niche, url, ai_engine, zip_path, csv_path, manifest_json, created_at 
        FROM campaigns 
        ORDER BY created_at DESC 
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    
    results = []
    for r in rows:
        results.append({
            "id": r[0],
            "topic": r[1],
            "niche": r[2],
            "url": r[3],
            "ai_engine": r[4],
            "zip_path": r[5],
            "csv_path": r[6],
            "manifest": json.loads(r[7]) if r[7] else {},
            "created_at": r[8]
        })
    return results
