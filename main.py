from Source.Modules.EnergyExchange import Exchanger, Scheduler as ExchangeScheduler
from Source.Modules.ValuesCards import ValuesCards
from Source.UI.AdditionalOptions import Options
from Source.UI.OnlineLayout import Layout
from Source.Modules.YesNo import YesNo

from Source.TeleBotAdminPanel.Core.Moderation import Moderator
from Source.TeleBotAdminPanel.Core.Uploading import Uploader
from Source.Core.AdditionalColumns import *
from Source.TeleBotAdminPanel import Panel

from Source.Functions import FindNearest, ChoiceMessage, CacherSending, UpdateThinkCardData, UpdateThinkCardData2, GetNumberCard, update_think_card, delete_thinking_messages
from Source.UI.WorkpiecesMessages import WorkpiecesMessages
from Source.Modules.InternalСaching import InternalCaching
from Source.Core.BlackDictionary import BlackDictionary
from Source.Modules.Subscription import Subscription
from Source.InlineKeyboards import InlineKeyboards
from Source.Neurowork import NeuroRequestor
from Source.Modules.WordMouth import Mailer
from Source.Core.Reader import Reader

from dublib.TelebotUtils.Cache import TeleCache
from dublib.Methods.Filesystem import ReadJSON
from dublib.TelebotUtils import UsersManager
from dublib.TelebotUtils import TeleMaster
from dublib.Engine.GetText import GetText
from dublib.Methods.System import Clear


from datetime import datetime
from threading import Thread
import dateparser
import logging
import os

from apscheduler.schedulers.background import BackgroundScheduler
from telebot import types

Clear()

Settings = ReadJSON("Settings.json")

MasterBot = TeleMaster(Settings["token"])
Bot = MasterBot.bot
scheduler = BackgroundScheduler()

usermanager = UsersManager("Data/Users")
Cacher = TeleCache()
Cacher.set_options(Settings["token"], Settings["chat_id"])
subscription = Subscription(MasterBot, Settings["subscription_chanel"], Cacher)
reader = Reader(Settings)
mailer = Mailer(MasterBot, usermanager, reader, Cacher, subscription) 
AdminPanel = Panel(Bot, usermanager, Settings["password"])
sender = WorkpiecesMessages(Bot, Cacher)

yes_no = YesNo(MasterBot, Cacher, reader, usermanager, subscription)
values_cards = ValuesCards(MasterBot, usermanager, Cacher, subscription)
Neurowork = NeuroRequestor(Bot, Cacher)
OnlineLayout = Layout(subscription)
AddictionalOptional = Options(MasterBot, usermanager, Settings, sender, Cacher, subscription)

EnergyExchanger = Exchanger(Bot, usermanager, Cacher, subscription)
ExchangeSchedulerObject = ExchangeScheduler(EnergyExchanger, scheduler)

Moderator.initialize(EnergyExchanger.get_unmoderated_mails, EnergyExchanger.moderate_mail)
Uploader.set_uploadable_files(["Data/Exchange/Mails.xlsx"])

logging.basicConfig(level = logging.INFO, encoding = "utf-8", filename = "LOGING.log", filemode = "w", force = True,
	format = '%(asctime)s - %(levelname)s - %(message)s',
	datefmt = '%Y-%m-%d %H:%M:%S')

logging.getLogger("pyTelegramBotAPI").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)

GetText.initialize("Taro", Settings["language"], "locales")
_ = GetText.gettext

#==========================================================================================#
# >>>>> ПРИЗЫВЫ И КАРТА ДНЯ <<<<< #
#==========================================================================================#

scheduler.add_job(mailer.appeals.click_update_card_day, 'cron', hour = 0, minute = 0)
scheduler.add_job(mailer.appeals.randomize_days, "cron", day_of_week = "mon", hour = 0, minute = 0)
scheduler.add_job(mailer.card_day_mailing, 'cron', hour = 8, minute = 0)

#==========================================================================================#
# >>>>> ПОСЛАНИЯ <<<<< #
#==========================================================================================#

scheduler.add_job(mailer.letters.randomize_time, "cron", day = "9, 19, 28", hour = 0, minute = 0)
scheduler.add_job(mailer.letters_mailing, "cron", day = "9, 19, 28", hour = "9-21", minute = "*")

#==========================================================================================#
# >>>>> ЗАГАДАЙ КАРТУ И ОБМЕН ЭНЕРГИЕЙ <<<<< #
#==========================================================================================#

scheduler.add_job(update_think_card, 'cron', day_of_week = "mon, wed, fri", hour = 0, minute = 0, args = [usermanager])
scheduler.start()

