from dublib.Methods.Filesystem import ReadJSON, WriteJSON

import os

import xlsxwriter
import pandas

class LayoutsExamples:
	"""Контейнер шаблонов вопросов."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def all_questions(self) -> tuple[str]:
		"""Последовательность всех вопросов."""

		return self.common_questions + self.love_questions

	@property
	def common_questions(self) -> tuple[str]:
		"""Последовтельность общих вопросов."""

		return tuple(self.__Data["Общие вопросы:"])

	@property
	def love_questions(self) -> tuple[str]:
		"""Последовтельность вопросов про любовь."""

		return tuple(self.__Data["Про любовь:"])

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self):
		"""Контейнер шаблонов вопросов."""

		self.__Path = "Materials/Онлайн_расклад.xlsx"
		self.__Data = {
			"Общие вопросы:": [],
			"Про любовь:": []
		}

		self.__UnmoderatedPath = "Data/UnmoderatedLayoutsExample.json"
		self.__Unmoderated = list()

		self.reload()

	def add_common(self, question: str):
		"""
		Добавляет новый общий вопрос.

		:param mail: Текст вопроса.
		:type mail: str
		"""

		if question not in self.all_questions: self.__Data["Общие вопросы:"].append(question.strip())
		self.save()

	def add_unmoderated_common(self, question: str):
		"""
		Добавляет не прошедший модерацию общий вопрос.

		:param mail: Текст вопроса.
		:type mail: str
		"""

		self.__Unmoderated.append(question.strip())
		WriteJSON(self.__UnmoderatedPath, self.__Unmoderated)

	def get_unmoderated_common(self) -> tuple[str]:
		"""
		Возвращает последовательность не прошедших модерацию вопросов.

		:return: Последовательность не прошедших модерацию вопросов.
		:rtype: tuple[str]
		"""

		return tuple(self.__Unmoderated)

	def moderate_common(self, question: str, status: bool, edited_question: str):
		"""
		Модерирует общий вопрос.

		:param question: Текст вопроса.
		:type question: str
		:param status: _description_
		:type status: bool
		:param edited_question: _description_
		:type edited_question: str
		"""

		try: self.__Unmoderated.remove(question)
		except ValueError: pass

		if status: self.add_common(edited_question if edited_question else question)

	def reload(self):
		"""Считывает послания."""

		if os.path.exists(self.__Path):
			Data = pandas.read_excel(self.__Path, dtype = str)
			Data = Data.fillna("")
			self.__Data = Data.to_dict(orient = "list")
			self.__Data["Общие вопросы:"] = list(filter(lambda Value: Value, self.__Data["Общие вопросы:"]))
			self.__Data["Про любовь:"] = list(filter(lambda Value: Value, self.__Data["Про любовь:"]))

			for Type in ("Общие вопросы:", "Про любовь:"):
				for Index in range(0, len(self.__Data[Type])): self.__Data[Type][Index] = self.__Data[Type][Index].strip()
			
		else: self.save()

		if os.path.exists(self.__UnmoderatedPath): self.__Unmoderated = ReadJSON(self.__UnmoderatedPath)
		else: self.__Unmoderated = list()

	def save(self):
		"""Сохраняет таблицу посланий."""

		if os.path.exists(self.__Path): os.remove(self.__Path)
		WorkBook = xlsxwriter.Workbook(self.__Path)
		WorkSheet = WorkBook.add_worksheet("Вопросы")

		Bold = WorkBook.add_format({"bold": True})
		Wrap = WorkBook.add_format({"text_wrap": True, "valign": "top"})

		ColumnIndex = 0
		for ColumnName in self.__Data.keys():
			WorkSheet.write(0, ColumnIndex, ColumnName, Bold)
			ColumnIndex += 1

		WorkSheet.write_column(1, 0, self.__Data["Общие вопросы:"], Wrap)
		WorkSheet.write_column(1, 1, self.__Data["Про любовь:"], Wrap)

		WorkSheet.autofit(max_width = 500)
		WorkBook.close()