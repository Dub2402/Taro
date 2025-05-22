from dublib.TelebotUtils.Cache import TeleCache
from dublib.Methods.Filesystem import ReadJSON

from Source.Functions import _, CashingFiles
from Source.UI.OnlineLayout import end_layout

import telebot
import random
import os
import re
from telebot import types
from g4f.client import Client
import logging

class Neurowork:

	@property
	def __GenerationPhotos(self) -> int:
		return random.randint(1,40)
	
	def __match_rus(self, character, alphabet=set('абвгдеёжзийклмнопрстуфхцчшщъыьэюя')):
		
		return character.lower() in alphabet
	
	def __choice_text(self, texts):
		random_text = random.choice(texts)
		return random_text

	# Удаляем всё, что находится в тегах html
	def __remove_html_tags(self, text):
		return re.sub(r'<[^>]+>', '', text)
	
	def __GetNumber(self, card: str):
		return card.replace(".jpg", "").strip()

	def __GetTextByCardNumber(self, number: int, Text_typle = ("Первая", "Вторая", "Третья")) -> str:
		return Text_typle[number - 2]
	
	def __NameCard(self, collection: str, number: int):
		return ReadJSON(f"Materials/Layouts/{collection}/cards.json")[number-2]
	
	def IsTextRussian(self, text):
		fix_text = self.__remove_html_tags(text) 
		IsRussian = True 
		if not fix_text:
			IsRussian = False
		else:
			for Character in fix_text:
				if Character.isalpha() and not self.__match_rus(Character):
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
						text = "\n\n".join(Text),
						parse_mode = "HTML",
						reply_markup = end_layout()
						)
					
		Completed = True
		return Completed
	
	def generate_text(self, request: str, tries: int = 3) -> str | None:
		"""
		Генерирует текст по запросу.
			request – текст запроса;\n
			tries – количество попыток.
		"""

		CurrentTry = 0

		while CurrentTry < tries:
			Response = self.__Client.chat.completions.create(model = "gpt-4o", messages = [{"role": "user", "content": request}])
			Response: str = Response.choices[0].message.content.strip()

			if Response.startswith("You have reached your request limit for the hour."): continue
			if type(Response) != str or not Response: continue

			if Response == "Ваше сообщение не понятно.": 
				CurrentTry += 1
				continue

			if not self.IsTextRussian(Response):
				CurrentTry += 1
				logging.warning(f"Иноязычная речь: {Response}")
				continue

			Replaces = {
				"\n": "\n\n",
				"«": "«<b>",
				"»": "</b>»"
			}

			for Substring in Replaces.keys(): Response = Response.replace(Substring, Replaces[Substring])
			return Response
		
	def PreparationText(self, user_text) -> tuple[str, bool]:
		
		texts = [
			_("Ну что ж, давай погрузимся в тайны Таро..."),
			_("Ухх.. Хороший какой вопрос! Сейчас посмотрим..."),
			_("Спасибо, очень интересно! Сейчас разложим карты..."),
			_("Ничего себе! Вот это я понимаю запрос к картам..."),
			_("Вот это ситуация! Довольно любопытный расклад...")
		]
		random_text = self.__choice_text(texts)
		Request = f"У тебя есть шаблон: {random_text} [question]."
		Request += f"Тебе задали вопрос: {user_text}. Выведи шаблон учитывая, что спрашивающий имеет ввиду не тебя в вопросе, не добавляй восклицательный знак и двоеточие, а также не используй форматирование. Согласуй, учитывая правила русского языка."
		Request += "Если вопрос является бессмысленным набором символов - выведи следующую строку: \"Ваше сообщение не понятно.\" не добавляя ничего другого."
		Text_response = self.generate_text(Request, 10)

		if not Text_response: 
			Text_response = "Ваше сообщение не совсем понятно. Если у вас есть вопрос или тема, которую вы хотите обсудить, пожалуйста, напишите об этом. Я с радостью помогу вам!"
			Result = False
		else: Result = True
			
		logging.info(f"Текст вопроса: {user_text},\nтекст для пользователя: {Text_response}")
		return Text_response, Result

	def GenerationCardLayout(self, number: str, card: str, user_text: str) -> str:

		Request = f"Проанализируй эти данные: {number}, {card} и {user_text} и предоставь ответ в следующем формате:"
		Request += f"{number}, «{card}», может указывать на [помести сюда своё мнение о том, на что может указывать значение карты о заданном вопросе]."
		Request += "Не более 250 символов в тексте. Не меняй первые два словосочетания!!!"

		Text_response = self.generate_text(Request, 10)
		logging.info(f"Текст вопроса: {user_text},\nтекст для пользователя: {Text_response}")

		return Text_response
	
	def GenerationOutcome(self, First: str, Second: str, Three: str, user_text: str):
		texts = [
			_("В целом"),
			_("Таким образом"),
			_("Как разультат"),
			_("В итоге")
		]
		random_text = self.__choice_text(texts)
		Request = f"Проанализируй эти карты Таро: {First}, {Second} и {Three} и предоставь ответ в следующем формате на вопрос {user_text}:"
		Request += f"{random_text}, карты показывают [помести сюда своё мнение о том, на что могут показывать указанные значения карт о заданном вопросе]."
		Request += "Не более 250 символов в тексте. Не меняй первые два слова!!! Не упоминай названия карт!!!"
			
		Text_response = self.generate_text(Request, 10)	
		logging.info(f"Текст вопроса: {user_text},\nтекст для пользователя: {Text_response}")

		Text = (
			"<b>" + _("Заключение:") + "</b>",
		  	Text_response,
		  	"<i>" + _("Если желаете рассмотреть ваши вопросы более серьезно, то рекомендуем взять расклад у нашего Таро Мастера, где уже живой опытный эксперт даст вам действующие подсказки и советы!") + "</i>"
		)

		return Text