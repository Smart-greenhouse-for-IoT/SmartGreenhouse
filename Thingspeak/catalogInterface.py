import json
import requests


class catalogInterface():

    def __init__(self, conf_path):

        with open(conf_path) as f:
            self.conf_dict = json.load(f)
        
    def get_broker(self): 
        """
        get_broker
        ----------
        GET all the broker information
        """

        # Address of the catalog for obtaining all the informations of the MQTT broker
        addr = "http://" + self.conf_dict["ip"] + ":" + self.conf_dict["port"] + "/broker" 
        try:
            broker_dict = requests.get(addr).json()  
        except:
            raise Exception(f"Fail to establish a connection with {self.conf_dict['ip']}")

        # Return a json dict with BrokerIP and BrokerPort
        return broker_dict
    
    def get_devices(self):
        """
        get_broker
        ----------
        GET the list of devices connected to the catalog and currently running
        """

        # Address of the catalog for obtaining all the informations of the MQTT broker
        addr = "http://" + self.conf_dict["ip"] + ":" + self.conf_dict["port"] + "/device" #TODO 
        try:
            devices_dict = requests.get(addr).json()  
        except:
            raise Exception(f"Fail to establish a connection with {self.conf_dict['ip']}")

        # Return a json dict with BrokerIP and BrokerPort
        return devices_dict
    
    def updateToCat(self):
        """
        updateToCat
        -----------
        Update the current status of the microservice to the catalog --> 'alive'.
        """
        
        # Address of the catalog for updating the status
        addr = "http://" + self.cat_info["ip"] + ":" + self.cat_info["port"] + "/updateMS"  #TODO fox
        try:
            #PUT the status to the catalog
            req = requests.put(addr, data=json.dumps('"STATUS": "alive"')) #sistemare json mandato TODO STEVE
            if req.status_code == 200:
                print(f"Updated to catalog (HB)")
            else:
                print(f"Update failed!")
        except:
            raise Exception(f"Fail to establish a connection with {self.cat_info['ip']}")
        
    def getThresholdsPlant(self, plant_name, devID):

        addr = "http://" + self.cat_info["ip"] + ":" + self.cat_info["port"] + "/service/getThrPlant"  #TODO fox
        try:
            #Get the status to the catalog
            req = requests.get(addr, data=json.dumps(self.mydevice))
            if req.status_code == 200:
                return req.json()  #sistema quando implementato

            else:
                print(f"Update failed!")
        except:
            raise Exception(f"Fail to establish a connection with {self.cat_info['ip']}")
        
