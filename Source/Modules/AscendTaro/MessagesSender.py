from dublib.TelebotUtils.Cache import TeleCache
from dublib.Methods.Filesystem import ListDir
from dublib.Engine.GetText import _

from telebot import TeleBot, types

import logging
import random
from os import PathLike

class InlineTemplates:
	"""Inline-keyboards для модуля AscendTaro"""

	def delete_message(text: str) -> types.InlineKeyboardMarkup:
		"""
		Строит Inline-интерфейс.

		:param text: Текст кноппки.
		:type text: str
		:return: inline-keyboard
		:rtype: types.InlineKeyboardMarkup
		"""

		Menu = types.InlineKeyboardMarkup()

		for_delete = types.InlineKeyboardButton(text, callback_data = "for_delete")

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
	
	def __randomize_animation(self, path_to_animations: PathLike) -> str:
		"""
		Выбирает рандомную анимацию из необходимой папки.

		:param path_to_animations: Путь к папке с гифками.
		:type path_to_animations: PathLike
		:return: Название рандомной гифки.
		:rtype: str
		"""
		
		animation_paths = list()

		for animation_path in ListDir(path_to_animations):
			animation_paths.append(animation_path)

		name_animation = random.choice(animation_paths)

		return name_animation
	
	def __message_with_referal(self, chat_id: types.Message, text: str) -> None:
		name_animation = self.__randomize_animation("Data/AscendTarobot/Materials/Join")

		self.__bot.send_animation(
			chat_id = chat_id,
			animation = self.__cacher.get_real_cached_file(
				path = f"Data/AscendTarobot/Materials/Join/{name_animation}",
				autoupload_type = types.InputMediaAnimation,
				).file_id,
			caption = "<b>" + _("Присоединяйся к Тароботу, я уже там:") + "</b>\n\n" + self.generate_referal_link(id = chat_id),
			parse_mode = "HTML",
			reply_markup = InlineTemplates.delete_message(_("Спасибо, друзья уже в курсе!"))
		)

	def generate_referal_link(self, id: int) -> str:
		"""Реферальная ссылка."""

		return "https://t.me/" + self.__bot.get_me().username + "?start=" + str(id)

	def limiter_layouts(self, chat_id: types.Message) -> None:
		"""Отправка сообщения об oграничении онлайн раскладов в этот день."""

		logging.info("Вызван limiter_layouts.")
		
		text = (
				"<b>" + _("Дорогой пользователь") + "!</b>\n",
				_("Вы можете делать 1 Онлайн расклад в день" + "! 🎁" + " " + "Чтобы получить 5 бонусных раскладов - пригласите, пожалуйста, друга присоединиться к нашему Тароботу" + "!\n"),
				"<b>" + _("Вот ваша ссылка приглашение, поделитесь ею:") + "</b>"
				)
		
		self.__bot.send_animation(
			chat_id = chat_id,
			animation = self.__cacher.get_real_cached_file(
				path = "Data/AscendTarobot/Materials/limiter.gif",
				autoupload_type = types.InputMediaAnimation,
				).file_id,
			caption = "\n".join(text), 
			parse_mode = "HTML"
		)
		self.__message_with_referal(chat_id = chat_id, text = "<b>" + _("Присоединяйся к Тароботу, я уже там:") + "</b>\n\n")
		
	def worked_referal(self, user_id: int) -> None:
		text = (
				"<b>" + _("Поздравляем!!! От вас пришел новый пользователь!") + "</b>\n",
				"🌟" + _("Вы получили за это бонус:"),
				_("5 дополнительных Онлайн раскладов!") + "\n",
				"<b>" + _("Спасибо за совместное развитие Таробота!") + "</b>"
				)
		
		self.__bot.send_animation(
			chat_id = user_id,
			animation = self.__cacher.get_real_cached_file(
				path = "Data/AscendTarobot/Materials/level_up.gif",
				autoupload_type = types.InputMediaAnimation,
				).file_id,
			caption = "\n".join(text), 
			parse_mode = "HTML",
			reply_markup = InlineTemplates.delete_message(_("Спасибо! Приятно!"))
		)

	def end_bonus_layout(self, user_id):
		text = (
				"<b>" + _("Дорогой пользователь!") + " " + "🤗" + "</b>" + "\n",
				_("Ваш лимит бонусных Онлайн раскладов подошел к концу!") + "\n",
				_("Пожалуйста, попробуйте ещё раз завтра или пригласите друга!") + "\n",
				"<b>" + _("Вот ваша ссылка приглашение:") + "</b>"
				)
		
		self.__bot.send_message(
			chat_id = user_id,
			text = "\n".join(text), 
			parse_mode = "HTML"
		)

		self.__message_with_referal(chat_id = user_id, text = "<b>" + _("Присоединяйся к Тароботу, я уже там:") + "</b>\n\n")