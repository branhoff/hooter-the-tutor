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
  - `core.py`: Core bot setup and configuration
  - `events.py`: Handles Discord events
  - `setup.py`: Bot setup utilities
- `cogs/`: Contains modular extensions for the bot
  - `leetcode.py`: LeetCode-related functionality
  - `streaks.py`: Streak tracking functionality
- `models/`: Contains different AI model integrations
  - `octoAI.py`: OctoAI model integration
  - `openAI.py`: OpenAI model integration
- `domain/`: Domain models and business logic
  - `streak_data.py`: Streak data models
- `tests/`: Unit tests
  - `unit/`: Unit test files
- `scripts/`: Contains utility scripts
  - `build_and_run.sh`: Script for building and running the bot
  - `install_dependencies.sh`: Script for installing dependencies
  - `run-dev.sh`: Script for local Docker development
- `requires/`: Dependency files
  - `requirements.txt`: Production dependencies
  - `dev.txt`: Development dependencies
- `docs/`: Documentation files
- `main.py`: The entry point of the application
- `choose_model.py`: Handles model selection
- `responses.py`: Defines bot responses
- `Dockerfile`: Production Docker configuration
- `Dockerfile.local`: Local development Docker configuration

This structure allows for modular development and easy expansion of the bot's functionality.

## Setup

### Option 1: Docker Development Setup (Recommended)

For a containerized development environment with all tools pre-installed:

1. **Prerequisites**
   - Install Docker on your system
   - Clone the repository

2. **Create your `.env` file** in the project root:
```
   DISCORD_TOKEN=your_discord_bot_token_here
   OPENAI_API_KEY=your_openAI_key_here
   OCTOAI_API_TOKEN=your_octoAI_key_here
```

3. **Configure the channel IDs** in `main.py`:
```python
   STUDY_CHANNEL_ID = your_study_channel_id
   GENERAL_CHANNEL_ID = your_general_channel_id
```

4. **Choose your model** in `main.py`:
```python
   client = your_chosen_model
```

5. **Run the development container**:
```bash
   ./scripts/run-dev.sh
```

   This script will:
   - Build the production Docker image (`Dockerfile`)
   - Build the local development image (`Dockerfile.local`) that extends production
   - Drop you into an interactive bash shell with all development tools

6. **Inside the container**, you can:
```bash
   # Run the bot
   python main.py
   
   # Run tests
   pytest
   
   # Run specific tests
   pytest tests/unit/test_leetcode.py
   
   # Run with coverage
   pytest --cov
   
   # Format code
   black .
   
   # Lint code
   flake8
```

7. **Exit the container**:
```bash
   exit
```

**Docker Architecture:**
- `Dockerfile`: Production-ready, minimal image
- `Dockerfile.local`: Extends the production image with development tools and dependencies from `requires/dev.txt`
- This approach ensures your local development environment stays in sync with production

### Option 2: Manual Python Setup

For development without Docker:

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
- Choose your model in `main.py`:
```python
   client = your_chosen_model
```
- Run the bot:
```
   python main.py
```

## Running Unit Tests

This project uses pytest for unit testing.

### Docker Environment (Recommended)

1. Start the development container:
```bash
   ./scripts/run-dev.sh
```
2. Inside the container, run tests:
```bash
   pytest tests/unit
```

### Local Python Environment

1. Navigate to the root directory of the project in your terminal.
2. Make sure you've run the `./scripts/install_dependencies.sh` script which will install testing requirements from `requires/dev.txt`:
```bash
   pip install -r requires/dev.txt
```
3. Run the following command to execute all unit tests:
```bash
   pytest tests/unit
```

### Test Commands

- Run all unit tests:
```bash
  pytest tests/unit
```
- Run a specific test file:
```bash
  pytest tests/unit/test_leetcode.py
```
- Run a specific test function:
```bash
  pytest tests/unit/test_leetcode.py::test_leetcode_command_success
```
- Verbose output:
```bash
  pytest -v tests/unit
```
- With coverage:
```bash
  pytest --cov tests/unit
```

## Deployment

The production `Dockerfile` is designed for deployment to container platforms like Google Cloud Run. See `docs/deploy_to_google_run.md` for deployment instructions.