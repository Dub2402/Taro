from dublib.Methods.Filesystem import ReadJSON
from dublib.Methods.System import Clear
from dublib.TelebotUtils.Cache import TeleCache
from dublib.TelebotUtils import UsersManager
from dublib.TelebotUtils import TeleMaster
from dublib.Engine.GetText import GetText

from Source.TeleBotAdminPanel import Panel
from Source.InlineKeyboards import InlineKeyboards
from Source.Cards import Cards
from Source.Neurowork import Neurowork
from Source.Mailer import Mailer
from Source.Functions import IsSubscripted
from Source.Reader import Reader

import os
import logging
import dateparser
import os
from telebot import types
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
from datetime import datetime
from time import sleep

Settings = ReadJSON("Settings.json")

GetText.initialize("Taro", Settings["language"], "locales")
_ = GetText.gettext

MasterBot = TeleMaster(Settings["token"])
Bot = MasterBot.bot

usermanager = UsersManager("Data/Users")
InlineKeyboard = InlineKeyboards()
Cacher = TeleCache()
Cacher.set_options(Settings["token"], Settings["chat_id"])
Card = Cards(Bot, InlineKeyboard, Cacher)
neurowork = Neurowork(Bot, Cacher)
mailer = Mailer(Bot, usermanager, Card, InlineKeyboard)
AdminPanel = Panel()
reader = Reader(Settings)

logging.basicConfig(level=logging.INFO, encoding="utf-8", filename="LOGING.log", filemode="w", force=True,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

logging.getLogger("pyTelegramBotAPI").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)

Clear()

# Получение структуры данных кэшированного файла.
try:
    File = Cacher.get_cached_file(Settings["qr_id"], type = types.InputMediaPhoto)
    File = Cacher.get_cached_file(Settings["start_id"], type = types.InputMediaAnimation)
    # Получение ID кэшированного файла.
    QrImage = Cacher[Settings["qr_id"]]
    StartImage = Cacher[Settings["start_id"]]
except Exception:
    pass

scheduler = BackgroundScheduler()

executors = {
    'default': ThreadPoolExecutor(1)
}
scheduler.configure(executors = executors)

scheduler.add_job(mailer.StartMailing, 'cron', hour = Settings["mailing_time"].split(":")[0], minute = Settings["mailing_time"].split(":")[1])
scheduler.add_job(mailer.Planning, "cron", day_of_week = Settings["planning_day"], hour = Settings["planning_time"].split(":")[0], minute = Settings["planning_time"].split(":")[1])
for i in range(7): scheduler.add_job(mailer.Mailings, "cron", day_of_week = i, hour = Settings["mailings"].split(":")[0], minute = Settings["mailings"].split(":")[1], args = [i, reader, scheduler, Bot])
scheduler.start()

now = datetime.now()

current_hour = now.hour
current_minute = now.minute
day_of_week = now.weekday()

if Settings["restart_mailings"]: mailer.Mailings(day_of_week, reader, scheduler, Bot, True)
if Settings["once_mailing"]: mailer.once_mailing(Bot)

AdminPanel.decorators.commands(Bot, usermanager, Settings["password"])

@Bot.message_handler(commands=["start"])
def ProcessCommandStart(Message: types.Message):
    User = usermanager.auth(Message.from_user)
    Message = Bot.send_message(
        Message.chat.id,
        text = _("<b>Добро пожаловать в Таробот!</b>\n\nСамый большой бот для Таро-гаданий в Telegram!\n\nЗадай боту любой❓️вопрос и наслаждайся ответом!"),
        parse_mode = "HTML"
    )
    Message = Bot.send_animation(
        Message.chat.id,
        animation = StartImage,
        caption = None,
        reply_markup = InlineKeyboard.SendMainMenu(),
        parse_mode = "HTML"
    )
    User.set_property("Current_place", None, force = False)
    User.set_property("Card_name", None, force = False)
    User.set_property("Question", None)
    User.set_property("Generation", False)
    User.set_property("Subscription", None, force = False)
    User.set_property("Planning_days", None, force = False)
    User.clear_temp_properties()
    if User.get_property("Planning_days") == None:
        mailer.SavePlanning_days(User)

    if not IsSubscripted(MasterBot, User, Settings, InlineKeyboard): return    
    
