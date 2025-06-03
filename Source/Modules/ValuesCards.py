from dublib.TelebotUtils import UsersManager, UserData
from dublib.TelebotUtils.Master import TeleMaster
from dublib.TelebotUtils.Cache import TeleCache, RealCachedFile
from dublib.Engine.GetText import _
from dublib.Methods.Filesystem import ReadJSON

from Source.Functions import IsSubscripted

from telebot import TeleBot, types
import os

#==========================================================================================#
# >>>>> РАБОТА С НАЗВАНИЯМИ КАРТ <<<<< #
#==========================================================================================#
 
class Titles:
	"""Работа с названими карт."""

	def generate_taro_name_section(type_card: str) -> str:
		"""
		Получение заголовка для секций карт.

		:param type_card: Cups, Swords, Wands, Pentacles, Arcanas
		:type type_card: str
		:return: МАСТЬ КУБКОВ, МАСТЬ МЕЧЕЙ, МАСТЬ ЖЕЗЛОВ, МАСТЬ ПЕНТАКЛЕЙ, СТАРШИЕ АРКАНЫ
		:rtype: str
		"""

		determinations = {
			"Cups":  "МАСТЬ КУБКОВ",
			"Swords": "МАСТЬ МЕЧЕЙ",
			"Wands": "МАСТЬ ЖЕЗЛОВ",
			"Pentacles": "МАСТЬ ПЕНТАКЛЕЙ",
			"Arcanas": "СТАРШИЕ АРКАНЫ"
		}

		return determinations[type_card]

	def get_suit_suffix(type_card: str) -> str:
		"""
		Получение части названия для клавиатуры мастей.

		:param type_card: Cups, Swords, Wands, Pentacles
		:type type_card: str
		:return: кубков, мечей, жезлов, пентаклей.
		:rtype: str
		"""

		determinations = {
			"Cups":  "кубков",
			"Swords": "мечей",
			"Wands": "жезлов",
			"Pentacles": "пентаклей"
		}

		return determinations[type_card]

#==========================================================================================#
# >>>>> НАБОР INLINE_KEYBOARDS <<<<< #
#==========================================================================================#

class ValuesCardInlineTemplates:

	def __init__(self):
		"""
		Инициализация.
		"""

		#---> Генерация статических атрибутов.
		#==========================================================================================#

		self.__views = ReadJSON("Data/ValuesCards/Views.json")
		self.__views_minor: list = self.__views["minor"]
		self.__views_major: list = self.__views["major"]

		self.__pages_distribution = {
			1: (0, 7),
			2: (7, 14),
			3: (14, 22)
		}

	def get_page_keyboard(self, value: int) -> int:
		return next((key for key, (start, end) in self.__pages_distribution.items() if start <= value < end), None)

	def sections_cards(self) -> types.InlineKeyboardMarkup:
		"""
		Клавиатура секций карт (кубки, мечи, жезлы, пентакли, старшие арканы.)

		:return: inline-keyboard
		:rtype: types.InlineKeyboardMarkup
		"""

		menu = types.InlineKeyboardMarkup()

		determinations = {
			_("🏆 Кубки"): "Cups",
			_("⚔️ Мечи"): "Swords",
			_("🎋 Жезлы"): "Wands",
			_("🪙 Пентакли"): "Pentacles",
			_("🃏 Старшие арканы"): "Arcanas",
			_("◀️ Назад"): "all_taro"
		}

		for string in determinations.keys(): menu.add(types.InlineKeyboardButton(string, callback_data = determinations[string]), row_width = 1)

		return menu
	
	def generate_view(self, type_card: str, page: int)-> types.InlineKeyboardMarkup:
		"""
		Сгенерированная клавиатура для конкретной масти, включающая генерацию конкретной страницы клавиатуры.

		:param type_card: Секция карт (кубки, мечи, жезлы, пентакли, старшие арканы.).
		:type type_card: str
		:param page: Номер страницы.
		:type page: int
		:return: Inline-keyboard.
		:rtype: types.InlineKeyboardMarkup
		"""

		menu = types.InlineKeyboardMarkup()

		start, end = self.__pages_distribution[page]

		if type_card == "Arcanas": generated_buttons = [types.InlineKeyboardButton(f"{self.__views_major[i]}", callback_data = f"{type_card}_{i}") for i in range(start, end)]
		else: generated_buttons = [types.InlineKeyboardButton(f"{i+1}. {self.__views_minor[i]} {Titles.get_suit_suffix(type_card)}", callback_data = f"{type_card}_{i+1}") for i in range(start, end)]

		menu.add(*generated_buttons, row_width = 1)

		if page == 1:
			menu.add(types.InlineKeyboardButton(_("Далее ▶️"), callback_data = f"generation_view_{type_card}_{2}"))
			menu.add(types.InlineKeyboardButton(_("◀️ Назад"), callback_data = "sections_cards"))

		elif page == 2:

			if type_card != "Arcanas":
				menu.add(types.InlineKeyboardButton(_("◀️ Назад"), callback_data = f"generation_view_{type_card}_{1}"))
				menu.add(types.InlineKeyboardButton(_("⏪️ К мастям"), callback_data = "sections_cards"))
			else:
				menu.add(types.InlineKeyboardButton(_("Далее ▶️"), callback_data = f"generation_view_{type_card}_{3}"))
				menu.add(types.InlineKeyboardButton(_("◀️ Назад"), callback_data = f"generation_view_{type_card}_{1}"))

		else:
			menu.add(types.InlineKeyboardButton(_("◀️ Назад"), callback_data = f"generation_view_{type_card}_{2}"))
			menu.add(types.InlineKeyboardButton(_("⏪️ К мастям"), callback_data = "sections_cards"))

		return menu

	def values_card(self) -> types.InlineKeyboardMarkup:
		"""
		Клавиатура значений карты (Общее значение, Личностное состояние, На глубоком уровне, В работе и карьере, В финансах, В любовной сфере, Состояние здоровья, Перевернутая карта, Назад).

		:return: Inline-keyboard.
		:rtype: types.InlineKeyboardMarkup
		"""

		menu = types.InlineKeyboardMarkup()
	
		determinations = {
			_("1. Общее значение"): "GeneralMeaning",
			_("2. Личностное состояние"): "PersonalState",
			_("3. На глубоком уровне"): "DeepLevel",
			_("4. В работе и карьере"): "WorkCareer",
			_("5. В финансах"): "Finance",
			_("6. В любовной сфере"): "Love",
			_("7. Состояние здоровья"): "HealthStatus",
			_("8. Перевернутая карта"): "Inverted",
			_("◀️ Назад"): "generation_view"
		}

		for string in determinations.keys(): menu.add(types.InlineKeyboardButton(string, callback_data = determinations[string]), row_width = 1)

		return menu
	
	def back(self) -> types.InlineKeyboardMarkup:
		"""
		Клавиатура возвращения к values_card.

		:return: Inline-keyboard.
		:rtype: types.InlineKeyboardMarkup
		"""

		return types.InlineKeyboardMarkup([[types.InlineKeyboardButton(_("Назад"), callback_data = "values_card")]])

