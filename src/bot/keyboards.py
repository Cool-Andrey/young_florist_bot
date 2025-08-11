from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)
language = await self.conn.get_language(message.from_user.id)
if language == 'ru':
    main_keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="местоположение", request_location=True), KeyboardButton(text="подробнее")],
                                     [KeyboardButton(text="похожие изображения"), KeyboardButton(text="оценка тяжести симптомов")],
                                     [KeyboardButton(text="помощь")],
                                     [KeyboardButton(text="язык")]],
                           resize_keyboard=True,
                           input_field_placeholder='Ваш цветок')
else:
    main_keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="location", request_location=True), KeyboardButton(text="more details")],
                  [KeyboardButton(text="similar images"), KeyboardButton(text="symptom severity rating")],
                  [KeyboardButton(text="help")],
                  [KeyboardButton(text="language")]],
        resize_keyboard=True,
        input_field_placeholder='Your flower')

translate_menu = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Русский', callback_data='ru')],
                                                       [InlineKeyboardButton(text='English(original)', callback_data='en')]])
