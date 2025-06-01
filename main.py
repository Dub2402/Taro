from dublib.TelebotUtils.Cache import TeleCache
from dublib.TelebotUtils import UsersManager
from dublib.TelebotUtils import TeleMaster
from dublib.Engine.GetText import GetText
from dublib.Methods.Filesystem import ReadJSON
from dublib.Methods.System import Clear

from Source.Modules.InternalСaching import InternalCaching
from Source.Modules.EnergyExchange import Exchanger
from Source.Modules.ValuesCards import ValuesCards
from Source.Modules.YesNo import YesNo
from Source.Modules.WordMouth import Mailer

from Source.Core.BlackDictionary import BlackDictionary
from Source.Core.Reader import Reader
from Source.UI.WorkpiecesMessages import WorkpiecesMessages
from Source.UI.AdditionalOptions import Options
from Source.UI.OnlineLayout import Layout
from Source.TeleBotAdminPanel.Core.Moderation import Moderator
from Source.TeleBotAdminPanel import Panel
from Source.InlineKeyboards import InlineKeyboards

from Source.Neurowork import Neurowork
from Source.Functions import IsSubscripted, FindNearest, ChoiceMessage, CacherSending, UpdateThinkCardData, UpdateThinkCardData2, GetNumberCard, update_think_card, delete_thinking_messages

import dateparser
import logging
import os

from datetime import datetime
from threading import Thread
from time import sleep

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
from telebot import types

Settings = ReadJSON("Settings.json")

GetText.initialize("Taro", Settings["language"], "locales")
_ = GetText.gettext

MasterBot = TeleMaster(Settings["token"])
Bot = MasterBot.bot

usermanager = UsersManager("Data/Users")
reader = Reader(Settings)
Cacher = TeleCache()
Cacher.set_options(Settings["token"], Settings["chat_id"])
yes_no = YesNo(MasterBot, Cacher, reader, usermanager, Settings)
neurowork = Neurowork(Bot, Cacher)
mailer = Mailer(MasterBot, usermanager, reader, Cacher, Settings) 
values_cards = ValuesCards(MasterBot, usermanager, Cacher, Settings)
AdminPanel = Panel()
sender = WorkpiecesMessages(Bot)
OnlineLayout = Layout()
AddictionalOptional = Options(MasterBot, usermanager, Settings, sender, Cacher)
EnergyExchanger = Exchanger(Bot, usermanager)
Moderator.initialize(EnergyExchanger.get_unmoderated_mails, EnergyExchanger.moderate_mail)
Thread(target = InternalCaching(Cacher).caching).start()

logging.basicConfig(level = logging.INFO, encoding = "utf-8", filename = "LOGING.log", filemode = "w", force = True,
	format = '%(asctime)s - %(levelname)s - %(message)s',
	datefmt = '%Y-%m-%d %H:%M:%S')

logging.getLogger("pyTelegramBotAPI").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)

scheduler = BackgroundScheduler()

executors = {
	'default': ThreadPoolExecutor(1)
}
scheduler.configure(executors = executors)

scheduler.add_job(mailer.card_day_mailing, 'cron', hour = 0, minute = 0)
scheduler.add_job(mailer.appeals.randomize_days, "cron", day_of_week = "mon", hour = 17, minute = 42)
scheduler.add_job(mailer.letters.randomize_time, "cron", day = "2, 16", hour = 0, minute = 0)
scheduler.add_job(mailer.letters_mailing, "cron", day = "2, 16", hour = "9-21", minute = "*")
scheduler.add_job(update_think_card, 'cron', day_of_week = "mon, wed, fri", hour = 0, minute = 0, args = [usermanager])
scheduler.add_job(EnergyExchanger.push_mails, "cron", day_of_week = "mon", hour = 0, minute = 0)
scheduler.start()

Clear()

AdminPanel.decorators.commands(Bot, usermanager, Settings["password"])

