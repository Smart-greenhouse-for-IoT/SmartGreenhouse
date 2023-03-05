import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import json
import requests
import time

class Telegram_Bot:
    """Some response of the bot"""

    def __init__(self):
        self.conf = json.load(open("telegram_bot\\setting.json"))
        self.tokenBot = self.conf["token"]
        self.bot = telepot.Bot(self.tokenBot)
        MessageLoop(self.bot, {'chat': self.on_chat_message,
                               'callback_query' : self.on_callback_query}).run_as_thread()

    def on_chat_message(self, msg): 
        """This is actually the main of the bot"""
        content_type, chat_type, chat_ID = telepot.glance(msg)
        #if chat_ID not in self.chatIDs:   # this line maybe is needed for security????
        #    self.chatIDs.append(chat_ID)
        message = msg['text']

        if (message.find('_')>0): #This mean that i have the information that the command is carrying
            command, Name, userID = message.split('_') 

            if command == "/addUser":            
                self.newUser = {"username": Name,
                                "userID": userID}
                buttons = [[InlineKeyboardButton(text=f'Yes', callback_data=f'Add_User_True'), #TODO:trovare un modo per togliere la selezione grafica del pulsante su telegram(davvero brutto da vedere)
                            InlineKeyboardButton(text=f'No', callback_data=f'Add_User_False')]]
                keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
                self.bot.sendMessage(chat_ID, text=f"The new user is:\n {self.newUser}") #TODO: scriverlo in un modo più carino???
                self.bot.sendMessage(chat_ID, text='Is the data correct?', reply_markup=keyboard)

            elif command == "/addPlant":
                pass
        else:
            if message == "/help": #choosing the action to do based on the command received
                self.help(chat_ID)

            elif message == "/start": #welcome message
                self.start(chat_ID)

            elif message == "/addUser":
                text_Add = ("To add a new user write in this way:\n"
                            "/addUser_Name_ID \n")
                self.bot.sendMessage(chat_ID, text=text_Add)
            elif message == "/selectGreenhouse":
                self.bot.sendMessage(chat_ID, text="C'mon do something")
            elif message == "/values":
                self.bot.sendMessage(chat_ID, text="C'mon do something")
            elif message == "/plant":
                self.bot.sendMessage(chat_ID, text="C'mon do something")
            elif message == "/irrigate":
                self.bot.sendMessage(chat_ID, text="C'mon do something")
            elif message.startswith('/'):
                self.bot.sendMessage(chat_ID, text="Command not supported")
            
    def on_callback_query(self, msg):
        """callback query function:
                - it will elabrate the information when a button is pressed"""
        
        query_ID, chat_ID, query_data = telepot.glance(msg, flavor='callback_query') #query_data is the callback data write in the buttons
        action, place, doing = query_data.split('_')

        if action == 'Add': #Action of adding something to the catalog
            if place == 'Plant':
                pass

            elif place == 'User': #Adding a new user to the catalog
                if doing == "True":
                    string = f"http://" + self.conf["CatIP"] + ":" + self.conf["CatPort"] + "/addUser" #URL for POST #TODO: we need a post or a put???
                    requests.post(string, json = self.newUser)
                    self.bot.sendMessage(chat_ID, text=f"User added correctly")
                elif doing == "False":
                    self.bot.sendMessage(chat_ID, text=f"User not added, please repeat the command")
            
            else:
                pass

    def help(self, chat_ID):
        """Send a message when the command /help is received."""

        help_message = ("*You can perform the following actions:*\n" #TODO: comandi help fatti un po a caso, sono tutti da decidere
                    "- /status: Get info about your greenhouses\n"
                    "- /addUser: Add new user\n"
                    "- /addPlant: Add new plant\n" #TODO: decidere se si possono aggiungere piante nuove o se cerchiamo un database già fatto
                    "- /selectGreenhouse: Get ID info about your greenhouse\n"
                    "- /values: Get environmental info for your plant\n"
                    "- /plant: Get info about your plants\n"
                    "- /irrigate: Manually irrigate the selected plants\n")
        self.bot.sendMessage(chat_ID, text=help_message,
                    parse_mode='Markdown')
        
    def start(self, chat_ID):
        """Send a message when the command /start is received."""

        help_message = ("Welcome to the SmartGreenHouse bot 🌱"
                        "\nYou can send /help if you need to see al the commands.")
        self.bot.sendMessage(chat_ID, text=help_message,
                    parse_mode='Markdown')


if __name__ == "__main__":
    Telegram_Bot()
    while 1:
        time.sleep(10)