from dublib.TelebotUtils import UsersManager
from telebot import types


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
		Deleted_messages = User.set_property("Deleted_messages", Deleted_messages)