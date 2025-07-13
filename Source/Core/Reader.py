import pandas

from os import PathLike
from typing import Iterable

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
	
	def __init__(self, Settings: dict):

		"""
		Инициализация.

		:param Settings: Настройки бота.
		:type Settings: dict
		"""

		self.__LettersDict = self.__ReadExcel(Settings["letters"])
		self.__YesNoDict = self.__ReadExcel(Settings["yes_no"])

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#
	
	def __ReadExcel(self, path: PathLike) -> dict:
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