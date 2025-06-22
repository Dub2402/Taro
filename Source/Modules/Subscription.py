from Source.UI.WorkpiecesMessages import WorkpiecesMessages

from dublib.TelebotUtils.Cache import TeleCache
from dublib.TelebotUtils.Users import UserData
from dublib.TelebotUtils import TeleMaster
from dublib.Engine.GetText import _

from Source.InlineKeyboards import InlineKeyboards as BasicInlineKeyboards

from telebot import types

class InlineKeyboards:
	"""Набор inline-клавиатур."""

	def subscribtion() -> types.InlineKeyboardMarkup:
		menu = types.InlineKeyboardMarkup()

		determinations = {
			_("Твой Таролог🌙"): "https://t.me/+ns_u9dpjys1jMjFi",
			_("Послания Вселенной🔆"): "https://t.me/+9U9SMzbOwY1iNzFi"
		}
		menu.add(*[types.InlineKeyboardButton(text = name, url = link) for name, link in determinations.items()], row_width = 1)
		menu.add(types.InlineKeyboardButton(_("Я подписался!"), callback_data="Subscribe"))

		return menu

class Subscription:
	"""Проверка подписки."""

	def __send_requirements(self, User: UserData):
		"""
		Отправка сообщения о необходимости подписки на каналы.

		:param User: Данные пользователя.
		:type User: UserData
		"""
		
		Text = (
			("<b><i>" + _("Друзья, чтобы использовать бот, подпишитесь на 2 наших канала спонсора! 💔") + "</i></b>"),
			_("Как подпишетесь - нажмите на кнопку \"Я подписался!\"")
		)
		
		Message = self.__masterbot.bot.send_message(
			chat_id = User.id, 
			text = "\n\n".join(Text), 
			parse_mode = "HTML",
			disable_web_page_preview = True,
			reply_markup = InlineKeyboards.subscribtion()
		)

		User.set_property("Subscription", Message.id)

	def __init__(self, masterbot: TeleMaster, chanel: list[int], cacher: TeleCache):
		self.__masterbot = masterbot
		self.__chanel = chanel
		self.__cacher = cacher

		self.__Templates = WorkpiecesMessages(self.__masterbot.bot, self.__cacher)

	def IsSubscripted(self, User: UserData):
		if User.has_permissions(["developer", "admin"]): return True

		if not self.__chanel: return True

		IsSubscribed = self.__masterbot.check_user_subscriptions(User, self.__chanel)

		if User.has_property("Subscription"): Subscribtion_Message = User.get_property("Subscription")
		else: Subscribtion_Message = None

		if not IsSubscribed and not Subscribtion_Message: 
			self.__send_requirements(User)
			return IsSubscribed
		
		if not IsSubscribed and Subscribtion_Message: 
			self.__masterbot.safely_delete_messages(
				chat_id = User.id, 
				messages = Subscribtion_Message
				)

			self.__send_requirements(User)
			return IsSubscribed
		
		if IsSubscribed and Subscribtion_Message: 
			self.__masterbot.safely_delete_messages(User.id, Subscribtion_Message)
			self.__Templates.send_start_messages(User, title = False)
			User.set_property("Subscription", None)
			
			return IsSubscribed
		
		if IsSubscribed and not Subscribtion_Message: 
			return IsSubscribed