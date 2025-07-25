import pandas

from typing import Iterable
from os import PathLike
import random

class Reader:

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def letters(self) -> tuple[str]:
		"""Кортеж наставлений."""

		return self.__LettersDict["Наставления"]
	
	@property
	def appeals(self) -> tuple[str]:
		"""Кортеж призывов."""

		return self.__LettersDict["Призывы"]
		
	@property
	def StraightCard(self) -> tuple[str]:
		"""Кортеж названий прямых карт."""

		return self.__YesNoDict["Обычные карты"]

	@property
	def ReversedCard(self) -> tuple[str]:
		"""Кортеж названий перевёрнутых карт."""

		return self.__YesNoDict["Перевернутые карты"]
	
	@property
	def StraightValues(self) -> tuple[str]:
		"""Кортеж значений прямых карт."""

		return self.__YesNoDict["Значения обычных карт"]
	
	@property
	def ReversedValues(self) -> tuple[str]:
		"""Кортеж значений перевёрнутых карт."""

		return self.__YesNoDict["Значения перевернутых карт"]
	
	@property
	def mottos(self) -> tuple[str]:
		"""Кортеж девизов дня."""

		return self.__MottoDict["Девизы"]
	
	@property
	def general_questions(self) -> tuple[str]:
		"""Кортеж общих вопросов."""

		return self.__OnlineLayout["Общие вопросы:"]
	
	@property
	def love_questions(self) -> tuple[str]:
		"""Кортеж вопросов про любовь."""

		return self.__OnlineLayout["Про любовь:"]
	
	@property
	def random_motto(self):
		"""Рандомный девиз дня."""

		return random.choice(self.mottos)
	
	@property
	def random_love_question(self):
		"""Рандомный любовный вопрос."""

		return random.choice(self.general_questions)
	
	@property
	def random_general_question(self):
		"""Кортеж вопросов про любовь."""

		return random.choices(self.general_questions, k = 2)
	
	def __init__(self, Settings: dict):

		"""
		Инициализация.

		:param Settings: Настройки бота.
		:type Settings: dict
		"""

		self.__LettersDict = self.__ReadExcel(Settings["letters"])
		self.__YesNoDict = self.__ReadExcel(Settings["yes_no"])
		self.__MottoDict = self.__ReadExcel(Settings["motto_day"])
		self.__OnlineLayout = self.__ReadExcel(Settings["online_layout"])

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#
	
	def __ReadExcel(self, path: PathLike) -> tuple:
		"""
		Считывает файл Excel и интерпретирует его в словарь.

		:param path: Путь к файлу.
		:type path: PathLike
		:return: Словарное представление.
		:rtype: dict
		"""

		Data = pandas.read_excel(path, dtype = str)
		Data = Data.fillna("")
		DataDictionary: dict[str, Iterable[str]] = Data.to_dict(orient = "list")

		for Column in DataDictionary.keys(): DataDictionary[Column] = tuple(filter(lambda Value: Value, DataDictionary[Column]))

		for Column in DataDictionary.keys():
			Buffer = list()
			for Item in DataDictionary[Column]: Buffer.append(Item.strip())
			DataDictionary[Column] = tuple(Buffer)

		return DataDictionary