from dublib.TelebotUtils import UsersManager, UserData
from dublib.TelebotUtils.Cache import TeleCache
from dublib.TelebotUtils import TeleMaster
from dublib.Engine.GetText import _
from dublib.Methods.Filesystem import WriteJSON, ReadJSON

from Source.Modules.Subscription import Subscription
from Source.Core.Reader import Reader
from Source.InlineKeyboards import InlineKeyboards

from datetime import datetime
import random
import logging
import os

from telebot import TeleBot, types

#==========================================================================================#
# >>>>> НАБОР INLINE_KEYBOARDS <<<<< #
#==========================================================================================#

class WordMonthInlineTemplates:

	def appeal_or_delete(text: str, appeal: bool) -> types.InlineKeyboardMarkup:
		"""
		Строит Inline-интерфейс:
			Поделиться
			В другой раз

		:return: inline-keyboard
		:rtype: types.InlineKeyboardMarkup
		"""

		Menu = types.InlineKeyboardMarkup()
		send_appeal = types.InlineKeyboardButton(f"{text}", callback_data = "send_appeal") if appeal else types.InlineKeyboardButton(f"{text}", callback_data = "for_delete")

		Menu.add(send_appeal, row_width = 1) 

		return Menu

	def start_appeals(text: str) -> types.InlineKeyboardMarkup:
		"""
		Строит Inline-интерфейс:
			Поделиться
			В другой раз!

		:return: inline-keyboard
		:rtype: types.InlineKeyboardMarkup
		"""

		Menu = types.InlineKeyboardMarkup()

		share = types.InlineKeyboardButton(
			_("Поделиться"), 
			switch_inline_query = text
			)
		for_delete = types.InlineKeyboardButton(_("В другой раз!"), callback_data = "for_delete")

		Menu.add(share, for_delete, row_width= 1) 

		return Menu
	
#==========================================================================================#
# >>>>> ОБЩИЕ МЕТОДЫ РАБОТЫ С САРАФАННЫМ РАДИО <<<<< #
#==========================================================================================#

class WordMonth:
	"""Работа с призывами и посланиями."""

	def randomize_text(self, texts: list[str]) -> str:
		"""
		Выбрать случайный текст из множества текстов.

		:param appeals: Список текстов.
		:type appeals: list[str]
		:return: Случайный текст из списка.
		:rtype: str
		"""

		random_text = random.randint(1, len(texts))
		
		for Index in range(len(texts)):
			if Index == random_text-1:
				Text = texts[Index]

		return Text
	
#==========================================================================================#
# >>>>> ПРИЗЫВЫ <<<<< #
#==========================================================================================#
	
class Appeals:
	"""Работа с призывами."""

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#
	
	def __mailing_days(self, week: int) -> dict[str, list[int]]:
		"""
		Получение всех дней рассылки призывов.

		:param week: номер недели.
		:type week: int
		:return: дни рассылки призывов.
		:rtype: dict[str, list[int]]
		"""
	
		return ReadJSON("Data/WordMonth/Appeals.json")[str(week)]
	
	def __day_of_week(self) -> int:
		"""
		Получение индекса текущего дня недели.

		:return: индекса текущего дня недели
		:rtype: int
		"""

		return datetime.now().weekday()
	
	def __week_of_year(self) -> int:
		"""
		Получение текущего номера недели.

		:return: текущего номер недели
		:rtype: int
		"""

		Now = datetime.now()

		return datetime(Now.year, Now.month, Now.day).isocalendar()[1]

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#
	
	def __init__(self, mailer: "Mailer"):

		#---> Генерация динамических атрибутов.
		#==========================================================================================#
		self.__Mailer = mailer

	def is_mailing_day(self) -> bool:
		"""
		Является ли сегодняшний день днём рассылки призыва.

		:return: Необходимость рассылки.
		:rtype: bool
		"""

		if self.__day_of_week() in self.__mailing_days(self.__week_of_year()): return True
		return False
	
	def randomize_days(self):
		"""Разброс призывов по дням недели и сохранение в формате json."""
		
		days = random.sample(population = list(range(7)), k = 3)
		days.sort()

		Data = {}
		Data[str(self.__week_of_year())] = days
		WriteJSON("Data/WordMonth/Appeals.json", Data)

	def click_update_card_day(self):
		self.__Mailer.users.set_property("send_appeal", False)

#==========================================================================================#
# >>>>> ПОСЛАНИЯ <<<<< #
#==========================================================================================#

