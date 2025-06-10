from dublib.TelebotUtils import UserData, UsersManager
from dublib.TelebotUtils import TeleMaster
from dublib.TelebotUtils.Cache import TeleCache
from dublib.Engine.GetText import _

from Source.InlineKeyboards import InlineKeyboards

import os
import logging
from datetime import datetime
from telebot import TeleBot, types
		
def IsNewRound(today: str, saved_date: str):
	isNewRound = None

	now = datetime.now()
	day_of_week = now.weekday()

	today_datetime = datetime.strptime(today, "%d.%m.%Y")
	saved_datetime = datetime.strptime(saved_date, "%d.%m.%Y")

	difference = today_datetime - saved_datetime

	if difference <=1: isNewRound = False
	elif difference >1 and day_of_week == 6: isNewRound = False
	else: isNewRound = True

	return isNewRound

def FindNearest(today: str):
	"""
	Получение самой близкой даты к сегодняшнему дню

	:param today: сегодняшняя дата в формате 22.05.2025
	:type today: str
	:return: самая близкая дата к сегодняшнему дню в прошлом (21.05 или 22.05, при правильной работе)
	:rtype: _type_
	"""

	directory_path = "Materials/ChoiceCard/"
	dates = os.listdir(directory_path)
	today_datetime = datetime.strptime(today, "%d.%m.%Y")
	past_dates = []
	
	for date in dates:
		try:
			dir_datetime = datetime.strptime(date, "%d.%m.%Y")
			if dir_datetime < today_datetime:
				past_dates.append(dir_datetime)
		except ValueError:
			continue
	
	closest_past_date = max(past_dates) if past_dates else None
	
	return closest_past_date.strftime("%d.%m.%Y") if closest_past_date else None

def ChoiceMessage(day_of_week: int, Bot: TeleBot, Call: types.CallbackQuery) -> types.Message:
	"""
	Выбор сообщения в зависимости от дня недели

	:param day_of_week: порядковый номер дня недели, где 0 - понедельник
	:type day_of_week: int
	:param Bot: Бот Telegram
	:type Bot: TeleBot
	:param Call: ThinkCard
	:type Call: types.CallbackQuery
	:return: Сообщение отправленное пользователю
	:rtype: types.Message
	"""
	if day_of_week in (0, 1):
		Think_message3 = Bot.send_message(
			Call.message.chat.id, 
			"Каждый <b>понедельник, среду и пятницу</b> наши эксперты обновляют для вас \"Загадай карту\". Мы хотим сделать ваш досуг с Тароботом еще интереснее)\n\nЖдём вас с нетерпением в <b>среду!</b> 💖",
			reply_markup = InlineKeyboards.delete_before_mm(),
			parse_mode = "HTML"
		)
		return Think_message3
	
	if day_of_week in (2, 3):
		Think_message3 = Bot.send_message(
			Call.message.chat.id, 
			"Каждый <b>понедельник, среду и пятницу</b> наши эксперты обновляют для вас \"Загадай карту\". Мы хотим сделать ваш досуг с Тароботом еще интереснее)\n\nЖдём вас с нетерпением в <b>пятницу!</b>💗",
			reply_markup = InlineKeyboards.delete_before_mm(),
			parse_mode = "HTML"
		)
		return Think_message3
	if day_of_week in (4, 5, 6):
		Think_message3 = Bot.send_message(
			Call.message.chat.id, 
			"Каждый <b>понедельник, среду и пятницу</b> наши эксперты обновляют для вас \"Загадай карту\". Мы хотим сделать ваш досуг с Тароботом еще интереснее)\n\nЖдём вас с нетерпением в <b>понедельник!</b> 💞",
			reply_markup = InlineKeyboards.delete_before_mm(),
			parse_mode = "HTML"
		)
		return Think_message3
	
def CacherSending(Cacher: TeleCache, Bot: TeleBot, path: str, User: UserData, number_card: int, adding: str = "", inline: InlineKeyboards = None):
	
	ThinkCard = Cacher.get_real_cached_file(path + f"/{number_card}.jpg", types.InputMediaPhoto)

	with open(path + f"/{number_card}.txt") as file:
		Text = file.read()
	Think_message2 = Bot.send_photo(
		chat_id = User.id,
		photo = ThinkCard.file_id,
		caption = Text + adding,
		reply_markup = inline,
		parse_mode = "HTML"
	)
	return Think_message2

def UpdateThinkCardData(User: UserData, Think_message: types.Message):
	ThinkCardData = User.get_property("ThinkCard")
	if ThinkCardData is None:
		ThinkCardData = {"day": None, "messages": [Think_message.id], "number": None}
		User.set_property("ThinkCard", ThinkCardData)
	else:
		ThinkCardData["messages"].append(Think_message.id)
		User.set_property("ThinkCard", ThinkCardData)

def UpdateThinkCardData2(User: UserData, Think_messages: list[types.Message], number_card: int, date: str):
	ThinkCardData = User.get_property("ThinkCard")
	if ThinkCardData is None:
		ThinkCardData = {"day": date, "messages": Think_messages, "number": number_card}
		User.set_property("ThinkCard", ThinkCardData)
	else:
		ThinkCardData["messages"].extend(Think_messages)
		ThinkCardData["number"] = number_card
		ThinkCardData["day"] = date
		User.set_property("ThinkCard", ThinkCardData)

def GetNumberCard(User:UserData, Call: types.CallbackQuery, write: bool = True):
	"""
	Получить номер карты, загаданной пользователем в первый раз 

	:param User: данные пользователя
	:type User: UserData
	:param Call: ThinkCard
	:type Call: types.CallbackQuery
	:param write: записывать ли номер карты,если значение пустое, defaults to True
	:type write: bool, optional
	:return: номер выбранной карты
	:rtype: _type_
	"""
	ThinkCardData = User.get_property("ThinkCard")
	if ThinkCardData["number"] != None: number_card = ThinkCardData["number"] 
	else: 
		if write: number_card = int(Call.data.split("_")[-1])
		else: number_card = None
	return number_card

def update_think_card(usermanager: UsersManager):
	"""
	Сброс значения номера загаданной карты

	:param usermanager: объект класса
	:type usermanager: UsersManager
	"""
	for User in usermanager.users:
		try:
			if User.has_property("ThinkCard"):
				ThinkCard = User.get_property("ThinkCard")
				ThinkCard["number"] = None
				User.set_property("ThinkCard", ThinkCard)
		except:
			logging.info(User.id, "Загадай картой не пользовался")

def delete_thinking_messages(user: UserData, master_bot: TeleMaster, call: types.CallbackQuery):
	"""
	Удаление сообщений из раздела "загадай карту"

	:param user: объект класса
	:type user: UserData
	:param master_bot: объект класса
	:type master_bot: TeleMaster
	:param call: объект класса; ThinkCard/ delete_before_mm
	:type call: types.CallbackQuery
	"""

	ThinkCardData = user.get_property("ThinkCard")
	master_bot.safely_delete_messages(call.message.chat.id, user.get_property("ThinkCard")["messages"])
	ThinkCardData["messages"] = []
	user.set_property("ThinkCard", ThinkCardData)
		