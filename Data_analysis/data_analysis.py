from datetime import datetime
import numpy as np
from thingspeak_reader import * 
import cherrypy
import json
import pandas as pd
import plotly.express as px
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import VarianceThreshold
from sklearn.model_selection import cross_val_score


class DataAnalysisMicroservice:
    
    exposed = True

    def __init__(self, conf_path, conf_DA_path):

        with open(conf_path) as f:
            self.conf = json.load(f)

        with open(conf_DA_path) as ff:
            self.confDA = json.load(ff)

        self.TR = ThingspeakReader(conf_path)
        self.df = self.TR.readCSV()

        

        self.queryClass = Queries()

        # Address of the catalog for adding the devices
        self.CatAddr = "http://" + self.conf["ip"] + ":" + self.conf["port"]

        # Register to catalog
        self.registerToCat()

        '''
        df1: 17164 rows × 5 columns

            id: measurement id 
            T(°) : greenhouse temperature
            HR (%) : Relative greenhouse humidity
            CO2(Analog): greenhouse CO2
            timestamp: yyyy-dd-mm hh:mm

        -
        df2: 300 rows × 5 columns - roses dataset

            HS (Analog): soil humidity
            T(°) : greenhouse temperature
            HR (%) : Relative greenhouse humidity
            CO2(Analog): greenhouse CO2
            class: 
                0: environment correct- No water needed
                1: small water required - low level actuation
                2: too much hot - medium level
                3: soil without water  - high level
        '''

        csv_data = self.confDA.get("path_dataset2")
        self.df2 = pd.read_csv(csv_data, sep=",", decimal='.')

        self.pipe = self.RandomForest()

    def registerToCat(self, tries = 10):
        """
        registerToCat
        -------------
        This function will register the microservice to the catalog.
        """

        count = 0
        update = False
        while count < tries and not update:
            count += 1
            try:
                req_dev = requests.post(self.CatAddr + "/addService", data=json.dumps(self.confDA))
                if req_dev.ok:
                    print(f"Service {self.confDA['servID']} added successfully!")
                    update = True
                else:
                    print(f"Service {self.confDA['servID']} could not be added!")
                    time.sleep(1)
            except:
                print(f"Fail to establish a connection with {self.conf['ip']}")
                time.sleep(1)

        if update == False:
            raise Exception(f"Fail to establish a connection with {self.conf['ip']}")  
        

    def RandomForest(self):
        '''
        - performs some machine learning (Random Forest Classifier) on the roses dataset
        '''

        # self.df2.isna().any().any() # there are not NaN values
        self.df2 = self.df2.drop(columns=["L (Lux)"])
        self.df2 = self.df2.rename(columns={'clase':'class'})
        target = self.df2['class']
        self.features = self.df2.columns.drop('class')
        train = self.df2[self.features]

        # self.graphDFAnalysis()
        '''
        # Splitting the data into a training set and combined validation/test set
        train_df_, test_df = train_test_split(self.df2, test_size=0.2, random_state=1, shuffle=True)

        # Splitting the combined validation/test set into validation and test sets
        train_df, val_df  = train_test_split(train_df_, test_size=0.20, random_state=1, shuffle=True)

        # Printing the sizes of the resulting sets
        print("Training set size:", len(train_df)) # 192
        print("Validation set size:", len(val_df)) # 48
        print("Test set size:", len(test_df)) # 60
        '''
        classifier = RandomForestClassifier()
        pipe = Pipeline([
            ('standardization', StandardScaler()),
            ('featureS', VarianceThreshold()),
            ('ridge', classifier )
            ])
        
        '''
        pipe.fit(train_df[features], train_df['class'])
        val_predictions = pipe.predict(val_df[features])

        # train, val and test scores:
        train_score = pipe.score(train_df[features], train_df['class'])
        print("Training set score:", train_score)

        val_score = pipe.score(val_df[features], val_df['class'])
        print("Validation set score:", val_score)

        test_score = pipe.score(test_df[features], test_df['class'])
        print("Test set score:", test_score)
        '''
        pipe.fit(train, target)
        return pipe
        
        
    def dftransform(self, ghid, moisture):
        '''
        predict the label when getting the moisture level
        '''
        last_rows = self.queryClass.get_all_last_values(self.df, ghid) # temperature, humidity, CO2
        
        new_point = [float(moisture), last_rows[0].get('value').values[0], last_rows[2].get('value').values[0], last_rows[1].get('value').values[0]] # temperature, CO2, Humidity

        new_point_df = pd.DataFrame([new_point], columns=self.features)
        predicted_class = int(self.pipe.predict(new_point_df)[0])
        return predicted_class
        


    def graphDFAnalysis(self):
        '''
        used to analyse the RosesGreenhDB before performing ML
        '''
    
        figHS = px.scatter(self.df2, x='HS (Analog)', y='class', color='class', title='Data Clustering by Class')
        figHS.show()

        figT = px.scatter(self.df2, x='T (°)', y='class', color='class', title='Data Clustering by Class')
        figT.show()

        figCO2 = px.scatter(self.df2, x='CO2 (Analog)', y='class', color='class', title='Data Clustering by Class')
        figCO2.show()

        figHR = px.scatter(self.df2, x='HR (%)', y='class', color='class', title='Data Clustering by Class')
        figHR.show()

        fig2 = px.scatter(self.df2, x='HS (Analog)', y='T (°)', color='class', title='Data Clustering by Class')
        fig2.show()

        fig3 = px.scatter(self.df2, x='HS (Analog)', y='HR (%)', color='class', title='Data Clustering by Class')
        fig3.show()

        fig4 = px.scatter(self.df2, x='HS (Analog)', y='CO2 (Analog)', color='class', title='Data Clustering by Class')
        fig4.show()

    #//////////////////////////////////////////////////////////////////////////////////////////////////
    #////////////////////////////////////////////////////////////////////////////////////////////////////

    def getGHIDlist(self):
        '''
        Function used to retrieve the ghid list, used for dropdown menu in nodered dashboard
        '''
        ghid_list = []
        response = requests.get(f'{self.CatAddr}/greenhouse')
        if response.status_code == 200:
            print("Greenhouses' list obtained successfully!")
        
            data = response.json()
            for gh in data:
                ghid_list.append(gh.get("ghID"))
            # print(ghid_list)
        else:
            print('Failed to get the list of greenhouses.')
        
        return json.dumps(ghid_list)
    
    # Function used to retrieve data using node-red
    def prepareDataForChart(self, ghid, n, t):
        '''
        Function used to filter data and create the line chart in node red dashboard
        Data is processed so that the format is correct as input for the chart
        '''
        
        last_t_df = pd.DataFrame()
        df_filtered = self.df[(self.df['ghID'] == ghid) & (self.df['quantity'] == n)] # df for the selected ghid and quantity
        
        current_date = pd.to_datetime('today').date()
        current_date_sec = (current_date - pd.Timestamp("1970-01-01").date()).total_seconds()

        timestamp = 1698238111.85808

        date_time = datetime.fromtimestamp(timestamp)

        if t == 'day':
            last_day = (current_date - pd.DateOffset(days=1)).to_pydatetime().timestamp()
            last_t_df = df_filtered[df_filtered['timestamp'] >= last_day]
            
        elif t == 'week':
            last_week = (current_date - pd.DateOffset(weeks=1)).to_pydatetime().timestamp()
            last_t_df = df_filtered[(df_filtered['timestamp'] >= last_week) & (df_filtered['timestamp'] < current_date_sec)]
        
        elif t == 'month':
            last_month = (current_date - pd.DateOffset(months=1)).to_pydatetime().timestamp()
            last_t_df = df_filtered[(df_filtered['timestamp'] >= last_month) & (df_filtered['timestamp'] < current_date_sec)]
        
        else:
            print('Error in getting the input date')

        result = [{
            "series": ["A"],
            "data": [[{"x": row['timestamp']*1000, "y": row['value']} for _, row in last_t_df.iterrows()]],
            "labels": [""]
        }]
        return result

    def powerConsumptionChart(self, ghid, action, t):

        # Filter DataFrame based on greenhouse ID
        df_first_filter = self.df[(self.df['ghID'] == ghid)]

        # Filter DataFrame based on the specified time period
        end_time = pd.Timestamp.now()
        if t == 'day':
            start_time = end_time - pd.DateOffset(days=1)
        elif t == 'week':
            start_time = end_time - pd.DateOffset(weeks=1)
        elif t == 'month':
            start_time = end_time - pd.DateOffset(months=1)
        else:
            raise ValueError("Invalid time period. Supported values are 'day', 'week', or 'month'")

        df_filtered = df_first_filter[(df_first_filter['timestamp'] >= int(start_time.timestamp())) & (df_first_filter['timestamp'] <= int(end_time.timestamp()))]

        # Sort DataFrame by timestamp
        df_filtered = df_filtered.sort_values(by='timestamp')

        # Calculate power consumption
        power_consumption = []
        result = []

        
        series_count = 0
        data_tot = []

        series = []
        devices = df_filtered['devID'].unique()
        # Calculate power consumption for each actuator and return in a list
        for device in devices:
            data = []
            labels = []
            device_df = df_filtered[df_filtered['devID'] == device]
            actuators = device_df['sensID'].unique()
            for actuator in actuators:
                if "a" in actuator:
                    actuator_df = device_df[device_df['sensID'] == actuator]

                    consumption_time = 0
                    start = None

                    for index, row in actuator_df.iterrows():
                        if row['actuation_level'] == 1:
                            start = row['timestamp']
                        elif row['actuation_level'] == 0 and start is not None:
                            stop = row['timestamp']
                            consumption_time += (stop - start)
                            start = None

                    
                    data.append(round(consumption_time/60, 2))
                    labels.append(f"Power consumption for {actuator} (in minutes)")
                
            data_tot.append(data)
            series.append(series_count)
            series_count += 1
        if action == "Actuator":
            result.append({"series": series, "data": data_tot, "labels": labels})
        elif action == "Device":
            data_dev = []
            labels_dev = []
            for i,dev in enumerate(data_tot):
                data_dev.append([round(sum(dev),2)])
                labels_dev.append(f"Power consumption for {devices[i]} (in minutes)")
            result.append({"series": [1], "data": data_dev, "labels": labels_dev})
        elif action == "Greenhouse":
            data_gh = 0
            label_gh = [f"Power consumption for {ghid} (in minutes)"]
            for dev in data_tot:
                data_gh += round(sum(dev),2)
            result.append({"series": [1], "data": [[data_gh]], "labels": label_gh})
        else:
            raise ValueError("Invalid Action.")
        return result



        #///////////////////////////////////////////////////////////////////////////
        #///////////////////////////////////////////////////////////////////////////
        # GET function

    def GET(self, *uri, **params):
        
        self.df = self.TR.readCSV() # Devo analizzare questo df?

        if len(uri) > 0:

            # Get the last specific value for temperature/humidity/CO2 for a gh
            if uri[0] == "getLastValue":
                if params.get("ghID"):
                    ghID = params.get("ghID")
                    if params.get("n"):
                        measure = params.get("n")
                        # use the method from the query class
                        value_row = self.queryClass.get_last_value(self.df, ghID, measure)
                        print(f"{measure} level retrieved successfully.")
                        return json.dumps(value_row.to_dict())
                    else:
                        print("Not recognised parameter.")
                        raise cherrypy.HTTPError(404, f"Measure not found!")
                elif params == {}:
                    print("Missing parameters.")
                    raise cherrypy.HTTPError(400, f"Missing parameters!")
                else:
                    print("Not recognised parameters.")
                    raise cherrypy.HTTPError(400, f"Not recognised parameters!")
                
            # Get the last specific value for moisture level for a gh, given a sensor
            elif uri[0] == "getLastMoistureLevel":
                if params.get("ghID"):
                    ghID = params.get("ghID")
                    if params.get("sensID"):
                        sensID = params.get("sensID")
                        value_row = self.queryClass.get_last_moisture_level(self.df, ghID, sensID)
                        print("Moisture level retrieved successfully.")
                        return json.dumps({"moisture":value_row})
                    else:
                        raise cherrypy.HTTPError(404, f"Sensor not found!")
                elif params == {}:
                    print("Cannot retrieve moisture level.")
                    raise cherrypy.HTTPError(400, f"Missing parameters!")
                else:
                    print("Cannot retrieve moisture level.")
                    raise cherrypy.HTTPError(400, f"Not recognised parameters!")
                
            # Get the last retrieved data for temperature, humidity and CO2
            elif uri[0] == "getAllLastValues":
                if params.get("ghID"):
                    ghID = params.get("ghID")
                    last_rows = self.queryClass.get_all_last_values(self.df, ghID)
                    last_temperature_row = last_rows[0]
                    last_humidity_row = last_rows[1]
                    last_CO2_row = last_rows[2]
                    print("Temperature, humidity and CO2 retrieved successfully.")
                    return json.dumps({"temperature":last_temperature_row['value'].iloc[0],
                                       "humidity":last_humidity_row['value'].iloc[0],
                                       "CO2":last_CO2_row['value'].iloc[0]})

                elif params == {}:
                    print("Cannot retrieve data for temperature, humidity and CO2.")
                    raise cherrypy.HTTPError(400, f"Missing parameters!")
                else:
                    print("Cannot retrieve data for temperature, humidity and CO2.")
                    raise cherrypy.HTTPError(400, f"Not recognised parameters!")
                
            #////////////////////////////////////////////////////////////////////////////////////
            #////////////////////////////////////////////////////////////////////////////////////
            # Get the water label

            elif uri[0] == "getWaterCoefficient":
                if params.get("ghid"):
                    ghID = params.get("ghid")
                    if params.get("moisture_level"):
                        moisture = params.get("moisture_level")
                        label = self.dftransform(ghID, moisture)
                        print(f"The predicted coefficient is {label}.")
                        return json.dumps({"coefficient":label})
                    else:
                        raise cherrypy.HTTPError(404, f"Moisture level not found!")
                elif params == {}:
                    print("Cannot predict water coefficient.")
                    raise cherrypy.HTTPError(400, f"Missing parameters!")
                else:
                    print("Cannot predict water coefficient.")
                    raise cherrypy.HTTPError(400, f"Not recognised parameters!")
                
            #///////////////////////////////////////////////////////////////////////////
            #///////////////////////////////////////////////////////////////////////////
            # Functions needed by node-red

           # Get the list of ghids
            elif uri[0] == "getGHIDlist":
                ghID_list = self.getGHIDlist()
                print(f"ghID list: {ghID_list}")
                return ghID_list
            
            # Get the data to be used for the chart
            elif uri[0] == "getDataChart":
                if params.get("ghID"):
                    ghid = params.get("ghID")
                    if params.get("n"):
                        n = params.get("n")
                        if params.get("t"):
                            t = params.get("t")
                            resultForChart = self.prepareDataForChart(ghid, n, t)
                            print("Data sent to NodeRed.")
                            return json.dumps(resultForChart)
                        else:
                            print("Impossible to send data to Nodered.")
                            raise cherrypy.HTTPError(400, f"Timestamp parameter not found")
                    else:
                        print("Impossible to send data to Nodered.")
                        raise cherrypy.HTTPError(400, f"Measure parameter not found!")
                        
                elif params == {}:
                    print("Impossible to send data to Nodered.")
                    raise cherrypy.HTTPError(400, f"Missing parameters!")
                else:
                    print("Impossible to send data to Nodered.")
                    raise cherrypy.HTTPError(400, f"Not recognised parameters!")
                

            elif uri[0] == "getDataPowerConsumption":
                if params.get("ghID"):
                    ghid = params.get("ghID")
                    if params.get("action"):
                        action = params.get("action")
                        if params.get("t"):
                            t = params.get("t")
                            resultForGauge = self.powerConsumptionChart(ghid, action, t)
                            print("Data sent to NodeRed.")
                            return json.dumps(resultForGauge)
                        else:
                            print("Impossible to send data to Nodered.")
                            raise cherrypy.HTTPError(400, f"Time parameter not found!")
                    else:
                        print("Impossible to send data to Nodered.")
                        raise cherrypy.HTTPError(400, f"Measure parameter not found!")
                        
                elif params == {}:
                    print("Impossible to send data to Nodered.")
                    raise cherrypy.HTTPError(400, f"Missing parameters!")
                else:
                    print("Impossible to send data to Nodered.")
                    raise cherrypy.HTTPError(400, f"Not recognised parameters!")
        else:
            print("Error! Method not found.")
            raise cherrypy.HTTPError(404, f"Error! Method not found!")     



    def loop(self, refresh_time = 10):
        """
        Loop
        ----
        loop to mantain updated the services in the catalog
        """
        last_time = 0

        try:
            while True:
                print("looping\n")
                local_time = time.time()
                # Every refresh_time the measure are done and published to the topic
                if local_time - last_time > refresh_time: 
                    self.updateToCat()
                    # self.post_sensor_Cat()
                    last_time = time.time() 

                time.sleep(5)
        except KeyboardInterrupt:
            cherrypy.engine.block()
            print("Loop manually interrupted")

    def updateToCat(self, tries = 10):
        """
        updateToCat
        -----------
        Update the microservice, to let the catalog know that this microservic is still operative.
        """

        count = 0
        update = False
        while count < tries and not update:
            count += 1
            try:
                req_dev = requests.put(self.CatAddr + "/updateService", data=json.dumps(self.confDA))
                if req_dev.ok:
                    print(f"Service {self.confDA['servID']} updated successfully!")
                    update = True
                else:
                    print(f"Service {self.confDA['servID']} could not be updated!")
                    time.sleep(1)
            except:
                print(f"Fail to establish a connection with {self.conf['ip']}")
                time.sleep(1)

        if update == False:
            raise Exception(f"Fail to establish a connection with {self.conf['ip']}")

    