@Bot.message_handler(commands=["card"])
def ProcessCommandCard(Message: types.Message):
    User = usermanager.auth(Message.from_user)
    if not IsSubscripted(MasterBot, User, Settings, InlineKeyboard): return

    if len(Message.text.split(" ")) == 2:
        user_date = Message.text.split(" ")[-1]
        try:
            datekey = dateparser.parse(user_date, settings = {'DATE_ORDER': 'DMY','STRICT_PARSING': True}).strftime("%d.%m.%Y")
            InstantCard = Card.GetInstantCard(datekey)
            if InstantCard:
                Bot.send_photo(
                                Message.chat.id,
                                photo = InstantCard["photo"],
                                caption = InstantCard["text"], 
                                parse_mode= 'HTML'
                            )
            else:
                try:
                    Photo, Text = Card.GetCard(datekey)
                    Message = Bot.send_photo(
                        Message.chat.id,
                        photo = open(f"{Photo}", "rb"),
                        caption = Text, 
                        parse_mode= 'HTML'
                        )
                    Card.AddCard(Message.photo[0].file_id, datekey)
                except: 
                    Bot.send_message(
                        Message.chat.id,
                        text = _("Такой даты пока не существует.")
                        )
        except:
            Bot.send_message(
                Message.chat.id,
                text = _("Команда введена неправильно. Формат команды: /card 21.01.2025")
                )
    else: 
        Bot.send_message(
        Message.chat.id,
        text = _("Команда введена неправильно. Формат команды: /card 21.01.2025"))

@Bot.message_handler(commands = ["mailset"])
def ProcessCommandMailset(Message: types.Message):
    User = usermanager.auth(Message.from_user)
    if not IsSubscripted(MasterBot, User, Settings, InlineKeyboard): return
    Bot.send_message(Message.chat.id, _("Желаете включить утреннюю рассылку <b>Карты дня</b>?"), parse_mode = "HTML", reply_markup = InlineKeyboard.notifications())

@Bot.message_handler(commands=["share"])
def ProcessShareWithFriends(Message: types.Message):
    User = usermanager.auth(Message.from_user)
    if not IsSubscripted(MasterBot, User, Settings, InlineKeyboard): return
    try:
        Bot.send_photo(
            Message.chat.id, 
            photo = QrImage,
            caption = _('@Taro100_bot\n@Taro100_bot\n@Taro100_bot\n\n<b>Таробот | Расклад онлайн | Карта дня</b>\nБот, который ответит на все твои вопросы ❓❓❓\n\n<b><i>Пользуйся и делись с друзьями!</i></b>'), 
            reply_markup = InlineKeyboard.AddShare(), 
            parse_mode = "HTML"
            )
    except: 
        Bot.send_message(
            Message.chat.id, 
            text = _('@Taro100_bot\n@Taro100_bot\n@Taro100_bot\n\n<b>Таробот | Расклад онлайн | Карта дня</b>\nБот, который ответит на все твои вопросы ❓❓❓\n\n<b><i>Пользуйся и делись с друзьями!</i></b>'), 
            reply_markup = InlineKeyboard.AddShare(), 
            parse_mode = "HTML"
            )
    
AdminPanel.decorators.reply_keyboards(Bot, usermanager)	

@Bot.message_handler(content_types=["text"])
def ProcessText(Message: types.Message):
    User = usermanager.auth(Message.from_user)
    if AdminPanel.procedures.text(Bot, User, Message): return

    if User.expected_type == "Question":
        User.set_property("Question", Message.text)
        User.set_property("Generation", True)
        User.set_expected_type(None)

        try:
            Bot.send_chat_action(Message.chat.id, action = "typing")
            Completed = neurowork.AnswerForUser(Message.chat.id, User.get_property("Question"), User)
            if Completed:
                User.set_property("Generation", False)
                Message = Bot.send_animation(
                    Message.chat.id,
                    animation = StartImage,
                    caption = None,
                    reply_markup = InlineKeyboard.SendMainMenu(),
                    parse_mode = "HTML"
                    )
        except Exception as ExceptionData: print(ExceptionData)

        User.set_property("Generation", False)

    else: 
        if User.get_property("Generation"): pass
        else:
            User.set_property("Generation", True)
            User.set_property("Question", Message.text)
            User.set_expected_type(None)
            Bot.send_chat_action(Message.chat.id, action = "typing")
            Completed = neurowork.AnswerForUser(Message.chat.id, User.get_property("Question"), User)
            if Completed:
                User.set_property("Generation", False)
                Message = Bot.send_animation(
                    Message.chat.id,
                    animation= StartImage,
                    caption = None,
                    reply_markup = InlineKeyboard.SendMainMenu(),
                    parse_mode = "HTML"
                    )

