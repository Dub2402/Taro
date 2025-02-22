
from dublib.TelebotUtils import UserData
from dublib.TelebotUtils import TeleMaster
from dublib.Methods.Filesystem import ReadJSON

from Source.InlineKeyboards import InlineKeyboards

import gettext

Settings = ReadJSON("Settings.json")
Language = Settings["language"]

_ = gettext.gettext
try: _ = gettext.translation("Taro", "locales", languages = [Language]).gettext
except FileNotFoundError: pass

def IsSubscripted(MasterBot: TeleMaster, User: UserData, Settings: dict, InlineKeyboard: InlineKeyboards):
	if Settings["subscription_chanel"] == None:
		IsSubscribed = True
		return IsSubscribed
	else:
		IsSubscribed = MasterBot.check_user_subscriptions(User, Settings["subscription_chanel"])
		try:
			Subscribtion_Message = User.get_property("Subscription")
		except:
			Subscribtion_Message = None

		if not IsSubscribed and not Subscribtion_Message: 
			Subscribtion_Link = Settings["subscription_link"]
			Message = MasterBot.bot.send_message(
				chat_id = User.id, 
				text = _("Чтобы использовать бот, станьте участником канала! %s") % Subscribtion_Link, 
				reply_markup = InlineKeyboard.Subscribtion())
			User.set_property("Subscription", Message.id)
			return IsSubscribed
		
		if not IsSubscribed and Subscribtion_Message: return

		if IsSubscribed and Subscribtion_Message: 
			try: 
				MasterBot.bot.delete_message(User.id, Subscribtion_Message)
				User.set_property("Subscription", None)
			except: pass
			return IsSubscribed
		
		if IsSubscribed and not Subscribtion_Message: 
			return IsSubscribed