import dash 
import polars as pl 
import plotly.graph_objects as go 
import dash_bootstrap_components as dbc
import sys
sys.path.insert(0, r'talmin')
from utils.Base_Components import *
from dash import dcc,html,Input, Output, State,ctx

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
        return [dbc.Col(id=f'plot-settings-{self.id}',
                        children=[dbc.Row([dbc.Col(
                                  children=[html.H4(['Select Plot Type']),
                                            create_dropdown(id=f'plot-type-{self.id}',options=self.plot_types,value='Violineplot'),
                                          ]),
                                dbc.Row([dbc.Col(id=f'plot-specific-settings-{self.id}')])]),],width=2),
                dbc.Col(id=f'plot-space-{self.id}',width=10)]
    def create_base_callbacks(self,app):
        @app.callback(Output(f'plot-specific-settings-{self.id}','children'),
                       Input(f'plot-type-{self.id}','children'))
        def create_plot_specific_settings(plot_type):
            """creates plot specifc settings
            Args:
                plot_type (string):type of the plot
            """
            return create_dropdown(id=f'id_{self.id}',options=['Test1','Test2'],value='Test1')
      