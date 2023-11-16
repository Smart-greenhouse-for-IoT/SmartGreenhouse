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



class DataAnalysis():

    def __init__(self, conf_DA_path):

        '''
        df1: 17164 rows × 5 columns

            id: measurement id 
            T(°) : greenhouse temperature
            HR (%) : Relative greenhouse humidity
            CO2(Analog): greenhouse CO2
            timestamp: yyyy-dd-mm hh:mm

        -
        df2: 300 rows × 5 columns

            HS (Analog): soil humidity
            T(°) : greenhouse temperature
            HR (%) : Relative greenhouse humidity
            CO2(Analog): greenhouse CO2
            class: 
                1: soil without water - bagno tanto
                2: environment correct - non bagno
                3: too much hot - bagno medio
                4: very cold - bagno poco
        '''

        with open(conf_DA_path) as f:
            self.confDA = json.load(f)

        csv_data = self.confDA.get("path_dataset1")
        self.df2 = pd.read_csv(csv_data, sep=";", decimal='.')


    def dfAnalysis(self):
        
        self.df2.isna().any().any() # there are not NaN values
        self.df2 = self.df2.drop(columns=["L (Lux)"])
        self.df2 = self.df2.rename(columns={'clase':'class'})
        target = self.df2['class']
        features = self.df2.columns.drop('class')

        self.graphDFAnalysis()

        # Splitting the data into a training set and combined validation/test set
        train_df_, test_df = train_test_split(self.df2, test_size=0.2, random_state=1, shuffle=True)

        # Splitting the combined validation/test set into validation and test sets
        train_df, val_df  = train_test_split(train_df_, test_size=0.20, random_state=1, shuffle=True)

        # Printing the sizes of the resulting sets
        print("Training set size:", len(train_df)) # 192
        print("Validation set size:", len(val_df)) # 48
        print("Test set size:", len(test_df)) # 60

        classifier = RandomForestClassifier()
        pipe = Pipeline([
            ('standardization', StandardScaler()),
            ('featureS', VarianceThreshold()),
            ('ridge', classifier )
            ])
        pipe.fit(train_df[features], train_df['class'])
        val_predictions = pipe.predict(val_df[features])

        # train, val and test scores:
        train_score = pipe.score(train_df[features], train_df['class'])
        print("Training set score:", train_score)

        val_score = pipe.score(val_df[features], val_df['class'])
        print("Validation set score:", val_score)

        test_score = pipe.score(test_df[features], test_df['class'])
        print("Test set score:", test_score)

        # cross validation:
        combined_data = pd.concat([train_df, val_df])
        cross_val_scores = cross_val_score(pipe, combined_data[features], combined_data['class'], cv=5)
        print("Cross-Validation Scores:", cross_val_scores)
        mean_cv_score = cross_val_scores.mean()
        print("Mean Cross-Validation Score:", mean_cv_score)

        # aggiungere accuracy, capire come si vuole restituire il valore


    def graphDFAnalysis(self):
    
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

    #/////////////////////////////////////////////////////////
    #/////////////////////////////////////////////////////////

    #TODO add some time reference and allow the choice of the time interval

    # Energy consumption analysis for the actuator
    def EnergyConsumptionACT(self, df, ghid, devid, actid):
        consumption_time = 0
        start, stop = 0
        df_filtered = df[(df['ghID'] == ghid) & (df['devID'] == devid) & (df['actID'] == actid)]
        df_filtered.orderby(by='timestamp')

        for index, row in df_filtered.iterrows():
            if (row['v'] == 1):
                start = df_filtered['timestamp']
            elif ((row['v'] == 0) & (start != 0)):
                stop = df_filtered['timestamp']
                consumption_time += stop - start
            else:
                print('Error! Actuation is not working!')
            
        return consumption_time
    
    # Energy consumption for the device
    def EnergyConsumptionDEV(self, df, ghid, devid):
        consumption_time_dev = 0
        df_filtered = df[(df['ghID'] == ghid) & (df['devID'] == devid)]

        for index, row in df_filtered.iterrows():
            consumption_time_dev += self.EnergyConsumptionACT(df, ghid, devid, row['actID'])

        return consumption_time_dev
            
    # Energy consumption for the greenhouse
    def EnergyConsumptionGH(self, df, ghid):
        consumption_time_gh = 0
        df_filtered = df[(df['ghID'] == ghid)]
        
        for index, row in df_filtered.iterrows():
            consumption_time_gh += self.EnergyConsumptionDEV(df, ghid, row['devID'])

        return consumption_time_gh
    
    #/////////////////////////////////////////////////////////
    #/////////////////////////////////////////////////////////
    # La prossima funzione al momento non ha senso
    
    def analysis(self, df):
        # Checking the shape of the DataFrame
        print(f"The shape of the dataframe is: {df.shape}")
        # Checking the number of missing values in each column
        print(f"The number of missing values is: {df.isnull().sum()}")
        # Handling missing data 
        # df = df.dropna(inplace=True) # drop missing values
        df = df.fillna(df.mean(), inplace=True) # fill the missing values with the mean

        # datetime handling
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        '''
        graph with data from a certain year or month or day
        '''
        df['year'] = df['timestamp'].dt.year # create year column
        df['month'] = df['timestamp'].dt.month # create month column
        df['day'] = df['timestamp'].dt.day # create day column
        # aggiungere orario
    

