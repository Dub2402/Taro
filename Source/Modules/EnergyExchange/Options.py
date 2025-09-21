from dublib.TelebotUtils.Users import UserData
from dublib.TelebotUtils.Master import TeleMaster
from dublib.Engine.GetText import _

from telebot import TeleBot

from typing import Iterable, Any
from types import MappingProxyType
import logging

ExchangeParameters = MappingProxyType(
	{
		"removable_messages": [],
		"additional_menu": None,
		"exchange_menu": None,
		"mails": [],
		"date_animation": "",
		"animation_path": ""
	}
)

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
	
	@property
	def date_animation(self) -> str:
		"""Строковое представление даты обновления обмена энергии."""

		return self.__Data["date_animation"]
	
	@property
	def animation_path(self) -> str:
		"""Имя анимации для обмена энергии."""

		return self.__Data["animation_path"]

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __ValidateDate(self) -> dict[str, Any]:
		"""
		Проверяет валидность бонусных данных пользователя.

		:return: Данные пользователя.
		:rtype: dict[str, Any]
		"""
		
		if not self.__User.has_property("energy_exchange"):
			self.__User.set_property("energy_exchange", ExchangeParameters.copy())
			
		else:
			Data: dict = self.__User.get_property("energy_exchange")

			for Key in ExchangeParameters.keys():

				if Key not in Data.keys():
					Data[Key] = ExchangeParameters[Key]
					logging.debug(f"For user #{self.__User.id} key \"{Key}\" set to default.")

			self.__User.set_property("energy_exchange", Data)

		return self.__User.get_property("energy_exchange")

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
	
		self.__Data = self.__ValidateDate()

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

	def set_date_animation(self, date: str):
		"""
		Сохраняет дату обновления анимации в обмене энергии.

		:param messages: Дата обновления анимации.
		:type messages: str
		"""

		self.__Data["date_animation"] = date
		self.save()

	def set_animation_path(self, name: str):
		"""
		Сохраняет имя анимации в обмене энергии.

		:param messages: Имя файла анимации.
		:type messages: str
		"""

		self.__Data["animation_path"] = name
		self.save()
