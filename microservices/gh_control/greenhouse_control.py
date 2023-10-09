import requests
import json
from sub.MyMQTT import * 
import time
from datetime import datetime
from catalogInterface import *



# Open and initialize with config.json
class GHControl():

    def __init__(self, conf_path, confMS_path):

        with open(conf_path) as f:
            self.conf_dict = json.load(f)
        
        # Opening the devices file
        with open(confMS_path) as f:
            self.myservice = json.load(f)

        self.addr_cat = "http://" + self.conf_dict["ip"] + ":" + self.conf_dict["port"]

        self.registerToCat()

        self._topic = self.conf_dict.get("topic")
        self.broker_dict = self.get_broker()
        
        self._pubSub = MyMQTT( clientID = self.conf_dict["clientID"], broker = self.broker_dict["IP"], port = self.broker_dict["port"], notifier=self) 
        self._pubSub.start()

        for topic in self._topic:
            self._pubSub.mySubscribe(topic)


    
    def registerToCat(self):
        """
        registerToCat
        -------------
        This function will register the plant control service to the catalog.
        """

        # Address of the catalog for adding the devices
        try:
            req_dev = requests.post(self.addr_cat + "/addService", data=json.dumps(self.myservice))
            if req_dev.ok:
                print(f"Plant control service {self.myservice['servID']} added successfully!")
            else:
                print(f"Plant control service {self.myservice['servID']} could not be added!")
        except:
            raise Exception(f"Fail to establish a connection with {self.conf_dict['ip']}")


    def updateToCat(self):
        """
        updateToCat
        -----------
        Update all the decice of this device connector to the catalog, to let the catalog \n
        know that this device connector and its devices are still 'alive'.
        """
        
        # Address of the catalog for updating the devices
        try:
            #PUT the devices to the catalog
            req = requests.put(self.addr_cat + "/updateService", data=json.dumps(self.myservice))
            if req.ok:
                print(f"Plant control service {self.myservice['servID']} updated successfully!")
            else:
                print(f"Plant control service {self.myservice['servID']} could not be updated!")
        except:
            raise Exception(f"Fail to establish a connection with {self.conf_dict['ip']}")
    

    def getThresholdsGH(self, devID, sensID):

        addr = f"{self.addr_cat}/greenhouse?devID={devID}&sensID={sensID}"
        try:
            #Get the status to the catalog
            req = requests.get(addr)
            if req.status_code == 200:
                return req.json() 

            else:
                print(f"Request failed!")
        except:
            raise Exception(f"Fail to establish a connection with {self.cat_info['ip']}")
        

    def get_broker(self): 
        """
        get_broker
        ----------
        GET all the broker information
        """

        # Address of the catalog for obtaining all the informtions of the MQTT broker
        try:
            b_dict = requests.get(self.addr_cat + "/broker").json()  
        except:
            raise Exception(f"Fail to establish a connection with {self.conf_dict['ip']}")

        # Return a json dict with BrokerIP and BrokerPort
        return b_dict       



    def notify(self, topic, body):
        '''This function is the on message callback
        '''
        
        measure_dict = json.loads(body)
        measure_dict_resp = {}

        GH_description = self.getThresholdsGH(measure_dict.get("device"), measure_dict.get("sensor"))

        if topic.split("/")[3] == "humidity":
            if measure_dict.get("v") < GH_description("th_min"):
                measure_dict_resp["command"] = "start"

            else:
                measure_dict_resp["command"] = "stop"
                

        if topic.split("/")[3] == "temperature":
            if measure_dict.get("v") < GH_description("th_min"): 
                measure_dict_resp["command"] = "start"
            else:
                measure_dict_resp["command"] = "stop"
                
               
        #set up response message
        topic_ = topic.split("/")
        measure_dict_resp["devID"] = topic_[1]
        topic_[2] = GH_description.get("actID")
        measure_dict_resp["devID"] = topic_[2]
        measure_dict_resp["timestamp"] = time.now()

        self._pubSub.myPublish("/".join(topic_), measure_dict)


    def loop(self, refresh_time = 10):

        last_time = 0
        try:
            while True:
                print("looping\n")
                local_time = time.time()

                # Every refresh_time the measure are done and published to the topic
                if local_time - last_time > refresh_time: 

                    self.updateToCat()

                    last_time = time.time() 

        except KeyboardInterrupt: #to kill the program
            print("Loop manually interrupted")
            pass


if __name__ == "__main__":

    gh_control = GHControl(
        conf_path = "microservices/conf.json",
        confMS_path = "microservices/confMS.json")

    gh_control.loop()
    