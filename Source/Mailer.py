from dublib.TelebotUtils import UsersManager, UserData

from Source.Cards import Cards
from Source.Reader import Reader
from Source.InlineKeyboards import InlineKeyboards

from telebot import TeleBot
import random
from datetime import datetime
import logging
from apscheduler.schedulers.background import BackgroundScheduler

class Mailer:

	def __ChoiceSentence(self, Sentences) -> str:
		random_sentence = random.randint(1, len(Sentences))
		
		for Index in range(len(Sentences)):
			if Index == random_sentence-1:
				Text = Sentences[Index]

		return Text

	def __init__(self, bot: TeleBot, usermanager: UsersManager, Card: Cards, InlineKeyboard: InlineKeyboards):
		self.__Bot = bot
		self.__usermanager = usermanager
		self.__Card = Card
		self.__InlineKeyboard = InlineKeyboard
		
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
							reply_markup = self.__InlineKeyboard.for_delete("Да будет так!"),
							caption = InstantCard["text"], 
							parse_mode= 'HTML'
							)
					else:
						Photo, Text = self.__Card.GetCard()
						Message = self.__Bot.send_photo(
							User.id,
							photo = open(f"{Photo}", "rb"),
							reply_markup = self.__InlineKeyboard.for_delete("Да будет так!"),
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

	def Mailings(self, day_of_week, reader: Reader, scheduler: BackgroundScheduler, Bot: TeleBot, restart: bool = False):
		
		for User in self.__usermanager.users:

			try: 
				type_text = None
				random_hour = 0
				random_minute = 0 
				text = None
				main_text = "Послание Вселенной для тебя на сегодня:"
				
				days = User.get_property("Planning_days")
				for i in days["common_days"]:
					if day_of_week == i: type_text = "common"
				if day_of_week == days["exclusive_day"]: type_text = "exclusive"
				today = datetime.now()
				if not restart:
					random_hour = random.randint(6, 23)
					random_minute = random.randint(0, 59)
				else:
					current_hour = today.hour
					current_minute = today.minute
					random_hour = random.randint(current_hour, 23)

					if random_hour == current_hour: random_minute = random.randint(current_minute, 59)
					else: random_minute = random.randint(0, 59)

				
				time_variable = f"{random_hour}:{random_minute}:00"
				hours, minutes, seconds = map(int, time_variable.split(':'))
				specific_time = today.replace(hour=hours, minute=minutes, second=seconds, microsecond=0)

				if type_text == "common": 
					text = self.__ChoiceSentence(reader.Get_letters)
					common_text = f"<i>{main_text}</i>\n\n<b>- {text}</b>"
					scheduler.add_job(self.send_message, 'date', run_date=specific_time, args=[User, Bot, common_text, type_text, day_of_week])
					logging.info(f"Послания Вселенной будут отправлены {specific_time} пользователю {User.id} с сообщением {text}, {type_text}")

				if type_text == "exclusive": 
					text = self.__ChoiceSentence(reader.Get_appeals)
					exclusive_text = f"<i>{main_text}</i>\n\n<b><i>- {text}</i></b>"
					scheduler.add_job(self.send_message, 'date', run_date=specific_time, args=[User, Bot, exclusive_text, type_text, day_of_week])
					logging.info(f"Послания Вселенной будут отправлены {specific_time} пользователю {User.id} с сообщением {text}, {type_text}")

			except Exception as ExceptionData: print(User.id, ExceptionData)

	def send_message(self, User: UserData, Bot: TeleBot, text: str, type_text: str, day_of_week: int):

		if type_text == "common":
			Planning_days: dict = User.get_property("Planning_days")
			Common_days: list = Planning_days["common_days"].copy()
			Common_days.remove(day_of_week)
			Planning_days["common_days"] = Common_days
			User.set_property("Planning_days", Planning_days)
			Bot.send_message(
				User.id,
				text = text,
				parse_mode = "HTML",
				reply_markup = self.__InlineKeyboard.for_delete("Принимаю")
			)
			return
		
		if type_text == "exclusive":
			Planning_days: dict = User.get_property("Planning_days")
			Planning_days["exclusive_day"] = ""
			User.set_property("Planning_days", Planning_days)
			Bot.send_message(
				User.id,
				text = text,
				parse_mode = "HTML",
				reply_markup = self.__InlineKeyboard.Sharing(text)
			)
			return
		
	def once_mailing(self, Bot: TeleBot):
		text = "<i>Послание Вселенной для тебя на сегодня:</i>\n\n<b>- Завтра день чудес</b>"
		for User in self.__usermanager.users:
			try: User.get_property("Once")					
			except: 
				try:
					Bot.send_message(
						User.id,
						text = text,
						parse_mode = "HTML",
						reply_markup = self.__InlineKeyboard.for_restart("Принимаю")
					)
					logging.info(f"Послания Вселенной отправлены  пользователю {User.id} с сообщением {text}")
					User.set_temp_property("Once", True)
				except:
					logging.info(f"{User.id}")
					User.set_chat_forbidden(True)
