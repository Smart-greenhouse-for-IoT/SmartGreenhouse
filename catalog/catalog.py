import json
import cherrypy
import requests
from datetime import datetime

class catalog():

    def __init__(self):
        self.catalogFile = "catalog/catalog.json" 
        self.plantDBFile = "catalog/plantsDatabase.json"
        self.catDic = json.load(open(self.catalogFile))
        self.plantDB = json.load(open(self.plantDBFile))

        self.lastUpdate = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.catDic["lastUpdate"] = self.lastUpdate

    ######################## DEVICE CATALOG ########################
    def devicesInfo(self):
        # Method to retrieve all devices
        return self.catDic["devices"]

    def searchDevice(self, key, value):
        # Search a device given name or ID
        found_dev = {}
        for device in self.catDic["devices"]:
            if device[key] == value:
                found_dev = device.copy()
        return found_dev
    
    def addDevice(self, newDev):
        # Add new device in catalog
        if self.searchDevice("devID", newDev["devID"]) == {}:
            self.lastUpdate = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            newDev["lastUpdate"] = self.lastUpdate
            self.catDic["devices"].append(newDev)
            self.catDic["lastUpdate"] = self.lastUpdate
            return 0
        else:
            return -1
    
    def updateDevice(self, update_dev):
        # Update a device already present in catalog
        for i, device in enumerate(self.catDic["devices"]):
            if device["devID"] == update_dev["devID"]:
                for key in update_dev.keys():
                    self.catDic["devices"][i][key] = update_dev[key]
                self.lastUpdate = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.catDic["devices"][i]["lastUpdate"] = self.lastUpdate
                self.catDic["lastUpdate"] = self.lastUpdate
                return 0
        return -1
    
    
    ######################## SERVICE CATALOG ########################
    def brokerInfo(self):
        # Method to receive broker's information as dictionary
        return self.catDic["broker"]   

    
    def catInfo(self):
        # Method to retrieve information related to the catalog such as IP and port
        return self.catDic["catalog"]
    
    def addUser(self, newUser):
        fw = open(self.filename, "w")
        self.catDic["usersList"].append(newUser)
        json.dump(self.catDic, fw, indent=4)
    

        

    def getNumberLots(self, ghID = []):
        greenhouses = self.catDic["greenhouses"]
        numLots = 0
        for gh in greenhouses:
            if ghID.count(gh.get("ghID")) != 0:   
                numLots = gh.get("numPlants")
        return numLots
    
    # Retrieve humidity threshold from telegram bot given plant name
    def thresholdHumidity(self, plantRequest = ""):
        '''
        Method to give humidity threshold to plant control
        ---
        The threshold are given in the form:\
            {
                "th_min": 0.1,
                "th_max": 0.2
            }
        If the plant requested is not found the return -1
        '''
        try:
            # find dictionary by plant type in plantDB dictionary
            humidityTh = next(item for item in self.plantDB["humidityThresh"] if item["plant"] == plantRequest)
            humidityTh.pop("plant")  # pop plant key to return only desired thresholds
            return humidityTh
        except KeyError:    # if plant not present raise error
            error_code = -1
            return error_code
    
    ######################## GENERAL METHODS ########################
    def saveJson(self):
        # Used to save the catalog as a JSON file
        with open(self.catalogFile, 'w') as fw:
            json.dump(self.catDic, fw, indent=4)
            return 0
        return 1



class REST_catalog(catalog):
    '''
    Child class of catalog that implement REST methods
    ---
    Methods:
    - GET 
        - broker: retrieve broker informations
        - getThresholds: retrieve humidity thresholds given a plant's type 
    - POST
        - updateDevices: update devices from device connector
    '''
    
    exposed = True        

    def GET(self, *uri, **params):
        if len(uri) >=1:
            
            # DEVICE CATALOG
            if uri[0] == "devices":
                return json.dumps(self.devicesInfo)
            
            elif uri[0] == "device":
                if "devID" in params:
                    devID = params["devID"]
                    search_dev = self.searchDevice("devID", params["devID"])
                    if search_dev:
                        return json.dumps(search_dev)
                    else:
                        raise cherrypy.HTTPError(404, f"Device {devID} not found!")
                elif "name" in params:
                    name = params["name"]
                    search_dev = self.searchDevice("name", params["name"])
                    if search_dev:
                        return json.dumps(search_dev)
                    else:
                        raise cherrypy.HTTPError(404, f"Device {name} not found!")
                else:
                    cherrypy.HTTPError(400, f"Parameters are missing or are not correct!")

            # SERVICE CATALOG
            elif uri[0] == "broker":
                return json.dumps(self.brokerInfo())    # return broker info as json string

            # retrieve humidity threshold given ID 
            elif uri[0] == "getThresholds":
                humidityTh = self.thresholdHumidity(params.get("plant")) # retrieve humidity threshold given plant name
                return json.dumps(humidityTh)   # return a list containing min and max thresholds

            elif uri[0] == "infoPlantControl":
                pass
        else:
            return "Waiting for valid URI"

    
    def POST(self, *uri, **params):
        # load body of request as dictionary
        bodyAsString = cherrypy.request.body.read()
        bodyAsDictionary = json.loads(bodyAsString)

        if len(uri) >= 1:
            # DEVICE CATALOG
            if uri[0] == "updateDevices":
                self.updateDevices(bodyAsDictionary)

            elif uri[0] == "addDevice":
                if self.addDevice(bodyAsDictionary) == 0:
                    self.saveJson()
                    print('\nNew device added successfully!')    #NOTE: come aggiungere una response del server che non sia un'eccezione??
                else:
                    print("The device could not be added")
                    raise cherrypy.HTTPError(400, "The device could not be added!")

            # SERVICE CATALOG
            elif uri[0] == "user":
                self.addUser(bodyAsDictionary)
    
    def PUT(self, *uri, **params):  # /device/id?deviceName=DHT11&availableServices=MQTT

        bodyAsString = cherrypy.request.body.read()
        bodyAsDictionary = json.loads(bodyAsString)
        if len(uri) >= 1:
            if uri[0] == "device":
                if self.updateDevice(bodyAsDictionary) == 0:
                    self.saveJson()
                    print('\nDevice updated successfully')
                else:
                    print("The device could not be updated")
                    raise cherrypy.HTTPError(400, "The device could not be updated!")
    
if __name__ == "__main__": #Standard configuration to serve the url "localhost:8080"
	
	conf={
		'/':{
			'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
			'tools.sessions.on': True
		}
	}
	webService=REST_catalog()
	cherrypy.tree.mount(webService,'/',conf)
	cherrypy.engine.start()
	cherrypy.engine.block()
