import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import json
import requests
import time

from tools import searchDict

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

        self.DA_connected = False
        self.DA_info()    

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
            "devices": [],
            "usrID": "",
            "gh_params":{
                "temperature": "",
                "CO2_level": "",
                "humidity": ""
            },
            "plantsList": [],
            "lastUpdate": ""
        }

        self.plant = {
            "plant": "",
            "th_min": "",
            "th_max": "",
            "sensID":"",
            "actID":"",
            "devID":""
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

        #####################################
        ######### MULTIPLE COMMANDS #########
        #####################################

        if (message.find('_')>0): 
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
                            self.bot.sendMessage(chat_ID, text=f"User {parameters[0]} correctly created.")
                            self.bot.sendMessage(chat_ID, text=f"Your ID is {req_id.json()['usrID']}")
                        except:
                            self.bot.sendMessage(chat_ID, text=f"Sorry, in this moment the catalog web service is unreachable! Try again later.")
                    
                    else:
                        self.bot.sendMessage(chat_ID, text=f"You are already logged with user {self.user['name']} {self.user['usrID']}.")
                
                elif command == "/addgrhousedevice":
                    if self.userConnected == True: 
                        if self.grHselected == True:

                            try:
                                req_dev = requests.get(self.addr_cat + f"/device?devID={parameters[0]}")
                                r_assigned_dev = requests.get(self.addr_cat + 
                                                            f"/greenhouse?devID={parameters[0]}")
                                if req_dev.ok:
                                    device = req_dev.json()
                                    if not r_assigned_dev.ok:
                                        # Assign sensors to greenhouse
                                        for sensor in device["resources"]["sensors"]:
                                            for service in sensor["services_details"]:
                                                if service["service_type"] == "MQTT":
                                                    for topic in service["topic"]:
                                                        if "temperature" in topic:
                                                            sens_temp =  sensor["sensID"]
                                                        elif "CO2_level" in topic:
                                                            sens_co2 = sensor["sensID"]
                                        
                                        # Assign actuators to greenhouse
                                        for sensor in device["resources"]["actuators"]:
                                            for service in sensor["services_details"]:
                                                if service["service_type"] == "MQTT":
                                                    for topic in service["topic"]:
                                                        if "fan_control" in topic:
                                                            act_fan= sensor["actID"]
                                                        elif "vaporizer_control" in topic:
                                                            act_vap = sensor["actID"]
                                                        elif "co2_control" in topic:
                                                            act_co = sensor["actID"]
                                                            
                                        self.greenhouse["devices"].append(
                                            {
                                                "devID": parameters[0],
                                                "sensors":{
                                                    "temp_hum": sens_temp,
                                                    "CO2_level": sens_co2 
                                                },
                                                "actuators": {
                                                    "fan_control": act_fan,
                                                    "vaporizer_control": act_vap,
                                                    "co2_control": act_co
                                                }
                                            }
                                            )
                                        req_gh = requests.put(self.addr_cat + "/updateGreenhouse", json.dumps(self.greenhouse))
                                        self.bot.sendMessage(chat_ID, text=f"Device {parameters[0]} correctly added"
                                                                        f" in greenhouse {self.greenhouse['ghID']}.")
                                    
                                    else:
                                        self.bot.sendMessage(chat_ID, text=f"The device {parameters[0]} is already used by"
                                                            " another greenhouse!")

                                else:
                                    self.bot.sendMessage(chat_ID, text=f"The device {parameters[0]} does not exist!")
                            except:
                                self.bot.sendMessage(chat_ID, text=f"Sorry, in this moment the catalog web service is unreachable! Try again later.")
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
                        except:
                            self.bot.sendMessage(chat_ID, text=f"Sorry, in this moment the catalog web service is unreachable! Try again later.")

                    else:
                        self.bot.sendMessage(chat_ID, text=f"You are already logged with user {self.user['name']} {self.user['usrID']}.")
                        buttons = [[InlineKeyboardButton(text=f'Yes', callback_data=f'signout'), 
                                    InlineKeyboardButton(text=f'No', callback_data=f'none')]]
                        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
                        self.bot.sendMessage(chat_ID, text=f"Do you want to log out and enter with another user?",
                                                        parse_mode='Markdown', reply_markup=keyboard)
                
                # Add a owned plant to the selected greenhouse 
                elif command == "/addgrhouseplant": 
                    if self.userConnected == True:
                        if self.grHselected == True:
                            device = parameters[0]
                            plant_name = parameters[1]
                            
                            # Check which sensors and actuators are already used by the device
                            used_sens = [plant["sensID"] for plant in self.greenhouse["plantsList"] 
                                         if plant["devID"] == device]
                            used_act = [plant["actID"] for plant in self.greenhouse["plantsList"] 
                                         if plant["devID"] == device]
                            
                            try:
                                req_plant = requests.get(self.addr_cat + f"/user?usrID={self.user['usrID']}&plant={plant_name}")
                                req_sens = requests.get(self.addr_cat + f"/device/sensors?devID={device}")
                                req_act = requests.get(self.addr_cat + f"/device/actuators?devID={device}")

                                # Assign a sensor and actuator to the plant to be added
                                if req_sens.ok and req_act.ok:
                                    sensors = req_sens.json()
                                    actuators = req_act.json()

                                    all_sens = [sens["sensID"] for sens in sensors if sens["device_name"] == "chirp"]
                                    all_act = [act["actID"] for act in actuators]

                                    free_sens = [sens for sens in all_sens if sens not in used_sens]
                                    free_act = [act for act in all_act if act not in used_act]

                                    # Check if there are sensor available
                                    try:
                                        sensID = free_sens.pop(0)
                                        actID = free_act.pop(free_act.index("a" + sensID[1:]))
                                    except:
                                        self.bot.sendMessage(chat_ID, text=f"Device {device} does not have more free sensor!")
                                else:
                                    self.bot.sendMessage(chat_ID, text=f"Device {device} does not exist!")
                                

                                # Check if the plant exist in user owned plants
                                if req_plant.ok: 
                                    
                                    # Check if there is a free sensors to be assigned
                                    if sensID and actID:
                                        plant = req_plant.json()

                                        # Add device, sensor, actuators info to the plant
                                        plant["devID"] = device
                                        plant["sensID"] = sensID
                                        plant["actID"] = actID

                                        self.greenhouse["plantsList"].append(plant)
                                        
                                        # Update the greenhouse in catalog
                                        try:
                                            req_gh = requests.put(self.addr_cat + f"/updateGreenhouse", json.dumps(self.greenhouse))
                                            self.bot.sendMessage(chat_ID, text=f"{plant_name} correctly added "
                                                                f"to greenhouse {self.greenhouse['ghID']}"
                                                                f"\nPlease insert in the pot the sensor {plant['sensID']} and actuator {plant['actID']}")
                                        except:
                                            self.bot.sendMessage(chat_ID, text=f"Sorry, in this moment the catalog web service is unreachable! Try again later.")
                                    else: 
                                        self.bot.sendMessage(chat_ID, text=f"There are no more free sensor in device {device}!")
                                else:
                                    self.bot.sendMessage(chat_ID, text=f"{plant_name} does not exist in user {self.user['usrID']} owned plants!")

                            except:
                                self.bot.sendMessage(chat_ID, text=f"Sorry, in this moment the catalog web service is unreachable! Try again later.")
                        
                        else:
                            self.bot.sendMessage(chat_ID, text=f"Greenhouse not selected."
                                                        "\nPlease first select a greenhouse with /selectgreenhouse"
                                                        "\nOr create a new one with /addgreenhouse")
                    else:
                        self.bot.sendMessage(chat_ID, text=f"User not connected."
                                                "\nTo add a greenhouse plant, first you need to sign in with a user clicking on /start")
                        
                else:
                    self.bot.sendMessage(chat_ID, text=f"Number of parameters for command {command} not correct!")

            elif len(parameters) == 3:
                # Check if the user is correctly connected
                if command == "/addplant":
                    if self.userConnected == True:
                        if parameters[1].isnumeric() and parameters[2].isnumeric():
                            parameters[1] = int(parameters[1])
                            parameters[2] = int(parameters[2])
                            if parameters[1] >= 0 and parameters[1] <= 100 and parameters[2] >= 0 and parameters[2] <= 100:
                                if parameters[1] < parameters[2]:
                                    newPlant = {
                                        "plant": parameters[0].lower(),
                                        "th_min": parameters[1],
                                        "th_max": parameters[2]
                                    }
                                    try:
                                        req = requests.post(self.addr_cat + f"/addPlant?usrID={self.user['usrID']}",
                                                            data=json.dumps(newPlant))
                                        if req.ok:
                                            self.bot.sendMessage(chat_ID, text=f"{newPlant['plant']} correctly added to the user database.")
                                        else:
                                            self.bot.sendMessage(chat_ID, text=f"{newPlant['plant']} has not been added to the user database!.")
                                    except:
                                        self.bot.sendMessage(chat_ID, text=f"Sorry, in this moment the catalog web service is unreachable! Try again later.")

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
                elif command == "/addgreenhouse":
                    if self.userConnected:
                        devID_gh = parameters[0]
                        if parameters[1].isnumeric() and parameters[2].isnumeric():
                            parameters[1] = int(parameters[1])
                            parameters[2] = int(parameters[2])
                            if parameters[1] < 40 and parameters[2] >= 0 and parameters[2] <= 100:
                                try:
                                    req_dev = requests.get(self.addr_cat + f"/device?devID={devID_gh}")
                                    r_assigned_dev = requests.get(self.addr_cat + 
                                                                f"/greenhouse?devID={devID_gh}")
                                    if req_dev.ok:
                                        device = req_dev.json()
                                        device["ghID"] = self.greenhouse["ghID"]
                                        
                                        if not r_assigned_dev.ok:
                                            self.greenhouse["usrID"] = self.user["usrID"]
                                            #self.greenhouse["devID"].append(parameters[0])
                                            self.greenhouse["gh_params"]["temperature"] = parameters[1]
                                            self.greenhouse["gh_params"]["humidity"] = parameters[2]
                                            #FIXME: find a better way to assign the CO2 value
                                            self.greenhouse["gh_params"]["CO2_level"] = 420
                                            req_gh = requests.post(self.addr_cat + "/addGreenhouse", json.dumps(self.greenhouse))
                                            req_id = requests.get(self.addr_cat + "/greenhouse/recentID")
                                            self.greenhouse["ghID"] = req_id.json()["ghID"]
                                            # Update user and device adding the new greenhouse
                                            self.user["ghID"].append(self.greenhouse["ghID"])
                                            req_usr = requests.put(self.addr_cat + f"/updateUser", json.dumps(self.user))
                                            req_dev = requests.put(self.addr_cat + f"/updateDevice", json.dumps(device))

                                            if req_gh.ok and req_usr.ok:
                                                self.bot.sendMessage(chat_ID, text=f"Greenhouse {self.greenhouse['ghID']} correctly added."
                                                                                    f"\nWith DC {devID_gh} a max of " 
                                                                                    f"{len(device['resources']['sensors'])-1}"
                                                                                    " different plants can be added into the greenhouse.")
                                            else:
                                                self.bot.sendMessage(chat_ID, text=f"Greenhouse {self.greenhouse['ghID']} has not been added!")
                                        
                                        else:
                                            self.bot.sendMessage(chat_ID, text=f"The device {devID_gh} is already used by"
                                                                " another greenhouse!")

                                    else:
                                        self.bot.sendMessage(chat_ID, text=f"The device {devID_gh} does not exist!")
                                except:
                                    self.bot.sendMessage(chat_ID, text=f"Sorry, in this moment the catalog web service is unreachable! Try again later.")
                            else:
                                self.bot.sendMessage(chat_ID, text="Humidity and temperature values out of maximum range."
                                                                "\nPlease reinsert the command.")
                        else:
                            self.bot.sendMessage(chat_ID, text="Humidity and temperature threshold format not correct."
                                                                "\nPlease reinsert the command.")
                            
                    else:
                        self.bot.sendMessage(chat_ID, text=f"User not connected."
                                                        "\nTo add a greenhouse, first you need to sign in with a user clicking on /start")
                else:
                    self.bot.sendMessage(chat_ID, text=f"Number of parameters for command {command} not correct!")
            
            else:
                self.bot.sendMessage(chat_ID, text=f"Number of parameters for command {command} not correct!")


        ###################################
        ######### SIMPLE COMMANDS #########
        ###################################

        else:

            ##########################################
            ######### GRH CONNECTED COMMANDS #########
            ##########################################

            if self.userConnected == True:
                if self.grHselected == True:
                    # Check the status of the selected greenhouse, including: humidity, temperature and number of plants
                    if message == "/status":
                        done = True

                        if self.DA_connected == False:
                            self.DA_info()
                        
                        try:
                            req_ghINFO = requests.get(self.addr_DA + f"/getAllLastValues?ghID={self.greenhouse['ghID']}")
                            ghINFO = req_ghINFO.json() 
                            self.bot.sendMessage(chat_ID, text=f"In greenhouse {self.greenhouse['ghID']} there are:"
                                                    f"\nTemperature: {ghINFO['temperature']} C°"
                                                    f"\nHumidity: {ghINFO['humidity']} %"
                                                    f"\nCO2: {ghINFO['CO2']} ppm"
                                                    f"\nNumber of plants: {len(self.greenhouse['plantsList'])}"
                                                    "\nIf you want the list of the plants of this greenhouse click /plants")
                        except:
                            self.bot.sendMessage(chat_ID, text=f"Sorry, in this moment the data analysis web service is unreachable! Try again later.")
                        
                    # Check and print all the plant list of the selected greenhouse
                    elif message == "/plants":
                        done = True
                        if len(self.greenhouse['plantsList']) > 0:
                            self.bot.sendMessage(chat_ID, text=f"The list of plants of greenhouse {self.greenhouse['ghID']} is:")
                            for i in self.greenhouse['plantsList']:
                                self.bot.sendMessage(chat_ID, text=f"/{i['plant']}")
                        else:
                            self.bot.sendMessage(chat_ID, text=f"There are no plants in greenhouse {self.greenhouse['ghID']}"
                                                                "\nTo add a plant click on /addgrhouseplant")

                    # Inform the user how to obtain all the name of the plants of the selected greenhouse
                    elif message == "/selectplant":
                        done = True
                        self.bot.sendMessage(chat_ID, text="If you want to select a specific plant obtain the greenhouse list with /plants")

                    # If we have a greenhouse selected and we receive a command message of a plant present in this greenhouse, then this plant is selected
                    elif searchDict(self.greenhouse, 'plantsList', 'plant', message[1:]):
                        done = True
                        self.bot.sendMessage(chat_ID, text=f"{message[1:]} plant selected")
                        self.plantSelected = True
                        self.plant["plant"] = message[1:]
                        ind, plant = searchDict(self.greenhouse, 'plantsList', 'plant', self.plant["plant"],index=True)
                        self.plant["th_min"] = plant["th_min"]
                        self.plant["th_max"] = plant["th_max"]
                        self.plant["devID"] = plant["devID"]
                        self.plant["sensID"] = plant["sensID"]
                        self.plant["actID"] = plant["actID"]

                    # Inform the user to the complete command to add a plant to the greenhouse
                    elif message == "/addgrhouseplant":
                        done = True
                        self.bot.sendMessage(chat_ID, text="To add a plant to the greenhouse write:"
                                                        "\n/addgrhouseplant_devID_NameOfThePlant"
                                                        f"\n{self.greenhouse['ghID']} have {len(self.greenhouse['devices'])} device connector.")
                        
                        for dev in self.greenhouse['devices']:
                            used_sens = [plant["sensID"] for plant in self.greenhouse["plantsList"] 
                                         if plant["devID"] == dev["devID"]]
                            try:
                                req_sens = requests.get(self.addr_cat + f"/device/sensors?devID={dev['devID']}")
                                
                                # Assign a sensor and actuator to the plant to be added
                                if req_sens.ok:
                                    sensors = req_sens.json()

                                    all_sens = [sens["sensID"] for sens in sensors if sens["device_name"] == "chirp"]

                                    free_sens = [sens for sens in all_sens if sens not in used_sens]
                                    self.bot.sendMessage(chat_ID, text=f"Device connector {dev['devID']} have {len(free_sens)} sensor available")
                                else:
                                    self.bot.sendMessage(chat_ID, text=f"Device {device} does not exist!")
                            except:
                                self.bot.sendMessage(chat_ID, text=f"Sorry, the catalog web service is unreachable! Try again later.")
                        
                        text = ("Do you want the list of the user plants?")
                        buttons = [[InlineKeyboardButton(text=f'Yes', callback_data=f'plants'), 
                                    InlineKeyboardButton(text=f'No', callback_data=f'none')]]
                        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
                        self.bot.sendMessage(chat_ID, text=text, parse_mode='Markdown', reply_markup=keyboard)

                    # Inform the user to the complete command to add a new device to the greenhouse
                    elif message == "/addgrhousedevice":
                        done = True
                        self.bot.sendMessage(chat_ID, text="To add a new device to the selected greenhouse write:"
                                                        "\n/addgrhousedevice_devID")

                    # If plant commands are received before a plant is selected send the proper error message
                    elif (message == "/plantstatus") and not self.plantSelected:
                        done = True
                        self.bot.sendMessage(chat_ID, text=f"Plant not selected."
                                                            "\nPlease first select a plant with /selectplant")
                        
                    # If a plant is selected then other commands are unlocked
                    if self.plantSelected == True:
                        
                        # Obtain the plant information like its humidity treshold (low and high) and the last moisture level measured
                        if message == "/plantstatus":
                            done = True
                            if self.DA_connected == False:
                                self.DA_info()

                            try:
                                req_plantINFO = requests.get(self.addr_DA + f"/getLastMoistureLevel?ghID={self.greenhouse['ghID']}&sensID={self.plant['sensID']}")
                                plantINFO = req_plantINFO.json() 
                                self.bot.sendMessage(chat_ID, text=f"Plant {self.plant['plant']} information are:"
                                                                    f"\nMoisture level: {plantINFO['moisture']} %"
                                                                    f"\nSensor connected: {self.plant['sensID']}"
                                                                    f"\nActuator connected: {self.plant['actID']}")
                            except:
                                self.bot.sendMessage(chat_ID, text=f"Sorry, in this moment the data analysis web service is unreachable! Try again later.")

                ###########################################
                ######### USER CONNECTED COMMANDS #########
                ###########################################

                # Help message when the user is connected
                if message == "/help": 
                    self.help(chat_ID)

                # Welcome message when the user is connected
                elif message == "/start": 
                    self.start(chat_ID)
                
                # Message for adding a new greenhouse
                elif message == "/addgreenhouse":
                    self.bot.sendMessage(chat_ID, text=f"To add a new greenhouse type the command:"
                                                        "\n/addgreenhouse_devID_T_H"
                                                        "\nWith devID as the identifier of the device connector of this specific greenhouse."
                                                        "\nT is the temperature object value of the greenhouse"
                                                        " and H is the humidity objective value")

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
                        if req.ok:
                            self.greenhouse = req.json()
                        else:
                            self.bot.sendMessage(chat_ID, text=f"An error occured when selecting greenhouse {self.greenhouse['ghID']}!")
                    except:
                        self.bot.sendMessage(chat_ID, text=f"Sorry, in this moment the catalog web service is unreachable! Try again later.")
                    
                # Used to specify the correct command to add a new plant to the user database
                elif message == "/addplant":
                    self.bot.sendMessage(chat_ID, text="Add a new plant to the user database."
                                                        "\nPlease write it in this way:"
                                                        "\n/addplant_Name_lowHumidityTresh_highHumidityTresh"
                                                        "\nWhere the last two data are the level of humidity treshold in %"
                                                        "\nThe humidity thresold are numbers that goes from 0 to 100")
                elif message == "/getlinkgraph":
                    link = requests.get(self.addr_cat + f"/something")
                    self.bot.sendMessage(chat_ID, text=f"To acces nodered click on the following link:\n"
                                                        f"{link}")
                    
                ##########################
                ######### ERRORS #########
                ##########################

                # If greenhouse or plant commands are received before a greenhouse is selected send the proper error message
                elif (message == "/addgrhouseplant" or message == "/status" or message == "/plants") and not self.grHselected:
                    self.bot.sendMessage(chat_ID, text=f"No greenhouse selected."
                                                        "\nPlease first select a greenhouse with /selectgreenhouse"
                                                        "\nOr create a new one with /addgreenhouse")
                    
                elif (message == "/selectplant" or message == "/plantstatus" or message == "/addgrhousedevice") and not self.grHselected:
                    self.bot.sendMessage(chat_ID, text=f"No greenhouse selected."
                                                        "\nPlease first select a greenhouse with /selectgreenhouse"
                                                        "\nOr create a new one with /addgreenhouse")
                        
                elif message.startswith('/') and not done:
                    self.bot.sendMessage(chat_ID, text="Command not supported")

                elif not done:
                    self.bot.sendMessage(chat_ID, text="Word/words not recognized. Please start with command /start")

        ##############################################
        ######### USR NOT CONNECTED COMMANDS #########
        ##############################################

            else:
                if message == "/help": 
                    self.help(chat_ID)

                elif message == "/start": 
                    self.start(chat_ID)

                ##########################
                ######### ERRORS #########
                ##########################

                elif message == "/addgreenhouse" or message == "/selectgreenhouse" or message == "/addplant":
                    self.bot.sendMessage(chat_ID, text=f"User not connected."
                                                        "\nPlease first sign in with a user clicking on /start")
                    
                elif message == "/addgrhouseplant" or message == "/status" or message == "/selectplant":
                    self.bot.sendMessage(chat_ID, text=f"User not connected."
                                                        "\nPlease first sign in with a user clicking on /start")
                elif message == "/plantstatus" or message == "/selectplant" or message == "/plants":
                    self.bot.sendMessage(chat_ID, text=f"User not connected."
                                                        "\nPlease first sign in with a user clicking on /start")
                elif message.startswith('/'):
                    self.bot.sendMessage(chat_ID, text="Command not supported")
                else:
                    self.bot.sendMessage(chat_ID, text="Word/words not recognized. Please start with command /start")

    #####################################
    ######### BUTTONS REACTIONS #########
    #####################################

    def on_callback_query(self, msg):
        """
        on_callback_query
        -----------------
        Callback query function:
            - it will elaborate the information when a button is pressed
        """
        
        # action is the callback data write in the buttons
        query_ID, chat_ID, action = telepot.glance(msg, flavor='callback_query') 

        # When the signup button is pressed 
        if action == 'signup': 
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
            try:
                req_users = requests.get(self.addr_cat + f"/user?usrID={self.user['usrID']}")
                if req_users.ok:
                    user = req_users.json()
                    ownedPlants = user['ownedPlants']
                    self.bot.sendMessage(chat_ID, text=f"Plant list:")
                    for plant in ownedPlants:
                        self.bot.sendMessage(chat_ID, text=f"{plant['plant']}")
                else:
                    self.bot.sendMessage(chat_ID, text=f"User {self.user['usrID']} does not have plants in its database!")
            except:
                self.bot.sendMessage(chat_ID, text=f"Sorry, in this moment the catalog web service is unreachable! Try again later.")

        # When 'No' buttons are clicked
        elif action == 'none':
            self.bot.sendMessage(chat_ID, text=f"No action done")

    ###########################################
    ######### HELP AND START COMMANDS #########
    ###########################################

    def help(self, chat_ID):
        """
        help
        ----
        Send a message when the command /help is received.
        The different type of help messages are for having a dynamic\\
        printing of help messages in different cases.
        """

        if self.userConnected == True and self.grHselected == False:
            help_message = ("*You can perform the following actions:*\n"  
                        "- /addplant: Add new plant to the user database\n"
                        "- /selectgreenhouse: Get the ID of your greenhouse to select one\n"
                        "- /addgreenhouse: Add a new empty greenhouse\n"
                        "- /getlinkgraph: Get the link to open the nodered dashboard\n")
            
        elif self.userConnected == True and self.grHselected == True and self.plantSelected == False:
            help_message = ("*You can perform the following actions:*\n" 
                        "- /status: Get info about your greenhouse\n" 
                        "- /addplant: Add new plant to the user database\n"
                        "- /selectgreenhouse: Get the ID of your greenhouse to select one\n"
                        "- /addgreenhouse: Add a new empty greenhouse\n"
                        "- /addgrhouseplant: Add new plant to the greenhouse\n"
                        "- /addgrhousedevice: Add a new device to the selected greenhouse\n"
                        "- /plants: Get the list of the plants of the selected greenhouse\n"
                        "- /selectplant: Get the name of the selected greenhouse plants to select one\n"
                        "- /getlinkgraph: Get the link to open the nodered dashboard\n")
            
        elif self.userConnected == True and self.grHselected == True and self.plantSelected == True:
            help_message = ("*You can perform the following actions:*\n"
                        "- /status: Get info about your greenhouse\n" 
                        "- /addplant: Add new plant to the user database\n"
                        "- /selectgreenhouse: Get the ID of your greenhouse to select one\n"
                        "- /addgreenhouse: Add a new empty greenhouse\n"
                        "- /addgrhouseplant: Add new plant to the greenhouse\n"
                        "- /addgrhousedevice: Add a new device to the selected greenhouse\n"
                        "- /plants: Get the list of the plants of the selected greenhouse\n"
                        "- /selectplant: Get the name of the selected greenhouse plants to select one\n"
                        "- /getlinkgraph: Get the link to open the nodered dashboard\n"
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

    def DA_info(self, tries = 10):
        """
        DA_info
        -------
        Try to contact the catalog to obtain the information of thingspeak.
        ### Parameters obtained
        - TsIp: IP of thingspeak rest interface
        - TsPort: Port of thingspeak rest interface
        """
        count = 0
        update = False
        while count < tries and not update:
            count += 1
            try:
                req_Da = requests.get(self.addr_cat + "/service?name=data_analysis")
                if req_Da.ok:
                    Da =req_Da.json()
                    DA_info = {
                        "ip": Da["endpoints_details"][0]["ip"],
                        "port": str(Da["endpoints_details"][0]["port"])
                    }
                    self.addr_DA = "http://" + DA_info["ip"] + ":" + DA_info["port"]
                    self.DA_connected = True
                    update = True
                else:
                    print("Data analysis microservice not present in the catalog!")
                    time.sleep(1)
            except:
                print("The catalog web service is unreachable!")
                time.sleep(1)

        #if update == False:
        #    raise Exception("Data analysis microservice not present in the catalog!")


if __name__ == "__main__":

    Telegram_Bot()
    while 1:
        time.sleep(10)