import json
import time
import random
import sys

class chirp:
    """
    Class which will generate the moisture level of chirp sensor 
    """
    def __init__(self, conf):
        """

        """
        self.config = conf
        self._name = self.config["device_name"]
        self._pin = int(self.config["pin"])


    def measure(self):
        """
        Measure
        -------
        The function return the moisture generated values
        """

        # Generation of moisture humidity  values
        humidity = round(random.uniform(1, 99), 2)

        h_value = {
            "n": "Soil moisture",
            "u": "%",
            "t": 0,
            "v": 0
        }

        h_value["t"] = time.time()
        h_value["v"] = humidity

        out = [h_value]

        return out
    
# Program demo used for testing
if __name__ == "__main__":
    
    sample_conf = {
        "device_name": "DHT11",
        "pin": 7
    }

    sensor = chirp(sample_conf)
    print(f"Moisture measurment: {sensor.measure()}")