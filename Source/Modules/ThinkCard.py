from dublib.TelebotUtils import UserData, UsersManager
from dublib.TelebotUtils.Master import TeleMaster
from dublib.TelebotUtils.Cache import TeleCache
from dublib.Methods.Data import ToIterable
from dublib.Engine.GetText import _

from Source.InlineKeyboards import InlineKeyboards

from telebot import TeleBot, types

from types import MappingProxyType
from datetime import datetime
from os import PathLike
from typing import Literal, Any, Iterable, TYPE_CHECKING
import logging
import os

if TYPE_CHECKING:
	from Source.Modules.Subscription import Subscription

ThinkCardParameters = MappingProxyType(
	{
	"messages": [],
	"number": None,
	}
)

def update_think_card(usermanager: UsersManager):
	"""
	Сброс значения номера загаданной карты

	:param usermanager: объект класса
	:type usermanager: UsersManager
	"""
	for User in usermanager.users:
		try:
			if User.has_property("ThinkCard"):
				ThinkCard = User.get_property("ThinkCard")
				ThinkCard["number"] = None
				User.set_property("ThinkCard", ThinkCard)
		except:
			logging.info(User.id, "Загадай картой не пользовался")

class Data:

	@property
	def number_card(self):
		"""Номер загаданной карты."""
		
		return self.__Data["number"]
	
	@property
	def messages(self):
		"""Сохраннёные сообщения из модуля загадай карту."""
		
		return self.__Data["messages"]

	def __ValidateDate(self) -> dict[str, Any]:
		"""
		Проверяет валидность данных для загадай карты пользователя.

		:return: Данные пользователя.
		:rtype: dict[str, Any]
		"""
		
		if not self.__User.has_property("ThinkCard"):
			self.__User.set_property("ThinkCard", ThinkCardParameters.copy())
			
		else:
			Data: dict = self.__User.get_property("ThinkCard")

			for Key in ThinkCardParameters.keys():

				if Key not in Data.keys():
					Data[Key] = ThinkCardParameters[Key]
					logging.debug(f"For user #{self.__User.id} key \"{Key}\" set to default.")

			self.__User.set_property("ThinkCard", Data)

		return self.__User.get_property("ThinkCard")

	def __init__(self, user: UserData):
		"""
		Контейнер данных для загадай карты пользователя.

		:param user: Данные пользователя.
		:type user: UserData
		"""

		self.__User = user
	
		self.__Data = self.__ValidateDate()

	def __SetParameter(self, key: Literal["day", "messages", "number"], value: Any):
		"""
		Сохраняет параметры данные для загадай карты пользователя.

		:param key: Ключ параметра.
		:type key: Literal["day", "messages", "number"]
		:param value: Значение параметра.
		:type value: Any
		"""

		self.__Data[key] = value

		self.save()

	def save(self):
		"""Сохраняет данные для загадай карты пользователя."""

		self.__User.set_property("ThinkCard", self.__Data)

	def set_number_card(self, number_card: int):
		"""
		Передаёт параметры для сохранения данных для загадай карты пользователя. Перезаписывается, только если значение None.

		:param number_card: номер выбранной карты.
		:type number_card: int
		"""

		if self.number_card == None:self.__SetParameter("number", number_card)
	
	def add_messages(self, message_id: Iterable[int] | int):
		"""
		Добавляет id сообщений, которые необходимо удалить.

		:param message_id: Добавляет id сообщений, которые необходимо удалить.
		:type message_id: Iterable[int] | int
		"""

		MessagesID: list = self.messages 
		MessagesID.extend(ToIterable(message_id))
		self.__SetParameter("messages", MessagesID)

	def zeroing_messages(self):
		"""Обнуление ID сообщений, относятся к модулю загадай карту."""

		self.__SetParameter("messages", [])
	
class Manager:

	@property
	def day_of_week(self):
		"""Сегодняшний день недели."""

		return datetime.now().weekday()
	
	@property
	def date(self):
		"""Сегодняшнее число."""

		return datetime.now().strftime("%d.%m.%Y")
	
	
	def __FindNearest(self, today: str)-> PathLike:
		"""
		Получение самой близкой даты к сегодняшнему дню.

		:param today: сегодняшняя дата в формате 22.05.2025
		:type today: str
		:return: самая близкая дата к сегодняшнему дню в прошлом (21.05 или 22.05, при правильной работе)
		:rtype: PathLike
		"""

		directory_path = "Materials/ChoiceCard/"
		dates = os.listdir(directory_path)
		today_datetime = datetime.strptime(today, "%d.%m.%Y")
		past_dates = []
		
		for date in dates:
			try:
				dir_datetime = datetime.strptime(date, "%d.%m.%Y")
				if dir_datetime < today_datetime:
					past_dates.append(dir_datetime)
			except ValueError:
				continue
		
		closest_past_date: datetime = max(past_dates) if past_dates else None
		
		return closest_past_date.strftime("%d.%m.%Y") if closest_past_date else None
	
	def needed_folder(self) -> PathLike:
		"""
		Получение пути к папке, которая содержит необходимые данные для сегодняшнего дня. 

		:return: Путь к папке, которая содержит необходимые данные для сегодняшнего дня.
		:rtype: PathLike
		"""

		today_date = datetime.now().strftime("%d.%m.%Y")
		path = f"Materials/ChoiceCard/{today_date}"
		
		if not os.path.exists(path):
			today_date = self.__FindNearest(today_date)
			path = f"Materials/ChoiceCard/{today_date}"

		return path
	
