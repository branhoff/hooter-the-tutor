import logging

from bot.core import bot
from bot.events import on_member_join, on_voice_state_update, on_ready, on_disconnect, on_message
from bot.tasks import daily_streak_update
from bot.commands import CommandsCog

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def setup_commands(bot):
    await bot.add_cog(CommandsCog(bot))
    logging.info("Commands have been set up")

def setup_events(bot):
    bot.event(on_member_join)
    bot.event(on_voice_state_update)
    bot.event(on_ready)
    bot.event(on_disconnect)
    bot.event(on_message)
    logging.info("Events have been set up.")

async def setup_tasks(bot):
    daily_streak_update.start()
    logging.info("Tasks have been set up.")

async def setup_bot():
    await setup_commands(bot)
    setup_events(bot)
    await setup_tasks(bot)
    logging.info("Bot setup completed.")