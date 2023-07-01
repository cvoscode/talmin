import sys

import dash_bootstrap_components as dbc
import plotly.express as px
import polars as pl

from dash import Input, Output, State, ctx, dcc, html
from dash.exceptions import PreventUpdate

sys.path.insert(0, r'talmin')
from plotting.Base_Plotter import *
from utils.Base_Components import *
from utils.polars_addons import detect_column_types

save_path=''

class ECDFPlotter(Base_Fig):
    def __init__(self, id):
        self.x=None
        self.y=None
        self.color=None
        self.marginal=None
        self.fig={}
        self.numeric_cols=None
        self.temporal_cols=None
        self.nested_cols=None
        self.discrete_cols=None
        self.title=None
        self.id=id
    def update_title(self,title):
        self.title=title

    def set_data(self,df:pl.DataFrame):
        self.data=df
        self.numeric_cols,self.temporal_cols,self.nested_cols,self.discrete_cols=detect_column_types(df)
        self.all_columns=df.columns

    def set_x(self,x:str):
        """_summary_

        Args:
            x (str): name of x col
        """
        self.x=x
    def set_y(self,y:str):
        """_summary_

        Args:
            y (str): name of y col
        """
        self.y=y
    
    def set_marginal(self,marginal:str):
        """_summary_

        Args:
            marginal (str): 'rug','violine','histogram','box',None 
        """
        self.marginal=marginal
    def set_color(self,color:str):
        """_summary_

        Args:
            color (str): color col
        """
        self.color=color

    def update_fig(self):
        if self.x:
            self.fig=px.ecdf(self.data.to_pandas(),x=self.x,color=self.color,marginal=self.marginal)
        elif self.y:
            self.fig=px.ecdf(self.data.to_pandas(),y=self.y,color=self.color,marginal=self.marginal)
        if self.title and self.fig:
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
            create_dropdown_paging(id=f'X-{self.id}',options=self.all_columns,value=None,name='X-Column',multi=True),
            create_Tooltip('Select a column from your data for the horizontal axis',target=f'X-{self.id}')
            ]),
            dbc.Col([
            create_dropdown_paging(id=f'Y-{self.id}',options=self.all_columns,value=None,name='Y-Column',multi=False),
            create_Tooltip('Select a column from your data for the vertical axis',target=f'Y-{self.id}')
            ]),
            dbc.Col([
            create_dropdown_paging(id=f'color-{self.id}',options=self.all_columns,value=None,name='Color-Column',multi=False),
            create_Tooltip('Select a column from your data as color',target=f'color-{self.id}')
            ]),
            dbc.Col([
            create_dropdown_paging(id=f'marginal-{self.id}',options=['rug','histogram','box','violin'],value=None,name='marginal',multi=False),
            create_Tooltip('Select a column from your data as color',target=f'marginal-{self.id}')
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
        @app.callback(Output(f"modal-fs-{self.id}",'is_open'),
                    Input(f'popup-button-{self.id}','n_clicks'),
                    Input(f"close-modal-{self.id}",'n_clicks'),allow_duplicate=True)
        def modal(popup,clos):
            if ctx.triggered_id==f'popup-button-{self.id}':
                return True
            if ctx.triggered_id==f"close-modal{self.id}":
                return False
            
        @app.callback(Output(f'Graph-{self.id}','figure'),
                      Output(f'Graph-Modal-{self.id}','figure'),
                      Output(f'plot_div-{self.id}','children',allow_duplicate=True),
                      Input(f'X-{self.id}','value'),
                      Input(f'Y-{self.id}','value'),
                      Input(f'color-{self.id}','value'),
                      Input(f'marginal-{self.id}','value'),
                      Input(f'title-{self.id}','value'),
                      prevent_initial_call=True,)
        def vals(x,y,color,marginal,title):
            if ctx.triggered_id==f'X-{self.id}':
                self.set_x(x)
            elif ctx.triggered_id==f'Y-{self.id}':
                self.set_y(y)
            elif ctx.triggered_id==f'color-{self.id}':
                self.set_color(color)
            elif ctx.triggered_id==f'marginal-{self.id}':
                self.set_marginal(marginal)
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
        
        for id in [f'X-{self.id}',f'Y-{self.id}',f'color-{self.id}']:
            create_dropdown_paging_callback(id,app)

        @app.callback(Output(f'plot_div-{self.id}','children',allow_duplicate=True),
                      Input(f'save-{self.id}','n_clicks'),
                      State(f'title-{self.id}','value'),
                      prevent_initial_callback=True
                      )
        #TODO correct save plot
        def save_plot(save,title):
            if save:
                super().save(self.fig,title,save_path)
                return create_Toast(children=f'The plot was sucessfully saved to {save_path} under the name {title}',header='Plot saved',icon='sucess')