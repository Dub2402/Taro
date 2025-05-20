def heading_suits(type_card: str) -> str:
	"""
	Получение заголовка для клавиатуры мастей.

	:param type_card: Cups, Swords, Wands, Pentacles, Arcanas
	:type type_card: str
	:return: МАСТЬ КУБКОВ, МАСТЬ МЕЧЕЙ, МАСТЬ ЖЕЗЛОВ, МАСТЬ ПЕНТАКЛЕЙ, СТАРШИЕ АРКАНЫ
	:rtype: str
	"""
	  
	if type_card == "Cups": title = "МАСТЬ КУБКОВ"
	if type_card == "Swords": title = "МАСТЬ МЕЧЕЙ"
	if type_card == "Wands": title = "МАСТЬ ЖЕЗЛОВ"
	if type_card == "Pentacles": title = "МАСТЬ ПЕНТАКЛЕЙ"
	if type_card == "Arcanas": title = "СТАРШИЕ АРКАНЫ"

	return title