@Bot.message_handler(commands = ["start"])
def ProcessCommandStart(Message: types.Message):
	user = usermanager.auth(Message.from_user)

	Message = Bot.send_message(
		Message.chat.id,
		text = _("<b>Добро пожаловать в Таробот!</b>\n\nСамый большой бот для Таро-гаданий в Telegram!\n\nЗадай боту любой❓️вопрос и наслаждайся ответом!"),
		parse_mode = "HTML"
	)

	Message = Bot.send_animation(
		Message.chat.id,
		animation = Cacher.get_real_cached_file(Settings["start_animation"], types.InputMediaAnimation).file_id,
		caption = None,
		reply_markup = InlineKeyboards.main_menu(),
		parse_mode = "HTML"
	)

	user.set_property("Current_place", None, force = False)
	user.set_property("Card_name", None, force = False)
	user.set_property("Question", None)
	user.set_property("Generation", False)
	user.set_property("Subscription", None, force = False)
	user.clear_temp_properties()

	if not IsSubscripted(MasterBot, user, Settings): return    
	
@Bot.message_handler(commands = ["card"])
def ProcessCommandCard(Message: types.Message):
	user = usermanager.auth(Message.from_user)
	if not IsSubscripted(MasterBot, user, Settings): return

	if len(Message.text.split(" ")) == 2:
		user_date = Message.text.split(" ")[-1]
		try:
			datekey = dateparser.parse(user_date, settings = {'DATE_ORDER': 'DMY','STRICT_PARSING': True}).strftime("%d.%m.%Y")
			with open(f"Materials/Texts/{datekey}.txt") as file:
				text = file.read()

			Bot.send_video(
				chat_id = Message.chat.id,
				video = Cacher.get_real_cached_file(f"Materials/Video/{datekey}.mp4", types.InputMediaVideo).file_id,
				caption = text, 
				parse_mode = "HTML"
				)
			
		except FileNotFoundError: 
			Bot.send_message(
				Message.chat.id,
				text = _("Такой даты пока не существует.")
				)
		except:
			Bot.send_message(
				Message.chat.id,
				text = _("Команда введена неправильно. Формат команды: /card 21.01.2025")
				)

@Bot.message_handler(commands = ["mailset"])
def process_command_mailset(Message: types.Message):
	"""
	Настройка рассылки.

	:param Message: объект класса; command /mailset
	:type Message: types.Message
	"""

	user = usermanager.auth(Message.from_user)
	if not IsSubscripted(MasterBot, user, Settings): return
	sender.settings_mailing(Message, action = "restart")

@Bot.message_handler(commands = ["share"])
def ProcessShareWithFriends(Message: types.Message):
	user = usermanager.auth(Message.from_user)
	if not IsSubscripted(MasterBot, user, Settings): return

	Bot.send_photo(
		Message.chat.id, 
		photo = Cacher.get_real_cached_file(Settings["qr_image"], types.InputMediaPhoto).file_id,
		caption = _('@Taro100_bot\n@Taro100_bot\n@Taro100_bot\n\n<b>Таробот | Расклад онлайн | Карта дня</b>\nСамый большой бот для Таро гаданий в Telegram! Ответит на любые твои вопросы ❓❓❓\n\n<b><i>Пользуйся и делись с друзьями!</i></b>'), 
		reply_markup = InlineKeyboards.AddShare(["Share"]), 
		parse_mode = "HTML"
		)
	
AdminPanel.decorators.reply_keyboards(Bot, usermanager)	

@Bot.message_handler(content_types = ["text"])
def ProcessText(Message: types.Message):
	user = usermanager.auth(Message.from_user)
	if AdminPanel.procedures.text(Bot, usermanager, Message): return
	if EnergyExchanger.procedures.text(Message): return

	if user.expected_type == "Question":
		user.set_property("Question", Message.text)
		user.set_property("Generation", True)
		user.set_expected_type(None)
		logging.info(f"ID пользователя: {user.id}, текст вопроса: {Message.text}")

		try:
			Bot.send_chat_action(Message.chat.id, action = "typing")
			Completed = neurowork.AnswerForUser(Message.chat.id, user.get_property("Question"), user)

			if Completed:
				user.set_property("Generation", False)
		except Exception as ExceptionData: print(ExceptionData)

		user.set_property("Generation", False)

	else: 
		if user.get_property("Generation"): pass
		else:
			user.set_property("Generation", True)
			user.set_property("Question", Message.text)
			logging.info(f"ID пользователя: {user.id}, текст вопроса: {Message.text}")
			user.set_expected_type(None)
			Bot.send_chat_action(Message.chat.id, action = "typing")
			Completed = neurowork.AnswerForUser(Message.chat.id, user.get_property("Question"), user)
			if Completed:
				user.set_property("Generation", False)

