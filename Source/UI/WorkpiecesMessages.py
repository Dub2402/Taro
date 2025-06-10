from dublib.Engine.GetText import _
from dublib.TelebotUtils.Cache import TeleCache
from dublib.TelebotUtils import UsersManager

from Source.InlineKeyboards import InlineKeyboards

from telebot import TeleBot, types

class WorkpiecesMessages:
	"""Набор сообщений для пользователя"""

	def __init__(self, bot: TeleBot, cacher: TeleCache):
		"""
		Инициализация.

		:param bot: бот Telegram
		:type bot: TeleBot
		"""

		self.__bot = bot
		self.__cacher = cacher

	def settings_mailing(self, message: types.Message, action: str):
		"""
		Включение/отключение рассылки "карты дня"

		:param message: данные сообщения; command /mailset или callback: mailing_card_day
		:type message: types.Message
		:param action: тип реакции на кнопку спасибо
		:type action: str
		"""
		
		self.__bot.send_message(message.chat.id, _("Желаете включить/отключить утреннюю рассылку <b>Карты дня</b>?"), parse_mode = "HTML", reply_markup = InlineKeyboards.notifications(action))

	def notification_result(self, message: types.Message, action: str, choice: bool):
		"""
		Сообщение при включении рассылки

		:param message: данные сообщения; command /mailset или callback: mailing_card_day
		:type message: types.Message
		:param action: выполняемое действие, при нажатии кнопки спасибо
		:type action: str
		:param choice: выбор пользователя
		:type choice: bool
		"""

		button = InlineKeyboards.for_restart("Спасибо!") if action == "restart" else InlineKeyboards.for_delete("Спасибо!")
		text = _("Хорошо! Вы в любой момент сможете посмотреть <b>Карту дня</b> из главного меню"+ " ⭐️")
		if choice: text = _("Благодарим! Теперь ваше утро будет начинаться с магии карт Таро!" + " 💌")

		self.__bot.edit_message_text(
			chat_id = message.chat.id, 
			text = text,
			message_id = message.id,
			reply_markup = button,
			parse_mode = "HTML"
		)

	def restart_messages(self, Message: types.Message, user: UsersManager):
		Message = self.__bot.send_message(
			Message.chat.id,
			text = _("<b>Добро пожаловать в Таробот!</b>\n\nСамый большой бот для Таро-гаданий в Telegram!\n\nЗадай боту любой❓️вопрос и наслаждайся ответом!"),
			parse_mode = "HTML"
		)

		Message = self.__bot.send_animation(
			Message.chat.id,
			animation = self.__cacher.get_real_cached_file(
				path = "Start.mp4", autoupload_type = types.InputMediaAnimation
				).file_id,
			caption = None,
			reply_markup = InlineKeyboards.main_menu(),
			parse_mode = "HTML"
		)
		user.set_property("is_chat_forbidden", True, force = True)
		user.set_property("Current_place", None, force = False)
		user.set_property("Card_name", None, force = False)
		user.set_property("Question", None)
		user.set_property("Generation", False)
		user.set_property("Subscription", None, force = False)
		user.clear_temp_properties()