class Letters:
	"""Работа с посланиями."""

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __random_time(self) -> str:
		"""Получение рандомного времени.

		:return: Дата и время.
		:rtype: str
		"""
	
		today = datetime.now()
		random_hour = random.randint(9, 10)
		random_minute = random.randint(0, 59)

		date_time = today.replace(hour = random_hour, minute = random_minute, second = 0).strftime("%H:%M:%S")

		return date_time
	
	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, users: UsersManager):
		"""Инициализация."""

		#---> Генерация статических атрибутов.
		#==========================================================================================#

		if os.path.exists("Data/WordMonth/Letters.json"): self.__Data = ReadJSON("Data/WordMonth/Letters.json")
		else: self.__Data = {}

		#---> Генерация динамических атрибутов.
		#==========================================================================================#

		self.__users = users

	def randomize_time(self):
		"""Разброс посланий (пользователь - рандомное время) и сохранение в формате json."""

		self.__Data = {}

		for User in self.__users.users:
			time = self.__random_time()
			self.__Data[str(User.id)] = time

		WriteJSON("Data/WordMonth/Letters.json", self.__Data)

	def users_mailing_now(self) -> list:
		"""
		Пользователи, которым будет сейчас произведена рассылка.

		:return: список пользователей, которые требуют рассылки.
		:rtype: list
		"""

		id_users = []

		now = datetime.now().time()
		for user_id, time in self.__Data.items():
			if now >= datetime.strptime(time, "%H:%M:%S").time(): id_users.append(user_id)
			
		return id_users
	
	def delete_time_mailings(self, user_id: str):

		"""Удаление данных произведённой рассылки."""
		
		self.__Data.pop(user_id, None)
		WriteJSON("Data/WordMonth/Letters.json", self.__Data)

#==========================================================================================#
# >>>>> DECORATORS <<<<< #
#==========================================================================================#

class Decorators:
	"""Набор декораторов."""

	def __init__(self, mailer: "Mailer"):

		#---> Генерация динамических атрибутов.
		#==========================================================================================#
		self.__Mailer = mailer
		
	def inline_keyboards(self):
		"""
		Обработка inline_keyboards.
		"""

		@self.__Mailer.bot.callback_query_handler(func = lambda Callback: Callback.data == "send_appeal")
		def send_appeal(Call: types.CallbackQuery):
			user = self.__Mailer.users.auth(Call.from_user)
			if not self.__Mailer.subscription.IsSubscripted(user): 
				self.__Mailer.bot.answer_callback_query(Call.id)
				return
			self.__Mailer.masterbot.safely_delete_messages(
				chat_id = Call.message.chat.id,
				messages = Call.message.id
			)
			text = self.__Mailer.word_month.randomize_text(texts = self.__Mailer.reader.appeals)
			self.__Mailer.bot.send_message(
				chat_id = Call.message.chat.id,
				text = text,
				reply_markup = WordMonthInlineTemplates.start_appeals(text)
				)
			
			self.__Mailer.bot.answer_callback_query(Call.id)

		@self.__Mailer.bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("card_day"))
		def card_day(Call: types.CallbackQuery):
			user = self.__Mailer.users.auth(Call.from_user)
			if not self.__Mailer.subscription.IsSubscripted(user): 
				self.__Mailer.bot.answer_callback_query(Call.id)
				return
			
			today = datetime.today().strftime("%d.%m.%Y")

			with open(f"Materials/Texts/{today}.txt") as file:
				text = file.read()

			appeals = True if self.__Mailer.appeals.is_mailing_day() else False

			if user.has_property("send_appeal"): send_appeal = user.get_property("send_appeal")
			else: send_appeal = False

			if appeals and not send_appeal: button = WordMonthInlineTemplates.appeal_or_delete(text = "Благодарю!", appeal = appeals) 
			else: button = InlineKeyboards.for_delete("Благодарю!")

			self.__Mailer.bot.send_video(
				chat_id = Call.message.chat.id,
				video = self.__Mailer.cacher.get_real_cached_file(f"Materials/Video/{today}.mp4", types.InputMediaVideo).file_id,
				caption = text, 
				reply_markup = button,
				parse_mode = "HTML"
				)
			
			user.set_property("send_appeal", True)
			self.__Mailer.bot.answer_callback_query(Call.id)

#==========================================================================================#
# >>>>> РАССЫЛЬЩИК <<<<< #
#==========================================================================================#

