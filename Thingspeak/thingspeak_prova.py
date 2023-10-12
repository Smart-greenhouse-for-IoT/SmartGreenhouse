import requests
import json
from datetime import datetime

channel_api = "6K2SF8DLAG4J7D3L"
api_endpoint = "https://api.thingspeak.com/update.json"

current_time = datetime.strftime(datetime.now(), "%Y/%m/%d - %H:%M")

# sostituire il json_prova con il notify del subscriber
json_prova = {
    "api_key": channel_api,
    "field1": "001",
    "field2": "26",
    "field3": "10",
    "field4": current_time,
    "field5": "basilico"
}

response = requests.post(api_endpoint, json_prova)
print(response)