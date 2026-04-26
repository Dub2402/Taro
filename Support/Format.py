from dublib.Methods.Filesystem import ListDir, MakeRootDirectories

import os

def format_card_day():

	if not os.path.exists("Materials/Texts_bot"): MakeRootDirectories("Materials/Texts_bot")
	for file_original in ListDir("Materials/Texts"):

		if file_original in ListDir("Materials/Texts_bot"): continue
		else:
			with open(f"Materials/Texts/{file_original}") as file:
				text = file.read()

			start = True
			lines = text.split("\n")
			collected = []

			for line in lines: 
				if line.strip() == "❤️ЛЮБОВЬ И ОТНОШЕНИЯ❤️": 
					start = False 
					continue 
				if line.strip() == "⭐️ДРУГИЕ СФЕРЫ⭐️": 
					start = True 
					continue 
				if line.strip() == "🙏СОВЕТ ДНЯ🙏": 
					start = True 
					continue 
				if start: collected.append(line) 
			
		new_text = "\n".join(collected) + "\n\n<i><b>С любовью, Галина Таро Мастер!</b></i>"
		with open(f"Materials/Texts_bot/{file_original}", "w", encoding = "utf-8") as f:
			f.write(new_text)