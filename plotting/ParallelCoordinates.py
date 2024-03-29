import sys

import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import numpy as np
import polars as pl

from dash import Input, Output, State, ctx, dcc, html
from dash.exceptions import PreventUpdate

sys.path.insert(0, r'talmin')
from plotting.Base_Plotter import *
from utils.Base_Components import *
from utils.polars_addons import detect_column_types

save_path=''

class PCPlotter(Base_Fig):
    def __init__(self, id,app):
        self.x=None
        self.y=None
        self.color=None
        self.points=None
        self.fig={}
        self.numeric_cols=None
        self.temporal_cols=None
        self.nested_cols=None
        self.discrete_cols=None
        self.title=None
        self.id=id
        self.cerate_base_callbacks(app)
    def update_title(self,title):
        self.title=title

    def set_data(self,df:pl.DataFrame):
        self.data=df
        self.numeric_cols,self.temporal_cols,self.nested_cols,self.discrete_cols=detect_column_types(df)
        self.all_columns=df.columns

    def set_color(self,color:str):
        """_summary_

        Args:
            color (str): color col
        """
        self.color=color

    def update_fig(self):
        dimensions = list([dict(range = [self.data[col].min(),self.data[col].max()],
         label = col, values = self.data[col],multiselect = True,) for col in self.numeric_cols])
        if len(dimensions)<12:
            labelangle=0
        else:
            labelangle=-45
        if self.color:
            self.fig=go.Figure(data=go.Parcoords(dimensions=dimensions,labelangle=labelangle,labelside='bottom',line = dict(color = self.data[self.color],showscale = True, colorbar = {'title': self.color}),unselected=dict(line={'opacity':0.1})))#name=figure_temp,colorscale = color_scale
        else:
            self.fig=go.Figure(data=go.Parcoords(dimensions=dimensions,labelangle=labelangle,labelside='bottom',unselected=dict(line={'opacity':0.1})))#name=figure_temp,
        #print(self.fig.to_json())
        if self.title:
            self.fig.update_layout(title=self.title)
    
        
    def get_plot_ui(self):
        ui=html.Div([
        dbc.Row(    
        dbc.Card([               
            dbc.Row(id=f'plot-div-{self.id}',children=[dcc.Loading(id=f'loading-{self.id}',children=[dcc.Graph(id=f'Graph-{self.id}',figure={},config=dict(displaylogo=False, toImageButtonOptions=dict(format= 'svg'),
                    modeBarButtonsToAdd=['drawline',
                                        'drawopenpath',  
                                        'drawclosedpath',
                                        'drawcircle',
                                        'drawrect',
                                        'eraseshape'
                                       ]))]),  
                        dbc.Modal(
                        [
                            dbc.ModalHeader(dbc.ModalTitle(f"Scatter Graph")),
                            dbc.ModalBody(dcc.Graph(id=f'Graph-Modal-{self.id}',figure={},config=dict(displaylogo=False, toImageButtonOptions=dict(format= 'svg'),
                                        modeBarButtonsToAdd=['drawline',
                                        'drawopenpath',  
                                        'drawclosedpath',
                                        'drawcircle',
                                        'drawrect',
                                        'eraseshape'
                                       ]))),
                            dbc.ModalFooter(
                                dbc.Button("Close", id=f"close-modal-{self.id}", className="ml-auto"),
                                 ),
                        ],
                        id=f"modal-fs-{self.id}",
                        fullscreen=True,is_open=False
                    )]),
            dbc.Row(dbc.Col(dbc.Stack([create_Button(id=f'popup-button-{self.id}', color='primary',children=['Popup']),html.Div(id=f'plot_div-{self.id}') ],direction='horizontal'), width={"offset":11})),
            create_Tooltip(f"Opens the graph in full screen mode",target=f'popup-button-{self.id}')
            ]),),])
        return ui
    def get_settings_ui(self):
        ui=dbc.Row([
            html.Hr(),
            dbc.Col([
            create_dropdown_paging(id=f'color-{self.id}',options=self.numeric_cols,value=None,name='Color-Column',multi=False),
            create_Tooltip('Select a column from your data as color',target=f'color-{self.id}')
            ]),
            dbc.Col([
            dbc.InputGroup([
            dbc.InputGroupText('Title'),
            create_Text_Input(placeholder='Provide a title for saving',id=f'title-{self.id}'),
            create_Button(id=f'save-{self.id}',children=['Save Plot as HTML'],color='primary'),
            ]),
            create_Tooltip('Set your plot Title, the same title is used while saving',target=f'title-{self.id}'),
            create_Tooltip('Save your plot as an HTML file under the globally set directory',target=f'save-{self.id}'),
            ]),
        ])     
        return ui




    def cerate_base_callbacks(self, app):
       
        #TODO callbacks are not registered???
        @app.callback(Output(f"modal-fs-{self.id}",'is_open'),
                    Input(f'popup-button-{self.id}','n_clicks'),
                    Input(f"close-modal-{self.id}",'n_clicks'))
        def modal(popup,clos):
            if ctx.triggered_id==f'popup-button-{self.id}':
                return True
            if ctx.triggered_id==f"close-modal{self.id}":
                return False
            
        @app.callback(Output(f'Graph-{self.id}','figure'),
                      Output(f'Graph-Modal-{self.id}','figure'),
                      Output(f'plot_div-{self.id}','children'),
                      Input(f'color-{self.id}','value'),
                      Input(f'title-{self.id}','value'),
                      )
        def vals(color,title):
            if ctx.triggered_id==f'color-{self.id}':
                self.set_color(color)
            elif ctx.triggered_id==f'title-{self.id}':
                self.update_title(title=title)
                self.fig.update_layout(title=self.title)
                return self.fig,self.fig,[]
            self.update_fig()
            if self.fig:
                return self.fig,self.fig,[]
            else:
                raise PreventUpdate
                       
            
        # @app.callback(Output(f'color-{self.id}','disabled'),
        #               Output(f'save-{self.id}','disabled'),
        #               Output(f'title-{self.id}','disabled'),
        #               Input(f'X-{self.id}','value'),
        #               Input(f'Y-{self.id}','value'),
        #                )
        # def activate_settings(x,y):
        #     if not x or not y:
        #         return [True,True,True]
        #     else:
        #         return [False,False,False]
        
        for id in [f'color-{self.id}']:
            create_dropdown_paging_callback(id,app)

        @app.callback(Output(f'plot_div-{self.id}','children', allow_duplicate=True),
                      Input(f'save-{self.id}','n_clicks'),
                      State(f'title-{self.id}','value'),
                     
                      )
        #TODO correct save plot
        def save_plot(save,title):
      
            if save:
                super().save(self.fig,title,save_path)
                return create_Toast(children=f'The plot was sucessfully saved to {save_path} under the name {title}',header='Plot saved',icon='sucess')