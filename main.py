import requests
import json
import os
from datetime import datetime

# URL ของ Webhook จะถูกดึงมาจาก Secret ที่คุณตั้งเมื่อกี้ (ปลอดภัย 100%)
WEBHOOK_URL = os.environ.get("TEAMS_WEBHOOK")

# รายชื่อกองทุน (Mapping รหัสให้ตรงกับระบบ Finnomena)
FUNDS = [
    {"code": "K-USXNDQ-A(A)", "name": "🇺🇸 USXNDQ-A (Tech)"},
    {"code": "K-CHANGE-RMF",  "name": "🌍 Change RMF (Climate)"},
    {"code": "K-US500X-RMF",  "name": "📈 US500X RMF (S&P500)"} 
]

def get_nav(fund_code):
    """ฟังก์ชันดึงราคา NAV ล่าสุดจาก Finnomena"""
    try:
        url = f"https://www.finnomena.com/fn3/api/fund/public/fund_overview?fund_code={fund_code}"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        data = res.json()
        
        # เจาะเอาข้อมูลราคาและวันที่
        nav = data['data']['nav_price']
        date = data['data']['nav_date']
        
        # จัดรูปแบบวันที่ให้อ่านง่าย (จาก 2023-12-15 เป็น 15 Dec)
        date_obj = datetime.strptime(date[:10], '%Y-%m-%d')
        date_nice = date_obj.strftime('%d %b')
        
        return f"{nav:.4f} THB ({date_nice})"
    except Exception as e:
        print(f"Error fetching {fund_code}: {e}")
        return "N/A"

def send_to_teams():
    if not WEBHOOK_URL:
        print("Error: ไม่พบ TEAMS_WEBHOOK ใน Secrets")
        return

    facts = []
    print("Fetching data...")
    for fund in FUNDS:
        price = get_nav(fund['code'])
        facts.append({"name": fund['name'], "value": price})
        print(f"Got {fund['name']}: {price}")

    # สร้างการ์ดสวยๆ ส่งเข้า Teams
    card = {
        "@type": "MessageCard",
        "@context": "http://schema.org/extensions",
        "themeColor": "0076D7",
        "summary": "Fund Update",
        "sections": [{
            "activityTitle": "💰 Daily Fund Status",
            "activitySubtitle": f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "facts": facts,
            "markdown": True
        }]
    }
    
    # ยิงข้อมูลออกไป
    res = requests.post(WEBHOOK_URL, json=card)
    print(f"Sent to Teams. Status Code: {res.status_code}")

if __name__ == "__main__":
    send_to_teams()
