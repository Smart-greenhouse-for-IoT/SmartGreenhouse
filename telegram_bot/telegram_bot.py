import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import json
import requests
import time

#FIXME: sometimes a lot of exception arrives and to resolve it the catalog must be restarted. true problem not found
#TODO: in /addGreenhouse fare in modo di poter mettere più devices (quindi piu parametri)

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
        
        MessageLoop(self.bot, {'chat': self.on_chat_message,
                               'callback_query' : self.on_callback_query}).run_as_thread()
        self.cat_info = {
            "ip": self.conf["CatIP"],
            "port": self.conf["CatPort"]
        }
        self.addr_cat = "http://" + self.cat_info["ip"] + ":" + self.cat_info["port"]

        #TODO: IDEA: taking the basic configuration from the catalog???
        self.userConnected = False
        self.grHselected = False
        self.plantSelected = False

        self.user = {
            "usrID": "",
            "name": "",
            "ghID": [],
            "ownedPlants": [],
            "lastUpdate": ""
        } 

        self.greenhouse = {
            "ghID": "",
            "devID": "",
            "usrID": "",
            "maxNumPlants": "",
            "plantsList": [],
            "lastUpdate": ""
        }

        self.plant = {
            "plant": "",
            "th_min": "",
            "th_max": ""
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
            
            if len(parameters) == 1: 
                if  command == "/signup":
                    if self.userConnected == False:            
                        newUser = self.user.copy()
                        newUser["name"] = parameters[0]
                        
                        try:
                            req = requests.post(self.addr_cat + "/addUser", json.dumps(newUser))
                            req_id = requests.get(self.addr_cat + "/user/recentID")
                        except:
                            raise Exception("The catalog web service is unreachable!")
                            
                        self.bot.sendMessage(chat_ID, text=f"User {parameters[0]} correctly created.")
                        self.bot.sendMessage(chat_ID, text=f"Your ID is {req_id.json()['usrID']}")
                    
                    else:
                        self.bot.sendMessage(chat_ID, text=f"You are already logged with user {self.user['name']} {self.user['usrID']}.")

            elif len(parameters) == 2:
                if command == "/signin":
                    if self.userConnected == False:            
                        self.user["usrID"] = parameters[1]
                        self.user["name"] = parameters[0]
                        
                        try:
                            req = requests.get(self.addr_cat + f"/user?usrID={self.user['usrID']}")
                        except:
                            raise Exception("The catalog web service is unreachable!")

                        if req.ok:              
                            usr = req.json()
                            if usr['name'] == self.user['name']:
                                self.bot.sendMessage(chat_ID, text=f"Logged in with user: {parameters[0]} {parameters[1]}")
                                self.userConnected = True
                                if usr["ghID"] == []:
                                    self.bot.sendMessage(chat_ID, text=f"No greenhouses found, add your first greenhouse."
                                                                    "\n /addgreenhouse")
                                else:
                                    self.user["ghID"] = usr["ghID"]
                                    self.bot.sendMessage(chat_ID, text=f"Select one greenhouse /selectgreenhouse")
                            else:
                                self.bot.sendMessage(chat_ID, text=f"The name {self.user['name']} does not match\
                                                                                        with the existing user!")

                                
                        else:
                            self.bot.sendMessage(chat_ID, text=f"User {self.user['usrID']} not found!")
                    else:
                        self.bot.sendMessage(chat_ID, text=f"You are already logged with user {self.user['name']} {self.user['usrID']}.")
                        buttons = [[InlineKeyboardButton(text=f'Yes', callback_data=f'signout_none_none'), 
                                    InlineKeyboardButton(text=f'No', callback_data=f'none_none_none')]]
                        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
                        self.bot.sendMessage(chat_ID, text=f"Do you want to log out and enter with another user?",
                                                        parse_mode='Markdown', reply_markup=keyboard)
                        
                elif command == "/addgreenhouse":
                    if self.userConnected:
                        self.greenhouse["usrID"] = self.user["usrID"]
                        self.greenhouse["devID"] = parameters[0]
                        self.greenhouse["maxNumPlants"] = parameters[1]
                        #TODO: check that maxNumPlants is <= number of plants sensors in device devID (decidere se farlo o meno)
                        #TODO: controlla di non mettere un devID che è gia stato assegnato
                        try:
                            req_dev = requests.get(self.addr_cat + f"/device?devID={self.greenhouse['devID']}")
                            if req_dev.ok:
                                req_gh = requests.post(self.addr_cat + "/addGreenhouse", json.dumps(self.greenhouse))
                                req_id = requests.get(self.addr_cat + "/greenhouse/recentID")
                                self.greenhouse["ghID"] = req_id.json()["ghID"]
                                # Update user and device adding the new greenhouse
                                self.user["ghID"].append(self.greenhouse["ghID"])
                                req_usr = requests.put(self.addr_cat + f"/updateUser", json.dumps(self.user))
                                device = req_dev.json()
                                device["ghID"] = self.greenhouse["ghID"]
                                req_dev = requests.put(self.addr_cat + f"/updateDevice", json.dumps(device))
                                
                                if req_gh.ok and req_usr.ok:
                                    self.bot.sendMessage(chat_ID, text=f"Greenhouse {self.greenhouse['ghID']} correctly added.")
                                else:
                                    self.bot.sendMessage(chat_ID, text=f"Greenhouse {self.greenhouse['ghID']} has not been added!")

                            else:
                                self.bot.sendMessage(chat_ID, text=f"The device {self.greenhouse['devID']} does not exist!")
                        except:
                            raise Exception("The catalog web service is unreachable!")
                        
                    else:
                        self.bot.sendMessage(chat_ID, text=f"User not connected."
                                                        "\nTo add a greenhouse first you need to sign in with a user clicking on /start")


            elif len(parameters) == 3:
                if self.userConnected == True:
                    if command == "/addplant":
                        if parameters[1].isnumeric() and parameters[2].isnumeric():
                            parameters[1] = int(parameters[1])
                            parameters[2] = int(parameters[2])
                            if parameters[1] >= 0 and parameters[1] <= 100 and parameters[2] >= 0 and parameters[2] <= 100:
                                if parameters[1] < parameters[2]:
                                    newPlant = {
                                        "plant": parameters[0],
                                        "th_min": parameters[1],
                                        "th_max": parameters[2]
                                    }
                                    try:
                                        req = requests.post(self.addr_cat + f"/addPlant?usrID={self.user['usrID']}",
                                                            data=json.dumps(newPlant))
                                    except:
                                        raise Exception("The catalog web service is unreachable!")
                                    if req.ok:
                                        self.bot.sendMessage(chat_ID, text=f"{newPlant['plant']} correctly added to the user database.")
                                    else:
                                        self.bot.sendMessage(chat_ID, text=f"{newPlant['plant']} has not been added to the user database!.")

                                else:
                                    self.bot.sendMessage(chat_ID, text="Low humidity threshold cannot be higher than the high treshold."
                                                                        "\nPlease reinsert the command.")
                            else:
                                self.bot.sendMessage(chat_ID, text="Humidity threshold number out of range."
                                                                    "\nPlease reinsert the command.")
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
                    if message == "/status":
                        self.bot.sendMessage(chat_ID, text="C'mon do something")
                    # 
                    elif message == "/plants":
                        self.bot.sendMessage(chat_ID, text="C'mon do something")
                    # 
                    elif message == "/selectplant":
                        self.bot.sendMessage(chat_ID, text="C'mon do something")
                    # 
                    elif message == "/addgrhouseplant":
                        self.bot.sendMessage(chat_ID, text="C'mon do something")

                    # If plant commands are received before a plant is selected send the proper error message
                    elif message == "/plantstatus" or message == "/irrigate" and self.plantSelected == False :
                        self.bot.sendMessage(chat_ID, text=f"Plant not selected."
                                                            "\nPlease first select a plant with /selectplant")

                    if self.plantSelected == True:
                        if message == "/irrigate":
                            self.bot.sendMessage(chat_ID, text="C'mon do something")
                        # 
                        elif message == "/plantstatus":
                            self.bot.sendMessage(chat_ID, text="C'mon do something")
                        
                # Help message when the user is connected
                if message == "/help": 
                    self.help(chat_ID)

                # Welcome message when the user is connected
                elif message == "/start": 
                    self.start(chat_ID)
                
                # Message for adding a new greenhouse
                elif message == "/addgreenhouse":
                    self.bot.sendMessage(chat_ID, text=f"To add a new greenhouse type the command:"
                                                        "\n/addgreenhouse_devID_maxNumPlants"
                                                        "\nWith devID as the identifier of the device connector of this specific greenhouse.")

                # 
                elif message == "/selectgreenhouse":
                    self.bot.sendMessage(chat_ID, text=f"{self.user['name']} you have {len(self.user['ghID'])} greenhouses."
                                                        "\nWhich one do you want to select?")
                    for i in self.user['ghID']:
                        self.bot.sendMessage(chat_ID, text=f"Greenhouse : /{i}")

                # If the message is one of the greenhouse in the user list then is selected
                elif message[1:] in self.user['ghID']:
                    self.bot.sendMessage(chat_ID, text=f"Greenhouse {message[1:]} selected")
                    self.grHselected = True
                    self.greenhouse["ghID"] = message[1:]
                    #TODO: FOX prendi tutte le informazioni di questa greenhouse selezionata
                    
                # Used to specify the correct command to add a new plant to the user database
                elif message == "/addplant":
                    self.bot.sendMessage(chat_ID, text="Add a new plant to the user database."
                                                        "\nPlease write it in this way:"
                                                        "\n/addplant_Name_lowHumidityTresh_highHumidityTresh"
                                                        "\nWhere the last two data are the level of humidity treshold in %"
                                                        "\nThe humidity thresold are numbers that goes from 0 to 100")
                    
                # If greenhouse or plant commands are received before a greenhouse is selected send the proper error message
                elif message == "/addgrhouseplant" or message == "/status" or message == "/plants" and self.grHselected == False:
                    self.bot.sendMessage(chat_ID, text=f"No greenhouse selected."
                                                        "\nPlease first select a greenhouse with /selectgreenhouse"
                                                        "\nOr create a new one with /addgreenhouse")
                    
                elif message == "/selectplant" or message == "/plantstatus" or message == "/irrigate" and self.grHselected == False :
                    self.bot.sendMessage(chat_ID, text=f"No greenhouse selected."
                                                        "\nPlease first select a greenhouse with /selectgreenhouse"
                                                        "\nOr create a new one with /addgreenhouse")
                        
                elif message.startswith('/'):
                    self.bot.sendMessage(chat_ID, text="Command not supported")

                else:
                    self.bot.sendMessage(chat_ID, text="Word/words not recognized. Please start with command /start")
            else:
                if message == "/help": 
                    self.help(chat_ID)

                elif message == "/start": 
                    self.start(chat_ID)

                elif message == "/addgreenhouse" or message == "/selectgreenhouse" or message == "/addplant":
                    self.bot.sendMessage(chat_ID, text=f"User not connected."
                                                        "\nPlease first sign in with a user clicking on /start")
                    
                elif message == "/addgrhouseplant" or message == "/status" or message == "/plants" or message == "/selectplant":
                    self.bot.sendMessage(chat_ID, text=f"User not connected."
                                                        "\nPlease first sign in with a user clicking on /start")
                elif message == "/plantstatus" or message == "/irrigate" or message == "/selectplant":
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
                                "/signup_Name \n")
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
                        "- /status: Get info about your greenhouses\n" 
                        "- /addplant: Add new plant to the user database\n"
                        "- /selectgreenhouse: Get the ID of your greenhouse to select one\n"
                        "- /addgreenhouse: Add a new empty greenhouse\n")
            
        elif self.userConnected == True and self.grHselected == True and self.plantSelected == False:
            help_message = ("*You can perform the following actions:*\n" 
                        "- /status: Get info about your greenhouses\n" 
                        "- /addplant: Add new plant to the user database\n"
                        "- /selectgreenhouse: Get the ID of your greenhouse to select one\n"
                        "- /addgreenhouse: Add a new empty greenhouse\n"
                        "- /addgrhouseplant: Add new plant to the greenhouse\n"
                        "- /plants: Get the list of the plants of the selected greenhouse\n"
                        "- /selectplant: Get the name of the selected greenhouse plants to select one\n")
            
        elif self.userConnected == True and self.grHselected == True and self.plantSelected == True:
            help_message = ("*You can perform the following actions:*\n"
                        "- /status: Get info about your greenhouses\n" 
                        "- /addplant: Add new plant to the user database\n"
                        "- /selectgreenhouse: Get the ID of your greenhouse to select one\n"
                        "- /addgreenhouse: Add a new empty greenhouse\n"
                        "- /addgrhouseplant: Add new plant to the greenhouse\n"
                        "- /plants: Get the list of the plants of the selected greenhouse\n"
                        "- /selectplant: Get the name of the selected greenhouse plants to select one\n"
                        "- /irrigate: Manually irrigate the selected plants\n"
                        "- /plantstatus: Get info about the selected plant\n")
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