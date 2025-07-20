from Source.InlineKeyboards import InlineKeyboards

from dublib.TelebotUtils import UserData, UsersManager
from dublib.Methods.Data import ToIterable
from dublib.TelebotUtils.Cache import TeleCache
from dublib.Methods.Filesystem import ListDir
from dublib.Engine.GetText import _

from apscheduler.schedulers.background import BackgroundScheduler
from telebot import TeleBot, types

import logging
from typing import Literal, Any, Iterable
from types import MappingProxyType
import random
from os import PathLike

ParametersDetermination = MappingProxyType(
	{
	"today_layouts": 0,
	"bonus_layouts": 0,
	"invited_users": [],
	"days_with_bot": 0,
	"level_tarobot": 0,
	"promo": None,
	"delete_limiter": []
	}
)

DEFAULT_COUNT_TODAY_LAYOUTS = 0
MIN_COUNT_BONUS_LAYOUTS = 0
DEFAULT_COUNT_DAYS_WITH_BOT = 0
MAX_COUNT_TODAY_LAYOUTS = 1
STANDART_ADDING_COUNT_BONUS_LAYOUTS = 5

class AscendData:
	"""Контейнер бонусных данных пользователя."""

	@property
	def invited_users(self) -> list[int]:
		"""Список id пользователей, выполнивших реферальную программу."""

		return self.__Data["invited_users"]

	@property
	def days_with_bot(self) -> int:
		"""Количество дней с тароботом."""

		return self.__Data["days_with_bot"]
	
	@property
	def level_tarobot(self) -> int:
		"""Уровень таробота."""

		return self.__Data["level_tarobot"]
	
	@property
	def delete_limiter(self) -> list[int]:
		"""Список id сообщений, говорящих об ограничении количества онлайн раскладов и которые необходимо удалить."""

		return self.__Data["delete_limiter"]
	
	@property
	def is_new_level_available(self) -> bool:
		"""Состояние: доступен ли новый уровень таробота."""

		count_days_for_new_level = (3, 7, 14, 30)
		bot_level_requirements = {level + 1: day_requirements for level, day_requirements in enumerate(count_days_for_new_level)}
	
		if self.days_with_bot in count_days_for_new_level:
			
			for level, count_days in bot_level_requirements.items():
				if count_days == self.days_with_bot: return level == self.level_tarobot + 1			 
				
		return False

	@property
	def is_today_layout_available(self):
		"""Состояние: доступен ли бесплатный онлайн расклад."""

		return self.__Data["today_layouts"] < MAX_COUNT_TODAY_LAYOUTS

	@property
	def is_bonus_layout_available(self):
		"""Состояние: доступен ли бонусный онлайн расклад."""

		return self.__Data["bonus_layouts"] > MIN_COUNT_BONUS_LAYOUTS

	@property
	def is_layout_available(self) -> bool:
		"""Состояние: доступен ли онлайн расклад."""

		if self.__User.has_permissions("admin"): return True
		if self.is_bonus_layout_available: return True
		if self.is_today_layout_available: return True
		return False

	@property
	def count_invited_users(self) -> int:
		"""
		Количество приглашённых пользователей.

		:return: Количество приглашённых пользователей.
		:rtype: int
		"""

		return len(self.__Data["invited_users"])

	def __SetParameter(self, key: Literal["today_layouts", "bonus_layouts", "invited_users", "days_with_bot", "level_tarobot", "promo", "delete_limiter"], value: Any):
		"""
		Сохраняет параметры бонусных данных пользователя.

		:param key: Ключ параметра.
		:type key: Literal["today_layouts", "bonus_layouts", "level_user", "invited_users", "days_with_bot", "promo", "delete_limiter"]
		:param value: Значение параметра.
		:type value: Any
		"""

		self.__Data[key] = value
		self.save()

	def __ValidateDate(self) -> dict[str, Any]:
		"""
		Проверяет валидность бонусных данных пользователя.

		:return: Данные пользователя.
		:rtype: dict[str, Any]
		"""
		
		if not self.__User.has_property("ascend"):
			self.__User.set_property("ascend", ParametersDetermination.copy())
			
		else:
			Data: dict = self.__User.get_property("ascend")

			for Key in ParametersDetermination.keys():

				if Key not in Data.keys():
					Data[Key] = ParametersDetermination[Key]
					logging.debug(f"For user #{self.__User.id} key \"{Key}\" set to default.")

			self.__User.set_property("ascend", Data)

		return self.__User.get_property("ascend")

	def __init__(self, user: UserData):
		"""
		Контейнер бонусных данных пользователя.

		:param user: Данные пользователя.
		:type user: UserData
		"""

		self.__User = user
	
		self.__Data = self.__ValidateDate()

	def save(self):
		"""Сохраняет бонусные данные пользователя."""

		self.__User.set_property("ascend", self.__Data)

	def set_today_layouts(self, count: int = DEFAULT_COUNT_TODAY_LAYOUTS):
		"""
		Передаёт параметры для сохранения бонусных данных пользователя.

		:param count: Количество бесплатных онлайн раскладов.
		:type count: int
		"""

		self.__SetParameter("today_layouts", count)

	def set_days_with_bot(self, count: int = DEFAULT_COUNT_DAYS_WITH_BOT):
		"""
		Передаёт параметры для сохранения бонусных данных пользователя.

		:param count: Количество бесплатных онлайн раскладов.
		:type count: int
		"""

		self.__SetParameter("days_with_bot", count)

	def add_invited_user(self, user_id: int):
		"""
		Добавляет id пользователя, которые выполнили условия реферальной программы, по ссылке пользователя.

		:param user_id:  id пользователя.
		:type user_id: int
		"""

		UsersID = self.invited_users
		if user_id in UsersID: return
		UsersID.append(user_id)
		self.__SetParameter("invited_users", UsersID)

	def add_delete_limiter(self, message_id: Iterable[int] | int):
		"""
		Добавляет id сообщений, которые необходимо удалить и говорящие об ограничении использования онлайн раскладов.

		:param message_id: Сообщения об ограничении использования онлайн раскладов.
		:type message_id: Iterable[int] | int
		"""

		MessagesID = self.delete_limiter 
		MessagesID.extend(ToIterable(message_id))
		self.__SetParameter("delete_limiter", MessagesID)

	def incremente_today_layouts(self):
		"""Увеличивает количество использованных бесплатных онлайн раскладов."""

		self.__Data["today_layouts"] = self.__Data["today_layouts"] + 1
		self.save()
	
	def incremente_days_with_bot(self):
		"""Увеличивает количество дней с ботом."""

		self.__Data["days_with_bot"] = self.__Data["days_with_bot"] + 1
		self.save()

	def decremente_bonus_layouts(self):
		"""Уменьшает количество использованных бонусных онлайн раскладов."""

		self.__Data["bonus_layouts"] = self.__Data["bonus_layouts"] - 1
		self.save()

	def add_bonus_layouts(self, count: int = STANDART_ADDING_COUNT_BONUS_LAYOUTS):
		"""
		Увеличивает количество бонусных раскладов.

		:param count: Добавляемое количество бонусных раскладов, defaults to 5
		:type count: int, optional
		"""

		self.__Data["bonus_layouts"] = self.__Data["bonus_layouts"] + count
		self.save()

