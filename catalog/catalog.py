import json

class catalog():

    def __init__(self):
        self.catalogFile = "catalog\catalog.json"    # file's json name
        self.plantDBFile = "catalog\plantsDatabse.json" # file that works as DB for plants
        self.jsonDic = json.load(open(self.catalogFile))   # load json file into a dictionary
        self.plantDB = json.load(open(self.plantDBFile))
        
    # Method to receive broker's information as dictionary
    def brokerInfo(self):
        return self.jsonDic["broker"]   

    # Method to receive devices information (ids can be specified)
    def devicesInfo(self, id=[]):
        devices = self.jsonDic["greenHouses"]   
        if len(id) != 0:    #check if ids are selected
            idDevices = []
            for device in devices:
                if id.count(device.get('deviceID')) != 0:   
                    idDevices.append(device)
            return idDevices    #return the id selected devices
        return devices  #return all the devices

    def addDevice(self, newDevice):
        fw = open(self.filename, "w")
        self.jsonDic["greenHouses"].append(newDevice)
        json.dump(self.jsonDic, fw, indent=4)
    
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
        greenhouses = self.jsonDic["greenHouses"]
        numLots = 0
        for gh in greenhouses:
            if ghID.count(gh.get("ghID")) != 0:   
                numLots = gh.get("numPlants")
        return numLots
    
    # Retrieve humidity threshold from telegram bot given plant name
    def thresholdHumidity(self, plantRequest = ""):
        try:
            plantDict = next(item for item in self.plantDB["humidityThresh"] if item["plant"] == plantRequest)  # find dictionary by plant type in plantDB
            humidityTh = [plantDict.get("th_min"), plantDict.get("th_max")] # list composed of [th_min, th_max]
            return humidityTh
        except KeyError:    # if plant not present raise error
            error_code = -1
            return error_code