AdminPanel.decorators.inline_keyboards(Bot, usermanager)
EnergyExchanger.decorators.inline_keyboards()

AddictionalOptional.decorators.inline_keyboards()
OnlineLayout.decorators.inline_keyboards(Bot, usermanager, Cacher.get_real_cached_file(Settings["start_animation"], types.InputMediaAnimation))
mailer.decorators.inline_keyboards()
values_cards.decorators.inline_keyboards()
yes_no.decorators.inline_keyboards()

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("for_restart"))
def InlineButtonAccept(Call: types.CallbackQuery):
	User = usermanager.auth(Call.from_user)
	MasterBot.safely_delete_messages(
		Call.message.chat.id,
		Call.message.id
	)
	ProcessCommandStart(Call.message)
	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("Subscribe"))
def InlineButtonAllTaro(Call: types.CallbackQuery):
	User = usermanager.auth(Call.from_user)
	if not IsSubscripted(MasterBot, User, Settings):
		Bot.answer_callback_query(Call.id)
		return
	
@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("for_delete"))
def InlineButtonAccept(Call: types.CallbackQuery):
	User = usermanager.auth(Call.from_user)
	MasterBot.safely_delete_messages(
		Call.message.chat.id,
		Call.message.id
	)
	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("delete_before_mm"))
def InlineButtonAccept(Call: types.CallbackQuery):
	User = usermanager.auth(Call.from_user)
	delete_thinking_messages(User, MasterBot, Call)
	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("notifications"))
def InlineButton(Call: types.CallbackQuery):
	User = usermanager.auth(Call.from_user)
	if not IsSubscripted(MasterBot, User, Settings):
		Bot.answer_callback_query(Call.id)
		return
	print(Call.data)
	choice, action = Call.data.split("_")[1:]
	choice: bool = choice == "yes"

	User.set_property("mailing", choice)
	sender.notification_result(message = Call.message, choice = choice, action = action)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("Card_Day"))
def InlineButtonCardDay(Call: types.CallbackQuery):
	User = usermanager.auth(Call.from_user)
	if not IsSubscripted(MasterBot, User, Settings):
		Bot.answer_callback_query(Call.id)
		return
	
	today = datetime.today().strftime("%d.%m.%Y")

	with open(f"Materials/Texts/{today}.txt") as file:
		text = file.read()

	Bot.send_video(
		chat_id = Call.message.chat.id,
		video = Cacher.get_real_cached_file(f"Materials/Video/{today}.mp4", types.InputMediaVideo).file_id,
		caption = text, 
		reply_markup = InlineKeyboards.for_delete("Да будет так!"),
		parse_mode = "HTML"
		)

	Bot.answer_callback_query(Call.id)
	
@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("order_layout"))
def InlineButtonRemoveReminder(Call: types.CallbackQuery):
	User = usermanager.auth(Call.from_user)
	if not IsSubscripted(MasterBot, User, Settings):
		Bot.answer_callback_query(Call.id)
		return
	Bot.edit_message_caption(
		caption = "<b>" + _("РАСКЛАД ОТ МАСТЕРА") + "</b>",
		chat_id = Call.message.chat.id,
		message_id = Call.message.id,
		reply_markup = InlineKeyboards.SendOrderLayout(),
		parse_mode = "HTML"
		)
	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("Online_Layout"))
