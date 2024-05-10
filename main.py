import json
import logging
from typing import Final
import os
from dotenv import load_dotenv
from discord.ext import commands
from discord import Intents, Member, Message
from responses import get_response
from streaks import load_streaks, save_streaks, process_streak

load_dotenv()
TOKEN: Final[str] = os.getenv("DISCORD_TOKEN")

intents: Intents = Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

STUDY_CHANNEL_ID = 1236433017250250806
MINIMUM_MINUTES = 1

@bot.event
async def on_member_join(member):
    guild = member.guild
    welcome_channel = guild.system_channel

    if welcome_channel:
        purpose = "Welcome to the server! The purpose of this group is to build accountability for side and study projects."
        await welcome_channel.send(f"Welcome {member.mention}! {purpose}")

@bot.event
async def on_voice_state_update(member, before, after):
    if member.bot:
        return  # Ignore voice state updates for bots, including the bot itself

    await process_streak(member, before, after, STUDY_CHANNEL_ID, MINIMUM_MINUTES)

@bot.command(name="streak")
async def streak(ctx, member: Member = None):
    if member is None:
        member = ctx.author

    streaks_data = load_streaks()
    await display_streak(ctx, member, streaks_data)

async def send_message(message: Message, user_message: str) -> None:
    if not user_message:
        print("Message was empty because intents were not enabled properly")
    if is_private := user_message[0] == '?':
        user_message = user_message[1:]

    try:
        response: str = get_response(user_message)
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        print(e)

@bot.event
async def on_ready() -> None:
    print(f"{bot.user} is now running")
    await initialize_streaks()

@bot.event
async def on_disconnect():
    save_streaks(load_streaks())
    print("Bot disconnected. Streaks data saved.")

@bot.event
async def on_message(message: Message) -> None:
    if message.author == bot.user:
        return

    username: str = str(message.author)
    user_message: str = message.content
    channel: str = str(message.channel)

    print(f"[{channel}] {username}: {user_message}")

    if bot.user.mentioned_in(message):
        user_message = user_message.replace(f'<@!{bot.user.id}>', '').strip()
        await send_message(message, user_message)

    await bot.process_commands(message)

async def initialize_streaks():
    logger.info("Initializing streaks data...")
    streaks_data = load_streaks()

    for guild in bot.guilds:
        logger.info(f"Processing guild: {guild.name}")
        async for member in guild.fetch_members(limit=None):
            if member.bot:
                continue
            user_id = str(member.id)
            if user_id not in streaks_data:
                streaks_data[user_id] = {
                    "username": member.name,
                    "current_streak": 0,
                    "longest_streak": 0,
                    "last_join_date": None
                }
                logger.info(f"Added {member.name} to streaks data with initial streak of 0.")

    save_streaks(streaks_data)
    logger.info("Streaks data initialization completed.")

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