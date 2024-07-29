import logging

from discord import Message

from bot.core import bot
from choose_model import choose_model
from responses import get_hooter_explanation

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

client = "openAI"
model = choose_model(client)


@bot.event
async def on_member_join(member):
  guild = member.guild
  welcome_channel = guild.system_channel

  if welcome_channel:
    welcome_message = f"Whoo-hoo! Welcome, {member.display_name}! 🎉 I’m Hooter the Tutor, your guide to staying accountable. We’ve got daily sessions at 9 PM PST but remember, you can hop in anytime that works for you to maintain your streak!"
    # Sending the initial welcome message
    await welcome_channel.send(welcome_message)
    # Detailed explanation as a follow-up message
    await welcome_channel.send(get_hooter_explanation())


@bot.event
async def on_ready() -> None:
  logger.info(f"{bot.user} is now running")
  streaks_cog = bot.get_cog('StreaksCog')
  await streaks_cog.initialize_streaks()


@bot.event
async def on_disconnect() -> None:
  streaks_cog = bot.get_cog('StreaksCog')
  streaks_cog.save_streaks(streaks_cog.load_streaks())
  logging.info("Bot disconnected. Streaks data saved.")


@bot.event
async def on_message(message: Message) -> None:
  if message.author == bot.user:
    return

  username: str = str(message.author)
  user_message: str = message.content
  channel: str = str(message.channel)

  logger.info(f"[{channel}] {username}: {user_message}")

  if bot.user.mentioned_in(message):
    user_message = user_message.replace(f'<@!{bot.user.id}>', '').strip()
    await send_message(message, user_message)

  await bot.process_commands(message)


async def send_message(message: Message, user_message: str) -> None:
  if not user_message:
    logger.debug("Message was empty because intents were not enabled properly")
  if is_private := user_message[0] == '?':
    user_message = user_message[1:]

  try:
    response: str = model.generate_response(user_message)
    await message.author.send(
      response) if is_private else await message.channel.send(response)
  except Exception as e:
    logging.debug(e)
