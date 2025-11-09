from dublib.TelebotUtils import UsersManager
from dublib.TelebotUtils.Cache import TeleCache

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
	
		@self.__Marathon.bot.callback_query_handler(func = lambda Callback: Callback.data == "marathons")
		def click_marathons(Call: types.CallbackQuery):
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

			Message = self.__Marathon.bot.send_animation(
				chat_id = Call.message.chat.id,
				animation = self.__Marathon.cacher.get_real_cached_file(
					path = "Data/Marathons/03.11.2025/1. Бывший.mp4",
					autoupload_type = types.InputMediaVideo,
					).file_id,
				caption = text_announcement,
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
			
			Message = self.__Marathon.bot.edit_message_reply_markup(
				chat_id = Call.message.chat.id,
				message_id = Call.message.id,
				reply_markup = self.__Marathon.inline_templates.marathon_with_days()
			)
			self.__Marathon.bot.answer_callback_query(Call.id)

		@self.__Marathon.bot.callback_query_handler(func = lambda Callback: Callback.data == "about_marathons")
		def click_about_marathons(Call: types.CallbackQuery):
			"""
			Нажатие на кнопку: "О марафонах недели"

			:param Call: join_marathon
			:type Call: types.CallbackQuery
			"""

			user = self.__Marathon.users.auth(Call.from_user)
			if not self.__Marathon.subscription.IsSubscripted(user):
				self.__Marathon.bot.answer_callback_query(Call.id)
				return
			
			Message = self.__Marathon.bot.edit_message_reply_markup(
				chat_id = Call.message.chat.id,
				message_id = Call.message.id,
				reply_markup = self.__Marathon.inline_templates.marathon_with_days()
			)
			self.__Marathon.bot.answer_callback_query(Call.id)

		@self.__Marathon.bot.callback_query_handler(func = lambda Callback: Callback.data == "next_marathon")
		def click_next_marathon(Call: types.CallbackQuery):
			"""
			Нажатие на кнопку: "Следующий марафон"

			:param Call: next_marathon
			:type Call: types.CallbackQuery
			"""

			user = self.__Marathon.users.auth(Call.from_user)
			if not self.__Marathon.subscription.IsSubscripted(user):
				self.__Marathon.bot.answer_callback_query(Call.id)
				return
			
			name_next_marathon = "\"КАК СТАТЬ АФРИКАНКОЙ\""
			description_next_marathon = "Благодаря этому 7-дневному марафону ты избавишься от белого цвета кожи и сможешь бегать за бегемотами с копьем и в одних трусиках!"
			monday_date = "10.11.2025"
			synday_date = "17.11.2025"
			
			next_marathon_template = (
				"ВНИМАНИЕ!!! МАРАФОН СЛЕДУЮЩЕЙ НЕДЕЛИ:" + "\n\n"
				f"<b>{name_next_marathon}</b>" + "\n",
				f"{description_next_marathon}\n",
				"<b>" + "📆 Даты проведения: " + f"{monday_date} - {synday_date}" + "</b>" + "\n",
				"<b><i>" + "Будем ждать тебя и твоих друзей, @tarobotX_bot! 🤗" + "</i></b>"
			)
			
			Message = self.__Marathon.bot.send_message(
				chat_id = Call.message.chat.id,
				text = "\n".join(next_marathon_template),
				parse_mode = "HTML",
				reply_markup = self.__Marathon.inline_templates.menu_marathon("◀️ Назад")
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
				reply_markup = self.__Marathon.inline_templates.menu_marathon("◀️ Назад")
			)
			self.__Marathon.bot.answer_callback_query(Call.id)

		@self.__Marathon.bot.callback_query_handler(func = lambda Callback: Callback.data == "1")
		def click_more_detailed_marathon(Call: types.CallbackQuery):
			"""
			Нажатие на кнопку: "1 день (понедельник)"

			:param Call: join_marathon
			:type Call: types.CallbackQuery
			"""

			user = self.__Marathon.users.auth(Call.from_user)
			if not self.__Marathon.subscription.IsSubscripted(user):
				self.__Marathon.bot.answer_callback_query(Call.id)
				return
			
			folder_marathon = "03.11.2025"

			with open(f"Data/Marathons/{folder_marathon}/1/1.txt") as file:
				first_text = file.read()

			with open(f"Data/Marathons/{folder_marathon}/1/2.txt") as file:
				second_text = file.read()

			with open(f"Data/Marathons/{folder_marathon}/1/3.txt") as file:
				third_text = file.read()

			with open(f"Data/Marathons/{folder_marathon}/1/4.txt") as file:
				fourth_text = file.read()

			with open(f"Data/Marathons/{folder_marathon}/1/5.txt") as file:
				fifth_text = file.read()

			with open(f"Data/Marathons/{folder_marathon}/1/6.txt") as file:
				sixth_text = file.read()

			Message = self.__Marathon.bot.send_message(
				chat_id = Call.message.chat.id,
				text = first_text,
				parse_mode = "HTML"
			)

			Message = self.__Marathon.bot.send_animation(
				chat_id = Call.message.chat.id,
				animation = self.__Marathon.cacher.get_real_cached_file(
					path = "Data/Marathons/03.11.2025/1/2.mp4",
					autoupload_type = types.InputMediaVideo,
					).file_id,
				caption = second_text,
				parse_mode = "HTML"
			)

			Message = self.__Marathon.bot.send_message(
				chat_id = Call.message.chat.id,
				text = third_text,
				parse_mode = "HTML"
			)

			Message = self.__Marathon.bot.send_message(
				chat_id = Call.message.chat.id,
				text = fourth_text,
				parse_mode = "HTML"
			)

			Message = self.__Marathon.bot.send_animation(
				chat_id = Call.message.chat.id,
				animation = self.__Marathon.cacher.get_real_cached_file(
					path = "Data/Marathons/03.11.2025/1/5.mp4",
					autoupload_type = types.InputMediaVideo,
					).file_id,
				caption = fifth_text,
				parse_mode = "HTML"
			)

			Message = self.__Marathon.bot.send_message(
				chat_id = Call.message.chat.id,
				text = sixth_text,
				parse_mode = "HTML",
				reply_markup = self.__Marathon.inline_templates.menu_marathon("Спасибо большое!")
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
			"О марафонах недели": "about_marathons",
			"Следующий марафон": "next_marathon",
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
			"1 день (понедельник)": "1",
			"2 день (вторник)": "requirements_for_5_level",
			"Продолжение🔥": "requirements_for_5_level",
			"◀️ Назад": "requirements_for_5_level"
		}

		for String in determinations.keys(): menu.add(types.InlineKeyboardButton(text = String, callback_data = determinations[String]), row_width = 1)

		return menu
	
	def menu_marathon(text: str) -> types.InlineKeyboardMarkup:
		"""
		Возвращает нас к меню марафона.

		:return: Inline Keyboard. 
		:rtype: types.InlineKeyboardMarkup
		"""
									
		return types.InlineKeyboardMarkup([[types.InlineKeyboardButton(text = text, callback_data = "menu_marathon")]])

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
	
	@property
	def cacher(self):
		"""Менеджер кэша."""
		
		return self.__cacher

	def __init__(self, users: UsersManager, bot: TeleBot, subscription: "Subscription", cacher: TeleCache):

		self.__users = users
		self.__subscription = subscription
		self.__bot = bot
		self.__cacher = cacher

		self.__decorators = Decorators(self)
		self.__inline_templates = InlineKeyboards