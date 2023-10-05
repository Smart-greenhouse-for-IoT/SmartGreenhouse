import requests
import json
from sub.MyMQTT import *
import time

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

        self.url_TS = self.conf_dict['thingspeak_url']
        self.broker_dict = self.get_broker()

        self.device = self.getCatDevice()
        
        self.client_mqtt = MyMQTT( clientID = self.broker_dict["clientID"], broker = self.broker_dict["IP"], port = self.broker_dict["port"], notifier=self) 
        self.client_mqtt.start()

    #########################################
    ############### MQTT part ###############
    #########################################

    def subscribe(self, topic):
        """
        subscribe
        ---------
        Subscriber to all the sensor topics of all DC
        """

        self.client_mqtt.mySubscribe(topic = topic)

    def get_broker(self): 
        """
        get_broker
        ----------
        GET all the broker information
        """

        # Address of the catalog for obtaining all the informtions of the MQTT broker
        addr = "http://" + self.conf_dict["ip"] + ":" + self.conf_dict["port"] + "/broker" 
        try:
            b_dict = requests.get(addr).json()  
        except:
            raise Exception(f"Fail to establish a connection with {self.conf_dict['ip']}")

        # Return a json dict with BrokerIP and BrokerPort
        return b_dict   
    
    def getCatDevice(self):
        """
        getCatDevice
        ------------
        
        """
        # Address of the catalog for updating the devices
        addr = "http://" + self.conf_dict["ip"] + ":" + self.conf_dict["port"] + "/device"
        try:
            #PUT the devices to the catalog
            return requests.get(addr).json()
        except:
            raise Exception(f"Fail to establish a connection with {self.conf_dict['ip']}")
     
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


if __name__ == "__main__":

    ThingspeakAdaptor("Thingspeak\conf.json")
    while 1:
        time.sleep(10)