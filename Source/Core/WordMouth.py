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

from telebot import types

#==========================================================================================#
# >>>>> INLINE_KEYBOARDS <<<<< #
#==========================================================================================#

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

class WordMonth:
	"""Работа с призывами."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#
	
	@property
	def mailing_days(self) -> dict[str, list[int]]:
		"""Получение всех дней рассылки призывов."""

		return ReadJSON("Data/WordMonth//Appeals.json")
	
	@property
	def day_of_week(self) -> int:
		"""Получение индекса текущего дня недели."""

		return datetime.now().weekday()
	
	@property
	def week_of_year(self) -> int:
		"""Получение текущего номера недели."""

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

		if self.day_of_week in self.mailing_days[str(self.week_of_year)]: return True
		return False
	
	def randomize_appeals_days(self):
		"""Разброс призывов по дням недели и сохранение в формате json."""
		
		days = random.sample(population = list(range(7)), k = 4)
		days.sort()

		Data = {}
		Data[str(self.week_of_year)] = days
		WriteJSON("Data/WordMonth/Appeals.json", Data)

	def randomize_appeal_text(self, appeals: list[str]) -> str:
		"""
		Выбрать случайный текст из призывов.

		:param appeals: Тексты призывов.
		:type appeals: list[str]
		:return: Случайный текст призыва.
		:rtype: str
		"""
		random_sentence = random.randint(1, len(appeals))
		
		for Index in range(len(appeals)):
			if Index == random_sentence-1:
				Text = appeals[Index]

		return Text

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
			text = self.__WordMonth.randomize_appeal_text(appeals = self.__reader.appeals)
			self.__bot.send_message(
				chat_id = Call.message.chat.id,
				text = text,
				reply_markup = start_appeals(text)
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
	def decorators(self) -> Decorators:
		"""Набор декораторов."""

		return self.__Decorators

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __card_day(self, User: UserData, video: str, text: str) -> types.Message:
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
				reply_markup = appeal_or_delete(text = "Благодарю!", appeal = appeals),
				caption = text, 
				parse_mode = 'HTML'
			)
			logging.info(f"Карта дня отправлена {User.id}")
			User.set_chat_forbidden(False)

		except ZeroDivisionError: User.set_chat_forbidden(True)

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
		self.__Decorators = Decorators(self.__masterbot, self.__users, self.__WordMonth, self.__reader)

	def card_day_mailing(self):
		"""Рассылка карты дня."""
		
		for User in self.__users.users:
			logging.info(f"Проверка рассылки для {User.id}")

			if User.has_property("mailing") and User.get_property("mailing"):
				InstantCard = self.__Card.GetInstantCard()

				if InstantCard: self.__card_day(User = User, video = InstantCard["video"], text = InstantCard["text"])

				else:
					Video, Text = self.__Card.GetCard()
					Message = self.__card_day(User = User, video = open(f"{Video}", "rb"), text = Text)
					self.__Card.AddCard(Message.video.file_id)
