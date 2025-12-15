import requests
import json
import os
from datetime import datetime

# URL จาก Secrets
WEBHOOK_URL = os.environ.get("TEAMS_WEBHOOK")

# เราจะไม่ใส่รหัสเป๊ะๆ แล้ว แต่ใส่ "คำค้นหา" แทน (ให้ระบบไปหาตัวจริงมาเอง)
SEARCH_LIST = [
    {"keyword": "K-USXNDQ-A(A)", "display_name": "🇺🇸 USXNDQ-A (Tech)"},
    {"keyword": "K-CHANGE-RMF",  "display_name": "🌍 Change RMF (Climate)"},
    {"keyword": "K-US500X-RMF",  "display_name": "📈 US500X RMF (S&P500)"}
]

def get_nav_auto_search(keyword):
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        # 1. ค้นหารหัสที่ถูกต้องก่อน (Search API)
        search_url = "https://www.finnomena.com/fn3/api/fund/public/search"
        search_res = requests.get(search_url, params={"q": keyword}, headers=headers)
        search_data = search_res.json()
        
        if not search_data:
            return "Fund Not Found"
            
        # เอาผลลัพธ์แรกสุดที่เจอ (แม่นยำที่สุด)
        best_match = search_data[0]
        valid_fund_code = best_match['fund_code']
        print(f"[{keyword}] Found valid code: {valid_fund_code}") # Log ดูว่ามันเจออะไร

        # 2. ใช้รหัสที่ถูกต้อง ไปดึงราคา (Overview API)
        overview_url = "https://www.finnomena.com/fn3/api/fund/public/fund_overview"
        res = requests.get(overview_url, params={"fund_code": valid_fund_code}, headers=headers)
        data = res.json()
        
        # ป้องกัน Error 'bool' object (เช็คว่ามี data จริงไหม)
        if not data.get('data'): 
            return "Data Empty"

        nav = data['data']['nav_price']
        date = data['data']['nav_date']
        
        # จัด Format วันที่
        date_nice = datetime.strptime(date[:10], '%Y-%m-%d').strftime('%d %b')
        return f"{nav:.4f} ({date_nice})"

    except Exception as e:
        print(f"Error processing {keyword}: {e}")
        return "Error"

def send_to_teams():
    if not WEBHOOK_URL:
        print("Error: No Webhook URL")
        return

    facts = []
    print("--- Starting Auto-Search Fund Monitor ---")
    
    for item in SEARCH_LIST:
        price = get_nav_auto_search(item['keyword'])
        facts.append({"title": item['display_name'], "value": price})

    # สร้างการ์ดส่ง Teams
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
