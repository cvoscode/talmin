import dash
from dash import dcc,html,Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from utils.Base_Components import *
import plotly.express as px
import flask
from ui.read_data import DataReader
from ui.transfrom_data import DataTransformer
from ui.data import DataContainer
from ui.explore_data import DataExplorer


server = flask.Flask(__name__)
app=dash.Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP],suppress_callback_exceptions=True,server=server)




# The data container hold the actual version of the data in the memory
Data_Container=DataContainer()

Get_Data=DataReader(id='Data-Reader')
TransformData=DataTransformer(id='Data-Transformer')
ExplorData=DataExplorer(id='Data-Explorer')

app.layout = dbc.Container([
                            #header
                            dbc.Row([
                                    dbc.Col(html.H1(id='Header',children='Talmin',className='Header')),html.Img(src=app.get_asset_url('logo.png'),style={'height':'60px','width':'105px'}),html.Hr()
                                    ]),
                            #Table and GlobalSettings
                            dbc.Row([
                                    dbc.Tabs(id='Tabs',children=[
                                            dbc.Tab(id='Tab0',label='Load and view data',children=[Get_Data.get_ui()]),
                                            dbc.Tab(id='Tab1',label='Transfrom data',children=[
                                                dbc.Row([dbc.Col(html.H3(id=f'View-Header-Tab1',children=['Transfrom your data'])),dbc.Col(create_Button(f'Get-data-button-Tab1',children=['Refresh Data'],color='primary'))]),
                                                dbc.Row(id='Tab1-UI'),
                                            ]),
                                            dbc.Tab(id='Tab2',label='Explore data',
                                                    children=[
                                                        dbc.Row([dbc.Col(html.H3(id=f'View-Header-Tab2',children=['Explore your data'])),dbc.Col(create_Button(f'Get-data-button-Tab2',children=['Refresh Data'],color='primary'))]),
                                                        dbc.Row(id='Tab2-UI'),

                                                    ]),
                                            dbc.Tab(id='Tab3',label='Dimensionality Reduction'),
                                            dbc.Tab(id='Tab4',label='Synthetic Data Generation'),
                                            ]),
                                    ]),
                            ],fluid=True)

Get_Data.create_base_callbacks(app)
TransformData.create_base_callbacks(app)
ExplorData.create_base_callbacks(app)

@app.callback(  Output('Tab1-UI','children'),
                Input('Get-data-button-Tab1','n_clicks'),
              )
def get_data_and_make_ui(get_data):
    # if there are data inputted into the app
    if not Get_Data.data.is_empty():
        TransformData.set_data(Get_Data.data)
        return TransformData.get_ui()
    else: return html.H5('Please load some data first!')


@app.callback(  Output('Tab2-UI','children'),
                Input('Get-data-button-Tab2','n_clicks'),
              )
def get_data_and_make_ui(get_data):
    # if there are data inputted into the app
    if not TransformData.data.is_empty():
        ExplorData.set_data(TransformData.data)
        return ExplorData.get_ui()
    else: return html.H5('Please load some data first!')




# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)