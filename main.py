import requests
import json
import os
from datetime import datetime

WEBHOOK_URL = os.environ.get("TEAMS_WEBHOOK")

# ใช้ Keyword กว้างๆ เดี๋ยวให้ระบบไปหาตัวจริงมาให้เอง
SEARCH_LIST = [
    {"keyword": "USXNDQ",     "display_name": "🇺🇸 USXNDQ-A (Tech)"},
    {"keyword": "CHANGE-RMF", "display_name": "🌍 Change RMF (Climate)"},
    {"keyword": "US500X-RMF", "display_name": "📈 US500X RMF (S&P500)"}
]

def get_nav_bulletproof(keyword):
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        # 1. ค้นหา Fund Code ที่ถูกต้องจากระบบ (Search API)
        search_url = "https://www.finnomena.com/fn3/api/fund/public/search"
        # สั่งค้นหาและเอาตัวแรกสุดที่เจอ
        search_res = requests.get(search_url, params={"q": keyword}, headers=headers)
        search_data = search_res.json()
        
        if not search_data or isinstance(search_data, bool):
            return "Fund Not Found"
            
        # ดึงรหัสที่ถูกต้องจากผลลัพธ์แรก
        valid_fund_code = search_data[0]['fund_code']
        print(f"[{keyword}] Found valid code: {valid_fund_code}")

        # 2. เอา Fund Code ไปดึงราคา (Overview API)
        overview_url = "https://www.finnomena.com/fn3/api/fund/public/fund_overview"
        res = requests.get(overview_url, params={"fund_code": valid_fund_code}, headers=headers)
        data = res.json()
        
        # --- จุดแก้ Error: เช็กก่อนว่าเป็น Boolean (False) หรือไม่ ---
        if isinstance(data, bool): 
            return "N/A (API returned False)"
            
        if 'data' not in data or not data['data']:
            return "Data Empty"
        # ----------------------------------------------------

        nav = data['data']['nav_price']
        date = data['data']['nav_date']
        date_nice = datetime.strptime(date[:10], '%Y-%m-%d').strftime('%d %b')
        return f"{nav:.4f} ({date_nice})"

    except Exception as e:
        print(f"Error processing {keyword}: {e}")
        return "Error"

def send_to_teams():
    if not WEBHOOK_URL:
        return

    facts = []
    print("--- Starting Bulletproof Monitor ---")
    
    for item in SEARCH_LIST:
        price = get_nav_bulletproof(item['keyword'])
        facts.append({"title": item['display_name'], "value": price})

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
