from Source.InlineKeyboards import InlineKeyboards as MainInlineKeyboards

from dublib.TelebotUtils import UserData, UsersManager
from dublib.Methods.Filesystem import GetRandomFile
from dublib.TelebotUtils.Cache import TeleCache
from dublib.Methods.Filesystem import ReadJSON, WriteJSON
from dublib.Methods.Filesystem import ListDir
from dublib.Methods.Data import ToIterable
from dublib.Engine.GetText import _
from dublib.TelebotUtils.Master import TeleMaster

from apscheduler.schedulers.background import BackgroundScheduler
from telebot import TeleBot, types

from typing import Literal, Any, Iterable, TYPE_CHECKING
from types import MappingProxyType
from os import PathLike
import logging
import random
import os

if TYPE_CHECKING:
	from Source.Modules.Subscription import Subscription

AscendParameters = MappingProxyType(
	{
	"today_layouts": 0,
	"is_notification_bonus_send": False,
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
DEFAULT_LEVEL_TAROBOT = 0
MAX_COUNT_TODAY_LAYOUTS = 1
STANDART_ADDING_COUNT_BONUS_LAYOUTS = 5
NECESSARY_INVITED_USERS = 10

ADDITIONAL_BONUS_LAYOUT_DEPENDING_ON_LEVEL = {
	1: 3,
	2: 7,
	3: 14,
	4: 30,
	5: 55
}

PATH_TO_ANIMATION_LEVEL_UP = "Data/AscendTarobot/Materials/Level_Up"
PATH_TO_USED_PROMOCODES = "Data/AscendTarobot/Promocodes.json"

class ManagerPromoCodes:
	"""Менеджер промокодов."""
	
	@property
	def used_promocodes(self) -> set[str]:
		"""Множество выданных промокодов."""

		return self.__Promocodes.keys()
	
	def __generate_promocode(self, length_promo: int = 5) -> str:
		"""
		Генерирует промокод, длиной в 5 символов, исключая некоторые буквы(I, O) и цифры(0).

		:param length_promo: Длина промокода, defaults to 5
		:type length_promo: int, optional
		:return: Промокод.
		:rtype: str
		"""

		promocode = ""

		choices = random.choices(population = ("letter", "number"), k = length_promo)

		for choice in choices:
			if choice == "letter": promocode += random.choice("ABCDEFGHJKLMNPQRSTUVWXYZ")
			else: promocode += random.choice("123456789")

		return promocode
	
	def __is_unique(self, promocode: str) -> bool:
		"""
		Проверяет является ли промокод уникальным.

		:param promocode: Промокод.
		:type promocode: str
		:return: Статус: уникален ли промокод.
		:rtype: bool
		"""

		for used_promocode in self.used_promocodes: 
			if promocode == used_promocode: return False

		return True
	
	def __init__(self):
		"""Подготовка к работе менеджера промокодов."""

		self.__Path = "Data/AscendTarobot/Promocodes.json"
		self.__Promocodes = dict()

		if os.path.exists(self.__Path): self.__Promocodes = ReadJSON(self.__Path)

	def get_new_promo(self) -> str:
		"""
		Получаем новый, нигде не задействованный промокод.

		:return: Промокод, который выдадем пользователю.
		:rtype: str
		"""

		new_promocode = self.__generate_promocode()

		while True: 

			if not self.__is_unique(promocode = new_promocode): pass
			else: return new_promocode

	def save(self, promocode: str, user_id: int): 

		self.__Promocodes[promocode] = {"user_id": user_id}
		WriteJSON(self.__Path, self.__Promocodes)

class AscendData:
	"""Контейнер бонусных данных пользователя."""

	@property
	def is_notification_bonus_send(self) -> bool:
		"""Присылалось ли уведомление, о том, что пользователь за каждого приглашённого друга получает 5 бонусных раскладов."""

		return self.__Data["is_notification_bonus_send"]

	@property
	def bonus_layouts(self) -> int:
		"""Количество бонусных раскладов."""

		return self.__Data["bonus_layouts"]

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
	def promo(self) -> int:
		"""Промокод пользователя."""

		return self.__Data["promo"]
	
	@property
	def delete_limiter(self) -> list[int]:
		"""Список id сообщений, говорящих об ограничении количества онлайн раскладов и которые необходимо удалить."""

		return self.__Data["delete_limiter"]
	
	@property
	def is_available_time_based_level_up(self) -> bool:
		"""Состояние: доступен ли новый уровень таробота, основанный на количестве дней подряд, в которые пользователь использовал бота."""

		count_days_for_new_level = (3, 7, 14, 30)
		bot_level_requirements = {level + 1: day_requirements for level, day_requirements in enumerate(count_days_for_new_level)}
	
		if self.days_with_bot in count_days_for_new_level:
			
			for level, count_days in bot_level_requirements.items():
				if count_days == self.days_with_bot: return level == self.level_tarobot + 1			 
				
		return False
	
	@property
	def is_available_user_based_level_up(self) -> bool:
		"""Состояние: доступен ли новый уровень таробота, основанный на количестве пользователей, перешедших по реферальной ссылке пользователя."""

		return len(self.invited_users) == NECESSARY_INVITED_USERS

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
	
	@property
	def users_need_to_invited(self) -> int:
		"""
		Количество пользователей, которых надо пригласить для того чтобы получить 5 уровень.

		:return: Количество пользователей, которых надо пригласить.
		:rtype: int
		"""

		count_users_need_to_invited = NECESSARY_INVITED_USERS - self.count_invited_users 
		if count_users_need_to_invited < 0: count_users_need_to_invited = 0

		return count_users_need_to_invited

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
			self.__User.set_property("ascend", AscendParameters.copy())
			
		else:
			Data: dict = self.__User.get_property("ascend")

			for Key in AscendParameters.keys():

				if Key not in Data.keys():
					Data[Key] = AscendParameters[Key]
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

	def set_is_notification_bonus_send(self, status: bool = True):
		"""
		Передаёт параметры для сохранения бонусных данных пользователя.

		:param status: Присылалось ли уведомление, о том, что пользователь за каждого приглашённого друга получает 5 бонусных раскладов.
		:type status: bool
		"""

		self.__SetParameter("is_notification_bonus_send", status)

	def set_days_with_bot(self, count: int = DEFAULT_COUNT_DAYS_WITH_BOT):
		"""
		Передаёт параметры для сохранения бонусных данных пользователя.

		:param count: Количество дней с ботом.
		:type count: int
		"""

		self.__SetParameter("days_with_bot", count)

	def set_level_tarobot(self, count: int = DEFAULT_LEVEL_TAROBOT) -> int:
		"""
		Передаёт параметры для сохранения бонусных данных пользователя.

		:param count: Уровень таробота.
		:type count: int
		:return: Текущий уровень таробота.
		:rtype: int
		"""

		self.__SetParameter("level_tarobot", count)

		return self.level_tarobot

	def set_level_up_rewards(self, level: int, manager_promocode: ManagerPromoCodes): 
		"""
		Добавляет бонусы за уровень пользователю.

		:param count: Текущий уровень таробота.
		:type count: int, optional
		"""

		count_bonus_layouts = self.bonus_layouts + ADDITIONAL_BONUS_LAYOUT_DEPENDING_ON_LEVEL[level]

		if level == 5: 
			if not self.promo:

				promocode = manager_promocode.get_new_promo()
				self.__SetParameter("promo", promocode)
				manager_promocode.save(promocode = promocode, user_id = self.__User.id)

		self.__SetParameter("bonus_layouts", count_bonus_layouts)

	def add_bonus_layouts(self, count : int = STANDART_ADDING_COUNT_BONUS_LAYOUTS):
		"""
		Добавляет бонусные расклады пользователю.

		:param count: Количество добавляемых бонусных раскладов, defaults to STANDART_ADDING_COUNT_BONUS_LAYOUTS
		:type count: int, optional
		"""

		count_bonus_layouts = self.bonus_layouts + count
		self.__SetParameter("bonus_layouts", count_bonus_layouts)

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

	def zeroing_delete_limiter(self):
		"""Обнуление ID сообщений, которые удаляют сообщения, лимитирующие онлайн-рассклад."""

		self.__SetParameter("delete_limiter", [])

class Scheduler:
	"""Планировщик изменений бонусных данных пользователей."""

	def __load_tasks(self):
		"""Загружает задачи в фоновое хранилище."""

		self.__ascend.scheduler.add_job(self.__zeroing_today_layours, "cron", hour = 0, minute = 0)
		self.__ascend.scheduler.add_job(self.__tracking_activity, "cron", hour = 0, minute = 0)

	def __zeroing_today_layours(self):
		"""Приводит значение сегодняшних раскладов к стандартному значению."""

		for user in self.__ascend.users.users: AscendData(user = user).set_today_layouts()

	def __init__(self, ascend: "MainAscend"):
		"""Подготавливает планировщик задач к работе."""

		self.__ascend = ascend

		self.__load_tasks()

	def __tracking_activity(self):
		"""Изменяет значение количества дней подряд проведённых с тароботом, а также обновляет значение уровня таробота, если количество дней сбросилось до нуля."""

		for user in self.__ascend.users.users:

			if user in self.__ascend.users.active_users: AscendData(user = user).incremente_days_with_bot()

			else: 
				ascend_data = AscendData(user = user)
				ascend_data.set_days_with_bot()
		
class InlineKeyboards:
	"""Набор Inline Keyboards"""

	def delete_message_limiter(text: str) -> types.InlineKeyboardMarkup:
		"""
		Inline-keyboard.

		:param text: Текст кнопки.
		:type text: str
		:return: Inline-keyboard.
		:rtype: types.InlineKeyboardMarkup
		"""

		return types.InlineKeyboardMarkup([[types.InlineKeyboardButton(text = text, callback_data = "delete_message_limiter")]])

	def requirements_for_5_level() -> types.InlineKeyboardMarkup:
		"""
		Возвращает клавиатуру, при нажатии на кнопку которой отправляются требования для перехода на 5-ый уровень.

		:return: Inline Keyboard.
		:rtype: types.InlineKeyboardMarkup
		"""

		return types.InlineKeyboardMarkup([[types.InlineKeyboardButton(text = "Узнать подробнее!", callback_data = "requirements_for_5_level")]])
	
	def reaching_5_level(name_buttons: tuple[str])-> types.InlineKeyboardMarkup:
		"""
		Возвращает клавиатуру, в зависимости от нажатой кнопки или удаляется сообщение или пользователь переходит в чат с экспертом.

		:param name_buttons: Названия кнопок. Первый элемент - чат с экспертом. Второй - удаление.
		:type name_buttons: tuple[str] | None
		:return: Inline Keyboard.
		:rtype: types.InlineKeyboardMarkup
		"""
		
		menu = types.InlineKeyboardMarkup()

		determinations = {
			name_buttons[0]: "https://t.me/m/k70ODNf4ZGEy",
			name_buttons[1]: "for_delete"
		}

		for string in determinations.keys(): 
			if determinations[string].startswith("https:"): menu.add(types.InlineKeyboardButton(string, url = determinations[string]), row_width = 1)
			else: menu.add(types.InlineKeyboardButton(string, callback_data = determinations[string]), row_width = 1)

		return menu

class Decorators:
	"""Набор декораторов."""

	def __init__(self, ascend: "MainAscend"):
		self.__ascend = ascend
		
	def inline_keyboards(self):
		"""
		Обработка inline_keyboards.
		"""

		@self.__ascend.bot.callback_query_handler(func = lambda Callback: Callback.data == "requirements_for_5_level")
		def requirements_for_5_level(Call: types.CallbackQuery):
			user = self.__ascend.users.auth(Call.from_user)
			if not self.__ascend.subscription.IsSubscripted(user): 
				self.__ascend.bot.answer_callback_query(Call.id)
				return
			
			text = (
				"<b>" + _("Чтобы достичь 5-й уровень " + "🏆,") + "</b>",
				_("вам необходимо пригласить 10 друзей присоединится к Тароботу, используя вот эту ссылку:") + "\n",
				Sender(self.__ascend.bot, self.__ascend.cacher).generate_referal_link(id = Call.message.chat.id) + "\n", 
				_("Эту ссылку вы можете в любой момент еще раз увидеть, нажав на \"Мой уровень Таробота\", в разделе \"Доп. опции\"") + "\n",
				"<b><i>" + _("Пользователь вам зачтется тогда, когда начнет использовать функционал бота!") + "</i></b>"
				)

			self.__ascend.bot.send_message(
				chat_id = Call.message.chat.id,
				text = "\n".join(text),
				parse_mode = "HTML",
				reply_markup = MainInlineKeyboards.for_delete("Спасибо, я все понял!")
				)
			
			self.__ascend.bot.answer_callback_query(Call.id)

		@self.__ascend.bot.callback_query_handler(func = lambda Callback: Callback.data == "delete_message_limiter")
		def requirements_for_5_level(Call: types.CallbackQuery):
			user = self.__ascend.users.auth(Call.from_user)
			if not self.__ascend.subscription.IsSubscripted(user): 
				self.__ascend.bot.answer_callback_query(Call.id)
				return
			
			TeleMaster(self.__ascend.bot).safely_delete_messages(chat_id = user.id, messages = AscendData(user = user).delete_limiter, complex = True)
			AscendData(user = user).zeroing_delete_limiter()
			self.__ascend.bot.answer_callback_query(Call.id)

class Sender:
	"""Отправитель сообщений."""

	@property
	def bot(self):
		"""Telegram bot."""

		return self.__bot
	
	@property
	def cacher(self):
		"""Менеджер кэша."""

		return self.__cacher

	def __init__(self, bot: TeleBot, cacher: TeleCache):
		"""Подготавливает отправителя задач к работе."""

		self.__bot = bot
		self.__cacher = cacher
	
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
	
	def __message_with_referal(self, chat_id: types.Message) -> int:
		"""
		Отправляет сообщение с реферальной ссылкой.

		:param chat_id: ID Telegram чата.
		:type chat_id: types.Message
		:return: ID сообщения Telegram.
		:rtype: int
		"""

		name_animation = self.__randomize_animation("Data/AscendTarobot/Materials/Join")

		message_with_referal = self.bot.send_animation(
			chat_id = chat_id,
			animation = self.cacher.get_real_cached_file(
				path = f"Data/AscendTarobot/Materials/Join/{name_animation}",
				autoupload_type = types.InputMediaAnimation,
				).file_id,
			caption = "<b>" + _("Присоединяйся к Тароботу, я уже там") +  " 😉!" + "</b>\n\n" + self.generate_referal_link(id = chat_id),
			parse_mode = "HTML",
			reply_markup = InlineKeyboards.delete_message_limiter(_("Спасибо!"))
		)

		return message_with_referal.id

	def generate_referal_link(self, id: int) -> str:
		"""Генерирует реферальную ссылку."""

		return "https://t.me/" + self.bot.get_me().username + "?start=" + str(id)

	def limiter_layouts(self, chat_id: types.Message) -> types.Message:
		"""Отправляет сообщение об oграничении онлайн раскладов в этот день."""

		messages = list()
		
		text = (
				"<b><i>" + _("Дорогой пользователь") + "!</i></b>\n",
				_("Вы можете делать 1 Онлайн расклад в день" + "! 🎁" + " " + "Чтобы получить 5 бонусных раскладов - пригласите, пожалуйста, друга присоединиться к нашему Тароботу" + "!\n"),
				"<b><i>" + _("Вот ваш пост-приглашение, поделитесь им с друзьями:") + "</i></b>"
				)
		
		message_limiter = self.__bot.send_message(
			chat_id = chat_id,
			text = "\n".join(text), 
			parse_mode = "HTML"
		)
		messages.append(message_limiter.id)

		message_with_referal = self.__message_with_referal(chat_id = chat_id)

		messages.append(message_with_referal)

		return messages
		
	def worked_referal(self, user_id: int):
		"""
		Отправляет сообщение о том, что по реферальной ссылке перешли и воспользовались функционалом бота.

		:param user_id: ID пользователя.
		:type user_id: int
		"""

		text = (
				"<b>" + _("Поздравляем!!! От вас пришел новый пользователь!") + "</b>\n",
				"🌟 " + _("Вы получаете бонус:"),
				_("5 дополнительных Онлайн раскладов!") + "\n",
				"<b><i>" + _("Спасибо за совместное развитие Таробота!") + "</i></b>"
				)
		
		path_animation = GetRandomFile(directory = PATH_TO_ANIMATION_LEVEL_UP)
		
		self.bot.send_animation(
			chat_id = user_id,
			animation = self.cacher.get_real_cached_file(
				path = path_animation,
				autoupload_type = types.InputMediaAnimation,
				).file_id,
			caption = "\n".join(text), 
			parse_mode = "HTML",
			reply_markup = MainInlineKeyboards.for_delete(_("Отлично!"))
		)

	def end_bonus_layout(self, user_id: int):
		"""
		Оповещает пользователя о конце бонусных раскладов.

		:param user_id: ID пользователя.
		:type user_id: int
		"""
		messages = list()

		text = (
				"<b><i>" + _("Дорогой пользователь!") + " 🤗</i></b>\n",
				_("Ваш лимит бонусных Онлайн раскладов подошел к концу!") + "\n",
				_("Пожалуйста, попробуйте ещё раз завтра или пригласите друга!") + "\n",
				"<b><i>" + _("Вот ваша ссылка приглашение, просто перешлите пост!)") + "</i></b>"
				)
		
		message_limiter = self.bot.send_message(
			chat_id = user_id,
			text = "\n".join(text), 
			parse_mode = "HTML"
		)

		messages.append(message_limiter.id)

		message_with_referal = self.__message_with_referal(chat_id = user_id)

		messages.append(message_with_referal)

		return messages

	def level_up(self, user: UserData, level: int)-> bool:
		"""
		Отправляет сообщение о том, что уровень таробота повысился за счёт количества дней подряд проведённых пользователем в тароботе.

		:param user: Данные пользователя.
		:type user: UserData
		:param level: Уровень таробота, на который перешёл поьзователь.
		:type level: int
		:return: Состояние: отправлено ли сообщение.
		:rtype: bool
		"""

		greeting_cards = {
				1: (_("3-х дней"), _("расклада"), _("неделя с Тароботом!")),
				2: (_("всей недели"), _("раскладов"), _("2 недели с Тароботом!")),
				3: (_("целых 2-х недель"), _("раскладов"), _("месяц с Тароботом!")),
				4: (_("аж целого месяца"), _("раскладов"), _("пригласи 10 друзей!")),
				5: ("", "")
			}

		card = greeting_cards[level]

		if level != 5: 

			reply_markup = MainInlineKeyboards.for_delete("Супер!") if level < 4 else InlineKeyboards.requirements_for_5_level()

			text = (
				"<b>" + _("Поздравляем!!! Вы были активны на протяжении $day_with_bot!") + "</b>\n",
				"🏆 " + _("У вас $number-й уровень! Вы получаете бонус: $bonus дополнительных Онлайн $layout!") + "\n",
				"<b><i>" + _("Следующий уровень - $requirements_next_level") + "</i></b>"
				)
		
		else:

			reply_markup = InlineKeyboards.reaching_5_level(("Написать эксперту сейчас!", "Спасибо, я напишу позже!"))
			text = (
				"<b>" + _("Поздравляем!!! Вы успешно пригласили в Таробот 10 своих друзей!") + "</b>\n",
				"🏆 " + _("У вас 5-й уровень! Вы получаете бонус: $bonus дополнительных Онлайн раскладов и 1 бесплатный расклад от Таро мастера!") + "\n",
				_("Ваш промокод: <b><code>$promocode</code></b><b>!</b> 👈 нажмите, чтобы скопировать") + "\n",
				"<i>" + _("Промокод вы также можете в любой момент посмотреть, нажав на \"Мой уровень Таробота\", в разделе \"Доп. опции\"") + "</i>\n",
				"<b><i>" + _("Чтобы получить расклад, напишите нашему эксперту и отправьте ей этот промокод!") + "</i></b>"
				)
			
		text = "\n".join(text)

		Replaces = {
			"$day_with_bot": card[0],
			"$number": str(level),
			"$bonus": str(ADDITIONAL_BONUS_LAYOUT_DEPENDING_ON_LEVEL[level]),
			"$layout": card[1],
			"$requirements_next_level": card[2],
			"$promocode": str(AscendData(user = user).promo)
		}

		for Substring in Replaces.keys(): text = text.replace(Substring, Replaces[Substring])
		
		path_animation = GetRandomFile(directory = PATH_TO_ANIMATION_LEVEL_UP)
	
		self.bot.send_animation(
			chat_id = user.id,
			animation = self.cacher.get_real_cached_file(
				path = path_animation,
				autoupload_type = types.InputMediaAnimation,
				).file_id,
			caption = text, 
			parse_mode = "HTML",
			reply_markup = reply_markup
		)

		return True
	
	def level_tarobot(self, user: UserData, level: int, bonus_layouts: int):
		
		requirements_action = ""

		tarobot_status = {
			0: _("3-х дней подряд"),
			1: _("1 недели"),
			2: _("2-х недель"),
			3: _("1 месяца"),
			4: _("пригласить в Таробот 10 своих друзей"),
			5: ""
		}

		requirements_action = " заходить в Таробот на протяжении" if level < 4 else ""

		if level != 0: 
			name_level = "У вас $level-й уровень!"
			comment = ""
		else: 
			name_level = _("Ваш уровень - новичок!")
			comment = "<i>" + _("Но вы уже удачно пустили сюда свои корни!)") + "</i>\n\n"

		if level == 4: referal_link = " Вот ваша пригласительная ссылка:\n\n$referal_link"
		else: referal_link = ""

		common_text = "<b>🌟 " + _("Бонусных Онлайн раскладов: " + "<u>" + "$bonus_layouts" + "</u>") + "</b>\n\n"
	
		low_level_text = (
			"<b>" + _("Задание: ") + "</b>" + _("Чтобы достичь $next_level-го уровня, вы должны$requirements_action $requirements") + referal_link + "\n",
			"<i>" +_("Повышайте свой уровень и гарантированно получайте призы!!") + " 🎁" + "</i>"
			)
		
		high_level_text = (
			_("Ваш промокод на подарочный Таро расклад от нашего Мастера:") + "\n\n" + "<b><code>$promocode</code></b><b>!</b>\n",
			"☝️" + _("Нажмите, чтобы скопировать! Вы его можете использовать только 1 раз!" + "\n"),
			"<b>" + "Вы достигли финального уровня пользователя Таробота! ПОЗДРАВЛЯЕМ!!! " + " </b>🎉✨🎈"
			)
		
		text = "$name_level" + comment + common_text
		
		text: str = text + "\n".join(low_level_text) if level != 5 else text + "\n".join(high_level_text)

		if level == 4: text = text + "\n\n🎉 " + _("Пришло пользователей: $invited_users\n😏 Осталось пригласить: $need_users")
		
		Replaces = {
			"$name_level": "<b>🏆 " + name_level + "</b>\n",
			"$bonus_layouts": str(bonus_layouts),
			"$level": str(level),
			"$next_level": str(level + 1),
			"$requirements_action": requirements_action,
			"$requirements": tarobot_status[level] + "!",
			"$referal_link": self.generate_referal_link(user.id), 
			"$promocode" : str(AscendData(user = user).promo),
			"$invited_users": str(AscendData(user = user).count_invited_users),
			"$need_users": str(AscendData(user = user).users_need_to_invited)
		}

		for Substring in Replaces.keys(): text = text.replace(Substring, Replaces[Substring])

		self.bot.send_animation(
			chat_id = user.id,
			animation = self.__cacher.get_real_cached_file(
				path = f"Data/AscendTarobot/Materials/Levels/{level}.mp4",
				autoupload_type = types.InputMediaAnimation,
				).file_id,
			caption = text, 
			parse_mode = "HTML",
			reply_markup = MainInlineKeyboards.for_delete("Окей!") if level != 5 else InlineKeyboards.reaching_5_level(("Написать Таро Мастеру!", "Окей! Спасибо большое!"))
			)

class MainAscend:
	"""Основной класс модуля повышения таробота."""

	@property
	def users(self):
		"""Данные пользователей."""
		return self.__users
	
	@property
	def scheduler(self):
		"""Планировщик задач."""

		return self.__scheduler
	
	@property
	def bot(self):
		"""Telegram bot."""

		return self.__bot

	@property
	def cacher(self):
		"""Менеджер кэша."""

		return self.__cacher

	@property
	def subscription(self):
		"""Менеджер подписки."""

		return self.__subscription
	
	@property
	def decorators(self):
		"""Набор декораторов."""

		return self.__Decorators
	
	@property
	def sender(self):
		"""Отправитель сообщений."""

		return self.__Sender
	
	def __init__(self, users: UsersManager, scheduler: BackgroundScheduler, bot: TeleBot, cacher: TeleCache, subscription: "Subscription"):
		"""
		Основной класс модуля повышения таробота.

		:param users: Данные пользователей.
		:type users: UsersManager
		:param scheduler: Планировщик задач.
		:type scheduler: BackgroundScheduler
		:param bot: Telegram bot.
		:type bot: TeleBot
		:param cacher: Менеджер кэша.
		:type cacher: TeleCache
		"""

		self.__users = users
		self.__scheduler = scheduler or BackgroundScheduler()
		self.__bot = bot
		self.__cacher = cacher
		self.__subscription = subscription

		self.__Scheduler = Scheduler(self)
		self.__Decorators = Decorators(self)

		self.__Sender = Sender(self.__bot, self.__cacher)
