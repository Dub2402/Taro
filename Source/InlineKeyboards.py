from telebot import types

class InlineKeyboards:

	def __init__(self):
		pass

	def SettingsMenu(self) -> types.InlineKeyboardMarkup:
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
		Pentacles = types.InlineKeyboardButton("Пентакли", callback_data = "Order_Layout")
		Arcanas = types.InlineKeyboardButton("Старшие арканы", callback_data = "Arcanas")
	
		# Добавление кнопок в меню.
		Menu.add(Сups, Swords, Wands, Pentacles, Arcanas, row_width= 1) 

		return Menu

	def SendFirstСups(self) -> types.InlineKeyboardMarkup:
		# Кнопочное меню.
		Menu = types.InlineKeyboardMarkup()

		# Генерация кнопок.
		AceСups = types.InlineKeyboardButton("1. Туз кубков", callback_data = "AceСups")
		TwoСups = types.InlineKeyboardButton("2. Двойка кубков", callback_data = "TwoСups")
		ThreeСups = types.InlineKeyboardButton("3. Тройка кубков", callback_data = "ThreeСups")
		FourСups = types.InlineKeyboardButton("4. Четверка кубков", callback_data = "FourСups")
		FiveСups = types.InlineKeyboardButton("5. Пятерка кубков", callback_data = "FiveСups")
		SixСups = types.InlineKeyboardButton("6. Шестерка кубков", callback_data = "SixСups")
		SevenСups = types.InlineKeyboardButton("7. Семерка кубков", callback_data = "SevenСups")
		Further = types.InlineKeyboardButton("Далее", callback_data = "Further")
		Back = types.InlineKeyboardButton("Назад", callback_data = "Back")

		# Добавление кнопок в меню.
		Menu.add(AceСups, TwoСups, ThreeСups, FourСups, FiveСups, SixСups, SevenСups, Further, Back, row_width= 1) 

		return Menu

	def SendSecondСups(self) -> types.InlineKeyboardMarkup:
		# Кнопочное меню.
		Menu = types.InlineKeyboardMarkup()

		EightСups = types.InlineKeyboardButton("8. Восьмерка кубков ", callback_data = "EightСups")
		NineСups = types.InlineKeyboardButton("9. Девятка кубков ", callback_data = "NineСups")
		TenСups = types.InlineKeyboardButton("10. Десятка кубков", callback_data = "TenСups")
		PageСups = types.InlineKeyboardButton("11. Паж кубков", callback_data = "PageСups")
		KnightСups = types.InlineKeyboardButton("12. Рыцарь кубков", callback_data = "KnightСups")
		QueenСups = types.InlineKeyboardButton("13. Королева кубков", callback_data = "QueenСups")
		KingСups = types.InlineKeyboardButton("14. Король кубков", callback_data = "KingСups")
		Back = types.InlineKeyboardButton("Назад", callback_data = "Back")

		# Добавление кнопок в меню.
		Menu.add(EightСups, NineСups, TenСups, PageСups, KnightСups, QueenСups, KingСups, Back, row_width= 1) 

		return Menu

	def SendFirstSwords(self) -> types.InlineKeyboardMarkup:
		# Кнопочное меню.
		Menu = types.InlineKeyboardMarkup()

		# Генерация кнопок.
		AceSwords = types.InlineKeyboardButton("1. Туз мечей", callback_data = "AceSwords")
		TwoSwords = types.InlineKeyboardButton("2. Двойка мечей", callback_data = "TwoSwords")
		ThreeSwords = types.InlineKeyboardButton("3. Тройка мечей", callback_data = "ThreeSwords")
		FourSwords = types.InlineKeyboardButton("4. Четверка мечей", callback_data = "FourSwords")
		FiveSwords = types.InlineKeyboardButton("5. Пятерка мечей", callback_data = "FiveSwords")
		SixSwords = types.InlineKeyboardButton("6. Шестерка мечей", callback_data = "SixSwords")
		SevenSwords = types.InlineKeyboardButton("7. Семерка мечей", callback_data = "SevenSwords")
		Further = types.InlineKeyboardButton("Далее", callback_data = "Further")
		Back = types.InlineKeyboardButton("Назад", callback_data = "Back")

		# Добавление кнопок в меню.
		Menu.add(AceSwords, TwoSwords, ThreeSwords, FourSwords, FiveSwords, SixSwords, SevenSwords, Further, Back, row_width= 1) 

		return Menu
	
	def SendSecondSwords(self) -> types.InlineKeyboardMarkup:
		# Кнопочное меню.
		Menu = types.InlineKeyboardMarkup()

		EightSwords = types.InlineKeyboardButton("8. Восьмерка мечей ", callback_data = "EightSwords")
		NineSwords = types.InlineKeyboardButton("9. Девятка мечей ", callback_data = "NineSwords")
		TenSwords = types.InlineKeyboardButton("10. Десятка мечей", callback_data = "TenSwords")
		PageSwords = types.InlineKeyboardButton("11. Паж мечей", callback_data = "PageSwords")
		KnightSwords = types.InlineKeyboardButton("12. Рыцарь мечей", callback_data = "KnightSwords")
		QueenSwords = types.InlineKeyboardButton("13. Королева мечей", callback_data = "QueenSwords")
		KingSwords = types.InlineKeyboardButton("14. Король мечей", callback_data = "KingSwords")
		Back = types.InlineKeyboardButton("Назад", callback_data = "Back")

		# Добавление кнопок в меню.
		Menu.add(EightSwords, NineSwords, TenSwords, PageSwords, KnightSwords, QueenSwords, KingSwords, Back, row_width= 1) 

		return Menu

	def SendFirstWands(self) -> types.InlineKeyboardMarkup:
		# Кнопочное меню.
		Menu = types.InlineKeyboardMarkup()

		# Генерация кнопок.
		AceWands = types.InlineKeyboardButton("1. Туз жезлов", callback_data = "AceWands")
		TwoWands = types.InlineKeyboardButton("2. Двойка жезлов", callback_data = "TwoWands")
		ThreeWands = types.InlineKeyboardButton("3. Тройка жезлов", callback_data = "ThreeWands")
		FourWands = types.InlineKeyboardButton("4. Четверка жезлов", callback_data = "FourWands")
		FiveWands = types.InlineKeyboardButton("5. Пятерка жезлов", callback_data = "FiveWands")
		SixWands = types.InlineKeyboardButton("6. Шестерка жезлов", callback_data = "SixWands")
		SevenWands = types.InlineKeyboardButton("7. Семерка жезлов", callback_data = "SevenWands")
		Further = types.InlineKeyboardButton("Далее", callback_data = "Further")
		Back = types.InlineKeyboardButton("Назад", callback_data = "Back")

		# Добавление кнопок в меню.
		Menu.add(AceWands, TwoWands, ThreeWands, FourWands, FiveWands, SixWands, SevenWands, Further, Back, row_width= 1) 

		return Menu
	
	def SendSecondWands(self) -> types.InlineKeyboardMarkup:
		# Кнопочное меню.
		Menu = types.InlineKeyboardMarkup()

		EightWands = types.InlineKeyboardButton("8. Восьмерка жезлов ", callback_data = "EightWands")
		NineWands = types.InlineKeyboardButton("9. Девятка жезлов ", callback_data = "NineWands")
		TenWands = types.InlineKeyboardButton("10. Десятка жезлов", callback_data = "TenWands")
		PageWands = types.InlineKeyboardButton("11. Паж жезлов", callback_data = "PageWands")
		KnightWands = types.InlineKeyboardButton("12. Рыцарь жезлов", callback_data = "KnightWands")
		QueenWands = types.InlineKeyboardButton("13. Королева жезлов", callback_data = "QueenWands")
		KingWands = types.InlineKeyboardButton("14. Король жезлов", callback_data = "KingWands")
		Back = types.InlineKeyboardButton("Назад", callback_data = "Back")

		# Добавление кнопок в меню.
		Menu.add(EightWands, NineWands, TenWands, PageWands, KnightWands, QueenWands, KingWands, Back, row_width= 1) 

		return Menu

	def SendFirstPentacles(self) -> types.InlineKeyboardMarkup:
		# Кнопочное меню.
		Menu = types.InlineKeyboardMarkup()

		# Генерация кнопок.
		AcePentacles = types.InlineKeyboardButton("1. Туз жезлов", callback_data = "AcePentacles")
		TwoPentacles = types.InlineKeyboardButton("2. Двойка жезлов", callback_data = "TwoPentacles")
		ThreePentacles = types.InlineKeyboardButton("3. Тройка жезлов", callback_data = "ThreePentacles")
		FourPentacles = types.InlineKeyboardButton("4. Четверка жезлов", callback_data = "FourPentacles")
		FivePentacles = types.InlineKeyboardButton("5. Пятерка жезлов", callback_data = "FivePentacles")
		SixPentacles = types.InlineKeyboardButton("6. Шестерка жезлов", callback_data = "SixPentacles")
		SevenPentacles = types.InlineKeyboardButton("7. Семерка жезлов", callback_data = "SevenPentacles")
		Further = types.InlineKeyboardButton("Далее", callback_data = "Further")
		Back = types.InlineKeyboardButton("Назад", callback_data = "Back")

		# Добавление кнопок в меню.
		Menu.add(AcePentacles, TwoPentacles, ThreePentacles, FourPentacles, FivePentacles, SixPentacles, SevenPentacles, Further, Back, row_width= 1) 

		return Menu	

	def SendSecondPentacles(self) -> types.InlineKeyboardMarkup:

		# Кнопочное меню.
		Menu = types.InlineKeyboardMarkup()

		EightPentacles = types.InlineKeyboardButton("8. Восьмерка жезлов ", callback_data = "EightPentacles")
		NinePentacles = types.InlineKeyboardButton("9. Девятка жезлов ", callback_data = "NinePentacles")
		TenPentacles = types.InlineKeyboardButton("10. Десятка жезлов", callback_data = "TenPentacles")
		PagePentacles = types.InlineKeyboardButton("11. Паж жезлов", callback_data = "PagePentacles")
		KnightPentacles = types.InlineKeyboardButton("12. Рыцарь жезлов", callback_data = "KnightPentacles")
		QueenPentacles = types.InlineKeyboardButton("13. Королева жезлов", callback_data = "QueenPentacles")
		KingPentacles = types.InlineKeyboardButton("14. Король жезлов", callback_data = "KingPentacles")
		Back = types.InlineKeyboardButton("Назад", callback_data = "Back")

		# Добавление кнопок в меню.
		Menu.add(EightPentacles, NinePentacles, TenPentacles, PagePentacles, KnightPentacles, QueenPentacles, KingPentacles, Back, row_width= 1) 

		return Menu
	
	def SendFirstArcanas(self) -> types.InlineKeyboardMarkup:
		# Кнопочное меню.
		Menu = types.InlineKeyboardMarkup()

		# Генерация кнопок.
		Fool = types.InlineKeyboardButton("0. Шут", callback_data = "Fool")
		Mage = types.InlineKeyboardButton("I. Маг", callback_data = "Mage")
		HighPriestess = types.InlineKeyboardButton("II. Верховная жрица", callback_data = "HighPriestess")
		Empress = types.InlineKeyboardButton("Ⅲ. Императрица", callback_data = "Empress")
		Emperor = types.InlineKeyboardButton("Ⅳ. Император", callback_data = "Emperor")
		HighPriest = types.InlineKeyboardButton("Ⅴ. Верховный жрец", callback_data = "HighPriest")
		Lovers = types.InlineKeyboardButton("Ⅵ. Влюбленные", callback_data = "Lovers")
		Further = types.InlineKeyboardButton("Далее", callback_data = "Further")
		Back = types.InlineKeyboardButton("Назад", callback_data = "Back")

		# Добавление кнопок в меню.
		Menu.add(Fool, Mage, HighPriestess, Empress, Emperor, HighPriest, Lovers, Further, Back, row_width= 1) 

		return Menu	

	def SendSecondArcanas(self) -> types.InlineKeyboardMarkup:

		# Кнопочное меню.
		Menu = types.InlineKeyboardMarkup()

		Chariot = types.InlineKeyboardButton("Ⅶ. Колесница", callback_data = "Chariot")
		Justice = types.InlineKeyboardButton("Ⅷ. Справедливость ", callback_data = "Justice")
		Hermit = types.InlineKeyboardButton("Ⅸ. Отшельник", callback_data = "Hermit")
		WheelFortune = types.InlineKeyboardButton("Ⅹ. Колесо Фортуны", callback_data = "WheelFortune")
		Strength = types.InlineKeyboardButton("Ⅺ. Сила", callback_data = "Strength")
		Hanged = types.InlineKeyboardButton("Ⅻ. Повешенный", callback_data = "Hanged")
		Death = types.InlineKeyboardButton("ⅩⅢ. Смерть", callback_data = "Death")
		Further = types.InlineKeyboardButton("Далее", callback_data = "Further")
		Back = types.InlineKeyboardButton("Назад", callback_data = "Back")

		# Добавление кнопок в меню.
		Menu.add(Chariot, Justice, Hermit, WheelFortune, Strength, Hanged, Death, Further, Back, row_width= 1) 

		return Menu
	

	def SendThirdArcanas(self) -> types.InlineKeyboardMarkup:

		# Кнопочное меню.
		Menu = types.InlineKeyboardMarkup()

		Temperance = types.InlineKeyboardButton("ⅩⅣ. Умеренность", callback_data = "Temperance")
		Devil = types.InlineKeyboardButton("ⅩⅤ. Дьявол", callback_data = "Devil")
		Tower = types.InlineKeyboardButton("ⅩⅥ. Башня", callback_data = "Tower")
		Star = types.InlineKeyboardButton("ⅩⅦ. Звезда", callback_data = "Star")
		Moon = types.InlineKeyboardButton("ⅩⅧ. Луна", callback_data = "Moon")
		Sun = types.InlineKeyboardButton("ⅩⅨ. Солнце", callback_data = "Sun")
		Court = types.InlineKeyboardButton("ⅩⅩ. Суд", callback_data = "Court")
		World = types.InlineKeyboardButton("ⅩⅪ. Мир", callback_data = "World")
		Back = types.InlineKeyboardButton("Назад", callback_data = "Back")

		# Добавление кнопок в меню.
		Menu.add(Temperance, Devil, Tower, Star, Moon, Sun, Court, World, Back, row_width= 1) 

		return Menu
	

	


