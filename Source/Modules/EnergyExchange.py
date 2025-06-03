from dublib.Methods.Filesystem import MakeRootDirectories, ReadJSON, WriteJSON
from dublib.TelebotUtils.Users import UserData, UsersManager
from dublib.TelebotUtils.Master import TeleMaster
from dublib.Engine.GetText import _

from typing import Iterable
from time import sleep
import random
import os

from telebot import TeleBot, types
import xlsxwriter
import pandas

#==========================================================================================#
# >>>>> ФУНКЦИИ <<<<< #
#==========================================================================================#

def OpenExchanger(bot: TeleBot, user: UserData):
	"""
	Отправляет стартовое сообщение обмена энергии.

	:param bot: Бот Telegram.
	:type bot: TeleBot
	:param user: Данные пользователя.
	:type user: UserData
	"""

	Text = (
		_("Весь мир существует по законам обмена энергией. И наш бот - <b>Таробот</b>, тому не исключение. Только у нас энергия тепла, любви и добра!"),
		_("Стань участником программы взаимной поддержки и напиши свое собственное послание. Оно придёт абсолютно рандомному участнику нашего бота и поднимет ему настроение)"),
		_("<b><i>А кто-то может написать и тебе!</i></b>")
	)
	bot.send_message(
		chat_id = user.id,
		text = "\n\n".join(Text),
		parse_mode = "HTML",
		reply_markup = ExchangerInlineTemplates.start(user)
	)

#==========================================================================================#
# >>>>> ВСПОМОГАТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

class Options:
	"""Параметры обмена энергией пользователя."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def mails(self) -> list[str]:
		"""Последовательность посланий пользователю."""

		return self.__Data["mails"]

	@property
	def removable_messages(self) -> list[int]:
		"""Последовательность ID удаляемых сообщений."""

		return self.__Data["removable_messages"]
	
	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#
	
	def __ParseData(self):
		"""Парсит параметры обмена энергией."""

		if self.__User.has_property("energy_exchange"): self.__Data = self.__User.get_property("energy_exchange")
		else: self.save()

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, user: UserData):
		"""
		Параметры обмена энергией пользователя.

		:param user: Данные пользователя.
		:type user: UserData
		"""

		#---> Генерация динамических свойств.
		#==========================================================================================#
		self.__User = user

		self.__Data = {
			"removable_messages": [],
			"mails": []
		}

		self.__ParseData()

	def add_removable_messages(self, messages: int | Iterable[int]):
		"""
		Добавляет ID сообщений или конкретного сообщения в набор удаляемых.

		:param messages: ID одного или нескольких сообщений.
		:type messages: int | Iterable[int]
		"""

		if type(messages) == int: messages = [messages]
		else: messages = list(messages)

		self.__Data["removable_messages"] += messages
		self.save()

	def delete_removable_messages(self, bot: TeleBot):
		"""
		Удаляет сообщения из содержащегося в параметрах списка.

		:param bot: Бот Telegram.
		:type bot: TeleBot
		"""

		for MessageID in self.__Data["removable_messages"]: TeleMaster(bot).safely_delete_messages(self.__User.id, MessageID)
		self.__Data["removable_messages"] = list()
		self.save()

	def push_mail(self, mail: str):
		"""
		Добавляет послание в почтовый ящик пользователя.

		:param mail: Текст послания.
		:type mail: str
		"""

		self.__Data["mails"].append(mail)
		self.save()

	def remove_mail(self, mail: str):
		"""
		Удаляет послание с указанным текстом.

		:param mail: Текст послания.
		:type mail: str
		"""

		try: self.__Data["mails"].remove(mail)
		except ValueError: pass
		self.save()

	def save(self):
		"""Сохраняет параметры обмена энергией."""

		self.__User.set_property("energy_exchange", self.__Data)

#==========================================================================================#
# >>>>> КОНТЕЙНЕРЫ ПОСЛАНИЙ <<<<< #
#==========================================================================================#

class MailsContainer:
	"""Контейнер одобренных посланий."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def all_mails(self) -> tuple[str]:
		"""Последовательность всех посланий."""

		return self.system_mails + self.users_mails

	@property
	def system_mails(self) -> tuple[str]:
		"""Последовтельность заранее заложенных посланий."""

		return tuple(self.__Data["Наши сообщения"])

	@property
	def users_mails(self) -> tuple[str]:
		"""Последовтельность посланий от пользователей."""

		return tuple(self.__Data["Сообщения клиентов"])

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self):
		"""Контейнер одобренных посланий."""

		#---> Генерация динамических свойств.
		#==========================================================================================#
		self.__Path = "Data/Exchange/Mails.xlsx"
		self.__Data = {
			"Наши сообщения": [],
			"Сообщения клиентов": []
		}

		self.reload()

	def append(self, mail: str):
		"""
		Добавляет новое послание.

		:param mail: Текст послания.
		:type mail: str
		"""

		if mail not in self.all_mails: self.__Data["Сообщения клиентов"].append(mail.strip())
		self.save()

	def reload(self):
		"""Считывает послания."""

		if os.path.exists(self.__Path):
			Data = pandas.read_excel(self.__Path, dtype = str)
			Data = Data.fillna("")
			self.__Data = Data.to_dict(orient = "list")
			self.__Data["Наши сообщения"] = list(filter(lambda Value: Value, self.__Data["Наши сообщения"]))
			self.__Data["Сообщения клиентов"] = list(filter(lambda Value: Value, self.__Data["Сообщения клиентов"]))

			for Type in ("Наши сообщения", "Сообщения клиентов"):
				for Index in range(0, len(self.__Data[Type])): self.__Data[Type][Index] = self.__Data[Type][Index].strip()
			
		else: self.save()

	def save(self):
		"""Сохраняет таблицу посланий."""

		if os.path.exists(self.__Path): os.remove(self.__Path)
		WorkBook = xlsxwriter.Workbook(self.__Path)
		WorkSheet = WorkBook.add_worksheet("Послания")

		Bold = WorkBook.add_format({"bold": True})
		Wrap = WorkBook.add_format({"text_wrap": True, "valign": "top"})

		ColumnIndex = 0
		for ColumnName in self.__Data.keys():
			WorkSheet.write(0, ColumnIndex, ColumnName, Bold)
			ColumnIndex += 1

		WorkSheet.write_column(1, 0, self.__Data["Наши сообщения"], Wrap)
		WorkSheet.write_column(1, 1, self.__Data["Сообщения клиентов"], Wrap)

		WorkSheet.autofit(max_width = 500)
		WorkBook.close()

