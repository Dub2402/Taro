from Source.Modules.Subscription import Subscription
from Source.InlineKeyboards import InlineKeyboards as GeneralInlineKeyboards

from dublib.Engine.GetText import _
from dublib.TelebotUtils.Users import UsersManager, UserData
from dublib.Methods.Filesystem import ReadJSON, WriteJSON
from dublib.TelebotUtils.Cache import TeleCache
from dublib.TelebotUtils import TeleMaster
from dublib.Methods.Data import ToIterable

from telebot import TeleBot, types

from datetime import datetime
from types import MappingProxyType
from typing import  Iterable
import logging
import os


class InlineKeyboards:
	"""Набор шаблонов InlineKeyboard."""

	def feedback():
		"""Строит Inline-интерфейс: конец работы."""

		Menu = types.InlineKeyboardMarkup()
		More = types.InlineKeyboardButton(_("Написать сообщение" + " +"), callback_data = "send_feedback")
		ThankYou = types.InlineKeyboardButton(_("◀️ Назад"), callback_data = "for_delete")
		Menu.add(More, ThankYou, row_width = 1)

		return Menu
	
	def feedback_message():
		"""Строит Inline-интерфейс: одобрение посланий."""

		Menu = types.InlineKeyboardMarkup()
		Edit = types.InlineKeyboardButton("✍️ " + _("Исправить"), callback_data = "edit_feedback")
		Confirm = types.InlineKeyboardButton("✅️ " +_("Подтвердить"), callback_data = "confirm_feedback")
		Menu.add(Edit, Confirm, row_width = 1)

		return Menu
	
	def end_get_feedback():
		"""Строит Inline-интерфейс: конец работы."""

		Menu = types.InlineKeyboardMarkup()
		ThankYou = types.InlineKeyboardButton(text = _("И вам тоже!"), callback_data = "end_get_feedback")
		Menu.add(ThankYou, row_width = 1)

		return Menu

