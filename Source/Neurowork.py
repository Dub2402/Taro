from dublib.TelebotUtils.Cache import TeleCache
from dublib.Methods.Filesystem import ReadJSON

from Source.Functions import _, CashingFiles

import telebot
import random
import os
import re
import g4f.Provider
from telebot import types
from time import sleep
from g4f.client import Client

class Neurowork:

	@property
	def __GenerationPhotos(self) -> int:
		return random.randint(1,40)
	
	def __match_rus(self, character, alphabet=set('абвгдеёжзийклмнопрстуфхцчшщъыьэюя')):
		
		return character.lower() in alphabet
	
	# Удаляем всё, что находится в тегах html
	def __remove_html_tags(self, text):
		return re.sub(r'<[^>]+>', '', text)
	
	def __GetNumber(self, card: str):
		return card.replace(".jpg", "").strip()

	def __GetTextByCardNumber(self, number: int, Text_typle = ("Первая", "Вторая", "Третья")) -> str:
		return Text_typle[number - 2]
	
	def __NameCard(self, collection: str, number: int):
		return ReadJSON(f"Materials/Layouts/{collection}/cards.json")[number-2]
	
	def __IsTextRussian(self, text):
		fix_text = self.__remove_html_tags(text) 
		IsRussian = True 
		if not fix_text:
			IsRussian = False
		else:
			for Character in fix_text:
				if Character.isalpha() and not self.__match_rus(Character):
					print(Character)
					IsRussian = False
					break

		return IsRussian

	def __init__(self, Bot: telebot.TeleBot, Cacher: TeleCache):
		self.__bot = Bot   
		self.__Cacher = Cacher
		self.__Client = Client()

	def AnswerForUser(self, chat_id: int, user_text: str, User):
		Completed = False
		
		set_photos = self.__GenerationPhotos

		for collection in os.listdir("Materials/Layouts"):
			dir_set = collection.split(" ")[0]
	
			if int(dir_set) == set_photos:
				Files = sorted(os.listdir(f"Materials/Layouts/{collection}"))
				Files = list(filter(lambda List: List.endswith(".jpg"), Files))
				for card in Files:
					self.__bot.send_chat_action(chat_id, action = "typing")
					NumberCard = self.__GetNumber(card)
					PhotoID = CashingFiles(self.__Cacher, f"Materials/Layouts/{collection}/{card}", types.InputMediaPhoto)
					if NumberCard == "1":
						Text_response, Result = self.PreparationText(user_text)
						if Result:
							self.__bot.send_photo(
								chat_id = chat_id,
								photo = PhotoID.file_id,
								caption = Text_response,
									parse_mode = "HTML" 
							)
						else:
							self.__bot.send_message(
								chat_id = chat_id,
								text = Text_response,
								parse_mode = "HTML" 
							)
							break
					else:
						if Result:
							CardNumber = self.__GetTextByCardNumber(int(NumberCard)) + " " + "карта"
							CardName = self.__NameCard(collection, int(NumberCard))
							Text = self.GenerationCardLayout(CardNumber, CardName, user_text)
							self.__bot.send_photo(
								chat_id = chat_id,
								photo = PhotoID.file_id,
								caption = Text,
								parse_mode = "HTML" 
							)
				if Result:
					self.__bot.send_chat_action(chat_id, action = "typing")
					Text = self.GenerationOutcome(self.__NameCard(collection, 2), self.__NameCard(collection, 3), self.__NameCard(collection, 4), user_text)
					self.__bot.send_message(
						chat_id = chat_id,
						text = Text,
						parse_mode = "HTML" 
						)
					
		Completed = True
		return Completed
		
	def PreparationText(self, user_text) -> tuple[str, bool]:
		Text_response = None
		Count_tries = 0

		texts = [
			_("Ну что ж, давай погрузимся в тайны Таро..."),
			_("Ухх.. Хороший какой вопрос! Сейчас посмотрим..."),
			_("Спасибо, очень интересно! Сейчас разложим карты..."),
			_("Ничего себе! Вот это я понимаю запрос к картам..."),
			_("Вот это ситуация! Довольно любопытный расклад...")
		]
		random_text = random.choice(texts)

		while Text_response is None and Count_tries < 3:
			Result = False
			Count_tries += 1
			print(Count_tries)

			Request = "\n".join([
				f"У тебя есть шаблон: {random_text} [question].", 
				f"Тебе задали вопрос: {user_text}. Выведи шаблон учитывая, что спрашивающий имеет ввиду не тебя в вопросе, не добавляй восклицательный знак и двоеточие, а также не используй форматирование. Согласуй, учитывая правила русского языка.",
				"Если вопрос является бессмысленным набором символов - выведи следующую строку: \"Ваше сообщение не понятно.\" не добавляя ничего другого."])

			Response = self.__Client.chat.completions.create(
				model="gpt-4o", 
				messages=[{"role": "user", "content": Request}]
			)

			Text_response = Response.choices[0].message.content.strip().replace("\n", "\n\n")

			if Text_response == "Ваше сообщение не понятно.":
				if Count_tries < 3:  
					continue
				else:  
					Text_response = "Ваше сообщение не совсем понятно. Если у вас есть вопрос или тема, которую вы хотите обсудить, пожалуйста, напишите об этом. Я с радостью помогу вам!"
					Result = False
					break  
			else:
				Result = True

				if Text_response and not self.__IsTextRussian(Text_response): Text_response = None
				else: break

		return Text_response, Result

	def GenerationCardLayout(self, number: str, card: str, user_text: str) -> str:

		Text_response = None

		while Text_response is None:
			Request = f"Проанализируй эти данные: {number}, {card} и {user_text} и предоставь ответ в следующем формате:"
			Request += f"{number}, «{card}», может указывать на [помести сюда своё мнение о том, на что может указывать значение карты о заданном вопросе]."
			Request += "Не более 250 символов в тексте. Не меняй первые два словосочетания!!!"
			Response = self.__Client.chat.completions.create(model = "gpt-4o", messages = [{"role": "user", "content": Request}])
			Text_response = Response.choices[0].message.content.strip().replace("\n", "\n\n").replace("«", "«<b>").replace("»", "</b>»")

			if not self.__IsTextRussian(Text_response): Text_response = None

		return Text_response
	
	def GenerationOutcome(self, First: str, Second: str, Three: str, user_text: str):

		Text_response = None

		while Text_response is None:
			Request = f"Проанализируй эти карты Таро: {First}, {Second} и {Three} и предоставь ответ в следующем формате на вопрос {user_text}:"
			Request += f"В целом, карты показывают [помести сюда своё мнение о том, на что могут показывать указанные значения карт о заданном вопросе]."
			Request += "Не более 250 символов в тексте. Не меняй первые два слова!!! Не упоминай названия карт!!!"
			Response = self.__Client.chat.completions.create(model = "gpt-4o", messages = [{"role": "user", "content": Request}])
			Text_response = Response.choices[0].message.content.strip().replace("\n", "\n\n")

			if not self.__IsTextRussian(Text_response): Text_response = None

		return Text_response
