import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import json
import requests
import time

class Telegram_Bot:
    """Some response of the bot"""

    def __init__(self):
        conf = json.load(open("telegram_bot\setting.json"))
        self.tokenBot = conf["token"]
        self.bot = telepot.Bot(self.tokenBot)
        MessageLoop(self.bot, {'chat': self.on_chat_message,
                               'callback_query' : self.on_callback_query}).run_as_thread()

    def on_chat_message(self, msg): 
        """This is actually the main of the bot"""
        content_type, chat_type, chat_ID = telepot.glance(msg)
        #if chat_ID not in self.chatIDs:   # this line maybe is needed for security????
        #    self.chatIDs.append(chat_ID)
        message = msg['text']
        if message == "/help": #choosing the action to do based on the command received
            self.help(chat_ID)
        elif message == "/start":
            self.start(chat_ID)
        elif message == "/add":
            buttons = [[InlineKeyboardButton(text=f'Add User', callback_data=f'Add_User'),
                        InlineKeyboardButton(text=f'Add Plant', callback_data=f'Add_Plant'),
                        InlineKeyboardButton(text=f'Add GreenHouse', callback_data=f'Add_Greenhouse'),
                        InlineKeyboardButton(text=f'Add lot', callback_data=f'Add_lot')]]
            keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
            self.bot.sendMessage(chat_ID, text='Add Command List', reply_markup=keyboard)
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
            query_ID, chat_ID, query_data = telepot.glance(msg, flavor='callback_query') #query_data is the callback data write in the buttons
            action, place = query_data.split('_')
            if action == 'Add':
                if place == 'Plant':
                    self.bot.sendMessage(chat_ID, text=f"Insert the name of the new plant")
                    self.plantname = True
                elif place == '':
                    pass
    
    def help(self, chat_ID):
        """Send a message when the command /help is received."""

        help_message = ("*You can perform the following actions:*\n"
                    "- /status: Get info about your greenhouses\n"
                    "- /add: Add new component\n"
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