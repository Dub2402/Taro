from telebot import types
from dublib.Methods.JSON import ReadJSON
from dublib.TelebotUtils import UsersManager
import telebot
from Source.InlineKeyboards import InlineKeyboards
from Source.ReplyKeyboards import ReplyKeyboards
from Source.Cards import Cards
from Source.MessagesManager import MessagesManager

Settings = ReadJSON("Settings.json")

Bot = telebot.TeleBot(Settings["token"])
usermanager = UsersManager("Data/Users")
InlineKeyboard = InlineKeyboards()
ReplyKeyboard = ReplyKeyboards()
Card = Cards()
messagemanager = MessagesManager()

@Bot.message_handler(commands=["start"])
def ProcessCommandStart(Message: types.Message):
	User = usermanager.auth(Message.from_user)
	DeleteMessage = Bot.send_message(
		Message.chat.id,
		text = "Тестовый текст для меню.",
		reply_markup = InlineKeyboard.SendMainMenu()
	)

	Bot.send_message(
		Message.chat.id,
		text = "Тестовый текст для кнопки поделиться с друзьями.",
		reply_markup = ReplyKeyboard.Share())
	messagemanager.AddDelMessages(User, DeleteMessage.id)
	
	
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
	DeleteMessage = Bot.send_message(
						Call.message.chat.id,
						text = "Тестовый текст.",
						reply_markup = InlineKeyboard.SendTypeCard()
						)
	
	messagemanager.DelListMessages(User, Bot, Call)
	messagemanager.AddDelMessages(User, DeleteMessage.id)

	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("Сups"))
def InlineButtonСups(Call: types.CallbackQuery):
	User = usermanager.auth(Call.from_user)
	if "_" in Call.data:
		CardID = Call.data.split("_")[-1]
		DeleteMessage = Bot.send_message(
							Call.message.chat.id,
							text = f"{Call.data}{CardID}"
							)
	else:
		DeleteMessage = Bot.send_message(
							Call.message.chat.id,
							text = "Тестовый текст.",
							reply_markup = InlineKeyboard.SendFirstСups()
							)
		
		messagemanager.DelListMessages(User, Bot, Call)
		messagemanager.AddDelMessages(User, DeleteMessage.id)
	Bot.answer_callback_query(Call.id)


@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("Swords"))
def InlineButtonSwords(Call: types.CallbackQuery):
	User = usermanager.auth(Call.from_user)
	if "_" in Call.data:
		CardID = Call.data.split("_")[-1]
		DeleteMessage = Bot.send_message(
							Call.message.chat.id,
							text = f"{Call.data}{CardID}"
							)
	else:
		DeleteMessage = Bot.send_message(
							Call.message.chat.id,
							text = "Тестовый текст.",
							reply_markup = InlineKeyboard.SendFirstSwords()
							)
		
		messagemanager.DelListMessages(User, Bot, Call)
		messagemanager.AddDelMessages(User, DeleteMessage.id)
	Bot.answer_callback_query(Call.id)


@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("Wands"))
def InlineButtonWands(Call: types.CallbackQuery):
	User = usermanager.auth(Call.from_user)
	if "_" in Call.data:
		CardID = Call.data.split("_")[-1]
		DeleteMessage = Bot.send_message(
							Call.message.chat.id,
							text = f"{Call.data}{CardID}"
							)
	else:
		DeleteMessage = Bot.send_message(
							Call.message.chat.id,
							text = "Тестовый текст.",
							reply_markup = InlineKeyboard.SendFirstWands()
							)
		
		messagemanager.DelListMessages(User, Bot, Call)
		messagemanager.AddDelMessages(User, DeleteMessage.id)
	Bot.answer_callback_query(Call.id)


@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("Pentacles"))
def InlineButtonPentacles(Call: types.CallbackQuery):
	User = usermanager.auth(Call.from_user)
	if "_" in Call.data:
		CardID = Call.data.split("_")[-1]
		DeleteMessage = Bot.send_message(
							Call.message.chat.id,
							text = f"{Call.data}{CardID}"
							)
	else:
		DeleteMessage = Bot.send_message(
							Call.message.chat.id,
							text = "Тестовый текст.",
							reply_markup = InlineKeyboard.SendFirstPentacles()
							)
		
		messagemanager.DelListMessages(User, Bot, Call)
		messagemanager.AddDelMessages(User, DeleteMessage.id)
	Bot.answer_callback_query(Call.id)


@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("Arcanas"))
def InlineButtonArcanas(Call: types.CallbackQuery):
	User = usermanager.auth(Call.from_user)
	if "_" in Call.data:
		CardID = Call.data.split("_")[-1]
		DeleteMessage = Bot.send_message(
							Call.message.chat.id,
							text = f"{Call.data}{CardID}"
							)
	else:
		DeleteMessage = Bot.send_message(
							Call.message.chat.id,
							text = "Тестовый текст.",
							reply_markup = InlineKeyboard.SendFirstArcanas()
							)
		
		messagemanager.DelListMessages(User, Bot, Call)
		messagemanager.AddDelMessages(User, DeleteMessage.id)
	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("Back"))
def InlineButtonArcanas(Call: types.CallbackQuery):
	User = usermanager.auth(Call.from_user)
	Target = Call.data.split("_")[-1]

	DeleteMessage = Bot.send_message(
						Call.message.chat.id,
						text = "Тестовый текст.",
						reply_markup = InlineKeyboard.ChoiceFunction(Target)
						)
	
	messagemanager.DelListMessages(User, Bot, Call)
	messagemanager.AddDelMessages(User, DeleteMessage.id)
	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("Further"))
def InlineButtonArcanas(Call: types.CallbackQuery):
	User = usermanager.auth(Call.from_user)
	Target = Call.data.split("_")[-1]

	DeleteMessage = Bot.send_message(
						Call.message.chat.id,
						text = "Тестовый текст.",
						reply_markup = InlineKeyboard.ChoiceFunction(Target)
						)
	
	messagemanager.DelListMessages(User, Bot, Call)
	messagemanager.AddDelMessages(User, DeleteMessage.id)
	Bot.answer_callback_query(Call.id)



@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("Order_Layout"))
def InlineButtonRemoveReminder(Call: types.CallbackQuery):
	User = usermanager.auth(Call.from_user)
	
	Bot.answer_callback_query(Call.id)



Bot.infinity_polling()

