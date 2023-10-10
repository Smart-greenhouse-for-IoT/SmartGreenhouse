import json
import time
import random
import sys

class CO2sensor:
    """
    Class which will generate the co2 level in the greenhouse
    """
    def __init__(self, conf):
        """

        """
        self.config = conf
        self.name = self.config["device_name"]
        self.pin = int(self.config["pin"])


    def measure(self):
        """
        Measure
        -------
        The function return temperature and humidity generated values
        """

        # Generation co2 levels in ppm(part per million)
        co2 = round(random.uniform(120, 480), 2)

        co2_value = {
            "n": "CO2",
            "u": "ppm",
            "t": 0,
            "v": 0
        }

        co2_value["t"] = time.time()
        co2_value["v"] = co2

        out = [co2_value]

        return out
    
# Program demo used for testing
if __name__ == "__main__":
    
    sample_conf = {
        "device_name": "CO2sensor",
        "pin": 7
    }

    sensor = CO2sensor(sample_conf)
    print(f"CO2 measurment of sensor {sensor.name} is: {sensor.measure()[0]}")