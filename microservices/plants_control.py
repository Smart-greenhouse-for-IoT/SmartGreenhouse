import requests
import json
from sub.MyMQTT import * 
import time
from datetime import datetime
from catalogInterface import *

# Open and initialize with config.json
class plantsControl():

    def __init__(self, conf_path):

        with open(conf_path) as f:
            self.conf_dict = json.load(f)

        self.catalog_interf = catalogInterface(conf_path)

        self._topic = self.conf_dict.get("topic")
        self.broker_dict = self.catalog_interf.get_broker()
        
        self._pubSub = MyMQTT( clientID = self.broker_dict["clientID"], broker = self.broker_dict["IP"], port = self.broker_dict["port"], notifier=self) 
        self._pubSub.start()
        self._pubSub.mySubscribe(self._topic)
        

    def notify(self, topic, body):
        '''
        This function is the on message callback
        '''

        measure_dict = json.loads(body)
        measure_dict_resp = {}

        plant_description = self.catalog_interf.getThresholdsPlant(measure_dict.get("device"), measure_dict.get("sensor"))

        if measure_dict.get("v") < plant_description.get("th_min"):
            measure_dict_resp["command"] = "start"
            
        else:
            measure_dict_resp["command"] = "stop"


        
        topic_ = topic.split("/")

        measure_dict_resp["devID"] = topic_[1]
        
        topic_[2] = plant_description.get("actID")
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

                    self.catalog_interf.updateToCat()

                    last_time = time.time() 

        except KeyboardInterrupt: #to kill the program
            print("Loop manually interrupted")
            pass



if __name__ == "__main__":

    plant_control = plantsControl(
        conf_path = "microservices/conf.json")

    plant_control.loop()
    