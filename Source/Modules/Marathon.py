from Source.Core.ExcelTools import Reader

from dublib.TelebotUtils import UsersManager
from dublib.TelebotUtils.Cache import TeleCache

from telebot import types, TeleBot

from typing import TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
	from Source.Modules.Subscription import Subscription

class Decorators:
	"""Набор декораторов."""

	@property
	def number_week(self):
		"""Возвращает номер текущей недели."""

		return datetime.today().isocalendar().week

	@property
	def year(self):
		"""Возвращает номер текущего года."""

		return datetime.today().isocalendar().year
	
	@property
	def name_day(self):
		"""Возвращает название текущего дня."""

		return datetime.today().isocalendar().weekday
	
	def __find_date(self, need_number_week: int, need_weekday: int):
		"""Возвращает дату необходимого нам дня."""

		return datetime.fromisocalendar(self.year, need_number_week, need_weekday)

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
			
			numbers_week: tuple = self.__Marathon.reader.numbers_week

			index_excel = numbers_week.index(str(self.number_week))

			text_announcement = (
				f"<b>МАРАФОН \"{self.__Marathon.reader.names_marathons[index_excel]}\"</b>\n",
				f"{self.__Marathon.reader.descriptions_marathons[index_excel]}\n",
				"<b><i>Присоединяйся, нас уже много! ✅</i></b>"
			)

			Message = self.__Marathon.bot.send_animation(
				chat_id = Call.message.chat.id,
				animation = self.__Marathon.cacher.get_real_cached_file(
					path = f"Data/Marathons/{self.year}/{self.number_week}/announcement.mp4",
					autoupload_type = types.InputMediaVideo,
					).file_id,
				caption = "\n".join(text_announcement),
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

			:param Call: about_marathons
			:type Call: types.CallbackQuery
			"""

			user = self.__Marathon.users.auth(Call.from_user)
			if not self.__Marathon.subscription.IsSubscripted(user):
				self.__Marathon.bot.answer_callback_query(Call.id)
				return
			
			text_about_marathons = (
				"<b>" + "Марафоны недели" + "</b>" + "— это увлекательный 7-дневный путь, где вы получаете лучшие советы, проводите практики и выполняете действенные ритуалы. Цель марафонов: изменить вашу жизнь к лучшему, раскрыть ваш потенциал и обрести долгожданное ощущение счастья!\n",
				"Наши авторы трудятся для вас большой командой, чтобы затронуть наиболее актуальные для современного быта темы. Во главе с нашим экспертом мы стараемся прорабатывать все основные сферы, такие как: личные отношения, работу, социум, самооценку, внутренний мир и тд.\n",
				"<b>" + "Хотелось бы, чтобы вы развивались и улучшали себя вместе с нами!" + "</b>"
			)
			
			Message = self.__Marathon.bot.send_message(
				chat_id = Call.message.chat.id,
				text = "\n".join(text_about_marathons),
				parse_mode = "HTML",
				reply_markup = self.__Marathon.inline_templates.menu_marathon("◀️ Назад")
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
			
			numbers_week: tuple = self.__Marathon.reader.numbers_week

			index_excel = numbers_week.index(str(self.number_week))
			
			next_marathon_template = (
				"ВНИМАНИЕ!!! МАРАФОН СЛЕДУЮЩЕЙ НЕДЕЛИ:" + "\n\n"
				f"<b>{self.__Marathon.reader.names_marathons[index_excel + 1]}</b>" + "\n",
				f"{self.__Marathon.reader.descriptions_marathons[index_excel + 1]}\n",
				"<b>" + "📆 Даты проведения: " + f"{self.__find_date(need_number_week = self.number_week + 1, need_weekday = 1).strftime("%d.%m.%Y")} - {self.__find_date(need_number_week = self.number_week + 1, need_weekday = 7).strftime("%d.%m.%Y")}" + "</b>" + "\n",
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

			with open(f"Data/Marathons/{self.year}/{self.number_week}/first_detailed_marathon.txt") as file:
				first_detailed_marathon = file.read()

			with open(f"Data/Marathons/{self.year}/{self.number_week}/second_detailed_marathon.txt") as file:
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

		@self.__Marathon.bot.callback_query_handler(func = lambda Callback: Callback.data in ("1 day", "2 day"))
		def click_1_day(Call: types.CallbackQuery):
			"""
			Нажатие на кнопку: "1 день (понедельник)/2 день (вторник)"

			:param Call: join_marathon
			:type Call: types.CallbackQuery
			"""

			send_message = False

			user = self.__Marathon.users.auth(Call.from_user)
			if not self.__Marathon.subscription.IsSubscripted(user):
				self.__Marathon.bot.answer_callback_query(Call.id)
				return
			
			if Call.data == "2 day" and self.name_day >= 2: send_message = True
			else: Message = self.__Marathon.bot.send_message(
					chat_id = Call.message.chat.id,
					text = f"Информация здесь появиться во вторник {self.__find_date(2).strftime("%d.%m.%Y")}. Пожалуйста, чуточку вашего терпения!)",
					parse_mode = "HTML",
					reply_markup = self.__Marathon.inline_templates.menu_marathon("◀️ Назад")
				)

			if Call.data == "1 day": send_message = True

			if send_message:

				with open(f"Data/Marathons/{self.year}/{self.number_week}/{Call.data}/1.txt") as file:
					first_text = file.read()

				with open(f"Data/Marathons/{self.year}/{self.number_week}/{Call.data}/2.txt") as file:
					second_text = file.read()

				with open(f"Data/Marathons/{self.year}/{self.number_week}/{Call.data}/3.txt") as file:
					third_text = file.read()

				with open(f"Data/Marathons/{self.year}/{self.number_week}/{Call.data}/4.txt") as file:
					fourth_text = file.read()

				with open(f"Data/Marathons/{self.year}/{self.number_week}/{Call.data}/5.txt") as file:
					fifth_text = file.read()

				with open(f"Data/Marathons/{self.year}/{self.number_week}/{Call.data}/6.txt") as file:
					sixth_text = file.read()

				Message = self.__Marathon.bot.send_message(
					chat_id = Call.message.chat.id,
					text = first_text,
					parse_mode = "HTML"
				)

				Message = self.__Marathon.bot.send_animation(
					chat_id = Call.message.chat.id,
					animation = self.__Marathon.cacher.get_real_cached_file(
						path = f"Data/Marathons/{self.year}/{self.number_week}/{Call.data}//2.mp4",
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
						path = f"Data/Marathons/{self.year}/{self.number_week}/{Call.data}//5.mp4",
						autoupload_type = types.InputMediaVideo,
						).file_id,
					caption = fifth_text,
					parse_mode = "HTML"
				)
				try: 
					Message = self.__Marathon.bot.send_animation(
					chat_id = Call.message.chat.id,
					animation = self.__Marathon.cacher.get_real_cached_file(
						path = f"Data/Marathons/{self.year}/{self.number_week}/{Call.data}//2.mp4",
						autoupload_type = types.InputMediaVideo,
						).file_id,
					caption = sixth_text,
					parse_mode = "HTML",
					reply_markup = self.__Marathon.inline_templates.menu_marathon("Спасибо большое!")
				)
					
				except:
					Message = self.__Marathon.bot.send_message(
						chat_id = Call.message.chat.id,
						text = sixth_text,
						parse_mode = "HTML",
						reply_markup = self.__Marathon.inline_templates.menu_marathon("Спасибо большое!")
					)

			self.__Marathon.bot.answer_callback_query(Call.id)
		
		@self.__Marathon.bot.callback_query_handler(func = lambda Callback: Callback.data in ("continue_marathon"))
		def click_continue_marathon(Call: types.CallbackQuery):
			"""
			Нажатие на кнопку: "Продолжение🔥"

			:param Call: continue_marathon
			:type Call: types.CallbackQuery
			"""

			user = self.__Marathon.users.auth(Call.from_user)
			if not self.__Marathon.subscription.IsSubscripted(user):
				self.__Marathon.bot.answer_callback_query(Call.id)
				return

			if self.name_day >= 3:

				Message = self.__Marathon.bot.send_message(
					chat_id = Call.message.chat.id,
					text = f"Для продолжения Марафона, напишите название марафона вот по этой ссылке:\n\nhttps://t.me/galina_tarot\n\nили просто нажмите на кнопку ниже.",
					parse_mode = "HTML",
					reply_markup = self.__Marathon.inline_templates.continue_marathon()
				)

			else: Message = self.__Marathon.bot.send_message(
					chat_id = Call.message.chat.id,
					text = f"Информация здесь появиться в среду {self.__find_date(3).strftime("%d.%m.%Y")}. Пожалуйста, чуточку вашего терпения!)",
					parse_mode = "HTML",
					reply_markup = self.__Marathon.inline_templates.menu_marathon("◀️ Назад")
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
			"1 день (понедельник)": "1 day",
			"2 день (вторник)": "2 day",
			"Продолжение🔥": "continue_marathon",
			"◀️ Назад": "requirements_for_5_level"
		}

		for String in determinations.keys(): menu.add(types.InlineKeyboardButton(text = String, callback_data = determinations[String]), row_width = 1)

		return menu
	
	def continue_marathon() -> types.InlineKeyboardMarkup:
		"""
		Возвращает ссылку на продолжение марафона.

		:return: Inline Keyboard. 
		:rtype: types.InlineKeyboardMarkup
		"""

		menu = types.InlineKeyboardMarkup()

		continue_marathon = types.InlineKeyboardButton(("Продолжить марафон!"), url = "https://t.me/m/TWo0FHB-NjM6")
		Back = types.InlineKeyboardButton(("◀️ Назад"), callback_data = "menu_marathon")
	
		menu.add(continue_marathon, Back, row_width = 1) 

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
	
	@property
	def reader(self):
		"""Читатель excel-файлы."""
		
		return self.__reader

	def __init__(self, users: UsersManager, bot: TeleBot, subscription: "Subscription", cacher: TeleCache, reader: Reader):

		self.__users = users
		self.__subscription = subscription
		self.__bot = bot
		self.__cacher = cacher
		self.__reader = reader

		self.__decorators = Decorators(self)
		self.__inline_templates = InlineKeyboards