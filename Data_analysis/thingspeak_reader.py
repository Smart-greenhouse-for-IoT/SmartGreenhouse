import requests
import json
from sub.MyMQTT import *
import time
import pandas as pd
from io import StringIO


class ThingspeakReader(): 

    def __init__(self, conf_path):

            with open(conf_path) as f:
                self.conf_dict = json.load(f)
            
            self.df = pd.DataFrame()

    def readCSV(self):

            channel_id = self.conf_dict.get('channel_id')
            read_api_key = self.conf_dict.get('read_key')
            url = f"https://api.thingspeak.com/channels/{channel_id}/feeds.csv?api_key={read_api_key}"

            response = requests.get(url)

            if response.status_code == 200:
                csv_data = response.text
                self.df = pd.read_csv(StringIO(csv_data))
                self.df = self.df.rename(columns={
                    'field1': 'ghID',
                    'field2': 'devID',
                    'field3': 'sensID',
                    'field4': 'quantity',
                    'field5': 'value',
                    'field6': 'timestamp',
                    'field7': 'plant_type',
                    'field8': 'actuation_level'
                })
                print("Data successfully retrieved from Thingspeak!")
                return self.df  # Return the filled DataFrame
            else:
                print("Failed to retrieve data from ThingSpeak.")
                return None



if __name__ == "__main__":
    
    TS = ThingspeakReader("Thingspeak/conf.json")
    df = TS.readCSV()
