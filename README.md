
# Hooter the Tutor

Hooter the Tutor is a Discord bot designed to promote accountability and track study streaks for users in a Discord server. It encourages consistent study habits by monitoring user activity in a dedicated study voice channel.

## Features

- **Streak Tracking**: Automatically tracks user study streaks based on time spent in a designated voice channel.
- **Daily Updates**: Provides daily streak updates for all users at 9 PM PST.
- **Welcome Messages**: Greets new members with an explanation of the accountability system.
- **User Commands**: Allows users to check their current and longest streaks.
- **Reintroduction Command**: Provides a refresher on how the accountability system works.

## Setup
- Install Python version 3.11 (pyenv recommended)
- Clone the repository
- Run the `install_dependencies.sh` script to install requirements and setup a virtual environment (`.venv`)
- Activate your `.venv`
- Create a `.env` file in the project root and add your Discord bot token:
   ```
   DISCORD_TOKEN=your_discord_bot_token_here
   ```
- Configure the channel IDs in `main.py`:
   ```python
   STUDY_CHANNEL_ID = your_study_channel_id
   GENERAL_CHANNEL_ID = your_general_channel_id
   ```
- Run the bot:
   ```
   python main.py
   ```