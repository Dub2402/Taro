from dublib.Methods.Filesystem import ListDir

from os import PathLike
from datetime import datetime

PATH_VIDEO = "Materials/Video"
PATH_TEXTS = "Materials/Texts"
PATH_CHOICE_CARD = "Materials/ChoiceCard"

class Informator:

	@property 
	def latest_video(self):
		"""Дата самого нового видео из карты дня."""

		return self.__find_latest(path = PATH_VIDEO, type_format = ".mp4")
	
	@property 
	def latest_text(self):
		"""Дата самого нового текста из карты дня."""

		return self.__find_latest(path = PATH_TEXTS, type_format = ".txt")
	
	@property
	def latest_post(self):
		"""Дата самых новых постов из загадай карту."""
		
		return self.__latest_choice_card(type_finding = "post")

	@property
	def latest_photo(self):
		"""Дата самых новых фото из загадай карту."""

		return self.__latest_choice_card(type_finding = "photo")

	def __latest_choice_card(self, type_finding: str) -> str:
		"""
		Дата самой новой папки из загадай карту, учитывающий тип контента.

		:param type_finding: тип контента для поиска.
		:type type_finding: str
		:return: дата самой новой папки из загадай карту.
		:rtype: str
		"""

		excluded_files = []
		latest_full = False

		name_folder_the_last = self.__find_latest(path = PATH_CHOICE_CARD, type_format = "")
		if self.__all_posts_in_latest(name_folder = name_folder_the_last, type_finding = type_finding): return name_folder_the_last

		else: 
			excluded_files.append(name_folder_the_last)

			while not latest_full:
				name_folder = self.__find_latest(path = PATH_CHOICE_CARD, type_format = "", excluded_files = excluded_files)

				if self.__all_posts_in_latest(name_folder = name_folder, type_finding = type_finding): 
					latest_full = True
					return name_folder
				
				else: excluded_files.append(name_folder)

	def __find_latest(self, path: PathLike, type_format: str, excluded_files: list = []) -> str:
		"""
		Название самого нового файла/папки из выбранной папки.

		:param path: путь к файлу.
		:type path: PathLike
		:param type_format: формат файла.
		:type type_format: str
		:param excluded_files: файлы, которые нужно исключить из поиска, defaults to []
		:type excluded_files: list, optional
		:return: название самого нового файла.
		:rtype: str
		"""

		valid_dates = []

		for name_file in ListDir(path):
			try:
				if name_file not in excluded_files: 
				
					name_file_except_suffix = name_file.replace(type_format, "")
					date_obj = datetime.strptime(name_file_except_suffix, "%d.%m.%Y")
					valid_dates.append(date_obj)

			except: print(name_file)

		latest_date: datetime = max(valid_dates)
		latest_name_file = latest_date.strftime("%d.%m.%Y")

		return latest_name_file
	
	def __all_posts_in_latest(self, name_folder: str, type_finding: str) -> bool:
		"""
		Есть ли все типы файлов в самой новой папке.

		:param name_folder: название самой новой папки
		:type name_folder: str
		:return: статус: есть ли все типы файлов в папки.
		:rtype: bool
		"""

		existing_files = ListDir(PATH_CHOICE_CARD + "/" + name_folder)

		if type_finding == "post": 
			required_files = ["0.txt", "1.txt", "2.txt", "3.txt", "4.txt"]
			filtered_existing_files = [f for f in existing_files if not f.endswith(".jpg")]

		else: 
			required_files = ["0.jpg", "1.jpg", "2.jpg", "3.jpg", "4.jpg"]
			filtered_existing_files = [f for f in existing_files if not f.endswith(".txt")]
	
		missing_files = [f for f in required_files if f not in filtered_existing_files]
		
		if not missing_files: return True
		else: return False