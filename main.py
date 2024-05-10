import json
import logging
from typing import Final
import os
from dotenv import load_dotenv
from discord.ext import commands
from discord import Intents, Member,  Message
from responses import get_response

load_dotenv()
TOKEN: Final[str] = os.getenv("DISCORD_TOKEN")

intents: Intents = Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

STUDY_CHANNEL_ID = 1236433017250250806
MINIMUM_MINUTES = 1

STREAKS_FILE = "streaks.json"

@bot.event
async def on_member_join(member):
    guild = member.guild
    welcome_channel = guild.system_channel

    if welcome_channel:
        purpose = "Welcome to the server! The purpose of this group is to build accountability for side and study projects."
        await welcome_channel.send(f"Welcome {member.mention}! {purpose}")

from datetime import datetime, timedelta

def load_streaks():
    if not os.path.exists(STREAKS_FILE):
        logger.info(f"Streaks file '{STREAKS_FILE}' does not exist. Creating empty file.")
        with open(STREAKS_FILE, 'w') as file:
            json.dump({}, file)
    else:
        logger.info(f"Loading streaks data from file: {STREAKS_FILE}")
    with open(STREAKS_FILE, 'r') as file:
        return json.load(file)

def save_streaks():
    logger.info(f"Saving streaks data to file: {STREAKS_FILE}")
    with open(STREAKS_FILE, 'w') as file:
        json.dump(streaks, file)
    logger.info("Streaks data saved successfully.")

streaks = load_streaks()

async def initialize_streaks():
    logger.info("Initializing streaks data...")
    for guild in bot.guilds:
        logger.info(f"Processing guild: {guild.name}")
        for member in guild.members:
            user_id = str(member.id)
            if user_id not in streaks:
                streaks[user_id] = {"streak": 0}
                logger.info(f"Added {member.name} to streaks data with initial streak of 0.")
    save_streaks()
    logger.info("Streaks data initialization completed.")

@bot.event
async def on_voice_state_update(member, before, after):
    user_id = str(member.id)
    if user_id not in streaks:
        streaks[user_id] = {"streak": 0}

    if after.channel and after.channel.id == STUDY_CHANNEL_ID:
        join_time = datetime.now()
        streaks[user_id]["join_time"] = join_time
        logger.info(f"{member.name} joined the study channel.")
    elif before.channel and before.channel.id == STUDY_CHANNEL_ID:
        if "join_time" in streaks[user_id]:
            join_time = streaks[user_id]["join_time"]
            duration = datetime.now() - join_time
            if duration >= timedelta(minutes=MINIMUM_MINUTES):
                today = datetime.now().date()
                if "last_join_date" in streaks[user_id]:
                    last_join_date = streaks[user_id]["last_join_date"]
                    if today - last_join_date == timedelta(days=1):
                        streaks[user_id]["streak"] += 1
                        logger.info(f"{member.name}'s streak increased to {streaks[user_id]['streak']} days.")
                    elif today - last_join_date > timedelta(days=1):
                        streaks[user_id]["streak"] = 1
                        logger.info(f"{member.name}'s streak reset to 1 day.")
                else:
                    streaks[user_id]["streak"] = 1
                    logger.info(f"{member.name} started a new streak of 1 day.")
                streaks[user_id]["last_join_date"] = today
                save_streaks()
            else:
                logger.info(f"{member.name} left the study channel before the minimum duration.")
            del streaks[user_id]["join_time"]
        else:
            logger.info(f"{member.name} left the study channel but had no active join time.")


@bot.command(name="streak")
async def streak(ctx, member: Member = None):
    if member is None:
        member = ctx.author

    user_id = str(member.id)

    # Load the latest streaks data from the file
    streaks_data = load_streaks()

    if user_id in streaks_data:
        streak_count = streaks_data[user_id]["streak"]
        await ctx.send(
            f"{member.mention}'s current streak is: {streak_count} days!")
        logger.info(
            f"{ctx.author.name} checked {member.name}'s streak of {streak_count} days.")
    else:
        await ctx.send(f"{member.mention} hasn't started a streak yet.")
        logger.info(
            f"{ctx.author.name} checked {member.name}'s streak, but they haven't started yet.")

async def send_message(message: Message, user_message: str) -> None:
    if not user_message:
        print("Message was empty because intents were not enabled properly")
    if is_private:= user_message[0] == '?':
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
    save_streaks()
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

def main():
    bot.run(token=TOKEN)

if __name__ == '__main__':
    main()
