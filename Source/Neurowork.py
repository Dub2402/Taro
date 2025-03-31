from dublib.TelebotUtils.Cache import TeleCache
from dublib.Methods.Filesystem import ReadJSON

from Source.Functions import _

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
	
	def __GetNumber(self, card: str):
		return card.replace(".jpg", "").strip()

	def __GetTextByCardNumber(self, number: int, Text_typle = ("Первая", "Вторая", "Третья")) -> str:
		return Text_typle[number - 2]
	
	def __NameCard(self, collection: str, number: int):
		return ReadJSON(f"Materials/Layouts/{collection}/cards.json")[number-2]
	
	def __IsTextValid(self, text: str) -> bool:
		"""
		Проверяет валидность текста на основе регулярного выражения, исключающего латиницу и иные не кирилические символы.
			text – проверяемый текст.
		"""

		text = str(text)

		return bool(re.match(r"^[А-Яа-яЁё\s.,:;!?()\-\–«»\"\'\[\]{}]+$", text, re.IGNORECASE))

	def __init__(self, Bot: telebot.TeleBot, Cacher: TeleCache):
		self.__bot = Bot   
		self.__cacher = Cacher
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
					File = self.__cacher.get_cached_file(f"Materials/Layouts/{collection}/{card}", type = types.InputMediaPhoto)
					PhotoID = self.__cacher[f"Materials/Layouts/{collection}/{card}"]
					if NumberCard == "1":
						Text_response, Result = self.PreparationText(user_text)
						if Result:
							self.__bot.send_photo(
								chat_id = chat_id,
								photo = PhotoID,
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
								photo = PhotoID,
								caption = Text,
								parse_mode = "HTML" 
							)
					sleep(1)
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
		
		texts = [
			_("Ну что ж, давай погрузимся в тайны Таро и раскроем, что карты говорят о том..."),
			_("Ухх.. Хороший какой вопрос! Сейчас посмотрим, какой ответ тебе даст расклад на..."),
			_("Спасибо, очень интересно! Сейчас разложим карты и узнаем какой совет они дадут тебе..."),
			_("Ничего себе! Вот это я понимаю запрос к картам. Давай-ка сейчас и узнаем, что расклад скажет о..."),
			_("Вот это ситуация! Довольно любопытный должен получится расклад на твой вопрос о...")
		]
		random_text = random.choice(texts)

		while Text_response is None:
			Result = False
			Request = f"У тебя есть шаблон: {random_text} [question]."
			Request += f"Тебе задали вопрос: {user_text}. Выведи шаблон учитывая, что спрашивающий имеет ввиду не тебя в вопросе, не добавляй восклицательный знак и двоеточие, а также не используй форматирование. Согласуй, учитывая правила русского языка."
			Request += "Если вопрос похож на случайно введённый или не имеющий значения, или это один символ - выведи: Ваше сообщение не совсем понятно. Если у вас есть вопрос или тема, которую вы хотите обсудить, пожалуйста, напишите об этом. Я с радостью помогу вам!"
			Response = self.__Client.chat.completions.create(model = "gpt-4o", messages = [{"role": "user", "content": Request}])
			Text_response = Response.choices[0].message.content.strip().replace("\n", "\n\n")

			if Text_response == "Ваше сообщение не совсем понятно. Если у вас есть вопрос или тема, которую вы хотите обсудить, пожалуйста, напишите об этом. Я с радостью помогу вам!":
				Result = False
			else:
				Result = True

			# if not self.__IsTextValid(Text_response): Text_response = None
				
		return Text_response, Result
	
	def GenerationCardLayout(self, number: str, card: str, user_text: str) -> str:

		Request = f"Проанализируй эти данные: {number}, {card} и {user_text} и предоставь ответ в следующем формате:"
		Request += f"{number}, «{card}», может указывать на [помести сюда своё мнение о том, на что может указывать значение карты о заданном вопросе]."
		Request += "Не более 250 символов в тексте. Не меняй первые два словосочетания!!!"
		Response = self.__Client.chat.completions.create(model = "gpt-4o", messages = [{"role": "user", "content": Request}])
		Text_response = Response.choices[0].message.content.strip().replace("\n", "\n\n").replace("«", "«<b>").replace("»", "</b>»")

		return Text_response
	
	def GenerationOutcome(self, First: str, Second: str, Three: str, user_text: str):
		Request = f"Проанализируй эти карты Таро: {First}, {Second} и {Three} и предоставь ответ в следующем формате на вопрос {user_text}:"
		Request += f"В целом, карты показывают [помести сюда своё мнение о том, на что могут показывать указанные значения карт о заданном вопросе]."
		Request += "Не более 250 символов в тексте. Не меняй первые два слова!!! Не упоминай названия карт!!!"
		Response = self.__Client.chat.completions.create(model = "gpt-4o", messages = [{"role": "user", "content": Request}])
		Text_response = Response.choices[0].message.content.strip().replace("\n", "\n\n")

		return Text_response
