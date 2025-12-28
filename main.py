from Source.Modules.EnergyExchange import Exchanger, Scheduler as ExchangeScheduler
from Source.Modules.AscendTaro import AscendData, MainAscend, ManagerPromoCodes
from Source.Modules.ValuesCards import ValuesCards
from Source.UI.AdditionalOptions import Options
from Source.UI.OnlineLayout import Layout
from Source.Modules.YesNo import YesNo
from Source.Modules.ThinkCard import Data as ThinkCard_Data, Manager as ThinkCard_Manager, InlineKeyboard as ThinkCard_InlineKeyboard, Main as MainThinkCard, update_think_card
from Source.Modules.Marathon import Marathon
from Source.Modules.Feedback import Feedback
from Source import Functions

from Source.TeleBotAdminPanel.Modules.Moderation import ModeratorsModes
from Source.TeleBotAdminPanel import Panel, Modules
from Source.Core import Statistics

from Source.Modules.LayoutsExamples import LayoutsExamples
from Source.TeleBotAdminPanel import Panel
from Source.UI.WorkpiecesMessages import WorkpiecesMessages
from Source.Core.BlackDictionary import BlackDictionary
from Source.Modules.Subscription import Subscription
from Source.InlineKeyboards import InlineKeyboards
from Source.Neurowork import NeuroRequestor
from Source.Modules.WordMouth import Mailer
from Source.Core.ExcelTools import Reader
from Source.Core.CustomUsersManager import CustomUsersManager
from Source.Core.AdminCommands import Informator
from Source.Core.Cacher import Cacher

from dublib.Engine.Configurator import Config
from dublib.TelebotUtils import TeleMaster
from dublib.Engine.GetText import GetText
from dublib.Methods.System import Clear

from datetime import datetime
from threading import Thread
import dateparser
import logging
import random

from apscheduler.schedulers.background import BackgroundScheduler
from telebot import types

Clear()

Settings = Config("Settings.json")
Settings.load()

MasterBot = TeleMaster(Settings["token"])
Bot = MasterBot.bot

scheduler = BackgroundScheduler()

manager_promocodes = ManagerPromoCodes()

usermanager = CustomUsersManager("Data/Users")
usermanager.set_bot(Bot)
usermanager.set_cacher(Cacher)
usermanager.set_manager_promocodes(manager_promocodes)

subscription = Subscription(MasterBot, Settings["subscription_chanel"], Cacher, usermanager)
reader = Reader(Settings)
mailer = Mailer(MasterBot, usermanager, reader, Cacher, subscription) 
sender = WorkpiecesMessages(Bot, Cacher)

yes_no = YesNo(MasterBot, Cacher, reader, usermanager, subscription)
values_cards = ValuesCards(MasterBot, usermanager, Cacher, subscription)
Neurowork = NeuroRequestor(Bot, Cacher)
OnlineLayout = Layout(subscription)
AddictionalOptional = Options(MasterBot, usermanager, Settings, sender, Cacher, subscription, reader)
marathon = Marathon(usermanager, Bot, subscription, Cacher, reader)

EnergyExchanger = Exchanger(Bot, usermanager, Cacher, subscription)
ExchangeSchedulerObject = ExchangeScheduler(EnergyExchanger, scheduler)
feedback = Feedback(usermanager, Cacher, subscription, Bot)

LayoutsExamplesObject = LayoutsExamples()

main_ascend = MainAscend(users = usermanager, scheduler = scheduler, bot = Bot, cacher = Cacher, subscription = subscription)
main_think = MainThinkCard(users = usermanager, bot = Bot, cacher = Cacher, subscription = subscription)

#==========================================================================================#
# >>>>> ИНИЦИАЛИЗАЦИЯ ПАНЕЛИ УПРАВЛЕНИЯ <<<<< #
#==========================================================================================#

AdminPanel = Panel(Bot, usermanager, Settings["password"])

TBAP_TREE = {
	"📊 Статистика": Statistics.CM_Statistics,
	"✍🏻 Модерация": Modules.SM_Moderation,
	"📤 Выгрузка": Modules.SM_Extraction,
	"❌ Закрыть": Modules.SM_Close
}

AdminPanel.set_tree(TBAP_TREE)
AdminPanel.set_close_callback(sender.send_start_messages)

