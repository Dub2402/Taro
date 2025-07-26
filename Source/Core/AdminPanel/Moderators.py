from Source.TeleBotAdminPanel.Core.Moderation import Moderator

from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from Source.Modules.LayoutsExamples import LayoutsExamples

class ExchangeModerator(Moderator):

	def _ProcessModeration(self, value: str, status: bool, edited_value: str | None = None):
		"""
		Переопределите данный метод для обработки модерации. По умолчанию выводит результат модерации в консоль.

		:param value: Модерируемая строка.
		:type value: str
		:param status: Статус модерации.
		:type status: bool
		:param edited_value: Новое значение, если оригинальное модерировалось.
		:type edited_value: str | None
		"""

		self.__Exchanger.moderate_mail(value, status, edited_value)

	def connect_exchanger(self, exchanger: "Exchanger") -> "Exchanger":
		"""
		Подключает модуль обмена энергией.

		:param exchanger: Модуль обмена энергией.
		:type exchanger: Exchanger
		:return: Текущий модератор контента.
		:rtype: Exchanger
		"""

		self.__Exchanger = exchanger
		self.__ContentGetter = self.__Exchanger.get_unmoderated_mails

		return self
	
class LayoutsExamplesModerator:

	def _ProcessModeration(self, value: str, status: bool, edited_value: str | None = None):
		self.__Exampler.moderate_common(value, status, edited_value)

	def connect_object(self, exampler: "LayoutsExamples") -> "LayoutsExamples":
		"""
		Подключает модуль обмена энергией.

		:param exchanger: Модуль обмена энергией.
		:type exchanger: Exchanger
		:return: Текущий модератор контента.
		:rtype: Exchanger
		"""

		self.__Exampler = exampler
		self.__ContentGetter = self.__Exampler.get_unmoderated_common

		return self