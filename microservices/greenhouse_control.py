import requests
import json
from sub.MyMQTT import * 
import time
from datetime import datetime
from catalogInterface import *



# Open and initialize with config.json
class GHControl():

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
        '''This function is the on message callback
        '''
        
        measure_dict = json.loads(body)

        if measure_dict.get("humidity") < self.catalog_interf.getGH("th_min"): # TODO
            measure_dict["fan_activation"] = True
            measure_dict["timestamp"] = datetime.now().strftime("")  # TODO aggiungere formato strftime

        if measure_dict.get("temperature") < self.catalog_interf.getGH("th_min"): # TODO
            measure_dict["dimmerLED_activation"] = True
            measure_dict["timestamp"] = datetime.now().strftime("")  # TODO aggiungere formato strftime

        self._pubSub.myPublish(topic, measure_dict)


if __name__ == "__main__":

    gh_control = GHControl(conf_path = "microservices/conf.json")

    gh_control.loop()
    