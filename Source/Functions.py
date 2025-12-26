from Source.TeleBotAdminPanel import Panel, PanelOptions

from typing import TYPE_CHECKING

from telebot import TeleBot, types

if TYPE_CHECKING:
	from dublib.TelebotUtils.Users import UserData

def CloseAdminPanel(bot: TeleBot, panel: Panel, user: "UserData") -> bool:
	"""
	Закрывает панель управления для пользователя.

	:param bot: Бот Telegram.
	:type bot: TeleBot
	:param panel: Панель управления.
	:type panel: Panel
	:param user: Данные пользователя.
	:type user: UserData
	:return: Возвращает `True`, если панель была закрыта.
	:rtype: bool
	"""

	MESSAGE = "Панель управления закрыта."

	Options = PanelOptions(user)
	if not Options.is_open: return False
	panel.close(user)
	bot.send_message(user.id, MESSAGE, reply_markup = types.ReplyKeyboardRemove())

	return True