# Unit Testing Pattern for Discord Bot Cogs

## Overview

This document outlines the pattern for writing unit tests for Discord bot cogs, specifically for the StreaksCog. These tests use pytest and follow a consistent structure to ensure thorough testing of cog functionality.

## Key Components

1. **pytest**: The testing framework used for writing and running tests.
2. **unittest.mock**: Used for creating mock objects to simulate Discord.py classes and methods.
3. **AsyncMock**: A special type of mock for asynchronous methods.
4. **MagicMock**: A powerful mock object that can mimic most Python objects.

## Test Structure

Each test function follows this general structure:

1. **Arrange**: Set up the test environment and mock necessary objects.
2. **Act**: Call the method being tested.
3. **Assert**: Verify the expected outcomes.

## Naming Convention

Test functions are named using the following pattern:
`test_[method_name]_[scenario_being_tested]`

For example: `test_reintroduce_command_no_member`

## Common Patterns

### 1. Mocking Discord.py Objects

Discord.py objects (like `Member`, `VoiceState`, etc.) are often mocked:

```python
member = MagicMock(spec=Member)
```

### 2. Mocking Cog Methods

Internal cog methods that aren't the focus of a particular test are often mocked:

```python
cog.process_streak = AsyncMock()
```

### 3. Asserting Method Calls

Verify that methods were called with the expected arguments:

```python
cog.process_streak.assert_called_once_with(member, before, after, cog.core.STUDY_CHANNEL_ID, cog.core.MINIMUM_MINUTES)
```

### 4. Checking Sent Messages

For commands that send messages, assert the content of the sent message:

```python
ctx.send.assert_called_once()
sent_message = ctx.send.call_args[0][0]
assert "Expected content" in sent_message
```

## Adding New Tests

To add a new test:

1. Create a new function in the appropriate test file (e.g., `test_streaks.py`).
2. Name the function following the naming convention.
3. Use the Arrange-Act-Assert pattern.
4. Mock any necessary Discord.py objects or cog methods.
5. Call the method being tested.
6. Assert the expected outcomes.

Example:

```python
@pytest.mark.asyncio
async def test_new_method_specific_scenario(cog):
    # Arrange
    # Set up mocks and input data

    # Act
    # Call the method being tested

    # Assert
    # Verify the expected outcomes
```

Remember to use `@pytest.mark.asyncio` for testing asynchronous methods.

## Running Tests

To run the tests, use the following command in the project root directory:

```
pytest tests/unit
```

This will run all tests in the `tests/unit` directory.