#!/usr/bin/env python3
"""
PinGenius - Upgrade 3: Automated Pinterest API v5 & Webhook Auto-Scheduler
Herm tha Worm Edition
"""

import argparse
import json
import os
import urllib.request
import urllib.error

PINTEREST_API_ENDPOINT = "https://api.pinterest.com/v5/pins"

def publish_pin_to_pinterest(access_token, board_id, title, description, link_url, image_url, alt_text=""):
    """
    Publishes a Pin directly via official Pinterest API v5.
    """
    if not access_token:
        return {"status": "error", "message": "PINTEREST_ACCESS_TOKEN environment variable is not configured."}
        
    payload = {
        "board_id": board_id,
        "title": title[:100],
        "description": description[:500],
        "link": link_url,
        "alt_text": alt_text[:500],
        "media_source": {
            "source_type": "image_url",
            "url": image_url
        }
    }
    
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        PINTEREST_API_ENDPOINT,
        data=data,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "User-Agent": "PinGenius/1.0"
        },
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            res_body = response.read().decode('utf-8')
            return {"status": "success", "pinterest_response": json.loads(res_body)}
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        return {"status": "error", "code": e.code, "message": error_body}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def dispatch_webhook_schedule(webhook_url, dispatch_queue):
    """
    Dispatches schedule payload to external automation webhooks (Make, Zapier, N8N, ISO CRM).
    """
    if not webhook_url:
        return {"status": "simulated", "message": "No webhook URL configured. Dry run complete."}
        
    data = json.dumps({"engine": "PinGenius (Herm Edition)", "queue": dispatch_queue}).encode('utf-8')
    req = urllib.request.Request(
        webhook_url,
        data=data,
        headers={"Content-Type": "application/json"}
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            return {"status": "success", "response_code": response.getcode()}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PinGenius Direct Publisher & Webhook Dispatcher")
    parser.add_argument("--token", help="Pinterest API Access Token")
    parser.add_argument("--board", help="Target Board ID")
    parser.add_argument("--title", default="Sample Pin Title")
    parser.add_argument("--desc", default="Sample Pin Description")
    parser.add_argument("--link", default="https://studio-7106835876-c5253.web.app/")
    parser.add_argument("--image", default="https://studio-7106835876-c5253.web.app/mamas_boy_logo.png")
    parser.add_argument("--webhook", help="Optional Webhook Dispatch URL")
    
    args = parser.parse_args()
    
    res = publish_pin_to_pinterest(
        access_token=args.token or os.environ.get("PINTEREST_ACCESS_TOKEN"),
        board_id=args.board or "1234567890",
        title=args.title,
        description=args.desc,
        link_url=args.link,
        image_url=args.image
    )
    
    print(json.dumps(res, indent=2))
