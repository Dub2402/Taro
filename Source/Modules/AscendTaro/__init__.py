from dublib.TelebotUtils import UserData
from dublib.Methods.Data import ToIterable

import logging
from typing import Literal, Any, Iterable
from types import MappingProxyType

ParametersDetermination = MappingProxyType({
	"today_layouts": 0,
	"bonus_layouts": 0,
	"level_user": 0,
	"promo": None,
	"delete_limiter": []
})

MAX_LAYOUTS = 1

class Ascend:
	"""Контейнер бонусных данных пользователя."""

	@property
	def delete_limiter(self) -> list[int]:
		"""Список id сообщений, говорящих об ограничении количества онлайн раскладов и которые необходимо удалить."""

		return self.__Data["delete_limiter"]

	@property
	def is_layouts_available(self) -> bool:
		"""Состояние: доступны ли бесплатные онлайн расклады."""

		if self.__User.has_permissions("admin"): return True
		return self.__Data["today_layouts"] < MAX_LAYOUTS

	def __SetParameter(self, key: Literal["today_layouts", "bonus_layouts", "level_user", "promo", "delete_limiter"], value: Any):
		"""
		Сохраняет параметры бонусных данных пользователя.

		:param key: Ключ параметра.
		:type key: Literal["today_layouts", "bonus_layouts", "level_user", "promo", "delete_limiter"]
		:param value: Значение параметра.
		:type value: Any
		"""

		if key not in self.__Data.keys(): self.__Data[key] = value
		self.save()

	def __ValidateDate(self) -> dict[str, Any]:
		"""
		Проверяет валидность бонусных данных пользователя.

		:return: Данные пользователя.
		:rtype: dict[str, Any]
		"""
		
		if not self.__User.has_property("ascend"):
			self.__User.set_property("ascend", ParametersDetermination)
			
		else:
			Data: dict = self.__User.get_property("ascend")

			for Key in ParametersDetermination.keys():

				if Key not in Data.keys():
					Data[Key] = ParametersDetermination[Key]
					logging.debug(f"For user #{self.__User.id} key \"{Key}\" set to default.")

			self.__User.set_property("ascend", Data)

		return self.__User.get_property("ascend")

	def __init__(self, user: UserData):
		"""
		Контейнер бонусных данных пользователя.

		:param user: Данные пользователя.
		:type user: UserData
		"""

		self.__User = user
	
		self.__Data = self.__ValidateDate()

	def save(self):
		"""Сохраняет бонусные данные пользователя."""

		self.__User.set_property("ascend", self.__Data)

	def set_today_layouts(self, count: int):
		"""
		Передаёт параметры для сохранения бонусных данных пользователя.

		:param count: Количество бесплатных онлайн раскладов.
		:type count: int
		"""

		self.__SetParameter("today_layouts", count)

	def add_delete_limiter(self, message_id: Iterable[int] | int):
		"""
		Добавляет id сообщений, которые необходимо удалить и говорящие об ограничении использования онлайн раскладов.

		:param message_id: Сообщения об ограничении использования онлайн раскладов.
		:type message_id: Iterable[int] | int
		"""

		MessagesID = self.delete_limiter 
		MessagesID.extend(ToIterable(message_id))
		self.__SetParameter("delete_limiter", MessagesID)

	def incremente_today_layouts(self):
		"""Увеличивает количесто использованных сегодня раскладов."""

		self.__Data["today_layouts"] = self.__Data["today_layouts"] + 1
		self.save()