class Mailer:

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def word_month(self) -> WordMonth:
		"""Работа с призывами."""

		return self.__WordMonth
	
	@property
	def appeals(self) -> Appeals:
		"""Призывы."""

		return self.__Appeals
	
	@property
	def letters(self) -> Letters:
		"""Послания."""

		return self.__Letters
	
	@property
	def decorators(self) -> Decorators:
		"""Набор декораторов."""

		return self.__Decorators
	
	@property
	def masterbot(self) -> TeleMaster:
		"""Masterbot."""

		return self.__masterbot
	
	@property
	def bot(self) -> TeleBot:
		"""Telegram bot."""

		return self.__masterbot.bot

	@property
	def users(self) -> UsersManager:
		"""Менеджер пользователей."""

		return self.__users
	
	@property
	def reader(self) -> Reader:
		"""Читатель excel-файлов."""

		return self.__reader
	
	@property
	def cacher(self) -> TeleCache:
		"""Менеджер кэша."""

		return self.__cacher
	
	@property
	def subscription(self) -> Subscription:
		"""Проверка подписки."""

		return self.__subscription

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __send_card_day(self, User: UserData, video: str, text: str) -> types.Message:
		"""
		Рассылка карты дня

		:param User: Данные пользователя.
		:type User: UserData
		:param video: Данные видео, которое будет отправлено в рассылке.
		:type video: str
		:param text: Данные текста, который будет отправлен в рассылке.
		:type text: str
		:return: Данные отправленного сообщения.
		:rtype: types.Message
		"""

		try:
			self.__Message = self.__masterbot.bot.send_video(
				chat_id = User.id,
				video = video,
				reply_markup = InlineKeyboards.for_delete("Да будет так!"),
				caption = text, 
				parse_mode = "HTML"
			)
			logging.info(f"Карта дня отправлена {User.id}")
			User.set_chat_forbidden(False)

		except: User.set_chat_forbidden(True)

		return self.__Message
	
	def __send_letters(self, user_id: str, text: str):
		"""
		Рассылка посланий.

		:param user_id: Id пользователя.
		:type User: str
		:param text: Данные текста, который будет отправлен в рассылке.
		:type text: str
		"""

		User = self.__users.get_user(user_id)

		try:
			self.__Message = self.__masterbot.bot.send_animation(
				chat_id = User.id,
				animation = self.__cacher.get_real_cached_file(
					path = "Data/WordMonth/letters.gif", 
					autoupload_type = types.InputMediaAnimation
					).file_id,
				caption = "<i>" + _("Наставление от Мастера 🔥 для тебя:") + "</i>" + "\n\n- " + "<b>" + text + "</b>", 
				parse_mode = "HTML",
				reply_markup = InlineKeyboards.for_restart("Принимаю!")
			)
			logging.info(f"Послание отправлено {User.id}")
			User.set_chat_forbidden(False)

		except: User.set_chat_forbidden(True)

		self.__Letters.delete_time_mailings(str(User.id))

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, masterbot: TeleMaster, users: UsersManager, reader: Reader, cacher: TeleCache, subscription: Subscription):
		"""
		Инициализация.

		:param masterbot: Masterbot.
		:type masterbot: TeleMaster
		:param users: Менеджер пользователей.
		:type users: UsersManager
		:param reader: читатель excel-файлов.
		:type reader: Reader
		:param cacher: Менеджер кэша.
		:type cacher: TeleCache
		"""

		#---> Генерация динамических атрибутов.
		#==========================================================================================#
		
		self.__masterbot = masterbot
		self.__users = users
		self.__reader = reader
		self.__cacher = cacher
		self.__subscription = subscription

		self.__WordMonth = WordMonth()
		self.__Appeals = Appeals(self)
		self.__Letters = Letters(users)
		self.__Decorators = Decorators(self)

	def card_day_mailing(self):
		"""Рассылка карты дня."""
		
		for User in self.__users.users:

			if User.has_property("mailing") and User.get_property("mailing"):
				today = datetime.today().strftime("%d.%m.%Y")
				text = None
				with open(f"Materials/Texts/{today}.txt") as file:
					text = file.read()
				
				self.__send_card_day(User = User, video = self.__cacher.get_real_cached_file(f"Materials/Video/{today}.mp4", types.InputMediaVideo).file_id, text = text)

	def letters_mailing(self):
		"""Рассылка посланий."""

		users_id = self.__Letters.users_mailing_now()
		for user_id in users_id:
			text = self.__WordMonth.randomize_text(self.__reader.letters)
			self.__send_letters(user_id = user_id, text = text)
