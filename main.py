from telebot import types
from dublib.Methods.JSON import ReadJSON
from dublib.TelebotUtils import UsersManager
import telebot
import os
from Source.InlineKeyboards import InlineKeyboards
from Source.ReplyKeyboards import ReplyKeyboards
from Source.Cards import Cards
from dublib.Polyglot import Markdown
from dublib.Methods.System import Clear

Settings = ReadJSON("Settings.json")

Bot = telebot.TeleBot(Settings["token"])
usermanager = UsersManager("Data/Users")
InlineKeyboard = InlineKeyboards()
ReplyKeyboard = ReplyKeyboards()
Card = Cards(Bot, InlineKeyboard)

Clear()

@Bot.message_handler(commands=["start"])
def ProcessCommandStart(Message: types.Message):
	User = usermanager.auth(Message.from_user)
	Message = Bot.send_message(
		Message.chat.id,
		text = "Тестовый текст для меню.",
		reply_markup = InlineKeyboard.SendMainMenu()
	)

	Bot.send_message(
		Message.chat.id,
		text = "Тестовый текст для кнопки поделиться с друзьями.",
		reply_markup = ReplyKeyboard.Share())
	
	
@Bot.message_handler(content_types = ["text"], regexp = "📢 Поделиться с друзьями")
def ProcessShareWithFriends(Message: types.Message):
	User = usermanager.auth(Message.from_user)

	Bot.send_photo(
		Message.chat.id, 
		photo = Settings["qr_id"],
		caption = '@Taro100\\_bot\n@Taro100\\_bot\n@Taro100\\_bot\n\nТаробот \\| Значения карт \\| Карта дня\nБот, который открывает магию карт абсолютно для каждого ✨️', 
		reply_markup = ReplyKeyboard.Share(),
		parse_mode = "MarkDownV2"
		)
	
	
@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("Card_Day"))
def InlineButtonCardDay(Call: types.CallbackQuery):
	User = usermanager.auth(Call.from_user)
	InstantCard = Card.GetInstantCard()
	if InstantCard:
		Bot.send_photo(
						Call.message.chat.id,
						photo = InstantCard["photo"],
						caption = InstantCard["text"]
					)
	else:
		Photo, Text = Card.GetCard()
		Message = Bot.send_photo(
						Call.message.chat.id,
						photo = open(f"{Photo}", "rb"),
						caption = Text
					)
		Card.AddCard(Message.photo[0].file_id)

	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("Value_Card"))
def InlineButtonValueCard(Call: types.CallbackQuery):
	User = usermanager.auth(Call.from_user)
	Message = Bot.send_message(
						Call.message.chat.id,
						text = "Тестовый текст.",
						reply_markup = InlineKeyboard.SendTypeCard()
						)
	
	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("Cups"))
def InlineButtonСups(Call: types.CallbackQuery):
	User = usermanager.auth(Call.from_user)
	if "_" in Call.data:
		Card.SendCardValues(Call, User)
	else:
		Bot.edit_message_reply_markup(Call.message.chat.id, Call.message.id, reply_markup = InlineKeyboard.SendFirstСups())
	
	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("Swords"))
def InlineButtonSwords(Call: types.CallbackQuery):
	User = usermanager.auth(Call.from_user)
	if "_" in Call.data:
		Card.SendCardValues(Call, User)
	else:
		Bot.edit_message_reply_markup(Call.message.chat.id, Call.message.id, reply_markup = InlineKeyboard.SendFirstSwords())

	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("Wands"))
def InlineButtonWands(Call: types.CallbackQuery):
	User = usermanager.auth(Call.from_user)
	if "_" in Call.data:
		Card.SendCardValues(Call, User)
	else:
		Bot.edit_message_reply_markup(Call.message.chat.id, Call.message.id, reply_markup = InlineKeyboard.SendFirstWands())

	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("Pentacles"))
def InlineButtonPentacles(Call: types.CallbackQuery):
	User = usermanager.auth(Call.from_user)
	if "_" in Call.data:
		Card.SendCardValues(Call, User)
	else:
		Bot.edit_message_reply_markup(Call.message.chat.id, Call.message.id, reply_markup = InlineKeyboard.SendFirstPentacles())
	
	Bot.answer_callback_query(Call.id)


