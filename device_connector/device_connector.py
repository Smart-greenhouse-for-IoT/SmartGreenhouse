# Device Connector : 28/02/2022

import requests
import json
from sub.MyMQTT import *
from device_sensors.dht11 import *
from device_sensors.chirp import *
import sys
import time
import datetime
import paho.mqtt.client as PahoMQTT

class Device_Connector(object):
    """
    Device connector class:
    -----------------------
        - get info from the catalog
        - 
    """

    def __init__(self, conf_path, device_path):

        # Opening the configuration files
        with open(conf_path) as f:
            self.cat_info = json.load(f)

        # Opening the devices file
        with open(device_path) as f:
            self.mydevice = json.load(f)
        
        # Read all the sensors in self.mydevice list
        # and initialize it all to start obtaining their values
        self.measures = []
        self.sensors_list = []
        self.sensor_index = {}
        count = 0

        # At the start the program check the sensor that are connected to the device connector
        for sensor in self.mydevice['resources']['sensors']:
            
            if sensor['device_name'] == "chirp":
                self.sensor_index[str(sensor["sensID"])] = count
                count += 1

                moisture_conf = sensor.copy()
                self.sensors_list.append(chirp(moisture_conf))
                

            elif sensor['device_name'] == "DHT11":
                self.sensor_index[str(sensor["sensID"])] = count
                count += 1

                dht_conf = sensor.copy()
                self.sensors_list.append(DHT11(dht_conf))
                
        
        # At the start the program does not know wich actuators have
        for actuators in self.mydevice['resources']['actuators']:
            pass
        
        # Register to catalog
        self.registerToCat()

        ###############################
        ### MQTT client
        # Obtaining the broker information
        self.broker_dict = self.get_broker()
        
        self.client_mqtt = MyMQTT(
            clientID = self.broker_dict["clientID"],
            broker = self.broker_dict["IP"],
            port = self.broker_dict["port"],
            notifier=self
            )
        
        # Start MQTT client
        self.client_mqtt.start()

    def notify(self,topic,payload): 
        """
        notify
        ------
        Where we receive the topic which we are subscribed (plant control microservices)
        """

        self.actuation = json.load(payload)
        if self.actuation["action"] == True:
            pass
            #TODO: start irrigation

    def subscribe(self):
        """
        subscribe
        ---------
        Subscriber to all the irrigator topics of this device connector
        """

        self.client_mqtt.start()
        # We want to be sure to do that commands in order
        time.sleep(3) 
        self.client_mqtt.mySubscribe()
    
    def registerToCat(self):
        """
        registerToCat
        -------------
        This function will register the device connector to the catalog.
        Each time the registration is done all the device of this device connector \n
        are sent to the catalog.
        """

        # Address of the catalog for adding the devices
        addr = "http://" + self.cat_info["ip"] + ":" + self.cat_info["port"] + "/addDevice"

        try:
            #POST the devices to the catalog
            req = requests.post(addr, data=json.dumps(self.mydevice))
            if req.status_code == 200:
                print(f"Device {self.mydevice['devID']} added successfully!")
            else:
                print(f"Device {self.mydevice['devID']} could not be added!")
        except:
            raise Exception(f"Fail to establish a connection with {self.cat_info['ip']}")
    
    def updateToCat(self):
        """
        updateToCat
        -----------
        Update all the decice of this device connector to the catalog, to let the catalog \n
        know that this device connector and its devices are still 'alive'.
        """
        
        # Address of the catalog for updating the devices
        addr = "http://" + self.cat_info["ip"] + ":" + self.cat_info["port"] + "/updateDevice"
        try:
            #PUT the devices to the catalog
            req = requests.put(addr, data=json.dumps(self.mydevice))
            if req.status_code == 200:
                print(f"Device {self.mydevice['devID']} updated successfully!")
            else:
                print(f"Device {self.mydevice['devID']} could not be updated!")
        except:
            raise Exception(f"Fail to establish a connection with {self.cat_info['ip']}")

    def get_broker(self): 
        """
        get_broker
        ----------
        GET all the broker information
        """

        # Address of the catalog for obtaining all the informtions of the MQTT broker
        addr = "http://" + self.cat_info["ip"] + ":" + self.cat_info["port"] + "/broker" 
        try:
            b_dict = requests.get(addr).json()  
        except:
            raise Exception(f"Fail to establish a connection with {self.cat_info['ip']}")

        # Return a json dict with BrokerIP and BrokerPort
        return b_dict        
    
    def updateMeasures(self):
        """
        updateMeasures
        --------------
        Function that each time is called will save in a self list all the current measures \n
        of all the sensors connected to the device connector.
        """

        # Clear the list containing the old measures
        self.measures.clear()

        # For every active sensor connected to the device connector
        for sens_id in self.sensor_index.keys():
            print(f"Measuring with sensor {sens_id}")
            sens = {"sensor": sens_id,
                    "device": self.mydevice['devID']}
            
            # Obtain the measure from the sensor
            curr_meas = self.sensors_list[self.sensor_index[sens_id]].measure()

            # Some sensor can measure more than one value (i.e. temperature and humidity)
            for i in range(len(curr_meas)):
                # At each measure is attached the origin, sensor_id and device_id
                curr_meas[i].update(sens)
            print(f"Measure: {curr_meas}")

            # Add the current measure to the list containing the last measures 
            # self.measures[self.sensor_index[sens_id]] = curr_meas
            self.measures.append(curr_meas)

    def publishLastMeas(self):
        """
        publishLastMeas
        ---------------
        This function will public through MQTT all the values measured to the respective \n
        microservice and thinkspeak adaptor.
        """

        # Iteration over all the sensor device to publish on their topic 
        for sensor in self.mydevice["resources"]["sensors"]:

            # Check if the sensor have a topic where public the measure
            if "MQTT" in sensor["available_services"]:
                measure_list = self.measures[self.sensor_index[sensor["sensID"]]]
                
                services = sensor["services_details"][0]
                for ind, measure in enumerate(measure_list):
                    if services["service_type"] == "MQTT":
                        # Obtain the topic list of this sensor
                        topic_list = services["topic"]
                        app = topic_list[ind]

                        # Publish the measure to the respective topic
                        self.client_mqtt.myPublish(topic = topic_list[ind], msg = measure)
                    else:
                        raise Exception(f"Sensor {sensor['device_name']} {sensor['sensID']} of greenhouse {self.mydevice['ghID']} have not an MQTT interface")
            else:
                raise Exception(f"Sensor {sensor['device_name']} {sensor['sensID']} of greenhouse {self.mydevice['ghID']} have not an MQTT interface")



    def loop(self, refresh_time = 10):
        """
        Loop
        ----
        ### Input Parameters:
        - refresh_time: time to wait before doing another measure of the sensors.

        This function will run continuously until it is stopped.\n
        At each loop, after a fixed time, the device connector will obtain all the \n
        measures from its sensors, will send the information to the catalog and ... ???? #NOTE: to be finished
        """
        #TODO: every given time update the catalog registration to know DC is alive
        last_time = 0

        try:
            while True:
                print("looping\n")
                local_time = time.time()

                # Every refresh_time the measure are done and published to the topic
                if local_time - last_time > refresh_time: 
                    self.updateMeasures()
                    self.publishLastMeas()
                    self.updateToCat()
                    # self.post_sensor_Cat()
                    last_time = time.time() 

                time.sleep(5)

        except KeyboardInterrupt: #to kill the program
            print("Loop manually interrupted")
            pass


if __name__=='__main__':

    dc = Device_Connector(
        conf_path = "device_connector/conf.json",
        device_path = "device_connector/dev2.json"
        )

    dc.loop()