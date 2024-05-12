import json
import logging
import os
from datetime import datetime, timedelta
from bot import bot

logger = logging.getLogger(__name__)

STREAKS_FILE = "streaks.json"

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
                    "last_join_date": None,
                    "join_time": None
                }
                logger.info(f"Added {member.name} to streaks data with initial streak of 0.")

    save_streaks(streaks_data)
    logger.info("Streaks data initialization completed.")

def load_streaks():
    if not os.path.exists(STREAKS_FILE):
        logger.info(f"Streaks file '{STREAKS_FILE}' does not exist. Creating empty file.")
        with open(STREAKS_FILE, 'w') as file:
            json.dump({}, file)
    else:
        logger.info(f"Loading streaks data from file: {STREAKS_FILE}")
    with open(STREAKS_FILE, 'r') as file:
        loaded_data = json.load(file)
        deserialized_streaks = {
            user_id: {
                "username": data["username"],
                "current_streak": data["current_streak"],
                "longest_streak": data["longest_streak"],
                "last_join_date": datetime.fromisoformat(data["last_join_date"]) if data["last_join_date"] else None,
                "join_time": datetime.fromisoformat(data["join_time"]) if data["join_time"] else None
            }
            for user_id, data in loaded_data.items()
        }
        return deserialized_streaks

def save_streaks(streaks_data):
    logger.info(f"Saving streaks data to file: {STREAKS_FILE}")
    serialized_data = {
        user_id: {
            "username": data["username"],
            "current_streak": data["current_streak"],
            "longest_streak": data["longest_streak"],
            "last_join_date": data["last_join_date"].isoformat() if isinstance(data["last_join_date"], datetime) else data["last_join_date"],
            "join_time": data["join_time"].isoformat() if isinstance(data["join_time"], datetime) else data["join_time"]
        }
        for user_id, data in streaks_data.items()
    }
    with open(STREAKS_FILE, 'w') as file:
        json.dump(serialized_data, file, indent=4)
    logger.info("Streaks data saved successfully.")

async def process_streak(member, before, after, study_channel_id, minimum_minutes):
    user_id = str(member.id)
    streaks_data = load_streaks()

    if user_id not in streaks_data:
        initialize_user_data(user_id, member.name)

    if is_joining_study_channel(after, study_channel_id):
        handle_join(user_id, member.name)
    elif is_leaving_study_channel(before, study_channel_id):
        handle_leave(user_id, member.name, minimum_minutes)

def is_joining_study_channel(after, study_channel_id):
    return after.channel and after.channel.id == study_channel_id

def is_leaving_study_channel(before, study_channel_id):
    return before.channel and before.channel.id == study_channel_id

def initialize_user_data(user_id, username):
    streaks_data = load_streaks()
    streaks_data[user_id] = {
        "username": username,
        "current_streak": 0,
        "longest_streak": 0,
        "last_join_date": None,
        "join_time": None
    }
    save_streaks(streaks_data)

def handle_join(user_id, username):
    streaks_data = load_streaks()
    join_time = datetime.now()
    streaks_data[user_id]["join_time"] = join_time.isoformat()
    logger.info(f"{username} joined the study channel.")
    save_streaks(streaks_data)

def handle_leave(user_id, username, minimum_minutes):
    streaks_data = load_streaks()
    logger.info(f'Handling leave for {username}')
    user_join_time = streaks_data[user_id]["join_time"]
    if user_join_time:
        logger.info(f"{username} has join time.")
        duration = datetime.now() - user_join_time
        if duration >= timedelta(minutes=minimum_minutes):
            streaks_data = update_streak(streaks_data, user_id, username)
        else:
            logger.info(f"{username} left the study channel before the minimum duration.")
    else:
        logger.info(f"{username} left the study channel but had no active join time.")

    streaks_data[user_id]["join_time"] = None
    save_streaks(streaks_data)

def update_streak(streaks_data, user_id, username):
    today = datetime.now().date()
    if streaks_data[user_id]["last_join_date"]:
        last_join_date = datetime.fromisoformat(streaks_data[user_id]["last_join_date"]).date()
        if today - last_join_date == timedelta(days=1):
            streaks_data = increment_streak(streaks_data, user_id, username)
        else:
            streaks_data = reset_streak(streaks_data, user_id, username)
    else:
        start_new_streak(streaks_data, user_id, username)
    streaks_data[user_id]["last_join_date"] = today.isoformat()
    return streaks_data

def increment_streak(streaks_data, user_id, username):
    streaks_data[user_id]["current_streak"] += 1
    streaks_data[user_id]["longest_streak"] = max(streaks_data[user_id]["longest_streak"], streaks_data[user_id]["current_streak"])
    logger.info(f"{username}'s streak increased to {streaks_data[user_id]['current_streak']} days.")
    return streaks_data

def reset_streak(streaks_data, user_id, username):
    streaks_data[user_id]["current_streak"] = 1
    logger.info(f"{username}'s streak reset to 1 day.")
    return streaks_data

def start_new_streak(streaks_data, user_id, username):
    streaks_data[user_id]["current_streak"] = 1
    streaks_data[user_id]["longest_streak"] = 1
    logger.info(f"{username} started a new streak of 1 day.")