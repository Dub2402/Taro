from dublib.TelebotUtils import UsersManager
from telebot import types
from telebot import TeleBot

class MessagesManager:

	def __init__(self) -> None:
		pass

	def AddDelMessages(self, User: UsersManager, ID: types.Message):

		try:
			Deleted_messages = User.get_property("Deleted_messages")
		except:
			User.set_property("Deleted_messages", [])
			Deleted_messages = list()

		Deleted_messages.append(ID)
		User.set_property("Deleted_messages", Deleted_messages)

	def DelListMessages(self, User: UsersManager, Bot: TeleBot, Call: types.CallbackQuery):

		Deleted_messages = User.get_property("Deleted_messages")
		for ID in Deleted_messages:
			try:
				Bot.delete_message(Call.message.chat.id, ID)
			except: 
				pass
		Deleted_messages = list()	
		User.set_property("Deleted_messages", Deleted_messages)


		