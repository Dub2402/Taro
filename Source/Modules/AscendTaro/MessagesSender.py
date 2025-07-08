from dublib.TelebotUtils.Cache import TeleCache
from dublib.Methods.Filesystem import ListDir
from dublib.Engine.GetText import _

from telebot import TeleBot, types

import logging
import random


def start_appeals() -> types.InlineKeyboardMarkup:
		"""
		Строит Inline-интерфейс:
			Поделиться
			В другой раз!

		:return: inline-keyboard
		:rtype: types.InlineKeyboardMarkup
		"""

		Menu = types.InlineKeyboardMarkup()

		for_delete = types.InlineKeyboardButton(_("Спасибо, друзья уже в курсе!"), callback_data = "for_delete")

		Menu.add(for_delete, row_width = 1) 

		return Menu

class Sender:
	"""Отправитель сообщений."""

	def __init__(self, bot: TeleBot, cacher: TeleCache) -> None:
		"""
		Отправитель сообщений.

		:param bot: Экземпляр Telegram Bot.
		:type bot: TeleBot
		:param cacher: Экземпляр Telegram Bot.
		:type cacher: TeleCache
		"""

		self.__bot = bot
		self.__cacher = cacher

	@property
	def bot(self) -> str:
		"""Telegram Bot"""

		return self.__bot
	
	def __generate_referal_link(self, id: int) -> str:
		"""Реферальная ссылка."""

		return "https://t.me/" + self.__bot.get_me().username + "?start=" + str(id)
	
	def __generate_join_animation(self) -> str:
		"""Генерация анимации при отправке реферальной ссылки."""
		
		animation_paths = list()

		for animation_path in ListDir("Data/AscendTarobot/Materials/Join"):
			animation_paths.append(animation_path)

		animation = random.choice(animation_paths)

		return animation

	def limiter_layouts(self, message: types.Message) -> None:
		"""Отправка сообщения об oграничении онлайн раскладов в этот день."""

		logging.info("Вызван limiter_layouts.")
		
		text = (
				"<b>" + _("Дорогой пользователь") + "!</b>\n",
				_("Вы можете делать 1 Онлайн расклад в день" + "! 🎁" + "Чтобы получить 5 бонусных раскладов - пригласите, пожалуйста, друга присоединиться к нашему Тароботу" + "!\n"),
				"<b>" + _("Вот ваша ссылка приглашение, поделитесь ею:") + "</b>"
				)
		self.__bot.send_animation(
			chat_id = message.chat.id,
			animation = self.__cacher.get_real_cached_file(
				path = "Data/AscendTarobot/Materials/limiter.gif",
				autoupload_type = types.InputMediaAnimation,
				).file_id,
			caption = "\n".join(text), 
			parse_mode = "HTML"
		)

		path = self.__generate_join_animation()

		self.__bot.send_animation(
			chat_id = message.chat.id,
			animation = self.__cacher.get_real_cached_file(
				path = f"Data/AscendTarobot/Materials/Join/{path}",
				autoupload_type = types.InputMediaAnimation,
				).file_id,
			caption = "<b>" + _("Присоединяйся к Тароботу, я уже там:") + "</b>\n\n" + self.__generate_referal_link(message.chat.id),
			parse_mode = "HTML",
			reply_markup = start_appeals()
		)