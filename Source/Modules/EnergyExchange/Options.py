from dublib.TelebotUtils.Users import UserData
from dublib.TelebotUtils.Master import TeleMaster
from dublib.Engine.GetText import _

from typing import Iterable

from telebot import TeleBot

class Options:
	"""Параметры обмена энергией пользователя."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def mails(self) -> list[str]:
		"""Последовательность посланий пользователю."""

		return self.__Data["mails"]

	@property
	def removable_messages(self) -> list[int]:
		"""Последовательность ID удаляемых сообщений."""

		return self.__Data["removable_messages"]
	
	@property
	def menu_message_id(self) -> int | None:
		"""ID сообщения с главным меню."""

		return self.__Data["menu_message_id"]
	
	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#
	
	def __ParseData(self):
		"""Парсит параметры обмена энергией."""

		if self.__User.has_property("energy_exchange"): self.__Data = self.__User.get_property("energy_exchange")
		else: self.save()

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, user: UserData):
		"""
		Параметры обмена энергией пользователя.

		:param user: Данные пользователя.
		:type user: UserData
		"""

		#---> Генерация динамических свойств.
		#==========================================================================================#
		self.__User = user

		self.__Data = {
			"removable_messages": [],
			"additional_menu": None,
			"exchange_menu": None,
			"mails": []
		}

		self.__ParseData()

	def add_removable_messages(self, messages: int | Iterable[int]):
		"""
		Добавляет ID сообщений или конкретного сообщения в набор удаляемых.

		:param messages: ID одного или нескольких сообщений.
		:type messages: int | Iterable[int]
		"""

		if type(messages) == int: messages = [messages]
		else: messages = list(messages)

		self.__Data["removable_messages"] += messages
		self.save()

	def delete_removable_messages(self, bot: TeleBot):
		"""
		Удаляет сообщения из содержащегося в параметрах списка.

		:param bot: Бот Telegram.
		:type bot: TeleBot
		"""
		
		TeleMaster(bot).safely_delete_messages(chat_id = self.__User.id, messages = self.__Data["removable_messages"], complex = True)
		self.__Data["removable_messages"] = list()
		self.save()

	def push_mail(self, mail: str):
		"""
		Добавляет послание в почтовый ящик пользователя.

		:param mail: Текст послания.
		:type mail: str
		"""

		self.__Data["mails"].append(mail)
		self.save()

	def remove_mail(self, mail: str):
		"""
		Удаляет послание с указанным текстом.

		:param mail: Текст послания.
		:type mail: str
		"""

		try: self.__Data["mails"].remove(mail)
		except ValueError: pass
		self.save()

	def save(self):
		"""Сохраняет параметры обмена энергией."""

		self.__User.set_property("energy_exchange", self.__Data)

	def set_menu_message_id(self, message_id: int | None):
		"""
		Сохраняет ID сообщения меню.

		:param messages: ID сообщения.
		:type messages: int | None
		"""

		self.__Data["menu_message_id"] = message_id
		self.save()
