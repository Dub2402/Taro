from dublib.Engine.GetText import _
from dublib.TelebotUtils.Users import UserData

from Source.InlineKeyboards import InlineKeyboards

from telebot import TeleBot, types

class WorkpiecesMessages:
	"""Набор сообщений для пользователя"""

	def __init__(self, bot: TeleBot):
		"""
		Инициализация.

		:param bot: бот Telegram
		:type bot: TeleBot
		"""

		self.__bot = bot

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

		button = self.__inline_keyboard.for_restart("Спасибо!") if action == "restart" else InlineKeyboards.for_delete("Спасибо!")
		text = _("Хорошо! Вы в любой момент сможете посмотреть <b>Карту дня</b> из главного меню"+ " ⭐️")
		if choice: text = _("Благодарим! Теперь ваше утро будет начинаться с магии карт Таро!" + " 💌")

		self.__bot.edit_message_text(
			chat_id = message.chat.id, 
			text = text,
			message_id = message.id,
			reply_markup = button
		)
