from dublib.TelebotUtils.Users import UsersManager
from dublib.TelebotUtils import TeleMaster
from dublib.Engine.GetText import _
from dublib.TelebotUtils.Cache import RealCachedFile

from Source.EnergyExchange import OpenExchanger
from Source.InlineKeyboards import InlineKeyboards
from Source.Functions import IsSubscripted
from Source.Bot_addition import send_settings_mailing

from telebot import types

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

def decorators_additional_options(master_bot: TeleMaster, users: UsersManager, inline_keyboard: InlineKeyboards, Settings: dict, QrImage: RealCachedFile):
	"""
	Обработка доп. опций

	:param MasterBot: бот Telegram
	:type MasterBot: TeleMaster
	:param users: данные пользователей
	:type users: UsersManager
	:param inline_keyboard: объект класса 
	:type inline_keyboard: InlineKeyboards
	:param Settings: словарь с настройками 
	:type Settings: dict
	:param QrImage: qr-code.jpg
	:type QrImage: RealCachedFile
	"""
	
	@master_bot.bot.callback_query_handler(func = lambda Callback: Callback.data == "additional_options")
	def click_additional_options(Call: types.CallbackQuery):
		"""
		Нажатие на кнопку: "Доп. опции"

		:param Call: additional_options
		:type Call: types.CallbackQuery
		"""
		User = users.auth(Call.from_user)
		if not IsSubscripted(master_bot, User, Settings, inline_keyboard): 
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
		if not IsSubscripted(master_bot, users.auth(Call.from_user), Settings, inline_keyboard): 
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
		if not IsSubscripted(master_bot, users.auth(Call.from_user), Settings, inline_keyboard): 
			master_bot.bot.answer_callback_query(Call.id)
			return
		master_bot.bot.send_photo(
			chat_id = Call.message.chat.id, 
			photo = QrImage.file_id,
			caption = _('@Taro100_bot\n@Taro100_bot\n@Taro100_bot\n\n<b>Таробот | Расклад онлайн | Карта дня</b>\nБот, который ответит на все твои вопросы ❓❓❓\n\n<b><i>Пользуйся и делись с друзьями!</i></b>'), 
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
		if not IsSubscripted(master_bot,  users.auth(Call.from_user), Settings, inline_keyboard): 
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
		if not IsSubscripted(master_bot, users.auth(Call.from_user), Settings, inline_keyboard): 
			master_bot.bot.answer_callback_query(Call.id)
			return
		send_settings_mailing(master_bot.bot, Call.message, inline_keyboard)
		master_bot.bot.answer_callback_query(Call.id)