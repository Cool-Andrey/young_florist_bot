from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)

main_keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="местоположение", request_location=True), KeyboardButton(text="подробнее")],
                                     [KeyboardButton(text="похожие изображения"), KeyboardButton(text="оценка тяжести симптомов")],
                                     [KeyboardButton(text="помощь")],
                                     [KeyboardButton(text="язык")]],
                           resize_keyboard=True,
                           input_field_placeholder='Ваш цветок')

translate_menu = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Русский', callback_data='ru')],
                                                       [InlineKeyboardButton(text='English(original)', callback_data='en')]])
