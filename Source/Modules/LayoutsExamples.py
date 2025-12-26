from dublib.Methods.Filesystem import ReadJSON, WriteJSON

from typing import TYPE_CHECKING
import os

import xlsxwriter
import pandas

if TYPE_CHECKING:
	from Source.TeleBotAdminPanel.Modules.Moderation.Moderators.Base import ModerationSignal
	from Source.TeleBotAdminPanel.Modules.Moderation.Storage import Storage

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

		self.__Unmoderated: "Storage" = None

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

	def get_unmoderated_common(self) -> tuple[str]:
		"""
		Возвращает последовательность не прошедших модерацию вопросов.

		:return: Последовательность не прошедших модерацию вопросов.
		:rtype: tuple[str]
		"""

		return self.__Unmoderated.elements

	def moderate_common(self, signal: "ModerationSignal"):
		"""
		Выполняет обработку модерации послания.

		:param edited_mail: Сигнал от модератора.
		:type edited_mail: ModerationSignal
		"""

		if signal.status: self.add_common(signal.value)

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

	def set_unmoderated_common_storage(self, storage: "Storage"):
		"""
		Привязывает контейнер не прошедших модерацию общих вопросов.

		:param storage: Контейнер вопросов.
		:type storage: Storage
		"""

		self.__Unmoderated = storage