# Получение объекта модуля статистики.
SM_Statistics: Modules.SM_Statistics = AdminPanel.get_module_object(Statistics.CM_Statistics.__name__)
# Определение нового словаря колонок для управления последовательностью колонок.
Columns = {"Index": Statistics.get_index}
# Установка методов для заполнения ячеек дополнительных колонки.
Columns.update(SM_Statistics.columns)
SM_Statistics.columns = Columns
SM_Statistics.columns["Name"] = Statistics.get_name
SM_Statistics.columns["Level"] = Statistics.get_level
SM_Statistics.columns["Promocode"] = Statistics.get_promocode
SM_Statistics.columns["Registration Date"] = Statistics.get_registration_date

# Получение объекта модуля выгрузки.
SM_Extraction: Modules.SM_Extraction = AdminPanel.get_module_object(Modules.SM_Extraction.__name__)
# Определение пар название-путь файла.
FILES = {"Послания": "Data/Exchange/Mails.xlsx"}
# Установка файлов для выгрузки.
SM_Extraction.set_files(FILES)

# Получение объекта модуля модерации.
SM_Moderation: Modules.SM_Moderation = AdminPanel.get_module_object(Modules.SM_Moderation.__name__)
# Инициализация модераторов контента.
Storage_Mails = SM_Moderation.add_moderator("mails", "Обмен энергией", ModeratorsModes.Editable, EnergyExchanger.moderate_mail)
Storage_Common = SM_Moderation.add_moderator("common", "Общие вопросы", ModeratorsModes.Editable, LayoutsExamplesObject.moderate_common)
Storage_Feedback = SM_Moderation.add_moderator("feedback", "Обратная связь", ModeratorsModes.View)
# Привязка модераторов к обработчикам.
EnergyExchanger.set_unmoderated_mails_storage(Storage_Mails)
LayoutsExamplesObject.set_unmoderated_common_storage(Storage_Common)
feedback.set_reports_storage(Storage_Feedback)

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

@Bot.message_handler(commands = ["admin"])
def Command(Message: types.Message):
	User = usermanager.auth(Message.from_user)
	AdminPanel.open(User, "Панель управления открыта.")

@Bot.message_handler(commands = ["new"])
def ProcessCommandStart(Message: types.Message):
	User = usermanager.auth(Message.from_user)
	Functions.CloseAdminPanel(Bot, AdminPanel, User)

	Bot.send_message(chat_id = User.id, text = "Отправьте текст вопроса.")
	User.set_expected_type("new_common_question")

@Bot.message_handler(commands = ["info"])
def ProcessInfo(Message: types.Message):
	User = usermanager.auth(Message.from_user)
	Functions.CloseAdminPanel(Bot, AdminPanel, User)

	if User.has_permissions("admin"):

		template_text = (
				_("СВОДКА:" + "\n\n"),
				"<b>" + _("Карта дня" + "</b>" + "\n"),
				_("Видео до " + Informator().latest_video + "\n"),
				_("Тексты до " + Informator().latest_text + "\n\n"),
				"<b>" + _("Загадай карту" + "</b>" + "\n"),
				_("Фото до " + Informator().latest_photo + "\n"),
				_("Посты до " + Informator().latest_post + "\n\n"),
				)

		Bot.send_message(
			chat_id = User.id, 
			text = (" ").join(template_text),
			parse_mode = "HTML")

@Bot.message_handler(commands = ["start"])
def ProcessCommandStart(Message: types.Message):
	if not usermanager.is_user_exists(Message.from_user.id):  
		user = usermanager.auth(Message.from_user)
		Functions.CloseAdminPanel(Bot, AdminPanel, user)
		
		if Message.text != "/start" and int(Message.text.split(" ")[-1]) != user.id: 
			user.set_property("invited_by", int(Message.text.split(" ")[-1]))
			AscendData(user = user).set_count_referal()

		EnergyExchanger.push_mail(user)
		
	else: 
		user = usermanager.auth(Message.from_user)
		Functions.CloseAdminPanel(Bot, AdminPanel, user)
	
	if not user.has_property("registration_date"): user.set_property("registration_date", datetime.now().strftime("%d.%m.%Y"))
	sender.send_start_messages(user)

@Bot.message_handler(commands = ["dev"])
def ProcessCommandStart(Message: types.Message):
	user = usermanager.auth(Message.from_user)
	Functions.CloseAdminPanel(Bot, AdminPanel, user)

	user.remove_permissions("developer") if user.has_permissions(["developer", "admin"]) else user.add_permissions("developer")
	text = "Режим разработчика включен." if user.has_permissions(["developer", "admin"]) else "Режим разработчика выключен."
	Bot.send_message(
		chat_id = Message.chat.id,
		text = text
	)

@Bot.message_handler(commands = ["card"])
def ProcessCommandCard(Message: types.Message):
	user = usermanager.auth(Message.from_user)
	Functions.CloseAdminPanel(Bot, AdminPanel, user)
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
	Functions.CloseAdminPanel(Bot, AdminPanel, user)
	if not subscription.IsSubscripted(user): return
	sender.settings_mailing(Message, action = "restart")

