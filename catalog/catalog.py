import json
import cherrypy

class catalog():

    def __init__(self):
        self.catalogFile = "catalog/catalog.json"    # file's json name
        self.plantDBFile = "catalog/plantsDatabase.json" # file that works as DB for plants
        self.catDic = json.load(open(self.catalogFile))   # load json file into a dictionary
        self.plantDB = json.load(open(self.plantDBFile))
        
    # Method to receive broker's information as dictionary
    def brokerInfo(self):
        return self.catDic["broker"]   

    # Method to retrieve devices information given a greenhouse id
    def devicesInfo(self, id: str):
        ghID_dic = next(gh for gh in self.catDic["greenhouses"] if gh["ghID"] == id)
        return ghID_dic["devicesList"]
    
    def catInfo(self):
        '''
        Method to retrieve information related to the catalog such as IP and port
        ---
        "catalog": {
            "ip": "127.0.0.1",
            "port": 8080
        }
        '''
        return self.catDic["catalog"]
    
    def addUser(self, newUser):
        fw = open(self.filename, "w")
        self.catDic["usersList"].append(newUser)
        json.dump(self.catDic, fw, indent=4)
    
    def updateDevice(self, id, infoToUpdate = {}):
        fw = open(self.filename, "w")
        id = [int(id)]
        devToUpdate = self.findDeviceFromID(id)
        #TODO: insert params to update

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
    
    def updateDevices(self, devicesDic):
        ''' 
        Method to update devices to the catalog json file
        ---
        - Used by device connector to keep the catalog updated
        - Update devices in "devicesList" key in the format:\n
            {
                "devID": "id",
                "type": "typeofSensor",
                "measurementType" = "",
                "topic": "/topic/forSensors"
            }
        '''
        fw = open(self.catalogFile, "w")
        self.catDic["greenhouses"]["ghID" == devicesDic["ghID"]]["devicesList"] = devicesDic["devicesList"] # update devices of the given ghID
        json.dump(self.catDic, fw, indent=4)


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
        
        if uri[0] == "broker":
            return json.dumps(self.brokerInfo())    # return broker info as json string
        
        # retrieve humidity threshold given ID 
        elif uri[0] == "getThresholds":
            humidityTh = self.thresholdHumidity(params.get("plant")) # retrieve humidity threshold given plant name
            return json.dumps(humidityTh)   # return a list containing min and max thresholds
        
        elif uri[0] == "infoPlantControl":
            pass

        """elif uri[0] == "devicesList":
            if len(params) != 0:
                ids = list(map(int,params.get('id')))
                idDevices = self.devicesInfo(ids)
                return json.dumps(idDevices) 
            devices = self.devicesInfo()
            return json.dumps(devices)"""

    
    def POST(self, *uri, **params):
        # load body of request as dictionary
        bodyAsString = cherrypy.request.body.read()
        bodyAsDictionary = json.loads(bodyAsString)

        # update 
        if uri[0] == "updateDevices":
            self.updateDevices(bodyAsDictionary)

        elif uri[0] == "user":
            self.addUser(bodyAsDictionary)
    
    def PUT(self, *uri, **params):  # /device/id?deviceName=DHT11&availableServices=MQTT
        if uri[0] == "device":
            self.updateDevice(id=uri[1], infoToUpdate=params)
        
    
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
