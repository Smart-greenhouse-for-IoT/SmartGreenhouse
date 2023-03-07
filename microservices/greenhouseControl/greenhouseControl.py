import json
import requests
from datetime import datetime
import files.MyMQTT as myMQTT

class catalogInterface():
    def __init__(self, catalog_IP, catalog_port):
        self._catalog_IP = catalog_IP
        self._catalog_port = catalog_port
    
    def getBroker(self):
        """GET broker information"""
        string = "http://" + self._catalog_IP + ":" + self._catalog_port + "/broker"  # URL for GET
        broker_dict = requests.get(string).json()  # GET from catalog #need a .text /.body?
        return broker_dict  # return a json dict with BrokerIP and BrokerPort

    def getTopic(self):
        """GET topic for subscription"""
        string = "http://" + self._catalog_IP + ":" + self._catalog_port + "/topic"  # URL for GET
        topic_dict = requests.get(string).json()  # GET from catalog #need a .text /.body?
        return topic_dict  # return a json dict with BrokerIP and BrokerPort

    def getGHThreshold(self):
        """GET the thresholds for the GreenHouse"""
        string = "http://" + self._catalog_IP + ":" + self._catalog_port + "/ghThreshold"  # URL for GET
        ghThreshold_dict = requests.get(string).json()  # GET from catalog #need a .text /.body?
        return ghThreshold_dict  # return a json dict with BrokerIP and BrokerPort

class greenHouseControl():      
    """Microservice class"""

    def __init__(self, broker_d, topic_d, cat_interface):
        self._pubSub = myMQTT.MyMQTT(broker_d["ClientID"], broker_d["IP"], broker_d["port"], self)
        self._pubSub.mySubscribe(topic_d["topic"])  # to subscribe to a topic
        self._cat_interface = cat_interface

    def notify(self, topic, payload):
        # topic example: "gh1/device1/globalhumidity"
        # payload example: "{"sensor_id":"aaa", "timestamp": "dd-mm-yy hh:mm", "value": "10"}"
        payload_dict = json.loads(payload)

        ghThreshold_d = self._cat_interface.getGHThreshold()

        if payload_dict["value"] < ghThreshold_d["min_value"]:
            actuation = True
            self._pubSub.myPublish(topic, json.dumps('{"actuation" : "True"}'))

if __name__=="__main__":
    file = open("files/config.json", "r")
    conf_dict = json.load(file)

    # I want to get the catalog 
    catalog = conf_dict["catalog"]
