"""
This module implements a Discord bot cog for managing user study streaks.

The StreaksCog class provides functionality to track, update, and display
user streaks based on their activity in a designated study voice channel.
It includes commands for users to check their streaks and for daily updates
of all users' streaks.

The module uses a JSON file to persist streak data across bot restarts.
"""

import json
import logging
import os
import shutil

import pytz
import tempfile

from datetime import datetime, timedelta, time, date
from discord.ext import commands, tasks
from discord import Member
from discord.types.voice import VoiceState

from bot import core
from responses import get_hooter_explanation
from typing import Dict


logger = logging.getLogger(__name__)

STREAKS_FILE = "streaks.json"

PST = pytz.timezone('US/Pacific')


class StreaksCog(commands.Cog):
  """
  A Discord bot cog for managing user study streaks.

  This cog tracks user activity in a designated study voice channel,
  updates streak counts, and provides commands for users to check their streaks.

  Attributes:
    bot: The Discord bot instance.
  """
  def __init__(self, bot):
    """
    Initialize the StreaksCog.

    Args:
      bot: The Discord bot instance.
    """
    self.bot = bot

  def cog_unload(self):
    """Cancel the daily streak update task when the cog is unloaded."""
    self.daily_streak_update.cancel()

  @tasks.loop(time=time(hour=21, minute=0, tzinfo=pytz.timezone(PST)))
  async def daily_streak_update(self):
    """
    Perform a daily update of all user streaks.

    This task runs daily at 9:00 PM Pacific Time, posting an update of all
    user streaks in the general channel.
    """
    channel = self.bot.get_channel(core.GENERAL_CHANNEL_ID)
    await self.list_all_streaks(channel)

  @daily_streak_update.before_loop
  async def before_daily_streak_update(self):
    """Ensure the bot is ready before starting the daily streak update task."""
    await self.bot.wait_until_ready()
    logger.info("Daily streak update task is ready!")

  @commands.Cog.listener()
  async def on_voice_state_update(self, member, before, after):
    """
    Listen for voice state updates and handle study channel activity.

    Args:
      member (discord.Member): The member whose voice state changed.
      before (discord.VoiceState): The previous voice state.
      after (discord.VoiceState): The new voice state.
    """
    if member.bot:
      return
    await self.handle_study_channel_activity(member, before, after)

  async def handle_study_channel_activity(self, member, before, after):
    """
    Process study channel activity for streak updates.

    Args:
      member (discord.Member): The member whose voice state changed.
      before (discord.VoiceState): The previous voice state.
      after (discord.VoiceState): The new voice state.
    """
    await self.process_streak(member, before, after, core.STUDY_CHANNEL_ID,
                              core.MINIMUM_MINUTES)

  @commands.command(name="reintroduce")
  async def reintroduce(self, ctx, member: Member = None):
    """
    Reintroduce the streak system to a user or the channel.

    Args:
      ctx (commands.Context): The command context.
      member (discord.Member, optional): The member to reintroduce the system to.
    """
    if member:
      message = f"Hey {member.display_name}, let me reintroduce you to how we keep things engaging around here!"
    else:
      message = "Looks like someone needs a refresher on how our awesome system works!"

    explanation = get_hooter_explanation()
    await ctx.send(f"{message}\n{explanation}")

  @commands.command(name="streak")
  async def streak(self, ctx, member: Member = None) -> None:
    """
    Display the current and longest streak for a user.

    Args:
      ctx (commands.Context): The command context.
      member (discord.Member, optional): The member to check the streak for.
                                         If not provided, checks for the command author.
    """
    if member is None:
      member = ctx.author

    streaks_data = self.load_streaks()
    await self.display_streak(ctx, member, streaks_data)

  async def process_streak(self, member: Member,
                           before: VoiceState,
                           after: VoiceState,
                           study_channel_id: int,
                           minimum_minutes: int) -> None:
    """
    Process a user's streak based on their voice channel activity.

    Args:
      member (discord.Member): The member whose voice state changed.
      before (discord.VoiceState): The previous voice state.
      after (discord.VoiceState): The new voice state.
      study_channel_id (int): The ID of the study channel.
      minimum_minutes (int): The minimum minutes required for a valid study session.
    """
    current_time = datetime.now(PST)
    user_id = str(member.id)
    streaks_data = self.load_streaks()

    if user_id not in streaks_data:
      self.initialize_user_data(user_id, member.name)
      self.save_streaks(streaks_data)

    if self.is_joining_study_channel(after, study_channel_id):
      logger.info(f"{user_id}, {member.name}, {current_time}")
      self.handle_join(user_id, member.name, current_time)
    elif self.is_leaving_study_channel(before, study_channel_id):
      channel = before.channel
      await self.handle_leave(user_id, member.name, minimum_minutes,
                              member, channel, current_time)

  async def initialize_streaks(self):
    """Initialize streak data for all guild members."""
    logger.info("Initializing streaks data...")
    streaks_data = self.load_streaks()

    for guild in core.bot.guilds:
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
          logger.info(
            f"Added {member.name} to streaks data with initial streak of 0.")

    self.save_streaks(streaks_data)
    logger.info("Streaks data initialization completed.")

  def initialize_user_data(self, user_id: str, username: str) -> None:
    """
    Initialize streak data for a new user.

    Args:
      user_id (str): The user's ID.
      username (str): The user's name.
    """
    streaks_data = self.load_streaks()
    streaks_data[user_id] = {
      "username": username,
      "current_streak": 0,
      "longest_streak": 0,
      "last_join_date": None,
      "join_time": None
    }
    self.save_streaks(streaks_data)

  def handle_join(self, user_id: str, username: str, join_time: datetime) -> None:
    """
    Handle a user joining the study channel.

    Args:
      user_id (str): The user's ID.
      username (str): The user's name.
      join_time (datetime): The time at which the user joined the voice channel
    """
    streaks_data = self.load_streaks()
    streaks_data[user_id]["join_time"] = join_time
    logger.info(f"{username} joined the study channel at {join_time}.")
    if self.save_streaks(streaks_data):
      logger.info(f"Successfully updated join time for {username} at {join_time}")
    else:
      logger.error(f"Failed to update join time for {username}")

  async def handle_leave(self, user_id: str, username: str, minimum_minutes: int, member: Member,
                         channel, current_time: datetime):
    """
    Handle a user leaving the study channel.

    Args:
      user_id (str): The user's ID.
      username (str): The user's name.
      minimum_minutes (int): The minimum minutes required for a valid study session.
      member (discord.Member): The member who left the channel.
      channel (discord.TextChannel): The channel to send notifications to.
      current_time (datetime): The time that the leave event occurs.
    """
    streaks_data = self.load_streaks()
    logger.info(f'Handling leave for {username} at {current_time}')
    user_join_time = streaks_data[user_id]["join_time"]

    if user_join_time is None:
      logger.warning(f"{username} left the study channel but had no active join time.")
    else:
      logger.info(
        f"{username} joined at {user_join_time} and left at {current_time}.")
      duration = current_time - user_join_time
      if duration >= timedelta(minutes=minimum_minutes):
        previous_streak = streaks_data[user_id]["current_streak"]
        updated = self.update_streak(user_id, username, current_time)
        if updated:
          await self.send_streak_notification(user_id, member, channel, previous_streak)
        else:
          logger.error(f"Failed to update streak for {username}")
      else:
        logger.info(f"{username} left the study channel after {duration.total_seconds() / 60:.2f} minutes, before the minimum duration.")
        await channel.send(
          f"Hey {member.mention}, you left the study channel before the minimum "
          f"{minimum_minutes} minutes. Keep at it next time to maintain your streak!")

    streaks_data = self.load_streaks()
    streaks_data[user_id]["join_time"] = None
    if self.save_streaks(streaks_data):
      logger.info(f"Successfully reset join time for {username}")
    else:
      logger.error(f"Failed to reset join time for {username}")

  async def send_streak_notification(self, user_id, member, channel, previous_streak):
    streaks_data = self.load_streaks()
    current_streak = streaks_data[user_id]["current_streak"]

    if current_streak > previous_streak:
      await channel.send(
        f"Congratulations, {member.mention}! Your streak has increased to {current_streak} days.")
    else:
      await channel.send(
        f"Great job, {member.mention}! You maintained your streak of {current_streak} days.")

  def update_streak(self, user_id, username, current_time: datetime) -> bool:
    """
    Update a user's streak based on their study activity.

    Args:
      user_id (str): The user's ID.
      username (str): The user's name.
      current_time (datetime): The time at which the streak is being updated.

    Returns:
      bool: True if the streak was updated or already updated today, False if an error occurred.
    """
    streaks_data = self.load_streaks()
    user_data = streaks_data[user_id]
    today = current_time.date()
    last_join_date = user_data["last_join_date"]

    logger.info(f"Updating streak for {username}. Current date: {today}, Last join date: {last_join_date}")

    if last_join_date is None:
      user_data = self.start_new_streak(user_data)
    elif (today - last_join_date).days == 1:
      user_data = self.increment_streak(user_data)
    elif (today - last_join_date).days == 0:
      logger.info(f"{username} has already successfully incremented today. Skipping today")
      return True
    elif (today - last_join_date).days > 1:
      user_data = self.reset_streak(user_data)
    else:
      logger.warning(f"Unexpected behavior: {username}'s last join date ({last_join_date}) is not before today ({today}).")
      return False

    user_data["last_join_date"] = today
    streaks_data[user_id] = user_data
    return self.save_streaks(streaks_data)

  async def list_all_streaks(self, channel):
    """
    List all user streaks in the given channel.

    Args:
      channel (discord.TextChannel): The channel to send the streak list to.
    """
    streaks_data = self.load_streaks()
    streaks_message = "**Daily Streak Update:**\n"
    for user_id, data in streaks_data.items():
      username = data["username"]
      current_streak = data["current_streak"]
      streaks_message += f"{username}: {current_streak} days\n"

    await channel.send(streaks_message)

  @staticmethod
  def load_streaks():
    """
    Load streak data from the JSON file.

    Returns:
      dict: The loaded and deserialized streak data.
    """
    if not os.path.exists(STREAKS_FILE):
      logger.info(
        f"Streaks file '{STREAKS_FILE}' does not exist. Creating empty file.")
      with open(STREAKS_FILE, 'w') as file:
        json.dump({}, file)
    else:
      logger.info(f"Loading streaks data from file: {STREAKS_FILE}")

    try:
      with open(STREAKS_FILE, 'r') as file:
        loaded_data = json.load(file)
        deserialized_streaks = {
          user_id: {
            "username": data["username"],
            "current_streak": data["current_streak"],
            "longest_streak": data["longest_streak"],
            "last_join_date": datetime.fromisoformat(
              data["last_join_date"]).date() if data["last_join_date"] else None,
            "join_time": datetime.fromisoformat(data["join_time"]) if data[
              "join_time"] else None
          }
          for user_id, data in loaded_data.items()
        }
        logger.debug(f"Deserialized streaks: {deserialized_streaks}")
        return deserialized_streaks
    except json.JSONDecodeError:
      logger.error(f"Failed to parse JSON from {STREAKS_FILE}. File may be corrupted.")
      return {}
    except Exception as e:
      logger.error(f"An error occurred while loading streaks: {str(e)}")
      return {}

  @staticmethod
  def save_streaks(streaks_data) -> bool:
    """
    Save streak data to the JSON file.

    Args:
      streaks_data (dict): The streak data to save.
    """
    logger.info(f"Saving streaks data to file: {STREAKS_FILE}")
    serialized_data = {
      user_id: {
        "username": data["username"],
        "current_streak": data["current_streak"],
        "longest_streak": data["longest_streak"],
        "last_join_date": data["last_join_date"].isoformat() if isinstance(
          data["last_join_date"], date) else None,
        "join_time": data["join_time"].isoformat() if isinstance(
          data["join_time"], datetime) else None
      }
      for user_id, data in streaks_data.items()
    }
    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
    try:
      json.dump(serialized_data, temp_file, indent=4)
      temp_file.flush()
      os.fsync(temp_file.fileno())
      temp_file.close()
      shutil.move(temp_file.name, STREAKS_FILE)
      logger.info("Streaks data saved successfully.")
    except Exception as e:
      logger.error(f"Failed to save streaks data: {str(e)}")
      os.unlink(temp_file.name)

    # Validate the save operation
    loaded_data = StreaksCog.load_streaks()
    if loaded_data != streaks_data:
      logger.error("Validation failed: Saved data does not match original data.")
      return False
    return True

  @staticmethod
  def is_joining_study_channel(after, study_channel_id):
    """
    Check if a user is joining the study channel.

    Args:
      after (discord.VoiceState): The new voice state.
      study_channel_id (int): The ID of the study channel.

    Returns:
      bool: True if the user is joining the study channel, False otherwise.
    """
    return after.channel and after.channel.id == study_channel_id

  @staticmethod
  def is_leaving_study_channel(before, study_channel_id):
    """
    Check if a user is leaving the study channel.

    Args:
      before (discord.VoiceState): The previous voice state.
      study_channel_id (int): The ID of the study channel.

    Returns:
      bool: True if the user is leaving the study channel, False otherwise.
    """
    return before.channel and before.channel.id == study_channel_id

  @staticmethod
  def increment_streak(user_data: Dict):
    """
    Increment a user's streak.

    Args:
      user_data (Dict):

    Returns:
      dict: The user's data for streaks.
    """
    user_data["current_streak"] += 1
    user_data["longest_streak"] = max(
      user_data["longest_streak"],
      user_data["current_streak"])
    logger.info(
      f"{user_data['username']}'s streak increased to {user_data['current_streak']} days.")
    return user_data

  @staticmethod
  def reset_streak(user_data):
    """
    Reset a user's streak to 1.

    Args:
      user_data (Dict):

    Returns:
      dict: The user's data for streaks.
    """
    user_data["current_streak"] = 1
    logger.info(f"{user_data['username']}'s streak reset to 1 day.")
    return user_data

  @staticmethod
  def start_new_streak(user_data):
    """
    Start a new streak for a user.

    Args:
      user_data (Dict):

    Returns:
      dict: The user's data for streaks.
    """
    user_data["current_streak"] = 1
    user_data["longest_streak"] = 1
    logger.info(f"{user_data['username']} started a new streak of 1 day.")
    return user_data

  @staticmethod
  async def display_streak(ctx, member, streaks_data):
    """
    Display the streak information for a given member.

    Args:
      ctx (commands.Context): The command context.
      member (discord.Member): The member to display the streak for.
      streaks_data (dict): The loaded streak data.
    """
    user_id = str(member.id)

    if user_id in streaks_data:
      current_streak = streaks_data[user_id]["current_streak"]
      longest_streak = streaks_data[user_id]["longest_streak"]
      username = streaks_data[user_id]["username"]
      message = f"{username}'s streaks:\n" \
                f"Current streak: {current_streak} days\n" \
                f"Longest streak: {longest_streak} days"
      await ctx.send(message)
    else:
      await ctx.send(f"{member.mention} hasn't started a streak yet.")
