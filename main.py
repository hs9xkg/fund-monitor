import requests
import json
import os
from datetime import datetime

WEBHOOK_URL = os.environ.get("TEAMS_WEBHOOK")

TARGETS = [
    # 1. Tech (ที่เดิม)
    {
        "name": "🇺🇸 USXNDQ-A (Tech)",
        "candidates": ["K-USXNDQ-A(A)", "K-USXNDQ-A", "K-USXNDQ"] 
    },
    # 2. Climate RMF (ที่เดิม)
    {
        "name": "🌍 Change RMF (Climate)",
        "candidates": ["K-CHANGE-RMF", "K-CHANGERMF", "K-CHANGE"] 
    },
    # 3. S&P500 RMF (ที่เดิม)
    {
        "name": "📈 US500X RMF (S&P500)",
        "candidates": ["K-US500X-RMF", "K-US500XRMF", "K-US500X-RMF(A)"] 
    },
    # 4. (ตัวใหม่!) S&P500 แบบธรรมดา เอามาเทียบดูว่าดึงได้ไหม
    {
        "name": "🧪 TEST: K-US500X-A (Normal)",
        "candidates": ["K-US500X-A(A)", "K-US500X-A", "K-US500X"] 
    }
]

def get_nav_smart(fund_name, candidates):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Referer': 'https://www.finnomena.com/'
    }
    
    for code in candidates:
        try:
            print(f"[{fund_name}] Trying: {code} ...")
            url = "https://www.finnomena.com/fn3/api/fund/public/fund_overview"
            res = requests.get(url, params={'fund_code': code}, headers=headers, timeout=10)
            data = res.json()

            # Anti-Crash: ถ้าได้ bool (False) ให้ข้าม
            if isinstance(data, bool):
                print(f"   ❌ Failed (API returned False)")
                continue
                
            if 'data' not in data or not data['data']:
                print(f"   ❌ Failed (Empty Data)")
                continue

            nav = data['data']['nav_price']
            date = data['data']['nav_date']
            date_nice = datetime.strptime(date[:10], '%Y-%m-%d').strftime('%d %b')
            
            print(f"   ✅ SUCCESS! Found NAV: {nav}")
            return f"{nav:.4f} ({date_nice})"

        except Exception as e:
            print(f"   ⚠️ Error: {e}")
            continue
            
    return "N/A (Not Found)"

def send_to_teams():
    if not WEBHOOK_URL:
        return

    facts = []
    print("--- Starting Monitor (With Control Test) ---")
    
    for item in TARGETS:
        price = get_nav_smart(item['name'], item['candidates'])
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
