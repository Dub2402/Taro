from Source.Modules.EnergyExchange.Options import Options as ExchangeOptions
from Source.Modules.EnergyExchange.Options import Options

from telebot import types

from dublib.TelebotUtils.Users import UserData
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
					_("Поделиться!"), 
					switch_inline_query = _('\n@TarobotX_bot\n@TarobotX_bot\n\n**Таробот | Расклад онлайн | Карта дня**\nСамый популярный бот для Таро-гаданий в Telegram! Ответит на любые твои вопросы ❓❓❓\n\n__Пользуйся и делись с друзьями!__'))
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
		
	def main_menu(user: UserData) -> types.InlineKeyboardMarkup:
		"""
		Клавиатура с кнопками: 
			Карта дня | Да/Нет
			Всё о Таро | Доп. опции 
			Загадай карту | Расклад у Мастера🔥
			Онлайн расклад 💫

		:return: Клавиатура главного меню
		:rtype: types.InlineKeyboardMarkup
		"""

		UserOptions = Options(user)
		Notifications = " (" + str(len(UserOptions.mails)) + ")" if UserOptions.mails else ""
		
		Menu = types.InlineKeyboardMarkup()
		
		CardDay = types.InlineKeyboardButton(_("Карта дня"), callback_data = "card_day")
		ThinkCard = types.InlineKeyboardButton(_("Загадай карту"), callback_data = "ThinkCard")
		MottoDay = types.InlineKeyboardButton(_("Девиз на сегодня"), callback_data ="motto_day")
		EnergyExchange = types.InlineKeyboardButton(Notifications + _(" Тебе сообщение"), callback_data = "energy_exchange")
		YesNo = types.InlineKeyboardButton(_("Да/Нет"), callback_data = "open_card")
		Additional_options = types.InlineKeyboardButton((_("Ещё...") + " "), callback_data = "additional_options")
		Online_layout = types.InlineKeyboardButton(_("Онлайн расклад💫"), callback_data = "Online_Layout")
	
		Menu.add(CardDay, ThinkCard, row_width = 2) 
		Menu.add(MottoDay, EnergyExchange, row_width = 2) 
		Menu.add(YesNo, Additional_options, row_width = 2)
		Menu.add(Online_layout, row_width = 1) 

		return Menu
	
	def send_all_taro() -> types.InlineKeyboardMarkup:
		Menu = types.InlineKeyboardMarkup()

		value_card = types.InlineKeyboardButton(_("Значение карт"), callback_data = "value_card")
		History = types.InlineKeyboardButton(_("История Таро"), url = "galina-taro.vercel.app/taro/history")
		What_is = types.InlineKeyboardButton(_("Что такое Таро?"),url = "galina-taro.vercel.app/taro/determination")
		Work_with = types.InlineKeyboardButton(_("Работа с картами"), url = "galina-taro.vercel.app/taro/work")
		Back = types.InlineKeyboardButton(_("◀️ Назад"), callback_data = "additional_options")
	
		Menu.add(value_card, History, What_is, Work_with, Back, row_width= 1) 

		return Menu

	def SendThinkCard() -> types.InlineKeyboardMarkup:
		Menu = types.InlineKeyboardMarkup()

		buttons = [types.InlineKeyboardButton(text=_(f"{i}"), callback_data = f"ThinkCard_{i}") for i in range(1, 5)]

		Menu.add(*buttons, row_width = 4)

		return Menu
	
	def delete_before_mm() -> types.InlineKeyboardMarkup:	
		return types.InlineKeyboardMarkup([[types.InlineKeyboardButton(text = _("Благодарю!"), callback_data = "delete_before_mm")]])
	
	def for_delete(text: str = "◀️ Назад") -> types.InlineKeyboardMarkup:
		"""
		Inline-keyboard.

		:param text: Текст кнопки.
		:type text: str
		:return: Inline-keyboard.
		:rtype: types.InlineKeyboardMarkup
		"""

		return types.InlineKeyboardMarkup([[types.InlineKeyboardButton(text = text, callback_data = "for_delete")]])
	
	def for_restart(text: str) -> types.InlineKeyboardMarkup:
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
			_("💔 Личная жизнь"): "https://t.me/m/EAtlSreSMGEy",
			_("💫 Ближайшее будущее"): "https://t.me/m/0LzEU0bdZTZi",
			_("🧿 Дальнее будущее"): "https://t.me/m/HjHMZt4gMWFi",
			_("💼 Карьера и работа"): "https://t.me/m/d_w1xEioNmVi",
			_("💵 Финансы"): "https://t.me/m/tzjnh2uTY2My",
			_("😭 Чёрная полоса"): "https://t.me/m/wHlaKPdvNzQy",
			_("🤔 Свой вопрос"): "https://t.me/m/DmIZFszBODFi"
		}

		for String in Determinations.keys(): Menu.add(types.InlineKeyboardButton(String, url = Determinations[String]), row_width = 1)
		Menu.add(types.InlineKeyboardButton(_("◀️ Назад"), callback_data = "additional_options"))

		return Menu