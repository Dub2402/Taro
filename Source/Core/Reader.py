import pandas

class Reader:

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def letters(self):
		"""Список посланий."""
		return self.__ReadExcel(self.__Settings["letters"], column = "Послания")
	
	@property
	def appeals(self):
		"""Список призывов."""
		return self.__ReadExcel(self.__Settings["letters"], column = "Призывы")
	
	@property
	def StraightCard(self):
		"""Список названий прямых карт."""
		return self.__ReadExcel(self.__Settings["yes_no"], column = "Обычные карты")
	
	@property
	def ReversedCard(self):
		"""Список названий перевёрнутых карт."""
		return self.__ReadExcel(self.__Settings["yes_no"], column = "Перевернутые карты")
	
	@property
	def StraightValues(self):
		"""Список значений прямых карт."""
		return self.__ReadExcel(self.__Settings["yes_no"], column = "Значения обычных карт")
	
	@property
	def ReversedValues(self):
		"""Список значений перевёрнутых карт."""
		return self.__ReadExcel(self.__Settings["yes_no"], column = "Значения перевернутых карт")
	
	def __init__(self, Settings: dict):

		"""
		Инициализация.

		:param Settings: Настройки бота.
		:type Settings: dict
		"""

		#---> Генерация динамических атрибутов.
		#==========================================================================================#

		self.__Settings = Settings

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __ReadExcel(self, path_file: str, column: str) -> list:
		"""
		Чтение колонки excel-файла.

		:param path_file: Путь к файлу.
		:type path_file: str
		:param column: Название колонки.
		:type column: str
		:return: Тексты в строках колонки.
		:rtype: list
		"""
		
		exceldata = pandas.read_excel(path_file)
		Products = pandas.DataFrame(exceldata, columns=[column])
		reading_data = Products[column].tolist()
		reading_data = list(filter(lambda x: str(x) != "nan", reading_data))
	
		return reading_data
	