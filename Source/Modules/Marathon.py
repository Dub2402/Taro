from dublib.TelebotUtils import UsersManager

from telebot import types, TeleBot

from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from Source.Modules.Subscription import Subscription

class Decorators:
	"""Набор декораторов."""

	def __init__(self, marathon: "Marathon"):
		"""Инициализация основных параметров."""

		self.__Marathon = marathon

	def inline_keyboards(self):
		"""Обработка Callback-запросов"""
	
		@self.__Marathon.bot.callback_query_handler(func = lambda Callback: Callback.data == "marathon")
		def click_marathon(Call: types.CallbackQuery):
			"""
			Нажатие на кнопку: "Марафон недели 🏁"

			:param Call: marathon
			:type Call: types.CallbackQuery
			"""

			user = self.__Marathon.users.auth(Call.from_user)
			if not self.__Marathon.subscription.IsSubscripted(user):
				self.__Marathon.bot.answer_callback_query(Call.id)
				return
			
			folder_marathon = "03.11.2025"

			with open(f"Data/Marathons/{folder_marathon}/announcement.txt") as file:
				text_announcement = file.read()
			
			Message = self.__Marathon.bot.edit_message_caption(
				caption = text_announcement,
				chat_id = Call.message.chat.id,
				message_id = Call.message.id,
				parse_mode = "HTML",
				reply_markup = self.__Marathon.inline_templates.marathon()
			)
			self.__Marathon.bot.answer_callback_query(Call.id)

		@self.__Marathon.bot.callback_query_handler(func = lambda Callback: Callback.data == "join_marathon")
		def click_join_marathon(Call: types.CallbackQuery):
			"""
			Нажатие на кнопку: "Присоединиться!"

			:param Call: join_marathon
			:type Call: types.CallbackQuery
			"""

			user = self.__Marathon.users.auth(Call.from_user)
			if not self.__Marathon.subscription.IsSubscripted(user):
				self.__Marathon.bot.answer_callback_query(Call.id)
				return
			
			folder_marathon = "03.11.2025"

			with open(f"Data/Marathons/{folder_marathon}/announcement.txt") as file:
				text_announcement = file.read()
			
			Message = self.__Marathon.bot.edit_message_reply_markup(
				chat_id = Call.message.chat.id,
				message_id = Call.message.id,
				reply_markup = self.__Marathon.inline_templates.marathon_with_days()
			)
			self.__Marathon.bot.answer_callback_query(Call.id)

		@self.__Marathon.bot.callback_query_handler(func = lambda Callback: Callback.data == "more_detailed_marathon")
		def click_more_detailed_marathon(Call: types.CallbackQuery):
			"""
			Нажатие на кнопку: "Подробнее о марафоне"

			:param Call: join_marathon
			:type Call: types.CallbackQuery
			"""

			user = self.__Marathon.users.auth(Call.from_user)
			if not self.__Marathon.subscription.IsSubscripted(user):
				self.__Marathon.bot.answer_callback_query(Call.id)
				return
			
			folder_marathon = "03.11.2025"

			with open(f"Data/Marathons/{folder_marathon}/first_detailed_marathon.txt") as file:
				first_detailed_marathon = file.read()

			with open(f"Data/Marathons/{folder_marathon}/second_detailed_marathon.txt") as file:
				second_detailed_marathon = file.read()
			
			Message = self.__Marathon.bot.edit_message_caption(
				caption = first_detailed_marathon,
				chat_id = Call.message.chat.id,
				message_id = Call.message.id,
				parse_mode = "HTML"
			)
			Message = self.__Marathon.bot.send_message(
				chat_id = Call.message.chat.id,
				text = second_detailed_marathon,
				parse_mode = "HTML",
				reply_markup = self.__Marathon.inline_templates.marathon()
			)
			self.__Marathon.bot.answer_callback_query(Call.id)
			
class InlineKeyboards:
	"""Набор Inline Keyboards."""

	def marathon() -> types.InlineKeyboardMarkup:
		"""
		Возвращает марафон недели.

		:return: Inline Keyboard. 
		:rtype: types.InlineKeyboardMarkup
		"""

		menu = types.InlineKeyboardMarkup()

		determinations = {
			"Присоединиться!": "join_marathon",
			"О марафонах недели": "for_delete",
			"Следующий марафон": "requirements_for_5_level",
			"◀️ Назад": "requirements_for_5_level"
		}

		for String in determinations.keys(): menu.add(types.InlineKeyboardButton(text = String, callback_data = determinations[String]), row_width = 1)

		return menu
	
	def marathon_with_days() -> types.InlineKeyboardMarkup:
		"""
		Возвращает марафон по дням.

		:return: Inline Keyboard. 
		:rtype: types.InlineKeyboardMarkup
		"""

		menu = types.InlineKeyboardMarkup()

		determinations = {
			"Подробнее о марафоне": "more_detailed_marathon",
			"1 день (понедельник)": "for_delete",
			"2 день (вторник)": "requirements_for_5_level",
			"Продолжение🔥": "requirements_for_5_level",
			"◀️ Назад": "requirements_for_5_level"
		}

		for String in determinations.keys(): menu.add(types.InlineKeyboardButton(text = String, callback_data = determinations[String]), row_width = 1)

		return menu

class Marathon:

	@property
	def decorators(self):
		"""Набор декораторов."""
		
		return self.__decorators
	
	@property
	def inline_templates(self):
		"""Набор Inline Keyboards."""
		
		return self.__inline_templates
	
	@property
	def users(self):
		"""Данные пользователей."""
		
		return self.__users
	
	@property
	def subscription(self):
		"""Менеджер подписки."""
		
		return self.__subscription
	
	@property
	def bot(self):
		"""Telegram bot."""
		
		return self.__bot

	def __init__(self, users: UsersManager, bot: TeleBot, subscription: "Subscription"):

		self.__users = users
		self.__subscription = subscription
		self.__bot = bot

		self.__decorators = Decorators(self)
		self.__inline_templates = InlineKeyboards