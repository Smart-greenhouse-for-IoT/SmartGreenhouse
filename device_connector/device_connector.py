# Device Connector : 28/02/2022

import requests
import json
from MyMQTT import *
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

class pub():
    def __init__(self, clientID, broker, port, topic):
        self.broker = broker
        self.port = port
        self.topic = topic
        self.clientID = clientID
        self.client = MyMQTT(self.clientID, self.broker, self.port,self)
    
    def startPub(self):
        """Starting the publisher"""
        self.client.start()
        time.sleep(3) #we want to be sure to do that commands in order
        
    def pubEvent(self):
        """Publish event"""
        self.client.myPublish(self.topic)

class sub():
    def __init__(self, clientID, broker, port, topic):
        self.broker = broker
        self.port = port
        self.topic = topic
        self.clientID = clientID
        self.client = MyMQTT(self.clientID, self.broker, self.port,self)

    def startSub(self):
        """Starting the subscriber"""
        self.client.start()
        time.sleep(3) #we want to be sure to do that commands in order
        self.client.mySubscribe(self.topic) #subscribing to the selected topic

    def notify(self,topic,payload):
        """Receiving the topic"""
        

if __name__=='__main__':

    while True:
        time.sleep(1)