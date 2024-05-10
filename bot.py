import os
from dotenv import load_dotenv
from discord.ext import commands
from discord import Intents

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready() -> None:
    print(f"{bot.user} is now running")
    from streaks import initialize_streaks
    await initialize_streaks()