class Decorators:
	"""Набор декораторов."""

	def __init__(self, feedback: "Feedback"):

		self.__Feedback = feedback

	def inline_keyboards(self):
		"""Обработка Callback-запросов"""

		bot = self.__Feedback.bot
		users = self.__Feedback.users
		subscription = self.__Feedback.subscription
		inline_keyboards = self.__Feedback.inline_keyboards

		@bot.callback_query_handler(func = lambda Callback: Callback.data == "feedback")
		def click_feedback(Call: types.CallbackQuery):
			"""
			Нажатие на кнопку: "Обратная связь"

			:param Call: feedback
			:type Call: types.CallbackQuery
			"""

			user = users.auth(Call.from_user)
			if not subscription.IsSubscripted(user):
				bot.answer_callback_query(Call.id)
				return
			
			Text = (
				("<b>" + _("ОБРАТНАЯ СВЯЗЬ") + "</b>"),
				_("Будем рады услышать от вас идеи 💡, просьбы, предложения и сообщения о проблемах! Мы стараемся делать для вас самый лучший и уникальный продукт!"),
				("<b><i>" + _("Спасибо, что вы с нами!" + "</i></b>"))
				)
		
			bot.send_animation(
				chat_id = Call.message.chat.id, 
				animation = self.__Feedback.cacher.get_real_cached_file(
					path = "Data/AdditionalOptions/feedback.mp4",
					autoupload_type = types.InputMediaAnimation
					).file_id,
				caption = "\n\n".join(Text),
				parse_mode = "HTML",
				reply_markup = self.__Feedback.inline_keyboards.feedback()
			)
			bot.answer_callback_query(Call.id)

		@bot.callback_query_handler(func = lambda Callback: Callback.data == "send_feedback")
		def send_feedback(Call: types.CallbackQuery):
			"""
			Нажатие на кнопку: "Написать сообщение +"

			:param Call: send_feedback
			:type Call: types.CallbackQuery
			"""

			user = users.auth(Call.from_user)
			if not subscription.IsSubscripted(user):
				bot.answer_callback_query(Call.id)
				return
			
			Text = (
				("Напишите, пожалуйста, что бы вы хотели передать службе поддержки Таробота."),
				_("У вас неограниченное количество, символов. Просьба, ") + "<u>" + "обязательно вначале указывать свои контакты," + "</u>" + " чтобы мы смогли, в случае чего, связаться с вами. Желательно ваш ник в телеграме!",
				("<b><i>" + _("Ваш текст можете вводить прям под этим сообщением:" + "</i></b>"))
				)
			
			Data(user).add_removable_messages(bot.send_message(
				chat_id = Call.message.chat.id, 
				text = "\n\n".join(Text),
				parse_mode = "HTML",
				reply_markup = GeneralInlineKeyboards.for_delete()
			).id
			)

			user.set_expected_type("feedback")
			bot.answer_callback_query(Call.id)

		@self.__Feedback.bot.callback_query_handler(func = lambda Callback: Callback.data == "edit_feedback")
		def edit_feedback(Call: types.CallbackQuery):
			"""
			Нажатие на кнопку: "✍️ Исправить"

			:param Call: edit_feedback
			:type Call: types.CallbackQuery
			"""

			user = users.auth(Call.from_user)
			if not subscription.IsSubscripted(user):
				bot.answer_callback_query(Call.id)
				return
			
			Data(user).add_removable_messages(bot.send_message(
				chat_id = Call.message.chat.id, 
				text = "Введите, пожалуйста, исправленный текст:",
				parse_mode = "HTML"
			).id
			)

			user.set_expected_type("feedback")
			bot.answer_callback_query(Call.id)

		@bot.callback_query_handler(func = lambda Callback: Callback.data == "confirm_feedback")
		def confirm_feedback(Call: types.CallbackQuery):
			"""
			Нажатие на кнопку: "✅️ Подтвердить"

			:param Call: confirm_feedback
			:type Call: types.CallbackQuery
			"""

			user = users.auth(Call.from_user)
			if not subscription.IsSubscripted(user):
				bot.answer_callback_query(Call.id)
				return
			
			Text = (
				"<i>" + _("Спасибо! Ваше сообщение было успешно отправлено на проверку! Если оно будет интересно и актуально для наших разработчиков Таробота, то мы обязательно свяжемся с вами и обсудим все детали!") + "</i>",
				"<b>" + _("Мы очень ценим ваше участие в нашем развитии! Хорошего вам дня!") + "</b>"
				)
			
			Data(user).add_removable_messages(bot.send_message(
				chat_id = Call.message.chat.id, 
				text = "\n\n".join(Text),
				parse_mode = "HTML",
				reply_markup = inline_keyboards.end_get_feedback()
			).id
			)
			user.reset_expected_type()
			user.clear_temp_properties()

			bot.answer_callback_query(Call.id)

		@bot.callback_query_handler(func = lambda Callback: Callback.data == "end_get_feedback")
		def end_feedback(Call: types.CallbackQuery):
			"""
			Нажатие на кнопку: "И вам тоже!"

			:param Call: confirm_feedback
			:type Call: types.CallbackQuery
			"""

			user = users.auth(Call.from_user)
			if not subscription.IsSubscripted(user):
				bot.answer_callback_query(Call.id)
				return
			
			data = Data(user)
			TeleMaster(bot).safely_delete_messages(chat_id = Call.message.chat.id, messages = data.removable_messages)
			data.delete_removable_messages()
		
			bot.answer_callback_query(Call.id)
			
class Procedures:
	"""Набор процедур."""

	def __init__(self, feedback: "Feedback"):

		#---> Генерация динамических свойств.
		#==========================================================================================#
		self.__Feedback = feedback

	def text(self, message: types.Message)-> bool:
		"""
		Процедура обработки текста.

		:param message: Структура сообщения.
		:type message: types.Message
		:return: Если процедура сработала, возвращает `True`.
		:rtype: bool
		"""

		user = self.__Feedback.users.auth(message.from_user)
	
		if user.expected_type != "feedback": return False

		else:
			user.reset_expected_type()
			user.set_temp_property("feedback_message", message.text)
			Data(user).add_removable_messages(message.id)
			Text = (
				_("<b>ВАШ ТЕКСТ:</b>"),
				message.text,
				_("<i>Проверьте, пожалуйста, все ли правильно вы написали?</i>")
			)
	
			Data(user).add_removable_messages(self.__Feedback.bot.send_message(
				chat_id = user.id,
				text = "\n\n".join(Text),
				parse_mode = "HTML",
				reply_markup = self.__Feedback.inline_keyboards.feedback_message()
			).id
			)	
	
		return True

FeedbackParameters = MappingProxyType(
	{
	"removable_messages": []
	}
)

