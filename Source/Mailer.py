from dublib.TelebotUtils import UsersManager, UserData

from Source.Cards import Cards
from Source.Reader import Reader
from Source.InlineKeyboards import InlineKeyboards

from telebot import TeleBot
import random
from datetime import datetime
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from time import sleep

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
		
	def __Generationrandomtime(self, restart: bool):
		random_hour = 0
		random_minute = 0 
		today = datetime.now()
		if not restart:
			random_hour = random.randint(8, 21)
			random_minute = random.randint(0, 59)
		else:
			current_hour = today.hour
			current_minute = today.minute
			random_hour = random.randint(current_hour, 21)

			if random_hour == current_hour: random_minute = random.randint(current_minute + 1, 59)
			else: random_minute = random.randint(0, 59)
		time_variable = f"{random_hour}:{random_minute}:00"
		hours, minutes, seconds = map(int, time_variable.split(':'))
		specific_time = today.replace(hour=hours, minute=minutes, second=seconds, microsecond=0)

		return specific_time
	
	def SavePlanning_days(self, User: UserData):
		exclusive_days = list()
		common_days = random.sample(list(range(7)), 3)
		common_days.sort()
		for i in range(6):
			if i not in common_days: exclusive_days.append(i)
		
		exclusive_day = random.choice(exclusive_days)

		values = ["for_restart"] * 2 + ["for_delete"]
		random.shuffle(values)

		common_days_dict = {day: value for day, value in zip(common_days, values)}

		User.set_property("Planning_days", {"common_days": common_days_dict, "exclusive_day": exclusive_day})

	def StartMailing(self):
		
		for User in self.__usermanager.users:
			logging.info(f"Начата рассылка: {User.id} ")
			try:
				if User.get_property("mailing"):
			
					InstantCard = self.__Card.GetInstantCard()
					if InstantCard:
						self.__Bot.send_video(
							chat_id = User.id,
							video = InstantCard["video"],
							reply_markup = self.__InlineKeyboard.for_delete("Да будет так!"),
							caption = InstantCard["text"], 
							parse_mode= 'HTML'
							)
					else:
						Video, Text = self.__Card.GetCard()
						Message = self.__Bot.send_video(
							chat_id = User.id,
							video = open(f"{Video}", "rb"),
							reply_markup = self.__InlineKeyboard.for_delete("Да будет так!"),
							caption = Text, 
							parse_mode = 'HTML'
							)
						self.__Card.AddCard(Message.video[0].file_id)
						
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
			try:
				self.SavePlanning_days(User)
			except Exception as ExceptionData: print(ExceptionData)

	def Mailings(self, day_of_week, reader: Reader, scheduler: BackgroundScheduler, Bot: TeleBot, restart: bool = False):
		
		for User in self.__usermanager.users:
			try:

				type_common = False
				type_exclusive = False
				common_text = None
				exclusive_text = None
				main_text = "Послание Вселенной для тебя:"
				
				days = User.get_property("Planning_days")

				if days:
					if str(day_of_week) in days["common_days"].keys(): type_common = True
					else: type_common = False
					if day_of_week == days["exclusive_day"]: type_exclusive = True
					else: type_exclusive = False
					
				if type_common and type_exclusive:
					common_text = self.__ChoiceSentence(reader.Get_letters)
					common_ready = f"<i>{main_text}</i>\n\n<b>- {common_text}</b>"
					exclusive_text = self.__ChoiceSentence(reader.Get_appeals)
					exclusive_ready = f"<i>{main_text}</i>\n\n<b><i>- {exclusive_text}</i></b>"

					specific_time_common = self.__Generationrandomtime(restart = restart)
					specific_time_exclusive = self.__Generationrandomtime(restart = restart)

					scheduler.add_job(self.send_message, 'date', run_date = specific_time_common, args=[User, Bot, common_ready, day_of_week, type_common, False])
					logging.info(f"Послания Вселенной будут отправлены {specific_time_common} пользователю {User.id} с сообщением {common_text}, общего типа.")

					scheduler.add_job(self.send_message, 'date', run_date = specific_time_exclusive, args=[User, Bot, exclusive_ready, day_of_week, False, type_exclusive])
					logging.info(f"Послания Вселенной будут отправлены {specific_time_exclusive} пользователю {User.id} с сообщением {exclusive_text}, эксклюзивного типа.")

				elif type_common:
					common_text = self.__ChoiceSentence(reader.Get_letters)
					common_ready = f"<i>{main_text}</i>\n\n<b>- {common_text}</b>"
					specific_time_common = self.__Generationrandomtime(restart = restart)
					scheduler.add_job(self.send_message, 'date', run_date=specific_time_common, args=[User, Bot, common_ready, day_of_week, type_common, False])
					logging.info(f"Послания Вселенной будут отправлены {specific_time_common} пользователю {User.id} с сообщением {common_text}, общего типа.")
					
				elif type_exclusive: 
					exclusive_text = self.__ChoiceSentence(reader.Get_appeals)
					exclusive_ready = f"<i>{main_text}</i>\n\n<b><i>- {exclusive_text}</i></b>"
					specific_time_exclusive = self.__Generationrandomtime(restart = restart)
					scheduler.add_job(self.send_message, 'date', run_date=specific_time_exclusive, args=[User, Bot, exclusive_ready, day_of_week, False, type_exclusive])
					logging.info(f"Послания Вселенной будут отправлены {specific_time_exclusive} пользователю {User.id} с сообщением {exclusive_text} эксклюзивного типа.")
				else:
					logging.info(f"Пользователю не будет послана рассылка Посланий Вселенной {User.id}")
			except ValueError as e:
				print(e)

	def send_message(self, User: UserData, Bot: TeleBot, text: str, day_of_week: int, type_common: bool, type_exclusive: bool):

		try: 
			if type_common:
				Planning_days: dict = User.get_property("Planning_days")
				Common_days: dict = Planning_days["common_days"].copy()
				if Common_days[str(day_of_week)] == "for_restart":
					try:
						Bot.send_message(
							User.id,
							text = text,
							parse_mode = "HTML",
							reply_markup = self.__InlineKeyboard.for_restart("Принимаю")
						)
						User.set_chat_forbidden(False)
						del Common_days[str(day_of_week)]
						Planning_days["common_days"] = Common_days
						User.set_property("Planning_days", Planning_days)
					except: 
						User.set_chat_forbidden(True)
					return
				else:
					try:
						Bot.send_message(
							User.id,
							text = text,
							parse_mode = "HTML",
							reply_markup = self.__InlineKeyboard.for_delete("Принимаю")
						)
						User.set_chat_forbidden(False)
						del Common_days[day_of_week]
						Planning_days["common_days"] = Common_days
						User.set_property("Planning_days", Planning_days)
					except: 
						User.set_chat_forbidden(True)
					return
			if type_exclusive:
				Planning_days: dict = User.get_property("Planning_days")

				Planning_days["exclusive_day"] = None
				User.set_property("Planning_days", Planning_days)
				try:
					Bot.send_message(
						User.id,
						text = text,
						parse_mode = "HTML",
						reply_markup = self.__InlineKeyboard.Sharing(text)
					)
					User.set_chat_forbidden(False)
				except: 
					User.set_chat_forbidden(True)
				return
			
		except Exception as ExceptionData: print(ExceptionData)
		
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
					User.set_chat_forbidden(False)
				except:
					logging.info(f"{User.id}")
					User.set_chat_forbidden(True)
