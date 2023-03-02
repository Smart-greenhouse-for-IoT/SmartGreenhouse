import json

class catalog():

    def __init__(self):
        self.catalogFile = "catalog\catalog.json"    # file's json name
        self.plantDBFile = "catalog\plantsDatabase.json" # file that works as DB for plants
        self.jsonDic = json.load(open(self.catalogFile))   # load json file into a dictionary
        self.plantDB = json.load(open(self.plantDBFile))
        
    # Method to receive broker's information as dictionary
    def brokerInfo(self):
        return self.jsonDic["broker"]   

    # Method to receive devices information (ids can be specified)
    def devicesInfo(self, id=[]):
        devices = self.jsonDic["greenhouses"]   
        if len(id) != 0:    #check if ids are selected
            idDevices = []
            for device in devices:
                if id.count(device.get('deviceID')) != 0:   
                    idDevices.append(device)
            return idDevices    #return the id selected devices
        return devices  #return all the devices
    
    def addUser(self, newUser):
        fw = open(self.filename, "w")
        self.jsonDic["usersList"].append(newUser)
        json.dump(self.jsonDic, fw, indent=4)
    
    def updateDevice(self, id, infoToUpdate = {}):
        fw = open(self.filename, "w")
        id = [int(id)]
        devToUpdate = self.findDeviceFromID(id)
        #TODO: insert params to update

    def getNumberLots(self, ghID = []):
        greenhouses = self.jsonDic["greenhouses"]
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
    
    def updateSensors(self, sensorsDic):
        ''' 
        Method to update sensors to the catalog json file
        ---
        - Used by device connector to keep the catalog updated
        - Update sensors in "sensors" key in the format:\n
            {
                "devID": "id",
                "type": "typeofSensor",
                "topic": "/topic/forSensors"
            }
        '''
        fw = open(self.catalogFile, "w")
        self.jsonDic["sensors"].clear() # remove previous sensors
        self.jsonDic["sensors"] = sensorsDic    # insert updated list of sensors
        json.dump(self.jsonDic, fw, indent=4)
        
    

