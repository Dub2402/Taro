from dublib.TelebotUtils.Users import UsersManager, UserData
from dublib.TelebotUtils.Cache import TeleCache
from dublib.TelebotUtils import TeleMaster
from dublib.Engine.GetText import _

from Source.Modules.EnergyExchange.Options import Options as ExchangeOptions
from Source.Modules.AscendTaro import AscendData, Sender as AscendSender
from Source.UI.WorkpiecesMessages import WorkpiecesMessages
from Source.Modules.Subscription import Subscription
from Source.InlineKeyboards import InlineKeyboards
from Source.Core.ExcelTools import Reader

from telebot import TeleBot, types
from apscheduler.schedulers.background import BackgroundScheduler
from types import MappingProxyType
from typing import Any, Literal
from datetime import datetime
import logging

MottoParameters = MappingProxyType(
	{
		"day": None,
		"text": "",
		"message_id": None
		}
)

class InlineTemplates:
	"""Набор Inline-keyboards."""

	def additional_options(user: UserData) -> types.InlineKeyboardMarkup:
		"""
		Inline-клавиатура: дополнительные опций: 

		:return: Inline-keyboard.
		:rtype: types.InlineKeyboardMarkup
		"""

		menu = types.InlineKeyboardMarkup()

		buttons = []

		UserOptions = ExchangeOptions(user)
		Notifications = " (" + str(len(UserOptions.mails)) + ")" if UserOptions.mails else ""

		determinations_first = {
			_("Девиз на сегодня"): "motto_day",
			Notifications + _(" Обмен энергией"): "energy_exchange"
		}

		determinations_second = {
			_("МОЙ УРОВЕНЬ ТАРОБОТА 🏆"): "level_tarobot",
			_("Марафон недели 🏁"): "marathons"
		}

		determinations_third = {
			_("◀️ Назад"): "main_menu",
			_("Настройки"): "menu_settings"
		}

		for string in determinations_first.keys(): buttons.append(types.InlineKeyboardButton(string, callback_data = determinations_first[string]))
		menu.add(*buttons, row_width = 2)
		buttons = []
		for string in determinations_second.keys(): menu.add(types.InlineKeyboardButton(string, callback_data = determinations_second[string]), row_width = 1)
		for string in determinations_third.keys(): buttons.append(types.InlineKeyboardButton(string, callback_data = determinations_third[string]))
		menu.add(*buttons, row_width = 2)
		return menu
	
	def menu_settings(user: UserData) -> types.InlineKeyboardMarkup:
		"""
		Inline-клавиатура: меню настроек:

		:return: Inline-keyboard.
		:rtype: types.InlineKeyboardMarkup
		"""

		menu = types.InlineKeyboardMarkup()

		determinations = {
			_("Рассылка карты дня"): "mailing_card_day",
			_("Перезапуск бота"): "restart_bot",
			_("Обратная связь"): "feedback",
			_("Поделиться!"): "share",
			_("◀️ Назад"): "menu_settings"
		}

		for string in determinations.keys(): menu.add(types.InlineKeyboardButton(string, callback_data = determinations[string]), row_width = 1)
	
		return menu

	def restart_bot() -> types.InlineKeyboardMarkup:
		"""
		Inline-клавиатура: перезапуск бота: 

		:return: Inline-keyboard.
		:rtype: types.InlineKeyboardMarkup
		"""

		menu = types.InlineKeyboardMarkup()

		determinations = {
			_("Перезапустить сейчас!"): "for_restart",
			_("◀️ Назад"): "for_delete"
		}

		for string in determinations.keys(): menu.add(types.InlineKeyboardButton(string, callback_data = determinations[string]), row_width = 1)
		return menu

