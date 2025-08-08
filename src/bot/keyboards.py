from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)

main = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="местоположение"), KeyboardButton(text="подробнее")],
                                     [KeyboardButton(text="похожие изображения"), KeyboardButton(text="тепловые карты и оценка тяжости симтомов")],
                                     [KeyboardButton(text="помощь")], [KeyboardButton(text="перевод")]],
                           resize_keyboard=True,
                           input_field_placeholder='Ваш цветок')

translate_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Русский', callback_data='ru')],
    [InlineKeyboardButton(text='English(original)', callback_data='en')]])
