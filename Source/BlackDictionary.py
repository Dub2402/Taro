from dublib.Methods.Filesystem import ListDir, ReadTextFile

class BlackDictionary:
	"""Оператор фильтрации текстового контента."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def words(self) -> tuple[str]:
		"""Набор нежелательных слов."""

		return self.__ForbiddenWords

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, path: str):
		"""
		Оператор фильтрации текстового контента.

		:param path: Путь к каталогу хранения чёрных списков.
		:type path: str
		"""

		#---> Генерация динамических свойств.
		#==========================================================================================#
		self.__Path: str = path

		self.__ForbiddenWords: tuple[str] = tuple()

		self.load()

	def validate_text(self, text: str) -> bool:
		"""
		Проверяет наличие в тексте нежелательных элементов.

		:param text: Проверяемый текст.
		:type text: str
		:return: В случае наличия нежелательных элементов возвращает `True`.
		:rtype: bool
		"""

		TextWords = text.split()

		for Word in self.__ForbiddenWords:
			if Word in TextWords: return True

		return False
	
	def load(self):
		"""Загружает чёрные списки из текстовых файлов."""

		Words = list()
		Files = ListDir(self.__Path)
		Files = tuple(filter(lambda File: File.endswith(".txt"), Files))

		for File in Files:
			FileContent = ReadTextFile(f"{self.__Path}/{File}")
			Words += FileContent.split()

		self.__ForbiddenWords = tuple(Words)