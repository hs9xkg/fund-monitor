import yfinance as yf
import requests
import os
from datetime import datetime

WEBHOOK_URL = os.environ.get("TEAMS_WEBHOOK")

# จับคู่กองทุนไทย -> กองทุนแม่ (Master Fund)
# ข้อดี: Yahoo Finance อัปเดต Real-time และไม่บล็อก
TARGETS = [
    {
        "thai_name": "🇺🇸 K-USXNDQ (Tech)",
        "master_ticker": "QQQ",  # Invesco QQQ Trust
        "desc": "Nasdaq-100 ETF"
    },
    {
        "thai_name": "📈 K-US500X (S&P500)",
        "master_ticker": "IVV",  # iShares Core S&P 500 ETF
        "desc": "S&P 500 ETF"
    },
    {
        "thai_name": "🌍 K-CHANGE (Climate)",
        "master_ticker": "BPGIX", # Baillie Gifford Positive Change (US Class)
        "desc": "Master Fund Proxy"
    }
]

def get_market_data(ticker):
    try:
        print(f"Fetching {ticker} from Yahoo Finance...")
        stock = yf.Ticker(ticker)
        
        # ดึงราคาล่าสุด
        history = stock.history(period="2d")
        if history.empty:
            return "N/A"
            
        last_close = history['Close'].iloc[-1]
        prev_close = history['Close'].iloc[-2]
        
        # คำนวณ % การเปลี่ยนแปลง (จะได้รู้ว่าวันนี้หุ้นขึ้นหรือลง)
        change_percent = ((last_close - prev_close) / prev_close) * 100
        
        # ใส่ Emoji บอกทิศทางกราฟ
        icon = "🟢" if change_percent >= 0 else "🔴"
        
        return f"${last_close:.2f} ({icon} {change_percent:+.2f}%)"
    except Exception as e:
        print(f"Error: {e}")
        return "Error"

def send_to_teams():
    if not WEBHOOK_URL:
        return

    facts = []
    print("--- Starting Yahoo Finance Monitor ---")
    
    for item in TARGETS:
        price_info = get_market_data(item['master_ticker'])
        facts.append({
            "title": item['thai_name'], 
            "value": f"{price_info} \n*({item['desc']})*"
        })

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
                        "text": "🇺🇸 Market Pulse (Master Funds)",
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
                    },
                    {
                        "type": "TextBlock",
                        "text": "*Note: Prices in USD. Use % change to track trend.*",
                        "size": "Small",
                        "isSubtle": True,
                        "wrap": True
                    }
                ]
            }
        }]
    }
    
    requests.post(WEBHOOK_URL, json=card_payload)
    print("--- Finished ---")

if __name__ == "__main__":
    send_to_teams()