class Decorators:
	"""Набор декораторов."""

	def __init__(self, options: "Options"):
		"""
		Инициализация основных параметров

		:param options: Дополнительный функционал
		:type options: Options
		"""

		self.__Options = options

	def inline_keyboards(self):
		"""Обработка Callback-запросов"""
	
		@self.__Options.bot.callback_query_handler(func = lambda Callback: Callback.data == "additional_options")
		def click_additional_options(Call: types.CallbackQuery):
			"""
			Нажатие на кнопку: "Доп. опции"

			:param Call: additional_options
			:type Call: types.CallbackQuery
			"""

			user = self.__Options.users.auth(Call.from_user)
			if not self.__Options.subscription.IsSubscripted(user):
				self.__Options.bot.answer_callback_query(Call.id)
				return
			Message = self.__Options.bot.edit_message_caption(
				caption = "<b>ДОП. ОПЦИИ</b>",
				chat_id = Call.message.chat.id,
				message_id = Call.message.id,
				parse_mode = "HTML",
				reply_markup = self.__Options.inline_templates.additional_options(user)
			)
			self.__Options.bot.answer_callback_query(Call.id)
		
		@self.__Options.bot.callback_query_handler(func = lambda Callback: Callback.data == "menu_settings")
		def click_share(Call: types.CallbackQuery):
			"""
			Нажатие на кнопку: "Меню настроек:"

			:param Call: menu_settings
			:type Call: types.CallbackQuery
			"""

			user = self.__Options.users.auth(Call.from_user)
			if not self.__Options.subscription.IsSubscripted(user):
				self.__Options.bot.answer_callback_query(Call.id)
				return

			Message = self.__Options.bot.edit_message_caption(
				caption = "<b>Меню настроек:</b>",
				chat_id = Call.message.chat.id,
				message_id = Call.message.id,
				parse_mode = "HTML",
				reply_markup = self.__Options.inline_templates.menu_settings(user)
			)
			
			self.__Options.bot.answer_callback_query(Call.id)
			
		@self.__Options.bot.callback_query_handler(func = lambda Callback: Callback.data == "share")
		def click_share(Call: types.CallbackQuery):
			"""
			Нажатие на кнопку: "📣 Поделиться с друзьями"

			:param Call: share
			:type Call: types.CallbackQuery
			"""

			user = self.__Options.users.auth(Call.from_user)
			if not self.__Options.subscription.IsSubscripted(user):
				self.__Options.bot.answer_callback_query(Call.id)
				return
			path = self.__Options.settings["qr_image"]
			
			self.__Options.bot.send_photo(
				chat_id = Call.message.chat.id, 
				photo = self.__Options.cacher.get_real_cached_file(path, types.InputMediaPhoto).file_id,
				caption = _('@TarobotX_bot\n@TarobotX_bot\n@TarobotX_bot\n\n<b>Таробот | Расклад онлайн | Карта дня</b>\nСамый популярный бот для Таро-гаданий в Telegram! Ответит на любые твои вопросы ❓❓❓\n\n<b><i>Пользуйся и делись с друзьями!</i></b>'), 
				parse_mode = "HTML",
				reply_markup = InlineKeyboards.AddShare(buttons = ["Share", "Back"])
				)
			self.__Options.bot.answer_callback_query(Call.id)

		@self.__Options.bot.callback_query_handler(func = lambda Callback: Callback.data == "mailing_card_day")
		def click_back_delete(Call: types.CallbackQuery):
			"""
			Нажатие на кнопку: "📲 Рассылка Карты дня"

			:param Call: mailing_card_day
			:type Call: types.CallbackQuery
			"""
			user = self.__Options.users.auth(Call.from_user)
			if not self.__Options.subscription.IsSubscripted(user):
				self.__Options.bot.answer_callback_query(Call.id)
				return
			self.__Options.sender.settings_mailing(Call.message, action = "delete")
			self.__Options.bot.answer_callback_query(Call.id)

		@self.__Options.bot.callback_query_handler(func = lambda Callback: Callback.data == "restart_bot")
		def click_restart_bot(Call: types.CallbackQuery):
			"""
			Нажатие на кнопку: "🤖 Перезапуск бота"

			:param Call: mailing_card_day
			:type Call: types.CallbackQuery
			"""

			user = self.__Options.users.auth(Call.from_user)
			if not self.__Options.subscription.IsSubscripted(user):
				self.__Options.bot.answer_callback_query(Call.id)
				return
			Text = (
				("<b><i>" + _("Если у вас случилось так, что бот глючит или перестает вам отвечать, то не переживайте! Такое бывает, и это происходит по независящим от нас причинам!") + " 😥" + "</i></b>"),
				_("Это могут быть или сбои в Telegram, или слабая скорость интернета, или загруженность сервера и запросов. Вы можете в любой момент его <u>перезапустить</u> двумя способами:"),
				("1️⃣ ") + _("В левом нижнем углу есть синяя кнопочка \"Меню\". Можете на неё нажать и далее нажать на \"Перезапустить бот 🚀\""),
				("2️⃣ ") + _("Или самому написать в чат слово на английском языке с черточкой и отправить! Вот так: /start"),
				("<i>" + _("Далее подождать чуть-чуть, и он в любом случае заработает!") + "</i>"),
				("<b><i>" + _("Главное не паникуйте, ведь нам нужны всегда счастливые и здоровые пользователи !!!\nМы вами дорожим! 🥰" + "</i></b>"))
			   )
			self.__Options.bot.send_animation(
				chat_id = Call.message.chat.id, 
				animation = self.__Options.cacher.get_real_cached_file(
					path = "Data/AdditionalOptions/restart.mp4",
					autoupload_type = types.InputMediaAnimation
					).file_id,
				caption = "\n\n".join(Text),
				parse_mode = "HTML",
				reply_markup = self.__Options.inline_templates.restart_bot()
			)
			self.__Options.bot.answer_callback_query(Call.id)

		@self.__Options.bot.callback_query_handler(func = lambda Callback: Callback.data == "motto_day")
		def click_motto_day(Call: types.CallbackQuery):
			user = self.__Options.users.auth(Call.from_user)
			if not self.__Options.subscription.IsSubscripted(user):
				self.__Options.bot.answer_callback_query(Call.id)
				return
			
			motto_data = Data(user = user)
			if not motto_data.is_motto_available: 
				motto = self.__Options.reader.random_motto 
				motto_data.set_day()
				motto_data.set_text_motto(motto)
			else: motto = motto_data.text_motto

			self.__Options.masterbot.safely_delete_messages(chat_id = Call.message.chat.id, messages = motto_data.message_id)
			
			motto_message = self.__Options.bot.send_message(
				chat_id = Call.message.chat.id,
				text = "<b>«" + motto + "»</b>",
				parse_mode = "HTML",
				reply_markup = InlineKeyboards.for_delete("Да будет так!")
			)

			motto_data.set_message_id(message_id = motto_message.id)

			self.__Options.bot.answer_callback_query(Call.id)

		@self.__Options.bot.callback_query_handler(func = lambda Callback: Callback.data == "level_tarobot")
		def click_level_tarobot(Call: types.CallbackQuery):	
			user = self.__Options.users.auth(Call.from_user)
			if not self.__Options.subscription.IsSubscripted(user):
				self.__Options.bot.answer_callback_query(Call.id)
				return
			
			ascend_data = AscendData(user = user)
			level = ascend_data.level_tarobot
			bonus_layouts = ascend_data.bonus_layouts

			AscendSender(self.__Options.bot, self.__Options.cacher).level_tarobot(user = user, level = level, bonus_layouts = bonus_layouts)

			self.__Options.bot.answer_callback_query(Call.id)

