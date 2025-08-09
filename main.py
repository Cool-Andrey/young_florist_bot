import asyncio
import logging

import src.config.config as config
import src.bot.mybot as bot
import src.repository.sqlite.sqlite as sqlite

conf = config.Config()
tg = bot.MyBot(conf)

async def main():
    await tg.run()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    conn = sqlite.Repository(conf.db_path)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот выключен')
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        conn.close()