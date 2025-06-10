from dublib.Methods.Filesystem import ReadJSON, WriteJSON
from dublib.Engine.Bus import ExecutionStatus

from typing import TYPE_CHECKING
import random
import os

from apscheduler.schedulers.background import BackgroundScheduler

if TYPE_CHECKING:
	from . import Exchanger

class Scheduler:
	"""Планировщик задач обмена энергией."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def scheduler(self) -> BackgroundScheduler:
		"""Фоновое хранилище задач."""

		return self.__Scheduler
	
	@property
	def mailing_days(self) -> str:
		"""Дни рассылки в формате **cron**."""

		return ",".join(self.__Data["energy_exchange_days"])

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __CheckFirstLaunch(self):
		"""Проверяет первый запуск и генерирует изначальные точки срабатывания."""

		if not self.__Data["generated_for_this_week"]:
			self.__Data["generated_for_this_week"] = True
			self.select_random_days_of_week()

			Status = ExecutionStatus()
			Status.push_warning("First launch. Generated days: " + str(self.__Data["energy_exchange_days"]) + ".")
			Status.print_messages()

	def __ReadData(self):
		"""Считывает сохранённые точки планирования."""

		if os.path.exists(self.__Path): self.__Data = ReadJSON(self.__Path)
		else: self.save()

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, exchanger: "Exchanger", scheduler: BackgroundScheduler | None = None):
		"""
		Планировщик задач обмена энергией.

		:param exchanger: Модуль обмена энергией.
		:type exchanger: Exchanger
		:param scheduler: Фоновое хранилище задач.
		:type scheduler: BackgroundScheduler | None
		"""

		self.__Exchanger = exchanger
		self.__Scheduler = scheduler or BackgroundScheduler()

		self.__Path = "Data/Exchange/Scheduler.json"
		self.__DaysOfWeek = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")
		self.__Data = {
			"count_range": [2, 3],
			"energy_exchange_days": [],
			"generated_for_this_week": False
		}

		self.__ReadData()
		self.__CheckFirstLaunch()
		self.load_tasks()

	def load_tasks(self):
		"""Загружает задачи в фоновое хранилище."""

		self.__Scheduler.add_job(self.select_random_days_of_week, "cron", day_of_week = 0, hour = 0, minute = 0)
		self.__Scheduler.add_job(self.__Exchanger.push_mails, "cron", day_of_week = self.mailing_days, hour = 0, minute = 0, id = "ee_mailer")

	def save(self):
		"""Сохраняет точки планирования."""

		WriteJSON(self.__Path, self.__Data)

	def select_random_days_of_week(self):
		"""
		Выбирает случайные дни недели и обновляет задачу рассылки.

		:raise ValueError: Выбрасывается при неверном указании диапазона.
		"""

		COUNT = random.choice(self.__Data["count_range"])

		if COUNT < 1 or COUNT > 7: raise ValueError("Only 1 to 7 days.")
		self.__Data["energy_exchange_days"] = random.sample(self.__DaysOfWeek, k = COUNT)
		self.save()

		if self.__Scheduler.get_job("ee_mailer"):
			self.__Scheduler.remove_job("ee_mailer")
			self.__Scheduler.add_job(self.__Exchanger.push_mails, "cron", day_of_week = self.mailing_days, hour = 0, minute = 0, id = "ee_mailer")