class Sender:

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
	
	def needed_message(self, path: PathLike, User: UserData, number_card: int, adding: str = "", inline: InlineKeyboards = None) -> types.Message:
		"""
		Отправляет сообщение с заданными параметрами.

		:param path: путь к папке которая содержит необходимые данные для сегодняшнего дня.
		:type path: PathLike
		:param User: данные пользователя.
		:type User: UserData
		:param number_card: номер карты.
		:type number_card: int
		:param adding: дополнение к сообщению, defaults to ""
		:type adding: str, optional
		:param inline: экземпляр клавиатруы, defaults to None
		:type inline: InlineKeyboards, optional
		:return: отпраленное сообщение.
		:rtype: types.Message
		"""
		
		with open(path + f"/{number_card}.txt") as file:
			Text = file.read()

		introdution_message = self.bot.send_photo(
			chat_id = User.id,
			photo = self.cacher.get_real_cached_file(
				path + f"/{number_card}.jpg", 
				types.InputMediaPhoto
				).file_id,
			caption = Text + adding,
			reply_markup = inline,
			parse_mode = "HTML"
		)

		return introdution_message

class InlineKeyboard:

	def about() -> types.InlineKeyboardMarkup:
		"""
		Клавиатура к модулю "загадай карту".

		:return: inline-keyboard
		:rtype: types.InlineKeyboardMarkup
		"""

		menu = types.InlineKeyboardMarkup()

		determinations = {
			_("О \"Загадай карту\""): "about_think_card",
			_("Благодарю!"): "delete_before_mm",
		}

		for string in determinations.keys(): menu.add(types.InlineKeyboardButton(string, callback_data = determinations[string]), row_width = 1)

		return menu
	
	def delete_about_think_card() -> types.InlineKeyboardMarkup:
		"""
		Клавиатура к тексту "О Загадай карту".

		:return: inline-keyboard
		:rtype: types.InlineKeyboardMarkup
		"""

		menu = types.InlineKeyboardMarkup()

		determinations = {
			_("◀️ Назад"): "for_delete",
			_("Благодарю!"): "delete_before_mm",
		}

		for string in determinations.keys(): menu.add(types.InlineKeyboardButton(string, callback_data = determinations[string]), row_width = 1)

		return menu
	
class Decorators:
	"""Набор декораторов."""

	def __init__(self, main_think: "Main"):

		self.__main_think = main_think

		
	def inline_keyboards(self):
		"""
		Обработка inline_keyboards.
		"""

		@self.__main_think.bot.callback_query_handler(func = lambda Callback: Callback.data == "about_think_card")
		def about_think_card(Call: types.CallbackQuery):
			user = self.__main_think.users.auth(Call.from_user)
			if not self.__main_think.subscription.IsSubscripted(user):
				self.__main_think.bot.answer_callback_query(Call.id)
				return
			
			day_of_week = Manager().day_of_week

			if day_of_week in (0, 1): name_day_of_week = "среду! 💖"
			if day_of_week in (2, 3): name_day_of_week = "пятницу! 💗"
			if day_of_week in (4, 5, 6): name_day_of_week = "понедельник! 💞"

			text = (
			"<b>" + _("Загадай карту") + "</b>" + " - интерактивная рубрика, где каждый может, опираясь на свою интуицию, сам вытянуть карту и получить ответ на заданную тему." + "\n",
			_("Каждый ") + "<b>" + _("понедельник, среду и пятницу ") + "</b>"+ "наши эксперты обновляют для вас эту рубрику и стараются придумывать наиболее интересные и актуальные темы. Наша цель: сделать ваш досуг с Тароботом еще интереснее)"+ "\n",
			_("Ждём вас с нетерпением в ")+ "<b>" + name_day_of_week + "</b>")

			about_message = self.__main_think.bot.send_message(
				Call.message.chat.id, 
				text = "\n".join(text) ,
				reply_markup = InlineKeyboard.delete_about_think_card(),
				parse_mode = "HTML"
			)

			Data(user = user).add_messages(about_message.id)
			self.__main_think.bot.answer_callback_query(Call.id)

		@self.__main_think.bot.callback_query_handler(func = lambda Callback: Callback.data == "delete_before_mm")
		def delete_before_mm(Call: types.CallbackQuery):
			user = self.__main_think.users.auth(Call.from_user)
			if not self.__main_think.subscription.IsSubscripted(user):
				self.__main_think.bot.answer_callback_query(Call.id)
				return
			
			data = Data(user = user)
			TeleMaster(self.__main_think.bot).safely_delete_messages(Call.message.chat.id, data.messages)
			data.zeroing_messages()

			self.__main_think.bot.answer_callback_query(Call.id)

class Main:

	@property
	def users(self):
		"""Данные пользователей."""
		return self.__users
	
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
		"""Набор декораторов."""

		return self.__Sender

	def __init__(self, users: UsersManager, bot: TeleBot, cacher: TeleCache, subscription: "Subscription"):

		self.__users = users
		self.__cacher = cacher
		self.__bot = bot
		self.__subscription = subscription

		self.__Decorators = Decorators(self)
		self.__Sender = Sender(self.__bot, self.__cacher)