# for user in usermanager.users: 
# 	if user.has_property("ap"): user.delete()

# Thread(target = InternalCaching(Cacher).caching).start()

AdminPanel.decorators.commands()

@Bot.message_handler(commands = ["start"])
def ProcessCommandStart(Message: types.Message):
	if not usermanager.is_user_exists(Message.from_user.id): 
		user = usermanager.auth(Message.from_user)
		EnergyExchanger.push_mail(user)
	else: user = usermanager.auth(Message.from_user)
	
	user.set_property("name", Message.from_user.full_name)
	sender.send_start_messages(user)

@Bot.message_handler(commands = ["dev"])
def ProcessCommandStart(Message: types.Message):
	user = usermanager.auth(Message.from_user)

	user.remove_permissions("developer") if user.has_permissions(["developer", "admin"]) else user.add_permissions("developer")
	text = "Режим разработчика включен." if user.has_permissions(["developer", "admin"]) else "Режим разработчика выключен."
	Bot.send_message(
		chat_id = Message.chat.id,
		text = text
	)

@Bot.message_handler(commands = ["card"])
def ProcessCommandCard(Message: types.Message):
	user = usermanager.auth(Message.from_user)
	if not subscription.IsSubscripted(user): return

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
	if not subscription.IsSubscripted(user): return
	sender.settings_mailing(Message, action = "restart")

@Bot.message_handler(commands = ["share"])
def ProcessShareWithFriends(Message: types.Message):
	user = usermanager.auth(Message.from_user)
	if not subscription.IsSubscripted(user): return

	Bot.send_photo(
		Message.chat.id, 
		photo = Cacher.get_real_cached_file(Settings["qr_image"], types.InputMediaPhoto).file_id,
		caption = _('@Taro100_bot\n@Taro100_bot\n@Taro100_bot\n\n<b>Таробот | Расклад онлайн | Карта дня</b>\nСамый большой бот для Таро-гаданий в Telegram! Ответит на любые твои вопросы ❓❓❓\n\n<b><i>Пользуйся и делись с друзьями!</i></b>'), 
		reply_markup = InlineKeyboards.AddShare(["Share"]), 
		parse_mode = "HTML"
		)

@Bot.message_handler(content_types = ["text"])
def ProcessText(Message: types.Message):
	user = usermanager.auth(Message.from_user)
	if AdminPanel.procedures.text(Bot, usermanager, Message): return
	if not subscription.IsSubscripted(user): return
	if EnergyExchanger.procedures.text(Message): return

	if user.expected_type == "Question" or not user.has_property("Generation"):
		user.set_expected_type(None)
		logging.info(f"ID пользователя: {user.id}.")
		logging.info(f"Текст вопроса: {Message.text}")

		try:
			Bot.send_chat_action(Message.chat.id, action = "typing")
			Neurowork.send_layout(user, Message.text)

		except Exception as ExceptionData: print(ExceptionData)

AdminPanel.decorators.inline_keyboards()
EnergyExchanger.decorators.inline_keyboards()

AddictionalOptional.decorators.inline_keyboards()
OnlineLayout.decorators.inline_keyboards(Bot, usermanager, Cacher.get_real_cached_file(Settings["start_animation"], types.InputMediaAnimation))
mailer.decorators.inline_keyboards()
values_cards.decorators.inline_keyboards()
yes_no.decorators.inline_keyboards()

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("for_restart"))
def InlineButtonAccept(Call: types.CallbackQuery):
	user = usermanager.auth(Call.from_user)
	if not subscription.IsSubscripted(user):
		Bot.answer_callback_query(Call.id)
		return
	MasterBot.safely_delete_messages(
		Call.message.chat.id,
		Call.message.id
	)
	sender.send_start_messages(user, title = False)
	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("Subscribe"))
def InlineButtonAllTaro(Call: types.CallbackQuery):
	user = usermanager.auth(Call.from_user)

	if not subscription.IsSubscripted(user):
		Bot.answer_callback_query(Call.id)
		return
	
@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("for_delete"))
def InlineButtonAccept(Call: types.CallbackQuery):
	user = usermanager.auth(Call.from_user)
	if not subscription.IsSubscripted(user):
		Bot.answer_callback_query(Call.id)
		return
	MasterBot.safely_delete_messages(
		Call.message.chat.id,
		Call.message.id
	)
	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("delete_before_mm"))
def InlineButtonAccept(Call: types.CallbackQuery):
	user = usermanager.auth(Call.from_user)
	if not subscription.IsSubscripted(user):
		Bot.answer_callback_query(Call.id)
		return
	delete_thinking_messages(user, MasterBot, Call)
	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("notifications"))
