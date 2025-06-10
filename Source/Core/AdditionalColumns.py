from Source.TeleBotAdminPanel.Core.Extractor import Extractor, CellData

from dublib.TelebotUtils import UserData

#==========================================================================================#
# >>>>> ДОБАВЛЕНИЕ В ВЫПИСКУ ДОПОЛНИТЕЛЬНЫХ КОЛОНОК <<<<< #
#==========================================================================================#

def get_name(user: UserData) -> CellData:

  Data = CellData()
  if user.has_property("name") and user.get_property("name"): Data.value = user.get_property("name")
  
  return Data

Extractor.Columns["Name"] = get_name