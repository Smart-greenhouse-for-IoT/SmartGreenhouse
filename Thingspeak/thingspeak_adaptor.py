import requests
import json
from sub.MyMQTT import *

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

# api_url = 'https://api.thingspeak.com/update.json'

class ThingspeakAdaptor():

    def __init__(self, conf_path):

        with open(conf_path) as f:
            self.conf_dict = json.load(f)

        self.fields_dict = {
            'api_key': None, # conf_json
            'ghID': None, # catalog
            'devID': None, # topic/message
            'sensID': None, # topic/message
            'quantity': None, # message
            'value': None, # message
            'timestamp': None, # message
            'plant_type': None # catalog
        }
        self.url_TS = self.conf_dict.get('url_TS')
        self._topic = self.conf_dict.get("topic")
        self.broker_dict = self.catalog_interf.get_broker()
        
        self._pubSub = MyMQTT( clientID = self.broker_dict["clientID"], broker = self.broker_dict["IP"], port = self.broker_dict["port"], notifier=self) 
        self._pubSub.start()
        self._pubSub.mySubscribe(self._topic)
     
    def dictCreation(self, topic, msg):
        fields = self.fields_dict.copy()
        fields['api_key'] = self.conf_dict['api_key']
        fields['ghID'] = self.retrieveGHID(msg.get('devID'))
        fields['devID'] = msg.get('devID')
        fields['sensID']: msg.get('sensID')
        fields['quantity']: msg.get('n')
        fields['value'] = msg.get('v')
        fields['timestamp'] = msg.get('t')
        fields['plant_type'] = self.retrievePlant_type(msg.get('devID'), msg.get('sensID'))
        return fields

    def sendDataToTS(self, field_dict):
        
        response = requests.post(self.url_TS, json=json.dumps(field_dict))

        if response.status_code == 200:
            print('Data sent to ThingSpeak successfully!')
        else:
            print('Failed to send data to ThingSpeak.')

    def notify(self, topic, msg):
            msg_json = json.loads(msg)
            field_dict = self.dictCreation(topic, msg_json)
            self.sendDataToTS(field_dict)

# inserire ip e port corretti
    def retrieveGHID(self, devID):
        ghID = requests.get(f'{self.ip}:{self.port}/{devID}')
        return ghID
    
    def retrievePlant_type(self, devID, sensID):
        plant_type = requests.get(f'{self.ip}:{self.port}/{devID}/{sensID}')
        return plant_type