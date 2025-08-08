import io

import imghdr
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, BotCommand
from aiohttp import request

from src.config.config import Config

import src.config.config

import src.bot.keyboards as kb
from src.ai.request_to_api import handle_photo
from src.config.config import Config


class MyBot:
    def __init__(self, config: Config):
        self.ai_token = config.ai_token
        self.bot = Bot(token=config.bot_token)
        self.dp = Dispatcher()
        self.dp.message.register(self.start, CommandStart())
        self.dp.message.register(self.menu_translate, F.text == 'перевод')
        self.dp.message.register(self.help, F.text == 'помощь')
        self.dp.message.register(self.gitler, F.text == "pivo")
        self.dp.message.register(self.geolocation, F.text == 'местоположение')
        self.dp.message.register(self.more_details, F.text == 'подробнее')
        self.dp.message.register(self.similar_images, F.text == "похожие изображения")
        self.dp.message.register(self.heat_maps_symptom_assessment,
                                 F.text == "тепловые карты и оценка тяжости симтомов")
        self.dp.message.register(self.handle_photo)

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

    async def menu_translate(self, message: Message):
        await message.answer('Выберете язык', reply_markup=kb.translate_menu)

    async def geolocation(self, message: Message):
        await message.answer('''СИСТЕМА ПОИСКА ПИДОРАСОВ АКТИВИРОВАНА
        ПИ
        ПИ-ПИ-ПИ-ПИ
        ПИДОРАС НАЙДЕН''')

    async def more_details(self, message: Message):
        await message.answer('Расскажи мне всё!')

    async def similar_images(self, message: Message):
        await message.answer('Похожие изибражения')

    async def heat_maps_symptom_assessment(self, message: Message):
        await message.answer('тепловые карты и оценка тяжости симтомов')

    async def run(self):
        await self.dp.start_polling(self.bot)

    async def handle_photo(self, message: Message):
        print("Начата обработка изображения")
        await message.reply("Обрабатываю изображение...")
        photo_id = message.photo[-1].file_id
        file = await self.bot.get_file(photo_id)
        buffer = io.BytesIO()
        await self.bot.download_file(file.file_path, buffer)
        buffer.seek(0)
        photo_bytes = buffer.read()
        mime_type = "image/"
        photo_type = imghdr.what(None, photo_bytes)
        if not photo_type:
            await message.reply(
                "Не удалось определить тип изображения. Возможно ваш файл поврежден. Отправьте его повторно или попробуйте другое изображение.")
            return
        files = {'image': (f'image_from_user.{photo_type}', io.BytesIO(photo_bytes), mime_type)}
        await message.reply(handle_photo(files, self.ai_token))
