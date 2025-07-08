from dublib.Methods.Filesystem import ReadJSON, WriteJSON
from dublib.TelebotUtils.Users import UsersManager
from dublib.TelebotUtils.Master import TeleMaster
from dublib.TelebotUtils.Cache import TeleCache
from dublib.Engine.GetText import _

from Source.InlineKeyboards import InlineKeyboards
from Source.Modules.Subscription import Subscription
from Source.Core.Reader import Reader

from time import sleep
from telebot import TeleBot, types

import random

#==========================================================================================#
# >>>>> НАБОР INLINE_KEYBOARDS <<<<< #
#==========================================================================================#

class YesNoInlineTemplates:
	"""Набор Inline-keyboards"""

	def OpenCard() -> types.InlineKeyboardMarkup:
		"""Клавиатура открытия карты."""
		return types.InlineKeyboardMarkup([[types.InlineKeyboardButton(_("Открыть карту"), callback_data = "open_card")]])
	
#==========================================================================================#
# >>>>> DECORATORS <<<<< #
#==========================================================================================#

class Decorators:
	"""Набор декораторов."""

	def __init__(self, yes_no: "YesNo"):
		"""
		Инициализация.

		:param yes_no: Основной класс.
		:type yes_no: YesNo
		"""

		#---> Генерация динамических атрибутов.
		#==========================================================================================#

		self.__YesNo = yes_no

	def inline_keyboards(self):
		"""Обработка inline_keyboards."""

		@self.__YesNo.bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("yes_no"))
		def yes_no(Call: types.CallbackQuery):
			user = self.__YesNo.users.auth(Call.from_user)
			if not self.__YesNo.subscription.IsSubscripted(user): 
				self.__YesNo.bot.answer_callback_query(Call.id)
				return
			
			self.__YesNo.bot.send_message(
				Call.message.chat.id, 
				text = _("Загадай ситуацию, где ответ должен быть <b>Да</b> или <b>Нет</b>.\n\nКак будешь готов, нажми на \"Открыть карту\""), 
				reply_markup = YesNoInlineTemplates.OpenCard(),
				parse_mode = "HTML")
			
			self.__YesNo.bot.answer_callback_query(Call.id)

		@self.__YesNo.bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("open_card"))
		def InlineButtonCardDay(Call: types.CallbackQuery):
			user = self.__YesNo.users.auth(Call.from_user)
			if not self.__YesNo.subscription.IsSubscripted(user): 
				self.__YesNo.bot.answer_callback_query(Call.id)
				return
			
			self.__YesNo.masterbot.safely_delete_messages(
				Call.message.chat.id,
				Call.message.id
			)

			stiker_message = self.__YesNo.bot.send_message(
				chat_id = Call.message.chat.id, 
				text = "🔮"
				)
			sleep(2.5)

			self.__YesNo.masterbot.safely_delete_messages(
				Call.message.chat.id,
				stiker_message.id
			)
			
			image, choice_type = self.__YesNo.ChoiceRandomCard()
			if choice_type == "Straight":
				cards = self.__YesNo.reader.StraightCard
				values = self.__YesNo.reader.StraightValues

			if choice_type == "Reversed":
				cards = self.__YesNo.reader.ReversedCard
				values = self.__YesNo.reader.ReversedValues
			
			card, value = self.__YesNo.Get_Text(image, cards, values)
			PhotoID = self.__YesNo.cacher.get_real_cached_file(image, types.InputMediaPhoto)

			self.__YesNo.bot.send_photo(
				Call.message.chat.id, 
				photo = PhotoID.file_id,
				caption = f"<b>{card}</b>\n\nВаш ответ: <b>{value}</b>",
				reply_markup = InlineKeyboards.for_delete("Благодарю!"),
				parse_mode = "HTML")
			
			self.__YesNo.bot.answer_callback_query(Call.id)

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class YesNo:
	"""Модуль да/нет."""

	@property
	def decorators(self) -> Decorators:
		"""Набор декораторов."""

		return self.__Decorators
	
	@property
	def masterbot(self) -> TeleMaster:
		"""Telegram bot."""

		return self.__masterbot
	
	@property
	def bot(self) -> TeleBot:
		"""Telegram bot."""

		return self.__masterbot.bot
	
	@property
	def cacher(self) -> TeleCache:
		"""Менеджер кэша."""

		return self.__cacher
	
	@property
	def reader(self) -> Reader:
		"""Менеджер кэша."""

		return self.__reader
	
	@property
	def users(self) -> UsersManager:
		"""Менеджер кэша."""

		return self.__users
	
	@property
	def subscription(self) -> Subscription:
		"""Проверка подписки."""

		return self.__subscription
	
	def __init__(self, masterbot: TeleMaster, cacher: TeleCache, reader: Reader, users: UsersManager, subscription: Subscription) -> None:
		"""
		Инициализация

		:param Bot: Telegram bot.
		:type Bot: TeleBot
		:param Cacher: Менеджер кэширования файлов.
		:type Cacher: TeleCache
		"""

		self.__masterbot = masterbot
		self.__cacher = cacher
		self.__reader = reader
		self.__users = users
		self.__subscription = subscription
		
		self.__Decorators = Decorators(self)
					
	def ChoiceRandomCard(self) -> str:
		"""
		Выбор рандомной карты (тип и номер). 

		:return: рандомная карта, тип карты.
		:rtype: str
		"""

		image = None
		choice_type = random.choice(["Straight", "Reversed"])
		choice_card = random.randint(1, 78) 
		image = f"Materials/{choice_type}/{choice_card}.jpg"

		return image, choice_type
	
	def Get_Text(self, photo: str, cards: list, values: list) -> str:
		"""
		_summary_

		:param photo: путь к изображению карты.
		:type photo: str
		:param cards: список названий карт.
		:type cards: list
		:param values: список результатов карт.
		:type values: list
		:return: название и результат карты.
		:rtype: str
		"""

		index = int(photo.split("/")[-1].replace(".jpg", "")) - 1
		card = cards[index]
		value = values[index]

		return card, value