@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("Arcanas"))
def InlineButtonArcanas(Call: types.CallbackQuery):
	User = usermanager.auth(Call.from_user)
	if "_" in Call.data:
		Card.SendCardValues(Call, User)
	else:
		Bot.edit_message_reply_markup(Call.message.chat.id, Call.message.id, reply_markup = InlineKeyboard.SendFirstArcanas())
	
	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("Back"))
def InlineButtonBack(Call: types.CallbackQuery):
	User = usermanager.auth(Call.from_user)
	if "_" not in Call.data: pass
	Target = Call.data.split("_")[-1]
	try: Bot.edit_message_caption(caption= "", chat_id = Call.message.chat.id, message_id = Call.message.id, reply_markup = InlineKeyboard.ChoiceFunction(Target))
	except KeyError: 
		Bot.delete_message(Call.message.chat.id, Call.message.id)
		Bot.send_message()
	except:
		Bot.edit_message_reply_markup(Call.message.chat.id, Call.message.id, reply_markup = InlineKeyboard.ChoiceFunction(Target))

	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("Further"))
def InlineButtonFuther(Call: types.CallbackQuery):
	User = usermanager.auth(Call.from_user)
	Target = Call.data.split("_")[-1]
	Bot.edit_message_reply_markup(Call.message.chat.id, Call.message.id, reply_markup = InlineKeyboard.ChoiceFunction(Target))
	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("GeneralMeaning"))
def InlineButtonGeneralMeaning(Call: types.CallbackQuery):
	User = usermanager.auth(Call.from_user)
	Bot.delete_message(Call.message.chat.id, Call.message.id)
	Card = User.get_property("Current_place")

	ID = Card.split("_")[-1]
	Type = Card.split("_")[0]

	for folder2 in os.listdir(f"Materials/Values/{Type}"):
		if folder2.split(".")[0] == ID:
			with open(f"Materials/Values/{Type}/{folder2}/1.txt") as file:
				FirstString = file.readline()
				Text = file.read()
				
				MarkdownText = Markdown(Text).escaped_text
				MarkdownString =  "*" + Markdown(FirstString).escaped_text + "*"
				FinalText = MarkdownString + MarkdownText +"\n\n*С любовью, @taro100\\_bot\\!*"

				Bot.send_photo(
				Call.message.chat.id, 
				open(f"Materials/Values/{Type}/{folder2}/image.jpg", "rb"), 
				caption = FinalText, 
				parse_mode = "MarkdownV2",
				reply_markup = InlineKeyboard.SendBack() 
			)
	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("PersonalState"))
def InlineButtonArcanas(Call: types.CallbackQuery):
	User = usermanager.auth(Call.from_user)
	folder = ""
	Bot.delete_message(Call.message.chat.id, Call.message.id)
	Card = User.get_property("Current_place")

	ID = Card.split("_")[-1]
	Type = Card.split("_")[0]

	folder = None
	if Type == "Сups": folder = "Materials/Values/Кубки"
	if Type == "Swords": folder = "Materials/Values/Мечи"
	if Type == "Wands": folder = "Materials/Values/Жезлы"
	if Type == "Pentacles": folder = "Materials/Values/Пентакли"
	if Type == "Arcanas": folder = "Materials/Values/Старшие арканы"


	for folder2 in os.listdir(folder):
		if folder2.split(".")[0] == ID:
			with open(f"{folder}/{folder2}/2.txt") as file:
				FirstString = file.readline()
				Text = file.read()
				
				MarkdownText = Markdown(Text).escaped_text
				MarkdownString =  "*" + Markdown(FirstString).escaped_text + "*"
				FinalText = MarkdownString + MarkdownText +"\n\n*С любовью, @taro100\\_bot\\!*"

				Bot.send_photo(
				Call.message.chat.id, 
				open(f"{folder}/{folder2}/image.jpg", "rb"), 
				caption = FinalText, 
				parse_mode = "MarkdownV2",
				# reply_markup =  
			)
	Bot.answer_callback_query(Call.id)


@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("Order_Layout"))
def InlineButtonRemoveReminder(Call: types.CallbackQuery):
	User = usermanager.auth(Call.from_user)
	Bot.edit_message_reply_markup(Call.message.chat.id, Call.message.id, reply_markup = InlineKeyboard.SendOrderLayout())
	
	Bot.answer_callback_query(Call.id)

Bot.infinity_polling()

