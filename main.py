import requests
import json
import os
from datetime import datetime

# URL จาก Secrets
WEBHOOK_URL = os.environ.get("TEAMS_WEBHOOK")

# 1. รายชื่อกองทุนที่ถูกต้อง (ตรวจสอบจาก Finnomena แล้ว)
FUNDS = [
    {"code": "K-USXNDQ-A(A)", "name": "🇺🇸 USXNDQ-A (Tech)"},
    {"code": "K-CHANGERMF",   "name": "🌍 Change RMF (Climate)"}, 
    {"code": "K-US500XRMF",   "name": "📈 US500X RMF (S&P500)"}   
]

def get_nav(fund_code):
    try:
        # 2. ปรับวิธีเรียก URL ให้ปลอดภัย (จัดการวงเล็บและอักษรพิเศษให้อัตโนมัติ)
        base_url = "https://www.finnomena.com/fn3/api/fund/public/fund_overview"
        # ใช้ params แทนการพิมพ์ต่อท้าย URL ตรงๆ เพื่อแก้ปัญหาเรื่องวงเล็บ ( )
        res = requests.get(base_url, params={'fund_code': fund_code}, headers={'User-Agent': 'Mozilla/5.0'})
        
        data = res.json()
        nav = data['data']['nav_price']
        date = data['data']['nav_date']
        date_nice = datetime.strptime(date[:10], '%Y-%m-%d').strftime('%d %b')
        return f"{nav:.4f} ({date_nice})"
    except Exception as e:
        print(f"Error fetching {fund_code}: {e}")
        return "N/A"

def send_to_teams():
    if not WEBHOOK_URL:
        print("Error: No Webhook URL")
        return

    facts = []
    print("Fetching data...")
    for fund in FUNDS:
        price = get_nav(fund['code'])
        facts.append({"title": fund['name'], "value": price})
        print(f"Got {fund['name']}: {price}")

    # Adaptive Card สำหรับ Teams Workflow
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
    
    headers = {'Content-Type': 'application/json'}
    res = requests.post(WEBHOOK_URL, json=card_payload, headers=headers)
    print(f"Sent to Teams. Status Code: {res.status_code}")

if __name__ == "__main__":
    send_to_teams()
