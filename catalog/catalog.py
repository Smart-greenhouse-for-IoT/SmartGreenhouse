import json
import cherrypy
from datetime import datetime
import time
from tools import searchDict, generateID

class catalog():
    """
    Catalog
    -------

    """
    #TODO: check on the ID formats
    #TODO: get per i topic
    #TODO: una greenhouse -> più device
    def __init__(self):
        self.catalogFile = "catalog/catalog.json" 
        self.plantDBFile = "catalog/plantsDatabase.json"
        with open(self.catalogFile) as cf:
            self.catDic = json.load(cf)
        
        with open(self.plantDBFile) as pf:
            self.plantDB = json.load(pf)

        # Save the numeric IDs of the catalog
        self.devIDs = [int(dev["devID"][1:]) for dev in self.catDic["devices"]]
        self.usrIDs = [int(usr["usrID"][1:]) for usr in self.catDic["users"]]
        self.ghIDs = [int(gh["ghID"][1:]) for gh in self.catDic["greenhouses"]]

        self.lastUpdate = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.catDic["lastUpdate"] = self.lastUpdate

    ######################## DEVICE CATALOG ########################
    def addDevice(self, newDev):
        """
        addDevice
        ---------
        Function used to add a new device in the catalog.
        """
        new_id = generateID(self.devIDs)
        self.devIDs.append(new_id)
        new_id = "d" + str(new_id)
        newDev["devID"] = new_id
        self.lastUpdate = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        newDev["lastUpdate"] = self.lastUpdate
        self.catDic["devices"].append(newDev)
        self.catDic["lastUpdate"] = self.lastUpdate
        return 0
    
    def updateDevice(self, update_dev):
        """
        updateDevice
        ------------
        Update a device already present in catalog.
        """
        for i, device in enumerate(self.catDic["devices"]):
            if device["devID"] == update_dev["devID"]:
                for key in update_dev.keys():
                    self.catDic["devices"][i][key] = update_dev[key]
                self.lastUpdate = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.catDic["devices"][i]["lastUpdate"] = self.lastUpdate
                self.catDic["lastUpdate"] = self.lastUpdate
                return 0
        return -1
    
    def updateDevices(self, devicesDic):
        """
        updateDevices
        -------------
        Method to update devices to the catalog json file.
        - Used by device connector to keep the catalog updated
        - Update devices in "devices" key of catalog.json
        """
        self.catDic["greenhouses"]["ghID" == devicesDic["ghID"]]["devicesList"] = devicesDic["devicesList"]
    
    
    ######################## SERVICE CATALOG ########################
    def brokerInfo(self):
        """
        brokerInfo
        ----------
        Method to receive broker's information as dictionary.
        """
        return self.catDic["broker"]   

    def catInfo(self):
        """
        catInfo
        -------
        Method to retrieve information related to the catalog such as IP and port.
        """
        return self.catDic["catalog"]
    
    def projectName(self):
        """
        projectName
        -----------
        Return the project name.
        """
        return self.catDic["projectName"]
    
    def telegramInfo(self):
        """
        telegramInfo
        ------------
        Return all the telegram info, included the Token.
        """
        return self.catDic["telegramBot"]
    
    def addUser(self, newUsr):
        """
        addUser
        -------
        Method to add a new user to the catalog.
        """
        new_id = generateID(self.usrIDs)
        self.usrIDs.append(new_id)
        new_id = "u" + str(new_id)
        newUsr["usrID"] = new_id
        self.lastUpdate = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        newUsr["lastUpdate"] = self.lastUpdate
        self.catDic["users"].append(newUsr)
        self.catDic["lastUpdate"] = self.lastUpdate
        return 0
    
    def updateUser(self, update_usr):
        """
        updateUser
        ----------
        Method to update the information of a user already present in the catalog.
        """
        for i, user in enumerate(self.catDic["users"]):
            if user["usrID"] == update_usr["usrID"]:
                for key in update_usr.keys():
                    self.catDic["users"][i][key] = update_usr[key]
                self.lastUpdate = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.catDic["users"][i]["lastUpdate"] = self.lastUpdate
                self.catDic["lastUpdate"] = self.lastUpdate
                return 0
        return -1
    
    def addGreenhouse(self, newGh):
        """
        addGreenhouse
        -------------
        Method to add a new greenhouse for a specific user to the catalog.
        """
        new_id = generateID(self.ghIDs)
        self.ghIDs.append(new_id)
        new_id = "g" + str(new_id)
        newGh["ghID"] = new_id
        self.lastUpdate = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        newGh["lastUpdate"] = self.lastUpdate
        self.catDic["greenhouses"].append(newGh)
        self.catDic["lastUpdate"] = self.lastUpdate
        return 0
    
    def updateGreenhouse(self, update_gh):
        """
        updateGreenhouse
        ----------------
        Method to update a greenhouse information in the catalog.
        """
        for i, greenhouse in enumerate(self.catDic["greenhouses"]):
            if greenhouse["ghID"] == update_gh["ghID"]:
                for key in update_gh.keys():
                    self.catDic["greenhouses"][i][key] = update_gh[key]
                self.lastUpdate = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.catDic["greenhouses"][i]["lastUpdate"] = self.lastUpdate
                self.catDic["lastUpdate"] = self.lastUpdate
                return 0
        return -1

    def getNumberLots(self, ghID = []):
        """
        getNumberLots
        -------------
        #FIXME: fox scrivi qualcosa tu
        """
        greenhouses = self.catDic["greenhouses"]
        numLots = 0
        for gh in greenhouses:
            if ghID.count(gh.get("ghID")) != 0:   
                numLots = gh.get("numPlants")
        return numLots
    
    # Retrieve humidity threshold from telegram bot given plant name
    def thresholdHumidity(self, plantRequest = ""):
        """
        thresholdHumidity
        -----------------
        ### Method to give humidity threshold to plant control
        The threshold are given in the form:\n
            {
                "th_min": 0.1,\n
                "th_max": 0.2\n
            }\n
        If the plant requested is not found the return -1
        """
        try:
            # Find dictionary by plant type in plantDB dictionary
            humidityTh = next(item for item in self.plantDB["humidityThresh"] if item["plant"] == plantRequest)
            # Pop plant key to return only desired thresholds
            humidityTh.pop("plant")  
            return humidityTh
        
        # If plant not present raise error
        except KeyError:    
            error_code = -1
            return error_code
    
    def lastUpdate(self, key):
        for dict in self.catDic["key"]:
            last_upd = time.mktime(datetime.strptime(device["lastUpdate"],
                                            "%Y-%m-%d %H:%M:%S").timetuple())
    
    ######################## GENERAL METHODS ########################
    def saveJson(self):
        """
        saveJson
        --------
        Used to save the catalog as a JSON file.
        """
        with open(self.catalogFile, 'w') as fw:
            json.dump(self.catDic, fw, indent=4)
            return 0
    
    def dictInfo(self, key):
        """
        dictInfo
        --------
        Method to retrieve value of dictionary given key.
        """
        return self.catDic[key]

