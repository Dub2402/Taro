from telebot import types

class InlineKeyboards:

	def __init__(self):
		pass

	def ChoiceFunction(self, Target: str):

		Functions = {
			self.SendMainMenu.__name__: self.SendMainMenu,
			self.SendTypeCard.__name__: self.SendTypeCard,
			self.SendFirstСups.__name__: self.SendFirstСups,
			self.SendSecondСups.__name__: self.SendSecondСups,
			self.SendFirstSwords.__name__: self.SendFirstSwords,
			self.SendSecondSwords.__name__: self.SendSecondSwords,
			self.SendFirstWands.__name__: self.SendFirstWands,
			self.SendSecondWands.__name__: self.SendSecondWands,
			self.SendFirstPentacles.__name__: self.SendFirstPentacles,
			self.SendSecondPentacles.__name__: self.SendSecondPentacles,
			self.SendFirstArcanas.__name__: self.SendFirstArcanas,
			self.SendSecondArcanas.__name__: self.SendSecondArcanas,
			self.SendThirdArcanas.__name__: self.SendThirdArcanas,
			self.SendValueCard.__name__: self.SendValueCard,
		}

		return Functions[Target]()
		
	def SendMainMenu(self) -> types.InlineKeyboardMarkup:
		# Кнопочное меню.
		Menu = types.InlineKeyboardMarkup()

		# Генерация кнопок.
		CardDay = types.InlineKeyboardButton("Карта дня", callback_data = "Card_Day")
		ValueCard = types.InlineKeyboardButton("Значения карт", callback_data = "Value_Card")
		OrderLayout = types.InlineKeyboardButton("Заказать расклад", callback_data = "Order_Layout")
	
		# Добавление кнопок в меню.
		Menu.add(CardDay, ValueCard, OrderLayout, row_width= 1) 

		return Menu

	def SendTypeCard(self) -> types.InlineKeyboardMarkup:
		# Кнопочное меню.
		Menu = types.InlineKeyboardMarkup()

		# Генерация кнопок.
		Сups = types.InlineKeyboardButton("Кубки", callback_data = "Сups")
		Swords = types.InlineKeyboardButton("Мечи", callback_data = "Swords")
		Wands = types.InlineKeyboardButton("Жезлы", callback_data = "Wands")
		Pentacles = types.InlineKeyboardButton("Пентакли", callback_data = "Pentacles")
		Arcanas = types.InlineKeyboardButton("Старшие арканы", callback_data = "Arcanas")
		Back = types.InlineKeyboardButton("Назад", callback_data = "Back_SendMainMenu")
	
		# Добавление кнопок в меню.
		Menu.add(Сups, Swords, Wands, Pentacles, Arcanas, Back, row_width= 1) 

		return Menu

	def SendFirstСups(self) -> types.InlineKeyboardMarkup:
		# Кнопочное меню.
		Menu = types.InlineKeyboardMarkup()

		# Генерация кнопок.
		AceСups = types.InlineKeyboardButton("1. Туз кубков", callback_data = "Сups_1")
		TwoСups = types.InlineKeyboardButton("2. Двойка кубков", callback_data = "Сups_2")
		ThreeСups = types.InlineKeyboardButton("3. Тройка кубков", callback_data = "Сups_3")
		FourСups = types.InlineKeyboardButton("4. Четверка кубков", callback_data = "Сups_4")
		FiveСups = types.InlineKeyboardButton("5. Пятерка кубков", callback_data = "Сups_5")
		SixСups = types.InlineKeyboardButton("6. Шестерка кубков", callback_data = "Сups_6")
		SevenСups = types.InlineKeyboardButton("7. Семерка кубков", callback_data = "Сups_7")
		Further = types.InlineKeyboardButton("Далее", callback_data = "Further_SendSecondСups")
		Back = types.InlineKeyboardButton("Назад", callback_data = "Back_SendTypeCard")

		# Добавление кнопок в меню.
		Menu.add(AceСups, TwoСups, ThreeСups, FourСups, FiveСups, SixСups, SevenСups, Further, Back, row_width= 1) 

		return Menu

	def SendSecondСups(self) -> types.InlineKeyboardMarkup:
		# Кнопочное меню.
		Menu = types.InlineKeyboardMarkup()

		EightСups = types.InlineKeyboardButton("8. Восьмерка кубков ", callback_data = "Сups_8")
		NineСups = types.InlineKeyboardButton("9. Девятка кубков ", callback_data = "Сups_9")
		TenСups = types.InlineKeyboardButton("10. Десятка кубков", callback_data = "Сups_10")
		PageСups = types.InlineKeyboardButton("11. Паж кубков", callback_data = "Сups_11")
		KnightСups = types.InlineKeyboardButton("12. Рыцарь кубков", callback_data = "Сups_12")
		QueenСups = types.InlineKeyboardButton("13. Королева кубков", callback_data = "Сups_13")
		KingСups = types.InlineKeyboardButton("14. Король кубков", callback_data = "Сups_14")
		Back = types.InlineKeyboardButton("Назад", callback_data = "Back_SendFirstСups")
		BackTypeCard = types.InlineKeyboardButton("К мастям", callback_data = "Back_SendTypeCard")

		# Добавление кнопок в меню.
		Menu.add(EightСups, NineСups, TenСups, PageСups, KnightСups, QueenСups, KingСups, Back, BackTypeCard, row_width= 1) 

		return Menu

	def SendFirstSwords(self) -> types.InlineKeyboardMarkup:
		# Кнопочное меню.
		Menu = types.InlineKeyboardMarkup()

		# Генерация кнопок.
		AceSwords = types.InlineKeyboardButton("1. Туз мечей", callback_data = "Swords_1")
		TwoSwords = types.InlineKeyboardButton("2. Двойка мечей", callback_data = "Swords_2")
		ThreeSwords = types.InlineKeyboardButton("3. Тройка мечей", callback_data = "Swords_3")
		FourSwords = types.InlineKeyboardButton("4. Четверка мечей", callback_data = "Swords_4")
		FiveSwords = types.InlineKeyboardButton("5. Пятерка мечей", callback_data = "Swords_5")
		SixSwords = types.InlineKeyboardButton("6. Шестерка мечей", callback_data = "Swords_6")
		SevenSwords = types.InlineKeyboardButton("7. Семерка мечей", callback_data = "Swords_7")
		Further = types.InlineKeyboardButton("Далее", callback_data = "Further_SendSecondSwords")
		Back = types.InlineKeyboardButton("Назад", callback_data = "Back_SendTypeCard")

		# Добавление кнопок в меню.
		Menu.add(AceSwords, TwoSwords, ThreeSwords, FourSwords, FiveSwords, SixSwords, SevenSwords, Further, Back, row_width= 1) 

		return Menu
	
	def SendSecondSwords(self) -> types.InlineKeyboardMarkup:
		# Кнопочное меню.
		Menu = types.InlineKeyboardMarkup()

		EightSwords = types.InlineKeyboardButton("8. Восьмерка мечей ", callback_data = "Swords_8")
		NineSwords = types.InlineKeyboardButton("9. Девятка мечей ", callback_data = "Swords_9")
		TenSwords = types.InlineKeyboardButton("10. Десятка мечей", callback_data = "Swords_10")
		PageSwords = types.InlineKeyboardButton("11. Паж мечей", callback_data = "Swords_11")
		KnightSwords = types.InlineKeyboardButton("12. Рыцарь мечей", callback_data = "Swords_12")
		QueenSwords = types.InlineKeyboardButton("13. Королева мечей", callback_data = "Swords_13")
		KingSwords = types.InlineKeyboardButton("14. Король мечей", callback_data = "Swords_14")
		Back = types.InlineKeyboardButton("Назад", callback_data = "Back_SendFirstSwords")
		BackTypeCard = types.InlineKeyboardButton("К мастям", callback_data = "Back_SendTypeCard")

		# Добавление кнопок в меню.
		Menu.add(EightSwords, NineSwords, TenSwords, PageSwords, KnightSwords, QueenSwords, KingSwords, Back, BackTypeCard, row_width= 1) 

		return Menu

	def SendFirstWands(self) -> types.InlineKeyboardMarkup:
		# Кнопочное меню.
		Menu = types.InlineKeyboardMarkup()

		# Генерация кнопок.
		AceWands = types.InlineKeyboardButton("1. Туз жезлов", callback_data = "Wands_1")
		TwoWands = types.InlineKeyboardButton("2. Двойка жезлов", callback_data = "Wands_2")
		ThreeWands = types.InlineKeyboardButton("3. Тройка жезлов", callback_data = "Wands_3")
		FourWands = types.InlineKeyboardButton("4. Четверка жезлов", callback_data = "Wands_4")
		FiveWands = types.InlineKeyboardButton("5. Пятерка жезлов", callback_data = "Wands_5")
		SixWands = types.InlineKeyboardButton("6. Шестерка жезлов", callback_data = "Wands_6")
		SevenWands = types.InlineKeyboardButton("7. Семерка жезлов", callback_data = "Wands_7")
		Further = types.InlineKeyboardButton("Далее", callback_data = "Further_SendSecondWands")
		Back = types.InlineKeyboardButton("Назад", callback_data = "Back_SendTypeCard")

		# Добавление кнопок в меню.
		Menu.add(AceWands, TwoWands, ThreeWands, FourWands, FiveWands, SixWands, SevenWands, Further, Back, row_width= 1) 

		return Menu
	
	def SendSecondWands(self) -> types.InlineKeyboardMarkup:
		# Кнопочное меню.
		Menu = types.InlineKeyboardMarkup()

		EightWands = types.InlineKeyboardButton("8. Восьмерка жезлов ", callback_data = "Wands_8")
		NineWands = types.InlineKeyboardButton("9. Девятка жезлов ", callback_data = "Wands_9")
		TenWands = types.InlineKeyboardButton("10. Десятка жезлов", callback_data = "Wands_10")
		PageWands = types.InlineKeyboardButton("11. Паж жезлов", callback_data = "Wands_11")
		KnightWands = types.InlineKeyboardButton("12. Рыцарь жезлов", callback_data = "Wands_12")
		QueenWands = types.InlineKeyboardButton("13. Королева жезлов", callback_data = "Wands_13")
		KingWands = types.InlineKeyboardButton("14. Король жезлов", callback_data = "Wands_14")
		Back = types.InlineKeyboardButton("Назад", callback_data = "SendFirstWands")
		BackTypeCard = types.InlineKeyboardButton("К мастям", callback_data = "Back_SendTypeCard")

		# Добавление кнопок в меню.
		Menu.add(EightWands, NineWands, TenWands, PageWands, KnightWands, QueenWands, KingWands, Back, BackTypeCard, row_width= 1) 

		return Menu

	def SendFirstPentacles(self) -> types.InlineKeyboardMarkup:
		# Кнопочное меню.
		Menu = types.InlineKeyboardMarkup()

		# Генерация кнопок.
		AcePentacles = types.InlineKeyboardButton("1. Туз пентаклей", callback_data = "Pentacles_1")
		TwoPentacles = types.InlineKeyboardButton("2. Двойка пентаклей", callback_data = "Pentacles_2")
		ThreePentacles = types.InlineKeyboardButton("3. Тройка пентаклей", callback_data = "Pentacles_3")
		FourPentacles = types.InlineKeyboardButton("4. Четверка пентаклей", callback_data = "Pentacles_4")
		FivePentacles = types.InlineKeyboardButton("5. Пятерка пентаклей", callback_data = "Pentacles_5")
		SixPentacles = types.InlineKeyboardButton("6. Шестерка пентаклей", callback_data = "Pentacles_6")
		SevenPentacles = types.InlineKeyboardButton("7. Семерка пентаклей", callback_data = "Pentacles_7")
		Further = types.InlineKeyboardButton("Далее", callback_data = "Further_SendSecondPentacles")
		Back = types.InlineKeyboardButton("Назад", callback_data = "Back_SendTypeCard")

		# Добавление кнопок в меню.
		Menu.add(AcePentacles, TwoPentacles, ThreePentacles, FourPentacles, FivePentacles, SixPentacles, SevenPentacles, Further, Back, row_width= 1) 

		return Menu	

	def SendSecondPentacles(self) -> types.InlineKeyboardMarkup:

		# Кнопочное меню.
		Menu = types.InlineKeyboardMarkup()

		EightPentacles = types.InlineKeyboardButton("8. Восьмерка жезлов ", callback_data = "Pentacles_8")
		NinePentacles = types.InlineKeyboardButton("9. Девятка жезлов ", callback_data = "Pentacles_9")
		TenPentacles = types.InlineKeyboardButton("10. Десятка жезлов", callback_data = "Pentacles_10")
		PagePentacles = types.InlineKeyboardButton("11. Паж жезлов", callback_data = "Pentacles_11")
		KnightPentacles = types.InlineKeyboardButton("12. Рыцарь жезлов", callback_data = "Pentacles_12")
		QueenPentacles = types.InlineKeyboardButton("13. Королева жезлов", callback_data = "Pentacles_13")
		KingPentacles = types.InlineKeyboardButton("14. Король жезлов", callback_data = "Pentacles_14")
		Back = types.InlineKeyboardButton("Назад", callback_data = "Back_SendFirstPentacles")
		BackTypeCard = types.InlineKeyboardButton("К мастям", callback_data = "Back_SendTypeCard")

		# Добавление кнопок в меню.
		Menu.add(EightPentacles, NinePentacles, TenPentacles, PagePentacles, KnightPentacles, QueenPentacles, KingPentacles, Back, BackTypeCard, row_width= 1) 

		return Menu
	
	def SendFirstArcanas(self) -> types.InlineKeyboardMarkup:
		# Кнопочное меню.
		Menu = types.InlineKeyboardMarkup()

		# Генерация кнопок.
		Fool = types.InlineKeyboardButton("𝟬. Шут", callback_data = "Arcanas_1")
		Mage = types.InlineKeyboardButton("Ⅰ. Маг", callback_data = "Arcanas_2")
		HighPriestess = types.InlineKeyboardButton("Ⅱ. Верховная жрица", callback_data = "Arcanas_3")
		Empress = types.InlineKeyboardButton("Ⅲ. Императрица", callback_data = "Arcanas_4")
		Emperor = types.InlineKeyboardButton("Ⅳ. Император", callback_data = "Arcanas_5")
		HighPriest = types.InlineKeyboardButton("Ⅴ. Верховный жрец", callback_data = "Arcanas_6")
		Lovers = types.InlineKeyboardButton("Ⅵ. Влюбленные", callback_data = "Arcanas_7")
		Further = types.InlineKeyboardButton("Далее", callback_data = "Further_SendSecondArcanas")
		Back = types.InlineKeyboardButton("Назад", callback_data = "Back_SendTypeCard")

		# Добавление кнопок в меню.
		Menu.add(Fool, Mage, HighPriestess, Empress, Emperor, HighPriest, Lovers, Further, Back, row_width= 1) 

		return Menu	

	def SendSecondArcanas(self) -> types.InlineKeyboardMarkup:

		# Кнопочное меню.
		Menu = types.InlineKeyboardMarkup()

		Chariot = types.InlineKeyboardButton("Ⅶ. Колесница", callback_data = "Arcanas_8")
		Justice = types.InlineKeyboardButton("Ⅷ. Справедливость ", callback_data = "Arcanas_9")
		Hermit = types.InlineKeyboardButton("Ⅸ. Отшельник", callback_data = "Arcanas_10")
		WheelFortune = types.InlineKeyboardButton("Ⅹ. Колесо Фортуны", callback_data = "Arcanas_11")
		Strength = types.InlineKeyboardButton("Ⅺ. Сила", callback_data = "Arcanas_12")
		Hanged = types.InlineKeyboardButton("Ⅻ. Повешенный", callback_data = "Arcanas_13")
		Death = types.InlineKeyboardButton("ⅩⅢ. Смерть", callback_data = "Arcanas_14")
		Further = types.InlineKeyboardButton("Далее", callback_data = "Further_SendThirdArcanas")
		Back = types.InlineKeyboardButton("Назад", callback_data = "Back_SendFirstArcanas")

		# Добавление кнопок в меню.
		Menu.add(Chariot, Justice, Hermit, WheelFortune, Strength, Hanged, Death, Further, Back, row_width= 1) 

		return Menu
	
	def SendThirdArcanas(self) -> types.InlineKeyboardMarkup:

		# Кнопочное меню.
		Menu = types.InlineKeyboardMarkup()

		Temperance = types.InlineKeyboardButton("ⅩⅣ. Умеренность", callback_data = "Arcanas_15")
		Devil = types.InlineKeyboardButton("ⅩⅤ. Дьявол", callback_data = "Arcanas_16")
		Tower = types.InlineKeyboardButton("ⅩⅥ. Башня", callback_data = "Arcanas_17")
		Star = types.InlineKeyboardButton("ⅩⅦ. Звезда", callback_data = "Arcanas_18")
		Moon = types.InlineKeyboardButton("ⅩⅧ. Луна", callback_data = "Arcanas_19")
		Sun = types.InlineKeyboardButton("ⅩⅨ. Солнце", callback_data = "Arcanas_20")
		Court = types.InlineKeyboardButton("ⅩⅩ. Суд", callback_data = "Arcanas_21")
		World = types.InlineKeyboardButton("ⅩⅪ. Мир", callback_data = "Arcanas_22")
		Back = types.InlineKeyboardButton("Назад", callback_data = "Back_SendSecondArcanas")
		BackTypeCard = types.InlineKeyboardButton("К мастям", callback_data = "Back_SendTypeCard")

		# Добавление кнопок в меню.
		Menu.add(Temperance, Devil, Tower, Star, Moon, Sun, Court, World, Back, BackTypeCard, row_width= 1) 

		return Menu
	
	def SendValueCard(self) -> types.InlineKeyboardMarkup:

		# Кнопочное меню.
		Menu = types.InlineKeyboardMarkup()

		GeneralMeaning = types.InlineKeyboardButton("1. Общее значение", callback_data = "GeneralMeaning")
		PersonalState  = types.InlineKeyboardButton("2. Личностное состояние", callback_data = "PersonalState")
		DeepLevel = types.InlineKeyboardButton("3. На глубоком уровне", callback_data = "DeepLevel")
		WorkCareer = types.InlineKeyboardButton("4. В работе и карьере", callback_data = "WorkCareer")
		Finance = types.InlineKeyboardButton("5. В финансах", callback_data = "Finance")
		Love = types.InlineKeyboardButton("6. В сфере любви ", callback_data = "Love")
		HealthStatus  = types.InlineKeyboardButton("7. Состояние здоровья ", callback_data = "HealthStatus")
		Inverted = types.InlineKeyboardButton("8. Перевернутая карта", callback_data = "Inverted")
		Back = types.InlineKeyboardButton("Назад", callback_data = "Back")

		# Добавление кнопок в меню.
		Menu.add(GeneralMeaning, PersonalState, DeepLevel, WorkCareer, Finance, Love, HealthStatus, Inverted, Back, row_width= 1) 

		return Menu
