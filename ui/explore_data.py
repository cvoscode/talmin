import dash 
import polars as pl 
import plotly.graph_objects as go 
import dash_bootstrap_components as dbc
import sys
sys.path.insert(0, r'talmin')
from utils.Base_Components import *
from dash import dcc,html,Input, Output, State,ctx
from plotting.Box import BoxPlotter
from plotting.ParallelCoordinates import PCPlotter
from plotting.Correlations import *
from plotting.ECDF import ECDFPlotter
from plotting.Histogram import HistogramPlotter
from plotting.ScatterPlot import ScatterPlotter
from plotting.Statistics import *
from plotting.Violine import ViolinePlotter




class DataExplorer(dash.Dash):
    def __init__(self, id):
        self.data=pl.DataFrame()
        self.id=id
        self.plot_types=['Boxplot','Histogram','Violinplot','ECDF Plot','Scatterplot','Parallel Coordinates']

    def set_data(self,data):
        """set data

        Args:
            data (pl.DataFrame): data for the class
        """
        self.data=data
    def get_data(self) -> pl.DataFrame:
        """get data

        Args:
            data (pl.DataFrame): data of the class

        Returns:
            data: pl.DataFrame
        """
        return self.data 
    def get_ui(self):
        return [dbc.Row(children=[create_dropdown_paging(id=f'plot-type-{self.id}',options=self.plot_types,value='Violinplot',name='Select Plot Type',multi=False),
                                          ]),
                dbc.Col(id=f'plot-space-{self.id}',width=12)]
    
    def create_base_callbacks(self,app,PCPlot,BoxPlot,ECDFPlot,HistPlot,SCPlot,VioPlot):
        @app.callback(Output(f'plot-space-{self.id}','children'),
                       Input(f'plot-type-{self.id}','value'),
                       prevent_inital_call=True)
        def create_plots(plot_type):
            """creates plot specifc settings
            Args:
                plot_type (string):type of the plot
            """
            if plot_type=='Parallel Coordinates':
                PCPlot.set_data(self.data)
                return [dbc.Row(PCPlot.get_plot_ui()),
                    dbc.Row(PCPlot.get_settings_ui())]
            elif plot_type=='Violinplot':
                VioPlot.set_data(self.data)
                return [dbc.Row(VioPlot.get_plot_ui()),
                    dbc.Row(VioPlot.get_settings_ui())]
            elif plot_type=='Boxplot':
                BoxPlot.set_data(self.data)
                return [dbc.Row(BoxPlot.get_plot_ui()),
                    dbc.Row(BoxPlot.get_settings_ui())]
            elif plot_type=='ECDF Plot':
                ECDFPlot.set_data(self.data)
                return [dbc.Row(ECDFPlot.get_plot_ui()),
                    dbc.Row(ECDFPlot.get_settings_ui())]
            elif plot_type=='Histogram':
                HistPlot.set_data(self.data)
                return [dbc.Row(HistPlot.get_plot_ui()),
                    dbc.Row(HistPlot.get_settings_ui())]
            elif plot_type=='Scatterplot':
                SCPlot.set_data(self.data)
                return [dbc.Row(SCPlot.get_plot_ui()),
                    dbc.Row(SCPlot.get_settings_ui())]
            return [],[]
        create_dropdown_paging_callback(f'plot-type-{self.id}',app)