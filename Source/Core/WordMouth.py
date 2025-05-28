from dublib.Methods.Filesystem import WriteJSON, ReadJSON

from datetime import datetime
import random

class WordMonth:
	"""Работа с призывами."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#
	
	@property
	def mailing_days(self) -> dict[str, list[int]]:
		"""Получение всех дней рассылки призывов."""

		return ReadJSON("Appeals.json")
	
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
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __randomize(self):
		"""Разброс призывов по дням недели и сохранение в формате json."""
		Data = {}

		for week in range(1, 53):
			days = random.sample(population = list(range(7)), k = 4)
			days.sort()
			Data[str(week)] = days

		WriteJSON("Appeals.json", Data)

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def is_mailing_day(self) -> bool:
		"""
		Является ли сегодняшний день днём рассылки призыва.

		:return: Статус рассылки
		:rtype: bool
		"""

		if self.day_of_week in self.mailing_days[str(self.week_of_year)]: return True
		return False
