import requests
import json
from datetime import datetime
import os

# รายชื่อกองทุนที่คุณอิฐสนใจ (ผม mapping รหัสของ Finnomena ให้แล้ว)
# ถ้าตัวไหนไม่ถูก แก้ไขชื่อในเครื่องหมายคำพูดได้เลยครับ
FUNDS = [
    {"code": "K-USXNDQ-A(A)", "name": "🇺🇸 USXNDQ-A (Tech)"},
    {"code": "K-CHANGE-RMF",  "name": "🌍 Change RMF"},
    {"code": "K-US500X-RMF",  "name": "📈 US500X RMF"} 
]
# หมายเหตุ: K-US500X-RMF ผมเดาว่าคือตัวนี้ ถ้าไม่ใช่ลองแก้เป็น 'K-US500X-A(A)' หรือชื่ออื่นใน Finnomena url

def get_nav(fund_code):
    try:
        # ใช้ API ลับของ Finnomena (ง่ายและแม่นกว่า scrape เอง)
        url = f"https://www.finnomena.com/fn3/api/fund/public/fund_overview?fund_code={fund_code}"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        data = res.json()
        
        # ดึงราคา NAV ล่าสุด
        nav = data['data']['nav_price']
        date = data['data']['nav_date']
        return f"{nav:.4f} ({date[:10]})"
    except:
        return "Not Found"

def send_teams():
    webhook_url = os.environ.get("TEAMS_WEBHOOK")
    if not webhook_url:
        print("Error: No Webhook URL found")
        return

    facts = []
    for fund in FUNDS:
        price = get_nav(fund['code'])
        facts.append({"name": fund['name'], "value": price})

    card = {
        "@type": "MessageCard",
        "@context": "http://schema.org/extensions",
        "themeColor": "0076D7",
        "summary": "Fund Update",
        "sections": [{
            "activityTitle": "💰 Daily Fund Update",
            "facts": facts,
            "markdown": True
        }]
    }
    requests.post(webhook_url, json=card)

if __name__ == "__main__":
    send_teams()
