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
        # Used to not print wrong commands
        done = False

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
                
                elif command == "/addgrhouseplant": 
                    if self.userConnected == True:
                        if self.grHselected == True:
                            # in param[0] there is the plant name
                            # TODO: FOX qua bisogna controllare che la pianta esista nel database, se esiste aggiungila alla serra selezionata
                            pass
                        else:
                            self.bot.sendMessage(chat_ID, text=f"Greenhouse not selected."
                                                        "\nPlease first select a greenhouse with /selectgreenhouse"
                                                        "\nOr create a new one with /addgreenhouse")
                    else:
                        self.bot.sendMessage(chat_ID, text=f"User not connected."
                                                "\nTo add a greenhouse plant, first you need to sign in with a user clicking on /start")
                else:
                    self.bot.sendMessage(chat_ID, text=f"Number of parameters for command {command} not correct!")

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
                        buttons = [[InlineKeyboardButton(text=f'Yes', callback_data=f'signout'), 
                                    InlineKeyboardButton(text=f'No', callback_data=f'none')]]
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
                                                        "\nTo add a greenhouse, first you need to sign in with a user clicking on /start")
                else:
                    self.bot.sendMessage(chat_ID, text=f"Number of parameters for command {command} not correct!")

            elif len(parameters) == 3:
                # Check if the user is correctly connected
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
                        self.bot.sendMessage(chat_ID, text=f"Number of parameters for command {command} not correct!")
                else:
                    self.bot.sendMessage(chat_ID, text=f"User not connected."
                                                        "\nPlease first sign in with a user clicking on /start")
            else:
                self.bot.sendMessage(chat_ID, text=f"Number of parameters for command {command} not correct!")

        else:
            if self.userConnected == True:
                if self.grHselected == True:
                    # Check the status of the selected greenhouse, including: humidity, temperature and number of plants
                    if message == "/status":
                        done = True
                        #TODO: FOX qui bisogna prendere le informazioni di temperatura e umidità più recenti dal catalog.
                        self.bot.sendMessage(chat_ID, text=f"In greenhouse {self.greenhouse['ghID']} there are n gradi % umidità"
                                                    f"\nNumber of plants: {len(self.greenhouse['plantsList'])}"
                                                    "\nIf you want the list of the plants of this greenhouse click /plants")
                        
                    # Check and print all the plant list of the selected greenhouse
                    elif message == "/plants":
                        done = True
                        if len(self.greenhouse['plantsList']) > 0:
                            self.bot.sendMessage(chat_ID, text=f"The list of plants of greenhouse {self.greenhouse['ghID']} is:")
                            for i in self.greenhouse['plantsList']:
                                self.bot.sendMessage(chat_ID, text=f"/{i}")
                        else:
                            self.bot.sendMessage(chat_ID, text=f"There are no plants in greenhouse {self.greenhouse['ghID']}"
                                                                "\nTo add a plant click on /addgrhouseplant")

                    # Inform the user how to obtain all the name of the plants of the selected greenhouse
                    elif message == "/selectplant":
                        done = True
                        self.bot.sendMessage(chat_ID, text="If you want to select a specific plant obtain the greenhouse list with /plants")

                    # If we have a greenhouse selected and we receive a command message of a plant present in this greenhouse, then this plant is selected
                    elif message[1:] in self.greenhouse['plantsList']:
                        done = True
                        self.bot.sendMessage(chat_ID, text=f"{message[1:]} plant selected")
                        self.plantSelected = True
                        self.plantSelected["plant"] = message[1:]
                        #TODO: FOX ottieni le info della pianta selezionata

                    # Inform the user to the complete command to add a plant to the greenhouse
                    elif message == "/addgrhouseplant":
                        done = True
                        self.bot.sendMessage(chat_ID, text="To add a plant to the greenhouse write:"
                                                        "\n/addgrhouseplant_NameOfThePlant")
                        text = ("Do you want the list of the user plants?")
                        buttons = [[InlineKeyboardButton(text=f'Yes', callback_data=f'plants'), 
                                    InlineKeyboardButton(text=f'No', callback_data=f'none')]]
                        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
                        self.bot.sendMessage(chat_ID, text=text, parse_mode='Markdown', reply_markup=keyboard)

                    # If plant commands are received before a plant is selected send the proper error message
                    elif (message == "/plantstatus" or message == "/irrigate") and not self.plantSelected:
                        done = True
                        self.bot.sendMessage(chat_ID, text=f"Plant not selected."
                                                            "\nPlease first select a plant with /selectplant")
                        
                    # If a plant is selected then other commands are unlocked
                    if self.plantSelected == True:
                        # Manually activate the irrigation on the selected plant
                        if message == "/irrigate":
                            done = True
                            self.bot.sendMessage(chat_ID, text="C'mon do something")
                        
                        # Obtain the plant information like its humidity treshold (low and high) and the last moisture level measured
                        elif message == "/plantstatus":
                            done = True
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

                # If present print of all the greenhouse of the user selected
                elif message == "/selectgreenhouse":
                    self.plantSelected = False
                    self.bot.sendMessage(chat_ID, text=f"{self.user['name']} you have {len(self.user['ghID'])} greenhouses."
                                                        "\nWhich one do you want to select?")
                    for i in self.user['ghID']:
                        self.bot.sendMessage(chat_ID, text=f"Greenhouse : /{i}")

                # If the message is one of the greenhouse in the user list then is selected
                elif message[1:] in self.user['ghID']:
                    self.bot.sendMessage(chat_ID, text=f"Greenhouse {message[1:]} selected")
                    self.grHselected = True
                    self.greenhouse["ghID"] = message[1:]
                    try:
                        req = requests.get(self.addr_cat + f"/greenhouse?ghID={self.greenhouse['ghID']}")
                    except:
                        raise Exception("The catalog web service is unreachable!")
                    if req.ok:
                        self.greenhouse = req.json()
                    else:
                        self.bot.sendMessage(chat_ID, text=f"An error occured when selecting greenhouse {self.greenhouse['ghID']}!")
                    
                # Used to specify the correct command to add a new plant to the user database
                elif message == "/addplant":
                    self.bot.sendMessage(chat_ID, text="Add a new plant to the user database."
                                                        "\nPlease write it in this way:"
                                                        "\n/addplant_Name_lowHumidityTresh_highHumidityTresh"
                                                        "\nWhere the last two data are the level of humidity treshold in %"
                                                        "\nThe humidity thresold are numbers that goes from 0 to 100")
                    
                # If greenhouse or plant commands are received before a greenhouse is selected send the proper error message
                elif (message == "/addgrhouseplant" or message == "/status" or message == "/plants") and not self.grHselected:
                    self.bot.sendMessage(chat_ID, text=f"No greenhouse selected."
                                                        "\nPlease first select a greenhouse with /selectgreenhouse"
                                                        "\nOr create a new one with /addgreenhouse")
                    
                elif (message == "/selectplant" or message == "/plantstatus" or message == "/irrigate") and not self.grHselected:
                    self.bot.sendMessage(chat_ID, text=f"No greenhouse selected."
                                                        "\nPlease first select a greenhouse with /selectgreenhouse"
                                                        "\nOr create a new one with /addgreenhouse")
                        
                elif message.startswith('/') and not done:
                    self.bot.sendMessage(chat_ID, text="Command not supported")

                elif not done:
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
                elif message.startswith('/'):
                    self.bot.sendMessage(chat_ID, text="Command not supported")
                else:
                    self.bot.sendMessage(chat_ID, text="Word/words not recognized. Please start with command /start")
            
    def on_callback_query(self, msg):
        """
        on_callback_query
        -----------------
        Callback query function:
            - it will elaborate the information when a button is pressed
        """
        
        query_ID, chat_ID, action = telepot.glance(msg, flavor='callback_query') #query_data is the callback data write in the buttons

        if action == 'signin': 
            self.bot.sendMessage(chat_ID, text="To sign up write it in this way:\n"
                                                "/signup_Name \n")
        
        # When the signin button is pressed 
        elif action == 'signin':
            self.bot.sendMessage(chat_ID, text="To sign in into your account write it in this way:\n"
                                                "/signin_Name_ID \n")

        # If the user will signout then all the previous selection must be setted to false
        elif action == 'signout':
            self.userConnected = False
            self.grHselected = False
            self.plantSelected = False
            self.bot.sendMessage(chat_ID, text=f"User correctly signed out."
                                                "\nPlease sign in with another user clicking on /start")
        
        # If the user does not remember which plant have in its database they can be all printed
        elif action == 'plants':
            #TODO: FOX qui c'è bisogno di stampare tutte le piante di questo user
            self.bot.sendMessage(chat_ID, text=f"Plant list:")

        # When 'No' buttons are clicked
        elif action == 'none':
            self.bot.sendMessage(chat_ID, text=f"No action done")


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
                        "- /status: Get info about your greenhouse\n" 
                        "- /addplant: Add new plant to the user database\n"
                        "- /selectgreenhouse: Get the ID of your greenhouse to select one\n"
                        "- /addgreenhouse: Add a new empty greenhouse\n"
                        "- /addgrhouseplant: Add new plant to the greenhouse\n"
                        "- /plants: Get the list of the plants of the selected greenhouse\n"
                        "- /selectplant: Get the name of the selected greenhouse plants to select one\n")
            
        elif self.userConnected == True and self.grHselected == True and self.plantSelected == True:
            help_message = ("*You can perform the following actions:*\n"
                        "- /status: Get info about your greenhouse\n" 
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
            buttons = [[InlineKeyboardButton(text=f'Sign up', callback_data=f'signup'), 
                        InlineKeyboardButton(text=f'Sign in', callback_data=f'signin')]]
            keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
            self.bot.sendMessage(chat_ID, text=message,
                        parse_mode='Markdown', reply_markup=keyboard)



if __name__ == "__main__":

    Telegram_Bot()
    while 1:
        time.sleep(10)