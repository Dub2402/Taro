from telebot import types

from dublib.Engine.GetText import _
from dublib.Polyglot import HTML

class InlineKeyboards:
	
	def AddShare(buttons: list) -> types.InlineKeyboardMarkup:
		"""
		Клавиатура с кнопками: 
			Поделиться
			◀️ Назад

		:param buttons: название переключателя и/или кнопки.
		:type buttons: list
		:return: клавиатура.
		:rtype: types.InlineKeyboardMarkup
		"""
		
		Menu = types.InlineKeyboardMarkup(row_width = 1)

		for button in buttons:
			if button == "Share":
				Menu.add(types.InlineKeyboardButton(
					_("Поделиться"), 
					switch_inline_query = _('\n@Taro100_bot\n@Taro100_bot\n\n**Таробот | Расклад онлайн | Карта дня**\nСамый большой бот для Таро гаданий в Telegram! Ответит на любые твои вопросы ❓❓❓\n\n__Пользуйся и делись с друзьями!__'))
					)
			if button == "Back":
				Menu.add(types.InlineKeyboardButton(
					_("◀️ Назад"), 
					callback_data = "for_delete")
			)
		
		return Menu
	
	def Sharing(text: str) -> types.InlineKeyboardMarkup:
		Menu = types.InlineKeyboardMarkup()
		Paragraphs = text.split("\n")
		PlainLastParagraph = HTML(Paragraphs[-1]).plain_text
		Paragraphs[-1] = "**" + PlainLastParagraph + "**"
		text = "\n".join(Paragraphs)

		good_text = "\n" + text.replace("<i>", "__").replace("</i>", "__")
		Share = types.InlineKeyboardButton(
			_("Поделиться"), 
			switch_inline_query = good_text
			)
		
		Menu.add(Share)

		return Menu
		
	def main_menu() -> types.InlineKeyboardMarkup:
		"""
		Клавиатура с кнопками: 
			Карта дня | Да/Нет
			Всё о Таро | Доп. опции 
			Загадай карту | Онлайн расклад 💫
			Расклад от Мастера 🔥

		:return: Клавиатура главного меню
		:rtype: types.InlineKeyboardMarkup
		"""

		Menu = types.InlineKeyboardMarkup()
		
		CardDay = types.InlineKeyboardButton(_("Карта дня"), callback_data = "Card_Day")
		YesNo = types.InlineKeyboardButton(_("Да/Нет"), callback_data = "yes_no")
		Additional_options = types.InlineKeyboardButton(_("Доп. опции"), callback_data = "additional_options")
		OrderLayout = types.InlineKeyboardButton(_("Расклад от Мастера 🔥"), callback_data = "order_layout")
		ThinkCard = types.InlineKeyboardButton(_("Загадай карту"), callback_data = "ThinkCard")
		Online_layout = types.InlineKeyboardButton(_("Онлайн расклад 💫"), callback_data = "Online_Layout")
		All_Taro = types.InlineKeyboardButton(_("Всё о Таро"), callback_data = "all_taro")
	
		Menu.add(CardDay, YesNo, row_width = 2) 
		Menu.add(All_Taro, Additional_options, row_width = 2) 
		Menu.add(ThinkCard, Online_layout, row_width = 2)
		Menu.add(OrderLayout, row_width = 1) 

		return Menu
	
	def send_all_taro() -> types.InlineKeyboardMarkup:
		Menu = types.InlineKeyboardMarkup()

		value_card = types.InlineKeyboardButton(_("Значение карт"), callback_data = "value_card")
		History = types.InlineKeyboardButton(_("История Таро"), url = "https://tarolog.me/taro/history.html")
		What_is = types.InlineKeyboardButton(_("Что такое Таро?"),url = "https://tarolog.me/taro/determination.html")
		Work_with = types.InlineKeyboardButton(_("Работа с картами"), url = "https://tarolog.me/taro/work.html")
		Back = types.InlineKeyboardButton(_("◀️ Назад"), callback_data = "main_menu")
	
		Menu.add(value_card, History, What_is, Work_with, Back, row_width= 1) 

		return Menu

	def SendThinkCard() -> types.InlineKeyboardMarkup:
		Menu = types.InlineKeyboardMarkup()

		buttons = [types.InlineKeyboardButton(text=_(f"{i}"), callback_data = f"ThinkCard_{i}") for i in range(1, 5)]

		Menu.add(*buttons, row_width = 4)

		return Menu
	
	def delete_before_mm() -> types.InlineKeyboardMarkup:	
		return types.InlineKeyboardMarkup([[types.InlineKeyboardButton(text = _("Благодарю!"), callback_data = "delete_before_mm")]])
	
	def Subscribtion() -> types.InlineKeyboardMarkup:
		return types.InlineKeyboardMarkup([[types.InlineKeyboardButton(text = _("Я подписался!"), callback_data = "Subscribe")]])
	
	def for_delete(text: str) -> types.InlineKeyboardMarkup:
		"""
		Inline-keyboard.

		:param text: Текст кнопки.
		:type text: str
		:return: Inline-keyboard.
		:rtype: types.InlineKeyboardMarkup
		"""

		return types.InlineKeyboardMarkup([[types.InlineKeyboardButton(text = text, callback_data = "for_delete")]])
	
	def for_restart( text: str) -> types.InlineKeyboardMarkup:
		"""
		Inline-keyboard.

		:param text: Текст кнопки.
		:type text: str
		:return: Inline-keyboard.
		:rtype: types.InlineKeyboardMarkup
		"""
 
		return types.InlineKeyboardMarkup([[types.InlineKeyboardButton(text = text, callback_data = "for_restart")]])
		
	def notifications(action: str) -> types.InlineKeyboardMarkup:
		"""
		Клавиатура с кнопками: 
			Отключить ❌
			Включить ✅

		:return: Клавиатура настройки рассылки
		:rtype: types.InlineKeyboardMarkup
		"""

		Menu = types.InlineKeyboardMarkup()

		Yes = types.InlineKeyboardButton(_("Включить ✅"), callback_data = f"notifications_yes_{action}")
		No = types.InlineKeyboardButton(_("Отключить ❌"), callback_data = "notifications_no_noation")
		
		Menu.add(Yes, No, row_width = 2)
		
		return Menu

	def SendOrderLayout() -> types.InlineKeyboardMarkup:

		Menu = types.InlineKeyboardMarkup()

		Determinations = {
			_("💔 Личная жизнь"): "https://t.me/m/XVa5Zsn0OTli",
			_("💫 Ближайшее будущее"): "https://t.me/m/6cDunvn0ZThi",
			_("🧿 Дальнее будущее"): "https://t.me/m/_1rfsRNfY2Ri",
			_("💼 Карьера и работа"): "https://t.me/m/o4AQSvQ_NGIy",
			_("💵 Финансы"): "https://t.me/m/3JgIK6ycYjVi",
			_("😭 Чёрная полоса"): "https://t.me/m/5Dr14DlUNGUy",
			_("🤔 Свой вопрос"): "https://t.me/m/jIn3AGYkNmNi"
		}

		for String in Determinations.keys(): Menu.add(types.InlineKeyboardButton(String, url = Determinations[String]), row_width = 1)
		Menu.add(types.InlineKeyboardButton(_("◀️ Назад"), callback_data = "main_menu"))

		return Menu