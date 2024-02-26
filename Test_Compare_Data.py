import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import polars as pl
from ui.read_data import DataReader
from utils.Base_Components import *
from ui.compare_data import DataComparer
import dash
from dash import Input, Output, State, dcc, html

import polars
df = polars.read_csv(r'C:\Python\Nsight\exmple_data\2019.csv')


# Create a Dash app
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
app = dash.Dash(external_stylesheets=[dbc.themes.LUMEN,dbc_css],prevent_initial_callbacks='initial_duplicate')
Data_Comparer=DataComparer(id='test')

# Define the app layout
app.layout = dbc.Card([
    Data_Comparer.get_ui()
    
])
Data_Comparer.create_base_callbacks(app=app)
# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
