import cherrypy
import json
import catalog

class REST_catalog():
    exposed = True
    def __init__(self):
        self.catObj = catalog.catalog() #define catalog object
    
    def GET(self, *uri, **params):
        # return broker info as json string
        if uri[0] == "broker":
            return json.dumps(self.catObj.brokerInfo())
        
        # DEVICES INFO
        elif uri[0] == "devicesList":
            if len(params) != 0:
                ids = list(map(int,params.get('id')))
                idDevices = self.catObj.devicesInfo(ids)
                return json.dumps(idDevices) 
            devices = self.catObj.devicesInfo()
            return json.dumps(devices)

        # retrieve humidity threshold given ID 
        # /getThresholds?plant=basilico
        elif uri[0] == "getThresholds":
            humidityTh = self.catObj.thresholdHumidity(params.get("plant")) # retrieve humidity threshold given plant name
            return json.dumps(humidityTh)   # return a list containing min and max thresholds
        
        elif uri[0] == "infoPlantControl":
            pass

    
    def POST(self, *uri, **params):
        bodyAsString = cherrypy.request.body.read()
        bodyAsDictionary = json.loads(bodyAsString)
        if uri[0] == "updateSensors":
            self.catObj.updateSensors(bodyAsDictionary)
        elif uri[0] == "user":
            self.catObj.addUser(bodyAsDictionary)
    
    def PUT(self, *uri, **params):  # /device/id?deviceName=DHT11&availableServices=MQTT
        if uri[0] == "device":
            self.catObj.updateDevice(id=uri[1], infoToUpdate=params)

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