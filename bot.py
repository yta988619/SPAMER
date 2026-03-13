import discord
from discord import app_commands
from discord.ext import commands
import os

# הגדרות בסיסיות
TOKEN = os.getenv('DISCORD_TOKEN')

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # מסנכרן את פקודות הסלאש (/) עם דיסקורד
        await self.tree.sync()
        print(f"Synced slash commands for {self.user}")

bot = MyBot()

# --- חלונית קופצת (Modal) להזנת פרטים ---
class SpamModal(discord.ui.Modal, title='Spam Configuration'):
    phone = discord.ui.TextInput(label='Phone Number', placeholder='0501234567...')
    amount = discord.ui.TextInput(label='Amount', placeholder='1-50', default='10')

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"🚀 Starting spam to {self.phone.value} ({self.amount.value} times)...", ephemeral=True)
        # כאן בהמשך נכניס את הלוגיקה של השליחה עצמה

# --- כפתורים מתחת להודעה ---
class ControlPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Spam Phone", style=discord.ButtonStyle.danger, custom_id="spam_btn")
    async def spam_button(self, interaction: discord.Interaction):
        await interaction.response.send_modal(SpamModal())

    @discord.ui.button(label="Stop All", style=discord.ButtonStyle.secondary, custom_id="stop_btn")
    async def stop_button(self, interaction: discord.Interaction):
        await interaction.response.send_message("🛑 All processes stopped.", ephemeral=True)

# --- פקודת ה-Setup ---
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