class Queries():
# returnare il timestamp in formato decente
    def __init__(self):
        pass

    # Get the last specific value for temperature/humidity/CO2 for a gh
    def get_last_value(self, df, gh_id, measure):
        selected_rows = df[df['ghID'] == gh_id]
        filtered_rows = selected_rows[selected_rows['quantity'] == measure]
        sorted_rows = filtered_rows.sort_values(by='timestamp', ascending= True)
        last_row = sorted_rows.tail(1)

        return last_row
    
    # Get the last specific value for moisture level for a gh, given a sensor
    def get_last_moisture_level(self, df, gh_id, sens_id):
        selected_rows = df[(df['ghID'] == gh_id) & (df['sensID'] == sens_id)]
        filtered_rows = selected_rows[selected_rows['quantity'] == "moisture_level"]
        sorted_rows = filtered_rows.sort_values(by='timestamp', ascending=True)
        last_row = sorted_rows.tail(1)
        moisture_level = last_row['value']

        return moisture_level
    
         

class DataAnalysisMicroservice():
    
    exposed = True

    def __init__(self, conf_path, conf_DA_path):

        with open(conf_path) as f:
            self.conf = json.load(f)

        with open(conf_DA_path) as f:
            self.confDA = json.load(f)

        self.DA = DataAnalysis("Data_analysis\conf_DA.json")

        self.TR = ThingspeakReader("Data_analysis\conf.json")
        self.df = self.TR.readCSV()

        self.queryClass = Queries()

        # Address of the catalog for adding the devices
        self.CatAddr = "http://" + self.conf["ip"] + ":" + self.conf["port"]

        # Register to catalog
        self.registerToCat()

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
        except:
            print(f"Fail to establish a connection with {self.conf['ip']}")
            time.sleep(1)

        if update == False:
            raise Exception(f"Fail to establish a connection with {self.conf['ip']}")  
        
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
                        return json.dumps(value_row.to_dict())
                    else:
                        raise cherrypy.HTTPError(404, f"Measure not found!")
                elif params == {}:
                    raise cherrypy.HTTPError(400, f"Missing parameters!")
                else:
                    raise cherrypy.HTTPError(400, f"Not recognised parameters!")
                
            # Get the last specific value for moisture level for a gh, given a sensor
            elif uri[0] == "getLastMoistureLevel":
                if params.get("ghID"):
                    ghID = params.get("ghID")
                    if params.get("sensID"):
                        sensID = params.get("sensID")
                        value_row = self.queryClass.get_last_moisture_level(self.df, ghID, sensID)
                        return json.dumps(value_row.to_dict())
                    else:
                        raise cherrypy.HTTPError(404, f"Sensor not found!")
                elif params == {}:
                    raise cherrypy.HTTPError(400, f"Missing parameters!")
                else:
                    raise cherrypy.HTTPError(400, f"Not recognised parameters!")
                
            # Get the last retrieved data for temperature, humidity and CO2
            elif uri[0] == "getAllLastValues":
                if params.get("ghID"):
                    ghID = params.get("ghID")
                    last_temperature_row = self.queryClass.get_last_value(self.df, ghID, "temperature")
                    last_humidity_row = self.queryClass.get_last_value(self.df, ghID, "humidity")
                    last_CO2_row = self.queryClass.get_last_value(self.df, ghID, "CO2")

                    return (last_temperature_row, last_humidity_row, last_CO2_row)

                elif params == {}:
                    raise cherrypy.HTTPError(400, f"Missing parameters!")
                else:
                    raise cherrypy.HTTPError(400, f"Not recognised parameters!")
                
            #///////////////////////////////////////////////////////////////////////////
            #///////////////////////////////////////////////////////////////////////////
            # Energy consumption functions

            # Get the consumption time for the entire gh
            elif uri[0] == "EnergyConsumptionGH":
                if params.get("ghid"):
                    ghid = params.get("ghid")
                    consumption_time_gh = self.DA.EnergyConsumptionGH(self.df, ghid)
                    return consumption_time_gh
                elif params == {}:
                    raise cherrypy.HTTPError(400, f"Missing parameters!")
                else:
                    raise cherrypy.HTTPError(400, f"Not recognised parameters!")

            # Get the consumption time for a single device
            elif uri[0] == "EnergyConsumptionDEV":
                if params.get("ghid"):
                    ghID = params.get("ghid")
                    if params.get("devid"):
                        devid = params.get("devid")
                        consumption_time_dev = self.DA.EnergyConsumptionDEV(self.df, ghid, devid)
                        return consumption_time_dev
                    else:
                        raise cherrypy.HTTPError(404, f"Device not found!")
                elif params == {}:
                    raise cherrypy.HTTPError(400, f"Missing parameters!")
                else:
                    raise cherrypy.HTTPError(400, f"Not recognised parameters!")
                
            # Get the consumption time for a single actuator
            elif uri[0] == "EnergyConsumptionACT":
                if params.get("ghid"):
                    ghID = params.get("ghid")
                    if params.get("devid"):
                        devid = params.get("devid")
                        if params.get("actid"):
                            actid = params.get("actid")
                            consumption_time_dev = self.DA.EnergyConsumptionACT(self.df, ghid, devid, actid)
                            return consumption_time_dev
                        else:
                            raise cherrypy.HTTPError(404, f"Actuator not found")
                    else:
                        raise cherrypy.HTTPError(404, f"Device not found!")
                elif params == {}:
                    raise cherrypy.HTTPError(400, f"Missing parameters!")
                else:
                    raise cherrypy.HTTPError(400, f"Not recognised parameters!")
                
            #///////////////////////////////////////////////////////////////////////////
            #///////////////////////////////////////////////////////////////////////////
            # Functions needed by node-red

            # Get the list of ghids
            elif uri[0] == "getGHIDlist":
                ghID_list = self.getGHIDlist()
                print(ghID_list)
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
                            return json.dumps(resultForChart)
                        else:
                            raise cherrypy.HTTPError(400, f"Timestamp parameter not found")
                    else:
                        raise cherrypy.HTTPError(400, f"Measure parameter not found!")
                        
                elif params == {}:
                    raise cherrypy.HTTPError(400, f"Missing parameters!")
                else:
                    raise cherrypy.HTTPError(400, f"Not recognised parameters!")
        else:
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
            except:
                print(f"Fail to establish a connection with {self.conf['ip']}")
                time.sleep(1)

        if update == False:
            raise Exception(f"Fail to establish a connection with {self.conf['ip']}")

    

if __name__ == "__main__": 
	
    webService = DataAnalysisMicroservice("Data_analysis\conf.json", "Data_analysis\conf_DA.json")
    cherryConf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True
        }
    }
    cherrypy.config.update({'server.socket_host': '0.0.0.0', 'server.socket_port': webService.confDA["endpoints_details"][0]["port"]})
    cherrypy.tree.mount(webService, '/', cherryConf)
    cherrypy.engine.start()

    webService.loop(refresh_time=50)
'''
if __name__ == "__main__":
    
    DA = DataAnalysis()
    DA.analysis()
    with plt.style.context("ggplot"):
        DA.BarPlot()
        '''

