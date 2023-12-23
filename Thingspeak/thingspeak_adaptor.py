import requests
import json
from sub.MyMQTT import *
import time
import pandas as pd
import random

"""
retrieved_data = {
    'n': 'measured quantity',
    'u': 'unit',
    't': 'timestamp',
    'v': 'measured value',
    'devID': '',
    'sensID': ''
    'actID': ''
}
"""


class ThingspeakAdaptor:
    def __init__(self, conf_path, confTS_path):
        # Conf_dict contains catalog's information
        with open(conf_path) as f:
            self.conf_dict = json.load(f)

        # confTS contains information regarding the adaptor
        with open(confTS_path) as f:
            self.myTS = json.load(f)

        self.headers = {
            "Content-Type": "application/json",
            "X-THINGSPEAKAPIKEY": self.myTS["TS_info"]["write_key"],
        }

        self.format = {
            "write_api_key": self.myTS["TS_info"]["write_key"],  # conf_json
            "updates": [],
        }

        self.tot_dict = []
        self.url_TS = self.myTS["TS_info"]["url_TS"]
        self._topic = self.myTS["endpoints_details"][0]["topic"]

        self.addr_cat = "http://" + self.conf_dict["ip"] + ":" + self.conf_dict["port"]

        self.broker_dict = self.get_broker()

        clientID = f"{self.conf_dict['clientID']}{random.getrandbits(30)}"

        self._pubSub = MyMQTT(
            clientID=clientID,
            broker=self.broker_dict["IP"],
            port=self.broker_dict["port"],
            notifier=self,
        )

        self._pubSub.start()

        time.sleep(3)
        for topic in self._topic:
            self._pubSub.mySubscribe(topic)

        self.registerToCat()

    def get_broker(self, tries=10):
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
            raise Exception(
                f"Fail to establish a connection with {self.conf_dict['ip']}"
            )

        # Return a json dict with BrokerIP and BrokerPort
        return b_dict

    def registerToCat(self, tries=10):
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
                req_serv = requests.post(
                    self.addr_cat + "/addService", data=json.dumps(self.myTS)
                )
                if req_serv.ok:
                    print(f"Service {self.myTS['servID']} added successfully!")
                    update = True
                else:
                    print(f"Service {self.myTS['servID']} could not be added!")
                    time.sleep(3)
            except:
                print(f"Fail to establish a connection with {self.conf_dict['ip']}")

        if update == False:
            raise Exception(
                f"Fail to establish a connection with {self.conf_dict['ip']}"
            )

    def updateToCat(self, tries=10):
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
                # PUT the TS to the catalog services
                req = requests.put(
                    self.addr_cat + "/updateService", data=json.dumps(self.myTS)
                )
                if req.ok:
                    update = True
                    print(f"Service {self.myTS['servID']} updated successfully!")
                else:
                    print(f"Service {self.myTS['servID']} could not be updated!")
            except:
                print(f"Fail to establish a connection with {self.conf_dict['ip']}")
                time.sleep(1)

        if update == False:
            raise Exception(
                f"Fail to establish a connection with {self.conf_dict['ip']}"
            )

    def tot_dictAppend(self, partial_dict):
        self.tot_dict.append(partial_dict)

    def dictCreation(self, topic, msg):
        fields = {}
        ghID = self.retrieveGHID(msg.get("devID"))
        if ghID:
            fields["field1"] = ghID
            fields["field2"] = msg.get("devID")
            fields["field3"] = msg.get("sensID")
            fields["field4"] = msg.get("n")
            fields["field5"] = msg.get("v")
            fields["field6"] = msg.get("t")
            fields["delta_t"] = 1
            if topic.split("/")[3] == "moisture_level":
                fields["field7"] = self.retrievePlant_type(
                    msg.get("devID"), msg.get("sensID")
                )

            if topic.split("/")[2].startswith("a"):
                fields["field8"] = msg.get("command")

        return fields

    def sendDataToTS(self):
        """
        sendDataToTS
        ------------

        """

        try:
            # formatting
            if self.tot_dict:
                dict = self.format.copy()
                dict["updates"] = self.tot_dict

                response = requests.post(
                    self.url_TS, headers=self.headers, data=json.dumps(dict)
                )
                if response.ok:
                    print("Data sent to ThingSpeak successfully!")
                else:
                    print("Failed to send data to ThingSpeak.")
        except:
            print("ThingSpeak not reachable")

    def notify(self, topic, msg):
        """
        notify
        ------

        """
        print(f"Msg:received from topic: {topic}")
        msg_json = json.loads(msg)
        # print(msg_json)
        field_dict = self.dictCreation(topic, msg_json)
        if field_dict:
            self.tot_dictAppend(field_dict)

    def retrieveGHID(self, devID, tries=10):
        """
        retrieveGHID
        ------------

        """
        count = 0
        update = False
        ghID = None
        while count < tries and not update:
            count += 1
            try:
                req = requests.get(f"{self.addr_cat}/greenhouse?devID={devID}")
                update = True
                if req.status_code == 200:
                    if req.json():
                        ghID = req.json()["ghID"]
            except:
                print(f"Fail to establish a connection with catalog!")
                time.sleep(1)

        return ghID

    def retrievePlant_type(self, devID, sensID, tries=10):
        """
        retrievePlant_type
        ------------------

        """
        # if it is different from s1 and s2
        # (predefined sensor for the greenhouse and not for the plant)
        # then it is possible to retrive the plant name
        if sensID != "s1" and sensID != "s2":
            count = 0
            update = False
            while count < tries and not update:
                count += 1
                try:
                    plant_type = requests.get(
                        f"{self.addr_cat}/plant?devID={devID}&sensID={sensID}"
                    )
                    update = True
                except:
                    print(f"Fail to establish a connection with catalog!")
                    time.sleep(1)

            if update == False:
                raise Exception(f"Fail to establish a connection with catalog!")

            return plant_type.json()["plant"]

        else:
            return None

    def cleanDict(self):
        self.tot_dict = []

    def loop(self, refresh_time=30):
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
                    self.sendDataToTS()
                    self.cleanDict()

                    self.updateToCat(tries=15)
                    # self.post_sensor_Cat()
                    last_time = time.time()

        # To kill the program
        except KeyboardInterrupt:
            print("Loop manually interrupted")


if __name__ == "__main__":
    TS = ThingspeakAdaptor("conf.json", "confTS.json")
    TS.loop()