class Data:
	"""Работа с данными модуля дополнительных опций."""

	@property
	def text_motto(self) -> str:
		"""Текст девиза дня."""

		return self.__Data["text"]
	
	@property
	def message_id(self) -> int:
		"""Id сообщений."""

		return self.__Data["message_id"]
	
	@property
	def day(self) -> str:
		"""День отправки девиза дня."""

		return self.__Data["day"]
	
	@property
	def today_date(self) -> str:
		"""Сегодняшняя дата."""

		return datetime.today().date().strftime("%d.%m.%Y")
	
	@property
	def is_motto_available(self) -> bool:
		"""Проверяет является ли текст девиза сегодняшним."""

		return self.today_date == self.day

	def __set_parameter(self, key: Literal["day", "text", "message_id"], value: Any):
		"""
		Задаёт параметры модуля девизов.

		:param key: Ключ параметра.
		:type key: Literal["day", "motto", "message_id"]
		:param value: Значение параметра.
		:type value: str
		"""

		self.__Data[key] = value
		
		self.__save()

	def __save(self):
		"""Сохраняет бонусные данные пользователя."""

		self.__User.set_property("motto", self.__Data)

	def __ValidateDate(self) -> dict[str, Any]:
		"""
		Проверяет валидность данных пользователя в модуле дополнительных опций.

		:return: Данные пользователя.
		:rtype: dict[str, Any]
		"""
		
		if not self.__User.has_property("motto"):
			self.__User.set_property("motto", MottoParameters.copy())
			
		else:
			Data: dict = self.__User.get_property("motto")

			for Key in MottoParameters.keys():

				if Key not in Data.keys():
					Data[Key] = MottoParameters[Key]
					logging.debug(f"For user #{self.__User.id} key \"{Key}\" set to default.")

			self.__User.set_property("motto", Data)

		return self.__User.get_property("motto")

	def __init__(self, user: UserData):
		"""
		Контейнер данных пользователя в модуле дополнительных опций.

		:param user: Данные пользователя.
		:type user: UserData
		"""

		self.__User = user
	
		self.__Data = self.__ValidateDate()
	
	def set_day(self):
		"""Передаёт сегодняшнюю дату в данные пользователя для модуля девиза дня."""

		self.__set_parameter("day", self.today_date)

	def set_text_motto(self, motto_text: str):
		"""
		Передаёт текст девиза дня в данные пользователя для модуля девиза дня.

		:param motto_text: Текст девиза дня.
		:type motto_text: str
		"""

		self.__set_parameter("text", motto_text)

	def set_message_id(self, message_id: int):
		"""
		Передаёт Id сообщения в данные пользователя для модуля девиза дня.

		:param message_id: Id сообщения.
		:type message_id: int
		"""

		self.__set_parameter("message_id", message_id)

