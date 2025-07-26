from Source.Modules.EnergyExchange import Exchanger, Scheduler as ExchangeScheduler
from Source.Modules.AscendTaro import AscendData, MainAscend
from Source.Modules.ValuesCards import ValuesCards
from Source.UI.AdditionalOptions import Options
from Source.UI.OnlineLayout import Layout
from Source.Modules.YesNo import YesNo

from Source.TeleBotAdminPanel.Core.Moderation import Moderator, ModeratorsStorage
from Source.TeleBotAdminPanel.Core.Uploading import Uploader

from Source.Modules.LayoutsExamples import LayoutsExamples
from Source.Core.AdditionalColumns import *
from Source.TeleBotAdminPanel import Panel
from Source.Functions import FindNearest, ChoiceMessage, CacherSending, UpdateThinkCardData, UpdateThinkCardData2, GetNumberCard, update_think_card, delete_thinking_messages
from Source.UI.WorkpiecesMessages import WorkpiecesMessages
from Source.Core.BlackDictionary import BlackDictionary
from Source.Modules.Subscription import Subscription
from Source.InlineKeyboards import InlineKeyboards
from Source.Neurowork import NeuroRequestor
from Source.Modules.WordMouth import Mailer
from Source.Core.ExcelTools import Reader
from Source.Core.CustomUsersManager import CustomUsersManager

from dublib.TelebotUtils.Cache import TeleCache
from dublib.Engine.Configurator import Config
from dublib.TelebotUtils import TeleMaster
from dublib.Engine.GetText import GetText
from dublib.Methods.System import Clear

from datetime import datetime
from threading import Thread
import dateparser
import logging
import random
import os

from apscheduler.schedulers.background import BackgroundScheduler
from telebot import types

Clear()

Settings = Config("Settings.json")
Settings.load()

MasterBot = TeleMaster(Settings["token"])
Bot = MasterBot.bot

scheduler = BackgroundScheduler()

Cacher = TeleCache()
Cacher.set_bot(Settings["token"])
Cacher.set_chat_id(Settings["chat_id"])

usermanager = CustomUsersManager("Data/Users")
usermanager.set_bot(Bot)
usermanager.set_cacher(Cacher)

subscription = Subscription(MasterBot, Settings["subscription_chanel"], Cacher, usermanager)
reader = Reader(Settings)
mailer = Mailer(MasterBot, usermanager, reader, Cacher, subscription) 
AdminPanel = Panel(Bot, usermanager, Settings["password"])
sender = WorkpiecesMessages(Bot, Cacher)

yes_no = YesNo(MasterBot, Cacher, reader, usermanager, subscription)
values_cards = ValuesCards(MasterBot, usermanager, Cacher, subscription)
Neurowork = NeuroRequestor(Bot, Cacher)
OnlineLayout = Layout(subscription)
AddictionalOptional = Options(MasterBot, usermanager, Settings, sender, Cacher, subscription, reader)

EnergyExchanger = Exchanger(Bot, usermanager, Cacher, subscription)
ExchangeSchedulerObject = ExchangeScheduler(EnergyExchanger, scheduler)

LayoutsExamplesObject = LayoutsExamples()

main_ascend = MainAscend(users = usermanager, scheduler = scheduler, bot = Bot, cacher = Cacher, subscription = subscription)

ModeratorsStorage.add_moderator(Moderator(EnergyExchanger.get_unmoderated_mails, EnergyExchanger.moderate_mail), "Обмен энергией")
ModeratorsStorage.add_moderator(Moderator(LayoutsExamplesObject.get_unmoderated_common, LayoutsExamplesObject.moderate_common), "Общие вопросы")
Uploader.set_uploadable_files("Data/Exchange/Mails.xlsx")

logging.basicConfig(level = logging.DEBUG, encoding = "utf-8", filename = "LOGING.log", filemode = "w", force = True,
	format = '%(asctime)s - %(levelname)s - %(message)s',
	datefmt = '%Y-%m-%d %H:%M:%S')

logging.getLogger("pyTelegramBotAPI").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)

GetText.initialize("Taro", Settings["language"], "locales")
_ = GetText.gettext

for User in usermanager.users: 
	if User.has_property("Generation") and User.get_property("Generation"): User.set_property("Generation", False)

usermanager.remove_property("Question")

#==========================================================================================#
# >>>>> ПРИЗЫВЫ И КАРТА ДНЯ <<<<< #
#==========================================================================================#

scheduler.add_job(mailer.appeals.click_update_card_day, 'cron', hour = 0, minute = 0)
scheduler.add_job(mailer.appeals.randomize_days, "cron", day_of_week = "mon", hour = 0, minute = 0)
scheduler.add_job(mailer.card_day_mailing, 'cron', hour = 8, minute = 0)

#==========================================================================================#
# >>>>> ПОСЛАНИЯ <<<<< #
#==========================================================================================#

scheduler.add_job(mailer.letters.randomize_time, "cron", day = "8, 18, 28", hour = 0, minute = 0) 
scheduler.add_job(mailer.letters_mailing, "cron", day = "8, 18, 28", hour = "9-21", minute = "*")

#==========================================================================================#
# >>>>> ЗАГАДАЙ КАРТУ <<<<< #
#==========================================================================================#

scheduler.add_job(update_think_card, 'cron', day_of_week = "mon, wed, fri", hour = 0, minute = 0, args = [usermanager])

scheduler.start()

try:
	from Source.Modules.InternalСaching import InternalCaching
	Thread(target = InternalCaching(Cacher).caching).start()

except ImportError: pass

AdminPanel.decorators.commands()

