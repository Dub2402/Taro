from dublib.Engine.GetText import _

from Source.InlineKeyboards import InlineKeyboards

from telebot import TeleBot, types

def send_settings_mailing(bot: TeleBot, message: types.Message, inline_keyboard: InlineKeyboards, action: str):
	"""
	Подтверждение/отклонение рассылки "карты дня"

	:param bot: объект класса
	:type bot: TeleBot
	:param message: объект класса; command /mailset или callback: mailing_card_day
	:type message: types.Message
	:param inline_keyboard: объект класса
	:type inline_keyboard: InlineKeyboards
	"""
	bot.send_message(message.chat.id, _("Желаете включить/отключить утреннюю рассылку <b>Карты дня</b>?"), parse_mode = "HTML", reply_markup = inline_keyboard.notifications(action))