import asyncio
import logging

import src.config.config as config
import src.bot.mybot as bot
import src.repository.sqlite.sqlite as sqlite

conf = config.Config()
conn = sqlite.Repository(conf.db_path)
myBot = bot.MyBot(conf, conn)

async def main():
    await myBot.run()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот выключен')
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        conn.close()