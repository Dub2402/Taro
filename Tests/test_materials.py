from dublib.Methods.Filesystem import ListDir, ReadTextFile
from dublib.Engine.Bus import ExecutionStatus

from html.parser import HTMLParser
import os

from bs4 import BeautifulSoup
import pytest

#==========================================================================================#
# >>>>> ВАЛИДАТОР HTML <<<<< #
#==========================================================================================#

class Validator(HTMLParser):
	"""Валидатор базового HTML синтаксиса."""

	def __init__(self):
		"""Валидатор базового HTML синтаксиса."""

		super().__init__()

		self.stack = list()
		self.errors = list()

	def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]):
		self.stack.append(tag)

	def handle_endtag(self, tag: str):

		if not self.stack:
			self.errors.append(f"Closing tag </{tag}> not opened.")
			return
		
		if self.stack[-1] == tag:
			self.stack.pop()

		else:
			self.errors.append(f"Bad tags order: expected </{self.stack[-1]}>, found </{tag}>.")
			self.stack.pop()

	def error(self, message):
		self.errors.append(f"Parsing error: {message}.")

def ValidateHTML(text: str) -> list[str]:
	parser = Validator()
	parser.feed(text)

	if parser.stack:
		for tag in reversed(parser.stack): parser.errors.append(f"Opening tag <{tag}> not closed.")

	return parser.errors

#==========================================================================================#
# >>>>> ТЕСТЫ <<<<< #
#==========================================================================================#

def test_texts():
	"""Тестирует валидность HTML текстов карт дня."""

	TextsDirectoryPath = "Materials/Texts"
	if not os.path.exists(TextsDirectoryPath): pytest.skip(f"Directory \"{TextsDirectoryPath}\" not exists.")
	Files = ListDir(TextsDirectoryPath)
	IsSuccessfull = True
	Status = ExecutionStatus()
	AllowedTags = ("b", "strong", "i", "em", "u", "ins", "s", "strike", "del", "span", "a", "code", "pre")

	for File in Files:
		FilePath = f"{TextsDirectoryPath}/{File}"
		Text = ReadTextFile(FilePath)
		Errors = ValidateHTML(Text)
		for Message in Errors: Status.push_error(f"File: {FilePath}. {Message}")

		if Errors:
			IsSuccessfull = False
			continue

		for Tag in BeautifulSoup(Text, "html.parser").find_all():
			if Tag.name not in AllowedTags:
				Status.push_error(f"File: {FilePath}. Unsupported tag \"{Tag.name}\".")
				IsSuccessfull = False
				continue
		
	if not IsSuccessfull: Status.print_messages()
	assert IsSuccessfull == True

def test_choice_card():
	"""Тестирует валидность HTML текстов карт."""

	ChoiceCardDirectoryPath = "Materials/ChoiceCard"
	if not os.path.exists(ChoiceCardDirectoryPath): pytest.skip(f"Directory \"{ChoiceCardDirectoryPath}\" not exists.")
	ChoiceCardDirectories = ListDir(ChoiceCardDirectoryPath)
	IsSuccessfull = True
	Status = ExecutionStatus()
	AllowedTags = ("b", "strong", "i", "em", "u", "ins", "s", "strike", "del", "span", "a", "code", "pre")

	for Directory in ChoiceCardDirectories:
		DirectoryPath = f"{ChoiceCardDirectoryPath}/{Directory}"
		Files = ListDir(DirectoryPath)
		Files = tuple(filter(lambda Value: Value.endswith(".txt"), Files))

		for File in Files:
			FilePath = f"{DirectoryPath}/{File}"
			Text = ReadTextFile(FilePath)
			Errors = ValidateHTML(Text)
			for Message in Errors: Status.push_error(f"File: {FilePath}. {Message}")

			if Errors:
				IsSuccessfull = False
				continue

			for Tag in BeautifulSoup(Text, "html.parser").find_all():
				if Tag.name not in AllowedTags:
					Status.push_error(f"File: {FilePath}. Unsupported tag \"{Tag.name}\".")
					IsSuccessfull = False
					continue
		
	if not IsSuccessfull: Status.print_messages()
	assert IsSuccessfull == True