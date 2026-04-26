from Source.UI.WorkpiecesMessages import WorkpiecesMessages

from dublib.TelebotUtils.Cache import TeleCache
from dublib.TelebotUtils.Users import UserData, UsersManager
from dublib.TelebotUtils import TeleMaster
from dublib.Engine.GetText import _

from Source.InlineKeyboards import InlineKeyboards as MainInlineKeyboards
from Source.Modules.AscendTaro import AscendData
from Source.Modules.AscendTaro import Sender

from telebot import types

class InlineKeyboards:
	"""Набор inline-клавиатур."""

	def subscribtion() -> types.InlineKeyboardMarkup:
		menu = types.InlineKeyboardMarkup()

		determinations = {
			_("Таро для души🪽"): "https://t.me/love_tarology",
			_("Тебе Послание✨"): "https://t.me/tebe_pos"
		}
		menu.add(*[types.InlineKeyboardButton(text = name, url = link) for name, link in determinations.items()], row_width = 1)
		menu.add(types.InlineKeyboardButton(_("Я подписался!"), callback_data="Subscribe"))

		return menu
	
	def taro_soul() -> types.InlineKeyboardMarkup:
		menu = types.InlineKeyboardMarkup()

		menu.add(*[types.InlineKeyboardButton(text = "Вернуться на канал", url = "https://t.me/love_tarology")], row_width = 1)
		menu.add(types.InlineKeyboardButton(_("Спокойно! Я еще вернусь!"), callback_data= "for_delete"))

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
			_("Как подпишетесь - нажмите на кнопку: \"Я подписался!\"")
		)
		
		Message = self.__masterbot.bot.send_message(
			chat_id = User.id, 
			text = "\n\n".join(Text), 
			parse_mode = "HTML",
			disable_web_page_preview = True,
			reply_markup = InlineKeyboards.subscribtion()
		)

		User.set_property("Subscription", Message.id)

	def __send_tarofamily_message(self, User: UserData):

		action = "ВОЗВРАЩЕНИЕМ" if User.get_property("was_channels_member") else "РАДОСТЬЮ ПРИНИМАЕМ ТЕБЯ"

		Text = (
			("<b>" + "🤗 " + _("С $action в нашу большую семью Таро!") + "</b>"),
			_("Здесь ты можешь чувствовать себя как дома и задавать любые вопросы. Пусть этот ключ станет твоим проводником в мир загадок и откровений!"),
			"<b><i>" + _("С любовью, Галина Таро Мастер!") + "</i></b>"
		)
		
		self.__masterbot.bot.send_animation(
			chat_id = User.id, 
			animation = self.__cacher.get_real_cached_file(
				path = "Data/AscendTarobot/Materials/taro_family.mp4",
				autoupload_type = types.InputMediaAnimation,
				).file_id,
			caption = "\n\n".join(Text).replace("$action", action),
			parse_mode = "HTML",
			reply_markup = MainInlineKeyboards.for_delete("Благодарю Вас!")
		)

	def __init__(self, masterbot: TeleMaster, chanel: list[int], cacher: TeleCache, usermanager: UsersManager):

		self.__masterbot = masterbot
		self.__chanel = chanel
		self.__cacher = cacher
		self.__usermanager = usermanager

		self.__Templates = WorkpiecesMessages(self.__masterbot.bot, self.__cacher)

	def IsSubscripted(self, User: UserData) -> bool:
		"""
		Проверяет подписан ли пользователь на канал/каналы.

		:param User: Данные пользователя.
		:type User: UserData
		:return: Статус подписки.
		:rtype: bool
		"""

		if not User.has_property("was_channels_member"): User.set_property("was_channels_member", False) 

		if User.has_permissions(["developer"]): return True

		if not self.__chanel: return True

		IsSubscribed = self.__masterbot.check_user_subscriptions(User, self.__chanel)

		Subscribtion_Message = None
		if User.has_property("Subscription"): Subscribtion_Message = User.get_property("Subscription")

		if IsSubscribed:

			if User.has_property("invited_by"): 
				
				invitee = self.__usermanager.get_user(User.get_property("invited_by"))
				ascend_data = AscendData(user = invitee)

				if ascend_data.level_tarobot == 4 and ascend_data.necessary_invited_users > len(ascend_data.invited_users): ascend_data.add_invited_user(User.id)
				
				if ascend_data.level_tarobot != 4 or ascend_data.necessary_invited_users <= len(ascend_data.invited_users): 
					if not ascend_data.is_notification_bonus_send: 
						Sender(self.__masterbot.bot, self.__cacher).worked_referal(invitee.id)
						ascend_data.set_is_notification_bonus_send()

					ascend_data.add_bonus_layouts()

				User.remove_property("invited_by")
				
			if Subscribtion_Message:
				self.__masterbot.safely_delete_messages(User.id, Subscribtion_Message)
				self.__Templates.send_start_messages(User, title = False)
				self.__send_tarofamily_message(User)
				
				User.set_property("Subscription", None)

			if not User.get_property("was_channels_member"): User.set_property("was_channels_member", True)

		else:
			if Subscribtion_Message: self.__masterbot.safely_delete_messages(User.id, Subscribtion_Message)
			self.__send_requirements(User)

		return IsSubscribed