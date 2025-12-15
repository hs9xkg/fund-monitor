import requests
import json
import os
from datetime import datetime

# URL จาก Secrets
WEBHOOK_URL = os.environ.get("TEAMS_WEBHOOK")

FUNDS = [
    {"code": "K-USXNDQ-A(A)", "name": "🇺🇸 USXNDQ-A (Tech)"},
    {"code": "K-CHANGE-RMF",  "name": "🌍 Change RMF (Climate)"},
    {"code": "K-US500X-RMF",  "name": "📈 US500X RMF (S&P500)"} 
]

def get_nav(fund_code):
    try:
        url = f"https://www.finnomena.com/fn3/api/fund/public/fund_overview?fund_code={fund_code}"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        data = res.json()
        nav = data['data']['nav_price']
        date = data['data']['nav_date']
        date_nice = datetime.strptime(date[:10], '%Y-%m-%d').strftime('%d %b')
        return f"{nav:.4f} ({date_nice})"
    except:
        return "N/A"

def send_to_teams():
    if not WEBHOOK_URL:
        print("Error: No Webhook URL")
        return

    # เตรียมข้อมูล Facts สำหรับ Adaptive Card
    facts = []
    print("Fetching data...")
    for fund in FUNDS:
        price = get_nav(fund['code'])
        facts.append({"title": fund['name'], "value": price})
        print(f"Got {fund['name']}: {price}")

    # --- ส่วนที่แก้ไข: เปลี่ยนเป็น Adaptive Card ---
    card_payload = {
        "type": "message",
        "attachments": [
            {
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
            }
        ]
    }
    
    # ยิงข้อมูลออกไป
    headers = {'Content-Type': 'application/json'}
    res = requests.post(WEBHOOK_URL, json=card_payload, headers=headers)
    print(f"Sent to Teams. Status Code: {res.status_code}")
    print(res.text) # ปริ้นท์ Response ดูว่า Teams ตอบกลับว่าอะไร

if __name__ == "__main__":
    send_to_teams()
