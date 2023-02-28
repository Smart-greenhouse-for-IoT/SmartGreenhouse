# Device Connector : 28/02/2022

import cherrypy
import requests
import json
import sys

class Data(object):
    # Get data from catalog 

    def __init__(self):
        self.conf = json.load(open("setting.json"))
        return

    def get_broker(self): #GET all the broker information
        string = "http://" + self.conf["CatIP"] + ":" + self.conf["CatPort"] + "/qualcosa" #URL for GET
        data = json.loads(requests.get(string).text)  #GET for catalog
        b_dict = 
        return b_dict
    
if __name__=='__main__':
    pass