import discord
from discord.ext import commands
from datetime import datetime
import os
import random
from flask import Flask
from threading import Thread

# --- RENDER PORT FIX ---
app = Flask('')
@app.route('/')
def home():
    return "Aries Bot is Online with Leader Protocol!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

# --- BOT CONFIGURATION ---
TOKEN = os.getenv("DISCORD_TOKEN") 
APP_ID = os.getenv("APPLICATION_ID")

TARGET_SERVER_ID = 770004215678369883
TARGET_CHANNEL_ID = 1426247870495068343
LEADER_ROLE_ID = 1412430417578954983  # ✅ Your Leader Role ID

class AriesBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True 
        super().__init__(command_prefix="!", intents=intents, application_id=APP_ID)
        self.active_sessions = {}

bot = AriesBot()

@bot.event
async def on_ready():
    print(f'✅ Logged in as: {bot.user}')

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    if message.guild is None or message.guild.id != TARGET_SERVER_ID: return
    if message.channel.id != TARGET_CHANNEL_ID: return

    content = message.content.lower().strip()
    user = message.author
    now = datetime.utcnow()
    timestamp = int(now.timestamp())
    
    # Leader Role Check
    is_leader = any(role.id == LEADER_ROLE_ID for role in user.roles)

    # --- ONLINE TRIGGER ---
    if content == "online":
        try: await message.delete()
        except: pass

        if user.id not in bot.active_sessions:
            bot.active_sessions[user.id] = now
            
            if is_leader:
                # Unique Leader Online Msg
                greeting = f"🛡️ **Order is restored. Leader {user.display_name} is watching.**"
                msg_color = 0xf1c40f # Gold
            else:
                greeting = f"✅ **{user.display_name}** has started their session."
                msg_color = 0x2ecc71 # Green

            embed = discord.Embed(title="Status: ONLINE", description=greeting, color=msg_color)
            embed.set_author(name=user.display_name, icon_url=user.display_avatar.url)
            embed.set_thumbnail(url=user.display_avatar.url)
            embed.add_field(name="Arrival", value=f"🕒 <t:{timestamp}:t>")
            await message.channel.send(embed=embed)
        else:
            await message.channel.send(f"⚠️ {user.mention}, you are already online!", delete_after=5)

    # --- OFFLINE TRIGGER ---
    elif content == "offline":
        try: await message.delete()
        except: pass

        if user.id in bot.active_sessions:
            start_time = bot.active_sessions[user.id]
            duration = now - start_time
            
            if is_leader:
                # Unique Leader Offline Msg
                status_msg = f"🌑 **The Leader {user.display_name} is now off-duty. Stay safe until his return.**"
                msg_color = 0x2f3136 # Dark Theme
            else:
                status_msg = f"🔴 **{user.display_name}** session ended."
                msg_color = 0xe74c3c # Red

            hours, remainder = divmod(int(duration.total_seconds()), 3600)
            minutes, _ = divmod(remainder, 60)
            duration_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"

            embed = discord.Embed(title="Status: OFFLINE", description=status_msg, color=msg_color)
            embed.set_author(name=user.display_name, icon_url=user.display_avatar.url)
            embed.add_field(name="Total Influence", value=f"⏳ `{duration_str}`")
            await message.channel.send(embed=embed)
            del bot.active_sessions[user.id]
        else:
            await message.channel.send(f"❓ {user.mention}, you were not marked online.", delete_after=5)

    await bot.process_commands(message)

# --- ADMIN LIST COMMAND ---
@bot.command()
@commands.has_permissions(administrator=True)
async def list(ctx):
    if not bot.active_sessions:
        await ctx.send("Empty list: No users are currently online.")
        return

    embed = discord.Embed(title="👥 Current Online Members", color=0x3498db)
    user_list = ""
    for user_id, start_time in bot.active_sessions.items():
        member = ctx.guild.get_member(user_id)
        name = member.display_name if member else f"User ID: {user_id}"
        user_list += f"• **{name}** (Started: <t:{int(start_time.timestamp())}:R>)\n"

    embed.add_field(name="Active Sessions", value=user_list, inline=False)
    await ctx.send(embed=embed)

if __name__ == "__main__":
    keep_alive()
    if TOKEN:
        bot.run(TOKEN)
        
