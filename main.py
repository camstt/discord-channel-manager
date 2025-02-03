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

# Flask server to keep Replit alive
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_server():
    app.run(host="0.0.0.0", port=8080)

# Start the Flask web server
Thread(target=run_server).start()

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
    1336029284703408270: ("18:05", "18:10"),  # Test Channel (Opens at 12:05 CST / 18:05 UTC, Closes at 12:10 CST / 18:10 UTC)
}

async def open_channel(channel_id):
    guild = bot.guilds[0]  # Assuming bot is only in one server
    channel = guild.get_channel(channel_id)
    if channel:
        await channel.set_permissions(guild.default_role, view_channel=True)
        print(f"✅ Opened channel {channel.name}")

async def close_channel(channel_id):
    guild = bot.guilds[0]
    channel = guild.get_channel(channel_id)
    if channel:
        await channel.set_permissions(guild.default_role, view_channel=False)
        print(f"❌ Closed channel {channel.name}")

@bot.event
async def on_ready():
    print(f"🤖 Bot is online as {bot.user}")
    for channel_id, (open_time, close_time) in SCHEDULED_CHANNELS.items():
        scheduler.add_job(open_channel, 'cron', args=[channel_id], hour=int(open_time.split(":")[0]), minute=int(open_time.split(":")[1]))
        scheduler.add_job(close_channel, 'cron', args=[channel_id], hour=int(close_time.split(":")[0]), minute=int(close_time.split(":")[1]))
    scheduler.start()

bot.run(TOKEN)