def InlineButtonRemoveReminder(Call: types.CallbackQuery):
	User = usermanager.auth(Call.from_user)
	if not IsSubscripted(MasterBot, User, Settings):
		Bot.answer_callback_query(Call.id)
		return
	Bot.send_chat_action(Call.message.chat.id, action = "typing")
	
	if not User.get_property("Generation"):
		Bot.send_message(
			Call.message.chat.id,
			_("Дорогой мой друг, задай мне вопрос, который больше всего тебя сейчас волнует!"))
		User.set_expected_type("Question")
	
	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("ThinkCard"))
def InlineButtonRemoveReminder(Call: types.CallbackQuery):
	User = usermanager.auth(Call.from_user)
	if not IsSubscripted(MasterBot, User, Settings):
		Bot.answer_callback_query(Call.id)
		return
	
	User.set_property("ThinkCard", {"day": None, "messages": [], "number": None}, force = False)
	today_date = datetime.now().strftime("%d.%m.%Y")
	path = f"Materials/ChoiceCard/{today_date}"
	day_of_week = datetime.now().weekday()
	
	if not os.path.exists(path):
		today_date = FindNearest(today_date)
		path = f"Materials/ChoiceCard/{today_date}"

	if "_" not in Call.data:
		number_card = GetNumberCard(User, Call, write = False)
		
		if number_card == None: 
			Think_message = CacherSending(Cacher, Bot, path, User, 0, inline = InlineKeyboards.SendThinkCard())
			UpdateThinkCardData(User, Think_message)
		else: 
			delete_thinking_messages(User, MasterBot, Call)
			Think_message1 = CacherSending(Cacher, Bot, path, User, 0)
			ThinkCardData = User.get_property("ThinkCard")
			MasterBot.safely_delete_messages(Call.message.chat.id, User.get_property("ThinkCard")["messages"])
			ThinkCardData["messages"] = []
			User.set_property("ThinkCard", ThinkCardData)

			Think_message2 = CacherSending(Cacher, Bot, path, User, number_card, "\n<b><i>С любовью, Галина Мастер Таро!</i></b>")
			Think_message3 = ChoiceMessage(day_of_week, Bot, Call)
			UpdateThinkCardData2(User, [Think_message1.id, Think_message2.id, Think_message3.id], number_card, today_date)
	else:
		number_card = GetNumberCard(User, Call)
		Think_message2 = CacherSending(Cacher, Bot, path, User, number_card, "\n<b><i>С любовью, Галина Мастер Таро!</i></b>")
		Think_message3 = ChoiceMessage(day_of_week, Bot, Call)
		UpdateThinkCardData2(User, [Think_message2.id, Think_message3.id], number_card, today_date)

	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("all_taro"))
def InlineButtonAllTaro(Call: types.CallbackQuery):
	User = usermanager.auth(Call.from_user)
	if not IsSubscripted(MasterBot, User, Settings):
		Bot.answer_callback_query(Call.id)
		return
	
	Bot.edit_message_caption(
		_("<b>ВСЁ О ТАРО</b>"),
		Call.message.chat.id,
		Call.message.id,
		reply_markup = InlineKeyboards.send_all_taro(),
		parse_mode = "HTML"
		)
	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("main_menu"))
def InlineButtonAllTaro(Call: types.CallbackQuery):
	User = usermanager.auth(Call.from_user)
	if not IsSubscripted(MasterBot, User, Settings):
		Bot.answer_callback_query(Call.id)
		return
	
	Bot.edit_message_caption(
		caption = None,
		chat_id = Call.message.chat.id,
		message_id = Call.message.id,
		reply_markup = InlineKeyboards.main_menu(), 
		parse_mode = "HTML"
	)

	Bot.answer_callback_query(Call.id)

AdminPanel.decorators.photo(Bot, usermanager)

@Bot.message_handler(content_types = ["audio", "document", "video", "voice"])
def File(Message: types.Message):
	User = usermanager.auth(Message.from_user)
	AdminPanel.procedures.files(Bot, User, Message)

Bot.infinity_polling()
