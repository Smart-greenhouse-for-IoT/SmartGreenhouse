import requests
import json
from sub.MyMQTT import *
import time
from catalogInterface import *
import pandas as pd

'''
retrieved_data = {
    'n': 'measured quantity',
    'u': 'unit',
    't': 'timestamp',
    'v': 'measured value',
    'devID': '',
    'sensID': ''
    'actID': ''
}
'''


class ThingspeakAdaptor():

    def __init__(self, conf_path):
        cat = catalogInterface(conf_path = conf_path)

        with open(conf_path) as f:
            self.conf_dict = json.load(f)

        self.fields_dict = {
            'api_key': None, # conf_json
            'field1': None, # catalog
            'field2': None, # topic/message
            'field3': None, # topic/message
            'field4': None, # message
            'field5': None, # message
            'field6': None, # message
            'field7': None # catalog
        }
        self.url_TS = self.conf_dict.get('url_TS')
        self._topic = self.conf_dict.get("topic")
        self.broker_dict = cat.get_broker()
        
        self._pubSub = MyMQTT( clientID = "ts_adaptor", broker = self.broker_dict["IP"], port = self.broker_dict["port"], notifier=self) 
        
        self._pubSub.start()
        
        time.sleep(3)
        self._pubSub.mySubscribe(self._topic)

        self.addr_cat = "http://" + self.conf_dict["ip"] + ":" + self.conf_dict["port"]
     
    def dictCreation(self, topic, msg):
        fields = self.fields_dict.copy()
        fields['api_key'] = self.conf_dict['write_key']
        fields['field1'] = 1# self.retrieveGHID(msg.get('devID'))
        fields['field2'] = msg.get('devID')
        fields['field3']: msg.get('sensID')
        fields['field4']: msg.get('n')
        fields['field5'] = msg.get('v')
        fields['field6'] = msg.get('t')
        fields['field7'] = 1# self.retrievePlant_type(msg.get('devID'), msg.get('sensID'))
        return fields

    def sendDataToTS(self, field_dict):

        print(json.dumps(field_dict))
        
        response = requests.post(self.url_TS, field_dict)
        print(response.status_code)
        if response.status_code == 200:
            print('Data sent to ThingSpeak successfully!')
        else:
            print('Failed to send data to ThingSpeak.')

    def notify(self, topic, msg):
            print("File correctly received")
            msg_json = json.loads(msg)
            #print(msg_json)
            field_dict = self.dictCreation(topic, msg_json)
            self.sendDataToTS(field_dict)

    def retrieveGHID(self, devID):
        ghID = requests.get(f'{self.addr_cat}/greenhouse?devID={devID}')
        return ghID
    
    def retrievePlant_type(self, devID, sensID):
        plant_type = requests.get(f'{self.addr_cat}/greenhouse?devID={devID}&sensID={sensID}')
        return plant_type
    
    def loop(self):
        while 1:
            i = 0


if __name__ == "__main__":
    
    TS = ThingspeakAdaptor("Thingspeak\conf.json")
    TS.loop()
    
