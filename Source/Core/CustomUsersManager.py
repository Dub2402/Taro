from Source.Modules.AscendTaro import AscendData, Sender as AscendSender, ManagerPromoCodes

from dublib.TelebotUtils import UsersManager, UserData
from dublib.TelebotUtils.Cache import TeleCache

from telebot import types, TeleBot

class CustomUsersManager(UsersManager):
	"""Модифицированный менеджер пользователей."""

	def __CheckLevelUp(self, user: UserData) -> int:
		"""
		Проверяет, повысился ли уровень пользователя от взаимодействия.

		:param user: Данные пользователя.
		:type user: UserData
		:return: Текущий уровень таробота. 
		:rtype: int
		"""

		level = None

		ascend_data = AscendData(user = user)
			
		if ascend_data.is_available_time_based_level_up: return ascend_data.level_tarobot + 1 
		
		elif ascend_data.is_available_user_based_level_up and ascend_data.level_tarobot == 4: return ascend_data.level_tarobot + 1 
			
		return level
			
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

		try: 
			ascend_data = AscendData(user = UserCurrent)
			if ascend_data.is_need_data_update(): ascend_data.incremente_days_with_bot()

			level = self.__CheckLevelUp(UserCurrent)
			
			if level: 

				ascend_data = AscendData(user = UserCurrent)
				ascend_data.set_level_tarobot(level)
				ascend_data.set_level_up_rewards(level = level, manager_promocode = self.__promocode_manager)

				AscendSender(self.__Bot, self.__Cacher).level_up(user = UserCurrent, level = ascend_data.level_tarobot)
				
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

	def set_manager_promocodes(self, promocode_manager: ManagerPromoCodes):
		"""
		Задаёт менеджера промокодов.

		:param bot: Менеджер промокодов.
		:type bot: ManagerPromoCodes
		"""

		self.__promocode_manager = promocode_manager