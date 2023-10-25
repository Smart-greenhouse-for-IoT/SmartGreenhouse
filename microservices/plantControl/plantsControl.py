import requests
from datetime import datetime
import json
import files.MyMQTT as MQTT_
import paho.mqtt.client as PahoMQTT

# le assegnazioni vasetti
# il db con i thrshld
# i topic dev connector


class catalogInterface():
    def __init__(self, catalog):
        self._catalogIP = catalog
    
    def getTopic():
        pass

    def getPlantInfo(self, plant_name):
        pass

# Open and initialize with config.json
class plantsControl():

    def __init__(self, catalog_f, Id, IP_broker, mqtt_port, topic):

        self._catalogF = catalog_f
        self._topic = topic
        self._pubSub = MQTT_.MyMQTT(Id, IP_broker, mqtt_port, self)  # self passed for notifier
        self._pubSub.start()
        self._pubSub.mySubscribe(self._topic)

    def notify(self, topic, body):
        '''This function is the on message callback
        
        json:

        {
            plant: "xxx",
            humidity: value,
            timestamp: ""
        }
        returned with the key irrigatio that is bool
        '''
        
        measure_dict = json.loads(body)
        plant_type = measure_dict.get("plant")

        plant_description = self._catalogF.getPlantInfo(plant_type)

        if measure_dict.get("humidity") < plant_description.get("th_min"):
            measure_dict["irrigation"] = True
            measure_dict["timestamp"] = datetime.now().strftime("")  # aggiungere strftime

        self._pubSub.myPublish(topic, measure_dict)


if __name__ == "__main__":

    conf_dict = json.load(open("conf.json", "r"))
    
   # sistemare class hierarchy




    





    
