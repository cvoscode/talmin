from dash import dcc,html,Input, Output, State,ctx,no_update
from plotly.subplots import make_subplots
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import plotly.express as px
import sys
# insert package path to get the utils components
sys.path.insert(0, r'talmin')
from utils.Base_Components import *
from ui.read_data import DataReader
import polars as pl
from scipy.stats import epps_singleton_2samp
import dash


class DataComparer(dash.Dash):
    def __init__(self,id):
        self.id=id
        self.ReferenzData=DataReader(id=f'Referenz-Data-{self.id}')
        self.CompareData=DataReader(id=f'Compare-Data-{self.id}')
        self.es_data={}
        self.Tab1=dbc.Tab(label='Load Data',id=f'Tab1-{self.id}',
                            children=[dbc.Row([dbc.Col(html.H3("Referenz Data")),dbc.Col(create_Button(id=f'Start-Comparison-{self.id}',children=['Start Comparison'],color='primary'))]),
                            dbc.Row(self.ReferenzData.get_ui()),
                            dbc.Row(html.H3("Compare Data")),
                            dbc.Row(self.CompareData.get_ui()),])
        self.Tab2=dbc.Tab(label='Overview',id=f'Tab2-{self.id}',
              children=[html.H3(id=f'Feature-info-{self.id}'),
                        dbc.Row(dcc.Loading(id=f'Violin-Features-{self.id}')),
                        dbc.Row(dcc.Loading(id=f'Correlation-Difference-{self.id}')),],disabled=True)
        self.Tab3=dbc.Tab(label='Details',id=f'Tab3-{self.id}',children=[dbc.Row(dbc.InputGroup([dcc.Dropdown(options=['1','2','Features']),
                                                               dbc.InputGroupText(f'KS-Value'),
                                                               ])),
                                        dbc.Row([dbc.Col(id=f'Rain-plot-{self.id}'),dbc.Col(id=f'ECDF-plot-{self.id}')]),],disabled=True)
        
    def es_test(self):
        for col in self.ReferenzData.data.columns:
            pvalue=epps_singleton_2samp(self.ReferenzData.data.get_column(col),self.CompareData.data.get_column(col)).pvalue
            self.es_data[col]={'pvalue':pvalue,'similar': True if pvalue >0.05 else False}

    def correlation_difference(self):
        corr_ReferenzData=self.ReferenzData.data.corr()
        corr_CompareData=self.CompareData.data.corr()
        self.corr_difference=corr_ReferenzData-corr_CompareData

    def get_ui(self):
        ui=html.Div([
            dbc.Row(html.H1("Data Comparer Demo")),
            html.Div(id=f'Info-div-{self.id}'),
            dbc.Tabs(id=f'Tabs-{self.id}',children=[self.Tab1,self.Tab2,self.Tab3]),
            
         ])
        return ui
    
    def create_base_callbacks(self,app):
        self.ReferenzData.create_base_callbacks(app=app)
        self.CompareData.create_base_callbacks(app=app)

        # @app.callback(Output(f'Start-Comparison-{self.id}','disabled'),
        #                 Input(f'get-data-button-Referenz-Data-{self.id}','n_clicks'),
        #               Input(f'get-data-button-Compare-Data-{self.id}','n_clicks'),
        #               )
        # def activate_comparison_button(ref,comp):
        #     if self.ReferenzData.data.is_empty() and self.CompareData.data.is_empty():
        #         return False
        #     else:
        #         return True
        
        @app.callback(Output(f'Info-div-{self.id}','children'),
                      Output(f'Tab2-{self.id}','disabled'),
                      Output(f'Tab3-{self.id}','disabled'),
                      Input(f'Start-Comparison-{self.id}','n_clicks'),
                      State(f'Tabs-{self.id}','children'),prevent_inital_call=True)
        def compare_data(start_comparison,children):
            if ctx.triggered_id==f'Start-Comparison-{self.id}':
                if  self.ReferenzData.data.schema != self.CompareData.data.schema:
                    return create_Toast(children=['The data you provided does not have the same schema! In order to compare the data both datasets must have the same schema'],header='Schema Error',icon='danger'),True,True
                elif self.ReferenzData.numeric!=self.ReferenzData.data.columns:
                    return create_Toast('There are non-numeric values in the data. Currently this non numeric data is not suported!','Non Numeric Values Detected','danger'),True,True
                else:
                    self.es_test()
                    self.correlation_difference()
                    print(self.es_data)
                    print(self.corr_difference)
                    return create_Toast('Computations are finished','Finished Computations','sucess'),False,False
            else:
                raise PreventUpdate
            
        @app.callback(Output(f'Feature-info-{self.id}','children'),
            Input(f'Tab2-{self.id}','disabled'),)
        def update_overview(state):
            different_cols=[]
            cols=self.ReferenzData.data.columns
            for col in cols:
                if self.es_data[col]['similar']==False:
                    different_cols.append(col)
            percent=round((len(cols)-len(different_cols))/len(cols)*100,2)   
            res=f'{percent} % of Features seem to be similar!'
            if percent!=100:
                res=f"{percent} % of Features seem to be similar! Unsimilar columns are: {(' ,').join(different_cols)}"
            return  res
        @app.callback(Output(f'Violin-Features-{self.id}','children'),
                      Input(f'Tab2-{self.id}','disabled'))
        def create_violine_plots(trigger):
            cols=self.ReferenzData.data.columns
            fig = make_subplots(cols=len(cols), rows=1, subplot_titles=cols)
            # Loop through columns and add violin plots
            for i, column in enumerate(cols, start=1):
                fig1=go.Figure()
                fig1.add_trace(go.Violin(x=['Reference Data'] * len(self.ReferenzData.data.get_column(column)),
                                        y=self.CompareData.data.get_column(column),
                                        line_color='blue'))
                fig1.add_trace(go.Violin(x=['Compare Data'] * len(self.CompareData.data.get_column(column)),
                                        y=self.ReferenzData.data.get_column(column),
                                        line_color='orange'))
                fig.add_trace(fig1.data[0],row=1, col=i)
                fig.add_trace(fig1.data[1],row=1, col=i)
            fig.update_layout(violingap=0,violinmode='overlay',showlegend=False)
                # Update subplot layout
            fig.update_layout(title='Comparison of Data Sources',
                            xaxis=dict(tickmode='array', tickvals=list(range(1, len(cols) + 1)),
                                        ticktext=cols),showlegend=False,
                            xaxis_title='Columns',
                            yaxis_title='Values')

            return dcc.Graph(figure=fig)
        
            #self.create_Violin_plots():
            #self.create_Correlation_Difference()
    