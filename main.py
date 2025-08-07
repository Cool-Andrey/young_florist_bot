import asyncio

import src.config.config as config
import src.bot.mybot as bot

conf = config.Config()
tg = bot.MyBot(conf.bot_token)

async def main():
    await tg.run()

if __name__ == "__main__":
    asyncio.run(main())