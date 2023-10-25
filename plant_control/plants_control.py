import requests
import json
from sub.MyMQTT import * 
import time
from datetime import datetime
import threading


# Open and initialize with config.json
class plantsControl():

    def __init__(self, conf_path, confMS_path):

        with open(conf_path) as f:
            self.conf_dict = json.load(f)
        
        # Opening the devices file
        with open(confMS_path) as f:
            self.myservice = json.load(f)

        self.addr_cat = "http://" + self.conf_dict["ip"] + ":" + self.conf_dict["port"]
        self.track_actuation_dict = {}
        self._actuation_time = 2

        self.registerToCat()
        for end_det in self.myservice["endpoints_details"]:
            if end_det.get("endpoint") == "MQTT":
                self._topic = end_det["topics"]
            
        self.broker_dict = self.get_broker()
        
        self._pubSub = MyMQTT( clientID = self.conf_dict["clientID"], broker = self.broker_dict["IP"], port = self.broker_dict["port"], notifier=self) 
        self._pubSub.start()
        for topic in self._topic:
            self._pubSub.mySubscribe(topic)
        

    def notify(self, topic, body):
        '''
        This function is the on message callback
        '''

        measure_dict = json.loads(body)

        plant_description = self.getThresholdsPlant(measure_dict.get("devID"), measure_dict.get("sensID"))        
        topic_act = self.transformTopic(topic, plant_description.get("actID"))
        measure_dict["plant"] = plant_description.get("plant")
        if measure_dict.get("v") < plant_description.get("th_min"):

            if topic_act not in self.track_actuation_dict:
                self.startActuation(topic_act, measure_dict)
            

    def startActuation(self, topic, body):

        measure_dict_resp = body

        measure_dict_resp["devID"] = topic.split("/")[1]
        measure_dict_resp["actID"] = topic.split("/")[2]
        measure_dict_resp["timestamp"] = time.time()
        measure_dict_resp["command"] = True
        

        self._pubSub.myPublish(topic, measure_dict_resp)

        self.track_actuation_dict[topic] = measure_dict_resp
        self.track_actuation_dict[topic]["timer"] = threading.Timer(self._actuation_time, self.stopActuation, args=(topic,))
        self.track_actuation_dict[topic]["timer"].start()
        
        print(f"Actuation started, topic:{topic}")

    def stopActuation(self, topic_):

        message = self.track_actuation_dict.get(topic_)
        
        message.pop("timer")
        message["timestamp"] = time.time()
        message["command"] = False
        self._pubSub.myPublish(topic_, message)

        self.track_actuation_dict.pop(topic_)

        print(f"Actuation stopped, topic:{topic_}")


    def transformTopic(self, topic, actuator):
        
        topic_ = topic.split("/")
        topic_[2] = actuator
        topic_ = ("/").join(topic_)
        return topic_

    
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


    def getThresholdsPlant(self, devID, sensID):

        addr = f"{self.addr_cat}/plant?devID={devID}&sensID={sensID}"
        try:
            #Get the status to the catalog
            req = requests.get(addr)
            if req.status_code == 200:
                return req.json() 

            else:
                print(f"Request failed!")
        except:
            raise Exception(f"Fail to establish a connection with {self.cat_info['ip']}")
        

    def loop(self, refresh_time = 10):

        last_time = 0
        try:
            while True:
                
                local_time = time.time()

                # Every refresh_time the measure are done and published to the topic
                if local_time - last_time > refresh_time: 
                    print("looping\n")
                    self.updateToCat()

                    last_time = time.time() 

        except KeyboardInterrupt: #to kill the program
            print("Loop manually interrupted")
            pass



if __name__ == "__main__":

    plant_control = plantsControl(
        conf_path = "plant_control/conf.json",
        confMS_path = "plant_control/confMS.json")

    plant_control.loop()
    