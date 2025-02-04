from dublib.TelebotUtils import UsersManager
from dublib.TelebotUtils.Cache import TeleCache

from Source.Cards import Cards

from telebot import TeleBot
from telebot import types

import logging


class Mailer:

	def __init__(self, bot: TeleBot, usermanager: UsersManager, Cacher: TeleCache, Card: Cards):
		self.__Bot = bot
		self.__usermanager = usermanager
		self.__Cacher = Cacher
		self.__Card = Card

	def StartMailing(self):
		
		for User in self.__usermanager.users:
			logging.info(f"Начата рассылка: {User.id} ")
			try:
				if User.get_property("mailing"):
			
					InstantCard = self.__Card.GetInstantCard()
					if InstantCard:
						self.__Bot.send_photo(
							User.id,
							photo = InstantCard["photo"],
							caption = InstantCard["text"], 
							parse_mode= 'HTML'
							)
					else:
						Photo, Text = self.__Card.GetCard()
						Message = self.__Bot.send_photo(
							User.id,
							photo = open(f"{Photo}", "rb"),
							caption = Text, 
							parse_mode= 'HTML'
							)
						self.__Card.AddCard(Message.photo[0].file_id)
						
					logging.info(f"Карта дня отправлена {User.id} ")
					User.set_chat_forbidden(False)
					
				else:
					logging.info(f"Рассылка выключена {User.id}")

			except KeyError:
				logging.info(f"Рассылкой пользователь {User.id} не пользовался.")

			except Exception as E: 
				logging.info(f"{E}, {User.id}")
				User.set_chat_forbidden(True)