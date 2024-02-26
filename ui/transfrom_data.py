from dash import dcc,html,Input, Output, State,ctx
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import plotly.express as px
import os
import sys
# insert package path to get the utils components
sys.path.insert(0, r'talmin')
from transformation.transformer import *
from utils.Base_Components import *
from utils.polars_addons import detect_column_types
from plotting.Base_Plotter import Base_Fig
import polars as pl
import dash


class DataTransformer(dash.Dash):
    def __init__(self,id):
        self.data=pl.DataFrame()
        self.id=id
        self.datatypes=['Float32','Int32','Datetime','Binary','Object','Utf8']
        self.options=['all columns']+self.data.columns
        self.numeric_cols,self.temporal_cols,self.nested_cols,self.discrete_cols=None,None,None,None
        self.types=None
       

    def set_data(self,df:pl.DataFrame):
        self.data=df
        self.numeric_cols,self.temporal_cols,self.nested_cols,self.discrete_cols=detect_column_types(self.data)
        self.options=['all columns']+self.data.columns
        self.calc_stats(df)
        
    def calc_stats(self,df:pl.DataFrame):
        print(df)
        self.stats=df.describe().select(pl.exclude('describe')).transpose(column_names=['count','null_count','mean','std','min','25%','50%','75%','max'])[1:].with_columns(pl.Series("Original Columns", df.columns),pl.all())
    
    def get_ui(self):
        ui=html.Div([
            dbc.Row(id=f'table-row-{self.id}',children=[dcc.Tabs(children=[dcc.Tab(label='Data',children=create_table(id=f'trans-table-{self.id}',df=self.data)),dcc.Tab(label='Statistics',children=create_table(id=f'stats-table-{self.id}',df=self.stats))])]),
            dbc.Row(id=f'info-row-{self.id}'),
            dbc.Row([dbc.Col([
                              dbc.Stack([
                                  html.H4(children=['Scaling']),
                                  create_dropdown(id=f'columns-{self.id}',options=self.options,value=''),
                                  create_Button(id=f'Label-encode-{self.id}',color='primary',children=['Label Encode Colum']),
                                  create_Button(id=f'MinMax-scaling-{self.id}',color='primary',children=['MinMax Scale Colum']),
                                  create_Button(id=f'Standardize-{self.id}',color='primary',children=['Standardize Colum']),
                              ],gap=2
                              )]),                                                                                                  dbc.Col([
                                                                                                                                             dbc.Stack([
                                                                                                                                                 html.H4(children=['Change Types']),
                                                                                                                                                 create_dropdown(id=f'columns-types-{self.id}',options=self.options,value=''),
                                                                                                                                                 create_dropdown(id=f'types-{self.id}',options=self.datatypes,value=''),
                                                                                                                                                 create_Button(id=f'change-type-button-{self.id}',color='primary',children=['Change Type'])
                                                                                                                                             ],gap=2)
                                                                                                                                             
                                                                                                                                             
                                                                                                                                             ])]),



            dbc.Row([dbc.Col([
                                dbc.Stack([
                                    html.H4(children=['DropNaN']),
                                    create_dropdown(id=f'columns-drop-{self.id}',options=self.options,value=''),
                                    create_Button(id=f'drop-null-{self.id}',color='primary',children=['DropNulls']),

                                ],gap=2
                        
                              )]),                                                                                                   dbc.Col([
                                                                                                                                                dbc.Stack([
                                                                                                                                                    html.H4(children=['Variance Filter']),
                                                                                                                                                    create_Numeric_Input(id=f'variance-input-{self.id}',placeholder='Variance Threshold',min=0,max=1,step=0.001),
                                                                                                                                                    create_Button(id=f'variance-button-{self.id}',color='primary',children=['Filter Variance'])

                                                                                                                                                ],gap=2)
                                  
                                                                                                                                                
                                                                                                                                             
                                                                                                                                             ])]),



         ])
        return ui
    def create_base_callbacks(self,app):
        @app.callback(Output(f'table-row-{self.id}','children'),
                      Output(f'info-row-{self.id}','children'),
                      #Variance
                      State(f'variance-input-{self.id}','value'),
                      Input(f'variance-button-{self.id}','n_clicks'),
                      #drop-null
                      Input(f'drop-null-{self.id}','n_clicks'),
                      State(f'columns-drop-{self.id}','value'),
                      # scale
                      State(f'columns-{self.id}','value'),
                      Input(f'Label-encode-{self.id}','n_clicks'),
                      Input(f'MinMax-scaling-{self.id}','n_clicks'),
                      Input(f'Standardize-{self.id}','n_clicks'),
                      #change types
                      State(f'columns-types-{self.id}','value'),
                      State(f'types-{self.id}','value'),
                      Input(f'change-type-button-{self.id}','n_clicks'),


                      prevent_initial_call=True)
        def update_table_and_data(variance_threshold,filter_variance,drop,drop_col,scale_col,label,min,standard,col_type,types,change_type):
            if ctx.triggered_id==f'variance-button-{self.id}':
                scaler=MinMaxScaler()
                scaled=scaler.fit_transform(self.data[self.numeric_cols])
                variance=scaled.var()
                drop_cols=[]
                for col in self.numeric_cols:
                    if pl.first(variance[col])<=float(variance_threshold):
                        drop_cols.append(col)
                self.set_data(self.data.drop(drop_cols))
                drop_cols=', '.join(drop_cols)
                return [dcc.Tabs(children=[dcc.Tab(label='Data',children=create_table(id=f'trans-table-{self.id}',df=self.data)),dcc.Tab(label='Statistics',children=create_table(id=f'stats-table-{self.id}',df=self.stats))])],create_Toast(children=[f'The following columns were dropped due to lower vaiance than {variance_threshold}: {drop_cols}'],header='Variance Filter',icon='sucess')
            if ctx.triggered_id==f'drop-null-{self.id}':
                if drop_col=='all columns':
                    self.set_data(self.data.drop_nulls())
                else:
                    self.set_data(self.data.drop_nulls(subset=drop_col))
                return [dcc.Tabs(children=[dcc.Tab(label='Data',children=create_table(id=f'trans-table-{self.id}',df=self.data)),dcc.Tab(label='Statistics',children=create_table(id=f'stats-table-{self.id}',df=self.stats))])],create_Toast(children=[f'On {drop_col} the nulls where dropped!'],header='Drop Nulls',icon='sucess')
            if ctx.triggered_id==f'Label-encode-{self.id}':
                if scale_col=='all columns':
                    # try:
                    label=LabelEncoder()
                    print(label.fit_transform(self.data.select(pl.col(col) for col in self.discrete_cols),self.discrete_cols))
                    self.set_data(self.data.with_columns(label.fit_transform(self.data.select(pl.col(col) for col in self.discrete_cols),self.discrete_cols)))
                    sucess=True
                    # except:
                    #     sucess=False
                else:
                    # try:
                    label=LabelEncoder()
                    self.set_data(self.data.with_columns(label.fit_transform(self.data.select(pl.col(scale_col)),scale_col)))
                    sucess=True
                    # except:
                    #     sucess=False
                if sucess:
                    return [dcc.Tabs(children=[dcc.Tab(label='Data',children=create_table(id=f'trans-table-{self.id}',df=self.data)),dcc.Tab(label='Statistics',children=create_table(id=f'stats-table-{self.id}',df=self.stats))])],create_Toast(children=[f'{scale_col}  was Label Encoded!'],header='Label Encoder',icon='sucess')
                else: return [dcc.Tabs(children=[dcc.Tab(label='Data',children=create_table(id=f'trans-table-{self.id}',df=self.data)),dcc.Tab(label='Statistics',children=create_table(id=f'stats-table-{self.id}',df=self.stats))])],create_Toast(children=[f'{scale_col} was not Label Encoded!'],header='Label Encoder',icon='danger')

            if ctx.triggered_id==f'MinMax-scaling-{self.id}':
                if scale_col=='all columns':
                    scaler=MinMaxScaler()
                    #this works really nicely
                    self.set_data(self.data.with_columns(scaler.fit_transform(self.data.select(pl.col(col) for col in self.numeric_cols))))
                    sucess=True
                else:
                    scaler=MinMaxScaler()
                    self.set_data(self.data.with_columns(scaler.fit_transform(self.data.select(pl.col(scale_col)))))
                    sucess=True
                if sucess:
                    return [dcc.Tabs(children=[dcc.Tab(label='Data',children=create_table(id=f'trans-table-{self.id}',df=self.data)),dcc.Tab(label='Statistics',children=create_table(id=f'stats-table-{self.id}',df=self.stats))])],create_Toast(children=[f'{scale_col}  was MinMax scaled!'],header='MinMax Scaler',icon='sucess')
                else: return [dcc.Tabs(children=[dcc.Tab(label='Data',children=create_table(id=f'trans-table-{self.id}',df=self.data)),dcc.Tab(label='Statistics',children=create_table(id=f'stats-table-{self.id}',df=self.stats))])],create_Toast(children=[f'{scale_col} was not MinMax scaled!'],header='MinMax Scaler',icon='danger')
            if ctx.triggered_id==f'Standardize-{self.id}':
                if scale_col=='all columns':
                    scaler=StandardScaler()
                    #this works really nicely
                    self.set_data(self.data.with_columns(scaler.fit_transform(self.data.select(pl.col(col) for col in self.numeric_cols))))
                    sucess=True
                else:
                    scaler=StandardScaler()
                    self.set_data(self.data.with_columns(scaler.fit_transform(self.data.select(pl.col(scale_col)))))
                    sucess=True
                if sucess:
                    return [dcc.Tabs(children=[dcc.Tab(label='Data',children=create_table(id=f'trans-table-{self.id}',df=self.data)),dcc.Tab(label='Statistics',children=create_table(id=f'stats-table-{self.id}',df=self.stats))])],create_Toast(children=[f'{scale_col}  was standardized!'],header='Standardize',icon='sucess')
                else: return [dcc.Tabs(children=[dcc.Tab(label='Data',children=create_table(id=f'trans-table-{self.id}',df=self.data)),dcc.Tab(label='Statistics',children=create_table(id=f'stats-table-{self.id}',df=self.stats))])],create_Toast(children=[f'{scale_col} was not standardized!'],header='Standardize',icon='danger')
            if ctx.triggered_id==f'change-type-button-{self.id}':
                try:
                    self.set_data(self.data.with_columns(pl.col(col_type).cast(eval(f'pl.{types}'))).rename({col_type:f"{col_type.split(' ')[0]} [{types}]"}))
                    print(self.data)
                    sucess=True
                except:
                    sucess=False
                if sucess:
                    return [dcc.Tabs(children=[dcc.Tab(label='Data',children=create_table(id=f'trans-table-{self.id}',df=self.data)),dcc.Tab(label='Statistics',children=create_table(id=f'stats-table-{self.id}',df=self.stats))])],create_Toast(children=[f'The type of {scale_col} was changed to {types}!'],header='Change Type',icon='sucess')
                else: return [dcc.Tabs(children=[dcc.Tab(label='Data',children=create_table(id=f'trans-table-{self.id}',df=self.data)),dcc.Tab(label='Statistics',children=create_table(id=f'stats-table-{self.id}',df=self.stats))])],create_Toast(children=[f'The type of {scale_col} could not be changed!'],header='Change Type',icon='danger')
           



        @app.callback(# scale
                    Output(f'Label-encode-{self.id}','disabled'),
                    Output(f'MinMax-scaling-{self.id}','disabled'),
                    Output(f'Standardize-{self.id}','disabled'),
                    Input(f'columns-{self.id}','value'),
                    )
        def activate_scaling(value):
            if value=='all columns':
                return True,False,False
            elif value: 
                return False,False,False
            else: 
                return True,True,True
        @app.callback(
                    Output(f'drop-null-{self.id}','disabled'),
                    Input(f'columns-drop-{self.id}','value'),
                    )
        def activate_scaling(value):
            if value:
                return False
            else: 
                return True
        @app.callback(
                    Output(f'variance-button-{self.id}','disabled'),
                    Input(f'variance-input-{self.id}','value'),
                    )
        def activate_scaling(value):
            if value:
                return False
            else: 
                return True
        @app.callback(
                    Output(f'change-type-button-{self.id}','disabled'),
                    Input(f'columns-types-{self.id}','value'),
                    Input(f'types-{self.id}','value'),
                    )
        def activate_scaling(value,types):
            if value and types:
                return False
            else: 
                return True
        