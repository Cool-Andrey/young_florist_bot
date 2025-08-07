from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

import src.bot.keyboards as kb

class MyBot:
    def __init__(self, token: str):
        self.bot = Bot(token=token)
        self.dp = Dispatcher()
        self.dp.message.register(self.start, CommandStart())
        self.dp.message.register(self.help, F.text == ('помощь'))
        self.dp.message.register(self.gitler, F.text == "pivo")

    async def start(self, message: Message):
        await message.answer("🌱 Отправьте фото растения – я назову его и проверю на болезни.", reply_markup=kb.main)

    async def help(self, message: Message):
        await message.answer(f'''📸 Как отправить фото:

1) Нажми на «📎 Скрепка» (вложения)

2)Выбери «Галерея» или «Камера»

3) Загрузи фото растения – и я его проанализирую!''')

    async def gitler(self, message: Message):
        await message.answer('''Was wollen wir trinken,
sieben Tage lang?
Was wollen wir trinken,
ja, was denn?
Wir wollen trinken,
sieben Tage lang!
Wir wollen trinken,
ja, wir wollen's!
Was wollen wir essen,
sieben Tage lang?
Was wollen wir essen,
ja, was denn?
Wir wollen essen,
sieben Tage lang!
Wir wollen essen,
ja, wir wollen's!
Was wollen wir tanzen,
sieben Tage lang?
Was wollen wir tanzen,
ja, was denn?
Wir wollen tanzen,
sieben Tage lang!
Wir wollen tanzen,
ja, wir wollen's!
Was wollen wir lieben,
sieben Tage lang?
Was wollen wir lieben,
ja, was denn?
Wir wollen lieben,
sieben Tage lang!
Wir wollen lieben,
ja, wir wollen's!''')

    async def run(self):
        await self.dp.start_polling(self.bot)
