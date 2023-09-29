import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import json
import requests
import time

class Telegram_Bot:
    """
    Telegram_Bot
    ------------
    Some response of the bot
    """

    def __init__(self):
        self.conf = json.load(open("telegram_bot/setting.json"))
        self.tokenBot = self.conf["token"]
        self.bot = telepot.Bot(self.tokenBot)

        self.userConnected = False
        self.grHselected = False
        
        MessageLoop(self.bot, {'chat': self.on_chat_message,
                               'callback_query' : self.on_callback_query}).run_as_thread()
        self.cat_info = {
            "ip": self.conf["CatIP"],
            "port": self.conf["CatPort"]
        }
        self.user = {
            "usrID":  "",
            "name":  "",
            "ghID": [],
            "ownedPlants": [],
            "lastUpdate": ""
        }
                
            
        


    def on_chat_message(self, msg): 
        """
        on_chat_message
        ---------------
        This is actually the main of the bot
        """

        content_type, chat_type, chat_ID = telepot.glance(msg)
        #if chat_ID not in self.chatIDs:   # this line maybe is needed for security????
        #    self.chatIDs.append(chat_ID)
        message = msg['text']

        if (message.find('_')>0): #This mean that i have the information that the command is carrying
            message = message.split('_')
            command = message.pop(0)
            parameters = message

            if len(parameters) == 2:

                if  command == "/signup":
                    if self.userConnected == False:            
                        newUser = self.user.copy()
                        newUser["usrID"] = parameters[1]
                        newUser["name"] = parameters[0]

                        addr = "http://" + self.cat_info["ip"] + ":" + self.cat_info["port"]
                        
                        try:
                            req = requests.get(addr  + f"/user?usrID={newUser['usrID']}")
                        except:
                            raise Exception("The catalog web service is unreachable!")
                        
                        if req.ok:              
                            self.bot.sendMessage(chat_ID, text=f"The user {parameters[1]} already exist!")
                        else:
                            req = requests.post(addr + "/addUser", json.dumps(newUser))
                            self.bot.sendMessage(chat_ID, text=f"User {parameters[0]} {parameters[1]} correctly created.")
                    else:
                        self.bot.sendMessage(chat_ID, text=f"You are already logged with user {self.user['name']} {self.user['usrID']}.")

                
                elif command == "/signin":
                    if self.userConnected == False:            
                        self.user["usrID"] = parameters[1],
                        self.user["name"] = parameters[0]
                        
                        addr = "http://" + self.cat_info["ip"] + ":" + self.cat_info["port"] + f"/user?usrID={self.user['usrID']}"
                        try:
                            req = requests.get(addr)
                        except:
                            raise Exception("The catalog web service is unreachable!")

                        if req.ok:              
                            usr = req.json()
                            if usr['name'] == self.user['name']:
                                self.bot.sendMessage(chat_ID, text=f"Logged in with user: {parameters[0]} {parameters[1]}")
                                self.userConnected = True
                            else:
                                self.bot.sendMessage(chat_ID, text=f"The name {self.user['name']} does not match\
                                                                                        with the existing user!")

                            if usr["ghID"] == []:
                                self.bot.sendMessage(chat_ID, text=f"No greenhouses found, add your first greenhouse."
                                                                    "\n /addGreenhouse")
                            else:
                                self.bot.sendMessage(chat_ID, text=f"Select one greenhouse /selectGreenhouse")
                                
                        else:
                            self.bot.sendMessage(chat_ID, text=f"User {self.user['usrID']} not found!")
                    else:

                        self.bot.sendMessage(chat_ID, text=f"You are already logged with user {self.user['name']} {self.user['usrID']}.")
                        buttons = [[InlineKeyboardButton(text=f'Yes', callback_data=f'signout_none_none'), 
                                    InlineKeyboardButton(text=f'No', callback_data=f'none_none_none')]]
                        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
                        self.bot.sendMessage(chat_ID, text=f"Do you want to log out and enter with another user?",
                                                        parse_mode='Markdown', reply_markup=keyboard)

            elif len(parameters) == 3:
                if self.userConnected == True:
                    if command == "/addPlant":
                        if parameters[1] >= 0 and parameters[1] <= 1 and parameters[2] >= 0 and parameters[2] <= 1 and parameters[1] < parameters[2]:
                            newPlant = {
                                "plant": "",
                                "th_min": 0,
                                "th_max": 0
                            }
                            #TODO: fox salva la nuova pianta nel catalog
                            
                        else:
                            self.bot.sendMessage(chat_ID, text="Humidity threshold format not correct."
                                                                "\nPlease reinsert the command.")

                else:
                    self.bot.sendMessage(chat_ID, text=f"User not connected."
                                                        "\nPlease first sign in with a user clicking on /start")
            else:
                self.bot.sendMessage(chat_ID, text=f"Number of parameters for command {command} not correct!")

        else:
            
            if self.userConnected == True:
                if self.grHselected == True:
                    # 
                    if message == "/values":
                        self.bot.sendMessage(chat_ID, text="C'mon do something")
                    # 
                    elif message == "/plant":
                        self.bot.sendMessage(chat_ID, text="C'mon do something")
                    # 
                    elif message == "/irrigate":
                        self.bot.sendMessage(chat_ID, text="C'mon do something")
                    # 
                    elif message == "/addGrHousePlant":
                        self.bot.sendMessage(chat_ID, text="C'mon do something")

                # Help message when the user is connected
                if message == "/help": 
                    self.help(chat_ID)

                # Welcome message when the user is connected
                elif message == "/start": 
                    self.start(chat_ID)
                
                # When received this message a new empty greenhouse is istantly created
                elif message == "/addGreenhouse":
                    self.bot.sendMessage(chat_ID, text=f"Greenhouse ... correctly added.")

                # 
                elif message == "/selectGreenhouse":
                    self.bot.sendMessage(chat_ID, text=f"{self.user['name']} you have {len(self.user['ghID'])} greenhouses."
                                                        "\nWhich one do you want to select?")
                    
                # Used to specify the correct command to add a new plant to the user database
                elif message == "/addPlant":
                    self.bot.sendMessage(chat_ID, text="Add a new plant to the user database."
                                                        "\nPlease write it in this way:"
                                                        "\n/addPlant_Name_lowHumidityTresh_highHumidityTresh"
                                                        "\nWhere the last two data are the level of humidity treshold in %"
                                                        "\nThe humidity thresold are numbers that goes from 0 to 1")
                
                elif message.startswith('/'):
                    self.bot.sendMessage(chat_ID, text="Command not supported")
                else:
                    self.bot.sendMessage(chat_ID, text="Word/words not recognized. Please start with command /start")
            else:
                if message == "/help": 
                    self.help(chat_ID)

                elif message == "/start": 
                    self.start(chat_ID)

                elif message == "/addGreenhouse" or message == "/selectGreenhouse" or message == "/addPlant":
                    self.bot.sendMessage(chat_ID, text=f"User not connected."
                                                        "\nPlease first sign in with a user clicking on /start")
                    
                elif message == "/addPlant" or message == "/values" or message == "/plant" or message == "/irrigate":
                    self.bot.sendMessage(chat_ID, text=f"User not connected."
                                                        "\nPlease first sign in with a user clicking on /start")
                else:
                    self.bot.sendMessage(chat_ID, text="Word/words not recognized. Please start with command /start")
            
    def on_callback_query(self, msg):
        """
        on_callback_query
        -----------------
        Callback query function:
            - it will elaborate the information when a button is pressed
        """
        
        query_ID, chat_ID, query_data = telepot.glance(msg, flavor='callback_query') #query_data is the callback data write in the buttons
        action, place, doing = query_data.split('_')

        if action == 'Add': # Action of adding something to the catalog
            if place == 'Plant':
                pass

            elif place == 'User': # Adding a new user to the catalog
                if doing == "True":
                    text_Add = ("To sign up write it in this way:\n"
                                "/signup_Name_ID \n")
                    self.bot.sendMessage(chat_ID, text=text_Add)
                elif doing == "False":
                    self.bot.sendMessage(chat_ID, text=f"User not added, please repeat the command.")
            
            else:
                pass
        elif action == 'signin':

            text_Add = ("To sign in into your account write it in this way:\n"
                            "/signin_Name_ID \n")
            self.bot.sendMessage(chat_ID, text=text_Add)

        elif action == 'signout':
            self.userConnected = False
            self.bot.sendMessage(chat_ID, text=f"User correctly signed out."
                                                "\nPlease sign in with another user clicking on /start")

        elif action == 'none':
            pass


    def help(self, chat_ID):
        """
        help
        ----
        Send a message when the command /help is received.
        """

        if self.userConnected == True and self.grHselected == False:
            help_message = ("*You can perform the following actions:*\n" 
                        "- /status: Get info about your greenhouses\n" #???
                        "- /addPlant: Add new plant to the user database\n"
                        "- /selectGreenhouse: Get the ID of your greenhouse to select one\n"
                        "- /addGreenhouse: Add a new empty greenhouse\n")
            
        elif self.userConnected == True and self.grHselected == True:
            help_message = ("*You can perform the following actions:*\n" #TODO: comandi help fatti un po a caso, sono tutti da decidere
                        "- /status: Get info about the greenhouse\n"
                        "- /addGrHousePlant: Add new plant to the greenhouse\n" #TODO: decidere se si possono aggiungere piante nuove o se cerchiamo un database già fatto
                        "- /selectGreenhouse: Get ID info about your greenhouse\n"
                        "- /plant: Get info about your plants\n"
                        "- /irrigate: Manually irrigate the selected plants\n")
        else:
            help_message = ("*Before doing anything please log in into your account*\n" 
                        "- /start: Sign in or sign up commands\n")
            
        self.bot.sendMessage(chat_ID, text=help_message,
                    parse_mode='Markdown')
        
    def start(self, chat_ID):
        """
        start
        -----
        Send a message when the command /start is received.
        """

        if self.userConnected == True:
            message = ("Welcome to the SmartGreenHouse bot 🌱"
                        "\nHere you will able to manage your plants and greenhouses."
                        f"\n{self.user['name']} if you need any help press /help")
            self.bot.sendMessage(chat_ID, text=message,
                        parse_mode='Markdown')
        else:
            message = ("Welcome to the SmartGreenHouse bot 🌱"
                            "\nHere you will able to manage your plants and greenhouses."
                            "\nPlease start with the registration or log in.")
            buttons = [[InlineKeyboardButton(text=f'Sign up', callback_data=f'Add_User_True'), 
                        InlineKeyboardButton(text=f'Sign in', callback_data=f'signin_none_none')]]
            keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
            self.bot.sendMessage(chat_ID, text=message,
                        parse_mode='Markdown', reply_markup=keyboard)



if __name__ == "__main__":

    Telegram_Bot()
    while 1:
        time.sleep(10)