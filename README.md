
# Hooter the Tutor

Hooter the Tutor is a Discord bot designed to promote accountability and track study streaks for users in a Discord server. It encourages consistent study habits by monitoring user activity in a dedicated study voice channel.

## Features

- **Streak Tracking**: Automatically tracks user study streaks based on time spent in a designated voice channel.
- **Daily Updates**: Provides daily streak updates for all users at 9 PM PST.
- **Welcome Messages**: Greets new members with an explanation of the accountability system.
- **User Commands**: Allows users to check their current and longest streaks.
- **Reintroduction Command**: Provides a refresher on how the accountability system works.

## Application Structure

The application is organized into several key directories and files:

- `bot/`: Contains core bot functionality
  - `commands.py`: Defines bot commands
  - `core.py`: Core bot setup and configuration
  - `events.py`: Handles Discord events
  - `tasks.py`: Defines scheduled tasks
- `cogs/`: Contains modular extensions for the bot
  - `leetcode.py`: LeetCode-related functionality
  - `streaks.py`: Streak tracking functionality
- `models/`: Contains different AI model integrations
  - `octoAI.py`: OctoAI model integration
  - `openAI.py`: OpenAI model integration
- `scripts/`: Contains utility scripts
  - `build_and_run.sh`: Script for building and running the bot
  - `install_dependencies.sh`: Script for installing dependencies
- `main.py`: The entry point of the application
- `choose_model.py`: Handles model selection
- `responses.py`: Defines bot responses
- `Dockerfile`: For containerizing the application
- `requirements.txt`: Lists Python dependencies

This structure allows for modular development and easy expansion of the bot's functionality.

## Setup
- Install Python version 3.11 (pyenv recommended)
- Clone the repository
- Run the `./scripts/install_dependencies.sh` script to install requirements and setup a virtual environment (`.venv`)
- Activate your `.venv`
- Create a `.env` file in the project root and add your Discord bot token:
   ```
   DISCORD_TOKEN=your_discord_bot_token_here
   OPENAI_API_KEY=your_openAI_key_here
   OCTOAI_API_TOKEN=your_octoAI_key_here
   ```
- Configure the channel IDs in `main.py`:
   ```python
   STUDY_CHANNEL_ID = your_study_channel_id
   GENERAL_CHANNEL_ID = your_general_channel_id
   ```
- Choose your model in main.py
   ```python
   client = your_chosen_model
   ```
- Run the bot:
   ```
   python main.py
   ```