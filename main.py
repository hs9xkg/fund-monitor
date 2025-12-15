import requests
import json
import os
import time
from datetime import datetime

WEBHOOK_URL = os.environ.get("TEAMS_WEBHOOK")

TARGETS = [
    {
        "name": "🇺🇸 USXNDQ-A (Tech)",
        "candidates": ["K-USXNDQ-A(A)", "K-USXNDQ-A"] 
    },
    {
        "name": "🌍 Change RMF (Climate)",
        "candidates": ["K-CHANGERMF", "K-CHANGE-RMF"] 
    },
    {
        "name": "📈 US500X RMF (S&P500)",
        "candidates": ["K-US500XRMF", "K-US500X-RMF"] 
    },
    {
        "name": "🧪 TEST: K-US500X-A",
        "candidates": ["K-US500X-A(A)"] 
    }
]

def get_nav_stealth(fund_name, candidates):
    # --- ส่วนสำคัญ: บัตรประชาชนปลอม (Headers) ---
    # หลอกว่าเป็น Chrome บน Windows 10
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Referer': 'https://www.finnomena.com/',
        'Origin': 'https://www.finnomena.com',
        'Accept-Language': 'en-US,en;q=0.9,th;q=0.8'
    }
    
    for code in candidates:
        try:
            print(f"[{fund_name}] Trying: {code} ...")
            
            # หน่วงเวลา 1 วินาที เพื่อไม่ให้ยิงรัวจนน่าสงสัย
            time.sleep(1)
            
            url = "https://www.finnomena.com/fn3/api/fund/public/fund_overview"
            res = requests.get(url, params={'fund_code': code}, headers=headers, timeout=15)
            
            # แปลงข้อมูลเป็น JSON
            try:
                data = res.json()
            except:
                print(f"   ❌ Failed to parse JSON (Status: {res.status_code})")
                continue

            # ถ้า API ตอบกลับมาเป็น False (โดนบล็อก)
            if isinstance(data, bool):
                print(f"   ❌ Blocked (API returned False)")
                continue
                
            if 'data' not in data or not data['data']:
                print(f"   ❌ Empty Data")
                continue

            # เจอก็เอาเลย!
            nav = data['data']['nav_price']
            date = data['data']['nav_date']
            date_nice = datetime.strptime(date[:10], '%Y-%m-%d').strftime('%d %b')
            
            print(f"   ✅ SUCCESS! Found NAV: {nav}")
            return f"{nav:.4f} ({date_nice})"

        except Exception as e:
            print(f"   ⚠️ Error: {e}")
            continue
            
    return "N/A (Blocked/Not Found)"

def send_to_teams():
    if not WEBHOOK_URL:
        return

    facts = []
    print("--- Starting Stealth Monitor ---")
    
    for item in TARGETS:
        price = get_nav_stealth(item['name'], item['candidates'])
        facts.append({"title": item['name'], "value": price})

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
