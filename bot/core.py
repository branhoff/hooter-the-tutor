import os
from dotenv import load_dotenv
from discord.ext import commands
from discord import Intents

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
STUDY_CHANNEL_ID = 1236433017250250806
GENERAL_CHANNEL_ID = 1236433017250250805
MINIMUM_MINUTES = 25

intents = Intents.default()
intents.members = True
intents.message_content = True


class HooterBot(commands.Bot):
  async def setup_hook(self):
    from bot.setup import setup_bot
    await setup_bot()


bot = HooterBot(command_prefix='!', intents=intents)