class FeedbackData:
	"""Данные обратной связи пользователей."""

	def __init__(self):

		self.__Path = "Data/AdditionalOptions/Feedback.json"
		self.__DataFeedback = {
			"feedback": {}
		}

		self.__reload()

	def __reload(self):
		"""Загружает сообщения обратной связи от пользователей."""

		if os.path.exists(self.__Path): self.__Data = ReadJSON(self.__Path)
		else: self.__save()

	def __save(self):
		"""Сохраняет сообщения обратной связи от пользователей."""

		WriteJSON(self.__Path, self.__DataFeedback)

	def __get_free_id(self):

		Increment = list()
		for key in self.__Data.keys(): Increment.append(int(key))
		Increment.sort()
		FreeID = 1
		if Increment: FreeID = max(Increment) + 1

		return FreeID

	def add_feedback(self, user_id: int, message: str):
		"""
		Запоминает текст обратной связи от пользователя.

		:param user_id: ID пользователя.
		:type user_id: int
		:param message: Текст сообщения.
		:type message: str
		"""

		self.__Data["feedback"][self.__get_free_id()] = {
			"message": message,
			"date": str(datetime.now()),
			"user": user_id
		}
		self.__save()

class Data:
	"""Хранитель данных пользователя."""

	@property
	def removable_messages(self) -> list[int]:
		"""Список id сообщений, которые необходимо удалить."""
		
		return self.__Data["removable_messages"]

	def __init__(self, user: UserData):
		"""
		Контейнер обратной связи пользователя.

		:param user: Данные пользователя.
		:type user: UserData
		"""

		self.__User = user
	
		self.__Data = self.__ValidateDate()

	def __ValidateDate(self) -> dict[str, list]:
		"""
		Проверяет валидность обратной связи пользователя.

		:return: Данные пользователя.
		:rtype: dict[str, Any]
		"""
		
		if not self.__User.has_property("feedback"):
			self.__User.set_property("feedback", FeedbackParameters.copy())
			
		else:
			Data: dict = self.__User.get_property("feedback")

			for Key in FeedbackParameters.keys():

				if Key not in Data.keys():
					Data[Key] = FeedbackParameters[Key]
					logging.debug(f"For user #{self.__User.id} key \"{Key}\" set to default.")

			self.__User.set_property("feedback", Data)

		return self.__User.get_property("feedback")
	
	def __SetParameter(self, key: str ["removable_messages"], value: Iterable[int]):
		"""
		Сохраняет параметры обратной связи пользователя.

		:param key: Ключ параметра.
		:type key: str ["removable_messages"]
		:param value: Значение параметра.
		:type value: Iterable[int]
		"""
		
		self.__Data[key] = value
		
		self.save()

	def save(self):
		"""Сохраняет данные обратной связи пользователя."""

		self.__User.set_property("feedback", self.__Data)

	def add_removable_messages(self, message_id: Iterable[int] | int):
		"""
		Добавляет id сообщений, которые необходимо удалить и говорящие об ограничении использования онлайн раскладов.

		:param message_id: Сообщения об ограничении использования онлайн раскладов.
		:type message_id: Iterable[int] | int
		"""

		MessagesID = self.removable_messages 
		MessagesID.extend(ToIterable(message_id))
		self.__SetParameter("removable_messages", MessagesID)

	def delete_removable_messages(self):
		"""
		Добавляет id сообщений, которые необходимо удалить и говорящие об ограничении использования онлайн раскладов.

		:param message_id: Сообщения об ограничении использования онлайн раскладов.
		:type message_id: Iterable[int] | int
		"""

		self.__SetParameter("removable_messages", [])

class Feedback:
	"""Раздел таробота, отвечающий за обратную связь от пользователей."""

	@property
	def decorators(self) -> Decorators:
		"""Наборы декораторов."""
		
		return self.__Decorators
	
	@property
	def procedures(self) -> Procedures:
		"""Наборы процедур."""
		
		return self.__Procedures

	@property
	def bot(self) -> TeleBot:
		"""Telegram bot."""

		return self.__bot
	
	@property
	def users(self) -> UsersManager:
		"""Данные о пользователях."""

		return self.__users
	
	@property
	def cacher(self) -> TeleCache:
		"""Основные настройки."""
		
		return self.__cacher
	
	@property
	def subscription(self) -> Subscription:
		"""Проверка подписки."""
		
		return self.__subscription
	
	@property
	def inline_keyboards(self) -> InlineKeyboards:
		"""Набор inline-keyboards."""
		
		return self.__inline_keyboards
	
	def __init__(self, users: UsersManager, cacher: TeleCache, subscription: Subscription, bot: TeleBot):
		"""Инициализация
		
		:param users: данные пользователей
		:type users: UsersManager
		:param cacher: экземпляр менеджера кэша
		:type cacher: TeleCache
		:param subscription: экземпляр менеджера подписки
		:type subscription: Subscription
		:param bot: экземпляр Telegram бота
		:type bot: TeleBot
		"""
	
		self.__Decorators = Decorators(self)
		self.__Procedures = Procedures(self)
		self.__inline_keyboards = InlineKeyboards
		self.__users = users
		self.__cacher = cacher
		self.__subscription = subscription
		self.__bot = bot