class Queries():
# returnare il timestamp in formato decente
    def __init__(self):
        pass

    # Get the last specific value for temperature/humidity/CO2 for a gh
    def get_last_value(self, df, gh_id, measure):
        selected_rows = df[df['ghID'] == gh_id]
        filtered_rows = selected_rows[selected_rows['quantity'] == measure]
        sorted_rows = filtered_rows.sort_values(by='timestamp', ascending=False)
        last_row = sorted_rows.tail(1)

        return last_row
    
    # Get all the last values for a gh
    def get_all_last_values(self, df, gh_id):
        last_temperature_row = self.get_last_value(df, gh_id, "Temperature")
        last_humidity_row = self.get_last_value(df, gh_id, "Humidity")
        last_CO2_row = self.get_last_value(df, gh_id, "CO2")

        return [last_temperature_row, last_humidity_row, last_CO2_row]

    # Get the last specific value for moisture level for a gh, given a sensor
    def get_last_moisture_level(self, df, gh_id, sens_id):
        selected_rows = df[(df['ghID'] == gh_id) & (df['sensID'] == sens_id)]
        filtered_rows = selected_rows[selected_rows['quantity'] == "Soil moisture"]
        sorted_rows = filtered_rows.sort_values(by='timestamp', ascending=False)
        last_row = sorted_rows.tail(1)
        moisture_level = last_row['value'].iloc[0]

        return moisture_level
    
         


if __name__ == "__main__": 
	
    webService = DataAnalysisMicroservice("conf.json", "conf_DA.json")
    cherryConf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True
        }
    }
    cherrypy.config.update({'server.socket_host': webService.confDA["endpoints_details"][0]["ip"], 'server.socket_port': webService.confDA["endpoints_details"][0]["port"]})
    cherrypy.tree.mount(webService, '/', cherryConf)
    cherrypy.engine.start()

    webService.loop(refresh_time=30)

