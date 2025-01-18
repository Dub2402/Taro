from dublib.Methods.Filesystem import ReadJSON, WriteJSON
from dublib.TelebotUtils import UsersManager
from dublib.TelebotUtils.Cache import TeleCache

from datetime import datetime
from telebot import types

from telebot import TeleBot
from .InlineKeyboards import InlineKeyboards

import os

class Cards():

    def __GetToday(self):
        today = datetime.today().strftime("%d.%m.%Y")
        return today
    
    def __init__(self, Bot: TeleBot, InlineKeyboard: InlineKeyboards, Cacher: TeleCache) -> None:
        self.__Bot = Bot
        self.__InlineKeyboard = InlineKeyboard
        self.__Cacher = Cacher


    def FindPhoto(self, datekey: str= "today") -> str:
        for photo in os.listdir("Materials/Photo"):
            namephoto = photo.replace(".jpg", "")
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
        Photo = "Materials/Photo/" + self.FindPhoto(datekey)
        TextFile = self.FindText(datekey)
        with open(f"Materials/Texts/{TextFile}") as file:
            self.Text = file.read()

        return Photo, self.Text
        
    def AddCard(self, Photo_ID, datekey: str = "today"):
        try:
            if self.Instant:
                pass
        except: self.Instant = dict()
        if datekey == "today":       
            self.Instant[self.__GetToday()] = {"photo": Photo_ID, "text": self.Text}
        else:
            self.Instant[datekey] = {"photo": Photo_ID, "text": self.Text}
        WriteJSON("Instant.json", self.Instant)

    def SendCardValues(self, Call: types.CallbackQuery, User: UsersManager):
        Type = Call.data.split("_")[0]
        CardID = Call.data.split("_")[-1]
        
        for filename in os.listdir(f"Materials/Values/{Type}"):
            Index = filename.split(".")[0]
            if Index == CardID:

                CardName = filename.split(".")[1].upper()
                User.set_property("Current_place", Call.data)
                User.set_property("Card_name", CardName)

                File = self.__Cacher.get_cached_file(f"Materials/Values/{Type}/{filename}/image.jpg", type = types.InputMediaPhoto)
                FileID = self.__Cacher[f"Materials/Values/{Type}/{filename}/image.jpg"]
                
                self.__Bot.send_photo(
                    Call.message.chat.id, 
                    photo = FileID, 
                    caption = CardName,
                    reply_markup = self.__InlineKeyboard.SendValueCard())