AdminPanel.decorators.inline_keyboards(Bot, usermanager)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("for_restart"))
def InlineButtonAccept(Call: types.CallbackQuery):
    User = usermanager.auth(Call.from_user)
    try:
        Bot.delete_message(
            Call.message.chat.id,
            Call.message.id
        )
    except: pass
    ProcessCommandStart(Call.message)
    Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("Subscribe"))
def InlineButtonAllTaro(Call: types.CallbackQuery):
    User = usermanager.auth(Call.from_user)
    if not IsSubscripted(MasterBot, User, Settings, InlineKeyboard):
        Bot.answer_callback_query(Call.id)
        return
    
@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("for_delete"))
def InlineButtonAccept(Call: types.CallbackQuery):
    User = usermanager.auth(Call.from_user)
    try: 
        Bot.delete_message(
            Call.message.chat.id,
            Call.message.id
        )
    except: pass
    Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("notifications"))
def InlineButton(Call: types.CallbackQuery):
    User = usermanager.auth(Call.from_user)
    if not IsSubscripted(MasterBot, User, Settings, InlineKeyboard):
        Bot.answer_callback_query(Call.id)
        return
    
    Command = Call.data.split("_")[-1]

    if Command == "yes":
        User.set_property("mailing", True)
        Bot.edit_message_text(
            chat_id = User.id, 
            text = _("Благодарим! Теперь ваше утро будет начинаться с магии карт Таро! 🥰"),
            message_id = Call.message.id,
            reply_markup = InlineKeyboard.for_restart("Спасибо!")
            )

    else:
        User.set_property("mailing", False)
        Bot.edit_message_text(
            text = _("Хорошо! Вы в любой момент сможете посмотреть <b>Карту дня</b> из главного меню ☺️"),
            chat_id = User.id,
            message_id = Call.message.id,
            parse_mode = "HTML",
            reply_markup = InlineKeyboard.for_restart("Спасибо!")
        )

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("Card_Day"))
def InlineButtonCardDay(Call: types.CallbackQuery):
    User = usermanager.auth(Call.from_user)
    if not IsSubscripted(MasterBot, User, Settings, InlineKeyboard):
        Bot.answer_callback_query(Call.id)
        return
    InstantCard = Card.GetInstantCard()
    if InstantCard:
        Bot.send_photo(
                            Call.message.chat.id,
                            photo = InstantCard["photo"],
                            caption = InstantCard["text"], 
                            reply_markup = InlineKeyboard.for_delete("Да будет так!"),
                            parse_mode = 'HTML'
                        )
    else:
        Photo, Text = Card.GetCard()
        Message = Bot.send_photo(
                        Call.message.chat.id,
                        photo = open(f"{Photo}", "rb"),
                        caption = Text, 
                        reply_markup = InlineKeyboard.for_delete("Да будет так!"),
                        parse_mode = 'HTML'
                    )
        
        Card.AddCard(Message.photo[0].file_id)
        
    Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("Yes_No"))
def InlineButtonCardDay(Call: types.CallbackQuery):
    User = usermanager.auth(Call.from_user)
    if not IsSubscripted(MasterBot, User, Settings, InlineKeyboard):
        Bot.answer_callback_query(Call.id)
        return
    
    Bot.send_message(
        Call.message.chat.id, 
        text = _("Загадай ситуацию, где ответ должен быть <b>Да</b> или <b>Нет</b>.\n\nКак будешь готов, нажми на \"Открыть карту\""), 
        reply_markup = InlineKeyboard.OpenCard(),
        parse_mode = "HTML")
    
    Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("OpenCard"))