#############################################################
#                       WEB SERVICE                         #
#############################################################
class REST_catalog(catalog):
    """
    REST_catalog
    ------------
    ### Child class of catalog that implement REST methods
    Methods:
    - GET 
        - broker: retrieve broker informations
        - getThresholds: retrieve humidity thresholds given a plant's type 
    - POST
        - updateDevices: update devices from device connector
    """
    
    exposed = True        

    def __init__(self):
        catalog.__init__(self)
        self.methodsFile = "catalog/methods.json"
        with open(self.methodsFile) as mf:
            self.methods = json.load(mf)

    def GET(self, *uri, **params):
        """
        GET
        ---
        Used to obtain information from other devices
        """
        
        if len(uri) >=1:
            
            # DEVICE CATALOG
            if uri[0] == "device":
                if len(uri) > 1 and uri[1] == "recentID":
                    # Retrieve the ID of the device added most recently
                    devID = self.catDic["devices"][-1]["devID"]
                    return json.dumps({'devID': devID})
                else:
                    if "devID" in params:
                        devID = params["devID"]
                        search_dev = searchDict(self.catDic, "devices", "devID", devID)
                        if search_dev:
                            return json.dumps(search_dev)
                        else:
                            raise cherrypy.HTTPError(404, f"Device {devID} not found!")
                    elif "name" in params:
                        name = params["name"]
                        search_dev = searchDict(self.catDic, "devices", "name", name)
                        if search_dev:
                            return json.dumps(search_dev)
                        else:
                            raise cherrypy.HTTPError(404, f"Device {name} not found!")
                    elif params == {}:
                        return json.dumps(self.dictInfo("devices"))

                    else:
                        cherrypy.HTTPError(400, f"Parameters are missing or are not correct!")

            # SERVICE CATALOG
            elif uri[0] == "broker":
                return json.dumps(self.brokerInfo())

            elif uri[0] == "catalogInfo":
                return json.dumps(self.catInfo())

            elif uri[0] == "projectInfo":
                return json.dumps(self.projectName())

            elif uri[0] == "telegramInfo":
                return json.dumps(self.telegramInfo())

            elif uri[0] == "greenhouse":
                if len(uri) > 1 and uri[1] == "recentID":
                    # Retrieve the ID of the device added most recently
                    ghID = self.catDic["greenhouses"][-1]["ghID"]
                    return json.dumps({'ghID': ghID})
                else:
                    if "ghID" in params:
                        ghID = params["ghID"]
                        search_gh = searchDict(self.catDic, "greenhouses", "ghID", ghID)
                        if search_gh:
                            return json.dumps(search_gh)
                        else:
                            raise cherrypy.HTTPError(404, f"Greenhouse {ghID} not found!")
                    elif "usrID" in params:
                        usrID = params["usrID"]
                        search_gh = searchDict(self.catDic, "greenhouses", "usrID", usrID)
                        if search_gh:
                            return json.dumps(search_gh)
                        else:
                            raise cherrypy.HTTPError(404, f"No greenhouses associated\
                                                            to user {usrID}")
                    elif params == {}:
                        return json.dumps(self.dictInfo("greenhouses"))
                    else:
                        cherrypy.HTTPError(400, f"Parameters are missing or are not correct!")

            elif uri[0] == "user":
                if len(uri) > 1 and uri[1] == "recentID":
                    # Retrieve the ID of the device added most recently
                    usrID = self.catDic["users"][-1]["usrID"]
                    return json.dumps({'usrID': usrID})
                else:
                    if "usrID" in params:
                        usrID = params["usrID"]
                        search_usr= searchDict(self.catDic, "users", "usrID", usrID)
                        if search_usr:
                            return json.dumps(search_usr)
                        else:
                            raise cherrypy.HTTPError(404, f"User {usrID} not found!")

                    elif params == {}:
                        return json.dumps(self.dictInfo("users"))

                    else:
                        cherrypy.HTTPError(400, f"Parameters are missing or are not correct!")

            elif uri[0] == "getThresholds":
                humidityTh = self.thresholdHumidity(params.get("plant")) # retrieve humidity threshold given plant name
                return json.dumps(humidityTh)   # return a list containing min and max thresholds

        else:
            return json.dumps(self.methods)

    
    def POST(self, *uri, **params):
        """
        POST
        ----
        Used to add new devices, users or greenhouses
        """

        # Load body of request as dictionary
        bodyAsStr = cherrypy.request.body.read()
        bodyAsDict = json.loads(bodyAsStr)

        if len(uri) >= 1:
            # DEVICE CATALOG
            if uri[0] == "updateDevices":
                self.updateDevices(bodyAsDict)
                self.saveJson()
            
            elif uri[0] == "addDevice":
                if self.addDevice(bodyAsDict) == 0:
                    self.saveJson()
                    print(f'\nDevice {bodyAsDict["devID"]} added successfully!')
                    #TODO: assegnare il nuovo ID al device connector 
                else:
                    raise cherrypy.HTTPError(400, f'Device {bodyAsDict["devID"]} could not be added!')

            # SERVICE CATALOG
            elif uri[0] == "addUser":
                if self.addUser(bodyAsDict) == 0:
                    self.saveJson()
                    print(f'\nUser {bodyAsDict["usrID"]} added successfully!') 
                else:
                    raise cherrypy.HTTPError(400, f'User {bodyAsDict["usrID"]} could not be added!')
            
            elif uri[0] == "addGreenhouse":
                if self.addGreenhouse(bodyAsDict) == 0:
                    self.saveJson()
                    print(f'\nGreenhouse {bodyAsDict["ghID"]} added successfully!') 
                else:
                    raise cherrypy.HTTPError(400, f'Greenhouse {bodyAsDict["ghID"]} could not be added!')
            
            elif uri[0] == "addPlant":
                if len(params.keys()) == 1 and params.get("usrID") != None:
                    #NOTE: decidere se assegnare un ID alle piante
                    ind_usr, found_usr = searchDict(self.catDic, "users", "usrID", params["usrID"],index=True)
                    if found_usr and ind_usr is not None:
                        self.catDic["users"][ind_usr]["ownedPlants"].append(bodyAsDict)
                        self.saveJson()
                        print(f"Plant added to user {params['usrID']}")
                else:
                    raise cherrypy.HTTPError(400, f'Invalid parameter! Format is /addPlant?usrID=')
            

    
    def PUT(self, *uri, **params):
        """
        PUT
        ---
        Used to update devices, users or greenhouses
        """

        bodyAsStr = cherrypy.request.body.read()
        bodyAsDict = json.loads(bodyAsStr)
        if len(uri) >= 1:
            if uri[0] == "updateDevice":
                if self.updateDevice(bodyAsDict) == 0:
                    self.saveJson()
                    print(f'\nDevice {bodyAsDict["devID"]} updated successfully')
                else:
                    print(f'Device {bodyAsDict["devID"]} could not be updated')
                    raise cherrypy.HTTPError(400, "The device could not be updated!")
            
            if uri[0] == "updateUser":
                if self.updateUser(bodyAsDict) == 0:
                    self.saveJson()
                    print('\nUser {bodyAsDict["usrID"]} updated successfully')
                else:
                    print('User {bodyAsDict["devID"]} could not be updated')
                    raise cherrypy.HTTPError(400, "The user could not be updated!")
            
            if uri[0] == "updateGreenhouse":
                if self.updateGreenhouse(bodyAsDict) == 0:
                    self.saveJson()
                    print('\nGreenhouse {bodyAsDict["ghID"]} updated successfully')
                else:
                    print('Greenhouse {bodyAsDict["ghID"]}could not be updated')
                    raise cherrypy.HTTPError(400, "The greenhouse could not be updated!")
    
    def cleaning(self, timeout):
        """
        cleaning
        --------
        Method to remove devices that are no more active.
        The inactivity is determined by a timeout. 
        """
        while True:
            for ind, device in enumerate(self.catDic["devices"]):
                last_upd = time.mktime(datetime.strptime(device["lastUpdate"],
                                            "%Y-%m-%d %H:%M:%S").timetuple())
                current_t = datetime.timestamp(datetime.now())
                if current_t - last_upd >= timeout:
                    self.catDic["devices"].pop(ind)
                    print(f"Device {device['devID']} has been removed due to inactivity!")
                    self.lastUpdate = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    self.catDic["lastUpdate"] = self.lastUpdate
                    self.saveJson()

    
if __name__ == "__main__": 
	
    # Standard configuration to serve the url "localhost:8080"
    conf={
    	'/':{
    		'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
    		'tools.sessions.on': True
    	}
    }
    webService = REST_catalog()
    cherrypy.tree.mount(webService,'/',conf)
    cherrypy.engine.start()
    try:
        webService.cleaning(timeout=15)
    except KeyboardInterrupt:
        cherrypy.engine.block()
