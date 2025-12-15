# ... (ส่วน import เหมือนเดิม) ...

# 1. แก้ไขชื่อกองทุนให้ถูกต้อง (ลบขีดออก)
FUNDS = [
    {"code": "K-USXNDQ-A(A)", "name": "🇺🇸 USXNDQ-A (Tech)"},
    {"code": "K-CHANGERMF",   "name": "🌍 Change RMF (Climate)"}, # แก้ชื่อ
    {"code": "K-US500XRMF",   "name": "📈 US500X RMF (S&P500)"}   # แก้ชื่อ
]

def get_nav(fund_code):
    try:
        # 2. ปรับวิธีเรียก URL ให้ปลอดภัยกับตัวอักษรพิเศษ ()
        base_url = "https://www.finnomena.com/fn3/api/fund/public/fund_overview"
        # ใช้ params แทน f-string เพื่อให้ Python จัดการวงเล็บให้เอง
        res = requests.get(base_url, params={'fund_code': fund_code}, headers={'User-Agent': 'Mozilla/5.0'})
        
        data = res.json()
        nav = data['data']['nav_price']
        date = data['data']['nav_date']
        date_nice = datetime.strptime(date[:10], '%Y-%m-%d').strftime('%d %b')
        return f"{nav:.4f} ({date_nice})"
    except Exception as e:
        print(f"Error fetching {fund_code}: {e}") # สั่งปริ้น Error ออกมาดู
        return "N/A"

# ... (ส่วน send_to_teams เหมือนเดิม) ...
