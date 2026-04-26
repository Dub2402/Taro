from Source.TeleBotAdminPanel.Modules.Statistics import CellData, InlineKeyboards, SM_Statistics
from Source.Modules.AscendTaro import AscendData

from dublib.TelebotUtils import UserData

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

#==========================================================================================#
# >>>>> ДОБАВЛЕНИЕ В ВЫПИСКУ ДОПОЛНИТЕЛЬНЫХ КОЛОНОК <<<<< #
#==========================================================================================#

class CM_Statistics(SM_Statistics):
	"""Кастомный модуль статистики."""

	def _SendStatistics(self, user: "UserData"):

		UsersCount = len(self._Panel.users_manager.users)
		BlockedUsersCount = 0

		for CurrentUser in  self._Panel.users_manager.users:
			if CurrentUser.is_chat_forbidden: BlockedUsersCount += 1

		Counts = (
			len(self._Panel.users_manager.premium_users),
			len(self._Panel.users_manager.get_active_users()),
			AscendData(user).count_referal,
			BlockedUsersCount
		)
		Percentages = [None, None, None, None]

		for Index in range(len(Counts)):
			Percentages[Index] = round(Counts[Index] / UsersCount * 100, 1)
			if str(Percentages[Index]).endswith(".0"): Percentages[Index] = int(Percentages[Index])

		Text = (
			"<b>📊 Статистика</b>\n",
			f"👤 Всего пользователей: <b>{UsersCount}</b>",
			f"⭐ Из них Premium: <b>{Counts[0]}</b> (<i>{Percentages[0]}%</i>)",
			f"🧩 Активных за сутки: <b>{Counts[1]}</b> (<i>{Percentages[1]}%</i>)",
			f"😏 Рефералов: <b>{Counts[2]}</b> (<i>{Percentages[2]}%</i>)",
			f"⛔ Заблокировали: <b>{Counts[3]}</b> (<i>{Percentages[3]}%</i>)"
		)

		self._Panel.bot.send_message(
			chat_id = user.id,
			text = "\n".join(Text),
			parse_mode = "HTML",
			reply_markup = InlineKeyboards.Extract() 
		)