@Bot.message_handler(commands = ["share"])
def ProcessShareWithFriends(Message: types.Message):
	user = usermanager.auth(Message.from_user)
	Functions.CloseAdminPanel(Bot, AdminPanel, user)
	if not subscription.IsSubscripted(user): return

	Bot.send_photo(
		Message.chat.id, 
		photo = Cacher.get_real_cached_file(Settings["qr_image"], types.InputMediaPhoto).file_id,
		caption = _('@TarobotX_bot\n@TarobotX_bot\n@TarobotX_bot\n\n<b>Таробот | Расклад онлайн | Карта дня</b>\nСамый популярный бот для Таро-гаданий в Telegram! Ответит на любые твои вопросы ❓❓❓\n\n<b><i>Пользуйся и делись с друзьями!</i></b>'), 
		reply_markup = InlineKeyboards.AddShare(["Share"]), 
		parse_mode = "HTML"
		)

@Bot.message_handler(content_types = ["text"])
def ProcessText(Message: types.Message):
	user = usermanager.auth(Message.from_user)
	if AdminPanel.procedures.text(Message): return
	if not subscription.IsSubscripted(user): return
	if EnergyExchanger.procedures.text(Message): return
	if feedback.procedures.text(Message): return
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
		print(Message.text)
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
		user.reset_expected_type()

AdminPanel.decorators.inline_keyboards()
EnergyExchanger.decorators.inline_keyboards()
main_ascend.decorators.inline_keyboards()
main_think.decorators.inline_keyboards()

AddictionalOptional.decorators.inline_keyboards()
OnlineLayout.decorators.inline_keyboards(Bot, usermanager, Cacher.get_real_cached_file(Settings["start_animation"], types.InputMediaAnimation))
mailer.decorators.inline_keyboards()
values_cards.decorators.inline_keyboards()
yes_no.decorators.inline_keyboards()
marathon.decorators.inline_keyboards()
feedback.decorators.inline_keyboards()

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
	
	user.reset_expected_type()
	MasterBot.safely_delete_messages(
		Call.message.chat.id,
		Call.message.id
	)

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
		caption = "<b>" + _("РАСКЛАД У МАСТЕРА") + "🔥</b>\n\n" + _("Возьми расклад у Мастера, и реши одну из своих проблем:"),
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
	
	ascend_data = AscendData(user = user)
	if not ascend_data.is_layout_available:

		if ascend_data.delete_limiter:
			MasterBot.safely_delete_messages(user.id, ascend_data.delete_limiter, complex = True)
			ascend_data.zeroing_delete_limiter()

		messages = main_ascend.sender.limiter_layouts(chat_id = Call.message.chat.id)
		ascend_data.add_delete_limiter(messages)
		Bot.answer_callback_query(Call.id)
		return

	Bot.send_chat_action(Call.message.chat.id, action = "typing")

	CommonQuestions = random.choices(LayoutsExamplesObject.common_questions, k = 2)
	LoveQuestion = random.choice(LayoutsExamplesObject.love_questions)

	text = (
		_("Дорогой мой друг, задай мне вопрос, который больше всего тебя волнует!") + "\n",
		"<b><i>" + _("ТРЕНДЫ ЗАПРОСОВ") + " 📈:" + "</i></b>",
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

	data = ThinkCard_Data(user = user)

	if "_" not in Call.data and data.number_card == None:
		MasterBot.safely_delete_messages(Call.message.chat.id, data.messages)
		data.zeroing_messages()
		introdution_message: types.Message = main_think.sender.needed_message(ThinkCard_Manager().needed_folder(), user, 0, inline = InlineKeyboards.SendThinkCard())
		data.add_messages(message_id = introdution_message.id)

	else:
		if "_" in Call.data: data.set_number_card(int(Call.data.split("_")[-1]))

		MasterBot.safely_delete_messages(Call.message.chat.id, data.messages)
		data.zeroing_messages()
		introdution_message: types.Message = main_think.sender.needed_message(ThinkCard_Manager().needed_folder(), user, 0)
		data.add_messages(message_id = introdution_message.id)
		
		message_with_selected_card = main_think.sender.needed_message(
			ThinkCard_Manager().needed_folder(), 
			user, 
			data.number_card, 
			"\n<b><i>С любовью, Галина Таро Мастер!</i></b>", 
			inline = ThinkCard_InlineKeyboard.about())
		data.add_messages(message_with_selected_card.id)
		
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

Bot.infinity_polling()
