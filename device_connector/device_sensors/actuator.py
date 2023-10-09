import json
import time
import random
import sys

class actuator:
    """
    Class which is used to control the actuator module.
    """
    def __init__(self, conf):
        """
        Parameters:
        - conf: configuration file as a json dictionary.
        """
        self.config = conf
        self.name = self.config["device_name"]
        self.pin = int(self.config["pin"])

        # At the start the actuators will always be set to off 
        self.state = 'off'



    def start_actuation(self):
        """
        start_actuation
        ---------------
        Start the actuation of the sensor selected.
        """

        if self.state == 'off':
            self.state = 'on'
            return 1
        else:
            return 0 
        
    def stop_actuation(self):
        """
        stop_actuation
        ---------------
        Stop the actuation of the sensor selected.
        """

        if self.state == 'on':
            self.state = 'off'
            return 1
        else:
            return 0 
    
# Program demo used for testing
if __name__ == "__main__":
    
    sample_conf = {
        "device_name": "actuator",
        "pin": 7
    }

    act = actuator(sample_conf)
    if act.start_actuation() == 1:
        print("Actuation start")
    else:
        print("Actuation start error")
    time.sleep(2)
    if act.stop_actuation() == 1:
        print("Actuation stop")
    else:
        print("Actuation stop error")
    