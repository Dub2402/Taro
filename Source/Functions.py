from dublib.TelebotUtils import UserData
from dublib.TelebotUtils import TeleMaster
from dublib.Engine.GetText import _

from Source.InlineKeyboards import InlineKeyboards

import random

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

		Subscribtion_Link = Settings["subscription_link"]

		if not IsSubscribed and not Subscribtion_Message: 
			Message = MasterBot.bot.send_message(
				chat_id = User.id, 
				text = _("Чтобы использовать бот, станьте участником канала! %s") % Subscribtion_Link, 
				reply_markup = InlineKeyboard.Subscribtion())
			User.set_property("Subscription", Message.id)
			return IsSubscribed
		
		if not IsSubscribed and Subscribtion_Message: 
			print(Subscribtion_Message)
			try:
				MasterBot.bot.delete_message(
				chat_id = User.id, 
				message_id = Subscribtion_Message
			)
			except: pass
			Message = MasterBot.bot.send_message(
				chat_id = User.id, 
				text = _("Чтобы использовать бот, станьте участником канала! %s") % Subscribtion_Link, 
				reply_markup = InlineKeyboard.Subscribtion())
			User.set_property("Subscription", Message.id)

		if IsSubscribed and Subscribtion_Message: 
			try: 
				MasterBot.bot.delete_message(User.id, Subscribtion_Message)
				User.set_property("Subscription", None)
			except: pass
			return IsSubscribed
		
		if IsSubscribed and not Subscribtion_Message: 
			return IsSubscribed
		