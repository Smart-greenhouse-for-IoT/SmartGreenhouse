import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
from thingspeak_reader import * 
import cherrypy
import json


class DataAnalysis():
    def __init__(self):
        pass


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


    
    def BarPlot(self, x, y, title="title", xlabel="x_label", ylabel="y_label", legend="legend"):
        fig, ax = plt.subplots(dpi=100, figsize=(10, 20), tight_layout=True)
        
        colormap = plt.cm.get_cmap('viridis', len(x))
        bar_colors = colormap(np.arange(len(x)))

        ax.bar(x, y, color=bar_colors)

        ax.set_ylabel(ylabel) # y_axis name
        ax.set_xlabel(xlabel) # x_axis name
        ax.set_title(title)
        ax.legend(title=legend)

        plt.show()

    def ScatterPlot(self, df, x_column, y_column, color_column, size_column, title="title", xlabel="x_label", ylabel="y_label", legend="legend"):
         
        fig = px.scatter(df, x=x_column, y=y_column, color=color_column,
                         size=size_column, opacity=0.3, title=title)

        fig.update_xaxes(title_text=xlabel)
        fig.update_yaxes(title_text=ylabel)

        fig.update_layout(
            showlegend=True,
            legend=dict(orientation='h', title=legend),
            title=title,
        )

        fig.show()

    def BoxPlot(self, df):
        df.plot.box()
            

    def HistogramPlot(self):
        pass

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

    def __init__(self):
        self.TR = ThingspeakReader("Thingspeak\conf.json")
        self.queryClass = Queries()

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

                    return 

                elif params == {}:
                    raise cherrypy.HTTPError(400, f"Missing parameters!")
                else:
                    raise cherrypy.HTTPError(400, f"Not recognised parameters!")
                
        else:
            raise cherrypy.HTTPError(404, f"Error! Method not found!")     
                
                

if __name__ == "__main__": 
	
    # Standard configuration to serve the url "localhost:8080"
    conf={
    	'/':{
    		'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
    		'tools.sessions.on': True
    	}
    }
    webService = DataAnalysisMicroservice()
    cherrypy.tree.mount(webService,'/',conf)
    cherrypy.engine.start()



'''
if __name__ == "__main__":
    
    DA = DataAnalysis()
    DA.analysis()
    with plt.style.context("ggplot"):
        DA.BarPlot()
        '''

