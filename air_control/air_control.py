import json
import requests
from tools.MyMQTT import *

class air_control:
    def __init__(self) -> None:
        self.conf = json.load(open("air_control/conf.json"))
        broker_dict = self.get_broker()
        self.client_mqtt = MyMQTT(broker_dict["clientID"],broker_dict["IP"],broker_dict["port"], self)
        self.client_mqtt.start()


    def get_broker(self):
        """GET all the broker information"""
        string = "http://" + self.conf["CatIP"] + ":" + self.conf["CatPort"] + "/broker" #URL for GET
        b_dict = requests.get(string).json()  #GET from catalog #need a .text /.body?
        return b_dict #return a json dict with BrokerIP and BrokerPort
    
class subscriber_ac(air_control):
    def __init__(self) -> None:
        self.topic = "smartGreenhouse/g_001/air_cotrol/+"   #NOTE: possiamo assumere di avere già il topic in questo modo?
        self.client_mqtt.mySubscribe(self.topic)
        #TODO: inserire in controlli in function notify