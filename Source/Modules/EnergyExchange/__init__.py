from .Scheduler import Scheduler
from .Options import Options

from Source.UI.AdditionalOptions import InlineTemplates
from Source.Modules.Subscription import Subscription
from Source.InlineKeyboards import InlineKeyboards

from dublib.Methods.Filesystem import MakeRootDirectories, ReadJSON, WriteJSON
from dublib.TelebotUtils.Users import UserData, UsersManager
from dublib.TelebotUtils.Master import TeleMaster
from dublib.TelebotUtils.Cache import TeleCache
from dublib.Engine.GetText import _

from time import sleep
import random
import os

from telebot import TeleBot, types
import xlsxwriter
import pandas

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
		More = types.InlineKeyboardButton(_("Написать ещё" + " +"), callback_data = "ee_message")
		ThankYou = types.InlineKeyboardButton(_("Спасибо, чуть позже!"), callback_data = "ee_main_menu")
		Menu.add(More, ThankYou, row_width = 1)

		return Menu

	def message():
		"""Строит Inline-интерфейс: одобрение посланий."""

		Menu = types.InlineKeyboardMarkup()
		Edit = types.InlineKeyboardButton("✍️ " + _("Исправить"), callback_data = "ee_edit")
		Confirm = types.InlineKeyboardButton("✅️ " +_("Подтвердить"), callback_data = "ee_confirm")
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
		"""
		Набор декораторов.

		:param exchanger: Модуль обмена энергией.
		:type exchanger: Exchanger
		"""


		self.__Exchanger = exchanger

	def inline_keyboards(self):
		"""Набор декораторов: Inline-кнопки."""

		bot = self.__Exchanger.bot
		users = self.__Exchanger.users

		@bot.callback_query_handler(func = lambda Callback: Callback.data == "energy_exchange")
		def Open(Call: types.CallbackQuery):
			"""
			Отправляет стартовое сообщение обмена энергии.

			:param Call: energy_exchange
			:type Call: types.CallbackQuery
			"""

			User = users.auth(Call.from_user)
			if not self.__Exchanger.subscription.IsSubscripted(User): 
				self.__Exchanger.bot.answer_callback_query(Call.id)
				return
			
			self.__Exchanger.open(User, Call.message.id)
			self.__Exchanger.bot.answer_callback_query(Call.id)

		@bot.callback_query_handler(func = lambda Callback: Callback.data == "ee_confirm")
		def Confirm(Call: types.CallbackQuery):
			User = users.auth(Call.from_user)
			UserOptions = Options(User)
			if not self.__Exchanger.subscription.IsSubscripted(User): 
				self.__Exchanger.bot.answer_callback_query(Call.id)
				return
			
			User.set_expected_type(None)
			self.__Exchanger.unmoderated_mails.append(User.get_property("ee_new_message"))
			User.clear_temp_properties()

			Text = (
				_("<i>" + "Ваше послание успешно отправлено на проверку!" + "</i>"),
				_("Если вы в хорошем настроении, то напишите ещё что-то. Вам это вернётся <b>в 10 раз больше!</b>" + " 😊")
			)
			TeleMaster(bot).safely_delete_messages(Call.from_user.id, Call.message.id)
			Message = bot.send_message(
				chat_id = Call.from_user.id,
				text = "\n\n".join(Text),
				parse_mode = "HTML",
				reply_markup = ExchangerInlineTemplates.end()
			)
			UserOptions.add_removable_messages(Message.id)

		@bot.callback_query_handler(func = lambda Callback: Callback.data == "ee_accept")
		def Accept(Call: types.CallbackQuery):
			User = users.auth(Call.from_user)
			if not self.__Exchanger.subscription.IsSubscripted(User): 
				self.__Exchanger.bot.answer_callback_query(Call.id)
				return
			UserOptions = Options(User)
			UserOptions.remove_mail(Call.message.text)
			TeleMaster(bot).safely_delete_messages(Call.from_user.id, Call.message.id)
			self.__Exchanger.open(User)

			if not UserOptions.mails:
				UserOptions.delete_removable_messages(bot)
				Start(Call)

		@bot.callback_query_handler(func = lambda Callback: Callback.data == "ee_edit")
		def Edit(Call: types.CallbackQuery):
			User = users.auth(Call.from_user)
			if not self.__Exchanger.subscription.IsSubscripted(User): 
				self.__Exchanger.bot.answer_callback_query(Call.id)
				return
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
			bot.answer_callback_query(Call.id)

			if not self.__Exchanger.subscription.IsSubscripted(User): 
				self.__Exchanger.bot.answer_callback_query(Call.id)
				return

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
					_("<b>Вы самый лучший человек на планете Земля! Хорошего вам дня!)</b>" + " 💋")
				)
				bot.send_message(
					chat_id = Call.from_user.id,
					text = "\n\n".join(Text),
					parse_mode = "HTML",
					reply_markup = ExchangerInlineTemplates.thank_you(_("Спасибо, очень приятно!"))
				)

		@bot.callback_query_handler(func = lambda Callback: Callback.data == "ee_message")
		def Message(Call: types.CallbackQuery):
			User = users.auth(Call.from_user)
			bot.answer_callback_query(Call.id)

			if not self.__Exchanger.subscription.IsSubscripted(User): 
				self.__Exchanger.bot.answer_callback_query(Call.id)
				return
			
			UserOptions = Options(User)
			User.set_expected_type("ee_message")

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
			if not self.__Exchanger.subscription.IsSubscripted(User): 
				self.__Exchanger.bot.answer_callback_query(Call.id)
				return
			TeleMaster(bot).safely_delete_messages(Call.from_user.id, Call.message.id)

		@bot.callback_query_handler(func = lambda Callback: Callback.data == "ee_to_menu")
		def ToMenu(Call: types.CallbackQuery):
			User = users.auth(Call.from_user)

			if not self.__Exchanger.subscription.IsSubscripted(User): 
				self.__Exchanger.bot.answer_callback_query(Call.id)
				return
			
			User.set_expected_type(None)
			UserOptions = Options(User)
			TeleMaster(bot).safely_delete_messages(Call.from_user.id, Call.message.id)
			UserOptions.delete_removable_messages(bot)
			# Условие исправляет попытку редактирования меню при пустом почтовом ящике.
			if UserOptions.mails: self.__Exchanger.open(User)

		@bot.callback_query_handler(func = lambda Callback: Callback.data == "ee_close")
		def Close(Call: types.CallbackQuery):
			User = users.auth(Call.from_user)
			UserOptions = Options(User)

			if not self.__Exchanger.subscription.IsSubscripted(User): 
				self.__Exchanger.bot.answer_callback_query(Call.id)
				return
			
			UserOptions.delete_removable_messages(bot)
			self.__Exchanger.close(User)

		@bot.callback_query_handler(func = lambda Callback: Callback.data == "ee_main_menu")
		def FullClose (Call: types.CallbackQuery):
			User = users.auth(Call.from_user)
			UserOptions = Options(User)

			if not self.__Exchanger.subscription.IsSubscripted(User): 
				self.__Exchanger.bot.answer_callback_query(Call.id)
				return
			
			UserOptions.delete_removable_messages(bot)
			self.__Exchanger.full_close(User)

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
				_("<i>Проверьте, пожалуйста, все ли правильно вы написали?</i>")
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
	
	@property
	def cacher(self) -> TeleCache:
		"""Менеджер кэша."""

		return self.__cacher
	
	@property
	def subscription(self) -> Subscription:
		"""Проверка подписки."""

		return self.__subscription

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

	def __init__(self, bot: TeleBot, users: UsersManager, cacher: TeleCache, subscription: Subscription):
		"""
		Модуль обмена энергией.

		:param bot: Бот Telegram.
		:type bot: TeleBot
		:param users: Менеджер пользователей.
		:type users: UsersManager
		"""

		self.__Bot = bot
		self.__Users = users
		self.__cacher = cacher
		self.__subscription = subscription

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

	def open(self, user: UserData, message_id: int | None = None):
		"""
		Редактирует сообщение в стартовое сообщение модуля обмена энергии.
		
		:param user: Данные пользователя.
		:type user: UserData
		:param message_id: ID сообщения.
		:type message_id: int
		"""

		UserOptions = Options(user)
		Text = (
				_("Весь мир существует по законам обмена энергией. И наш бот - <b>Таробот</b>, тому не исключение. Только у нас энергия тепла, любви и добра!"),
				_("<i>Стань участником программы взаимной поддержки и напиши свое собственное послание. Оно прилетит абсолютно рандомному участнику нашего бота и поднимет ему настроение 🤗</i>"),
				_("<b><i>А кто-то может написать и тебе!)</i></b>")
			)

		File = self.cacher.get_real_cached_file(
			path = "Data/Exchange/start.gif", 
			autoupload_type = types.InputMediaAnimation
		)
		
		if not message_id: message_id = UserOptions.menu_message_id
		else: UserOptions.set_menu_message_id(message_id)
		
		message_id = self.bot.edit_message_media(
			media = types.InputMediaAnimation(
				media = File.file_id,
				caption = "\n\n".join(Text),
				parse_mode = "HTML"
			),
			chat_id = user.id,
			message_id = message_id,
			reply_markup = ExchangerInlineTemplates.start(user)
		).id

	def close(self, user: UserData):
		"""
		Редактирует меню обмена энергии в меню дополнительных опций.
		
		:param user: Данные пользователя.
		:type user: UserData
		"""

		file = self.cacher.get_real_cached_file(
			path = "Start.mp4", 
			autoupload_type = types.InputMediaAnimation
		)
		
		self.bot.edit_message_media(
			media = types.InputMediaAnimation(
				media = file.file_id,
				caption = "<b>ДОП. ОПЦИИ</b>",
				parse_mode = "HTML"
			),
			chat_id = user.id,
			message_id = Options(user).menu_message_id,
			reply_markup = InlineTemplates.additional_options(user)
		)

	def full_close(self, user: UserData):
		"""
		Редактирует меню обмена энергии в главное меню бота.
		
		:param user: Данные пользователя.
		:type user: UserData
		"""

		file = self.cacher.get_real_cached_file(
			path = "Start.mp4", 
			autoupload_type = types.InputMediaAnimation
		)
		
		self.bot.edit_message_media(
			media = types.InputMediaAnimation(
				media = file.file_id
			),
			chat_id = user.id,
			message_id = Options(user).menu_message_id,
			reply_markup = InlineKeyboards.main_menu(user)
		)

	def push_mails(self):
		"""Запускает расфасовку посланий пользователям."""

		if not self.__MailsContainer.all_mails: return

		for User in self.__Users.users: self.push_mail(User)

	def push_mail(self, user: UserData):
		"""
		Помещает послание в почтовый ящик пользователя.

		:param user: Данные пользователя.
		:type user: UserData
		"""

		UserOptions = Options(user)
		Mail = random.choice(self.__MailsContainer.all_mails)
		if len(UserOptions.mails) < 10 and Mail not in UserOptions.mails: UserOptions.push_mail(Mail)