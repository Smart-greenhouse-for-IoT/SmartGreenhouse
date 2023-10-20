import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
from thingspeak_reader import * 
import plotly.express as px
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import VarianceThreshold
from sklearn.model_selection import cross_val_score

import json

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

class DataAnalysis():
    def __init__(self, conf_DA_path):
        with open(conf_DA_path) as f:
            self.confDA = json.load(f)

        csv_data = self.confDA.get("path_dataset2")
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

if __name__=="__main__":
    DA = DataAnalysis("Data_analysis\conf_DA.json")

