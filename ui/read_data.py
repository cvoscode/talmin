import dash
from dash import dcc,html,Input, Output, State,ctx
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import plotly.express as px
import os
import sys
# insert package path to get the utils components
sys.path.insert(0, r'talmin')
from utils.Base_Components import *
from plotting.Base_Plotter import PlotlyFigure
import polars as pl



class DataReader():
    def __init__(self,id):
        self.data_path=None
        self.file_type=None
        self.data=None
        self.has_header=True
        self.seperator=','
        self.low_memory=False
        self.id=id

    def set_path(self,path:str):
        """set file path

        Args:
            path (str): file path
        """
        path=path.strip('\"')
        self.data_path=os.path.normpath(path)
        
    def set_file_type(self,filetype:str):
        """set file_type

        Args:
            filetype (str): filetype, options: csv,parquet
        """
        self.file_type=filetype

    def set_has_header(self,header:bool):
        self.has_header=header
    
    def set_low_memory(self,low_memory:bool):
        self.low_memory=low_memory
    
    def set_seperator(self,sep:str):
     pass
    def get_data(self):
        """
        get data:
        We use the data path to give a source for polars to scan. Other Parameters are mainly used for csv
        If there is not data path or no file type the data path or file type get set to false, this is going to be used to return the Error to the UI
        """
        if self.data_path:
            if self.file_type:
                if self.file_type=='csv':
                    self.data=pl.read_csv(source=self.data_path,has_header=self.has_header,low_memory=self.low_memory)
                elif self.file_type=='parquet':
                    self.data=pl.scan_parquet(source=self.data_path)
                else: self.data='file_type'
            else: self.data='file_type'
        else: self.data='data_path'

    def get_ui(self):
        ui=html.Div([
            dbc.Row([
            dbc.Col(dbc.Stack([create_Text_Input(id=f'data_path-input-{self.id}',placeholder='Enter a path to the file you want to read'),
                               create_Button(id=f'get-data-button-{self.id}',color='primary',children=['Read Data']),
                               create_dropdown(id=f'select-filetype{self.id}',options=['csv','parquet'],value='parquet')],
                               direction='horizontal',gap=2)),
            dbc.Col(dbc.Stack([create_dropdown(id=f'seperator-{self.id}',options=[',','.',';'],value=','),
                               create_dropdown(id=f'has_header-{self.id}',options=['With Column Names','Without Column Names'],value='With Column Names'),
                               create_dropdown(id=f'low_memory-{self.id}',options=['Compress','No Compression'],value='No Compression')],
                               direction='horizontal',gap=2
                               )),
            ]),
            dbc.Tooltip(id=f'data_path-tipp-{self.id}',target=f'data_path-input-{self.id}',placement='top',className="ml-auto"),
            create_Tooltip(f'Those are the supported file types',target=f'select-filetype{self.id}'),
            create_Tooltip(f'You can select the seperator for csv files',target=f'seperator-{self.id}'),
            create_Tooltip(f'You can set wether your csv has Column Names or not for csv files',target=f'has_header-{self.id}'),
            create_Tooltip(f'You can set wether you want to compress the data in memory for csv files. You should use this only for big files, since compressing hurts performance',target=f'low_memory-{self.id}'),
            html.Div(id=f'Info-div-{self.id}')
        ])
        return ui
    def create_base_callbacks(self,app):
        @app.callback(Output(f'low_memory-{self.id}','disabled'),
                      Output(f'has_header-{self.id}','disabled'),
                      Output(f'seperator-{self.id}','disabled'),
                      Input(f'select-filetype{self.id}','value')
                      )
        def set_filetype(ftype):
            self.file_type=ftype
            if ftype=='csv':
                return False,False,False
            elif ftype=='parquet':
                return True,True,True
            
        @app.callback(Output(f'get-data-button-{self.id}','disabled'),
                      Output(f'data_path-tipp-{self.id}','children'),
                      Input(f'data_path-input-{self.id}','value'),
                      Input(f'select-filetype{self.id}','value'),
                      Input(f'seperator-{self.id}','value'),
                      Input(f'has_header-{self.id}','value'),
                      Input(f'low_memory-{self.id}','value'),
                      )
        def change_vals_and_validate(path,filetype,seperator,header,low_memory):
            if ctx.triggered_id==f'data_path-input-{self.id}':
                self.set_path(path)
            elif ctx.triggered_id==f'select-filetype{self.id}':
                self.set_file_type(filetype)
            elif ctx.triggered_id==f'seperator-{self.id}':
                self.seperator=seperator
            elif ctx.triggered_id==f'has_header-{self.id}':
                if header=='With Column Names':
                    self.set_has_header(True)
                else:
                    self.set_has_header(False)
            elif ctx.triggered_id==f'low_memory-{self.id}':
                if low_memory=='No Compression':
                    self.set_low_memory(False)
                else:
                    self.set_low_memory(True)
            if path:
                return False,'You can now read this *.csv or a *.parquet file'
            else:
                return True,'To read a file you must first specify a path to a *.csv or *.parquet file'
            
        @app.callback(Output(f'Info-div-{self.id}','children'),
                      Input(f'get-data-button-{self.id}','n_clicks'))        
        def read_data(clicks):
            if clicks:
                try:
                    print(self.file_type)
                    self.get_data()
                    print(self.data)
                    return create_Toast(f'The file {self.data_path} was read sucessfully','Read Sucess','sucess')
                except:
                    if self.data_path==False:
                        reason='an issue with the path occured'
                    elif self.file_type==False:
                        reason='an issue with the file type occured'
                    else:
                        reason='an unknown issure occured'
                    return create_Toast(f'The file {self.data_path} could not be read, since {reason}.','Error','danger')

    