import requests
import json
from sub.MyMQTT import *
import time
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

    def __init__(self, conf_path, confTS_path):
        # Conf_dict contains catalog's information
        with open(conf_path) as f:
            self.conf_dict = json.load(f)
        
        # confTS contains information regarding the adaptor
        with open(confTS_path) as f:
            self.myTS = json.load(f)

        self.fields_dict = {
            'api_key': None, # conf_json
            'field1': None, # catalog
            'field2': None, # topic/message
            'field3': None, # topic/message
            'field4': None, # message
            'field5': None, # message
            'field6': None, # message
            'field7': None, # catalog
            'field8': None
        }

        self.tot_dict = {
            'api_key': [], # conf_json
            'field1': [], # catalog
            'field2': [], # topic/message
            'field3': [], # topic/message
            'field4': [], # message
            'field5': [], # message
            'field6': [], # message
            'field7': [], # catalog
            'field8': []
        }
        self.url_TS = self.myTS['TS_info']['url_TS']
        self._topic = self.myTS['endpoints_details'][0]['topic']

        self.addr_cat = "http://" + self.conf_dict["ip"] + ":" + self.conf_dict["port"]

        self.broker_dict = self.get_broker()
        
        self._pubSub = MyMQTT( clientID = "ts_adaptor", broker = self.broker_dict["IP"], port = self.broker_dict["port"], notifier=self) 
        
        self._pubSub.start()
        
        time.sleep(3)
        for topic in self._topic:
            self._pubSub.mySubscribe(topic)

        self.registerToCat()
    
    def get_broker(self, tries = 10): 
        """
        get_broker
        ----------
        GET all the broker information
        """

        count = 0
        update = False
        while count < tries and not update:
            count += 1
            try:
                b_dict = requests.get(self.addr_cat + "/broker").json()  
                update = True
            except:
                print(f"Fail to establish a connection with {self.conf_dict['ip']}")
                time.sleep(1)

        if update == False:
            raise Exception(f"Fail to establish a connection with {self.conf_dict['ip']}")

        # Return a json dict with BrokerIP and BrokerPort
        return b_dict      

    def registerToCat(self, tries = 10):
        """
        registerToCat
        -------------
        This function will register the TS adaptor to the catalog.
        """

        count = 0
        update = False
        while count < tries and not update:
            count += 1
            try:
                req_serv = requests.post(self.addr_cat + "/addService", data=json.dumps(self.myTS))
                if req_serv.ok:
                    print(f"Service {self.myTS['servID']} added successfully!")
                    update = True
                else:
                    print(f"Service {self.myTS['servID']} could not be added!")
            except:
                print(f"Fail to establish a connection with {self.conf_dict['ip']}")
                time.sleep(1)

        if update == False:
            raise Exception(f"Fail to establish a connection with {self.conf_dict['ip']}")  
    
    def updateToCat(self, tries = 10):
        """
        updateToCat
        -----------
        Update the TS adaptor  to the catalog, to let the catalog \n
        know that this service is still 'alive'.
        """
        
        count = 0
        update = False
        while count < tries and not update:
            count += 1
            try:
                #PUT the TS to the catalog services
                req = requests.put(self.addr_cat + "/updateService", data=json.dumps(self.myTS))
                if req.ok:
                    update = True
                    print(f"Service {self.myTS['servID']} updated successfully!")
                else:
                    print(f"Service {self.myTS['servID']} could not be updated!")
            except:
                print(f"Fail to establish a connection with {self.conf_dict['ip']}")
                time.sleep(1)

        if update == False:
            raise Exception(f"Fail to establish a connection with {self.conf_dict['ip']}")
    
    def tot_dictCreation(self, partial_dict):

        for key in partial_dict.keys():
            self.tot_dict[key].append(partial_dict.get(key))
     
    def dictCreation(self, topic, msg):
        fields = self.fields_dict.copy()
        fields['api_key'] = self.myTS['TS_info']['write_key']
        fields['field1'] = self.retrieveGHID(msg.get('devID'))
        fields['field2'] = msg.get('devID')
        fields['field3'] = msg.get('sensID')
        fields['field4'] = msg.get('n')
        fields['field5'] = msg.get('v')
        fields['field6'] = msg.get('t')
        if topic.split("/")[3] == 'moisture_level':
            fields['field7'] = self.retrievePlant_type(msg.get('devID'), msg.get('sensID'))

        if topic.split("/")[2].startswith('a'):
            fields['field8'] = msg.get('command')

        return fields

    def sendDataToTS(self, dict):
        """
        sendDataToTS
        ------------

        """
        
        try:
            response = requests.post(self.url_TS, dict)
            if response.ok:
                print('Data sent to ThingSpeak successfully!')
            else:
                print('Failed to send data to ThingSpeak.')
        except:
            print('ThingSpeak not reachable')

    def notify(self, topic, msg):
        """
        notify
        ------

        """
        print(f"Msg:received from topic: {topic}")
        msg_json = json.loads(msg)
        # print(msg_json)
        field_dict = self.dictCreation(topic, msg_json)
        self.tot_dictCreation(field_dict)

    def retrieveGHID(self, devID, tries = 10):
        """
        retrieveGHID
        ------------

        """
        count = 0
        update = False
        while count < tries and not update:
            count += 1
            try:
                ghID = requests.get(f'{self.addr_cat}/greenhouse?devID={devID}')
                update = True
            except:
                print(f"Fail to establish a connection with catalog!")
                time.sleep(1)

        if update == False:
            raise Exception(f"Fail to establish a connection with catalog!")
        
        return ghID.json()['ghID']   
    
    def retrievePlant_type(self, devID, sensID, tries = 10):
        """
        retrievePlant_type
        ------------------

        """
        # if it is different from s1 and s2 
        # (predefined sensor for the greenhouse and not for the plant)
        # then it is possible to retrive the plant name
        if sensID != 's1' and sensID != 's2':
            count = 0
            update = False
            while count < tries and not update:
                count += 1
                try:
                    plant_type = requests.get(f'{self.addr_cat}/plant?devID={devID}&sensID={sensID}')
                    update = True
                except:
                    print(f"Fail to establish a connection with catalog!")
                    time.sleep(1)

            if update == False:
                raise Exception(f"Fail to establish a connection with catalog!")
            
            return plant_type.json()['plant']  
        
        else:
            return None
    
    def cleanDict(self):
           self.tot_dict = {
            'api_key': [], # conf_json
            'field1': [], # catalog
            'field2': [], # topic/message
            'field3': [], # topic/message
            'field4': [], # message
            'field5': [], # message
            'field6': [], # message
            'field7': [], # catalog
            'field8': []
        }
    
    def loop(self, refresh_time = 60):
        """
        Loop
        ----
        ### Input Parameters:
        - refresh_time: time to wait before doing another measure of the sensors.

        This function will run continuously until it is stopped.\n
        """
        last_time = 0

        try:
            while True:
                time.sleep(5)
                print("looping\n")
                local_time = time.time()

                # Every refresh_time the measure are done and published to the topic
                if local_time - last_time > refresh_time: 
                    self.updateToCat(tries=15)
                    self.sendDataToTS(self.tot_dict)
                    self.cleanDict()
                    # self.post_sensor_Cat()
                    last_time = time.time() 
                

        # To kill the program
        except KeyboardInterrupt: 
            print("Loop manually interrupted")


if __name__ == "__main__":
    
    TS = ThingspeakAdaptor("Thingspeak/conf.json", "Thingspeak/confTS.json")
    TS.loop()
    
