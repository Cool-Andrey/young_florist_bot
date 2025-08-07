from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message


class MyBot:
    def __init__(self, token: str):
        self.bot = Bot(token=token)
        self.dp = Dispatcher()
        self.dp.message.register(self.start, CommandStart())

    async def start(self, message: Message):
        await message.answer("Привет! Этот бот тебя шлёт к хуям!")

    async def run(self):
        await self.dp.start_polling(self.bot)
