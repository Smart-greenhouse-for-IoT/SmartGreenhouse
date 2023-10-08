import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
from thingspeak_reader import * 


class DataAnalysis():
    def __init__(self):
        TR = ThingspeakReader("Thingspeak\conf.json")
        self.df = TR.readCSV()


    def analysis(self):
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



if __name__ == "__main__":
    
    DA = DataAnalysis()
    DA.analysis()
    with plt.style.context("ggplot"):
        DA.BarPlot()

