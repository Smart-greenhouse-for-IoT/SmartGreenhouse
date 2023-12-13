import json
import cherrypy
from datetime import datetime
import time
from tools import searchDict, generateID

#TODO: ghID viene aggiunta in fondo, cercare un modo per cambiare posizione
#TODO: check on the ID formats
class catalog():
    """
    Catalog
    -------

    """
    
    def __init__(self):
        self.catalogFile = "catalog/catalog.json" 
        self.plantDBFile = "catalog/plantsDatabase.json"
        with open(self.catalogFile) as cf:
            self.catDic = json.load(cf)
        
        with open(self.plantDBFile) as pf:
            self.plantDB = json.load(pf)

        # Save the numeric IDs of the catalog
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
        if searchDict(self.catDic, "devices","devID", newDev["devID"]) == {}:
            self.lastUpdate = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            newDev["lastUpdate"] = self.lastUpdate
            self.catDic["devices"].append(newDev)
            self.catDic["lastUpdate"] = self.lastUpdate
            return 0
        else:
            return -1

    
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

    def addService(self, newServ):
        """
        addService
        ---------
        Function used to add a new service in the catalog.
        """
        if searchDict(self.catDic, "services","servID", newServ["servID"]) == {}:
            self.lastUpdate = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            newServ["lastUpdate"] = self.lastUpdate
            self.catDic["services"].append(newServ)
            self.catDic["lastUpdate"] = self.lastUpdate
            return 0
        else:
            return -1
    
    def updateService(self, update_serv):
        """
        updateService
        ------------
        Update a device already present in catalog.
        """
        for i, service in enumerate(self.catDic["services"]):
            if service["servID"] == update_serv["servID"]:
                for key in update_serv.keys():
                    self.catDic["services"][i][key] = update_serv[key]
                self.lastUpdate = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.catDic["services"][i]["lastUpdate"] = self.lastUpdate
                self.catDic["lastUpdate"] = self.lastUpdate
                return 0
        return -1
    
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
                if len(uri) > 1: 
                    if uri[1] == "recentID":
                        # Retrieve the ID of the device added most recently
                        devID = self.catDic["devices"][-1]["devID"]
                        return json.dumps({'devID': devID})
                    
                    # Retrieve sensors of a specified device
                    elif uri[1] == "sensors" and "devID" in params:
                        devID = params["devID"]
                        search_dev = searchDict(self.catDic, "devices", "devID", devID)
                        if search_dev:
                            sensors = search_dev["resources"]["sensors"]
                            return json.dumps(sensors)
                        else:
                            raise cherrypy.HTTPError(404, f"Device {devID} not found!")
                    
                    elif uri[1] == "actuators" and "devID" in params:
                        devID = params["devID"]
                        search_dev = searchDict(self.catDic, "devices", "devID", devID)
                        if search_dev:
                            actuators = search_dev["resources"]["actuators"]
                            return json.dumps(actuators)
                        else:
                            raise cherrypy.HTTPError(404, f"Device {devID} not found!")
                        
                    else:
                        cherrypy.HTTPError(400, f"URI and parameters are not correct!")

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
                    elif "devID" in params:
                        devID = params["devID"]
                        search_gh = {}
                        for gh in self.catDic["greenhouses"]:
                            for dev in gh["devices"]:
                                if dev["devID"] == devID:
                                    search_gh = gh.copy()
                                    sensors = dev["sensors"]
                                    actuators = dev["actuators"]
                        
                        if search_gh:
                            if "name" and "sensID" in params:
                                name_sens = list(sensors.keys())[list(sensors.values()).index(params["sensID"])]
                                if name_sens == "temp_hum" and params["name"] == "temperature":
                                    actID = actuators["fan_control"]
                                elif name_sens == "CO2_level" and params["name"] == "CO2_level":
                                    actID = actuators["co2_control"]
                                elif name_sens == "temp_hum" and params["name"] == "humidity":
                                    actID = actuators["vaporizer_control"]
                                return json.dumps({"actID": actID})

                            else:   
                                return json.dumps(search_gh)
                        else:
                            raise cherrypy.HTTPError(404, f"No greenhouses associated\
                                                            to device {devID}")
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
                            if "plant" in params:
                                #return the plant dict
                                plant_name = params["plant"].lower()
                                search_plant = searchDict(search_usr, "ownedPlants", "plant", plant_name)
                                if search_plant:
                                    return json.dumps(search_plant)
                                else:
                                    raise cherrypy.HTTPError(404, f"Plant {plant_name} not found!")
                            else:
                                # return the requested user
                                return json.dumps(search_usr)
                        else:
                            raise cherrypy.HTTPError(404, f"User {usrID} not found!")

                    elif params == {}:
                        return json.dumps(self.dictInfo("users"))

                    else:
                        cherrypy.HTTPError(400, f"Parameters are missing or are not correct!")

            elif uri[0] == "plant":
                if "devID" in params and "sensID" in params:
                    devID = params["devID"]
                    search_gh = {}
                    for gh in self.catDic["greenhouses"]:
                        for dev in gh["devices"]:
                            if dev["devID"] == devID:
                                search_gh = gh.copy()
                                sensors = dev["sensors"]
                                actuators = dev["actuators"]
                                gh_selected = gh["ghID"]
                    
                    if search_gh:
                        sensID = params["sensID"]
                        search_plant = searchDict(search_gh, "plantsList", "sensID", sensID)
                        search_plant["ghID"] = gh_selected

                        if search_plant:
                            return json.dumps(search_plant)
                        else:
                            raise cherrypy.HTTPError(404, f"No plant associated with sensor {sensID}")
                    else:
                            raise cherrypy.HTTPError(404, f"No plant associated with device {sensID}")
                
                else:
                    cherrypy.HTTPError(400, f"Parameters are missing or are not correct!")
            
            elif uri[0] == "service":
                if len(uri) > 1: 
                    if uri[1] == "recentID":
                        # Retrieve the ID of the service added most recently
                        servID = self.catDic["services"][-1]["servID"]
                        return json.dumps({'servID': servID})
                        
                    else:
                        cherrypy.HTTPError(400, f"URI and parameters are not correct!")

                else:
                    if "servID" in params:
                        servID = params["servID"]
                        search_serv = searchDict(self.catDic, "services", "servID", servID)
                        if search_serv:
                            return json.dumps(search_serv)
                        else:
                            raise cherrypy.HTTPError(404, f"Service {servID} not found!")
                    elif "name" in params:
                        name = params["name"]
                        search_serv = searchDict(self.catDic, "services", "name", name)
                        if search_serv:
                            return json.dumps(search_serv)
                        else:
                            raise cherrypy.HTTPError(404, f"Service {name} not found!")
                    elif params == {}:
                        return json.dumps(self.dictInfo("services"))

                    else:
                        cherrypy.HTTPError(400, f"Parameters are missing or are not correct!")

                

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
            if uri[0] == "addDevice":
                if self.addDevice(bodyAsDict) == 0:
                    self.saveJson()
                    print(f'\nDevice {bodyAsDict["devID"]} added successfully!')
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
            
            elif uri[0] == "addService":
                if self.addService(bodyAsDict) == 0:
                    self.saveJson()
                    print(f'\nService {bodyAsDict["servID"]} added successfully!')
                else:
                    raise cherrypy.HTTPError(400, f'Service {bodyAsDict["servID"]} could not be added!')
            

    
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
            
            elif uri[0] == "updateUser":
                if self.updateUser(bodyAsDict) == 0:
                    self.saveJson()
                    print(f'\nUser {bodyAsDict["usrID"]} updated successfully')
                else:
                    print('User {bodyAsDict["devID"]} could not be updated')
                    raise cherrypy.HTTPError(400, "The user could not be updated!")
            
            elif uri[0] == "updateGreenhouse":
                if self.updateGreenhouse(bodyAsDict) == 0:
                    self.saveJson()
                    print('\nGreenhouse {bodyAsDict["ghID"]} updated successfully')
                else:
                    print('Greenhouse {bodyAsDict["ghID"]}could not be updated')
                    raise cherrypy.HTTPError(400, "The greenhouse could not be updated!")
            
            elif uri[0] == "updateService":
                if self.updateService(bodyAsDict) == 0:
                    self.saveJson()
                    print(f'\nService {bodyAsDict["servID"]} updated successfully')
                else:
                    print(f'Service {bodyAsDict["servID"]} could not be updated')
                    raise cherrypy.HTTPError(400, "The service could not be updated!")
    
    def cleaningDev(self, timeout):
        """
        cleaningDev
        --------
        Method to remove devices that are no more active.
        The inactivity is determined by a timeout. 
        """
        
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
    
    def cleaningServ(self, timeout):
        """
        cleaningServ
        --------
        Method to remove services that are no more active.
        The inactivity is determined by a timeout. 
        """
        for ind, service in enumerate(self.catDic["services"]):
                last_upd = time.mktime(datetime.strptime(service["lastUpdate"],
                                            "%Y-%m-%d %H:%M:%S").timetuple())
                current_t = datetime.timestamp(datetime.now())
                if current_t - last_upd >= timeout:
                    self.catDic["services"].pop(ind)
                    print(f"Service {service['servID']} has been removed due to inactivity!")
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
        while True:
            webService.cleaningDev(timeout=50)
            webService.cleaningServ(timeout=50)
    except KeyboardInterrupt:
        cherrypy.engine.block()