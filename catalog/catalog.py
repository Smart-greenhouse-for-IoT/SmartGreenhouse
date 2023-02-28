import json

class catalog():

    def __init__(self):
        self.filename = "LAB05\catalog.json"    # file's json name
        self.jsonDic = json.load(open(self.filename))   # load json file into a dictionary
        
    # Method to receive broker's information as dictionary
    def brokerInfo(self):
        return self.jsonDic["broker"]   

    # Method to receive devices information (ids can be specified)
    def devicesInfo(self, id=[]):
        devices = self.jsonDic["devicesList"]   
        if len(id) != 0:    #check if ids are selected
            idDevices = []
            for device in devices:
                if id.count(device.get('deviceID')) != 0:   
                    idDevices.append(device)
            return idDevices    #return the id selected devices
        return devices  #return all the devices

    def addDevice(self, newDevice):
        fw = open(self.filename, "w")
        self.jsonDic["devicesList"].append(newDevice)
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

    def findDeviceFromID(self, id = []):
        devices = self.jsonDic["devicesList"]
        idDevices = []
        for device in devices:
            if id.count(device.get('deviceID')) != 0:   
                idDevices.append(device)
        return idDevices
    
    # Retrieve humidity threshold from telegram bot given plant name
    def thresholdHumidity(self, plantRequest = ""):
        try:
            plantDict = next(item for item in self.jsonDic["humidityThresh"] if item["plant"] == plantRequest)  # find dictionary by plant type
            humidityTh = [plantDict.get("th_min"), plantDict.get("th_max")] # list composed of [th_min, th_max]
            return humidityTh
        except KeyError:    # if plant not present raise error
            error_code = -1
            return error_code

