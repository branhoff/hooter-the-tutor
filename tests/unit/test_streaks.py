from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock, MagicMock, patch

import pytest
from discord import Member, VoiceState

from bot import core
from cogs import streaks


@pytest.fixture
def bot():
  return Mock()


@pytest.fixture
def cog(bot):
  return streaks.StreaksCog(bot)


@pytest.mark.asyncio
async def test_reintroduce_command_no_member(cog):
  # Arrange
  ctx = AsyncMock()
  ctx.send = AsyncMock()

  # Act
  await cog.reintroduce.callback(cog, ctx)

  # Assert
  ctx.send.assert_called_once()
  sent_message = ctx.send.call_args[0][0]
  assert "Looks like someone needs a refresher" in sent_message
  assert "how our awesome system works" in sent_message


@pytest.mark.asyncio
async def test_reintroduce_command_with_member(cog):
  # Arrange
  ctx = AsyncMock()
  ctx.send = AsyncMock()
  member = AsyncMock(spec=Member)
  member.display_name = "TestUser"

  # Act
  await cog.reintroduce.callback(cog, ctx, member)

  # Assert
  ctx.send.assert_called_once()
  sent_message = ctx.send.call_args[0][0]
  assert f"Hey TestUser, let me reintroduce you" in sent_message
  assert "how we keep things engaging around here" in sent_message


@pytest.mark.asyncio
async def test_daily_streak_update(cog):
  # Arrange
  cog.bot = MagicMock()
  channel = AsyncMock()
  cog.bot.get_channel.return_value = channel
  cog.list_all_streaks = AsyncMock()

  # Act
  await cog.daily_streak_update()

  # Assert
  cog.bot.get_channel.assert_called_once_with(core.GENERAL_CHANNEL_ID)
  cog.list_all_streaks.assert_called_once_with(channel)


@pytest.mark.asyncio
async def test_before_daily_streak_update(cog):
  # Arrange
  cog.bot = AsyncMock()

  # Act
  await cog.before_daily_streak_update()

  # Assert
  cog.bot.wait_until_ready.assert_called_once()


@pytest.mark.asyncio
async def test_on_voice_state_update_non_bot(cog):
  # Arrange
  member = MagicMock(spec=Member)
  member.bot = False
  before = MagicMock(spec=VoiceState)
  after = MagicMock(spec=VoiceState)
  cog.handle_study_channel_activity = AsyncMock()

  # Act
  await cog.on_voice_state_update(member, before, after)

  # Assert
  cog.handle_study_channel_activity.assert_called_once_with(member, before,
                                                            after)


@pytest.mark.asyncio
async def test_on_voice_state_update_bot(cog):
  # Arrange
  member = MagicMock(spec=Member)
  member.bot = True
  before = MagicMock(spec=VoiceState)
  after = MagicMock(spec=VoiceState)
  cog.handle_study_channel_activity = AsyncMock()

  # Act
  await cog.on_voice_state_update(member, before, after)

  # Assert
  cog.handle_study_channel_activity.assert_not_called()


@pytest.mark.asyncio
async def test_handle_study_channel_activity(cog):
  # Arrange
  member = MagicMock(spec=Member)
  before = MagicMock(spec=VoiceState)
  after = MagicMock(spec=VoiceState)
  cog.process_streak = AsyncMock()

  # Act
  await cog.handle_study_channel_activity(member, before, after)

  # Assert
  cog.process_streak.assert_called_once_with(
    member, before, after, core.STUDY_CHANNEL_ID, core.MINIMUM_MINUTES
  )


@pytest.mark.asyncio
async def test_streak_command_with_member(cog):
  # Arrange
  ctx = AsyncMock()
  ctx.author = AsyncMock()  # Add this line
  member = AsyncMock(spec=Member)
  cog.load_streaks = MagicMock(return_value={})
  cog.display_streak = AsyncMock()

  # Act
  await cog.streak.callback(cog, ctx, member)  # Change this line

  # Assert
  cog.load_streaks.assert_called_once()
  cog.display_streak.assert_called_once_with(ctx, member, {})


@pytest.mark.asyncio
async def test_streak_command_without_member(cog):
  # Arrange
  ctx = AsyncMock()
  ctx.author = AsyncMock(spec=Member)
  cog.load_streaks = MagicMock(return_value={})
  cog.display_streak = AsyncMock()

  # Act
  await cog.streak.callback(cog, ctx)  # Change this line

  # Assert
  cog.load_streaks.assert_called_once()
  cog.display_streak.assert_called_once_with(ctx, ctx.author, {})


@pytest.mark.asyncio
async def test_reintroduce_command_explanation_content(cog):
  # Arrange
  ctx = AsyncMock()
  ctx.send = AsyncMock()

  # Act
  await cog.reintroduce.callback(cog, ctx)

  # Assert
  ctx.send.assert_called_once()
  sent_message = ctx.send.call_args[0][0]

  # Check for the introductory message
  assert "Looks like someone needs a refresher on how our awesome system works!" in sent_message

  # Check for key parts of the explanation
  expected_content = [
    "Join the Accountability Room:",
    "Daily Accountability Sessions:",
    "Session Flexibility:",
    "Session Wrap-Up:",
    "Community Engagement:",
    "Track Your Progress:",
    "Streak Freeze:",
  ]

  for content in expected_content:
    assert content in sent_message, f"'{content}' not found in the explanation"


