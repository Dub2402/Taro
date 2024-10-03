from dublib.TelebotUtils import UserData
from telebot import types

class ReplyKeyboards:

	def __init__(self):
		pass

	def AddMenu(self) -> types.ReplyKeyboardMarkup:
		# Кнопочное меню.
		Menu = types.ReplyKeyboardMarkup(resize_keyboard = True)

		# Генерация кнопок.
		Share = types.KeyboardButton("📢 Поделиться с друзьями")
	
		# Добавление кнопок в меню.
		Menu.add(Share, row_width = 1)
		
		return Menu
