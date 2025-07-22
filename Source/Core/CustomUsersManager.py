from Source.Modules.AscendTaro import AscendData, Sender as AscendSender

from dublib.TelebotUtils import UsersManager, UserData
from dublib.TelebotUtils.Cache import TeleCache

from telebot import types, TeleBot

class CustomUsersManager(UsersManager):
	"""Модифицированный менеджер пользователей."""

	def __CheckLevelUp(self, user: UserData):
		"""
		Проверяет, повысился ли уровень пользователя от взаимодействия, и отправляет уведомление.

		:param user: Данные пользователя.
		:type user: UserData
		"""

		message_level_up = None

		ascend_data = AscendData(user = user)
		ascend_sender = AscendSender(self.__Bot, self.__Cacher)

		#СЛУЧАЙ, КОГДА У НАС ОДНОВРЕМЕННО ПОЯВИЛОСЬ 30 ДНЕЙ ПОДРЯД И 10 ПРИГЛАШЁННЫХ ПОЛЬЗОВАТЕЛЕЙ, НО УРОВЕНЬ ТАРОБОТА 3.
		if ascend_data.is_available_time_based_level_up and ascend_data.is_available_user_based_level_up:
			ascend_sender.level_up_users(user = user)
			ascend_data.set_level_tarobot(count = 5)
			return True

		elif ascend_data.is_available_time_based_level_up:
			incremente_level = ascend_data.level_tarobot + 1
			message_level_up = ascend_sender.level_up_time(user = user, level = incremente_level)
		
		elif ascend_data.is_available_user_based_level_up: message_level_up = ascend_sender.level_up_users(user = user)

		if message_level_up: ascend_data.incremente_level_tarobot()

		return False
			
	def auth(self, user: types.User, update_activity: bool = True):
		"""
		Выполняет идентификацию и обновление данных существующего пользователя или создаёт локальный файл для нового.

		:param user: Cтруктура описания пользователя Telegram.
		:type user: User
		:param update_activity: Указывает, нужно ли обновлять активность пользователя. По умолчанию `True`.
		:type update_activity: bool
		"""

		UserCurrent = super().auth(user, update_activity)
		UserCurrent.set_property("name", user.full_name)

		if not UserCurrent.has_property("index"): UserCurrent.set_property("index", self.get_new_index())

		try: self.__CheckLevelUp(UserCurrent)
		except Exception as ExceptionData: print(ExceptionData)

		return UserCurrent
	
	def get_new_index(self) -> int:
		"""
		Генериурет новый порядковый номер для аккаунта.

		:return: Порядковый номер.
		:rtype: int
		"""

		Indexes = list()

		for CurrentUser in self.users:
			if CurrentUser.has_property("index"): Indexes.append(CurrentUser.get_property("index"))

		return max(Indexes) + 1 if Indexes else 1

	def set_bot(self, bot: TeleBot):
		"""
		Задаёт бота Telegram.

		:param bot: Бот Telegram.
		:type bot: TeleBot
		"""

		self.__Bot = bot

	def set_cacher(self, Cacher: TeleCache):
		"""
		Задаёт менеджера кэша.

		:param bot: Менеджер кэша.
		:type bot: TeleCache
		"""

		self.__Cacher = Cacher