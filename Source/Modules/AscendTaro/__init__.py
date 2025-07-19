from dublib.TelebotUtils import UserData
from dublib.Methods.Data import ToIterable

import logging
from typing import Literal, Any, Iterable
from types import MappingProxyType

ParametersDetermination = MappingProxyType(
	{
	"today_layouts": 0,
	"bonus_layouts": 0,
	"invited_users": [],
	"level_user": 0,
	"promo": None,
	"delete_limiter": []
	}
)

MAX_LAYOUTS = 1
MIN_BONUS_lAYOUTS = 0

class Ascend:
	"""Контейнер бонусных данных пользователя."""

	@property
	def is_today_layout_available(self):
		"""Состояние: доступен ли бесплатный онлайн расклад."""

		return self.__Data["today_layouts"] < MAX_LAYOUTS

	@property
	def is_bonus_layout_available(self):
		"""Состояние: доступен ли бонусный онлайн расклад."""

		return self.__Data["bonus_layouts"] > MIN_BONUS_lAYOUTS

	@property
	def invited_users(self) -> list[int]:
		"""Список id пользователей, выполнивших реферальную программу."""

		return self.__Data["invited_users"]
	
	@property
	def is_layout_available(self) -> bool:
		"""Состояние: доступен ли онлайн расклад."""

		if self.__User.has_permissions("admin"): return True
		if self.is_bonus_layout_available: return True
		if self.is_today_layout_available: return True
		return False

	@property
	def delete_limiter(self) -> list[int]:
		"""Список id сообщений, говорящих об ограничении количества онлайн раскладов и которые необходимо удалить."""

		return self.__Data["delete_limiter"]
	
	@property
	def count_invited_users(self) -> int:
		"""
		Количество приглашённых пользователей.

		:return: Количество приглашённых пользователей.
		:rtype: int
		"""

		return len(self.__Data["invited_users"])

	def __SetParameter(self, key: Literal["today_layouts", "bonus_layouts", "invited_users", "level_user", "promo", "delete_limiter"], value: Any):
		"""
		Сохраняет параметры бонусных данных пользователя.

		:param key: Ключ параметра.
		:type key: Literal["today_layouts", "bonus_layouts", "level_user", "invited_users", "promo", "delete_limiter"]
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
			self.__User.set_property("ascend", ParametersDetermination.copy())
			
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

	def add_invited_user(self, user_id: int):
		"""
		Добавляет id пользователя, которые выполнили условия реферальной программы, по ссылке пользователя.

		:param user_id:  id пользователя.
		:type user_id: int
		"""

		UsersID = self.invited_users
		if user_id in UsersID: return
		UsersID.append(user_id)
		self.__SetParameter("invited_users", UsersID)

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
		"""Увеличивает количество использованных бесплатных онлайн раскладов."""

		self.__Data["today_layouts"] = self.__Data["today_layouts"] + 1
		self.save()

	def decremente_bonus_layouts(self):
		"""Уменьшает количество использованных бонусных онлайн раскладов."""

		self.__Data["bonus_layouts"] = self.__Data["bonus_layouts"] - 1
		self.save()

	def add_bonus_layouts(self, count: int = 5):
		"""
		Увеличивает количество бонусных раскладов.

		:param count: Добавляемое количество бонусных раскладов, defaults to 5
		:type count: int, optional
		"""

		self.__Data["bonus_layouts"] = self.__Data["bonus_layouts"] + count
		print(self.__Data)
		self.save()