def InlineButtonCardDay(Call: types.CallbackQuery):
    User = usermanager.auth(Call.from_user)
    try:
        Bot.delete_message(
            Call.message.chat.id,
            Call.message.id
            )
    except: pass
    
    image, choice_type = Card.ChoiceRandomCard()
    if choice_type == "Straight":
        cards = reader.Get_StraightCard
        values = reader.Get_StraightValues

    if choice_type == "Reversed":
        cards = reader.Get_ReversedCard
        values = reader.Get_ReversedValues
    
    card, value = Card.Get_Text(image, cards, values)
    try:
        File = Cacher.get_cached_file(image, type = types.InputMediaPhoto)
        # Получение ID кэшированного файла.
        PhotoID = Cacher[image]
    except Exception:
        pass

    sleep(1)
    Bot.send_photo(
        Call.message.chat.id, 
        photo = PhotoID,
        caption = f"<b>{card}</b>\n\nВаш ответ: <b>{value}</b>",
        reply_markup = InlineKeyboard.for_delete("Благодарю!"),
        parse_mode = "HTML")
    
    Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("Value_Card"))
def InlineButtonValueCard(Call: types.CallbackQuery):
    User = usermanager.auth(Call.from_user)
    if not IsSubscripted(MasterBot, User, Settings, InlineKeyboard):
        Bot.answer_callback_query(Call.id)
        return

    Bot.edit_message_caption(
        caption = _("ЗНАЧЕНИЕ КАРТ"),
        chat_id = Call.message.chat.id,
        message_id = Call.message.id,
        reply_markup = InlineKeyboard.SendTypeCard()
        )
    
    Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("Cups"))
def InlineButtonCups(Call: types.CallbackQuery):
    User = usermanager.auth(Call.from_user)
    if not IsSubscripted(MasterBot, User, Settings, InlineKeyboard):
        Bot.answer_callback_query(Call.id)
        return
    if "_" in Call.data:
        Bot.delete_message(Call.message.chat.id, Call.message.id)
        Card.SendCardValues(Call, User)
    else:
        Bot.edit_message_reply_markup(Call.message.chat.id, Call.message.id, reply_markup = InlineKeyboard.SendFirstCups())
    
    Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("Swords"))
def InlineButtonSwords(Call: types.CallbackQuery):
    User = usermanager.auth(Call.from_user)
    if not IsSubscripted(MasterBot, User, Settings, InlineKeyboard):
        Bot.answer_callback_query(Call.id)
        return
    if "_" in Call.data:
        Bot.delete_message(Call.message.chat.id, Call.message.id)
        Card.SendCardValues(Call, User)
    else:
        Bot.edit_message_reply_markup(Call.message.chat.id, Call.message.id, reply_markup = InlineKeyboard.SendFirstSwords())

    Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("Wands"))
def InlineButtonWands(Call: types.CallbackQuery):
    User = usermanager.auth(Call.from_user)
    if not IsSubscripted(MasterBot, User, Settings, InlineKeyboard):
        Bot.answer_callback_query(Call.id)
        return
    if "_" in Call.data:
        Bot.delete_message(Call.message.chat.id, Call.message.id)
        Card.SendCardValues(Call, User)
    else:
        Bot.edit_message_reply_markup(Call.message.chat.id, Call.message.id, reply_markup = InlineKeyboard.SendFirstWands())

    Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("Pentacles"))
def InlineButtonPentacles(Call: types.CallbackQuery):
    User = usermanager.auth(Call.from_user)
    if not IsSubscripted(MasterBot, User, Settings, InlineKeyboard):
        Bot.answer_callback_query(Call.id)
        return
    if "_" in Call.data:
        Bot.delete_message(Call.message.chat.id, Call.message.id)
        Card.SendCardValues(Call, User)
    else:
        Bot.edit_message_reply_markup(Call.message.chat.id, Call.message.id, reply_markup = InlineKeyboard.SendFirstPentacles())
    
    Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("Arcanas"))
def InlineButtonArcanas(Call: types.CallbackQuery):
    User = usermanager.auth(Call.from_user)
    if not IsSubscripted(MasterBot, User, Settings, InlineKeyboard):
        Bot.answer_callback_query(Call.id)
        return
    if "_" in Call.data:
        Bot.delete_message(Call.message.chat.id, Call.message.id)
        Card.SendCardValues(Call, User)
    else:
        Bot.edit_message_reply_markup(Call.message.chat.id, Call.message.id, reply_markup = InlineKeyboard.SendFirstArcanas())
    
    Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("Back"))
