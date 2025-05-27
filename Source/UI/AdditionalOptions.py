from dublib.TelebotUtils.Users import UsersManager
from dublib.TelebotUtils import TeleMaster
from dublib.Engine.GetText import _
from dublib.TelebotUtils.Cache import RealCachedFile

from Source.EnergyExchange import OpenExchanger
from Source.InlineKeyboards import InlineKeyboards
from Source.Functions import IsSubscripted
from Source.UI.WorkpiecesMessages import WorkpiecesMessages

from telebot import types

#==========================================================================================#
# >>>>> INLINE_KEYBOARD <<<<< #
#==========================================================================================#

def keyboard_additional_options() -> types.InlineKeyboardMarkup:
	"""
	Клавиатура с кнопками: 
		💟 Обмен энергией
		📲 Рассылка Карты дня
		📣 Поделиться с друзьями
		◀️ Назад

	:return: Клавиатура дополнительных опций
	:rtype: types.InlineKeyboardMarkup
	"""
	Menu = types.InlineKeyboardMarkup()

	energy_exchange = types.InlineKeyboardButton(_("💟 Обмен энергией"), callback_data = "energy_exchange")
	mailing_card_day = types.InlineKeyboardButton(_("📲 Рассылка Карты дня"), callback_data = "mailing_card_day")
	share = types.InlineKeyboardButton(_("📣 Поделиться с друзьями"), callback_data = "share")
	back = types.InlineKeyboardButton(_("◀️ Назад"), callback_data = "Back_SendMainMenu")

	Menu.add(energy_exchange, mailing_card_day, share, back, row_width= 1) 

	return Menu

#==========================================================================================#
# >>>>> ДЕКОРАТОРЫ <<<<< #
#==========================================================================================#

class Decorators:
	"""Набор декораторов."""

	def __init__(self, options: "Options"):
		"""
		Инициализация основных параметров

		:param options: Дополнительный функционал
		:type options: Options
		"""
		self.__Options = options

	def inline_keyboards(self, QrImage: RealCachedFile):
		"""
		Обработка Callback-запросов

		:param QrImage: данные о изображении
		:type QrImage: RealCachedFile
		"""

		master_bot = self.__Options.master_bot
		inline_keyboard = self.__Options.inline_keyboard
		users = self.__Options.users
		settings = self.__Options.settings
		master_bot = self.__Options.master_bot
		sender = self.__Options.sender
	
		@master_bot.bot.callback_query_handler(func = lambda Callback: Callback.data == "additional_options")
		def click_additional_options(Call: types.CallbackQuery):
			"""
			Нажатие на кнопку: "Доп. опции"

			:param Call: additional_options
			:type Call: types.CallbackQuery
			"""

			User = users.auth(Call.from_user)
			if not IsSubscripted(master_bot, User, settings, inline_keyboard): 
				master_bot.bot.answer_callback_query(Call.id)
				return
			master_bot.bot.edit_message_caption(
				caption = "<b>ДОП. ОПЦИИ</b>",
				chat_id = Call.message.chat.id,
				message_id = Call.message.id,
				parse_mode = "HTML",
				reply_markup = keyboard_additional_options()
			)
			master_bot.bot.answer_callback_query(Call.id)

		@master_bot.bot.callback_query_handler(func = lambda Callback: Callback.data == "energy_exchange")
		def click_energy_exchange(Call: types.CallbackQuery):
			"""
			Открывает меню обмена энергией

			:param Call: energy_exchange
			:type Call: types.CallbackQuery
			"""

			if not IsSubscripted(master_bot, users.auth(Call.from_user), settings, inline_keyboard): 
				master_bot.bot.answer_callback_query(Call.id)
				return
			
			OpenExchanger(master_bot.bot, users.auth(Call.from_user))
			master_bot.bot.answer_callback_query(Call.id)
			
		@master_bot.bot.callback_query_handler(func = lambda Callback: Callback.data == "share")
		def click_share(Call: types.CallbackQuery):
			"""
			Нажатие на кнопку: "📣 Поделиться с друзьями"

			:param Call: share
			:type Call: types.CallbackQuery
			"""
			if not IsSubscripted(master_bot, users.auth(Call.from_user), settings, inline_keyboard): 
				master_bot.bot.answer_callback_query(Call.id)
				return
			master_bot.bot.send_photo(
				chat_id = Call.message.chat.id, 
				photo = QrImage.file_id,
				caption = _('@Taro100_bot\n@Taro100_bot\n@Taro100_bot\n\n<b>Таробот | Расклад онлайн | Карта дня</b>\nСамый большой бот для Таро гаданий в Telegram! Ответит на любые твои вопросы ❓❓❓\n\n<b><i>Пользуйся и делись с друзьями!</i></b>'), 
				parse_mode = "HTML",
				reply_markup = inline_keyboard.AddShare(buttons = ["Share", "Back"])
				)
			master_bot.bot.answer_callback_query(Call.id)

		@master_bot.bot.callback_query_handler(func = lambda Callback: Callback.data == "back_delete")
		def click_back_delete(Call: types.CallbackQuery):
			"""
			Нажатие на кнопку: "◀️ Назад"

			:param Call: back_delete
			:type Call: types.CallbackQuery
			"""

			if not IsSubscripted(master_bot,  users.auth(Call.from_user), settings, inline_keyboard): 
				master_bot.bot.answer_callback_query(Call.id)
				return
			master_bot.bot.delete_message(Call.message.chat.id, Call.message.id)
			master_bot.bot.answer_callback_query(Call.id)

		@master_bot.bot.callback_query_handler(func = lambda Callback: Callback.data == "mailing_card_day")
		def click_back_delete(Call: types.CallbackQuery):
			"""
			Нажатие на кнопку: "📲 Рассылка Карты дня"

			:param Call: mailing_card_day
			:type Call: types.CallbackQuery
			"""

			if not IsSubscripted(master_bot, users.auth(Call.from_user), settings, inline_keyboard): 
				master_bot.bot.answer_callback_query(Call.id)
				return
			sender.send_settings_mailing(Call.message, action = "delete")
			master_bot.bot.answer_callback_query(Call.id)

class Options:
	"""Раздел бота, отвечающий за дополнительный функционал"""

	@property
	def decorators(self) -> Decorators:
		"""Наборы декораторов """
		return self.__Decorators
	
	@property
	def master_bot(self) -> TeleMaster:
		"""Telegram bot """
		return self.__master_bot
	
	@property
	def users(self) -> UsersManager:
		"""Данные о пользователях"""
		return self.__users
	
	@property
	def inline_keyboard(self) -> InlineKeyboards:
		"""Набор Inline-keyboards"""
		return self.__inline_keyboard
	
	@property
	def sender(self) -> WorkpiecesMessages:
		"""Набор Inline-keyboards"""
		return self.__sender
	
	@property
	def settings(self) -> dict:
		"""Основные настройки"""
		return self.__settings

	def __init__(self, MasterBot: TeleMaster, users: UsersManager, InlineKeyboard: InlineKeyboards, Settings, sender: WorkpiecesMessages):
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
		self.__master_bot = MasterBot
		self.__users = users
		self.__inline_keyboard = InlineKeyboard
		self.__settings = Settings
		self.__sender = sender
