from dublib.TelebotUtils import UserData, UsersManager
from dublib.TelebotUtils import TeleMaster
from dublib.TelebotUtils.Cache import TeleCache
from dublib.Engine.GetText import _

from Source.InlineKeyboards import InlineKeyboards

import os
import telebot
import logging
from datetime import datetime
from telebot import types

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
		
def CashingFiles(Cacher: TeleCache, path: str, type: types):
	try:
		File = Cacher.get_real_cached_file(path, type)
		return File
	except Exception as E: print(E)

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

def ChoiceMessage(day_of_week: int, Bot: telebot.TeleBot, Call: types.CallbackQuery, InlineKeyboard: InlineKeyboards):
	if day_of_week in (0, 1):
		Think_message3 = Bot.send_message(
			Call.message.chat.id, 
			"Каждый <b>понедельник, среду и пятницу</b> мы обновляем для вас интерактив \"Загадай карту\". Мы хотим сделать ваш быт и пользование Тароботом еще интереснее)\n\nЖдём вас с нетерпением в <b>среду!</b>",
			reply_markup = InlineKeyboard.delete_before_mm(),
			parse_mode = "HTML"
		)
		return Think_message3
	if day_of_week in (2, 3):
		Think_message3 = Bot.send_message(
			Call.message.chat.id, 
			"Каждый <b>понедельник, среду и пятницу</b> мы обновляем для вас интерактив \"Загадай карту\". Мы хотим сделать ваш быт и пользование Тароботом еще интереснее)\n\nЖдём вас с нетерпением в <b>пятницу!</b>",
			reply_markup = InlineKeyboard.delete_before_mm(),
			parse_mode = "HTML"
		)
		return Think_message3
	if day_of_week in (4, 5, 6):
		Think_message3 = Bot.send_message(
			Call.message.chat.id, 
			"Каждый <b>понедельник, среду и пятницу</b> мы обновляем для вас интерактив \"Загадай карту\". Мы хотим сделать ваш быт и пользование Тароботом еще интереснее)\n\nЖдём вас с нетерпением в <b>понедельник!</b>",
			reply_markup = InlineKeyboard.delete_before_mm(),
			parse_mode = "HTML"
		)
		return Think_message3
	
def CacherSending(Cacher: TeleCache, Bot: telebot.TeleBot, path: str, User: UserData, number_card: int, adding: str = "", inline: InlineKeyboards = None):
	
	ThinkCard = CashingFiles(Cacher, path + f"/{number_card}.jpg", types.InputMediaPhoto)

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

def UpdateThinkCardData2(User: UserData, Think_message2: types.Message, Think_message3: types.Message, number_card: int, date: str):
	ThinkCardData = User.get_property("ThinkCard")
	if ThinkCardData is None:
		ThinkCardData = {"day": date, "messages": [Think_message2.id, Think_message3.id], "number": number_card}
		User.set_property("ThinkCard", ThinkCardData)
	else:
		ThinkCardData["messages"].extend([Think_message2.id, Think_message3.id])
		ThinkCardData["number"] = number_card
		ThinkCardData["day"] = date
		User.set_property("ThinkCard", ThinkCardData)

def GetNumberCard(User:UserData, Call: types.CallbackQuery, write: bool = True):
	ThinkCardData = User.get_property("ThinkCard")
	if ThinkCardData["number"] != None: number_card = ThinkCardData["number"] 
	else: 
		if write: number_card = int(Call.data.split("_")[-1])
		else: number_card = None
	return number_card

def DeleteNumberCard(usermanager: UsersManager):
	for User in usermanager.users:
		try:
			if User.has_property("ThinkCard"):
				ThinkCard = User.get_property("ThinkCard")
				ThinkCard["number"] = None
				User.set_property("ThinkCard", ThinkCard)
		except:
			logging.info(User.id, "Загадай картой не пользовался")
		