class Options:
	"""Раздел бота, отвечающий за дополнительный функционал"""

	@property
	def decorators(self) -> Decorators:
		"""Наборы декораторов """
		return self.__Decorators
	
	@property
	def masterbot(self) -> TeleMaster:
		"""Masterbot"""
		return self.__masterbot
	
	@property
	def bot(self) -> TeleBot:
		"""Telegram bot """

		return self.__masterbot.bot
	
	@property
	def users(self) -> UsersManager:
		"""Данные о пользователях"""
		return self.__users
	
	@property
	def sender(self) -> WorkpiecesMessages:
		"""Набор Inline-keyboards"""
		return self.__sender
	
	@property
	def settings(self) -> dict:
		"""Основные настройки"""

		return self.__settings
	
	@property
	def cacher(self) -> TeleCache:
		"""Основные настройки."""
		
		return self.__cacher
	
	@property
	def subscription(self) -> Subscription:
		"""Проверка подписки."""
		
		return self.__subscription
	
	@property
	def inline_templates(self) -> InlineTemplates:
		"""Набор inline-keyboards."""
		
		return self.__inline_templates
	
	@property
	def reader(self) -> Reader:
		"""Читатель excel-файлы."""
		
		return self.__reader
	
	def __init__(self, masterbot: TeleMaster, users: UsersManager, Settings: dict, sender: WorkpiecesMessages, cacher: TeleCache, subscription: Subscription, reader: Reader):
		"""
		Инициализация   

		:param MasterBot: Telegram bot
		:type MasterBot: TeleMaster
		:param usermanager: данные пользователей
		:type usermanager: UsersManager
		:param InlineKeyboard: набор Inline-keyboards
		:type InlineKeyboard: InlineKeyboards
		:param Settings: словарь основных настроек
		:type Settings: dict
		:param sender: шаблоны сообщений
		:type sender: Sender
		"""

		self.__Decorators = Decorators(self)
		self.__inline_templates = InlineTemplates
		self.__masterbot = masterbot
		self.__users = users
		self.__settings = Settings
		self.__sender = sender
		self.__cacher = cacher
		self.__subscription = subscription
		self.__reader = reader
