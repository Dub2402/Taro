from dublib.Engine.GetText import _
from dublib.TelebotUtils.Users import UsersManager
from dublib.TelebotUtils import TeleMaster
from dublib.TelebotUtils.Cache import RealCachedFile

from Source.InlineKeyboards import InlineKeyboards
from Source.Modules.Subscription import Subscription

import random

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
	"""Набор декораторов."""

	def __init__(self, layout: "Layout"):
		self.__Layout = layout

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
			user = users.auth(Call.from_user)
			if not self.__Layout.subscription.IsSubscripted(user):
				bot.answer_callback_query(Call.id)
				return
			bot.send_message(
				chat_id = Call.message.chat.id,
				text = self.__Layout.end_phrases()
			)
			bot.send_animation(
				Call.message.chat.id,
				animation = StartAnimation.file_id,
				caption = None,
				parse_mode = "HTML",
				reply_markup = InlineKeyboards.main_menu(user)
				)
			bot.answer_callback_query(Call.id)
			
		@bot.callback_query_handler(func = lambda Callback: Callback.data == "send_order_layout")
		def send_order_layout(Call: types.CallbackQuery):
			User = users.auth(Call.from_user)
			if not self.__Layout.subscription.IsSubscripted(User):
				bot.answer_callback_query(Call.id)
				return
			bot.send_animation(
				chat_id = Call.message.chat.id,
				animation = StartAnimation.file_id,
				caption = "<b>" + _("РАСКЛАД У МАСТЕРА") + "</b>",
				parse_mode = "HTML",
				reply_markup = InlineKeyboards.SendOrderLayout()
				)
			bot.answer_callback_query(Call.id)
			
class Layout:
	"""Расклад от языковой модели."""

	@property
	def decorators(self) -> Decorators:
		"""Наборы декораторов."""

		return self.__Decorators
	
	@property
	def subscription(self) -> Subscription:
		"""Проверка подписки."""

		return self.__subscription

	def __init__(self, subscription: Subscription):
		"""Панель управления."""

		#---> Генерация динамических атрибутов.
		#==========================================================================================#

		self.__Decorators = Decorators(self)
		self.__subscription = subscription

	def end_phrases(self) -> str:
		"""
		Выбирает текст фразы в конце расклада.

		:return: Текст фразы.
		:rtype: str
		"""

		texts = [
			"Во благо!\nХорошего вам дня!)",
			"На здоровье!\nБудем рады вам сделать ещё расклад!)",
			"Всегда рады помочь!\nВы наш самый ценный пользователь!",
		   	"Всегда пожалуйста!\nЗадавайте любые вопросы и в любое время!)",
			"Вам спасибо!\nМы очень рады, что вы с нами!",
			"Рады быть полезными!\nКогда вы счастливы - мы ещё счастливее!)",
			"Мы рады, что вам понравилось!\nС удовольствием разложим карты снова!)",
			"Это мы благодарим за ваш вопрос!)\nОбращайтесь!",
			"Мы всегда рядом!\nУ вас довольно интересные вопросы!)",
			"Приятно с вами иметь дело!\nИ запросы у вас необычные!)"
		]
		text = random.choice(texts)

		return text