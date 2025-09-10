from dublib.Methods.Filesystem import ListDir

from os import PathLike
from datetime import datetime

PATH_VIDEO = "Materials/Video"
PATH_TEXTS = "Materials/Texts"
PATH_CHOICE_CARD = "Materials/ChoiceCard"


class Informator:

	def latest_video():
		valid_dates = []

		for video in ListDir(PATH_VIDEO):
		
			video_date = video.replace(".mp4", "")
			date_obj = datetime.strptime(video_date, "%d.%m.%Y")
			valid_dates.append(date_obj)
		latest: datetime = max(valid_dates)

		print(latest)

		date = latest.strftime("%d.%m.%Y")

		print(date)

		return latest
		
	latest_video()



	def find_latest(path: PathLike, type_format: str):

		valid_dates = []

		for name_file in ListDir(PATH_VIDEO):
		
			name_file_except_suffix = name_file.replace(type_format, "")
			date_obj = datetime.strptime(name_file_except_suffix, "%d.%m.%Y")
			valid_dates.append(date_obj)

		latest_date: datetime = max(valid_dates)
		latest_name_file = latest_date.strftime("%d.%m.%Y") + type_format

		return latest_name_file