#==========================================================================================#
# >>>>> ДЕКОРАТОРЫ <<<<< #
#==========================================================================================#

class Decorators:
	"""Набор декораторов."""

	def __init__(self, values_cards: "ValuesCards"):
		"""
		Инициализация.

		:param values_cards: Основной класс.
		:type values_cards: ValuesCards
		"""

		#---> Генерация динамических атрибутов.
		#==========================================================================================#

		self.__ValuesCards = values_cards

		self.__ValuesCardInlineTemplates = ValuesCardInlineTemplates()
		self.__Cards = Cards()

	def inline_keyboards(self):
		"""Обработка inline_keyboards."""

		@self.__ValuesCards.bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("value_card"))
		def value_card(Call: types.CallbackQuery):
			user = self.__ValuesCards.users.auth(Call.from_user)
			if not IsSubscripted(self.__ValuesCards.masterbot, user, self.__ValuesCards.settings):
				self.__ValuesCards.bot.answer_callback_query(Call.id)
				return

			self.__ValuesCards.bot.edit_message_caption(
				caption = _("<b>ЗНАЧЕНИЕ КАРТ</b>"),
				chat_id = Call.message.chat.id,
				message_id = Call.message.id,
				reply_markup = self.__ValuesCardInlineTemplates.sections_cards(),
				parse_mode = "HTML"
				)
			
			self.__ValuesCards.bot.answer_callback_query(Call.id)

		@self.__ValuesCards.bot.callback_query_handler(func = lambda Callback: Callback.data.startswith(("Cups", "Swords", "Wands", "Pentacles", "Arcanas")))
		def choice_sections_cards(Call: types.CallbackQuery):
			user = self.__ValuesCards.users.auth(Call.from_user)
			print(Call.data)

			if "_" in Call.data:
				self.__Cards.card_and_choice_value(bot = self.__ValuesCards.bot, Call = Call, User = user, inline_keyboard = self.__ValuesCardInlineTemplates, cacher = self.__ValuesCards.cacher)
			else:
				type_card = Call.data

				title = Titles.generate_taro_name_section(type_card)
				self.__ValuesCards.bot.edit_message_caption(
					caption = f"<b>{title}</b>", 
					chat_id = Call.message.chat.id, 
					message_id = Call.message.id, 
					parse_mode = "HTML",
					reply_markup = self.__ValuesCardInlineTemplates.generate_view(type_card, 1)
					)
			
			self.__ValuesCards.bot.answer_callback_query(Call.id)

		@self.__ValuesCards.bot.callback_query_handler(func = lambda Callback: Callback.data in ("GeneralMeaning", "PersonalState", "DeepLevel", "WorkCareer", "Finance", "Love", "HealthStatus", "Inverted"))
		def choice_values_card(Call: types.CallbackQuery):
			user = self.__ValuesCards.users.auth(Call.from_user)
			card_position: str = user.get_property("Current_place")
			type_card, id_card = card_position.split("_")

			determinations = {
				"GeneralMeaning": 1,
				"PersonalState": 2,
				"DeepLevel": 3,
				"WorkCareer": 4,
				"Finance": 5,
				"Love": 6,
				"HealthStatus": 7,
				"Inverted": 8
			}

			for name_card in os.listdir(f"Materials/Values/{type_card}"):
				if name_card.split(".")[0] == id_card:
					with open(f"Materials/Values/{type_card}/{name_card}/{determinations[Call.data]}.txt") as file:
						first_string = file.readline()
						text = file.read().strip()
						ending = _("С любовью, @taro100_bot!")
						final_text = "<b>" + first_string + "</b>\n" + text + f"\n\n<b><i>{ending}</i></b>"
						self.__Cards.send_card_and_value(bot = self.__ValuesCards.bot, Call = Call, User = user, inline_keyboard = self.__ValuesCardInlineTemplates, cacher = self.__ValuesCards.cacher, text = final_text)

			self.__ValuesCards.bot.answer_callback_query(Call.id)

		@self.__ValuesCards.bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("values_card"))
		def values_card(Call: types.CallbackQuery):
			user = self.__ValuesCards.users.auth(Call.from_user)	

			type_card = user.get_property("Current_place").split("_")[0]
			card_name = user.get_property("Card_name")

			if type_card == "Arcanas" and card_name:
				senior_lasso = _("СТАРШИЙ АРКАН")
				self.__ValuesCards.bot.edit_message_caption(caption = f"<b> {senior_lasso} «{card_name}»</b>", chat_id = Call.message.chat.id, message_id = Call.message.id, reply_markup = self.__ValuesCardInlineTemplates.values_card(), parse_mode = "HTML")
			else:
				self.__ValuesCards.bot.edit_message_caption(caption = f"<b>«{card_name}»</b>", chat_id = Call.message.chat.id, message_id = Call.message.id, reply_markup = self.__ValuesCardInlineTemplates.values_card(), parse_mode = "HTML")

			self.__ValuesCards.bot.answer_callback_query(Call.id)

		@self.__ValuesCards.bot.callback_query_handler(func = lambda Callback: Callback.data == "generation_view")
		def back_generation_view_(Call: types.CallbackQuery):
			user = self.__ValuesCards.users.auth(Call.from_user)
		
			type_card, id_card = user.get_property("Current_place").split("_")
			title = Titles.generate_taro_name_section(type_card)

			Animation = self.__ValuesCards.cacher.get_real_cached_file(ReadJSON("Settings.json")["start_animation"], types.InputMediaAnimation)
			if type_card == "Arcanas": 
				id_card = int(self.__Cards.roman_to_arabic(id_card))
				self.__Cards.change_all_message(self.__ValuesCards.bot, media_type = types.InputMediaAnimation, media = Animation.file_id, text = f"<b>{title}</b>", Call = Call, inline_keyboard = self.__ValuesCardInlineTemplates.generate_view(type_card, self.__ValuesCardInlineTemplates.get_page_keyboard(id_card)))
			else: self.__Cards.change_all_message(self.__ValuesCards.bot, media_type = types.InputMediaAnimation, media = Animation.file_id, text = f"<b>{title}</b>", Call = Call, inline_keyboard = self.__ValuesCardInlineTemplates.generate_view(type_card, self.__ValuesCardInlineTemplates.get_page_keyboard(int(id_card) - 1)))
			
			self.__ValuesCards.bot.answer_callback_query(Call.id)

		@self.__ValuesCards.bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("generation_view_"))
		def generation_view(Call: types.CallbackQuery):
			user = self.__ValuesCards.users.auth(Call.from_user)
			type_card, page = Call.data.split("_")[2:]
			
			self.__ValuesCards.bot.edit_message_reply_markup(
				chat_id = Call.message.chat.id,
				message_id = Call.message.id, 
				reply_markup = self.__ValuesCardInlineTemplates.generate_view(type_card, int(page))
			) 
			self.__ValuesCards.bot.answer_callback_query(Call.id)

		@self.__ValuesCards.bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("sections_cards"))
		def types_cards(Call: types.CallbackQuery):
			User = self.__ValuesCards.users.auth(Call.from_user)
			
			self.__ValuesCards.bot.edit_message_caption(caption = _("<b>ЗНАЧЕНИЕ КАРТ</b>"), chat_id = Call.message.chat.id, message_id = Call.message.id, reply_markup = self.__ValuesCardInlineTemplates.sections_cards(), parse_mode = "HTML")
			self.__ValuesCards.bot.answer_callback_query(Call.id)

