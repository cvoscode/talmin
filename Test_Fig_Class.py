import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import polars as pl
from plotting.Base_Plotter import Base_Fig
from plotting.ParallelCoordinates import PCPlotter
from plotting.ScatterPlot import ScatterPlotter
from plotting.ECDF import ECDFPlotter
from plotting.Histogram import HistogramPlotter
from ui.read_data import DataReader

import dash
from dash import Input, Output, State, dcc, html

import polars
df = polars.read_csv(r'C:\Python\Nsight\exmple_data\2019.csv')

Base_Fig('')




# Create a Dash app
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP],prevent_initial_callbacks='initial_duplicate')

Scatter = HistogramPlotter(id="PC",app=app)
Scatter.set_data(df)
# Define the app layout
app.layout = dbc.Card([
    dbc.Row(html.H1("Plotly Figure Demo")),
    dbc.Row(Scatter.get_plot_ui(),),
    dbc.Row(Scatter.get_settings_ui())

])


Scatter.cerate_base_callbacks(app)
# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
