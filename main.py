import requests
import json
import os
from datetime import datetime

# URL จาก Secrets
WEBHOOK_URL = os.environ.get("TEAMS_WEBHOOK")

# รายชื่อกองทุน พร้อม "รหัสสำรอง" (Candidate Codes)
# สคริปต์จะลองไล่เช็กทีละรหัส จนกว่าจะเจอตัวที่ใช่
TARGETS = [
    {
        "name": "🇺🇸 USXNDQ-A (Tech)",
        "candidates": ["K-USXNDQ-A(A)", "K-USXNDQ-A", "K-USXNDQ"] 
    },
    {
        "name": "🌍 Change RMF (Climate)",
        "candidates": ["K-CHANGE-RMF", "K-CHANGERMF", "K-CHANGE"] 
    },
    {
        "name": "📈 US500X RMF (S&P500)",
        "candidates": ["K-US500X-RMF", "K-US500XRMF", "K-US500X"] 
    }
]

def fetch_nav_smart(fund_name, candidates):
    base_url = "https://www.finnomena.com/fn3/api/fund/public/fund_overview"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'https://www.finnomena.com/'
    }
    
    # วนลูปลองรหัสทีละตัว
    for code in candidates:
        try:
            print(f"[{fund_name}] Trying code: {code} ...")
            res = requests.get(base_url, params={'fund_code': code}, headers=headers, timeout=10)
            
            if res.status_code == 200:
                data = res.json()
                if 'data' in data and data['data']:
                    nav = data['data']['nav_price']
                    date = data['data']['nav_date']
                    
                    # ถ้าได้ข้อมูลแล้ว ให้จัด Format แล้วส่งกลับเลย (ไม่ต้องลองตัวอื่นต่อ)
                    date_nice = datetime.strptime(date[:10], '%Y-%m-%d').strftime('%d %b')
                    print(f"✅ Success! Found {code} = {nav}")
                    return f"{nav:.4f} ({date_nice})"
        except Exception as e:
            print(f"❌ Error checking {code}: {e}")
            continue
            
    # ถ้าลองครบทุกรหัสแล้วยังไม่ได้
    print(f"⚠️ Failed to find NAV for {fund_name}")
    return "N/A (Not Found)"

def send_to_teams():
    if not WEBHOOK_URL:
        print("Error: No Webhook URL")
        return

    facts = []
    print("--- Starting Smart Fund Monitor ---")
    
    for item in TARGETS:
        price = fetch_nav_smart(item['name'], item['candidates'])
        facts.append({"title": item['name'], "value": price})

    # Adaptive Card
    card_payload = {
        "type": "message",
        "attachments": [{
            "contentType": "application/vnd.microsoft.card.adaptive",
            "content": {
                "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                "type": "AdaptiveCard",
                "version": "1.4",
                "body": [
                    {
                        "type": "TextBlock",
                        "text": "💰 Daily Fund Status",
                        "weight": "Bolder",
                        "size": "Large",
                        "color": "Accent"
                    },
                    {
                        "type": "TextBlock",
                        "text": f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                        "isSubtle": True,
                        "spacing": "None"
                    },
                    {
                        "type": "FactSet",
                        "facts": facts
                    }
                ]
            }
        }]
    }
    
    requests.post(WEBHOOK_URL, json=card_payload)
    print("--- Finished ---")

if __name__ == "__main__":
    send_to_teams()
