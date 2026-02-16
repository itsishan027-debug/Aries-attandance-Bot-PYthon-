import discord
from discord.ext import commands
from datetime import datetime
import os
import time

# --- CONFIGURATION ---
# Replace with your actual Bot Token
TOKEN = "MTQ3MTg4NTg4NDI0Nzc3MzMwNg.GFzWFH.e9k9TXwMhrO0bZhj8kD4Z6sdN2V5Pxe-pgDtMk"
TARGET_SERVER_ID = 770004215678369883
TARGET_CHANNEL_ID = 1426247870495068343

class AriesBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True 
        super().__init__(command_prefix="!", intents=intents)
        self.active_sessions = {}
        self.start_time = datetime.now()

bot = AriesBot()

@bot.event
async def on_ready():
    # Syncs slash commands if you ever add them
    print(f'✅ Bot is online as: {bot.user}')
    print(f'🛡️ Secured for Server: {TARGET_SERVER_ID}')
    print(f'📍 Monitoring Channel: {TARGET_CHANNEL_ID}')

@bot.event
async def on_message(message):
    # Security: Ignore bots and check server/channel
    if message.author == bot.user: return
    if message.guild is None or message.guild.id != TARGET_SERVER_ID: return

    # Trigger logic for Online/Offline in the specific channel
    if message.channel.id == TARGET_CHANNEL_ID:
        content = message.content.lower().strip()
        user = message.author
        now = datetime.now()
        time_str = now.strftime("%I:%M %p")

        # --- ONLINE LOGIC ---
        if content == "online":
            try: await message.delete()
            except: pass
            
            if user.id not in bot.active_sessions:
                bot.active_sessions[user.id] = now
                embed = discord.Embed(
                    title="System: Attendance Recorded",
                    description=f"✅ {user.mention} is now **ONLINE**",
                    color=0x2ecc71 # Green
                )
                embed.add_field(name="Login Time", value=f"🕒 `{time_str}`")
                embed.set_thumbnail(url=user.display_avatar.url)
                await message.channel.send(embed=embed)
            else:
                await message.channel.send(f"⚠️ {user.mention}, you are already marked online.", delete_after=5)

        # --- OFFLINE LOGIC ---
        elif content == "offline":
            try: await message.delete()
            except: pass
            
            if user.id in bot.active_sessions:
                start_time = bot.active_sessions[user.id]
                duration = now - start_time
                
                # Calculate Duration
                hours, remainder = divmod(int(duration.total_seconds()), 3600)
                minutes, _ = divmod(remainder, 60)
                duration_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"

                embed = discord.Embed(
                    title="System: Attendance Recorded",
                    description=f"🔴 {user.mention} is now **OFFLINE**",
                    color=0xe74c3c # Red
                )
                embed.add_field(name="Logged In", value=start_time.strftime("%I:%M %p"), inline=True)
                embed.add_field(name="Logged Out", value=time_str, inline=True)
                embed.add_field(name="Total Session", value=f"⏳ `{duration_str}`", inline=False)
                embed.set_thumbnail(url=user.display_avatar.url)
                
                await message.channel.send(embed=embed)
                del bot.active_sessions[user.id]
            else:
                await message.channel.send(f"❓ {user.mention}, you weren't marked online.", delete_after=5)

    # Process other commands
    await bot.process_commands(message)

# --- INSPECTION COMMAND (ADMIN ONLY) ---
@bot.command()
@commands.has_permissions(administrator=True)
async def inspect(ctx):
    uptime = datetime.now() - bot.start_time
    hours, remainder = divmod(int(uptime.total_seconds()), 3600)
    minutes, _ = divmod(remainder, 60)
    latency = round(bot.latency * 1000)
    
    embed = discord.Embed(title="🔍 Bot Health Inspection", color=0xf1c40f) # Yellow
    embed.add_field(name="Status", value="🟢 Online & Running", inline=False)
    embed.add_field(name="Latency", value=f"`{latency}ms`", inline=True)
    embed.add_field(name="Uptime", value=f"`{hours}h {minutes}m`", inline=True)
    embed.add_field(name="Active Sessions", value=f"`{len(bot.active_sessions)}` users", inline=True)
    embed.set_footer(text=f"Admin: {ctx.author.name}")
    await ctx.send(embed=embed)

# Error handling for !inspect
@inspect.error
async def inspect_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("🚫 **Access Denied:** Administrator only.", delete_after=5)

bot.run(TOKEN)
