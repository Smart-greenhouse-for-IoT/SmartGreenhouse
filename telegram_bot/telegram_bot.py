import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import json
import requests
import time
import cherrypy

class Telegram_Bot:
    """Some response of the bot"""

    def __init__(self, token):
        self.tokenBot = token
        self.bot = telepot.Bot(self.tokenBot)
        MessageLoop(self.bot, {'chat': self.on_chat_message}).run_as_thread()

    def on_chat_message(self, msg): 
        """This is actually the main of the bot"""
        content_type, chat_type, chat_ID = telepot.glance(msg)
        #if chat_ID not in self.chatIDs:
        #    self.chatIDs.append(chat_ID)
        message = msg['text']
        if message == "/help":
            self.help(chat_ID)
        elif message == "/start":
            self.start(chat_ID)
        elif message == "/status":
            self.bot.sendMessage(chat_ID, text="C'mon do something")
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
    
    def help(self, chat_ID):
        """Send a message when the command /help is received."""

        help_message = ("You can perform the following actions:\n"
                    "- /status: Get info about your greenhouses\n"
                    "- /selectGreenhouse: Get ID info about your greenhouse\n"
                    "- /values: Get environmental info for your plant\n"
                    "- /plant: Get info about your plants\n"
                    "- /irrigate: Irrigate the selected plants\n")
        self.bot.sendMessage(chat_ID, text=help_message,
                    parse_mode='Markdown')
        
    def start(self, chat_ID):
        """Send a message when the command /start is received."""

        help_message = ("Welcome to the SmartGreenHouse bot 🌱"
                        "\nYou can send /help if you need to see al the commands.")
        self.bot.sendMessage(chat_ID, text=help_message,
                    parse_mode='Markdown')


if __name__ == "__main__":
    conf = json.load(open("C:\\Users\\aledi\\Desktop\\Alessandro\\PoliTo\\Magistrale\\Programming_IOT\\Lab5\\setting.json"))
    token = conf["token"]
    sb=Telegram_Bot(token)
    while 1:
        time.sleep(10)