@pytest.mark.asyncio
async def test_increment_streak_next_day(cog):
  # Arrange
  user_id = "12345"
  username = "TestUser"

  # Mock initial streak data
  initial_streak_data = {
    user_id: {
      "username": username,
      "current_streak": 1,
      "longest_streak": 1,
      "last_join_date": (datetime.now() - timedelta(days=1)).date(),
      "join_time": None
    }
  }

  # Mock member and channel
  member = AsyncMock(spec=Member)
  member.id = user_id
  member.name = username
  channel = AsyncMock()

  with patch.object(cog, 'load_streaks', return_value=initial_streak_data), \
      patch.object(cog, 'save_streaks') as mock_save, \
      patch('cogs.streaks.datetime') as mock_datetime:
    # Set join time to next day
    join_time = datetime.now()
    mock_datetime.now.return_value = join_time

    # Simulate joining
    cog.handle_join(user_id, username, join_time)

    # Set leave time to 30 minutes after join time
    leave_time = join_time + timedelta(minutes=30)
    mock_datetime.now.return_value = leave_time

    # Act: Simulate leaving
    await cog.handle_leave(user_id, username, core.MINIMUM_MINUTES, member,
                           channel, leave_time)

    # Assert
    mock_save.assert_called()
    saved_data = mock_save.call_args[0][0]
    assert saved_data[user_id]["current_streak"] == 2
    assert saved_data[user_id]["longest_streak"] == 2
    assert saved_data[user_id]["last_join_date"] == leave_time.date()
    assert saved_data[user_id]["join_time"] is None


@pytest.mark.asyncio
async def test_reset_streak_after_two_days(cog):
  # Arrange
  user_id = "12345"
  username = "TestUser"

  # Mock initial streak data
  initial_streak_data = {
    user_id: {
      "username": username,
      "current_streak": 5,
      "longest_streak": 10,
      "last_join_date": (datetime.now() - timedelta(days=2)).date(),
      "join_time": None
    }
  }

  # Mock member and channel
  member = AsyncMock(spec=Member)
  member.id = user_id
  member.name = username
  channel = AsyncMock()

  with patch.object(cog, 'load_streaks', return_value=initial_streak_data), \
      patch.object(cog, 'save_streaks') as mock_save, \
      patch('cogs.streaks.datetime') as mock_datetime:
    # Set join time to 2 days later
    join_time = datetime.now() + timedelta(days=2)
    mock_datetime.now.return_value = join_time

    # Simulate joining
    cog.handle_join(user_id, username, join_time)

    # Set leave time to 30 minutes after join time
    leave_time = join_time + timedelta(minutes=30)
    mock_datetime.now.return_value = leave_time

    # Act: Simulate leaving
    await cog.handle_leave(user_id, username, core.MINIMUM_MINUTES, member,
                           channel, leave_time)

    # Assert
    mock_save.assert_called()
    saved_data = mock_save.call_args[0][0]
    assert saved_data[user_id]["current_streak"] == 1
    assert saved_data[user_id]["longest_streak"] == 10
    assert saved_data[user_id]["last_join_date"] == leave_time.date()
    assert saved_data[user_id]["join_time"] is None

@pytest.mark.asyncio
async def test_multiple_joins_in_one_day(cog):
  # Arrange
  user_id = "12345"
  username = "TestUser"

  # Mock initial streak data
  initial_streak_data = {
    user_id: {
      "username": username,
      "current_streak": 1,
      "longest_streak": 1,
      "last_join_date": (datetime.now() - timedelta(days=1)).date(),
      "join_time": None
    }
  }

  # Mock member and channel
  member = AsyncMock(spec=Member)
  member.id = user_id
  member.name = username
  channel = AsyncMock()

  with patch.object(cog, 'load_streaks', return_value=initial_streak_data), \
      patch.object(cog, 'save_streaks') as mock_save, \
      patch('cogs.streaks.datetime') as mock_datetime:
    # Simulate first join-leave cycle
    join_time1 = datetime.now()
    mock_datetime.now.return_value = join_time1
    cog.handle_join(user_id, username, join_time1)

    leave_time1 = join_time1 + timedelta(minutes=30)
    mock_datetime.now.return_value = leave_time1
    await cog.handle_leave(user_id, username, core.MINIMUM_MINUTES, member,
                           channel, leave_time1)

    # Simulate second join-leave cycle on the same day
    join_time2 = leave_time1 + timedelta(hours=2)
    mock_datetime.now.return_value = join_time2
    cog.handle_join(user_id, username, join_time2)

    leave_time2 = join_time2 + timedelta(minutes=30)
    mock_datetime.now.return_value = leave_time2
    await cog.handle_leave(user_id, username, core.MINIMUM_MINUTES, member,
                           channel, leave_time2)

    # Assert
    mock_save.assert_called()
    saved_data = mock_save.call_args[0][0]
    assert saved_data[user_id][
             "current_streak"] == 2  # Streak should only increment once
    assert saved_data[user_id]["longest_streak"] == 2
    assert saved_data[user_id]["last_join_date"] == leave_time2.date()
    assert saved_data[user_id]["join_time"] is None
