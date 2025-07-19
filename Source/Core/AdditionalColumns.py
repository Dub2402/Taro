from Source.TeleBotAdminPanel.Core.Extractor import Extractor, CellData

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

NewColumns = {
	"Index": get_index
}
NewColumns.update(Extractor.Columns)

Extractor.Columns = NewColumns
Extractor.Columns["Name"] = get_name
Extractor.Columns["Registration"] = get_registration_date