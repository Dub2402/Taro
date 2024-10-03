from telebot import types
from dublib.Methods.JSON import ReadJSON
from dublib.TelebotUtils import UsersManager
import telebot
from Source.InlineKeyboards import InlineKeyboards
from Source.ReplyKeyboards import ReplyKeyboards
from Source.Cards import Cards

Settings = ReadJSON("Settings.json")

Bot = telebot.TeleBot(Settings["token"])
Manager = UsersManager("Data/Users")
InlineKeyboard = InlineKeyboards()
ReplyKeyboard = ReplyKeyboards()
Card = Cards()

@Bot.message_handler(commands=["start"])
def ProcessCommandStart(Message: types.Message):
	User = Manager.auth(Message.from_user)
	Bot.send_message(
		Message.chat.id,
		text = "Тестовый текст.",
		reply_markup = InlineKeyboard.SettingsMenu())
	Bot.send_message(
		Message.chat.id,
		text = "Тестовый текст.",
		reply_markup = ReplyKeyboard.AddMenu())
	
@Bot.message_handler(content_types = ["text"], regexp = "📢 Поделиться с друзьями")
def ProcessShareWithFriends(Message: types.Message):
	User = Manager.auth(Message.from_user)

	Bot.send_photo(
		Message.chat.id, 
		photo = Settings["qr_id"],
		caption = '@Taro100\\_bot\n@Taro100\\_bot\n@Taro100\\_bot\n\nТаробот \\| Значения карт \\| Карта дня\nБот, который открывает магию карт абсолютно для каждого ✨️', 
		reply_markup = ReplyKeyboard.AddMenu(),
		parse_mode = "MarkDownV2"
		)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("Card_Day"))
def InlineButtonRemoveReminder(Call: types.CallbackQuery):
	User = Manager.auth(Call.from_user)
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
def InlineButtonRemoveReminder(Call: types.CallbackQuery):
	User = Manager.auth(Call.from_user)
	
	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("Order_Layout"))
def InlineButtonRemoveReminder(Call: types.CallbackQuery):
	User = Manager.auth(Call.from_user)
	
	Bot.answer_callback_query(Call.id)

Bot.infinity_polling()

