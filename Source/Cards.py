from dublib.Methods.JSON import ReadJSON, WriteJSON
from datetime import datetime
from telebot import types
from dublib.TelebotUtils import UsersManager
from telebot import TeleBot
from .InlineKeyboards import InlineKeyboards

import os

class Cards():

    def __GetToday(self):
        today = datetime.today().strftime("%d.%m.%Y")
        return today
    
    def __init__(self, Bot: TeleBot, InlineKeyboard: InlineKeyboards ) -> None:
        self.__Bot = Bot
        self.__InlineKeyboard = InlineKeyboard


    def FindPhoto(self) -> str:
        for photo in os.listdir("Materials/Photo"):
            namephoto = photo.replace(".jpg", "")
            if namephoto == self.__GetToday():
                return photo
            
    def FindText(self):
      
        for text in os.listdir("Materials/Texts"):
            nametext = text.replace(".txt", "")
            if nametext == self.__GetToday():
                return text
   
    def GetInstantCard(self):
        try:
            self.Instant = ReadJSON("Instant.json")
        
            for key in self.Instant.keys():
                if key == self.__GetToday():
                    return self.Instant[key]
                else:
                    pass
        except: pass

    def GetCard(self):
        Photo = "Materials/Photo/" + self.FindPhoto()
        TextFile = self.FindText()
        with open(f"Materials/Texts/{TextFile}") as file:
            self.Text = file.read()

        return Photo, self.Text
        

    def AddCard(self, Photo_ID):
        try:
            if self.Instant:
                pass
        except: self.Instant = dict()
                
        self.Instant[self.__GetToday()] = {"photo": Photo_ID, "text": self.Text}
        WriteJSON("Instant.json", self.Instant)


    def SendCardValues(self, Call: types.CallbackQuery, User: UsersManager):
        Type = Call.data.split("_")[0]
        CardID = Call.data.split("_")[-1]
        
        for filename in os.listdir(f"Materials/Values/{Type}"):
            Index = filename.split(".")[0]
            if Index == CardID:

                CardName = filename.split(".")[1].upper()
                User.set_property("Current_place", Call.data)
                self.__Bot.send_photo(
                    Call.message.chat.id, 
                    photo = open(f"Materials/Values/{Type}/{filename}/image.jpg", "rb"), 
                    caption = CardName,
                    reply_markup = self.__InlineKeyboard.SendValueCard())