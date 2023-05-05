import dash
from dash import dcc,html,Input, Output, State
from plotting.Base_Plotter import PlotlyFigure
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import plotly.express as px
from ui.read_data import DataReader


df = px.data.iris()
fig = px.scatter(df, x="sepal_width", y="sepal_length", color="species", marginal_y="violin",
           marginal_x="box", trendline="ols", template="simple_white")

df["e"] = df["sepal_width"]/100
fig2 = px.scatter(df, x="sepal_width", y="sepal_length", color="species", error_x="e", error_y="e")

fig3 = px.bar(df, x="sepal_width", y="sepal_length", color="species", barmode="group")

figs=[fig,fig2,fig3]


Get_Data=DataReader(id='asd')


# Create a Dash app
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

fig=PlotlyFigure(id='fig',fig=fig)
fig2=PlotlyFigure(id='fig2',fig=fig2)
fig3=PlotlyFigure(id='fig3',fig=fig3)


# Define the app layout
app.layout = dbc.Card([
    html.H1('Plotly Figure Demo'),
    dbc.Row([dbc.Col(fig.get_ui()),dbc.Col(fig2.get_ui()),dbc.Col(fig3.get_ui())]),
    dbc.Row(Get_Data.get_ui())
])

fig.cerate_base_callbacks(app)
fig2.cerate_base_callbacks(app)
fig3.cerate_base_callbacks(app)
Get_Data.create_base_callbacks(app)

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)