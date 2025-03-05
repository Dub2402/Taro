import pandas

class Reader:
	@property
	def Get_letters(self):
		return self.letters
	
	@property
	def Get_appeals(self):
		return self.appeals
	
	def __init__(self, Settings) -> None:
		self.letters = self.__ReadExcel(Settings["letters"], column = "Послания")
		self.appeals = self.__ReadExcel(Settings["letters"], column = "Призывы")

	def __ReadExcel(self, path_file: str, column: str) -> list:
		
		exceldata = pandas.read_excel(path_file)
		Products = pandas.DataFrame(exceldata, columns=[column])
		reading_data = Products[column].tolist()
	
		return reading_data
	