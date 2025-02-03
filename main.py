import discord
import os
from discord.ext import tasks
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from flask import Flask
from threading import Thread

# Get bot token from environment variables
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# Define bot intents
intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True
intents.guild_messages = True
intents.guild_scheduled_events = True

bot = discord.Client(intents=intents)
scheduler = AsyncIOScheduler()

# Flask server to keep the bot alive
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!", 200

def run():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    thread = Thread(target=run)
    thread.daemon = True
    thread.start()

# Start the Flask server
keep_alive()

# Channels to schedule (open at 4 AM EST / 9 AM UTC, close at 8 PM EST / 1 AM UTC)
SCHEDULED_CHANNELS = {
    1088824342651097129: ("09:00", "01:00"),  # Alpha
    1228075257672372245: ("09:00", "01:00"),  # Alpha Crypto Chat
    1211677154652201031: ("09:00", "01:00"),  # DIT General
    1258065136761966633: ("09:00", "01:00"),  # Iris General
    1088824790275596318: ("09:00", "01:00"),  # DIT Chat Tickers
    1103374763897933955: ("09:00", "01:00"),  # Alpha Support
    1090285346639585380: ("09:00", "01:00"),  # DIT Support
    1258065773717356574: ("09:00", "01:00"),  # IRIS Support
    1336029284703408270: ("15:15", "16:00"),  # Test Channel (Opens at 3:15 PM EST, Closes at 3:39 PM EST)
}

async def open_channel(channel_id):
    guild = bot.guilds[0]  # Assuming bot is only in one server
    channel = guild.get_channel(channel_id)
    if channel:
        await channel.set_permissions(guild.default_role, view_channel=True)
        print(f"✅ Opened channel {channel.name} ({channel_id})")
    else:
        print(f"⚠️ ERROR: Could not find channel {channel_id}")

async def close_channel(channel_id):
    print(f"🔒 Attempting to close channel {channel_id}...")
    guild = bot.guilds[0]
    channel = guild.get_channel(channel_id)
    if channel:
        await channel.set_permissions(guild.default_role, view_channel=False)
        print(f"❌ Closed channel {channel.name} ({channel_id})")
    else:
        print(f"⚠️ ERROR: Could not find channel {channel_id}")

@bot.event
async def on_ready():
    print(f"🤖 Bot is online as {bot.user}")
    for channel_id, (open_time, close_time) in SCHEDULED_CHANNELS.items():
        open_hour, open_minute = map(int, open_time.split(":"))
        close_hour, close_minute = map(int, close_time.split(":"))

        scheduler.add_job(open_channel, 'cron', args=[channel_id], hour=open_hour, minute=open_minute)
        scheduler.add_job(close_channel, 'cron', args=[channel_id], hour=close_hour, minute=close_minute)

        print(f"📅 Scheduled OPEN for {channel_id} at {open_hour}:{open_minute} UTC")
        print(f"📅 Scheduled CLOSE for {channel_id} at {close_hour}:{close_minute} UTC")

    scheduler.start()
    print("✅ Scheduler started!")

bot.run(TOKEN)