from Source.TeleBotAdminPanel.Core.Extractor import Extractor, CellData
from Source.TeleBotAdminPanel.UI.ReplyKeyboards import ReplyFunctions
from Source.TeleBotAdminPanel.UI.InlineKeyboards import InlineKeyboards

from Source.Modules.AscendTaro import AscendData
from Source.UI.WorkpiecesMessages import WorkpiecesMessages
from Source.Core.Cacher import Cacher

from dublib.TelebotUtils import UserData, UsersManager

from telebot import types

from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from telebot import TeleBot, types
	from dublib.TelebotUtils import UsersManager

#==========================================================================================#
# >>>>> ДОБАВЛЕНИЕ В ВЫПИСКУ ДОПОЛНИТЕЛЬНЫХ КОЛОНОК <<<<< #
#==========================================================================================#

def get_index(user: UserData) -> CellData:

	Data = CellData()
	if user.has_property("index"): Data.value = user.get_property("index")
	
	return Data

def get_name(user: UserData) -> CellData:

	Data = CellData()
	if user.has_property("name") and user.get_property("name"): Data.value = user.get_property("name")
	
	return Data

def get_registration_date(user: UserData) -> CellData:

	Data = CellData()
	if user.has_property("registration_date") and user.get_property("registration_date"): Data.value = user.get_property("registration_date")
	
	return Data

def get_promocode(user: UserData) -> CellData:

	Data = CellData()
	if user.has_property("ascend") and user.get_property("ascend"): 
		ascend_data = user.get_property("ascend")
		Data.value = ascend_data["promo"]
	
	return Data

def get_level(user: UserData):

	Data = CellData()

	ascend_data = AscendData(user = user)
	if ascend_data: Data.value = ascend_data.level_tarobot
	else: Data.value = 0
	
	return Data

NewColumns = {
	"Index": get_index
}

NewColumns.update(Extractor.Columns)

Extractor.Columns = NewColumns
Extractor.Columns["Name"] = get_name
Extractor.Columns["Registration"] = get_registration_date
Extractor.Columns["Promocode"] = get_promocode
Extractor.Columns["Level"] = get_level

#==========================================================================================#
# >>>>> ДОБАВЛЕНИЕ В ВЫПИСКУ ДОПОЛНИТЕЛЬНЫХ КОЛОНОК <<<<< #
#==========================================================================================#

def NewStatistics(bot: "TeleBot", users: "UsersManager", message: "types.Message"):
		"""
		Обрабатывает Reply-кнопку: 📊 Статистика
			bot – бот Telegram;\n
			users – менеджер пользователей;\n
			message – сообщение от пользователя.
		"""
		User = users.auth(message.from_user)

		UsersCount = len(users.users)
		BlockedUsersCount = 0

		for user in users.users:
			if user.is_chat_forbidden: BlockedUsersCount += 1

		Counts = [len(users.premium_users), len(users.get_active_users()), BlockedUsersCount]
		Percentages = [None, None, None]

		for Index in range(len(Counts)):
			Percentages[Index] = round(Counts[Index] / UsersCount * 100, 1)
			if str(Percentages[Index]).endswith(".0"): Percentages[Index] = int(Percentages[Index])

		count_referal = AscendData(user).count_referal
		Percentages_referal = round(count_referal / UsersCount * 100, 1)
		Text = (
			"<b>📊 Статистика</b>\n",
			f"👤 Всего пользователей: <b>{UsersCount}</b>",
			f"⭐ Из них Premium: <b>{Counts[0]}</b> (<i>{Percentages[0]}%</i>)",
			f"🛞 Активных за сутки: <b>{Counts[1]}</b> (<i>{Percentages[1]}%</i>)",
			f"😏 Рефералов: <b>{AscendData(user).count_referal}</b> (<i>{Percentages_referal}%</i>)",
			f"⛔ Заблокировали: <b>{Counts[2]}</b> (<i>{Percentages[2]}%</i>)",			
		)

		bot.send_message(
			chat_id = message.chat.id,
			text = "\n".join(Text),
			parse_mode = "HTML",
			reply_markup = InlineKeyboards.extract() 
		)

def NewClose(bot: "TeleBot", users: "UsersManager", message: "types.Message"):
	"""
	Обрабатывает Reply-кнопку: ❌ Закрыть
		bot – бот Telegram;\n
		users – менеджер пользователей;\n
		message – сообщение от пользователя.
	"""

	User = users.auth(message.from_user)
	Options = User.get_property("ap")
	Options["is_open"] = False
	User.set_property("ap", Options)
	bot.send_message(
		chat_id = message.chat.id,
		text = "Панель управления закрыта.",
		reply_markup = types.ReplyKeyboardRemove()
	)
	WorkpiecesMessages(bot, Cacher).send_start_messages(User, title = False)

ReplyFunctions.Statistics = NewStatistics
ReplyFunctions.Close = NewClose