def InlineButtonBack(Call: types.CallbackQuery):
    User = usermanager.auth(Call.from_user)

    if not IsSubscripted(MasterBot, User, Settings, InlineKeyboard):
        Bot.answer_callback_query(Call.id)
        return
    
    if "_" not in Call.data:
        Bot.delete_message(
            chat_id = Call.message.chat.id,
            message_id = Call.message.id,
        )
        Current_place = User.get_property("Current_place").split("_")[0]
        Bot.send_animation(
            animation = StartImage,
            caption = _("ЗНАЧЕНИЕ КАРТ"),
            chat_id = Call.message.chat.id,
            reply_markup = InlineKeyboard.ChoiceFunction(f"SendFirst{Current_place}"),
            parse_mode= "HTML"
        )
    else:
        Target = Call.data.split("_")[-1]
        if Target == "SendMainMenu":
            Bot.edit_message_caption(
                caption = None,
                chat_id = Call.message.chat.id,
                message_id = Call.message.id,
                reply_markup = InlineKeyboard.ChoiceFunction(Target), 
                parse_mode= "HTML"
            )
            return
        
        if Target == "SendTypeCard":
            Bot.edit_message_caption(
                caption = _("ЗНАЧЕНИЕ КАРТ"),
                chat_id = Call.message.chat.id,
                message_id = Call.message.id,
                reply_markup = InlineKeyboard.SendTypeCard(),
                parse_mode= "HTML"
            )
            return
        
        if Target == "SendValueCard":
            if User.get_property("Current_place").split("_")[0] == "Arcanas" and User.get_property("Card_name"):
                senior_lasso = _("СТАРШИЙ АРКАН")
                Bot.edit_message_caption(caption = f"<b> {senior_lasso} «{User.get_property("Card_name")}»</b>", chat_id = Call.message.chat.id, message_id = Call.message.id, reply_markup = InlineKeyboard.ChoiceFunction(Target), parse_mode="HTML")
            else:
                Bot.edit_message_caption(caption = f"<b>«{User.get_property("Card_name")}»</b>", chat_id = Call.message.chat.id, message_id = Call.message.id, reply_markup = InlineKeyboard.ChoiceFunction(Target), parse_mode="HTML")
            return
        else:
            Bot.edit_message_caption(caption = _("ЗНАЧЕНИЕ КАРТ"), chat_id = Call.message.chat.id, message_id = Call.message.id, reply_markup = InlineKeyboard.ChoiceFunction(Target), parse_mode="HTML")
 
    Bot.answer_callback_query(Call.id)
    
@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("Further"))
def InlineButtonFuther(Call: types.CallbackQuery):
    User = usermanager.auth(Call.from_user)
    if not IsSubscripted(MasterBot, User, Settings, InlineKeyboard):
        Bot.answer_callback_query(Call.id)
        return
    Target = Call.data.split("_")[-1]
    Bot.edit_message_reply_markup(Call.message.chat.id, Call.message.id, reply_markup = InlineKeyboard.ChoiceFunction(Target))
    Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("GeneralMeaning"))
def InlineButtonGeneralMeaning(Call: types.CallbackQuery):
    User = usermanager.auth(Call.from_user)
    if not IsSubscripted(MasterBot, User, Settings, InlineKeyboard):
        Bot.answer_callback_query(Call.id)
        return

    Bot.delete_message(Call.message.chat.id, Call.message.id)
    CardPosition = User.get_property("Current_place")
    ID = CardPosition.split("_")[-1]
    Type = CardPosition.split("_")[0]

    for folder2 in os.listdir(f"Materials/Values/{Type}"):
        if folder2.split(".")[0] == ID:
            with open(f"Materials/Values/{Type}/{folder2}/1.txt") as file:
                FirstString = file.readline()
                Text = file.read().strip()
                FinalText = "<b>" + FirstString + "</b>\n" + Text +"\n\n<b><i>С любовью, @taro100_bot!</i></b>"
                Card.SendCardValues(Call, User, FinalText)

    Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("PersonalState"))
