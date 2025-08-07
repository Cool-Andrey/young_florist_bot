import asyncio
import logging

import src.config.config as config
import src.bot.mybot as bot

conf = config.Config()
tg = bot.MyBot(conf)

async def main():
    await tg.run()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот выключен')