from dublib.CLI.Terminalyzer import Terminalyzer, Command
from dublib.TelebotUtils import TeleCache, UsersManager
from telebot import TeleBot, types
from telebot.apihelper import ApiTelegramException
import logging
from time import sleep

COMMANDS: tuple[Command] = (Command("mail", "Запускает рассылку."),)
Analyzer = Terminalyzer()

def MailIt(usermanager: UsersManager, Bot: TeleBot, Cacher: TeleCache):
	user_number = 0
	KEY = "14_02_2"

	for user in usermanager.users:
		sleep(1)
		user_number += 1
		logging.info(f"{user_number} / {len(usermanager.users)}")
		print(f"{user_number} / {len(usermanager.users)}")
		
		try: 
			IsSended = user.get_property(KEY)
			if IsSended: logging.info(f"User {user} skipped as sended.")
			else: logging.info(f"User {user} skipped as NOT sended.")
		except KeyError: pass
		else: continue

		text = (
			"🔥🔥<b>ДЕНЬ ВЛЮБЛЕННЫХ</b>🔥🔥",
			"<i><b>Время, когда можно сблизиться по максимуму со своей половинкой!!!</b></i>\n",
			"Эксклюзивные расклады для тебя:",
			"1) <b>\"Ключ к его сердцу\"</b> - растопи сердце возлюбленного, узнай на какие рычаги нужно давить, что говорить, и как он вообще будет реагировать на все.\n",
			"2) <b>\"По судьбе ли он?\"</b> - если без манипуляций и приемов, давай узнаем, какая у вас совместимость, и что в конечном счете подсказывает вам судьба!\n",
			"3) <b>\"Моя настоящая любовь\"</b> - как выглядит человек твоей жизни, какие у него внутренние и внешние характеристики. Может быть, он уже рядом, а если нет - то когда придет?\n",
			"<i><b>Пиши мне название расклада, по ссылке ниже. Мы все с тобой разберем, и твои волнения уйдут навсегда!</b></i>",
			"⬇️ ⬇️ ⬇️",
			"https://t.me/galina_tarot",
			"https://t.me/galina_tarot",
			"https://t.me/galina_tarot"
		)
		try:

			Bot.send_animation(
				chat_id = user.id,
				animation = Cacher.get_real_cached_file(path = "14_02.mp4", autoupload_type = types.InputMediaAnimation,).file_id,
				caption = "\n".join(text),
				parse_mode = "HTML"
			)
			user.set_property(KEY, True)

		except ApiTelegramException as e:
			logging.error(str(e))
			user.set_property(KEY, False)