def InlineButtonPersonalState(Call: types.CallbackQuery):
    User = usermanager.auth(Call.from_user)
    if not IsSubscripted(MasterBot, User, Settings, InlineKeyboard):
        Bot.answer_callback_query(Call.id)
        return

    
    Bot.delete_message(Call.message.chat.id, Call.message.id)
    CardPosition = User.get_property("Current_place")
    ID = CardPosition.split("_")[-1]
    Type = CardPosition.split("_")[0]

    for folder2 in os.listdir(f"Materials/Values/{Type}"):
        if folder2.split(".")[0] == ID:
            with open(f"Materials/Values/{Type}/{folder2}/2.txt") as file:
                FirstString = file.readline()
                Text = file.read().strip()
                FinalText = "<b>" + FirstString + "</b>\n" + Text +"\n\n<b><i>С любовью, @taro100_bot!</i></b>"

                Card.SendCardValues(Call, User, FinalText)
        
    Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("DeepLevel"))
def InlineButtonDeepLevel(Call: types.CallbackQuery):
    User = usermanager.auth(Call.from_user)
    if not IsSubscripted(MasterBot, User, Settings, InlineKeyboard):
        Bot.answer_callback_query(Call.id)
        return

    Bot.delete_message(Call.message.chat.id, Call.message.id)
    CardPosition = User.get_property("Current_place")
    ID = CardPosition.split("_")[-1]
    Type = CardPosition.split("_")[0]

    for folder2 in os.listdir(f"Materials/Values/{Type}"):
        if folder2.split(".")[0] == ID:
            with open(f"Materials/Values/{Type}/{folder2}/3.txt") as file:
                FirstString = file.readline()
                Text = file.read().strip()
                FinalText = "<b>" + FirstString + "</b>\n" + Text +"\n\n<b><i>С любовью, @taro100_bot!</i></b>"
                Card.SendCardValues(Call, User, FinalText)
            
    Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("WorkCareer"))
def InlineButtonWorkCareer(Call: types.CallbackQuery):
    User = usermanager.auth(Call.from_user)
    if not IsSubscripted(MasterBot, User, Settings, InlineKeyboard):
        Bot.answer_callback_query(Call.id)
        return

    Bot.delete_message(Call.message.chat.id, Call.message.id)
    CardPosition = User.get_property("Current_place")
    ID = CardPosition.split("_")[-1]
    Type = CardPosition.split("_")[0]

    for folder2 in os.listdir(f"Materials/Values/{Type}"):
        if folder2.split(".")[0] == ID:
            with open(f"Materials/Values/{Type}/{folder2}/4.txt") as file:
                FirstString = file.readline()
                Text = file.read().strip()
                Ending = _("С любовью, @taro100_bot!")
                FinalText = "<b>" + FirstString + "</b>\n" + Text +f"\n\n<b><i>{Ending}</i></b>"
                Card.SendCardValues(Call, User, FinalText)
            
    Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("Finance"))
def InlineButtonFinance(Call: types.CallbackQuery):
    User = usermanager.auth(Call.from_user)
    if not IsSubscripted(MasterBot, User, Settings, InlineKeyboard):
        Bot.answer_callback_query(Call.id)
        return

    Bot.delete_message(Call.message.chat.id, Call.message.id)
    CardPosition = User.get_property("Current_place")
    ID = CardPosition.split("_")[-1]
    Type = CardPosition.split("_")[0]

    for folder2 in os.listdir(f"Materials/Values/{Type}"):
        if folder2.split(".")[0] == ID:
            with open(f"Materials/Values/{Type}/{folder2}/5.txt") as file:
                FirstString = file.readline()
                Text = file.read().strip()
                Ending = _("С любовью, @taro100_bot!")
                FinalText = "<b>" + FirstString + "</b>\n" + Text +f"\n\n<b><i>{Ending}</i></b>"
                Card.SendCardValues(Call, User, FinalText)
                
    Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("Love"))
def InlineButtonLove(Call: types.CallbackQuery):
    User = usermanager.auth(Call.from_user)
    if not IsSubscripted(MasterBot, User, Settings, InlineKeyboard):
        Bot.answer_callback_query(Call.id)
        return

    Bot.delete_message(Call.message.chat.id, Call.message.id)
    CardPosition = User.get_property("Current_place")
    ID = CardPosition.split("_")[-1]
    Type = CardPosition.split("_")[0]

    for folder2 in os.listdir(f"Materials/Values/{Type}"):
        if folder2.split(".")[0] == ID:
            with open(f"Materials/Values/{Type}/{folder2}/6.txt") as file:
                FirstString = file.readline()
                Text = file.read().strip()
                Ending = _("С любовью, @taro100_bot!")
                FinalText = "<b>" + FirstString + "</b>\n" + Text +f"\n\n<b><i>{Ending}</i></b>"
                Card.SendCardValues(Call, User, FinalText)
        
    Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("HealthStatus"))
