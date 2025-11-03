from dublib.TelebotUtils.Cache import TeleCache

from dublib.Engine.Configurator import Config

Settings = Config("Settings.json")
Settings.load()

Cacher = TeleCache()
Cacher.set_bot(Settings["token"])
Cacher.set_chat_id(Settings["chat_id"])