#==========================================================================================#
# >>>>> РАБОТА С КАРТАМИ <<<<< #
#==========================================================================================#

class Cards:

	def roman_to_arabic(self, index_roman):

		determinations = {
			"0": 0,
			"I": 1,
			"II": 2,
			"III": 3,
			"IV": 4,
			"V": 5,
			"VI": 6,
			"VII": 7,
			"VIII": 8,
			"IX": 9,
			"X": 10,
			"XI": 11,
			"XII": 12,
			"XIII": 13,
			"XIV": 14,
			"XV": 15,
			"XVI": 16,
			"XVII": 17,
			"XVIII": 18,
			"XIX": 19,
			"XX": 20,
			"XXI": 21
		}

		return str(determinations[index_roman])

	def change_all_message(self, bot: TeleBot, media_type: types, media: RealCachedFile, text: str, Call: types.CallbackQuery, inline_keyboard: ValuesCardInlineTemplates):
		try:
			bot.edit_message_media(
				media = media_type(
					media = media,
					caption = text,
					parse_mode = "HTML"
				),
				chat_id = Call.message.chat.id,
				message_id = Call.message.id,
				reply_markup = inline_keyboard
			)
		except ZeroDivisionError:
			pass

	def send_card_and_value(self, bot: TeleBot, Call: types.CallbackQuery, User: UserData, inline_keyboard: ValuesCardInlineTemplates, cacher: TeleCache, text: str = ""):
		bot.edit_message_caption(
			caption = text,
			chat_id = Call.message.chat.id,
			message_id = Call.message.id,
			parse_mode = "HTML",
			reply_markup = inline_keyboard.back()
		)

	def card_and_choice_value(self, bot: TeleBot, Call: types.CallbackQuery, User: UserData, inline_keyboard: ValuesCardInlineTemplates, cacher: TeleCache, text: str = ""):
		Type, card_id = Call.data.split("_")
		print(Type, card_id)
	
		if Type != "Arcanas": User.set_property("Current_place", Call.data)
	
		for filename in os.listdir(f"Materials/Values/{Type}"):
			Index = filename.split(".")[0]
			if Type == "Arcanas": Index = self.roman_to_arabic(Index)
			if Index == card_id:
				Photo = cacher.get_real_cached_file(f"Materials/Values/{Type}/{filename}/image.jpg", types.InputMediaPhoto)

				if Type == "Arcanas": User.set_property("Current_place", "Arcanas_" + filename.split(".")[0])
				CardName = filename.split(".")[1].upper().strip()
				User.set_property("Card_name", CardName)

				if Type == "Arcanas": self.change_all_message(bot = bot, media_type = types.InputMediaPhoto, media = Photo.file_id, text = f"<b>СТАРШИЙ АРКАН «{CardName}»</b>", Call = Call, inline_keyboard = inline_keyboard.values_card())
				else: self.change_all_message(bot = bot, media_type = types.InputMediaPhoto, media = Photo.file_id, text = f"<b>«{CardName}»</b>", Call = Call, inline_keyboard = inline_keyboard.values_card())

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class ValuesCards:

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#
	
	@property
	def masterbot(self) -> TeleMaster:
		"""Мастербот."""

		return self.__masterbot
	
	@property
	def bot(self) -> TeleBot:
		"""Мастербот."""

		return self.__masterbot.bot
	
	@property
	def users(self) -> UsersManager:
		"""Данные пользователей."""

		return self.__users

	@property
	def cacher(self) -> TeleCache:
		"""Менеджер кэша."""

		return self.__cacher
	
	@property
	def settings(self) -> Decorators:
		"""Наcтройки бота."""

		return self.__settings
	
	@property
	def decorators(self) -> Decorators:
		"""Набор декораторов."""

		return self.__Decorators

	def __init__(self, masterbot: TeleMaster, users: UsersManager, cacher: TeleCache, settings: dict):

		#---> Генерация динамических атрибутов.
		#==========================================================================================#

		self.__masterbot = masterbot
		self.__users = users
		self.__cacher = cacher
		self.__settings = settings

		self.__Decorators = Decorators(self)	