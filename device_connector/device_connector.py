# Device Connector : 28/02/2022

import requests
import json
import time
import datetime
import paho.mqtt.client as PahoMQTT

from sub.MyMQTT import *
from device_sensors.dht11 import *
from device_sensors.chirp import *
from device_sensors.actuator import *
from device_sensors.CO2sens import *

class Device_Connector(object):
    """
    Device connector class:
    -----------------------
        - get info from the catalog
        - 
    """
    exposed = True

    def __init__(self, conf_path, device_path):

        self.conf_file = conf_path
        self.device_file = device_path
        # Opening the configuration files
        with open(conf_path) as f:
            self.cat_info = json.load(f)

        # Opening the devices file
        with open(device_path) as f:
            self.mydevice = json.load(f)

        # Address of the catalog for adding the devices
        self.CatAddr = "http://" + self.cat_info["ip"] + ":" + self.cat_info["port"]
        
        # Read all the sensors in self.mydevice list
        # and initialize it all to start obtaining their values
        self.measures = []
        self.sensors_list = []
        self.sensor_index = {}
        count = 0

        # At the start the program check the sensor that are connected to the device connector
        for sensor in self.mydevice['resources']['sensors']:
            #FIXME: now read all the sensor, but we need to start the actuation only for the active sensor
            
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

            elif sensor['device_name'] == "CO2sens":
                self.sensor_index[str(sensor["sensID"])] = count
                count += 1

                co2_conf = sensor.copy()
                self.sensors_list.append(CO2sensor(co2_conf))
                
        
        # At the start the program does not know wich actuators have
        # Also for the actuators, each actuator will be appended as an object
        count = 0
        self.actuator_index = {}
        self.actuator_list = []
        for act in self.mydevice['resources']['actuators']:
            if act['device_name'] == "actuator":
                self.actuator_index[str(act["actID"])] = count
                count += 1

                actuator_conf = act.copy()
                self.actuator_list.append(actuator(actuator_conf))
        
        # Register to catalog
        self.registerToCat(tries=15)

        ########################################
        # MQTT client
        # Obtaining the broker information
        self.broker_dict = self.get_broker()
        
        self.client_mqtt = MyMQTT(
            clientID = self.cat_info["clientID"],
            broker = self.broker_dict["IP"],
            port = self.broker_dict["port"],
            notifier=self
            )
        
        # Start MQTT client
        self.client_mqtt.start()
        
        # Subscription to MQTT topics
        for end_det in self.mydevice["endpoints_details"]:
            if end_det.get("endpoint") == "MQTT":
                self._topic = end_det["topics"]
        
        for topic in self._topic:
            self.client_mqtt.mySubscribe(topic)


    def notify(self,topic,payload): 
        """
        notify
        ------
        Where we receive the topic which we are subscribed (plant control microservices)
        """

        message = json.loads(payload)
        if topic.split("/")[2].startswith("a"):
            #print(f"Command received:\n{message}\n from topic {topic}")
            # Iteration over all the actuator to find the one of the topic
            for actuator in self.mydevice["resources"]["actuators"]:
                # Check if the actuator have a topic where public the measure
                if "MQTT" in actuator["available_services"]:
                    services = actuator["services_details"][0]
                    if services["service_type"] == "MQTT":
                        # Obtain the topic list of this actuator
                        topic_list = services["topic"]

                        # If this is the correct actuator then
                        if topic in topic_list:
                            #TODO:->ALE: maybe with the communication the actuator is already on, so check if it is already on
                            # Start the actuation
                            if message['command'] == True:
                                self.actuator_list[self.actuator_index[actuator["actID"]]].start_actuation()
                                print(f"{message['sensID']} start")
                            # Stop the actuation
                            elif message['command'] == False:
                                self.actuator_list[self.actuator_index[actuator["actID"]]].start_actuation()
                                print(f"{message['sensID']} stop")
                    else:
                        raise Exception(f"Actuator {actuator['device_name']} {actuator['actID']} of greenhouse {self.mydevice['ghID']} have not an MQTT interface")
                else:
                    raise Exception(f"Actuator {actuator['device_name']} {actuator['actID']} of greenhouse {self.mydevice['ghID']} have not an MQTT interface")
    
    def registerToCat(self, tries = 10):
        """
        registerToCat
        -------------
        This function will register the device connector to the catalog.
        Each time the registration is done all the device of this device connector \n
        are sent to the catalog.
        """

        count = 0
        update = False
        while count < tries and not update:
            count += 1
            try:
                req_dev = requests.post(self.CatAddr + "/addDevice", data=json.dumps(self.mydevice))
                if req_dev.ok:
                    print(f"Device {self.mydevice['devID']} added successfully!")
                    update = True
                    self.saveJson()
                else:
                    print(f"Device {self.mydevice['devID']} could not be added!")
                    time.sleep(1)
            except:
                print(f"Fail to establish a connection with {self.cat_info['ip']}")
                time.sleep(1)

        if update == False:
            raise Exception(f"Fail to establish a connection with {self.cat_info['ip']}")
    
    def updateToCat(self, tries = 10):
        """
        updateToCat
        -----------
        Update all the decice of this device connector to the catalog, to let the catalog \n
        know that this device connector and its devices are still 'alive'.
        """
        
        count = 0
        update = False
        while count < tries and not update:
            count += 1
            try:
                #PUT the devices to the catalog
                req = requests.put(self.CatAddr + "/updateDevice", data=json.dumps(self.mydevice))
                if req.ok:
                    update = True
                    print(f"Device {self.mydevice['devID']} updated successfully!")
                else:
                    print(f"Device {self.mydevice['devID']} could not be updated!")
                    time.sleep(1)
            except:
                print(f"Fail to establish a connection with {self.cat_info['ip']}")
                time.sleep(1)

        if update == False:
            raise Exception(f"Fail to establish a connection with {self.cat_info['ip']}")


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
                b_dict = requests.get(self.CatAddr + "/broker").json()  
                update = True
            except:
                print(f"Fail to establish a connection with {self.cat_info['ip']}")
                time.sleep(1)

        if update == False:
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
            #print(f"Measuring with sensor {sens_id}")
            sens = {"sensID": sens_id,
                    "devID": self.mydevice['devID']}
            
            # Obtain the measure from the sensor
            curr_meas = self.sensors_list[self.sensor_index[sens_id]].measure()

            # Some sensor can measure more than one value (i.e. temperature and humidity)
            for i in range(len(curr_meas)):
                # At each measure is attached the origin, sensor_id and device_id
                curr_meas[i].update(sens)
            #print(f"Measure: {curr_meas}")

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

                        # Publish the measure to the respective topic
                        self.client_mqtt.myPublish(topic = topic_list[ind], msg = measure)
                    else:
                        raise Exception(f"Sensor {sensor['device_name']} {sensor['sensID']} of greenhouse {self.mydevice['ghID']} have not an MQTT interface")
            else:
                raise Exception(f"Sensor {sensor['device_name']} {sensor['sensID']} of greenhouse {self.mydevice['ghID']} have not an MQTT interface")

    def saveJson(self):
        """
        saveJson
        --------
        Used to save the catalog as a JSON file.
        """
        with open(self.device_file, 'w') as fw:
            json.dump(self.mydevice, fw, indent=4)
            return 0

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
        last_time = 0

        try:
            while True:
                print("looping\n")
                local_time = time.time()

                # Every refresh_time the measure are done and published to the topic
                if local_time - last_time > refresh_time: 
                    self.updateMeasures()
                    self.publishLastMeas()
                    self.updateToCat(tries=15)
                    # self.post_sensor_Cat()
                    last_time = time.time() 

                time.sleep(5)
        # To kill the program
        except KeyboardInterrupt: 
            print("Loop manually interrupted")


if __name__=='__main__':

    dc = Device_Connector(
        conf_path = "conf.json",
        device_path = "devices.json"
        )

    dc.loop(refresh_time=30)