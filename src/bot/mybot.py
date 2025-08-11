import base64
import io

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

import src.bot.keyboards as kb
from src.ai.request_to_plant import handle_photo, get_details, get_similar_images
from src.bot.keyboards import translate_menu, main_keyboard
from src.config.config import Config
from src.repository.sqlite.sqlite import Repository


class MyBot:
    def __init__(self, config: Config, conn: Repository):
        self.ai_token = config.ai_token
        self.bot = Bot(token=config.bot_token)
        self.conn = conn
        self.dp = Dispatcher()
        self.dp.message.register(self.start, CommandStart())
        self.dp.message.register(self.menu_translate, F.text == 'язык')
        self.dp.message.register(self.help, F.text == 'помощь')
        self.dp.message.register(self.gitler, F.text == "pivo")
        self.dp.message.register(self.geolocation, F.text == 'местоположение')
        self.dp.message.register(self.more_details, F.text == 'подробнее')
        self.dp.message.register(self.similar_images, F.text == "похожие изображения")
        self.dp.message.register(self.heat_maps_symptom_assessment,
                                 F.text == "тепловые карты и оценка тяжости симтомов")
        self.dp.message.register(self.handle_photo, F.photo)
        self.dp.callback_query.register(self.translate_ru, F.data == 'ru')
        self.dp.callback_query.register(self.translate_en, F.data == 'en')

    async def start(self, message: Message):
        await message.answer("🌱 Отправьте фото растения – я назову его и проверю на болезни.", reply_markup=kb.main_keyboard)
        await self.conn.set_user_and_language(message.from_user.id)

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

    async def translate_ru(self, callback: CallbackQuery):
        await callback.answer('Вы выбрали язык: Русский')
        await callback.message.delete()
        await self.conn.set_user_and_language(callback.from_user.id, 'ru')
        await callback.message.edit_reply_markup(reply_markup=None)

    async def translate_en(self, callback: CallbackQuery):
        await callback.answer('You have chosen the language: English')
        await callback.message.delete()
        await self.conn.set_user_and_language(callback.from_user.id, 'en')
        await callback.message.edit_reply_markup(reply_markup=None)

    async def geolocation(self, message: Message):
        await message.answer('Пожалуйста, поделитесь своим местоположением:', reply_markup=main_keyboard)

    async def handle_location(self, message: Message):
        lat = message.location.latitude
        lon = message.location.longitude
        print(lon, lat)
        await message.answer(
            f"Ваше местоположение: {lat}, {lon}\n"
            f"🔗 [Открыть в Google Maps](https://maps.google.com/?q={lat},{lon})",
            lon, lat,
            parse_mode="Markdown")


    async def more_details(self, message: Message):
        try:
            user_id = message.from_user.id
            access_token = await self.conn.get_token(user_id)
            if access_token:
                language = await self.conn.get_language(user_id)
                await message.answer(get_details(access_token, self.ai_token, language),
                                 parse_mode="HTML")
        except Exception as e:
            print(e)
            await message.answer(str(e))

    async def similar_images(self, message: Message):
        access_token = await self.conn.get_token(message.from_user.id)
        if access_token:
            similar_images = await get_similar_images(access_token, self.ai_token)
            await self.bot.send_media_group(
                chat_id=message.chat.id,
                media=similar_images.build()
            )
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
        photo_bytes = buffer.getvalue()
        photo_base64 = base64.b64encode(photo_bytes).decode('utf-8')
        user_id = message.from_user.id
        language = await self.conn.get_language(user_id)
        res, access_token = handle_photo(photo_base64, self.ai_token, language)
        await message.reply(res)
        await self.conn.set_token(access_token, user_id)
