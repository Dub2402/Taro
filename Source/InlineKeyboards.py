from telebot import types

class InlineKeyboards:

	def __init__(self):
		pass

	def SettingsMenu(self) -> types.InlineKeyboardMarkup:
		# Кнопочное меню.
		Menu = types.InlineKeyboardMarkup()

		# Генерация кнопок.
		CardDay = types.InlineKeyboardButton("Карта дня", callback_data = f"Card_Day")
		ValueCard = types.InlineKeyboardButton("Значения карт", callback_data = f"Value_Card")
		OrderLayout = types.InlineKeyboardButton("Заказать расклад", callback_data = f"Order_Layout")
	
		# Добавление кнопок в меню.
		Menu.add(CardDay, ValueCard, OrderLayout, row_width= 1) 

		return Menu

