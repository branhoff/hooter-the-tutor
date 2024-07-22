import asyncio
import logging
import os

from bot.core import bot, TOKEN
from flask import Flask
from threading import Thread

from bot.setup import setup_bot

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask('')

@app.route('/')
def home():
    return "Hooter the Tutor is running!"

def keep_alive(port):
    app.run(host='0.0.0.0', port=port)

async def async_main():
    await bot.start(TOKEN)

def main():

    keep_alive_thread = Thread(target=bot.run, args=(TOKEN,))
    keep_alive_thread.start()
    port = int(os.environ.get('PORT', 8080))
    keep_alive(port)

    asyncio.run(async_main())


if __name__ == '__main__':
    main()