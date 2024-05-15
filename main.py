import logging
from datetime import time
from typing import Final
import os
import pytz
from discord.ext import tasks
from dotenv import load_dotenv
from discord import Member, Message
from responses import get_response, get_hooter_explanation
from streaks import initialize_streaks, load_streaks, save_streaks, \
    process_streak, list_all_streaks
from bot import bot

load_dotenv()
TOKEN: Final[str] = os.getenv("DISCORD_TOKEN")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

STUDY_CHANNEL_ID = 1236433017250250806
GENERAL_CHANNEL_ID = 1236433017250250805
MINIMUM_MINUTES = 25

@bot.event
async def on_member_join(member):
    guild = member.guild
    welcome_channel = guild.system_channel

    if welcome_channel:
        welcome_message = f"Whoo-hoo! Welcome, {member.display_name}! 🎉 I’m Hooter the Tutor, your guide to staying accountable. We’ve got daily sessions at 9 PM PST but remember, you can hop in anytime that works for you to maintain your streak!"
        # Sending the initial welcome message
        await welcome_channel.send(welcome_message)
        # Detailed explanation as a follow-up message
        await welcome_channel.send(get_hooter_explanation())

@bot.command(name="reintroduce")
async def reintroduce(ctx, member: Member = None):
    """Command to reintroduce the system. If a member is mentioned, it addresses them specifically."""
    if member:
      message = f"Hey {member.display_name}, let me reintroduce you to how we keep things engaging around here!"
    else:
      message = "Looks like someone needs a refresher on how our awesome system works!"

    explanation = get_hooter_explanation()
    await ctx.send(f"{message}\n{explanation}")


@bot.event
async def on_voice_state_update(member, before, after):
    if member.bot:
        return

    await process_streak(member, before, after, STUDY_CHANNEL_ID, MINIMUM_MINUTES)

@bot.command(name="streak")
async def streak(ctx, member: Member = None) -> None:
    if member is None:
        member = ctx.author

    streaks_data = load_streaks()
    await display_streak(ctx, member, streaks_data)

async def send_message(message: Message, user_message: str) -> None:
    if not user_message:
        logger.debug("Message was empty because intents were not enabled properly")
    if is_private := user_message[0] == '?':
        user_message = user_message[1:]

    try:
        response: str = get_response(user_message)
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        logging.debug(e)

@tasks.loop(time=time(hour=21, minute=0, tzinfo=pytz.timezone('US/Pacific')))
async def daily_streak_update():
    channel = bot.get_channel(1236433017250250805)
    await list_all_streaks(channel)

@daily_streak_update.before_loop
async def before_daily_streak_update():
    # sent at 9:53 instead of 9:00
    await bot.wait_until_ready()
    logger.info("Daily streak update task is ready!")

@bot.event
async def on_ready() -> None:
    print(f"{bot.user} is now running")
    await initialize_streaks()
    daily_streak_update.start()

@bot.event
async def on_disconnect() -> None:
    save_streaks(load_streaks())
    logging.info("Bot disconnected. Streaks data saved.")

@bot.event
async def on_message(message: Message) -> None:
    if message.author == bot.user:
        return

    username: str = str(message.author)
    user_message: str = message.content
    channel: str = str(message.channel)

    logger.info(f"[{channel}] {username}: {user_message}")

    if bot.user.mentioned_in(message):
        user_message = user_message.replace(f'<@!{bot.user.id}>', '').strip()
        await send_message(message, user_message)

    await bot.process_commands(message)

async def display_streak(ctx, member, streaks_data):
    user_id = str(member.id)

    if user_id in streaks_data:
        current_streak = streaks_data[user_id]["current_streak"]
        longest_streak = streaks_data[user_id]["longest_streak"]
        username = streaks_data[user_id]["username"]
        message = f"{username}'s streaks:\n" \
                  f"Current streak: {current_streak} days\n" \
                  f"Longest streak: {longest_streak} days"
        await ctx.send(message)
        logger.info(f"{ctx.author.name} checked {username}'s streaks - Current: {current_streak}, Longest: {longest_streak}")
    else:
        await ctx.send(f"{member.mention} hasn't started a streak yet.")
        logger.info(f"{ctx.author.name} checked {member.name}'s streak, but they haven't started yet.")

def main():
    bot.run(token=TOKEN)

if __name__ == '__main__':
    main()