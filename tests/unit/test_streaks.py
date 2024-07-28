from unittest.mock import AsyncMock, Mock, MagicMock

import pytest
from discord import Member, VoiceState

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
    cog.bot.get_channel.assert_called_once_with(cog.core.GENERAL_CHANNEL_ID)
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
    cog.handle_study_channel_activity.assert_called_once_with(member, before, after)

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
        member, before, after, cog.core.STUDY_CHANNEL_ID, cog.core.MINIMUM_MINUTES
    )

@pytest.mark.asyncio
async def test_streak_command_with_member(cog):
    # Arrange
    ctx = AsyncMock()
    member = MagicMock(spec=Member)
    cog.load_streaks = MagicMock(return_value={})
    cog.display_streak = AsyncMock()

    # Act
    await cog.streak(ctx, member)

    # Assert
    cog.load_streaks.assert_called_once()
    cog.display_streak.assert_called_once_with(ctx, member, {})

@pytest.mark.asyncio
async def test_streak_command_without_member(cog):
    # Arrange
    ctx = AsyncMock()
    ctx.author = MagicMock(spec=Member)
    cog.load_streaks = MagicMock(return_value={})
    cog.display_streak = AsyncMock()

    # Act
    await cog.streak(ctx)

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