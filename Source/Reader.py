import pandas

class Reader:
	@property
	def Get_letters(self):
		return self.letters
	
	@property
	def Get_appeals(self):
		return self.appeals
	
	@property
	def Get_StraightCard(self):
		return self.StraightCard
	
	@property
	def Get_ReversedCard(self):
		return self.ReversedCard
	
	@property
	def Get_StraightValues(self):
		return self.StraightValues
	
	@property
	def Get_ReversedValues(self):
		return self.ReversedValues
	
	def __init__(self, Settings) -> None:
		self.letters = self.__ReadExcel(Settings["letters"], column = "Послания")
		self.appeals = self.__ReadExcel(Settings["letters"], column = "Призывы")

		self.StraightCard = self.__ReadExcel(Settings["yes_no"], column = "Обычные карты")
		self.StraightValues = self.__ReadExcel(Settings["yes_no"], column = "Значения обычных карт")
		self.ReversedCard = self.__ReadExcel(Settings["yes_no"], column = "Перевернутые карты")
		self.ReversedValues = self.__ReadExcel(Settings["yes_no"], column = "Значения перевернутых карт")

	def __ReadExcel(self, path_file: str, column: str) -> list:
		
		exceldata = pandas.read_excel(path_file)
		Products = pandas.DataFrame(exceldata, columns=[column])
		reading_data = Products[column].tolist()
		reading_data = list(filter(lambda x: str(x) != "nan", reading_data))
	
		return reading_data
	