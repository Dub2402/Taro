from dublib.Methods.Filesystem import WriteJSON, ReadJSON
from dublib.TelebotUtils import UsersManager, UserData
from dublib.TelebotUtils import TeleMaster
from dublib.Engine.GetText import _

from Source.InlineKeyboards import InlineKeyboards
from Source.Core.Reader import Reader
from Source.Cards import Cards

from datetime import datetime
import random
import logging
import os

from telebot import types

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
			В другой раз

		:return: inline-keyboard
		:rtype: types.InlineKeyboardMarkup
		"""

		Menu = types.InlineKeyboardMarkup()

		share = types.InlineKeyboardButton(
			_("Поделиться"), 
			switch_inline_query = text
			)
		for_delete = types.InlineKeyboardButton(_("В другой раз"), callback_data = "for_delete")

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
	
		return ReadJSON("Data/WordMonth//Appeals.json")[str(week)]
	
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
		
		days = random.sample(population = list(range(7)), k = 4)
		days.sort()

		Data = {}
		Data[str(self.__week_of_year())] = days
		WriteJSON("Data/WordMonth/Appeals.json", Data)

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
		# random_hour = random.randint(9, 20)
		random_hour = random.randint(22, 22)
		random_minute = random.randint(0, 10)
		# random_minute = random.randint(0, 59)

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
		for time in self.__Data():
			if now >= datetime.strptime(time, "%H:%M:%S").time(): id_users.append(id_users)
			
		return id_users
	
	def delete_time_mailings(self, user_id: str):
		
		self.__Data.pop(user_id, None)
		WriteJSON("Data/WordMonth/Letters.json", self.__Data)

#==========================================================================================#
# >>>>> DECORATORS <<<<< #
#==========================================================================================#

class Decorators:
	"""Набор декораторов."""

	def __init__(self, masterbot: TeleMaster, users: UsersManager, WordMonth: WordMonth, reader: Reader):

		#---> Генерация динамических атрибутов.
		#==========================================================================================#

		self.__masterbot = masterbot
		self.__users = users
		self.__WordMonth = WordMonth
		self.__reader = reader

		self.__bot = self.__masterbot.bot

	def inline_keyboards(self):
		"""
		Обработка inline_keyboards.
		"""

		@self.__bot.callback_query_handler(func = lambda Callback: Callback.data == "send_appeal")
		def send_appeal(Call: types.CallbackQuery):
			User = self.__users.auth(Call.from_user)
			self.__masterbot.safely_delete_messages(
				chat_id = Call.message.chat.id,
				messages = Call.message.id
			)
			text = self.__WordMonth.randomize_text(texts = self.__reader.appeals)
			self.__bot.send_message(
				chat_id = Call.message.chat.id,
				text = text,
				reply_markup = WordMonthInlineTemplates.start_appeals(text)
				)
			
			self.__bot.answer_callback_query(Call.id)

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
			appeals = True if self.word_month.is_mailing_day() else False
			self.__Message = self.__bot.send_video(
				chat_id = User.id,
				video = video,
				reply_markup = WordMonthInlineTemplates.appeal_or_delete(text = "Благодарю!", appeal = appeals),
				caption = text, 
				parse_mode = "HTML"
			)
			logging.info(f"Карта дня отправлена {User.id}")
			User.set_chat_forbidden(False)

		except: User.set_chat_forbidden(True)

		return self.__Message
	
	def __send_letters(self, User: UserData, video: str, text: str) -> types.Message:
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
			self.__Message = self.__bot.send_video(
				chat_id = User.id,
				video = video,
				caption = text, 
				parse_mode = "HTML"
			)
			logging.info(f"Карта дня отправлена {User.id}")
			User.set_chat_forbidden(False)

		except: User.set_chat_forbidden(True)

		self.__Letters.delete_time_mailings(str(User.id))

		return self.__Message

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, masterbot: TeleMaster, users: UsersManager, Card: Cards, InlineKeyboard: InlineKeyboards, reader: Reader):
		"""
		Инициализация.

		:param bot: Telegram bot.
		:type bot: TeleBot
		:param usermanager: Менеджер пользователей.
		:type usermanager: UsersManager
		:param Card: работа с картами.
		:type Card: Cards
		:param InlineKeyboard: Набор inline-keyboards.
		:type InlineKeyboard: InlineKeyboards
		"""

		#---> Генерация динамических атрибутов.
		#==========================================================================================#
		
		self.__masterbot = masterbot
		self.__users = users
		self.__Card = Card
		self.__InlineKeyboard = InlineKeyboard
		self.__reader = reader

		self.__bot = self.__masterbot.bot

		self.__WordMonth = WordMonth()
		self.__Appeals = Appeals()
		self.__Letters = Letters(users)
		self.__Decorators = Decorators(self.__masterbot, self.__users, self.__WordMonth, self.__reader)

	def card_day_mailing(self):
		"""Рассылка карты дня."""
		
		for User in self.__users.users:
			logging.info(f"Проверка наличия рассылки для {User.id}")

			if User.has_property("mailing") and User.get_property("mailing"):
				InstantCard = self.__Card.GetInstantCard()

				if InstantCard: self.__send_card_day(User = User, video = InstantCard["video"], text = InstantCard["text"])

				else:
					Video, Text = self.__Card.GetCard()
					Message = self.__send_card_day(User = User, video = open(f"{Video}", "rb"), text = Text)
					self.__Card.AddCard(Message.video.file_id)

	def letters_mailing(self):
		"""Рассылка посланий."""

		users_id = self.__Letters.users_mailing_now()
		for User in users_id:
			text = self.__WordMonth.randomize_text(self.__reader.letters)
			self.__send_letters(User = User, text = text)
