from dublib.TelebotUtils.Cache import TeleCache
from dublib.Methods.Filesystem import ReadJSON, ListDir
from dublib.TelebotUtils.Users import UserData

from Source.Modules.solid_g4f.Connection.API import Requestor, Options
from Source.Functions import _
from Source.UI.OnlineLayout import end_layout

from dataclasses import dataclass
import telebot
import random
import logging
from telebot import types

@dataclass(frozen = True)
class SpecificQuestion:
	type: str | None
	reaction: str | None
	main_variant: str | None
	alt_variants: tuple[str] | None

	def print(self):
		print("Type:", self.type)
		print("Reaction:", self.reaction)
		print("Main variant:", self.main_variant)
		print("Alternative variants:", self.alt_variants)

class NeuroRequestor:
	"""Обработчик запросов к нейросети."""

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __FormatCardLayout(self, text: str) -> str | None:
		"""
		Форматирует ответ нейросети с раскладом.

		:param text: Текст ответа.
		:type text: str
		:return: Форматированный ответ или `None` при отсутствии оного.
		:rtype: str | None
		"""

		if not text: return
		Replaces = {
			"\n": "\n\n",
			"«": "«<b>",
			"»": "</b>»"
		}

		for Substring in Replaces.keys(): text = text.replace(Substring, Replaces[Substring])

		return text

	def __FormatPreparation(self, text: str) -> str | None:
		"""
		Форматирует ответ нейросети с вступлением.

		:param text: Текст ответа.
		:type text: str
		:return: Форматированный ответ или `None` при отсутствии оного.
		:rtype: str | None
		"""

		if not text: return
		Strings = (
			"Хороший какой вопрос.",
			"Спасибо, очень интересно.",
			"Ничего себе.",
			"Вот это ситуация."
		)

		for String in Strings:
			if String in text: text.replace(String, String[:-1] + "!") 

		return text

	def __ReadCardsData(self) -> dict[str, tuple]:
		"""
		Считывает данные карт.

		:return: Словарь, ключём в котором является название комплекта, а значением набор карт в комплекте.
		:rtype: dict[str, tuple]
		"""

		Data = dict()
		for Set in ListDir("Materials/Layouts"): Data[Set] = tuple(ReadJSON(f"Materials/Layouts/{Set}/cards.json"))

		return Data
	
	def __ParseQuestionData(self, question: str) -> SpecificQuestion:

		alt_variants = list()
		handler = None
		reaction = None
		main_variant = None

		words = question.split(" ")

		for word in words:
			if not word: continue

			if word in ("или", "между"):
		
				response: str | None = self.__Generator.generate(self.build_training_request(question)).json["text"]

				if response.count(";"):
					handler = "answer"
					variants = response.strip().split(";")

					for Index in range(len(variants)): variants[Index] = variants[Index].strip()

					if variants: 
						main_variant = random.choice(variants)
						alt_variants = variants
						alt_variants.remove(main_variant)
						alt_variants = tuple(alt_variants)

			elif word == "ли":
				handler = "reaction"
				reaction = random.choice(("нейтральному", "положительному", "положительному", "негативному"))

		if main_variant: reaction = None
					
		return SpecificQuestion(handler, reaction, main_variant, alt_variants)

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, bot: telebot.TeleBot, cacher: TeleCache):
		"""
		Обработчик запросов к нейросети.

		:param bot: Бот Telegram
		:type bot: telebot.TeleBot
		:param cacher: Менеджер кэша Telegram.
		:type cacher: TeleCache
		"""

		self.__Bot = bot
		self.__Cacher = cacher

		self.__Data: dict[str, tuple] = self.__ReadCardsData()

		RequestOptions = Options()
		RequestOptions.set_max_length(300)
		RequestOptions.set_timeout(60)
		RequestOptions.set_tries(10)
		RequestOptions.set_model("gpt-4")

		self.__Generator = Requestor(RequestOptions)

	def send_layout(self, user: UserData, question: str):
		"""
		Отправляет расклад пользователю.

		:param user: Данные пользователя.
		:type user: UserData
		:param question: Текст вопроса.
		:type question: str
		"""

		reaction = None

		user.set_property("Generation", True)
		Collection = random.choice(tuple(self.__Data.keys()))

		question_data = self.__ParseQuestionData(question)
		question_data.print()
		if question_data.type == "reaction": reaction = question_data.main_variant
		
		PreparationRequest = self.build_preparation_request(question)
		FirstCardRequest = self.build_card_layout_request(self.__Data[Collection][0], "Первая карта", question, reaction, question_data.main_variant, question_data.alt_variants)
		SecondCardRequest = self.build_card_layout_request(self.__Data[Collection][1], "Вторая карта", question, reaction, question_data.main_variant, question_data.alt_variants)
		ThirdCardRequest = self.build_card_layout_request(self.__Data[Collection][2], "Третья карта", question, reaction, question_data.main_variant, question_data.alt_variants)
		OutcomeRequest = self.build_outcome_request(self.__Data[Collection][0], self.__Data[Collection][1], self.__Data[Collection][2], question, reaction, question_data.main_variant, question_data.alt_variants)

		RequestsCollection = {
			2: FirstCardRequest,
			3: SecondCardRequest,
			4: ThirdCardRequest
		}

		for Index in range(1, 5):
			self.__Bot.send_chat_action(user.id, action = "typing")
			ImageCache = self.__Cacher.get_real_cached_file(f"Materials/Layouts/{Collection}/{Index}.jpg", types.InputMediaPhoto)

			if Index == 1:
				Text: str = self.__Generator.generate(PreparationRequest).json["text"]
				if Text: Text = Text.replace("*", "")
				Text = self.__FormatPreparation(Text)

				if Text and Text != "Ваше сообщение не понятно.": 
					self.__Bot.send_photo(
						chat_id = user.id,
						photo = ImageCache.file_id,
						caption = Text,
						parse_mode = "HTML"
					)

					logging.info(f"{user.id, Text}")

				else:
					self.__Bot.send_message(
						chat_id = user.id,
						text = _("Ваше сообщение не совсем понятно. Если у вас есть вопрос или тема, которую вы хотите обсудить, пожалуйста, напишите об этом. Я с радостью помогу вам!"),
						parse_mode = "HTML" 
					)
					user.set_property("Generation", False)

					logging.info(f"{user.id}, Ваше сообщение не совсем понятно. Если у вас есть вопрос или тема, которую вы хотите обсудить, пожалуйста, напишите об этом. Я с радостью помогу вам!")
					return

			else:
				Response = self.__Generator.generate(RequestsCollection[Index])
				Text: str | None = Response.json["text"]
				
				if Text: Text = Text.replace("*", "")
				else: logging.error(Response.json)

				Text = self.__FormatCardLayout(Text)
				self.__Bot.send_photo(
					chat_id = user.id,
					photo = ImageCache.file_id,
					caption = Text,
					parse_mode = "HTML" 
				)
				logging.info(f"{user.id, Text}")

		Text: str = self.__Generator.generate(OutcomeRequest).json["text"]
		if Text: Text = Text.replace("*", "")
		Outcome = (
			"<b>" + _("Заключение:") + "</b>",
		  	Text + "\n",
		  	"<i>" + _("Если желаете рассмотреть ваши вопросы более детально, то рекомендуем вам взять расклад у нашего <b>Таро Мастера</b>. Это живой и опытный эксперт, который даст вам самые действенные подсказки и советы!") + "</i>"
		)
		self.__Bot.send_message(
			chat_id = user.id,
			text = "\n".join(Outcome),
			parse_mode = "HTML",
			reply_markup = end_layout()
		)
		user.set_property("Generation", False)
		logging.info(f"{user.id, "\n".join(Outcome)}")

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ ПОСТРОЕНИЯ ЗАПРОСОВ <<<<< #
	#==========================================================================================#
	
	def build_training_request(self, question: str) -> str:
		"""
		Генерирует варианты ответов на вопрос разделяя их точкой с запятой.

		:param question: Вопрос пользователя.
		:type question: str
		:return: Текст запроса.
		:rtype: str
		"""

		Request = f"Тебе задали вопрос: {question}."
		Request += "Перечисли варианты из этого вопроса, если они есть, в именительном падеже, разделяя точкой с запятой, не добавляй форматирования и ничего лишнего."
		
		return Request
	
	def build_preparation_request(self, question: str) -> str:
		"""
		Строит текст первого запроса.

		:param question: Вопрос пользователя.
		:type question: str
		:return: Текст запроса.
		:rtype: str
		"""

		Starts = (
			_("Ну что ж, давай погрузимся в тайны Таро..."),
			_("Ухх.. Хороший какой вопрос! Сейчас посмотрим..."),
			_("Спасибо, очень интересно! Сейчас разложим карты..."),
			_("Ничего себе! Вот это я понимаю запрос к картам..."),
			_("Вот это ситуация! Довольно любопытный расклад...")
		)
		Start = random.choice(Starts)
		Request = f"У тебя есть шаблон: {Start} [question]. "
		Request += f"Тебе задали вопрос: \"{question}\". Выведи шаблон и подставь вопрос. Согласуй вопрос с шаблоном, поставь во второе лицо, учитывай правила русского языка. "
		Request += "Если вопрос является бессмысленным набором символов или непонятен тебе, выведи следующую строку: \"Ваше сообщение не понятно.\", не добавляя ничего другого. "
		
		return Request

	def build_card_layout_request(self, card_name: str, card_number: str, question: str, reaction: str | None = None, answer: str | None = None, alt_variants: tuple[str] | None = None) -> str:
		"""
		Строит текст запроса для конкретной карты.

		:param card_name: Имя карты.
		:type card_name: str
		:param card_number: Номер карты.
		:type card_number: str
		:param question: Текст вопроса.
		:type question: str
		:param reaction: тип реакции, defaults to None
		:type reaction: str | None, optional
		:return: Текст запроса.
		:rtype: str
		"""

		Request = f"Проанализируй эти данные: номер карты в раскладе - \"{card_number}\", тип карты - \"{card_name}\", вопрос пользователя - \"{question}\" и предоставь ответ в следующем формате: "
		Request += f"{card_number}, «{card_name}», [помести сюда ответ исходя из трактовки карты таро {card_name}]. "

		if answer:
			
			match card_number:

				case "Первая карта":
					Request += "Только общая характеристика внутреннего мира или характера вопрошающего. "

				case "Вторая карта": 
					if alt_variants: Request += f"Аргументируй, почему карта не советует следующий вариант: " + random.choice(alt_variants) + "." + "При необходимости "

				case "Третья карта":
					Request += f"Аргументируй, почему карта советует следующий вариант: {answer} "

			# Request += f"Склоняй к такому ответу на вопрос \"{answer}\". "

		if reaction and not answer: Request += f"Склоняйся к {reaction} ответу на вопрос. "
		Request += "Не более 250 символов в тексте. Сделай свой ответ уникальным и неповторимым."

		return Request
	
	def build_outcome_request(self, first_card: str, second_card: str, third_card: str, question: str, reaction: str | None = None, answer: str | None = None, alt_variants: list[str] | None = None) -> str:
		"""
		Строит текст запроса для резюмирования расклада.

		:param first_card: Первая карта.
		:type first_card: str
		:param second_card: Вторая карта.
		:type second_card: str
		:param third_card: Третья карта.
		:type third_card: str
		:param question: Вопрос пользователя.
		:type question: str
		:param reaction: тип реакции, defaults to None
		:type reaction: str | None, optional
		:return: Текст запроса.
		:rtype: str
		"""

		Starts = [
			_("В целом"),
			_("Таким образом"),
			_("Как разультат"),
			_("В итоге")
		]

		Start = random.choice(Starts)
		Request = f"Проанализируй эти карты Таро: {first_card}, {second_card}, {third_card} и предоставь ответ в следующем формате на вопрос {question}: "
		Request += f"{Start}, [помести сюда резюмированное значение карт Таро в заданном вопросе]. "
		if reaction and not answer: Request += f"Склоняйся к {reaction} ответу на вопрос. "
		elif answer: Request += f"Склоняй к такому ответу на вопрос \"{answer}\". Добавь аргументы, почему твой ответ на вопрос именно такой. Сделай свой ответ уникальным и неповторимым. "
		Request += "Не более 250 символов в тексте."
			
		return Request