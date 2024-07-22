from datetime import time

import logging
import pytz
from discord.ext import tasks

from bot.core import bot
from cogs.streaks import list_all_streaks

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@tasks.loop(time=time(hour=21, minute=0, tzinfo=pytz.timezone('US/Pacific')))
async def daily_streak_update():
    channel = bot.get_channel(1236433017250250805)
    await list_all_streaks(channel)


@daily_streak_update.before_loop
async def before_daily_streak_update():
    # sent at 9:53 instead of 9:00
    await bot.wait_until_ready()
    logger.info("Daily streak update task is ready!")