def InlineButtonHealthStatus(Call: types.CallbackQuery):
    User = usermanager.auth(Call.from_user)
    if not IsSubscripted(MasterBot, User, Settings, InlineKeyboard):
        Bot.answer_callback_query(Call.id)
        return

    Bot.delete_message(Call.message.chat.id, Call.message.id)
    CardPosition = User.get_property("Current_place")
    ID = CardPosition.split("_")[-1]
    Type = CardPosition.split("_")[0]

    for folder2 in os.listdir(f"Materials/Values/{Type}"):
        if folder2.split(".")[0] == ID:
            with open(f"Materials/Values/{Type}/{folder2}/7.txt") as file:
                FirstString = file.readline()
                Text = file.read().strip()
                Ending = _("С любовью, @taro100_bot!")
                FinalText = "<b>" + FirstString + "</b>\n" + Text +f"\n\n<b><i>{Ending}</i></b>"
                Card.SendCardValues(Call, User, FinalText)
            
    Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("Inverted"))
def InlineButtonInverted(Call: types.CallbackQuery):
    User = usermanager.auth(Call.from_user)
    if not IsSubscripted(MasterBot, User, Settings, InlineKeyboard):
        Bot.answer_callback_query(Call.id)
        return
    
    Bot.delete_message(Call.message.chat.id, Call.message.id)
    CardPosition = User.get_property("Current_place")
    ID = CardPosition.split("_")[-1]
    Type = CardPosition.split("_")[0]

    for folder2 in os.listdir(f"Materials/Values/{Type}"):
        if folder2.split(".")[0] == ID:
            with open(f"Materials/Values/{Type}/{folder2}/8.txt") as file:
                FirstString = file.readline()
                Text = file.read().strip()
                Ending = _("С любовью, @taro100_bot!")
                FinalText = "<b>" + FirstString + "</b>\n" + Text +f"\n\n<b><i>{Ending}</i></b>"

                Card.SendCardValues(Call, User, FinalText)
            
    Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("Order_Layout"))
def InlineButtonRemoveReminder(Call: types.CallbackQuery):
    User = usermanager.auth(Call.from_user)
    if not IsSubscripted(MasterBot, User, Settings, InlineKeyboard):
        Bot.answer_callback_query(Call.id)
        return
    Bot.edit_message_caption(
        _("РАСКЛАД ОТ МАСТЕРА"),
        Call.message.chat.id,
        Call.message.id,
        reply_markup = InlineKeyboard.SendOrderLayout()
        )
    Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("Online_Layout"))
def InlineButtonRemoveReminder(Call: types.CallbackQuery):
    User = usermanager.auth(Call.from_user)
    if not IsSubscripted(MasterBot, User, Settings, InlineKeyboard):
        Bot.answer_callback_query(Call.id)
        return
    Bot.send_chat_action(Call.message.chat.id, action = "typing")
    
    if not User.get_property("Generation"):
        Bot.send_message(
            Call.message.chat.id,
            _("Дорогой мой друг, задай мне вопрос, который больше всего тебя сейчас волнует!"))
        User.set_expected_type("Question")
    
    Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("All_Taro"))
def InlineButtonAllTaro(Call: types.CallbackQuery):
    User = usermanager.auth(Call.from_user)
    if not IsSubscripted(MasterBot, User, Settings, InlineKeyboard):
        Bot.answer_callback_query(Call.id)
        return
    Bot.edit_message_caption(
        _("ВСЁ О ТАРО"),
        Call.message.chat.id,
        Call.message.id,
        reply_markup = InlineKeyboard.SendAllTaro()
        )
    Bot.answer_callback_query(Call.id)

AdminPanel.decorators.photo(Bot, usermanager)

@Bot.message_handler(content_types = ["audio", "document", "video", "voice"])
def File(Message: types.Message):
    User = usermanager.auth(Message.from_user)
    AdminPanel.procedures.files(Bot, User, Message)

Bot.infinity_polling()