class UnmoderatedBuffer:
	"""Буфер ещё не прошедших модерацию посланий."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def mails(self) -> tuple[str]:
		"""Набор посланий."""

		return tuple(self.__Data["unmoderated"])

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self):

		#---> Генерация динамических свойств.
		#==========================================================================================#
		self.__Path = "Data/Exchange/Unmoderated.json"
		self.__Data = {
			"unmoderated": []
		}

		self.reload()

	def append(self, mail: str):
		"""
		Добавляет новое послание для модерации.

		:param mail: Текст послания.
		:type mail: str
		"""

		if mail not in self.__Data["unmoderated"]: self.__Data["unmoderated"].append(mail)
		self.save()

	def reload(self):
		"""Считывает не прошедшие модерацию послания."""

		if os.path.exists(self.__Path): self.__Data = ReadJSON(self.__Path)
		else: self.save()

	def remove(self, mail: str):
		"""
		Удаляет послание из буфера.

		:param mail: Текст послания.
		:type mail: str
		"""

		try:
			self.__Data["unmoderated"].remove(mail)
			self.save()

		except ValueError: pass

	def save(self):
		"""Сохраняет список посланий."""

		WriteJSON(self.__Path, self.__Data)

#==========================================================================================#
# >>>>> ШАБЛОНЫ <<<<< #
#==========================================================================================#

class ExchangerInlineTemplates:
	"""Генератор Inline-интерфейса."""

	def accept():
		"""Строит Inline-интерфейс: конец работы."""

		Menu = types.InlineKeyboardMarkup()
		Accept = types.InlineKeyboardButton(_("Спасибо, принимаю!"), callback_data = "ee_accept")
		Menu.add(Accept)

		return Menu

	def back():
		"""Строит Inline-интерфейс: возврат назад."""

		Menu = types.InlineKeyboardMarkup()
		Back = types.InlineKeyboardButton("◀️ " + _("Назад"), callback_data = "ee_to_menu")
		Menu.add(Back)

		return Menu

	def end():
		"""Строит Inline-интерфейс: конец работы."""

		Menu = types.InlineKeyboardMarkup()
		More = types.InlineKeyboardButton(_("Написать ещё"), callback_data = "ee_message")
		ThankYou = types.InlineKeyboardButton(_("Спасибо, чуть позже!"), callback_data = "ee_to_menu")
		Menu.add(More, ThankYou, row_width = 1)

		return Menu

	def message():
		"""Строит Inline-интерфейс: одобрение посланий."""

		Menu = types.InlineKeyboardMarkup()
		Edit = types.InlineKeyboardButton(_("Исправить"), callback_data = "ee_edit")
		Confirm = types.InlineKeyboardButton(_("Подтвердить"), callback_data = "ee_confirm")
		Menu.add(Edit, Confirm, row_width = 1)

		return Menu

	def start(user: UserData):
		"""
		Строит Inline-интерфейс: выгрузка.

		:param user: Данные пользователя.
		:type user: UserData
		"""

		UserOptions = Options(user)
		Notifications = " (" + str(len(UserOptions.mails)) + ")" if UserOptions.mails else ""

		Menu = types.InlineKeyboardMarkup()
		Mail = types.InlineKeyboardButton(_("Моя почта") + Notifications, callback_data = "ee_mails")
		NewMessage = types.InlineKeyboardButton(_("Написать послание"), callback_data = "ee_message")
		Back = types.InlineKeyboardButton("◀️ " + _("Назад"), callback_data = "ee_close")
		Menu.add(Mail, NewMessage, Back, row_width = 1)

		return Menu	
	
	def thank_you(text: str):
		"""
		Строит Inline-интерфейс: позже придумаю.

		:param text: Текст благодарности.
		:type text: str
		"""

		Menu = types.InlineKeyboardMarkup()
		ThankYou = types.InlineKeyboardButton(text, callback_data = "ee_to_menu")
		Menu.add(ThankYou)

		return Menu

#==========================================================================================#
# >>>>> НАБОРЫ ОБРАБОТЧИКОВ <<<<< #
#==========================================================================================#

class Decorators:
	"""Набор декораторов."""

	def __init__(self, exchanger: "Exchanger"):

		#---> Генерация динамических свойств.
		#==========================================================================================#
		self.__Exchanger = exchanger

	def inline_keyboards(self):
		"""Набор декораторов: Inline-кнопки."""

		bot = self.__Exchanger.bot
		users = self.__Exchanger.users

		@bot.callback_query_handler(func = lambda Callback: Callback.data == "ee_accept")
		def Accept(Call: types.CallbackQuery):
			User = users.auth(Call.from_user)
			UserOptions = Options(User)
			UserOptions.remove_mail(Call.message.text)
			TeleMaster(bot).safely_delete_messages(Call.from_user.id, Call.message.id)

			if not UserOptions.mails:
				UserOptions.delete_removable_messages(bot)
				Start(Call)

		@bot.callback_query_handler(func = lambda Callback: Callback.data == "ee_close")
		def Close(Call: types.CallbackQuery):
			TeleMaster(bot).safely_delete_messages(Call.from_user.id, Call.message.id) 

		@bot.callback_query_handler(func = lambda Callback: Callback.data == "ee_confirm")
		def Confirm(Call: types.CallbackQuery):
			User = users.auth(Call.from_user)
			User.set_expected_type(None)
			self.__Exchanger.unmoderated_mails.append(User.get_property("ee_new_message"))
			User.clear_temp_properties()

			Text = (
				_("Ваше послание успешно отправлено на проверку!"),
				_("Если вы в хорошем настроении, то напишите ещё что-то. Вам это вернётся в 10 раз больше 😊!")
			)
			TeleMaster(bot).safely_delete_messages(Call.from_user.id, Call.message.id)
			bot.send_message(
				chat_id = Call.from_user.id,
				text = "\n\n".join(Text),
				reply_markup = ExchangerInlineTemplates.end()
			)

		@bot.callback_query_handler(func = lambda Callback: Callback.data == "ee_edit")
		def Edit(Call: types.CallbackQuery):
			User = users.auth(Call.from_user)
			UserOptions = Options(User)

			TeleMaster(bot).safely_delete_messages(Call.from_user.id, Call.message.id)
			UserOptions.add_removable_messages(
				bot.send_message(
					chat_id = Call.from_user.id,
					text = _("Введите, пожалуйста, исправленный текст:")
				).id
			)

		@bot.callback_query_handler(func = lambda Callback: Callback.data == "ee_mails")
		def Message(Call: types.CallbackQuery):
			User = users.auth(Call.from_user)
			UserOptions = Options(User)
			TeleMaster(bot).safely_delete_messages(Call.from_user.id, Call.message.id)

			if UserOptions.mails: 
				UserOptions.add_removable_messages(bot.send_message(Call.from_user.id, _("ВАШИ ПОСЛАНИЯ:")).id)

				for Mail in UserOptions.mails:
					UserOptions.add_removable_messages(bot.send_message(Call.from_user.id, Mail, reply_markup = ExchangerInlineTemplates.accept()).id)
					sleep(0.1)

				UserOptions.add_removable_messages(
					bot.send_message(
						chat_id = Call.from_user.id,
						text = _("Для возврата в предыдущее меню нажмите \"<b>Назад</b>\":"),
						parse_mode = "HTML",
						reply_markup = ExchangerInlineTemplates.back()
					).id
				)

			else:
				Text = (
					_("У вас пока нет входящих посланий! Но не переживайте!"),
					_("<b>Вы самый лучший человек на планете Земля!</b> Хорошего вам дня!)")
				)
				bot.send_message(
					chat_id = Call.from_user.id,
					text = "\n\n".join(Text),
					parse_mode = "HTML",
					reply_markup = ExchangerInlineTemplates.thank_you("Спасибо, очень приятно!")
				)

		@bot.callback_query_handler(func = lambda Callback: Callback.data == "ee_message")
		def Message(Call: types.CallbackQuery):
			User = users.auth(Call.from_user)
			UserOptions = Options(User)
			User.set_expected_type("ee_message")

			TeleMaster(bot).safely_delete_messages(Call.from_user.id, Call.message.id)
			UserOptions.add_removable_messages(
				bot.send_message(
					chat_id = Call.from_user.id,
					text = _("У вас есть лимит на 200 символов, чтобы обрадовать человека и написать свой текст:"),
					reply_markup = ExchangerInlineTemplates.thank_you(_("Спасибо, чуть позже придумаю!"))
				).id
			)

		@bot.callback_query_handler(func = lambda Callback: Callback.data == "ee_start")
		def Start(Call: types.CallbackQuery):
			User = users.auth(Call.from_user)
			TeleMaster(bot).safely_delete_messages(Call.from_user.id, Call.message.id)
			OpenExchanger(bot, User)

		@bot.callback_query_handler(func = lambda Callback: Callback.data == "ee_to_menu")
		def ToMenu(Call: types.CallbackQuery):
			User = users.auth(Call.from_user)
			User.set_expected_type(None)
			UserOptions = Options(User)
			TeleMaster(bot).safely_delete_messages(Call.from_user.id, Call.message.id)
			UserOptions.delete_removable_messages(bot)

			Text = (
				_("Весь мир существует по законам обмена энергией. И наш бот - <b>Таробот</b>, тому не исключение. Только у нас энергия тепла, любви и добра!"),
				_("Стань участником программы взаимной поддержки и напиши свое собственное послание. Оно придёт абсолютно рандомному участнику нашего бота и поднимет ему настроение)"),
				_("<b>А кто-то может написать и тебе!</b>")
			)
			bot.send_message(
				chat_id = User.id,
				text = "\n\n".join(Text),
				parse_mode = "HTML",
				reply_markup = ExchangerInlineTemplates.start(User)
			)

class Procedures:
	"""Набор процедур."""

	def __init__(self, exchanger: "Exchanger"):

		#---> Генерация динамических свойств.
		#==========================================================================================#
		self.__Exchanger = exchanger

	def text(self, message: types.Message) -> bool:
		"""
		Процедура обработки текста.

		:param message: Структура сообщения.
		:type message: types.Message
		:return: Если процедура сработала, возвращает `True`.
		:rtype: bool
		"""

		bot = self.__Exchanger.bot
		users = self.__Exchanger.users

		User = users.auth(message.from_user)
		UserOptions = Options(User)

		if User.expected_type != "ee_message": return False
		UserOptions.add_removable_messages(message.id)
		LENGTH = len(message.text)

		if LENGTH <= 200:
			User.set_temp_property("ee_new_message", message.text)
			Text = (
				_("<b>ВАШ ТЕКСТ:</b>"),
				message.text,
				_("<i>Проверьте, пожалуйста, все ли правильно вы написали.</i>")
			)
			UserOptions.add_removable_messages(
				bot.send_message(
					chat_id = User.id,
					text = "\n\n".join(Text),
					parse_mode = "HTML",
					reply_markup = ExchangerInlineTemplates.message()
				).id
			)
		
		else:
			UserOptions.add_removable_messages(
				bot.send_message(
					chat_id = User.id,
					text = _("Ваше посление слишком длинное (%d символов). Попробуйте сократить его до 200!") % LENGTH
				).id
			)

		return True

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class Exchanger:
	"""Модуль обмена энергией."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def bot(self) -> TeleBot:
		"""Бот Telegram."""

		return self.__Bot

	@property
	def users(self) -> UsersManager:
		"""Менеджер пользователей."""

		return self.__Users

	#==========================================================================================#
	# >>>>> КОНТЕЙНЕРЫ ПОСЛАНИЙ <<<<< #
	#==========================================================================================#

	@property
	def mails_container(self) -> MailsContainer:
		"""Контейнер посланий."""

		return self.__MailsContainer
	
	@property
	def unmoderated_mails(self) -> UnmoderatedBuffer:
		"""Буфер не прошедших модерацию сообщений."""

		return self.__UnmoderatedBuffer

	#==========================================================================================#
	# >>>>> НАБОРЫ ОБРАБОТЧИКОВ <<<<< #
	#==========================================================================================#
	
	@property
	def decorators(self) -> Decorators:
		"""Набор декораторов."""

		return self.__Decorators
	
	@property
	def procedures(self) -> Procedures:
		"""Набор процедур."""

		return self.__Procedures

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, bot: TeleBot, users: UsersManager):
		"""
		Модуль обмена энергией.

		:param bot: Бот Telegram.
		:type bot: TeleBot
		:param users: Менеджер пользователей.
		:type users: UsersManager
		"""

		#---> Генерация динамических свойств.
		#==========================================================================================#
		self.__Bot = bot
		self.__Users = users

		MakeRootDirectories(["Data/Exchange"])

		self.__Decorators = Decorators(self)
		self.__Procedures = Procedures(self)
		self.__UnmoderatedBuffer = UnmoderatedBuffer()
		self.__MailsContainer = MailsContainer()

	def get_unmoderated_mails(self) -> tuple[str]:
		"""
		Возвращает последовательность ещё не прошедших модерацию посланий.

		:return: Последовательность посланий.
		:rtype: tuple[str]
		"""

		return self.unmoderated_mails.mails

	def moderate_mail(self, mail: str, status: bool):
		"""
		Выполняет обработку модерации послания.

		:param mail: Текст послания.
		:type mail: str
		:param status: Статус модерации.
		:type status: bool
		"""

		self.__UnmoderatedBuffer.remove(mail)
		if status: self.__MailsContainer.append(mail)

	def open(self, user: UserData):
		"""
		Отправляет стартовое сообщение модуля обмена энергии.
		
		:param user: Данные пользователя.
		:type user: UserData
		"""

		OpenExchanger(self.__Bot, user)

	def push_mails(self):
		"""Запускает расфасовку посланий пользователям."""

		if not self.__MailsContainer.all_mails: return

		for User in self.__Users.users:
			UserOptions = Options(User)
			Mail = random.choice(self.__MailsContainer.all_mails)
			if len(UserOptions.mails) < 10 and Mail not in UserOptions.mails: UserOptions.push_mail(Mail)