class Scheduler:
	"""Обновляет бонусные данные пользователей."""

	def __load_tasks(self):
		"""Загружает задачи в фоновое хранилище."""

		self.__sheduler.add_job(self.__zeroing_today_layours, "cron", hour = 0, minute = 0)
		self.__sheduler.add_job(self.__tracking_activity, "cron", hour = 12, minute = 34)

	def __zeroing_today_layours(self):
		for user in self.__usermanager.users:
			AscendData(user = user).set_today_layouts()

	def __init__(self, usermanager: UsersManager, scheduler: BackgroundScheduler):
		"""Обновляет бонусные данные пользователей."""

		self.__usermanager = usermanager

		self.__sheduler = scheduler or BackgroundScheduler()

		self.__load_tasks()

	def __tracking_activity(self):
		"""Добавляет один день в активность, тем пользователям, кто использовал бота за последние 24 часа."""

		for user in self.__usermanager.users:
			if user in self.__usermanager.active_users: AscendData(user = user).incremente_days_with_bot()
			else: AscendData(user = user).set_days_with_bot()
		
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
			reply_markup = InlineKeyboards.for_delete(_("Спасибо, друзья уже в курсе!"))
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
			reply_markup = InlineKeyboards.for_delete(_("Спасибо! Приятно!"))
		)

	def end_bonus_layout(self, user_id: int):
		"""
		Оповещает пользователя о конце бонусных раскладов.

		:param user_id: ID пользователя.
		:type user_id: int
		"""

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

	def level_up(self, user_id: int, level: int) -> None:
		
		greeting_cards = {
			1: ["3-х дней", "3", "неделя с Тароботом!"],
			2: ["всей недели", "7", "2 недели с Тароботом!"],
			3: ["целых 2-х недель", "14", "месяц с Тароботом!"],
			4: ["аж целого месяца", "30", "пригласи 10 друзей!"]
		}
		print(level)
		if level < 5:
			card = greeting_cards[level]

			text = (
				"<b>" + _(f"Поздравляем!!! Вы были активны на протяжении $day_with_bot!") + "</b>" + "\n",
				"🏆" + " " + _("У вас $number-й уровень! Вы получаете бонус: $bonus дополнительных Онлайн расклада!") + "\n",
				"<b>" + _("Следующий уровень - $requirements_next_level") + "</b>"
				)
			
			self.__bot.send_message(
				chat_id = user_id,
				text = "\n".join(text).replace("$day_with_bot", card[0]).replace("$number", str(level)).replace("$bonus", card[1]).replace("$requirements_next_level", card[2]), 
				parse_mode = "HTML",
				reply_markup = InlineKeyboards.for_delete("Вау! Невероятно!")
			)






