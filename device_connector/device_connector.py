# Device Connector : 28/02/2022

import requests
import json
from MyMQTT import *
import sys
import time
import datetime
import paho.mqtt.client as PahoMQTT

class Device_Connector(object):
    """Device connector class:
            - get info from the catalog
            - """

    def __init__(self):

        self.conf = json.load(open("device_connector\\conf.json"))
        self.devices = json.load(open("device_connector\\devices.json"))
        broker_dict = self.get_broker()
        print(broker_dict)
        self.client_mqtt = MyMQTT(broker_dict["clientID"],broker_dict["IP"],broker_dict["port"],self)

    def notify(self,topic,payload): 
        """Where we receive the topic which we are subscribed (plant control microservices)"""

        self.actuation = json.load(payload)
        if self.actuation["action"] == True:
            self.irrigator() #TODO: bisogna passargli il lotto a cui irrigare, lo prendo dal topic???

    def subscribe(self):
        """subscriber to all the irrigator topics of this device connector"""

        self.client_mqtt.start()
        time.sleep(3) #we want to be sure to do that commands in order
        self.client_mqtt.mySubscribe()

    def get_broker(self): 
        """GET all the broker information"""

        string = "http://" + self.conf["CatIP"] + ":" + self.conf["CatPort"] + "/broker" #URL for GET
        b_dict = requests.get(string).json()  #GET from catalog #need a .text /.body?
        return b_dict #return a json dict with BrokerIP and BrokerPort
    
    #def get_broker_topic(self,id): 
    #    """GET all the topic needed for sub and pub"""
    #    string = f"http://" + self.conf["CatIP"] + ":" + self.conf["CatPort"] + "/topics" + "/" + {id} #URL for GET
    #    top_dict = requests.get(string).json()  #GET from catalog the topics that i have to subscribe and publish
    #    return top_dict
    
    def post_sensor_Cat(self): 
        """Post to the catalog all the sensors of this device connector"""

        self.localtime = datetime.datetime.now() # get struct_time
        if (self.localtime-self.post_senstor_cat_Time) > datetime.timedelta(seconds=30):
            string = f"http://" + self.conf["CatIP"] + ":" + self.conf["CatPort"] + "/updateSensors" #URL for POST
            requests.post(string, json = self.devices)
        self.post_senstor_cat_Time = self.localtime
        
    
    def humiditySens(self):
        """Get the simulated value of the humidity sensor and publish it to the correspondent topic"""

        self.localtime = datetime.datetime.now() # get struct_time
        if (self.localtime-self.humidity_Time) > datetime.timedelta(minutes=1):
            for dv in self.devices["devicesList"]:
                if dv["type"] == "sensor":
                    #TODO: get the humidity level
                    #humidity = leggo da un file json?
                    #self.client_mqtt.myPublish(dv["topic"], humidity) #TODO: quante cose devo mandare? basta topic e umidità?
                    pass
        self.humidity_Time = self.localtime

    def irrigator(self, lot):
        #TODO: pubblicare al topic dell'attuatore dell'irrigazione?
        pass


if __name__=='__main__':

    dc = Device_Connector()

    while True:
        #dc.humiditySens()
        dc.post_sensor_Cat()
        time.sleep(5)