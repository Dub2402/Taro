from dublib.Engine.GetText import _
from dublib.TelebotUtils.Users import UsersManager
from dublib.TelebotUtils import TeleMaster
from dublib.TelebotUtils.Cache import RealCachedFile

from Source.InlineKeyboards import InlineKeyboards

from telebot import TeleBot, types

#==========================================================================================#
# >>>>> INLINE_KEYBOARDS <<<<< #
#==========================================================================================#

def end_layout() -> types.InlineKeyboardMarkup:
	"""
	Строит Inline-интерфейс:
		Взять расклад у Мастера 🔥
		Благодарю за расклад!

	:return: keyboard
	:rtype: types.InlineKeyboardMarkup
	"""
	Menu = types.InlineKeyboardMarkup()

	energy_exchange = types.InlineKeyboardButton(_("Взять расклад у Мастера 🔥"), callback_data = "send_order_layout")
	mailing_card_day = types.InlineKeyboardButton(_("Благодарю за расклад!"), callback_data = "send_main_menu")

	Menu.add(energy_exchange, mailing_card_day, row_width= 1) 

	return Menu

#==========================================================================================#
# >>>>> DECORATORS <<<<< #
#==========================================================================================#

class Decorators:
	"""
	Набор декораторов
	"""

	def inline_keyboards(self, bot: TeleBot, users: UsersManager, StartAnimation: RealCachedFile):
		"""
		Обработка inline_keyboards.

		:param bot: Telegram bot.
		:type bot: TeleBot
		:param users: Менеджер пользователей.
		:type users: UsersManager
		:param StartAnimation: Данные кэшированной анимации.
		:type StartAnimation: RealCachedFile
		"""

		@bot.callback_query_handler(func = lambda Callback: Callback.data == "send_main_menu")
		def send_main_menu(Call: types.CallbackQuery):
			User = users.auth(Call.from_user)
			bot.answer_callback_query(Call.id)
			bot.send_animation(
				Call.message.chat.id,
				animation = StartAnimation.file_id,
				caption = None,
				parse_mode = "HTML",
				reply_markup = InlineKeyboards.main_menu()
				)
			
		@bot.callback_query_handler(func = lambda Callback: Callback.data == "send_order_layout")
		def send_order_layout(Call: types.CallbackQuery):
			User = users.auth(Call.from_user)
			bot.answer_callback_query(Call.id)
			bot.send_animation(
				chat_id = Call.message.chat.id,
				animation = StartAnimation.file_id,
				caption = "<b>" + _("РАСКЛАД ОТ МАСТЕРА") + "</b>",
				parse_mode = "HTML",
				reply_markup = InlineKeyboards.SendOrderLayout()
				)
			
class Layout:
	"""
	Расклад от языковой модели
	"""

	@property
	def decorators(self) -> Decorators:
		"""Наборы декораторов."""

		return self.__Decorators

	def __init__(self):
		"""Панель управления."""

		#---> Генерация динамических атрибутов.
		#==========================================================================================#
		self.__Decorators = Decorators()