from dublib.TelebotUtils import UsersManager
from dublib.TelebotUtils.Cache import TeleCache

from Source.Cards import Cards
from Source.Reader import Reader

from telebot import TeleBot
from telebot import types

import random
from datetime import datetime
import logging
from apscheduler.schedulers.background import BackgroundScheduler

class Mailer:

	def __ChoiceSentence(Sentences) -> str:
		random_sentence = random.randint(1, len(Sentences))
		
		for Index in range(len(Sentences)):
			if Index == random_sentence-1:
				Text = Sentences[Index]

		return Text

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

	def Planning(self):
		for User in self.__usermanager.users:
			exclusive_days = list()
			User.set_property("Planning_days", None, force = False)
			common_days = random.sample(list(range(7)), 5)
			common_days.sort()
			for i in range(6):
				if i not in common_days: exclusive_days.append(i)
			
			exclusive_day = random.choice(exclusive_days)
			User.set_property("Planning_days", {"common_days": common_days, "exclusive_day": exclusive_day})

	def Mailings(self, day_of_week, reader: Reader, scheduler: BackgroundScheduler, Bot: TeleBot):
		
		for User in self.__usermanager.users:
			exclusive = False
			common = False
			random_hour = 0
			random_minute = 0 
			text = None
			
			days = User.get_property("Planning_days")
			for i in days["common_days"]:
				if day_of_week == i: common = True
			if day_of_week == days["exclusive_day"]: exclusive = True

			
			random_hour = random.randint(6, 23)
			random_minute = random.randint(0, 59)
			if common: 
				text = self.__ChoiceSentence(reader.Get_letters)
			if exclusive: 
				text = self.__ChoiceSentence(reader.Get_appeals)


			today = datetime.now()
			time_variable = f"{random_hour}:{random_minute}:00"
			hours, minutes, seconds = map(int, time_variable.split(':'))
			specific_time = today.replace(hour=hours, minute=minutes, second=seconds, microsecond=0)
			scheduler.add_job(self.send_message, 'date', run_date=specific_time, args=[User.id, Bot, text])


	def send_message(self, user_id: int, Bot: TeleBot, text: str):
		Bot.send_message(
			user_id,
			text
		)