@Bot.message_handler(commands = ["new"])
def ProcessCommandStart(Message: types.Message):
	User = usermanager.auth(Message.from_user)
	Bot.send_message(chat_id = User.id, text = "Отправьте текст вопроса.")
	User.set_expected_type("new_common_question")

@Bot.message_handler(commands = ["start"])
def ProcessCommandStart(Message: types.Message):
	if not usermanager.is_user_exists(Message.from_user.id):  
		user = usermanager.auth(Message.from_user)

		if Message.text != "/start" and int(Message.text.split(" ")[-1]) != user.id: user.set_property("invited_by", int(Message.text.split(" ")[-1]))
		
		EnergyExchanger.push_mail(user)
	else: user = usermanager.auth(Message.from_user)
	
	if not user.has_property("registration_date"): user.set_property("registration_date", datetime.now().strftime("%d.%m.%Y"))
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

	Message_send = False
	if len(Message.text.split(" ")) == 2:
		user_date = Message.text.split(" ")[-1]
		try:
			datekey = dateparser.parse(user_date, settings = {'DATE_ORDER': 'DMY','STRICT_PARSING': True}).strftime("%d.%m.%Y")
			with open(f"Materials/Texts/{datekey}.txt") as file:
				text = file.read()

			try:
				Message_send = Bot.send_video(
					chat_id = Message.chat.id,
					video = Cacher.get_real_cached_file(f"Materials/Video/{datekey}.mp4", types.InputMediaVideo).file_id,
					caption = text, 
					parse_mode = "HTML"
					)
				
			except FileNotFoundError: 
				Message_send = Bot.send_photo(
					chat_id = Message.chat.id,
					photo = Cacher.get_real_cached_file(f"Materials/Photo/{datekey}.jpg", types.InputMediaPhoto).file_id,
					caption = text, 
					parse_mode = "HTML"
					)
			
		except FileNotFoundError: 
			if not Message_send and text:
				Bot.send_message(
					chat_id = Message.chat.id,
					text = text, 
					parse_mode = "HTML"
					)
			else:

				Bot.send_message(
					Message.chat.id,
					text = _("Такой даты пока не существует.")
					)
				
		except Exception as E:
			Bot.send_message(
				Message.chat.id,
				text = _(f"{E}, Команда введена неправильно. Формат команды: /card 21.01.2025")
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
		caption = _('@Taro100_bot\n@Taro100_bot\n@Taro100_bot\n\n<b>Таробот | Расклад онлайн | Карта дня</b>\nСамый популярный бот для Таро-гаданий в Telegram! Ответит на любые твои вопросы ❓❓❓\n\n<b><i>Пользуйся и делись с друзьями!</i></b>'), 
		reply_markup = InlineKeyboards.AddShare(["Share"]), 
		parse_mode = "HTML"
		)

@Bot.message_handler(content_types = ["text"])
def ProcessText(Message: types.Message):
	user = usermanager.auth(Message.from_user)
	if AdminPanel.procedures.text(Bot, usermanager, Message): return
	if not subscription.IsSubscripted(user): return
	if EnergyExchanger.procedures.text(Message): return
	if user.has_property("Generation") and user.get_property("Generation"): return

	if user.expected_type == "question":
		logging.info(f"ID пользователя: {user.id}.")
		logging.info(f"Текст вопроса: {Message.text}")

		try:
			Bot.send_chat_action(Message.chat.id, action = "typing")
			Neurowork.send_layout(user, Message.text)

		except Exception as ExceptionData:
			logging.error(str(ExceptionData))
			user.set_property("Generation", False)

	elif user.expected_type == "new_common_question":
		LayoutsExamplesObject.add_unmoderated_common(Message.text)
		Text = (
			"Ваш вопрос сохранён.",
			"Чтобы приступить к редактированию и модерации, нажмте /admin и перейдите в <b>Модерация</b> ➜ <b>Общие вопросы</b>."
		)
		Bot.send_message(
			chat_id = User.id,
			text = "\n\n".join(Text),
			parse_mode = "HTML"
		)
		User.reset_expected_type()

AdminPanel.decorators.inline_keyboards()
EnergyExchanger.decorators.inline_keyboards()
main_ascend.decorators.inline_keyboards()

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
		caption = "<b>" + _("РАСКЛАД У МАСТЕРА") + "</b>" + "\n\n" + _("Возьми расклад у Мастера, и реши одну из своих проблем:"),
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
	if not AscendData(user = user).is_layout_available:

		main_ascend.sender.limiter_layouts(chat_id = Call.message.chat.id)
		Bot.answer_callback_query(Call.id)
		return

	Bot.send_chat_action(Call.message.chat.id, action = "typing")

	CommonQuestions = random.choices(LayoutsExamplesObject.common_questions, k = 2)
	LoveQuestion = random.choice(LayoutsExamplesObject.love_questions)

	text = (
		_("Дорогой мой друг, задай мне вопрос, который больше всего тебя сейчас волнует!") + "\n",
		"<b>" + _("Например:") + "</b>",
		"<b>- </b>" + "<i>" + LoveQuestion + "</i>",
		"<b>- </b>" + "<i>" + CommonQuestions[0] + "</i>",
		"<b>- </b>" + "<i>" + CommonQuestions[1] + "</i>",
		"<b>- </b>" + "<i>" + _("Любой свой Вопрос❓") + "</i>" + "\n",
		"Напиши мне его прям под этим сообщением:"
		)
	
	if not user.get_property("Generation"):
		user.set_expected_type("question")
		Bot.send_message(
			chat_id = Call.message.chat.id,
			text = "\n".join(text),
			parse_mode = "HTML",
			reply_markup = InlineKeyboards.for_delete("◀️ Назад"))
	
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
