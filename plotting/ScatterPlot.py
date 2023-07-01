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

class ScatterPlotter(Base_Fig):
    def __init__(self, id):
        self.z=None
        self.x=None
        self.y=None
        self.color=None
        self.size=None
        self.size=None
        self.marginal_x=None
        self.marginal_y=None
        self.trendline=None
        self.fig={}
        self.facet_col=None
        self.numeric_cols=None
        self.temporal_cols=None
        self.nested_cols=None
        self.discrete_cols=None
        self.trendline_options=None
        self.animation_frame=None
        self.animation_group=None
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
    def set_z(self,z:str):
        """_summary_

        Args:
            z (str): name of z col
        """
        self.z=z
    def set_color(self,color:str):
        """_summary_

        Args:
            color (str): color col
        """
        self.color=color
    def set_size(self,size:str):
        """_summary_

        Args:
            size (_type_): size col
        """
        self.size=size
    def set_marginal_y(self,marginal_y:str):
        """_summary_

        Args:
            marginal_y (str): marginal of y "violine" or "boxplot"
        """
        self.marginal_y=marginal_y

    def set_marginal_x(self,marginal_x:str):
        """_summary_

        Args:
            marginal_x (str): marginal of y "violine" or "boxplot"
        """
        self.marginal_x=marginal_x
        

    def set_trendline(self,trendline):
        self.trendline=trendline
    
    def set_trendline_options(self,trendline):
        if trendline=='rolling':
            self.trendline_options=dict(window=5)
        elif trendline=='expanding':
            self.trendline_options=dict(function="max")
        elif trendline=='ewm':
            self.trendline_options=dict(halflife=2)
        else:
            self.trendline_options=None
    
    def set_facet_col(self,facet_col):
        self.facet_col=facet_col

    def set_animation_frame(self,animation_frame):
        self.animation_frame=animation_frame
    def set_animation_group(self,animation_group):
        self.animation_group=animation_group
    def update_fig(self):
        if self.x and self.y and self.z:
            self.fig=px.scatter_3d(self.data.to_pandas(),x=self.x,y=self.y,z=self.z,color=self.color,size=self.size)
            if self.title:
                self.fig.update_layout(title=self.title)
        elif self.y and self.x:
            self.fig=px.scatter(self.data.to_pandas(),x=self.x,y=self.y,color=self.color,size=self.size,marginal_x=self.marginal_x,marginal_y=self.marginal_y,trendline=self.trendline,trendline_options=self.trendline_options,facet_col=self.facet_col,
                                animation_frame=self.animation_frame,animation_group=self.animation_group)
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
            create_dropdown_paging(id=f'X-{self.id}',options=self.all_columns,value=None,name='X-Column',multi=False),
            create_Tooltip('Select a column from your data for the horizontal axis',target=f'X-{self.id}')
            ]),
            dbc.Col([
            create_dropdown_paging(id=f'Y-{self.id}',options=self.all_columns,value=None,name='Y-Column',multi=False),
            create_Tooltip('Select a column from your data for the vertical axis',target=f'Y-{self.id}')
            ]),
            dbc.Col([
            create_dropdown_paging(id=f'Z-{self.id}',options=self.all_columns,value=None,name='Z-Column',multi=False),
            create_Tooltip('Select a column from your data to create a 3d plot',target=f'Z-{self.id}')
            ]),
            dbc.Col([
            create_dropdown_paging(id=f'color-{self.id}',options=self.all_columns,value=None,name='Color-Column',multi=False),
            create_Tooltip('Select a column from your data as color',target=f'color-{self.id}')
            ]),
            dbc.Col([
            create_dropdown_paging(id=f'size-{self.id}',options=self.numeric_cols,value=None,name='Size-Column',multi=False),
            create_Tooltip('Select a column from your data as size',target=f'size-{self.id}')
            ]),
            html.Hr(),
            dbc.Row([
            dbc.Col([
            create_dropdown(id=f'marginal_x-{self.id}',options=['box','violin','rug','histogram'],value=None),
            create_Tooltip('Select a possible marginal plot for the horizontal axis',target=f'marginal_x-{self.id}')
            ]),
            dbc.Col([
            create_dropdown(id=f'marginal_y-{self.id}',options=['box','violin','rug','histogram'],value=None),
            create_Tooltip('Select a possible marginal plot for the vertical axis',target=f'marginal_y-{self.id}')
            ]),
            dbc.Col([
            create_dropdown(id=f'trendline-{self.id}',options=['ols','lowess','rolling','expanding','ewm'],value=None),
            create_Tooltip('Select a possible trendline option',target=f'trendline-{self.id}')
            ]),
            dbc.Col([
            create_dropdown(id=f'facet-{self.id}',options=self.discrete_cols,value=None),
            create_Tooltip('Select a possible facet column. This should be a column with just a few categories!',target=f'facet-{self.id}')
            ]),
            dbc.Col([
            create_dropdown(id=f'animation_frame-{self.id}',options=self.all_columns,value=None),
            create_Tooltip('Select a column which is the timeframe to be animated by!',target=f'animation_frame-{self.id}')
            ]),
            dbc.Col([
            create_dropdown(id=f'animation_group-{self.id}',options=self.all_columns,value=None),
            create_Tooltip('Select a comumn which is the target of the animation!',target=f'animation_group-{self.id}')
            ]),
            dbc.Col([
            dbc.InputGroup([
            dbc.InputGroupText('Title'),
            create_Text_Input(placeholder='Provide a title for saving',id=f'title-{self.id}'),
            create_Button(id=f'save-{self.id}',children=['Save Plot as HTML'],color='primary'),
            ]),
            create_Tooltip('Set your plot Title, the same title is used while saving',target=f'title-{self.id}'),
            create_Tooltip('Save your plot as an HTML file under the globally set directory',target=f'save-{self.id}'),
            ]),]),
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
                      Input(f'Z-{self.id}','value'),
                      Input(f'color-{self.id}','value'),
                      Input(f'size-{self.id}','value'),
                      Input(f'marginal_x-{self.id}','value'),
                      Input(f'marginal_y-{self.id}','value'),
                      Input(f'trendline-{self.id}','value'),
                      Input(f'facet-{self.id}','value'),
                      Input(f'animation_frame-{self.id}','value'),
                      Input(f'animation_group-{self.id}','value'),
                      Input(f'title-{self.id}','value'),
                      prevent_initial_call=True,)
        def vals(x,y,z,color,size,marginal_x,marginal_y,trendline,facet,animation_frame,animation_group,title):
            if ctx.triggered_id==f'X-{self.id}':
                self.set_x(x)
            elif ctx.triggered_id==f'Y-{self.id}':
                self.set_y(y)
            elif ctx.triggered_id==f'Z-{self.id}':
                self.set_z(z)
            elif ctx.triggered_id==f'color-{self.id}':
                self.set_color(color)
            elif ctx.triggered_id==f'size-{self.id}':
                self.set_size(size)
            elif ctx.triggered_id==f'marginal_x-{self.id}':
                self.set_marginal_x(marginal_x)
            elif ctx.triggered_id==f'marginal_y-{self.id}':
                self.set_marginal_y(marginal_y)
            elif ctx.triggered_id==f'trendline-{self.id}':
                self.set_trendline(trendline)
                self.set_trendline_options(trendline)
                try:
                    self.update_fig()
                except:
                   return self.fig,self.fig,create_Toast(children=['Unfortunatly no trendline could be calculated!'],header='Unusable Graph',icon='danger')
            elif ctx.triggered_id==f'facet-{self.id}':
                self.set_facet_col(facet)
                try:
                    self.update_fig()
                except:
                    return self.fig,self.fig,create_Toast(children=['Unfortunatly the selected facet column has to many unique values, which would result in a unusable graph! Please use another one'],header='Unusable Graph',icon='danger')
            elif ctx.triggered_id==f'animation_frame-{self.id}':
                self.set_animation_frame(animation_frame)
            elif ctx.triggered_id==f'animation_group-{self.id}':
                self.set_animation_group(animation_group) 
            elif ctx.triggered_id==f'title-{self.id}':
                self.update_title(title=title)
                self.fig.update_layout(title=self.title)
                return self.fig,self.fig,[]
            self.update_fig()
            if self.fig:
                return self.fig,self.fig,[]
            else:
                raise PreventUpdate
                       
            
        @app.callback(Output(f'Z-{self.id}','disabled'),
                      Output(f'color-{self.id}','disabled'),
                      Output(f'size-{self.id}','disabled'),
                      Output(f'marginal_x-{self.id}','disabled'),
                      Output(f'marginal_y-{self.id}','disabled'),
                      Output(f'trendline-{self.id}','disabled'),
                      Output(f'facet-{self.id}','disabled'),
                      Output(f'save-{self.id}','disabled'),
                      Output(f'title-{self.id}','disabled'),
                      Input(f'X-{self.id}','value'),
                      Input(f'Y-{self.id}','value'),
                       )
        def activate_settings(x,y):
            if not x or not y:
                return [True,True,True,True,True,True,True,True,True]
            else:
                return [False,False,False,False,False,False,False,False,False]
        
        for id in [f'X-{self.id}',f'Y-{self.id}',f'Z-{self.id}',f'color-{self.id}',f'size-{self.id}']:
            create_dropdown_paging_callback(id,app)

        @app.callback(Output(f'plot_div-{self.id}','children',allow_duplicate=True),
                      Input(f'save-{self.id}','n_clicks'),
                      State(f'title-{self.id}','value'),
                      prevent_initial_callback=True
                      )
        def save_plot(save,title):
            if save:
                super().save(self.fig,title,save_path)
                return create_Toast(children=f'The plot was sucessfully saved to {save_path} under the name {title}',header='Plot saved',icon='sucess')