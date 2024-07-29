import discord
import pytest
from unittest.mock import Mock, patch, AsyncMock
from cogs import leetcode


@pytest.fixture
def bot():
  return Mock()


@pytest.fixture
def cog(bot):
  return leetcode.LeetCodeCog(bot)


def test_fetch_leetcode_profile_success(cog):
  """
  Test the successful retrieval and parsing of a LeetCode profile.

  This test verifies that the fetch_leetcode_profile method of the LeetCodeCog
  class correctly handles a successful API response. It checks that the method:
  1. Makes the correct API call
  2. Properly handles a successful status code (200)
  3. Correctly parses the JSON response
  4. Returns the expected data structure

  The test uses mocking to simulate a successful API response without making
  an actual network call.

  Args:
      cog (LeetCodeCog): An instance of the LeetCodeCog class to be tested.

  Raises:
      AssertionError: If any of the test conditions are not met.
  """
  expected_url = "https://leetcode-stats-api.herokuapp.com/testuser"
  mock_response = {
    'easySolved': 10,
    'totalEasy': 100,
    'mediumSolved': 20,
    'totalMedium': 200,
    'hardSolved': 5,
    'totalHard': 50
  }

  with patch('requests.get') as mock_get:
    # Configure the mock to return a successful response
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = mock_response

    # Act
    result = cog.fetch_leetcode_profile('testuser')

    # Assert
    mock_get.assert_called_once_with(expected_url)

    # Check that the result is not None (indicating successful retrieval)
    assert result is not None, "Expected a non-None result"

    # Verify that all expected keys are present in the result
    expected_keys = ['easySolved', 'totalEasy', 'mediumSolved', 'totalMedium',
                     'hardSolved', 'totalHard']
    for key in expected_keys:
      assert key in result, f"Expected key '{key}' not found in result"

    # Check that the values in the result match the mock response
    for key, value in mock_response.items():
      assert result[
               key] == value, f"Mismatch for key '{key}': expected {value}, got {result[key]}"

    # Additional specific checks can be added here if needed
    assert result['easySolved'] == 10, "Incorrect value for 'easySolved'"
    assert result['totalEasy'] == 100, "Incorrect value for 'totalEasy'"
    assert result['mediumSolved'] == 20, "Incorrect value for 'mediumSolved'"
    assert result ['totalMedium'] == 200, "Incorrect value for 'totalMedium'"
    assert result ['hardSolved'] == 5, "Incorrect value for 'hardSolved'"
    assert result ['totalHard'] == 50,  "Incorrect value for 'totalHard'"

  # The 'with' block ensures that the patch is properly removed after the test

def test_fetch_leetcode_profile_failure(cog):
  with patch('requests.get') as mock_get:
    mock_get.return_value.status_code = 404

    result = cog.fetch_leetcode_profile('nonexistentuser')
    assert result is None

@pytest.mark.asyncio
async def test_leetcode_command_success(cog):
  """
  Test the successful execution of the LeetCode command.

  This test verifies that the leetcode command in the LeetCodeCog class
  correctly handles a successful profile retrieval. It checks that the method:
  1. Calls fetch_leetcode_profile with the correct username
  2. Creates an appropriate discord.Embed object with the profile data
  3. Sends the embed via the Discord context

  The test uses mocking to simulate both the Discord context and the
  fetch_leetcode_profile method to avoid external dependencies.

  Args:
      cog (LeetCodeCog): An instance of the LeetCodeCog class to be tested.

  Raises:
      AssertionError: If any of the test conditions are not met.
  """
  # Arrange
  ctx = AsyncMock()
  username = 'testuser'
  mock_profile_data = {
    'easySolved': 10, 'totalEasy': 100,
    'mediumSolved': 20, 'totalMedium': 200,
    'hardSolved': 5, 'totalHard': 50
  }

  with patch.object(cog, 'fetch_leetcode_profile') as mock_fetch:
    # Configure the mock to return our test profile data
    mock_fetch.return_value = mock_profile_data

    # Act
    # We need to call the callback directly, as it would be called by Discord.py
    await cog.leetcode.callback(cog, ctx, username)

    # Assert
    # Verify that fetch_leetcode_profile was called with the correct username
    mock_fetch.assert_called_once_with(username)

    # Verify that ctx.send was called once
    ctx.send.assert_called_once()

    # Verify that ctx.send was called with an Embed object
    call_args = ctx.send.call_args
    assert len(call_args[1]) == 1, "Expected one keyword argument"
    assert 'embed' in call_args[1], "Expected 'embed' in keyword arguments"
    embed = call_args[1]['embed']
    assert isinstance(embed,
                      discord.Embed), "Expected an instance of discord.Embed"

    # Verify the contents of the Embed
    assert embed.title == f"LeetCode Profile: {username}"
    assert embed.color == discord.Color.blue()

    # Check that all fields are present with correct values
    expected_fields = [
      ("Username", username, False),
      ("Easy Solved", f"10 / 100", True),
      ("Medium Solved", f"20 / 200", True),
      ("Hard Solved", f"5 / 50", True)
    ]
    for i, (name, value, inline) in enumerate(expected_fields):
      assert embed.fields[i].name == name, f"Incorrect name for field {i}"
      assert embed.fields[i].value == value, f"Incorrect value for field {i}"
      assert embed.fields[
               i].inline == inline, f"Incorrect inline setting for field {i}"

  # The 'with' block ensures that the patch is properly removed after the test

@pytest.mark.asyncio
async def test_leetcode_command_failure(cog):
  """
  Test the LeetCode command's behavior when profile retrieval fails.

  This test verifies that the leetcode command in the LeetCodeCog class
  correctly handles a failed profile retrieval. It checks that the method:
  1. Calls fetch_leetcode_profile with the correct username
  2. Sends an appropriate error message when no data is returned

  Args:
      cog (LeetCodeCog): An instance of the LeetCodeCog class to be tested.

  Raises:
      AssertionError: If any of the test conditions are not met.
  """
  # Arrange
  ctx = AsyncMock()
  username = 'nonexistentuser'

  with patch.object(cog, 'fetch_leetcode_profile') as mock_fetch:
    # Configure the mock to return None, simulating a failed retrieval
    mock_fetch.return_value = None

    # Act
    await cog.leetcode.callback(cog, ctx, username)

    # Assert
    mock_fetch.assert_called_once_with(username)
    ctx.send.assert_called_once_with(f"Could not fetch data for {username}.")

# Add more tests for edge cases and other scenarios