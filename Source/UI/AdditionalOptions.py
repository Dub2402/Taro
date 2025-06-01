from dublib.TelebotUtils.Users import UsersManager
from dublib.TelebotUtils.Cache import TeleCache
from dublib.TelebotUtils import TeleMaster
from dublib.Engine.GetText import _
from dublib.TelebotUtils.Cache import RealCachedFile

from Source.Modules.EnergyExchange import OpenExchanger
from Source.InlineKeyboards import InlineKeyboards
from Source.Functions import IsSubscripted
from Source.UI.WorkpiecesMessages import WorkpiecesMessages

from telebot import TeleBot, types

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
	back = types.InlineKeyboardButton(_("◀️ Назад"), callback_data = "main_menu")

	Menu.add(energy_exchange, mailing_card_day, share, back, row_width = 1) 

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

	def inline_keyboards(self):
		"""Обработка Callback-запросов"""
	
		@self.__Options.bot.callback_query_handler(func = lambda Callback: Callback.data == "additional_options")
		def click_additional_options(Call: types.CallbackQuery):
			"""
			Нажатие на кнопку: "Доп. опции"

			:param Call: additional_options
			:type Call: types.CallbackQuery
			"""

			User = self.__Options.users.auth(Call.from_user)
			if not IsSubscripted(self.__Options.masterbot, User, self.__Options.settings): 
				self.__Options.bot.answer_callback_query(Call.id)
				return
			self.__Options.bot.edit_message_caption(
				caption = "<b>ДОП. ОПЦИИ</b>",
				chat_id = Call.message.chat.id,
				message_id = Call.message.id,
				parse_mode = "HTML",
				reply_markup = keyboard_additional_options()
			)
			self.__Options.bot.answer_callback_query(Call.id)

		@self.__Options.bot.callback_query_handler(func = lambda Callback: Callback.data == "energy_exchange")
		def click_energy_exchange(Call: types.CallbackQuery):
			"""
			Открывает меню обмена энергией

			:param Call: energy_exchange
			:type Call: types.CallbackQuery
			"""
			
			OpenExchanger(self.__Options.bot, self.__Options.users.auth(Call.from_user))
			self.__Options.bot.answer_callback_query(Call.id)
			
		@self.__Options.bot.callback_query_handler(func = lambda Callback: Callback.data == "share")
		def click_share(Call: types.CallbackQuery):
			"""
			Нажатие на кнопку: "📣 Поделиться с друзьями"

			:param Call: share
			:type Call: types.CallbackQuery
			"""
			path = self.__Options.settings["qr_image"]
			
			self.__Options.bot.send_photo(
				chat_id = Call.message.chat.id, 
				photo = self.__Options.cacher.get_real_cached_file(path, types.InputMediaPhoto).file_id,
				caption = _('@Taro100_bot\n@Taro100_bot\n@Taro100_bot\n\n<b>Таробот | Расклад онлайн | Карта дня</b>\nСамый большой бот для Таро гаданий в Telegram! Ответит на любые твои вопросы ❓❓❓\n\n<b><i>Пользуйся и делись с друзьями!</i></b>'), 
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

			self.__Options.sender.settings_mailing(Call.message, action = "delete")
			self.__Options.bot.answer_callback_query(Call.id)

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
		"""Основные настройки"""
		
		return self.__cacher

	def __init__(self, masterbot: TeleMaster, users: UsersManager, Settings: dict, sender: WorkpiecesMessages, cacher: TeleCache):
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
		self.__masterbot = masterbot
		self.__users = users
		self.__settings = Settings
		self.__sender = sender
		self.__cacher = cacher
