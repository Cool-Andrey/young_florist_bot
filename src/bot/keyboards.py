from  aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="местоположение"), KeyboardButton(text="оценка здоровья")],
                                     [KeyboardButton(text="похожие изображения"), KeyboardButton(text="тепловые карты и оценка тяжости симтомов")],
                                     [KeyboardButton(text="помощь")]],
                           input_field_placeholder='Ваш цветок')

