# Device Connector : 28/02/2022

import requests
import json
import sys
import time
import datetime
import paho.mqtt.client as PahoMQTT

class Device_Connector(object):
    """Get data from catalog"""

    def __init__(self):
        self.conf = json.load(open("setting.json"))
        return

    def get_broker(self): 
        """GET all the broker information"""
        string = "http://" + self.conf["CatIP"] + ":" + self.conf["CatPort"] + "/broker" #URL for GET
        b_dict = json.loads(requests.get(string))  #GET from catalog #need a .text /.body?
        return b_dict #return a json dict with BrokerIP and BrokerPort
    
    def get_broker_topic(self): 
        """GET all the topic needed for sub and pub"""
        string = "http://" + self.conf["CatIP"] + ":" + self.conf["CatPort"] + "/topics" #URL for GET
        top_dict = json.loads(requests.get(string))  #GET from catalog the topics that i have to subscribe and publish form 
        return top_dict
    
class MyPublisher(object): 
    """MQTT Publisher."""

    def __init__(self, clientID, serverIP, port):
        """Initialise MQTT client."""
        self.clientID = clientID
        self.devID = clientID
        self.port = int(port)
        self.messageBroker = serverIP
        self._paho_mqtt = PahoMQTT.Client(clientID, False)
        self._paho_mqtt.on_connect = self.my_on_connect
        self.loop_flag = 1

    def start(self):
        """Start publisher."""
        self._paho_mqtt.connect(self.messageBroker, self.port)
        self._paho_mqtt.loop_start()

    def stop(self):
        """Stop publisher."""
        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()

    def my_on_connect(self, client, userdata, flags, rc):
        """Define custom on_connect function."""
        print("P - Connected to %s - Res code: %d" % (self.messageBroker, rc))
        self.loop_flag = 0

    def my_publish(self, message, topic):
        """Define custom publish function."""
    
if __name__=='__main__':
    pass