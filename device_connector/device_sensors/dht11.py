import json
import time
import random
import sys

class DHT11:
    """
    Class which will generate the temperature and humidity level of sensor DHT11
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
        The function return temperature and humidity generated values
        """

        # Generation of humidity and temperature values
        humidity = round(random.uniform(20, 80), 2)
        temperature = round(random.uniform(18, 38), 2)

        t_value = {
            "n": "Temperature",
            "u": "Cel",
            "t": 0,
            "v": 0
        }

        t_value["t"] = time.time()
        t_value["v"] = temperature

        h_value = {
            "n": "Humidity",
            "u": "%",
            "t": 0,
            "v": 0
        }

        h_value["t"] = time.time()
        h_value["v"] = humidity

        out = [t_value, h_value]

        return out
    
# Program demo used for testing
if __name__ == "__main__":
    
    sample_conf = {
        "device_name": "DHT11",
        "pin": 7
    }

    sensor = DHT11(sample_conf)
    print(f"Temperature measurment: {sensor.measure()[0]}")
    print(f"Humidity measurment: {sensor.measure()[1]}")