def InlineButton(Call: types.CallbackQuery):
	user = usermanager.auth(Call.from_user)
	if not subscription.IsSubscripted(user):
		Bot.answer_callback_query(Call.id)
		return
	choice, action = Call.data.split("_")[1:]
	choice: bool = choice == "yes"

	user.set_property("mailing", choice)
	sender.notification_result(message = Call.message, choice = choice, action = action)
	
@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("order_layout"))
def InlineButtonRemoveReminder(Call: types.CallbackQuery):
	user = usermanager.auth(Call.from_user)
	if not subscription.IsSubscripted(user):
		Bot.answer_callback_query(Call.id)
		return
	Bot.edit_message_caption(
		caption = "<b>" + _("РАСКЛАД У МАСТЕРА") + "</b>",
		chat_id = Call.message.chat.id,
		message_id = Call.message.id,
		reply_markup = InlineKeyboards.SendOrderLayout(),
		parse_mode = "HTML"
		)
	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("Online_Layout"))
def InlineButtonRemoveReminder(Call: types.CallbackQuery):
	user = usermanager.auth(Call.from_user)
	if not subscription.IsSubscripted(user):
		Bot.answer_callback_query(Call.id)
		return
	Bot.send_chat_action(Call.message.chat.id, action = "typing")
	
	if not user.get_property("Generation"):
		Bot.send_message(
			Call.message.chat.id,
			_("Дорогой мой друг, задай мне вопрос, который больше всего тебя сейчас волнует!"))
		user.set_expected_type("Question")
	
	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("ThinkCard"))
def InlineButtonRemoveReminder(Call: types.CallbackQuery):
	user = usermanager.auth(Call.from_user)
	if not subscription.IsSubscripted(user):
		Bot.answer_callback_query(Call.id)
		return
	
	user.set_property("ThinkCard", {"day": None, "messages": [], "number": None}, force = False)
	today_date = datetime.now().strftime("%d.%m.%Y")
	path = f"Materials/ChoiceCard/{today_date}"
	day_of_week = datetime.now().weekday()
	
	if not os.path.exists(path):
		today_date = FindNearest(today_date)
		path = f"Materials/ChoiceCard/{today_date}"

	if "_" not in Call.data:
		number_card = GetNumberCard(user, Call, write = False)
		
		if number_card == None: 
			Think_message = CacherSending(Cacher, Bot, path, user, 0, inline = InlineKeyboards.SendThinkCard())
			UpdateThinkCardData(user, Think_message)
		else: 
			delete_thinking_messages(user, MasterBot, Call)
			Think_message1 = CacherSending(Cacher, Bot, path, user, 0)
			ThinkCardData = user.get_property("ThinkCard")
			MasterBot.safely_delete_messages(Call.message.chat.id, user.get_property("ThinkCard")["messages"])
			ThinkCardData["messages"] = []
			user.set_property("ThinkCard", ThinkCardData)

			Think_message2 = CacherSending(Cacher, Bot, path, user, number_card, "\n<b><i>С любовью, Галина Таро Мастер!</i></b>")
			Think_message3 = ChoiceMessage(day_of_week, Bot, Call)
			UpdateThinkCardData2(user, [Think_message1.id, Think_message2.id, Think_message3.id], number_card, today_date)
	else:
		number_card = GetNumberCard(user, Call)
		Think_message2 = CacherSending(Cacher, Bot, path, user, number_card, "\n<b><i>С любовью, Галина Таро Мастер!</i></b>")
		Think_message3 = ChoiceMessage(day_of_week, Bot, Call)
		UpdateThinkCardData2(user, [Think_message2.id, Think_message3.id], number_card, today_date)

	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("all_taro"))
def InlineButtonAllTaro(Call: types.CallbackQuery):
	user = usermanager.auth(Call.from_user)
	if not subscription.IsSubscripted(user):
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
	user = usermanager.auth(Call.from_user)
	if not subscription.IsSubscripted(user):
		Bot.answer_callback_query(Call.id)
		return
	
	Bot.edit_message_caption(
		caption = None,
		chat_id = Call.message.chat.id,
		message_id = Call.message.id,
		reply_markup = InlineKeyboards.main_menu(user), 
		parse_mode = "HTML"
	)

	Bot.answer_callback_query(Call.id)

@Bot.message_handler(content_types = ["audio", "document", "video", "voice", "photo"])
def File(Message: types.Message):
	User = usermanager.auth(Message.from_user)
	AdminPanel.procedures.files(Bot, User, Message)

Bot.infinity_polling()
