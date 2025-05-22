from dublib.Methods.Filesystem import ReadJSON, WriteJSON
from dublib.TelebotUtils import UserData
from dublib.TelebotUtils.Cache import TeleCache

from .InlineKeyboards import InlineKeyboards
from .Functions import CashingFiles

from datetime import datetime
from telebot import TeleBot, types

import os
import random

class Cards():

    def __GetToday(self):
        today = datetime.today().strftime("%d.%m.%Y")
        return today
    
    def __init__(self, Bot: TeleBot, InlineKeyboard: InlineKeyboards, Cacher: TeleCache) -> None:
        self.__Bot = Bot
        self.__InlineKeyboard = InlineKeyboard
        self.__Cacher = Cacher

    def FindVideo(self, datekey: str= "today") -> str:
        for photo in os.listdir("Materials/Video"):
            namephoto = photo.replace(".mp4", "")
            if datekey == "today":
                if namephoto == self.__GetToday():
                    return photo
            else:
                if namephoto == str(datekey):
                    return photo
            
    def FindText(self, datekey: str= "today"):
      
        for text in os.listdir("Materials/Texts"):
            nametext = text.replace(".txt", "")
            if datekey == "today":
                if nametext == self.__GetToday():
                    return text
            else:
                if nametext == str(datekey):
                    return text
   
    def GetInstantCard(self, datekey: str = "today"):
        try:
            self.Instant = ReadJSON("Instant.json")
        
            for key in self.Instant.keys():
                if datekey == "today":
                    if key == self.__GetToday():
                        return self.Instant[key]
                else:
                    key = str(datekey)
                    return self.Instant[key]
        except: pass

    def GetCard(self, datekey: str = "today"):
        Video = "Materials/Video/" + self.FindVideo(datekey)
        TextFile = self.FindText(datekey)
        with open(f"Materials/Texts/{TextFile}") as file:
            self.Text = file.read()

        return Video, self.Text
        
    def AddCard(self, Video_ID, datekey: str = "today"):
        try:
            if self.Instant:
                pass
        except: self.Instant = dict()
        if datekey == "today":       
            self.Instant[self.__GetToday()] = {"video": Video_ID, "text": self.Text}
        else:
            self.Instant[datekey] = {"video": Video_ID, "text": self.Text}
        WriteJSON("Instant.json", self.Instant)

    def SendCardValues(self, Call: types.CallbackQuery, User: UserData, text: str = ""):
        if text == "":
            Type = Call.data.split("_")[0]
            CardID = Call.data.split("_")[-1]
        else:
            Type = User.get_property("Current_place").split("_")[0]
            CardID = User.get_property("Current_place").split("_")[-1]
        
        for filename in os.listdir(f"Materials/Values/{Type}"):
            Index = filename.split(".")[0]
            if Index == CardID:
                FileID = CashingFiles(self.__Cacher, f"Materials/Values/{Type}/{filename}/image.jpg", types.InputMediaPhoto)

                if text == "":
                    CardName = filename.split(".")[1].upper().strip()
                    User.set_property("Current_place", Call.data)
                    User.set_property("Card_name", CardName)
                    if Type == "Arcanas":
                        self.__Bot.send_photo(
                            Call.message.chat.id, 
                            photo = FileID.file_id, 
                            caption = f"<b>СТАРШИЙ АРКАН «{CardName}»</b>",
                            parse_mode = "HTML",
                            reply_markup = self.__InlineKeyboard.SendValueCard())
                    
                    else:
                        self.__Bot.send_photo(
                            Call.message.chat.id, 
                            photo = FileID.file_id, 
                            caption = f"<b>«{CardName}»</b>",
                            parse_mode = "HTML",
                            reply_markup = self.__InlineKeyboard.SendValueCard())
                else:
                    self.__Bot.send_photo(
                        Call.message.chat.id, 
                        photo = FileID.file_id, 
                        caption = text,
                        parse_mode = "HTML",
                        reply_markup = self.__InlineKeyboard.SendBack()
                        )
                    
    def ChoiceRandomCard(self) -> str:

        image = None
        choice_type = random.choice(["Straight", "Reversed"])
        choice_card = random.randint(1,78) 
        image = f"Materials/{choice_type}/{choice_card}.jpg"
        return image, choice_type
    
    def Get_Text(self, photo: str, cards: list, values: list) -> str:
        index = int(photo.split("/")[-1].replace(".jpg", "")) -1
        card = cards[index]
        value = values[index]
        return card, value
